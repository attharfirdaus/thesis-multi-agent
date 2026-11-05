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
    SINGLE_AGENT_FAILED,
    SYNTHESIS_FAILED,
    SYNTHESIS_INCONSISTENCY,
    SYNTHESIS_RETRIED,
    evaluate_submission,
)
from app.agents.models import (
    CognitiveResult,
    IndicatorFinding,
    MetacognitiveResult,
    SegmentIndicators,
    SegmentLevel,
    SingleAgentResult,
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

    def complete_json(
        self, *, system: str, user: str, schema: type[BaseModel], check=None, **_: object
    ) -> Completion:
        self.calls.append(schema)
        outcome = self.plan[schema]
        if isinstance(outcome, list):
            outcome = outcome.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        # The real client runs the caller's check inside its retry loop; a stub that answers once
        # makes a rejected answer the agent's final failure, which is what the last attempt is.
        if check is not None:
            check(outcome)
        return Completion(parsed=outcome, raw="{}", latency_ms=1, attempts=1)


def calls_for(client: StubClient, schema: type[BaseModel]) -> int:
    return sum(1 for called in client.calls if called is schema)


def cognitive_levels(quote: str = COGNITIVE_QUOTE, level: str = "C4") -> list[SegmentLevel]:
    return [
        SegmentLevel(
            segment=1, level=level, evidence_quote=quote, rationale="Analisis membandingkan dua sumber."
        )
    ]


def metacognitive_segments(quote: str = METACOGNITIVE_QUOTE) -> list[SegmentIndicators]:
    return [
        SegmentIndicators(
            segment=1,
            indicators=[
                IndicatorFinding(
                    indicator="evaluasi",
                    evidence_quote=quote,
                    rationale="Mahasiswa memeriksa ulang data yang dipakai model.",
                )
            ],
        )
    ]


def cognitive_result(quote: str = COGNITIVE_QUOTE, level: str = "C4") -> CognitiveResult:
    return CognitiveResult(segments=cognitive_levels(quote, level))


def metacognitive_result(quote: str = METACOGNITIVE_QUOTE) -> MetacognitiveResult:
    return MetacognitiveResult(segments=metacognitive_segments(quote))


def synthesis_result() -> SynthesisResult:
    return SynthesisResult(
        rationale="Skor didukung kutipan dari analisis mahasiswa sendiri.",
        feedback_text="Pertahankan kebiasaan memeriksa ulang data yang dipakai model.",
    )


def single_agent_result(
    cognitive_quote: str = COGNITIVE_QUOTE, metacognitive_quote: str = METACOGNITIVE_QUOTE
) -> SingleAgentResult:
    return SingleAgentResult(
        cognitive=cognitive_levels(cognitive_quote),
        metacognitive=metacognitive_segments(metacognitive_quote),
    )


def make_state(**overrides: object) -> dict:
    state: dict = {
        "owner_id": "owner-1",
        "run_id": "run-1",
        "submission_id": "submission-1",
        "rubric": {"version": "v1", "levels": ["C2", "C4"], "indicators": ["evaluasi"]},
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

    for name in (
        "cognitive_prompt",
        "metacognitive_prompt",
        "synthesis_prompt",
        "single_agent_prompt",
    ):
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

    assert result["cognitive"].segments[0].level == "C4"
    # Each agent's own measurement, carried in the state so `persist` can write PRD §10's trace column.
    assert result["latencies"] == {"cognitive": 1, "metacognitive": 1, "synthesis": 1}
    assert result["metacognitive"].segments[0].indicators[0].indicator == "evaluasi"
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
    assert result["cognitive"].segments[0].evidence_quote == PARAPHRASE
    assert result["evidence_failures"] == [f"cognitive[1]: {PARAPHRASE}"]
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
    # A call that raised has no client-reported latency, so the node measures it: the duration of a
    # failed call is the number that says the provider is unhealthy, and it was null before this.
    assert result["latencies"]["cognitive"] >= 0
    assert result["latencies"]["metacognitive"] == 1
    assert result["metacognitive"].segments[0].indicators[0].evidence_quote == METACOGNITIVE_QUOTE
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
    assert result["evidence_failures"] == [f"cognitive[1]: {PARAPHRASE}"]
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


def test_a_segment_without_indicators_is_not_an_evidence_failure(prompt_calls):
    """Indicators are nominal (Bab II.2.4): a segment may show none, and an empty list is an answer."""
    plan = full_plan()
    plan[MetacognitiveResult] = MetacognitiveResult(segments=[SegmentIndicators(segment=1)])
    client = StubClient(plan)

    result = evaluate_submission(make_state(), client)

    assert result["metacognitive"].segments[0].indicators == []
    assert [span.source for span in result["evidence"]] == ["cognitive"]
    assert result.get("evidence_failures", []) == []
    assert result.get("flags", []) == []


def test_build_graph_compiles_without_a_client():
    """The production entry point builds its own client; a caller may inject one (JobQueue does)."""
    assert graph.build_graph() is not None


def test_single_agent_mode_calls_once_and_scores_both_dimensions(prompt_calls):
    """FR-15: one call, split into the same two shapes the multi-agent path produces."""
    client = StubClient({SingleAgentResult: single_agent_result()})

    result = evaluate_submission(make_state(mode="single_agent"), client)

    assert calls_for(client, SingleAgentResult) == 1
    assert result["cognitive"].segments[0].level == "C4"
    assert result["metacognitive"].segments[0].indicators[0].indicator == "evaluasi"
    # No synthesis call happened, and the trace must not look like three calls.
    assert result["latencies"] == {"single_agent": 1}
    assert calls_for(client, SynthesisResult) == 0
    assert result["single_agent"] is not None
    assert {span.source for span in result["evidence"]} == {"cognitive", "metacognitive"}
    assert result.get("flags", []) == []


def test_single_agent_mode_refuses_an_uncalibrated_run(monkeypatch):
    def refuse(**_: object) -> tuple[str, str]:
        raise prompts.MissingCalibration("calibration examples are empty")

    monkeypatch.setattr(prompts, "single_agent_prompt", refuse)
    client = StubClient({})

    with pytest.raises(prompts.MissingCalibration):
        evaluate_submission(make_state(mode="single_agent"), client)

    assert client.calls == []


def test_single_agent_mode_flags_an_unfindable_quote_without_retrying(prompt_calls):
    """No synthesis step exists to retry in this mode: an unverifiable quote is flagged once, the
    same way the multi-agent path flags a failed retry, never retried (PRD §6, baseline scope)."""
    client = StubClient({SingleAgentResult: single_agent_result(cognitive_quote=PARAPHRASE)})

    result = evaluate_submission(make_state(mode="single_agent"), client)

    assert calls_for(client, SingleAgentResult) == 1
    assert EVIDENCE_UNVERIFIED in result["flags"]
    assert NEEDS_REVIEW in result["flags"]
    assert SYNTHESIS_RETRIED not in result["flags"]
    assert result["cognitive"].segments[0].evidence_quote == PARAPHRASE
    assert result["evidence_failures"] == [f"cognitive[1]: {PARAPHRASE}"]


def test_single_agent_failure_flags_both_dimensions(prompt_calls):
    client = StubClient({SingleAgentResult: RuntimeError("provider unreachable")})

    result = evaluate_submission(make_state(mode="single_agent"), client)

    assert result["cognitive"] is None
    assert result["metacognitive"] is None
    assert SINGLE_AGENT_FAILED in result["flags"]
    assert any("provider unreachable" in message for message in result["errors"])


def test_build_single_agent_graph_compiles_without_a_client():
    assert graph.build_single_agent_graph() is not None


def test_evaluate_submission_defaults_to_multi_agent_when_mode_is_absent(prompt_calls):
    """State built before the baseline existed carries no `mode` key at all."""
    client = StubClient(full_plan())

    result = evaluate_submission(make_state(), client)

    assert result["synthesis"] is not None
    assert calls_for(client, SingleAgentResult) == 0


def test_both_specialists_read_the_paired_input(prompt_calls):
    """Bab II.2.2: the AI output (object of analysis) and the segmented analysis, for both agents."""
    evaluate_submission(make_state(), StubClient(full_plan()))

    for agent in ("cognitive", "metacognitive"):
        call = next(c for c in prompt_calls if c["agent"] == agent)
        assert call["ai_output_text"] == "Model menjawab dengan ringkasan singkat."
        assert [segment.text for segment in call["segments"]] == [ANALYSIS]
    # The synthesis agent gets the labels without the labelling rubric (Bab III.8).
    synthesis = next(c for c in prompt_calls if c["agent"] == "synthesis")
    assert "rubric" not in synthesis


def test_a_level_outside_the_rubric_fails_the_agent_rather_than_being_stored(prompt_calls):
    plan = full_plan()
    plan[CognitiveResult] = cognitive_result(level="C9")
    result = evaluate_submission(make_state(), StubClient(plan))

    assert result["cognitive"] is None
    assert COGNITIVE_FAILED in result["flags"]


def test_an_unlabelled_segment_fails_the_agent(prompt_calls):
    """Every segment gets a label: a missing segment is an unusable answer, not a partial score."""
    two_sentences = "Saya membandingkan dua sumber jurnal itu. Lalu saya memeriksa ulang datanya."
    result = evaluate_submission(
        make_state(student_analysis_text=two_sentences), StubClient(full_plan())
    )

    assert COGNITIVE_FAILED in result["flags"]


def test_a_quote_from_another_segment_does_not_back_the_label(prompt_calls):
    text = "Saya membandingkan dua sumber jurnal itu. Lalu saya memeriksa ulang datanya."
    plan = {
        CognitiveResult: CognitiveResult(
            segments=[
                SegmentLevel(
                    segment=1, level="C4", evidence_quote="memeriksa ulang datanya", rationale="Salah segmen."
                ),
                SegmentLevel(
                    segment=2, level="C2", evidence_quote="memeriksa ulang datanya", rationale="Benar."
                ),
            ]
        ),
        MetacognitiveResult: MetacognitiveResult(
            segments=[SegmentIndicators(segment=1), SegmentIndicators(segment=2)]
        ),
        SynthesisResult: synthesis_result(),
    }
    result = evaluate_submission(make_state(student_analysis_text=text), StubClient(plan))

    assert result["evidence_failures"] == ["cognitive[1]: memeriksa ulang datanya"]
    assert [(span.segment, span.quote) for span in result["evidence"]] == [(2, "memeriksa ulang datanya")]
    assert NEEDS_REVIEW in result["flags"]


def test_a_synthesis_inconsistency_sends_the_submission_to_review(prompt_calls):
    """Bab III.4: synthesis flags a rationale that does not match its quote; the label is kept."""
    plan = full_plan()
    plan[SynthesisResult] = SynthesisResult(
        rationale="Skor didukung kutipan dari analisis mahasiswa sendiri.",
        feedback_text="Pertahankan kebiasaan memeriksa ulang data yang dipakai model.",
        inconsistencies=["Segmen 1: alasan menyebut evaluasi, kutipan hanya membandingkan."],
    )
    result = evaluate_submission(make_state(), StubClient(plan))

    assert SYNTHESIS_INCONSISTENCY in result["flags"] and NEEDS_REVIEW in result["flags"]
    assert result["cognitive"].segments[0].level == "C4"
