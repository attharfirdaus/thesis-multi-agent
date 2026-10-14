"""Segmentation: `ExtractedDocument` in, `SegmentationResult` out.

The archived submissions are Word tables exported to PDF, and the first column of a row is the
only reliable boundary between the AI's answer and the student's own work. Two facts about those
files drive every branch below:

* a merged cell continues into the next row with an *empty* first cell, so a blank first cell means
  "more of the previous segment", never "something new" — misreading it moves a paragraph into the
  wrong artefact, which is why the segmenter tracks the region a row opened;
* the column header (`| Prompt | Hasil |`) repeats after every page break and carries no text of
  its own, so it restarts the pairing and contributes nothing.

Five of the nine archived files contain no AI output at all. That is the normal case, not an error:
the student segment covers the whole document and a warning says no AI segment was found.

When no label exists the segmenter guesses (a short row that asks a question, followed by a long
one, reads as question-then-answer) and reports the lower confidence, so the lecturer confirms or
corrects the boundary the ingest router offers them (FR-05). A shape that fits but asks nothing is
not a guess: the whole document stays with the student.
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Literal

from app.ingest.models import (
    Block,
    BlockKind,
    ExtractedDocument,
    Segment,
    SegmentationResult,
    SegmentKind,
)

Method = Literal["label", "heuristic"]

ANALYSIS_LABEL = "critical review"
PROMPT_LABEL = "prompt"
ANSWER_LABEL = "hasil"
LABELS = frozenset({ANALYSIS_LABEL, PROMPT_LABEL, ANSWER_LABEL})
# `| Prompt | Hasil |` names the two columns. Treating "Hasil" as content would put a table header
# into the AI answer it heads.
HEADER_CELLS = frozenset({PROMPT_LABEL, ANSWER_LABEL})

# A label decides a boundary; a guess does not. The gap is what the UI keys off to ask the lecturer
# to check the low-confidence segment.
LABEL_CONFIDENCE = 0.9
GUESS_CONFIDENCE = 0.3

# Row-shape heuristic bounds. Real question rows are one-liners and real answer rows are
# paragraphs; a pair outside both bounds is left with the student as analysis rather than guessed.
SHORT_ROW_MAX = 200
LONG_ROW_MIN = 400

# Row shape alone is not enough to call a short row a question: an unlabelled table whose first
# column is short and second long sorts the student's own work into the AI region. The wording has
# to ask something too, which is what these cues check.
QUESTION_CUES = frozenset(
    {
        "apa",
        "apakah",
        "bagaimana",
        "berikan",
        "buatkan",
        "jelaskan",
        "kapan",
        "kenapa",
        "mengapa",
        "mohon",
        "sebutkan",
        "siapa",
        "tolong",
        "uraikan",
    }
)

NO_AI_WARNING = "no AI segment was detected; the student's analysis covers the whole document"


@dataclass
class _Run:
    """One uninterrupted stretch of a single kind, in document order.

    Rows of the same kind are merged into one run so a table split across a page break becomes one
    segment rather than several the lecturer would have to stitch back together.
    """

    kind: SegmentKind
    method: Method
    confidence: float
    parts: list[str] = field(default_factory=list)
    prompt: str | None = None

    @property
    def text(self) -> str:
        return "\n".join(self.parts)


def _label_of(block: Block) -> str:
    if block.kind is not BlockKind.TABLE_ROW:
        return ""
    cells = block.cells if block.cells else [block.text]
    return cells[0].strip().casefold() if cells else ""


def _body_of(block: Block, *, drop_label: bool) -> str:
    """Cells joined with the same separator `Block.text` uses, minus the label cell when the label
    is a real label: "critical review" names the column, it is not part of the student's sentence."""
    cells = block.cells if block.cells else [block.text]
    body = cells[1:] if drop_label else cells
    return " | ".join(cell.strip() for cell in body if cell.strip())


def _has_label(blocks: Iterable[Block]) -> bool:
    return any(_label_of(block) in LABELS for block in blocks)


def _add(
    runs: list[_Run],
    kind: SegmentKind,
    text: str,
    method: Method,
    confidence: float,
    prompt: str | None = None,
) -> None:
    text = text.strip()
    if not text and not prompt:
        return
    if runs and runs[-1].kind is kind:
        run = runs[-1]
        if text:
            run.parts.append(text)
        if method == "heuristic":
            run.method = "heuristic"
        run.confidence = min(run.confidence, confidence)
        if prompt and not run.prompt:
            run.prompt = prompt
        return
    runs.append(
        _Run(kind=kind, method=method, confidence=confidence, parts=[text] if text else [], prompt=prompt)
    )


