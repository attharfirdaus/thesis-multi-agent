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

Strength = Literal["low", "medium", "high"]


class CognitiveResult(BaseModel):
    """Bloom level for the student's own analysis. The level must be one of the rubric's levels;
    the pipeline rejects anything else rather than storing an invented label."""

    level: str = Field(description="Exactly one of the rubric's cognitive levels.")
    evidence_quote: str = Field(min_length=10, description="Verbatim text from the student's analysis.")
    rationale: str = Field(min_length=10, description="Why this level, in one or two sentences.")


class IndicatorFinding(BaseModel):
    indicator: str = Field(description="Exactly one of the rubric's metacognitive indicator codes.")
    present: bool
    strength: Strength | None = Field(
        default=None, description="Only meaningful when present is true."
    )
    evidence_quote: str = Field(
        default="", description="Verbatim text from the student's analysis; empty when absent."
    )
    rationale: str = Field(min_length=5)


class MetacognitiveResult(BaseModel):
    findings: list[IndicatorFinding] = Field(min_length=1)


class SynthesisResult(BaseModel):
    """What the lecturer reads. `rationale` explains the scores, `feedback_text` is the per-student
    feedback of FR-19 that the lecturer may edit before export."""

    rationale: str = Field(min_length=20)
    feedback_text: str = Field(min_length=20)


class EvidenceSpan(BaseModel):
    """A quote that was located in the stored text, with the offsets the database will keep.

    Offsets point into `student_analysis_text`, or into `ai_output_text` when the synthesis agent
    quotes the AI answer while explaining itself. `source` says which agent produced the quote, so a
    lecturer can see who is being held to account for it.
    """

    source: Literal["cognitive", "metacognitive"]
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


class GraphState(TypedDict, total=False):
    """The LangGraph channel definition.

    `flags` merges instead of overwriting, because two agents running in parallel each raise their own
    concerns and the synthesis step has to see both.
    """

    # Identity and configuration, set once by the caller.
    owner_id: str
    run_id: str
    submission_id: str
    rubric: dict
    prompts: dict

    # Input, already redacted by phase 3. Nothing else from the submission ever enters this state.
    student_analysis_text: str
    ai_output_text: str

    # Agent output.
    cognitive: CognitiveResult | None
    metacognitive: MetacognitiveResult | None
    synthesis: SynthesisResult | None

    # Evidence, filled by the evidence node after the agents have run. Only that node writes these,
    # so plain (overwriting) channels are correct — a reducer would let a later node silently append
    # stale spans.
    evidence: list[EvidenceSpan]
    evidence_failures: list[str]

    # Bookkeeping. Both parallel agents write these, hence the reducers.
    flags: Annotated[list[str], _merge_lists]
    errors: Annotated[list[str], _merge_lists]
