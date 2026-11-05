"""The unit of assessment (Bab III.6) and the text-level aggregation (Bab I.3, luaran 4).

The thesis scores the student's analysis segment by segment, not as one block: a segment is one whole
sentence, except a sentence that only links two others and carries no analytical statement of its own,
which is merged into the sentence after it. Both the system and the expert raters label these same
units, so the split is deterministic — the same stored text always yields the same segments — and the
segment offsets are stored with every per-segment score.

Text-level scores are derived from the segment labels, never asked of a model separately: the highest
Bloom level over the segments for the cognitive dimension, and the set of indicators found in any
segment for the metacognitive one.
"""

import re

from pydantic import BaseModel, Field

# A sentence ends at ., ! or ? followed by whitespace, or at a blank line (a paragraph or list break). A
# single line break does not end one: extracted PDF text wraps lines in the middle of sentences.
_BOUNDARY = re.compile(r"(?<=[.!?])\s+|\n\s*\n")
# A connector sentence: too short to state anything on its own, or one that announces what follows.
# ponytail: word-count + trailing-colon heuristic; replace with the raters' finalised segmentation rule
# if the annotation guideline defines connectors differently.
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


def split_segments(text: str) -> list[Segment]:
    """Split `text` into sentence segments, merging each connector sentence into the next one."""
    spans: list[tuple[int, int]] = []
    position = 0
    for boundary in _BOUNDARY.finditer(text):
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