def _place(runs: Sequence[_Run], kind: SegmentKind) -> tuple[str, list[Segment]]:
    """Lay one kind's runs end to end and record where each landed.

    `start`/`end` index the returned string, which is what `Evidence.start_offset` will point into,
    so the slice at those offsets must reproduce the segment text exactly.
    """
    text = ""
    segments: list[Segment] = []
    for run in runs:
        if run.kind is not kind or not run.parts:
            continue
        separator = "\n" if text else ""
        start = len(text) + len(separator)
        text = f"{text}{separator}{run.text}"
        segments.append(
            Segment(
                kind=kind,
                text=run.text,
                start=start,
                end=start + len(run.text),
                method=run.method,
                confidence=run.confidence,
                prompt_text=run.prompt,
            )
        )
    return text, segments


def _segment_labelled(blocks: Sequence[Block]) -> list[_Run]:
    runs: list[_Run] = []
    current: SegmentKind | None = None
    pending_prompt: str | None = None

    for block in blocks:
        if block.kind is BlockKind.IMAGE_ONLY:
            continue
        label = _label_of(block)
        body = _body_of(block, drop_label=label in LABELS)

        if label == ANALYSIS_LABEL:
            current = SegmentKind.STUDENT_ANALYSIS
            _add(runs, current, body, "label", LABEL_CONFIDENCE)

        elif label in (PROMPT_LABEL, ANSWER_LABEL):
            current = SegmentKind.AI_OUTPUT
            if label == PROMPT_LABEL:
                if body and body.casefold() not in HEADER_CELLS:
                    # The student's question is context for the answer, never AI output, so it is
                    # carried on the segment instead of concatenated into the text that gets scored.
                    pending_prompt = body
            else:
                prompt, pending_prompt = pending_prompt, None
                _add(runs, current, body, "label", LABEL_CONFIDENCE, prompt)

        elif current is SegmentKind.AI_OUTPUT:
            prompt, pending_prompt = pending_prompt, None
            _add(runs, current, body, "label", LABEL_CONFIDENCE, prompt)

        else:
            # A paragraph or heading is never a boundary: it is either a cell continuation that
            # pdfplumber left outside the detected table, or a page header. It continues whatever
            # region is open — and before the first label that region is the student's analysis,
            # which is also where a standalone header belongs. The document is known to carry a
            # label (`_segment_labelled` only runs then), so this text is not a guess.
            _add(runs, SegmentKind.STUDENT_ANALYSIS, body, "label", LABEL_CONFIDENCE)

    return runs


def _looks_like_question(text: str) -> bool:
    """A short row only counts as a question when its wording asks one.

    Literal "begins with" would read `apabila` as `apa`, so the first word is compared whole.
    """
    folded = text.strip().casefold()
    if folded.endswith("?"):
        return True
    words = folded.split(maxsplit=1)
    return bool(words) and words[0].rstrip(".,:;!?()") in QUESTION_CUES


def _segment_guessed(blocks: Sequence[Block]) -> list[_Run]:
    texts: list[str] = []
    for block in blocks:
        if block.kind is BlockKind.IMAGE_ONLY:
            continue
        text = _body_of(block, drop_label=False)
        if text:
            texts.append(text)

    runs: list[_Run] = []
    index = 0
    while index < len(texts):
        question = texts[index]
        answer = texts[index + 1] if index + 1 < len(texts) else None
        if (
            answer is not None
            and len(question) <= SHORT_ROW_MAX
            and _looks_like_question(question)
            and len(answer) >= LONG_ROW_MIN
        ):
            _add(runs, SegmentKind.AI_OUTPUT, answer, "heuristic", GUESS_CONFIDENCE, question)
            index += 2
        else:
            _add(runs, SegmentKind.STUDENT_ANALYSIS, question, "heuristic", GUESS_CONFIDENCE)
            index += 1
    return runs


def segment(doc: ExtractedDocument) -> SegmentationResult:
    """Split the extracted blocks into the AI's output and the student's own analysis.

    Labels decide when the document has any; otherwise the whole thing is a low-confidence guess.
    A document with no AI output at all comes back with an empty `ai_output_text`, whatever method
    was used to look for one, and a warning rather than an error.
    """
    labelled = _has_label(doc.blocks)
    runs = _segment_labelled(doc.blocks) if labelled else _segment_guessed(doc.blocks)

    ai_output_text, ai_segments = _place(runs, SegmentKind.AI_OUTPUT)
    student_analysis_text, student_segments = _place(runs, SegmentKind.STUDENT_ANALYSIS)

    method: Literal["label", "heuristic", "none"] = "label" if labelled else "heuristic"
    if not ai_output_text and not labelled:
        method = "none"

    return SegmentationResult(
        ai_output_text=ai_output_text,
        student_analysis_text=student_analysis_text,
        # The AI's answer precedes the analysis in every archived file, so this is document order.
        segments=ai_segments + student_segments,
        method=method,
        warnings=[] if ai_output_text else [NO_AI_WARNING],
    )
