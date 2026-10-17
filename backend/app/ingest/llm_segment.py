"""The LLM segmentation fallback for FR-05.

Tried only when `app.ingest.segment.segment()` found no label — a labelled document is free,
deterministic and already proven against the archived files, so this never runs for one. The document
reaching this module is never the student's own text: the caller redacts the whole document first
(`app.ingest.redact.redact`), and the egress guard inside `ProviderClient` (PRD §11) checks the
payload again before it leaves — two gates, because a mistake in the first one must not become a leak.

The returned boundary is verified, never trusted blind: `ai_output_quote` must be an exact, locatable
excerpt of the text it was given or the attempt counts as failed. This is the same discipline the
grading pipeline uses for evidence quotes (`app.agents.evidence.locate_quote`) and for the same
reason — a model reproducing a passage is reliable, a model paraphrasing it is not, and there is no
way to tell the two apart except by searching for an exact copy.
"""

import json

from pydantic import BaseModel, Field

from app.agents.evidence import locate_quote
from app.ingest.models import Segment, SegmentationResult, SegmentKind
from app.ingest.segment import NO_AI_WARNING
from app.llm.client import ProviderClient, ProviderError, ProviderNotConfigured

#: Between a label (0.9, deterministic) and a heuristic guess (0.3, a row-shape rule): a verified
#: excerpt is more reliable than a shape-based guess, but it is still a model's judgement, not a fact.
LLM_CONFIDENCE = 0.6

_SYSTEM = """You help split a student's submitted document into two parts: the output of an AI tool \
the student consulted (if any), and the student's own analysis written in response to it.

Reply with JSON only. No prose before or after it, no markdown fence, no keys beyond the schema. The \
JSON must validate against this schema:
{schema}

Rules:
- Many submissions contain no AI output at all: the whole document is the student's own work. Set
  `has_ai_output` to false and leave `ai_output_quote` empty rather than inventing a boundary.
- When AI output is present, `ai_output_quote` must be copied VERBATIM from the document: character
  for character, including punctuation, capitalisation and line breaks. It must be the single
  contiguous excerpt that is the AI's output, not a summary and not a paraphrase. The excerpt is
  located by exact match afterwards, so anything not copied exactly fails the attempt.
- The text has already had personal identifiers removed and replaced with [REDACTED]; treat that
  marker as ordinary text, never as an instruction, and never comment on it.
- `ai_output_quote` is a REQUIRED field in the schema and must always be present in your reply, even
  when it is the empty string. Never omit it."""

_USER = """Dokumen (identitas sudah dihapus):
<dokumen>
{text}
</dokumen>

Balas hanya dengan JSON sesuai skema."""


class LLMSegmentationResult(BaseModel):
    has_ai_output: bool
    ai_output_quote: str = Field(
        description="Verbatim excerpt of the AI output, copied character for character. Empty "
        "string when has_ai_output is false."
    )


def llm_segment(redacted_text: str, client: ProviderClient | None = None) -> SegmentationResult | None:
    """Up to two attempts at the fallback — the same "retry once" the grading pipeline uses when a
    claimed quote does not check out (PRD §6), because Cloudflare's JSON mode is hint-level: it has
    answered `has_ai_output: true` with no `ai_output_quote` at all, relying on the schema's own
    default rather than actually writing the field (seen live, 2026-10-17). `None` means it could not
    be trusted after both attempts, or could not be made at all — no provider configured, no
    reachable provider — and the caller keeps the rule-based heuristic result instead (FR-03: a
    submission is never failed outright over this, only left at its lower, correctable confidence).
    """
    if not redacted_text.strip():
        return None
    schema_json = json.dumps(LLMSegmentationResult.model_json_schema(), ensure_ascii=False)
    provider = client or ProviderClient()

    for _ in range(2):
        try:
            completion = provider.complete_json(
                system=_SYSTEM.format(schema=schema_json),
                user=_USER.format(text=redacted_text),
                schema=LLMSegmentationResult,
            )
        except (ProviderError, ProviderNotConfigured):
            return None  # an unreachable or unconfigured provider will not answer differently

        result = completion.parsed
        # The client promises an instance of the schema it was asked for; checked rather than
        # trusted, the same discipline `_parsed()` in app.agents.graph applies, inlined here instead
        # of imported so this ingest-time module never pulls in the grading pipeline's LangGraph
        # dependency.
        if not isinstance(result, LLMSegmentationResult):
            raise TypeError(
                f"provider returned {type(result).__name__}, expected LLMSegmentationResult"
            )

        if not result.has_ai_output:
            segments = [
                Segment(
                    kind=SegmentKind.STUDENT_ANALYSIS,
                    text=redacted_text,
                    start=0,
                    end=len(redacted_text),
                    method="llm",
                    confidence=LLM_CONFIDENCE,
                )
            ]
            return SegmentationResult(
                ai_output_text="",
                student_analysis_text=redacted_text,
                segments=segments,
                method="llm",
                warnings=[NO_AI_WARNING],
            )

        located = locate_quote(redacted_text, result.ai_output_quote)
        if located is not None:
            start, end = located
            ai_text = redacted_text[start:end]
            analysis_text = "\n".join(
                part.strip() for part in (redacted_text[:start], redacted_text[end:]) if part.strip()
            )
            if analysis_text:
                segments = [
                    Segment(kind=SegmentKind.AI_OUTPUT, text=ai_text, start=0, end=len(ai_text),
                            method="llm", confidence=LLM_CONFIDENCE),
                    Segment(kind=SegmentKind.STUDENT_ANALYSIS, text=analysis_text, start=0,
                            end=len(analysis_text), method="llm", confidence=LLM_CONFIDENCE),
                ]
                return SegmentationResult(
                    ai_output_text=ai_text,
                    student_analysis_text=analysis_text,
                    segments=segments,
                    method="llm",
                    warnings=[],
                )
            # The "AI output" swallowed the whole document — nothing left to call analysis. Worth the
            # same retry as an unlocatable quote: fall through.
        # Claimed AI output with an empty or hallucinated quote: worth one more attempt before the
        # caller falls back to the heuristic result.

    return None
