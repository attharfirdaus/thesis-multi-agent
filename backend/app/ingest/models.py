"""Typed contracts for ingestion (phase 3).

These are frozen on purpose: the extractor, the segmenter, the redactor and the endpoints all
speak them, so the three implementations can be written independently.

Pipeline order, and why: **extract → segment → redact → store.**

1. *Extract* needs the original structure, because the source documents are tables whose
   first column carries the only reliable label ("Critical Review").
2. *Segment* therefore runs on the structured blocks, before any text is destroyed.
3. *Redact* runs last, per segment, so identifiers inside the student's own prose are removed
   from the artefact that is stored and sent.
4. Offset semantics follow from that order: `Evidence.start_offset` in the database refers to
   the **stored, already-redacted** segment text, so it can never point at a removed identifier.
"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class BlockKind(StrEnum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    TABLE_ROW = "table_row"
    IMAGE_ONLY = "image_only"  # a page or block with no extractable text; flagged, never sent


class Block(BaseModel):
    """One structural unit of the source document, before segmentation.

    Invariant for TABLE_ROW: `text == " | ".join(cells)`. Everything else has `cells is None`.
    """

    kind: BlockKind
    text: str
    order: int
    page: int | None = None
    cells: list[str] | None = None


class ExtractedDocument(BaseModel):
    """Everything the extractor produces. Only `blocks` survives into segmentation."""

    filename: str
    source_format: Literal["pdf", "docx", "txt"]
    blocks: list[Block] = Field(default_factory=list)
    # Document properties (author, creator, last modified by). Logged as a count, never stored.
    metadata: dict[str, str] = Field(default_factory=dict)
    # Extraction caveats worth surfacing to the lecturer, e.g. a page with no text layer.
    warnings: list[str] = Field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(b.text for b in self.blocks)

    @property
    def has_text(self) -> bool:
        return any(b.kind is not BlockKind.IMAGE_ONLY and b.text.strip() for b in self.blocks)


class SegmentKind(StrEnum):
    AI_OUTPUT = "ai_output"
    STUDENT_ANALYSIS = "student_analysis"


class Segment(BaseModel):
    kind: SegmentKind
    text: str
    start: int
    end: int
    # How the boundary was decided. "lecturer" means a human corrected it, which must survive
    # a re-run: FR-05 says the auto-segmenter proposes and the lecturer disposes.
    method: Literal["label", "heuristic", "lecturer"]
    confidence: float | None = None
    # The prompt the student gave the AI, when the document labels it. Useful context for the
    # synthesis agent; not the student's own work, so never scored.
    prompt_text: str | None = None


class SegmentationResult(BaseModel):
    ai_output_text: str
    student_analysis_text: str
    segments: list[Segment] = Field(default_factory=list)
    method: Literal["label", "heuristic", "none"]
    warnings: list[str] = Field(default_factory=list)

    @property
    def has_ai_output(self) -> bool:
        return bool(self.ai_output_text.strip())


class RedactionClass(StrEnum):
    NAME_LABEL = "name_label"
    STUDENT_ID = "student_id"
    EMAIL = "email"
    PHONE = "phone"
    PERSONAL_LINK = "personal_link"
    NAMED_PERSON = "named_person"


class RedactionEvent(BaseModel):
    """Counts only. The removed value is never recorded anywhere — that is the point of FR-04."""

    cls: RedactionClass
    count: int


class RedactionResult(BaseModel):
    text: str
    events: list[RedactionEvent] = Field(default_factory=list)

    @property
    def total_removed(self) -> int:
        return sum(e.count for e in self.events)
