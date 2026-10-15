"""Gate for the PRD §6 graph, run offline.

The provider is stubbed and the three prompt builders are replaced: they are pure text assembly with
their own tests, and what this file has to prove is the orchestration — which dimension survives a
failure, how many times synthesis is allowed to retry, and whether every stored offset slices the
student's text back out.

The stub is also how the retry count is counted: `StubClient.calls` records one entry per call, so
"one retry" is two `SynthesisResult` calls and not a promise in a docstring.
"""

import json

import pytest
from pydantic import BaseModel

from app.agents import graph, prompts
from app.agents.evidence import normalise
from app.agents.graph import (
    COGNITIVE_FAILED,
    EVIDENCE_UNVERIFIED,
    NEEDS_REVIEW,
    SYNTHESIS_FAILED,
    SYNTHESIS_RETRIED,
    evaluate_submission,
)
from app.agents.models import (
    CognitiveResult,
    IndicatorFinding,
    MetacognitiveResult,
    SynthesisResult,
)
from app.llm.client import Completion

ANALYSIS = (
    "Saya membandingkan keluaran AI dengan dua artikel jurnal yang saya baca, lalu memeriksa\n"
    "ulang data yang dipakai model tersebut sebelum menuliskannya kembali."
)
COGNITIVE_QUOTE = "membandingkan keluaran AI dengan dua artikel jurnal"
METACOGNITIVE_QUOTE = "memeriksa ulang data yang dipakai model"
# Absent from ANALYSIS on purpose: the pipeline must call this a failure, not find a near match.
PARAPHRASE = "saya menilai keluaran AI itu kurang tepat"


class StubClient:
    """Offline `ProviderClient`. `plan` maps a schema to an object, a list consumed one call at a
    time, or an exception to raise on the call for that schema."""

    def __init__(self, plan: dict[type[BaseModel], object]) -> None:
        self.plan = plan
        self.calls: list[type[BaseModel]] = []

    def complete_json(self, *, system: str, user: str, schema: type[BaseModel], **_: object) -> Completion:
        self.calls.append(schema)
        outcome = self.plan[schema]
        if isinstance(outcome, list):
            outcome = outcome.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return Completion(parsed=outcome, raw="{}", latency_ms=1, attempts=1)


def calls_for(client: StubClient, schema: type[BaseModel]) -> int:
    return sum(1 for called in client.calls if called is schema)


def cognitive_result(quote: str = COGNITIVE_QUOTE) -> CognitiveResult:
    return CognitiveResult(
        level="C4", evidence_quote=quote, rationale="Analisis mahasiswa membandingkan dua sumber."
    )


def metacognitive_result(quote: str = METACOGNITIVE_QUOTE) -> MetacognitiveResult:
    return MetacognitiveResult(
        findings=[
            IndicatorFinding(
                indicator="evaluasi",
                present=True,
                strength="kuat",
                evidence_quote=quote,
                rationale="Mahasiswa memeriksa ulang data yang dipakai model.",
            )
        ]
    )


def synthesis_result() -> SynthesisResult:
    return SynthesisResult(
        rationale="Skor didukung kutipan dari analisis mahasiswa sendiri.",
        feedback_text="Pertahankan kebiasaan memeriksa ulang data yang dipakai model.",
    )


def make_state(**overrides: object) -> dict:
    state: dict = {
        "owner_id": "owner-1",
        "run_id": "run-1",
        "submission_id": "submission-1",
        "rubric": {"version": "v1", "levels": ["C4"], "indicators": ["evaluasi"]},
        "prompts": {
            "calibration": {
                "cognitive": {
                    "instructions": "kalibrasi uji",
                    "examples": [{"level": "C4", "evidence_quote": "kalibrasi"}],
                },
                "metacognitive": {
                    "instructions": "kalibrasi uji",
                    "examples": [{"analisis_mhs": "kalibrasi"}],
                },
            }
        },
        "student_analysis_text": ANALYSIS,
        "ai_output_text": "Model menjawab dengan ringkasan singkat.",
    }
    state.update(overrides)
    return state


@pytest.fixture
def prompt_calls(monkeypatch):
    """Replace the builders with recorders that return the keyword arguments as the user prompt."""
    seen: list[dict] = []

    def builder(agent: str):
        def build(**kwargs: object) -> tuple[str, str]:
            seen.append({"agent": agent, **kwargs})
            return f"{agent} system", json.dumps(kwargs, default=str)

        return build

    for name in ("cognitive_prompt", "metacognitive_prompt", "synthesis_prompt"):
        monkeypatch.setattr(prompts, name, builder(name.removesuffix("_prompt")))
    return seen


def full_plan() -> dict[type[BaseModel], object]:
    return {
        CognitiveResult: cognitive_result(),
        MetacognitiveResult: metacognitive_result(),
        SynthesisResult: synthesis_result(),
    }


