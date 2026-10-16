"""Phase 4 gate for the provider client: retry behaviour and, above all, the egress guard.

No test here touches a network: every request goes to an in-process httpx transport, and the stub
itself is the evidence for the privacy rule — if an identifier leaks, the stub has one more recorded
call than the test allows. All text is synthetic.
"""

import json
from collections.abc import Iterator
from typing import Any

import httpx
import pytest

from app.agents.models import CognitiveResult
from app.config import get_settings
from app.llm.client import Completion, ProviderClient, ProviderError, ProviderNotConfigured

CONFIGURED = {
    "LLM_BASE_URL": "https://provider.test/v1",
    "LLM_API_KEY": "test-key",
    "LLM_MODEL": "test-model",
}
SYSTEM = "You are the cognitive agent."
USER = "Aktivitas ini menunjukkan peningkatan hasil belajar."
PAYLOAD = {
    "level": "C4",
    "evidence_quote": "Hasil belajar siswa meningkat setelah tindakan.",
    "rationale": "Analisis membandingkan kondisi awal dengan kondisi akhir.",
}


@pytest.fixture(autouse=True)
def _fresh_settings() -> Iterator[None]:
    """The client caches settings, so each test has to leave the cache cold for the next one."""
    yield
    get_settings.cache_clear()


def configure(monkeypatch: pytest.MonkeyPatch, **env: str) -> None:
    """State the LLM configuration a test needs, overriding whatever the shell or `.env` holds."""
    for key in CONFIGURED:
        monkeypatch.delenv(key, raising=False)
    for key, value in {**CONFIGURED, **env}.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()


def stub(replies: list[str | int]) -> tuple[ProviderClient, list[httpx.Request]]:
    """A client wired to an in-process transport, with every request it makes recorded.

    `replies` is consumed one per call and the last entry repeats after that. A string is returned as
    the assistant message, an int as an HTTP status with an error body.
    """
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        reply = replies[min(len(calls), len(replies)) - 1]
        if isinstance(reply, int):
            return httpx.Response(reply, json={"error": "provider says no"})
        return httpx.Response(200, json={"choices": [{"message": {"content": reply}}]})

    return ProviderClient(http=httpx.Client(transport=httpx.MockTransport(handler))), calls


def sent_body(call: httpx.Request) -> dict[str, Any]:
    return json.loads(call.content)


def test_valid_response_parses_and_reports_latency_and_attempts(monkeypatch):
    configure(monkeypatch)
    provider, calls = stub([json.dumps(PAYLOAD)])

    completion = provider.complete_json(system=SYSTEM, user=USER, schema=CognitiveResult)

    assert isinstance(completion, Completion)
    assert completion.parsed == CognitiveResult.model_validate(PAYLOAD)
    assert completion.raw == json.dumps(PAYLOAD)
    assert completion.attempts == 1
    assert isinstance(completion.latency_ms, int)
    assert completion.latency_ms >= 0
    assert len(calls) == 1


def test_request_is_configured_and_carries_the_schema_both_ways(monkeypatch):
    configure(monkeypatch)
    provider, calls = stub([json.dumps(PAYLOAD)])

    provider.complete_json(system=SYSTEM, user=USER, schema=CognitiveResult)

    body = sent_body(calls[0])
    assert calls[0].url.path.endswith("/chat/completions")
    assert body["model"] == CONFIGURED["LLM_MODEL"]  # from config, never from the call site
    assert body["temperature"] == 0  # the configured default
    assert body["max_tokens"] == 1024  # bounded output; unbounded generation never returns
    # Reasoning would spend the whole token budget and leave `content` empty (measured, 2026-10-16).
    assert body["chat_template_kwargs"] == {"enable_thinking": False}
    assert "seed" not in body  # optional, and unset by default
    assert body["response_format"]["type"] == "json_schema"
    response_schema = body["response_format"]["json_schema"]
    assert response_schema["name"] == "CognitiveResult"
    assert response_schema["strict"] is True
    assert response_schema["schema"] == CognitiveResult.model_json_schema()
    # The prompt copy, for the free endpoints that ignore response_format.
    assert '"level"' in body["messages"][1]["content"]
    assert calls[0].headers["authorization"] == f"Bearer {CONFIGURED['LLM_API_KEY']}"


def test_caller_temperature_and_seed_override_config(monkeypatch):
    configure(monkeypatch, LLM_TEMPERATURE="0.3", LLM_SEED="11")
    provider, calls = stub([json.dumps(PAYLOAD)])

    provider.complete_json(system=SYSTEM, user=USER, schema=CognitiveResult, temperature=0.9, seed=42)

    body = sent_body(calls[0])
    assert body["temperature"] == 0.9
    assert body["seed"] == 42


def test_malformed_json_is_retried_and_accepted_on_the_second_attempt(monkeypatch):
    configure(monkeypatch)
    provider, calls = stub(["ini bukan JSON", json.dumps(PAYLOAD)])

    completion = provider.complete_json(system=SYSTEM, user=USER, schema=CognitiveResult)

    assert completion.attempts == 2
    assert completion.parsed == CognitiveResult.model_validate(PAYLOAD)
    assert len(calls) == 2


def test_unreachable_provider_is_retried_then_raises(monkeypatch):
    configure(monkeypatch)
    provider, calls = stub([503])

    with pytest.raises(ProviderError, match="503"):
        provider.complete_json(system=SYSTEM, user=USER, schema=CognitiveResult)

    assert len(calls) == 3  # LLM_MAX_ATTEMPTS


def test_schema_violation_exhausts_the_attempts_and_raises(monkeypatch):
    configure(monkeypatch, LLM_MAX_ATTEMPTS="2")
    provider, calls = stub([json.dumps({**PAYLOAD, "evidence_quote": "pendek"})])

    with pytest.raises(ProviderError) as raised:
        provider.complete_json(system=SYSTEM, user=USER, schema=CognitiveResult)

    assert "2 attempts" in str(raised.value)
    assert "CognitiveResult" in str(raised.value)
    assert len(calls) == 2


@pytest.mark.parametrize("dirty_in", ["system", "user"])
def test_identifier_in_the_payload_blocks_the_call(monkeypatch, dirty_in):
    """The regression test for the egress guard: the stub records zero calls."""
    configure(monkeypatch)
    provider, calls = stub([json.dumps(PAYLOAD)])
    messages = {"system": SYSTEM, "user": USER, dirty_in: "Hubungi saya di budi@example.com"}

    with pytest.raises(ProviderError, match="refusing to send"):
        provider.complete_json(schema=CognitiveResult, **messages)

    assert calls == []


@pytest.mark.parametrize("missing", ["LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL"])
def test_incomplete_configuration_raises_before_any_call(monkeypatch, missing):
    configure(monkeypatch, **{missing: ""})
    provider, calls = stub([json.dumps(PAYLOAD)])

    with pytest.raises(ProviderNotConfigured, match=missing):
        provider.complete_json(system=SYSTEM, user=USER, schema=CognitiveResult)

    assert calls == []
