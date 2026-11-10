"""The unit of assessment (Bab III.6) and the text-level aggregation (Bab I.3, luaran 4).

The thesis scores the student's analysis segment by segment, not as one block: a segment is one whole
sentence, except a sentence that only links two others and carries no analytical statement of its own,
which is merged into the sentence after it. Both the system and the expert raters label these same
units, so the split is deterministic — the same stored text always yields the same segments — and the
segment offsets are stored with every per-segment score.

Text-level scores are derived from the segment labels, never asked of a model separately: the highest
Bloom level over the segments and the spread of segments over the three level groups for the cognitive
dimension, and the set of indicators found in any segment for the metacognitive one.

The split is stored on the submission when the analysis is set (KF-05), so it is fixed before the raters
or any run see it; `split_segments` is only re-applied to rows imported before that column existed.
"""

import re

from pydantic import BaseModel, Field

# A sentence ends at ., ! or ? followed by whitespace, at a blank line (a paragraph break), or at a line
# break before a list item ("2. …", "- …"). Any other single line break does not end one: extracted PDF
# text wraps lines in the middle of sentences.
_BOUNDARY = re.compile(r"(?<=[.!?])\s+|\n\s*\n|\n(?=[ \t]*(?:\d{1,2}[.)]|[-•–*])[ \t])")
# Three places a full stop is not the end of a sentence (all seen on real submissions, 2026-11-10; the
# rule was extended on Atthar's instruction the same day, and applies to submissions imported from then
# on — a stored split is never recomputed, KF-05):
# - a list number: "adalah:\n1." used to end a segment and strip the number from its own item;
# - an abbreviation that is always followed by what it abbreviates, or a citation "et al. (2020)";
# - a lower-case letter on the same line after it: a sentence does not start that way.
_LIST_MARKER = re.compile(r"\s*(?:\d{1,2}|[A-Za-z])[.)]\s*")
_ABBREVIATIONS = frozenset({"no.", "hlm.", "dr.", "prof.", "vs.", "e.g.", "i.e."})
_CITATION_ABBREVIATIONS = frozenset({"al.", "dkk."})
# A connector sentence (Bab III.6): fewer than 4 words, or ending in ":" because it announces what
# follows. This is the final rule (Atthar, 2026-11-05); the annotation guideline and Bab IV state it, so
# the raters and the system split the same way. Changing it changes the thesis's unit of assessment.
_MIN_WORDS = 4


class Segment(BaseModel):
    """One assessed unit. `index` is 1-based, as the prompt and the rater sheet number them; offsets are
    half-open and point into the stored `student_analysis_text`."""

    index: int = Field(ge=1)
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    text: str


def _is_connector(sentence: str) -> bool:
    return sentence.rstrip().endswith(":") or len(sentence.split()) < _MIN_WORDS


def _ends_sentence(text: str, position: int, boundary: re.Match[str]) -> bool:
    """Whether `boundary` really closes the sentence that started at `position`."""
    gap = boundary.group()
    if boundary.start() == 0 or text[boundary.start() - 1] not in ".!?" or gap.count("\n") > 1:
        return True  # a paragraph break, or a line break before a list item
    sentence = text[position : boundary.start()]
    if _LIST_MARKER.fullmatch(sentence):
        return False
    if text[boundary.start() - 1] != ".":
        return True
    last_word = sentence.split()[-1].casefold() if sentence.split() else ""
    following = text[boundary.end() : boundary.end() + 1]
    if last_word in _ABBREVIATIONS or (last_word in _CITATION_ABBREVIATIONS and following == "("):
        return False
    return "\n" in gap or not following.islower()


def split_segments(text: str) -> list[Segment]:
    """Split `text` into sentence segments, merging each connector sentence into the next one."""
    spans: list[tuple[int, int]] = []
    position = 0
    for boundary in _BOUNDARY.finditer(text):
        if not _ends_sentence(text, position, boundary):
            continue
        if boundary.start() > position:
            spans.append((position, boundary.start()))
        position = boundary.end()
    if position < len(text):
        spans.append((position, len(text)))
    spans = [(s, e) for s, e in spans if text[s:e].strip()]

    merged: list[tuple[int, int]] = []
    pending_start: int | None = None
    for position, (start, end) in enumerate(spans):
        start = start if pending_start is None else pending_start
        # The last sentence has nothing after it to merge into, so it stands even when it is short.
        if position < len(spans) - 1 and _is_connector(text[start:end]):
            pending_start = start
            continue
        pending_start = None
        merged.append((start, end))

    return [
        Segment(index=number, start=start, end=end, text=text[start:end])
        for number, (start, end) in enumerate(merged, start=1)
    ]


def numbered(segments: list[Segment]) -> str:
    """The analysis as the agents read it: one segment per line, prefixed with its number."""
    return "\n".join(f"[{segment.index}] {segment.text}" for segment in segments)


def highest_level(levels: list[str], rubric_levels: list[str]) -> str | None:
    """The highest of `levels` in the rubric's own order (C1 < … < C6), or None when there is none."""
    ranked = [level for level in levels if level in rubric_levels]
    return max(ranked, key=rubric_levels.index) if ranked else None


def stored(segments: list[Segment]) -> list[dict]:
    """The form `submissions.analysis_segments` keeps (KF-05): the split, fixed before measurement."""
    return [segment.model_dump() for segment in segments]


def from_stored(value: list[dict] | None, text: str) -> list[Segment]:
    """The stored split, or — for a row imported before it was stored — the same rule applied now."""
    return [Segment(**item) for item in value] if value else split_segments(text)


def distribution(levels: list[str], groups: dict[str, list[str]]) -> dict[str, int]:
    """How many segments fall in each level group (Bab III.6: lower / medium / higher order, after Xu Li
    dkk., 2026). The groups are rubric data, so a rubric without them yields an empty distribution."""
    return {name: sum(level in members for level in levels) for name, members in groups.items()}
