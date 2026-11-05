"""Request and response models. Kept separate from the DB rows on purpose."""

import datetime as dt
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SignupIn(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=200)
    password: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    email: str
    name: str
    role: Literal["lecturer", "admin"]


class MeOut(BaseModel):
    user: UserOut


class HealthOut(BaseModel):
    status: Literal["ok"]
    env: str
    database: Literal["ok", "error"]


class ImportedSubmission(BaseModel):
    """One file's outcome. FR-03: a bad file is reported, it does not fail the batch."""

    filename: str
    status: Literal["imported", "failed"]
    submission_id: UUID | None = None
    pseudonym: str | None = None
    segmentation_method: str | None = None
    has_ai_output: bool | None = None
    removed_by_class: dict[str, int] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None


class ImportResult(BaseModel):
    assignment_id: UUID
    files: list[ImportedSubmission]


class SubmissionOut(BaseModel):
    id: UUID
    assignment_id: UUID
    pseudonym: str
    #: The student's real name, from `app.ingest.identity_store` (DECISIONS.md, 2026-10-16) — never
    #: from an agent, never stored alongside the redacted text. `None` when ingest found no name to
    #: capture, or when the local store has nothing for this submission.
    real_name: str | None = None
    segmentation_status: Literal["pending", "segmented", "confirmed", "failed"]
    has_ai_output: bool
    analysis_chars: int
    import_warnings: list[str] = Field(default_factory=list)


class SegmentationPatch(BaseModel):
    """The lecturer's corrected boundary, as an offset into the combined document text."""

    analysis_start: int = Field(ge=0)


class EvidenceOut(BaseModel):
    quote: str
    start_offset: int
    end_offset: int


class ReviewOut(BaseModel):
    system_score_id: UUID
    action: Literal["accept", "override"]
    new_level: str | None = None
    reason: str | None = None
    reviewed_at: dt.datetime


class ScoreOut(BaseModel):
    dimension: Literal["cognitive", "metacognitive"]
    indicator: str | None = None
    #: The score's own id, so a review note can be attached to the score it judges. Optional because the
    #: results payload builds a score for a submission a run never reached as well.
    id: UUID | None = None
    level: str
    rationale: str | None = None
    evidence: list[EvidenceOut] = Field(default_factory=list)
    #: The lecturer's newest review of this score, or None when nobody has judged it. The dialog needs the
    #: reason next to the grade it overrides, which is also how the export pairs them.
    review: ReviewOut | None = None
    #: KF-07: segments per level group, on the text-level cognitive score only.
    distribution: dict[str, int] | None = None


class SubmissionResultOut(BaseModel):
    submission_id: UUID
    pseudonym: str
    real_name: str | None = None
    review_flags: list[str] = Field(default_factory=list)
    scores: list[ScoreOut] = Field(default_factory=list)
    #: What the export will write: the lecturer's edit when there is one, otherwise the generated text.
    #: The results screen previews the export, so it has to read the same expression the export does.
    feedback_text: str | None = None
    feedback_edited: bool = False


class RunResultsOut(BaseModel):
    run_id: UUID
    status: str
    submissions: list[SubmissionResultOut] = Field(default_factory=list)
    #: Same map as `RubricOut.level_names`, for the run the results came from: the results table names a
    #: level ("C4 Analyze") without a second request per row.
    level_names: dict[str, str] = Field(default_factory=dict)


class InFlightOut(BaseModel):
    """The submission a job is grading right now.

    The lecturer's screen can show what it is working on, not only how much is left: the counts say
    "2 of 4", and this says which one is being read.
    """

    submission_id: UUID
    pseudonym: str


class RunOut(BaseModel):
    id: UUID
    status: str
    mode: str
    #: Bab III.2.4/III.9: the R runs created together with one configuration share a group.
    repetition_group: UUID | None = None
    repetition_index: int = 1
    repetitions: int = 1
    #: Every run of the group, on the create response only, so a caller can drive them all.
    group_run_ids: list[UUID] = Field(default_factory=list)
    final_evaluation: bool = False
    #: The provider no longer serves the model this run snapshotted (KNF-04).
    model_unavailable: bool = False
    jobs: dict[str, int] = Field(default_factory=dict)
    needs_review: int = 0
    processed: int = 0
    failed: int = 0
    in_flight: list[InFlightOut] = Field(default_factory=list)


# --------------------------------------------------------------- lecturer UI (phase 5)


class LatestRunOut(BaseModel):
    """The one run the dashboard shows per assignment. A subset of `RunOut`: the list screen has no
    use for the per-job counters, and progress comes from the run's own endpoint."""

    id: UUID
    status: str
    jobs: dict[str, int] = Field(default_factory=dict)


class AssignmentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    course: str = Field(min_length=1, max_length=200)
    prompt_text: str = ""


class AssignmentSummaryOut(BaseModel):
    id: UUID
    title: str
    course: str
    prompt_text: str
    created_at: dt.datetime
    submission_count: int
    #: How many of those submissions any run has already scored. The lecturer's "grade what is new"
    #: choice needs it: without it the screen cannot say how much work a run would actually do, nor why
    #: nothing would happen.
    graded_count: int = 0
    latest_run: LatestRunOut | None = None


class SubmissionSummaryOut(SubmissionOut):
    """The ingest view plus the machine-written flags: the results table marks "perlu ditinjau" from
    here, without a request per row (FR-09)."""

    review_flags: list[str] = Field(default_factory=list)


