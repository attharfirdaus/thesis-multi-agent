"""The LLM segmentation fallback (FR-05): tried only when the rule-based segmenter finds no label,
and only ever on text already redacted by the caller. No test here touches a real network — every
request goes to an in-process httpx transport, matching `test_llm_client.py`'s own convention — and
one test below is the regression for the privacy rule itself: an unredacted identifier in the payload
must block the call before it ever reaches the transport.
"""

from collections.abc import Iterator

import httpx
import pytest

from app.config import get_settings
from app.ingest.llm_segment import LLM_CONFIDENCE, llm_segment
from app.ingest.segment import NO_AI_WARNING
from app.llm.client import ProviderClient

CONFIGURED = {
    "LLM_BASE_URL": "https://provider.test/v1",
    "LLM_API_KEY": "test-key",
    "LLM_MODEL": "test-model",
}
DOCUMENT = (
    "Berikut adalah risiko utama dalam manajemen proyek teknologi informasi menurut kerangka ISO 31000.\n"
    "Analisis saya terhadap kerangka ini menunjukkan bahwa penerapannya masih memerlukan penyesuaian "
    "konteks organisasi, khususnya pada tahap identifikasi risiko di lingkungan startup yang dinamis."
)
AI_EXCERPT = (
    "Berikut adalah risiko utama dalam manajemen proyek teknologi informasi menurut kerangka ISO 31000."
)
ANALYSIS_EXCERPT = (
    "Analisis saya terhadap kerangka ini menunjukkan bahwa penerapannya masih memerlukan penyesuaian "
    "konteks organisasi, khususnya pada tahap identifikasi risiko di lingkungan startup yang dinamis."
)


@pytest.fixture(autouse=True)
def _fresh_settings() -> Iterator[None]:
    yield
    get_settings.cache_clear()


def configure(monkeypatch: pytest.MonkeyPatch, **env: str) -> None:
    for key in CONFIGURED:
        monkeypatch.delenv(key, raising=False)
    for key, value in {**CONFIGURED, **env}.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()


def stub(replies: list[str | int]) -> tuple[ProviderClient, list[httpx.Request]]:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        reply = replies[min(len(calls), len(replies)) - 1]
        if isinstance(reply, int):
            return httpx.Response(reply, json={"error": "provider says no"})
        return httpx.Response(200, json={"choices": [{"message": {"content": reply}}]})

    return ProviderClient(http=httpx.Client(transport=httpx.MockTransport(handler))), calls


def _reply(has_ai_output: bool, quote: str = "") -> str:
    import json

    return json.dumps({"has_ai_output": has_ai_output, "ai_output_quote": quote})


def test_a_verified_excerpt_splits_the_document(monkeypatch):
    configure(monkeypatch)
    client, calls = stub([_reply(True, AI_EXCERPT)])

    result = llm_segment(DOCUMENT, client)

    assert result is not None
    assert result.method == "llm"
    assert result.ai_output_text == AI_EXCERPT
    assert result.student_analysis_text == ANALYSIS_EXCERPT
    assert len(calls) == 1
    assert len(result.segments) == 2
    assert all(segment.confidence == LLM_CONFIDENCE for segment in result.segments)


def test_a_confident_no_ai_output_answer_is_trusted(monkeypatch):
    configure(monkeypatch)
    client, _ = stub([_reply(False)])

    text = "Seluruh dokumen ini adalah analisis saya sendiri tanpa bantuan AI."
    result = llm_segment(text, client)

    assert result is not None
    assert result.method == "llm"
    assert result.ai_output_text == ""
    assert result.has_ai_output is False
    assert result.student_analysis_text == text
    # Same sentence the rule-based path shows for the same fact, so the lecturer reads one message
    # regardless of which method decided there was no AI output (DECISIONS.md, 2026-10-17).
    assert result.warnings == [NO_AI_WARNING]


def test_a_claimed_quote_not_actually_in_the_text_is_rejected_after_a_retry(monkeypatch):
    """A model that paraphrases instead of copying cannot be told apart from one that invents a
    boundary outright, so both are refused the same way (same discipline as `app.agents.evidence`) —
    but only after the same one retry the grading pipeline gives an unverified quote (PRD §6)."""
    configure(monkeypatch)
    client, calls = stub([_reply(True, "Ini kutipan yang tidak pernah ada di dalam dokumen aslinya.")])

    assert llm_segment(DOCUMENT, client) is None
    assert len(calls) == 2


def test_the_whole_document_claimed_as_ai_output_is_rejected_after_a_retry(monkeypatch):
    configure(monkeypatch)
    client, calls = stub([_reply(True, DOCUMENT)])

    assert llm_segment(DOCUMENT, client) is None
    assert len(calls) == 2


def test_an_empty_quote_on_the_first_attempt_succeeds_on_the_retry(monkeypatch):
    """Found live, 2026-10-17: the real model answered `has_ai_output: true` with no `ai_output_quote`
    at all — Cloudflare's JSON mode is hint-level, so the schema's own default filled the gap instead
    of the model writing the field. One retry recovers a submission that would otherwise lose a real
    AI-output detection to a formatting slip."""
    configure(monkeypatch)
    client, calls = stub([_reply(True, ""), _reply(True, AI_EXCERPT)])

    result = llm_segment(DOCUMENT, client)

    assert result is not None
    assert result.ai_output_text == AI_EXCERPT
    assert len(calls) == 2


def test_no_provider_configured_returns_none_instead_of_raising(monkeypatch):
    configure(monkeypatch, LLM_BASE_URL="")

    assert llm_segment(DOCUMENT) is None


def test_a_failed_provider_returns_none_instead_of_raising(monkeypatch):
    configure(monkeypatch, LLM_MAX_ATTEMPTS="1")
    client, calls = stub([500])

    assert llm_segment(DOCUMENT, client) is None
    assert len(calls) == 1


def test_empty_text_is_never_sent(monkeypatch):
    configure(monkeypatch)
    client, calls = stub([_reply(False)])

    assert llm_segment("   ", client) is None
    assert calls == []


def test_an_identifier_left_in_the_text_blocks_the_call(monkeypatch):
    """The regression test for the pipeline-order rule itself (DECISIONS.md, 2026-10-17): if the
    caller ever forgets to redact first, this module must not be what sends the leak. The stub
    records zero calls — the egress guard inside `ProviderClient.complete_json` raises before the
    request is built, the same gate the grading pipeline depends on."""
    configure(monkeypatch)
    client, calls = stub([_reply(False)])
    dirty = DOCUMENT + "\nNama : Budi Santoso"

    assert llm_segment(dirty, client) is None
    assert calls == []
