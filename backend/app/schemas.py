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


class ScoreOut(BaseModel):
    dimension: Literal["cognitive", "metacognitive"]
    indicator: str | None = None
    level: str
    rationale: str | None = None
    evidence: list[EvidenceOut] = Field(default_factory=list)


class SubmissionResultOut(BaseModel):
    submission_id: UUID
    pseudonym: str
    review_flags: list[str] = Field(default_factory=list)
    scores: list[ScoreOut] = Field(default_factory=list)
    feedback_text: str | None = None


class RunResultsOut(BaseModel):
    run_id: UUID
    status: str
    submissions: list[SubmissionResultOut] = Field(default_factory=list)


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


class RunRefOut(BaseModel):
    """Which run a submission's scores came from, for the detail view's header."""

    id: UUID
    status: str
    mode: str


class SubmissionScoreOut(BaseModel):
    """A score with the evidence the detail view highlights. Distinct from `ScoreOut`, which carries
    no id because the results table does not act on a score."""

    id: UUID
    dimension: Literal["cognitive", "metacognitive"]
    indicator: str | None = None
    level: str
    rationale: str | None = None
    evidence: list[EvidenceOut] = Field(default_factory=list)


class ReviewOut(BaseModel):
    system_score_id: UUID
    action: Literal["accept", "override"]
    new_level: str | None = None
    reason: str | None = None
    reviewed_at: dt.datetime


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
    segmentation_status: Literal["pending", "segmented", "confirmed", "failed"]
    import_warnings: list[str] = Field(default_factory=list)
    review_flags: list[str] = Field(default_factory=list)
    created_at: dt.datetime
    ai_output_text: str
    student_analysis_text: str
    rubric: RubricOut | None = None
    run: RunRefOut | None = None
    scores: list[SubmissionScoreOut] = Field(default_factory=list)
    feedback: FeedbackOut | None = None
    reviews: list[ReviewOut] = Field(default_factory=list)