def test_happy_path_scores_both_dimensions_and_locates_both_quotes(prompt_calls):
    client = StubClient(full_plan())

    result = evaluate_submission(make_state(), client)

    assert result["cognitive"].level == "C4"
    assert result["metacognitive"].findings[0].indicator == "evaluasi"
    assert result["synthesis"].feedback_text == synthesis_result().feedback_text
    assert result.get("evidence_failures", []) == []
    assert result.get("flags", []) == []
    assert {span.source for span in result["evidence"]} == {"cognitive", "metacognitive"}
    for span in result["evidence"]:
        # The offsets are the database's contract: slicing the stored text reproduces the quote, up to
        # the formatting the matcher exists to forgive.
        sliced = ANALYSIS[span.start_offset : span.end_offset]
        assert normalise(sliced) == normalise(span.quote)
        assert span.end_offset <= len(ANALYSIS) and sliced


def test_unfindable_quote_retries_synthesis_once_then_flags_for_review(prompt_calls):
    plan = full_plan()
    plan[CognitiveResult] = cognitive_result(PARAPHRASE)
    client = StubClient(plan)

    result = evaluate_submission(make_state(), client)

    assert calls_for(client, SynthesisResult) == 2
    assert SYNTHESIS_RETRIED in result["flags"]
    assert NEEDS_REVIEW in result["flags"]
    assert EVIDENCE_UNVERIFIED in result["flags"]
    # The score is kept for the lecturer, not discarded (PRD §6).
    assert result["cognitive"].evidence_quote == PARAPHRASE
    assert result["evidence_failures"] == [f"cognitive: {PARAPHRASE}"]
    assert [span.source for span in result["evidence"]] == ["metacognitive"]

    retries = [call for call in prompt_calls if call["agent"] == "synthesis" and call["retry_reason"]]
    assert len(retries) == 1
    assert PARAPHRASE in retries[0]["retry_reason"]


def test_a_failing_cognitive_agent_keeps_the_metacognitive_result(prompt_calls):
    plan = full_plan()
    plan[CognitiveResult] = RuntimeError("provider unreachable")
    client = StubClient(plan)

    result = evaluate_submission(make_state(), client)

    assert result["cognitive"] is None
    assert COGNITIVE_FAILED in result["flags"]
    assert any("provider unreachable" in message for message in result["errors"])
    assert result["metacognitive"].findings[0].evidence_quote == METACOGNITIVE_QUOTE
    assert result["synthesis"] is not None
    # Synthesis still ran, and it was told only what the pipeline actually produced.
    assert calls_for(client, SynthesisResult) == 1
    assert [span.source for span in result["evidence"]] == ["metacognitive"]


def test_empty_analysis_is_refused_before_any_model_call():
    client = StubClient({})

    with pytest.raises(ValueError, match="student analysis is empty"):
        evaluate_submission(make_state(student_analysis_text="   \n  "), client)

    assert client.calls == []


def test_failed_synthesis_keeps_the_scores_and_still_asks_for_review(prompt_calls):
    plan = full_plan()
    plan[CognitiveResult] = cognitive_result(PARAPHRASE)
    plan[SynthesisResult] = RuntimeError("provider unreachable")
    client = StubClient(plan)

    result = evaluate_submission(make_state(), client)

    assert result["synthesis"] is None
    assert SYNTHESIS_FAILED in result["flags"]
    # The evidence node is the one that noticed the unverifiable quote here, because synthesis never
    # got far enough to look.
    assert NEEDS_REVIEW in result["flags"]
    assert result["evidence_failures"] == [f"cognitive: {PARAPHRASE}"]
    assert result["cognitive"] is not None


def test_missing_calibration_aborts_the_run_instead_of_flagging(monkeypatch):
    def refuse(**_: object) -> tuple[str, str]:
        raise prompts.MissingCalibration("calibration examples are empty")

    monkeypatch.setattr(prompts, "cognitive_prompt", refuse)
    monkeypatch.setattr(prompts, "metacognitive_prompt", refuse)
    client = StubClient({})

    with pytest.raises(prompts.MissingCalibration):
        evaluate_submission(make_state(), client)

    assert client.calls == []


def test_an_indicator_without_a_quote_is_not_an_evidence_failure(prompt_calls):
    plan = full_plan()
    plan[MetacognitiveResult] = MetacognitiveResult(
        findings=[IndicatorFinding(indicator="orientasi", present=False, rationale="Tidak tampak.")]
    )
    client = StubClient(plan)

    result = evaluate_submission(make_state(), client)

    assert result["metacognitive"].findings[0].evidence_quote == ""
    assert [span.source for span in result["evidence"]] == ["cognitive"]
    assert result.get("evidence_failures", []) == []
    assert result.get("flags", []) == []


def test_build_graph_compiles_without_a_client():
    """The production entry point builds its own client; a caller may inject one (JobQueue does)."""
    assert graph.build_graph() is not None
