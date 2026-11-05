"""Typed contracts for the agent pipeline (phase 4).

Frozen on purpose: the provider client, the prompts, the graph and the job worker are written
against this file independently.

Two rules from the PRD that the shapes below encode:

- Each agent returns structured JSON validated against its schema, and an invalid response is retried
  before it is allowed to fail (PRD §6). That is why every agent has a model here and no agent returns
  free text.
- A score is only credible if it quotes the submission, so `evidence_quote` is required and the
  pipeline locates it in the stored text afterwards. A quote that cannot be found is a pipeline
  failure, not a stylistic complaint.
"""

from typing import Annotated, Literal, TypedDict

from pydantic import BaseModel, Field

from app.agents.segments import Segment


class SegmentLevel(BaseModel):
    """The Bloom level of one segment of the student's analysis (Bab III.6, III.8). Exactly one level per
    segment: the levels are ordinal and mutually exclusive. The level must be one of the rubric's levels;
    the graph rejects anything else and the call is retried rather than an invented label stored."""

    segment: int = Field(ge=1, description="The segment number, as shown in brackets in the input.")
    level: str = Field(description="Exactly one of the rubric's cognitive levels.")
    evidence_quote: str = Field(
        min_length=1, description="Verbatim text from this segment of the student's analysis."
    )
    rationale: str = Field(min_length=5, description="Why this level, in one sentence.")


class CognitiveResult(BaseModel):
    segments: list[SegmentLevel] = Field(min_length=1, description="One entry for every segment.")


class IndicatorFinding(BaseModel):
    """One metacognitive indicator found in one segment. Indicators are nominal (Bab II.2.4): a finding
    says the indicator is present, with the quote that shows it; absence is the finding's absence."""

    indicator: str = Field(description="Exactly one of the rubric's metacognitive indicator codes.")
    evidence_quote: str = Field(
        min_length=1, description="Verbatim text from this segment of the student's analysis."
    )
    rationale: str = Field(min_length=5)


class SegmentIndicators(BaseModel):
    segment: int = Field(ge=1, description="The segment number, as shown in brackets in the input.")
    indicators: list[IndicatorFinding] = Field(
        default_factory=list, description="The indicators present in this segment; may be empty."
    )


class MetacognitiveResult(BaseModel):
    segments: list[SegmentIndicators] = Field(min_length=1, description="One entry for every segment.")


class SingleAgentResult(BaseModel):
    """The single-agent baseline's answer, in one object (FR-15, Bab III.8).

    One call judges the whole rubric, so the model returns both dimensions' segment labels together.
    This is a baseline shape, not a merged multi-agent result: nothing here reconciles two independent
    calls, which is exactly the difference the comparison is meant to expose. The graph splits it back
    into `CognitiveResult` and `MetacognitiveResult` so evidence checking and persistence keep one path.
    """

    cognitive: list[SegmentLevel] = Field(min_length=1, description="One entry for every segment.")
    metacognitive: list[SegmentIndicators] = Field(
        min_length=1, description="One entry for every segment."
    )


class SynthesisResult(BaseModel):
    """What the lecturer reads. `rationale` explains the scores, `feedback_text` is the per-student
    feedback of FR-19 that the lecturer may edit before export, and `inconsistencies` lists every place
    where an agent's rationale does not match the quote it rests on (Bab III.4) — each one sends the
    submission to the lecturer for review."""

    rationale: str = Field(min_length=20)
    feedback_text: str = Field(min_length=20)
    inconsistencies: list[str] = Field(
        default_factory=list,
        description="Each mismatch between a rationale and its quoted evidence; empty when none.",
    )


class EvidenceSpan(BaseModel):
    """A quote that was located in the stored text, with the offsets the database will keep.

    Offsets point into `student_analysis_text`, never into the AI output: the AI output is the object of
    analysis, not a source of evidence. `segment` (and `indicator`, for a metacognitive finding) say which
    label the quote backs; `source` says which agent produced it.
    """

    source: Literal["cognitive", "metacognitive"]
    segment: int
    indicator: str | None = None
    quote: str
    start_offset: int = Field(ge=0)
    end_offset: int = Field(ge=0)


def _merge_lists(left: list[str], right: list[str]) -> list[str]:
    """Reducer for the two keys that parallel nodes both write.

    Without it LangGraph raises `InvalidUpdateError: At key 'errors': Can receive only one value per
    step` the moment the cognitive and metacognitive branches run concurrently — each has its own
    failures to report, and merging is what keeps one dimension's problem from erasing the other's.
    """
    return [*left, *right]


def _merge_maps(left: dict[str, int], right: dict[str, int]) -> dict[str, int]:
    """Reducer for `latencies`: the two analysis agents measure their own calls in parallel."""
    return {**left, **right}


def _merge_strings(left: dict[str, str], right: dict[str, str]) -> dict[str, str]:
    """Reducer for `inputs`, for the same reason as `latencies`."""
    return {**left, **right}


class GraphState(TypedDict, total=False):
    """The LangGraph channel definition.

    `flags` merges instead of overwriting, because two agents running in parallel each raise their own
    concerns and the synthesis step has to see both.
    """

    # Identity and configuration, set once by the caller.
    owner_id: str
    run_id: str
    submission_id: str
    # The run's mode, read from the run row: it selects which graph grades the submission (FR-15),
    # so the worker's CLI and the API both route through one place.
    mode: str
    rubric: dict
    prompts: dict

    # Input, already redacted by phase 3. Nothing else from the submission ever enters this state.
    student_analysis_text: str
    ai_output_text: str
    # The assessed units of the analysis (Bab III.6), set by `preprocess`.
    segments: list[Segment]

    # Agent output.
    cognitive: CognitiveResult | None
    metacognitive: MetacognitiveResult | None
    synthesis: SynthesisResult | None
    # The baseline's raw answer, kept so its one trace carries what the one call actually returned
    # (FR-15). The multi-agent path leaves it None, and `cognitive`/`metacognitive` above are the
    # split the rest of the pipeline reads either way.
    single_agent: SingleAgentResult | None

    # Evidence, filled by the evidence node after the agents have run. Only that node writes these,
    # so plain (overwriting) channels are correct — a reducer would let a later node silently append
    # stale spans.
    evidence: list[EvidenceSpan]
    evidence_failures: list[str]

    # Bookkeeping. Both parallel agents write these, hence the reducers.
    flags: Annotated[list[str], _merge_lists]
    errors: Annotated[list[str], _merge_lists]
    # Wall-clock milliseconds per agent call, taken from the client's own measurement (PRD §10
    # AgentTrace.latency_ms). Collected here because the client has no run or submission context, and
    # a free provider's latency is what the performance target in PRD §11 is set from.
    latencies: Annotated[dict[str, int], _merge_maps]
    # The user turn each agent call sent, per agent (Bab III, KNF-04: every step records its input).
    inputs: Annotated[dict[str, str], _merge_strings]