class AssignmentDetailOut(AssignmentSummaryOut):
    submissions: list[SubmissionSummaryOut] = Field(default_factory=list)
    runs: list[RunOut] = Field(default_factory=list)


class RubricOut(BaseModel):
    version: str
    levels: list[str] = Field(default_factory=list)
    indicators: list[str] = Field(default_factory=list)
    #: `{"C4": "Analyze"}` — the readable name of each level code, from the rubric row itself. A rubric
    #: seeded before names existed carries none, and the UI then shows the code alone rather than
    #: inventing a word for it.
    level_names: dict[str, str] = Field(default_factory=dict)


class RunRefOut(BaseModel):
    """Which run a submission's scores came from, for the detail view's header."""

    id: UUID
    status: str
    mode: str


class CommentOut(BaseModel):
    id: UUID
    system_score_id: UUID
    body: str
    created_at: dt.datetime


class CommentIn(BaseModel):
    body: str = Field(min_length=1, max_length=4000)


class SubmissionScoreOut(BaseModel):
    """A score with the evidence the detail view highlights. Distinct from `ScoreOut`, which carries
    no id because the results table does not act on a score."""

    id: UUID
    dimension: Literal["cognitive", "metacognitive"]
    indicator: str | None = None
    level: str
    rationale: str | None = None
    evidence: list[EvidenceOut] = Field(default_factory=list)
    comments: list[CommentOut] = Field(default_factory=list)
    # KF-07: segments per level group, on the text-level cognitive score only.
    distribution: dict[str, int] | None = None


class SegmentScoreOut(BaseModel):
    """One segment's label (Bab III.6): the unit behind the text-level score."""

    id: UUID
    segment_index: int
    segment_start: int
    segment_end: int
    dimension: Literal["cognitive", "metacognitive"]
    indicator: str | None = None
    level: str
    rationale: str | None = None
    evidence: list[EvidenceOut] = Field(default_factory=list)
    # KF-09: a segment label is accepted, corrected or commented on like a text-level score.
    comments: list[CommentOut] = Field(default_factory=list)


ExclusionReason = Literal["calibration_source", "author_own", "unreadable_or_unsegmentable"]


class ReviewIn(BaseModel):
    action: Literal["accept", "override"]
    new_level: str | None = None
    reason: str | None = None


class FeedbackOut(BaseModel):
    generated_text: str
    edited_text: str | None = None
    edited_by: UUID | None = None
    exported_at: dt.datetime | None = None


class FeedbackPatch(BaseModel):
    """The lecturer's edit. `None` or blank text means "no edit" and clears `edited_text` (FR-19)."""

    edited_text: str | None = None


class SubmissionDetailOut(BaseModel):
    id: UUID
    # The detail screen is reached from a results table and has to be able to link back to its
    # assignment; without this the lecturer's only way back is the browser's own history.
    assignment_id: UUID
    pseudonym: str
    real_name: str | None = None
    segmentation_status: Literal["pending", "segmented", "confirmed", "failed"]
    import_warnings: list[str] = Field(default_factory=list)
    review_flags: list[str] = Field(default_factory=list)
    created_at: dt.datetime
    ai_output_text: str
    student_analysis_text: str
    rubric: RubricOut | None = None
    run: RunRefOut | None = None
    scores: list[SubmissionScoreOut] = Field(default_factory=list)
    segment_scores: list[SegmentScoreOut] = Field(default_factory=list)
    feedback: FeedbackOut | None = None
    reviews: list[ReviewOut] = Field(default_factory=list)
    exclusion_reason: ExclusionReason | None = None


class ExclusionPatch(BaseModel):
    """Tabel III.4. `None` puts the submission back into the evaluation set."""

    reason: ExclusionReason | None = None


# --------------------------------------------------------------- admin area (Bab III.3)


class AdminUserOut(BaseModel):
    id: UUID
    email: str
    name: str
    role: Literal["lecturer", "admin"]
    created_at: dt.datetime


class RubricVersionOut(BaseModel):
    id: UUID
    version: int
    levels: list[str]
    indicators: list[str]
    descriptors: dict
    frozen_at: dt.datetime | None = None
    created_at: dt.datetime


class RubricIn(BaseModel):
    """A new rubric version (KF-12). Versions are immutable; saving always inserts version + 1."""

    levels: list[str] = Field(min_length=1)
    indicators: list[str] = Field(min_length=1)
    descriptors: dict = Field(default_factory=dict)


class PromptVersionOut(BaseModel):
    id: UUID
    agent_name: str
    version: int
    frozen_at: dt.datetime | None = None
    created_at: dt.datetime


class AdminConfigOut(BaseModel):
    #: What a new run would snapshot (FR-13); the API key is never part of it.
    llm: dict
    prompt_versions: list[PromptVersionOut]


class AdminRunOut(BaseModel):
    id: UUID
    assignment_id: UUID
    assignment_title: str
    mode: str
    status: str
    repetition_group: UUID | None = None
    repetition_index: int
    repetitions: int
    final_evaluation: bool
    model_unavailable: bool
    model: str | None = None
    created_at: dt.datetime


class TraceOut(BaseModel):
    id: UUID
    submission_pseudonym: str | None = None
    agent_name: str
    input_ref: str | None = None
    output_json: dict | None = None
    latency_ms: int | None = None
    error: str | None = None
    created_at: dt.datetime
