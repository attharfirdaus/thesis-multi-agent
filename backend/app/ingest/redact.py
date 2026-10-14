"""Redaction of identifiers, run per segment before anything is stored or sent.

Detection is pattern-based on purpose: this deployment has no local model, so a name or ID is only
found when the text gives a shape to match — a label (`Nama : ...`), a cue word, or a number format.
Every removal becomes the one constant `MARKER`. The marker is deliberately not per-student: a
student-specific token would let the inference provider re-link submissions across runs, which is
exactly what O-7 forbids.

Known limit, not papered over: a name written with no cue at all ("Budi menyusun laporan ini") has
no reliable pattern and survives. Catching that needs a model, which this design does not have. The
compensating controls are the lecturer review flag on every auto-segmented submission (FR-05) and
`app.ingest.guard.assert_sendable`, which refuses a still-dirty payload at egress (FR-04).
"""

import re
from collections import Counter
from typing import NamedTuple

from app.ingest.models import RedactionClass, RedactionEvent, RedactionResult

MARKER = "[REDACTED]"

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Personal cloud links only: a Drive/Docs/Sheets URL is tied to one account, a public journal link
# is not and must survive so the lecturer can still see the student's sources.
# The final class is a token that cannot be sentence punctuation, so a link at the end of a
# sentence does not swallow the full stop next to it.
_PERSONAL_LINK = re.compile(
    r"https?://(?:docs|drive)\.google\.com/[^\s<>\"')\]]*[^\s<>\"')\].,;:]", re.IGNORECASE
)
# Separators are limited to [ \t.-] so a phone cannot be assembled across a line break.
_PHONE = re.compile(r"(?<![\d+])(?:\+62|0)[ \t.-]?8(?:[ \t.-]?\d){7,11}\b")
# The label is kept and only the value replaced, so the document's structure survives redaction.
# It also has to accept the table-cell shape, `Nama | : Muhammad ...`, because extraction joins a
# row's cells with " | " and the colon lives in the second cell there.
_NAME_LABEL = re.compile(
    r"\bNama(?:\s+(?:Mahasiswa|Lengkap))?\b\s*(?:\||:|=)\s*:?\s*(?P<value>[^|\n]+)",
    re.IGNORECASE,
)
_NIM_CUE = re.compile(r"\b(?:NIM|NIP)\b", re.IGNORECASE)
_EIGHT_DIGITS = re.compile(r"\b\d{8}\b")
# A capitalised run is almost always an institution or a product in Indonesian academic prose, so
# this cue rule over-redacts. That is the safe direction: the marker hides a false positive, whereas
# a miss leaks a name, and the lecturer sees an over-redaction at review time.
_NAMED_PERSON = re.compile(
    r"\b(?:nama saya|saya,|penulis|oleh)\s*:?\s*([A-Z][A-Za-z']*(?:\s+[A-Z][A-Za-z']*){1,3})"
)

_FORMAT_PATTERNS = (
    (_EMAIL, RedactionClass.EMAIL),
    (_PERSONAL_LINK, RedactionClass.PERSONAL_LINK),
    (_PHONE, RedactionClass.PHONE),
)


class _Span(NamedTuple):
    start: int
    end: int
    cls: RedactionClass


def _lines(text: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    offset = 0
    for line in text.split("\n"):
        lines.append((offset, line))
        offset += len(line) + 1
    return lines


def _scan(text: str) -> list[_Span]:
    """Every identifier occurrence, as non-overlapping spans sorted by position."""
    spans: list[_Span] = []

    for pattern, cls in _FORMAT_PATTERNS:
        spans.extend(_Span(m.start(), m.end(), cls) for m in pattern.finditer(text))

    for match in _NAME_LABEL.finditer(text):
        value = match["value"].strip()
        if not value or value == MARKER:
            # An empty value is a label-only cell; the marker is our own output, so re-checking a
            # redacted document (the guard does exactly that) must not flag it again.
            continue
        left = len(match["value"]) - len(match["value"].lstrip())
        start = match.start("value") + left
        spans.append(_Span(start, start + len(value), RedactionClass.NAME_LABEL))

    # An 8-digit figure is only a student ID when an ID cue shares its line; the same documents are
    # full of legitimate figures, so a bare 8-digit run must never be removed on its own.
    for offset, line in _lines(text):
        if _NIM_CUE.search(line):
            spans.extend(
                _Span(offset + m.start(), offset + m.end(), RedactionClass.STUDENT_ID)
                for m in _EIGHT_DIGITS.finditer(line)
            )

    spans.extend(
        _Span(m.start(1), m.end(1), RedactionClass.NAMED_PERSON) for m in _NAMED_PERSON.finditer(text)
    )

    kept: list[_Span] = []
    for span in sorted(spans, key=lambda s: (s.start, -s.end)):
        if not kept or span.start >= kept[-1].end:
            kept.append(span)
    return kept


def _counts(spans: list[_Span]) -> dict[RedactionClass, int]:
    counted = Counter(span.cls for span in spans)
    return {cls: counted[cls] for cls in RedactionClass if counted[cls]}


def _apply(text: str, spans: list[_Span]) -> str:
    parts: list[str] = []
    cursor = 0
    for span in spans:
        parts.append(text[cursor : span.start])
        parts.append(MARKER)
        cursor = span.end
    parts.append(text[cursor:])
    return "".join(parts)


def find_identifiers(text: str) -> dict[RedactionClass, int]:
    """Counts of identifiers per class, never the values.

    Exposed separately because `app.ingest.guard` reuses the detector as its egress check; the
    counts-only contract is what lets a blocked send be logged and escalated without copying the
    student's data into the log.
    """
    return _counts(_scan(text))


def redact(text: str) -> RedactionResult:
    """Replace every detected identifier with `MARKER`, reporting counts only.

    Per the limits in the module docstring, a cue-less name is not detected here; `guard` and the
    lecturer review flag are the backstops. The returned `text` is what gets stored (FR-04), so no
    removed value appears in it, in `events`, or in any log written from this function.
    """
    spans = _scan(text)
    events = [RedactionEvent(cls=cls, count=count) for cls, count in _counts(spans).items()]
    return RedactionResult(text=_apply(text, spans), events=events)
