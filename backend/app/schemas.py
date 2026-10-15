"""Request and response models. Kept separate from the DB rows on purpose."""

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


class RunOut(BaseModel):
    id: UUID
    status: str
    mode: str
    jobs: dict[str, int] = Field(default_factory=dict)
    needs_review: int = 0
    processed: int = 0
    failed: int = 0
