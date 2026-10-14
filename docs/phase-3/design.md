# Phase 3 design — ingestion, segmentation and redaction

Constraint that shapes everything below: **the archived submissions are Word tables exported to
PDF**, and the only reliable boundary between the AI's answer and the student's own analysis is the
label in the first column of a table row. This was established by inspecting the real files on
2026-10-06, not assumed.

## What the real files look like

Four of the nine archived submissions contain AI output, and all four share one shape — a two-column
table repeated once per prompt:

```
| Prompt          | Hasil            |   ← the student's question, then the AI's answer
| Critical Review | <student text>   |   ← the student's own analysis
```

The other five (Tugas 5–8 and Tugas Akhir) contain **no AI output at all** — they are pure student
analysis with their own tables. A submission with no AI segment is therefore a normal case, not an
error: `SegmentationResult.has_ai_output` is false and the whole document is student analysis.

### Extraction hazards observed in the real files

1. **Merged cells split across rows.** The AI answer continues in the next row with an *empty* first
   cell; a row-by-row parser attributes that text to the wrong segment.
2. **Page breaks repeat the header row** (`| Prompt | Hasil |`) mid-document, and split one logical
   cell across two rows.
3. **The boundary is sometimes inside a cell.** In Tugas 2 the `Critical Review` cell begins with the
   AI's case list repeated verbatim, bullet by bullet, each followed by the student's comment. Row
   labels alone are not sufficient there; the segmenter must also fall back to heuristics and, when
   unsure, lower its confidence so the lecturer corrects it.
4. **Plain text extraction scrambles column order** in some files (Tugas 3, 4, 7): lines interleave.
   This is why extraction is *table-aware* (`pdfplumber`, `python-docx`) rather than a raw text dump.
5. **Screenshots and image-only pages** carry no text layer. They are flagged as `IMAGE_ONLY`, never
   silently dropped and never sent anywhere.

## Pipeline

```
upload → extract → segment → redact → store (redacted segments only)
```

- **Extract** (`app/ingest/extract.py`) — per file: PDF via `pdfplumber` (text + tables), DOCX via
  `python-docx` (real cell structure), TXT read directly, ZIP unpacked and each member dispatched by
  extension. One failing file must not fail the batch (FR-03): the failure is reported per file.
- **Segment** (`app/ingest/segment.py`) — label-driven first (first-column cell equals
  `Critical Review`, case-insensitively), heuristic second (a short question-like row followed by a
  long answer row; blank first column means continuation of the previous cell). Records `method` and
  `confidence` so the UI can propose-and-let-correct (FR-05).
- **Redact** (`app/ingest/redact.py`) — removes identifiers from each segment: labelled names
  (`Nama : …`), student IDs (NIM), emails, phone numbers, personal links, and names appearing in the
  prose. Counts only are logged; the removed values are never stored (FR-04).
- **Guard** (`app/ingest/guard.py`) — the single egress choke point. Phase 4's provider client calls
  it before every request; if it detects an identifier the call is refused and the submission is
  flagged for review rather than sent. Ingest filtering can miss something; this cannot be bypassed
  by a new call site because there is only one.

## What is stored, and what is not

| Artefact | Stored? |
| --- | --- |
| Uploaded file, filename, document metadata | **never** — in memory for the request only |
| Redacted AI-output and student-analysis segments | yes, in `submissions` |
| Real identifier → submission mapping | yes, `student_identities`, owner-only, never sent |
| Counts of what was removed | yes, `redaction_events` (counts per class, no values) |

## Gate result, and the two defects the gate found

Run against all nine archived files on 2026-10-14 (`uv run python -m scripts.verify_import <dir>`):

| | Tugas 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | Akhir |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Segmentation | label | label | label | label | none | none | none | none | none |
| AI output detected | yes | yes | yes | yes | – | – | – | – | – |
| Identifier removed | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Nine of nine imported with no identifier surviving into the stored text, and the egress guard accepts
every segment — which is the phase-3 gate in PRD §13. Four files carry AI output and are segmented by
label; five carry none and are correctly reported as pure student analysis rather than being forced
into a segment.

**Defect 1: table-first extraction silently dropped every non-table line on pages that contain a
table.** Measured on the real files: 992 characters lost on page 3 of Tugas 2, 2,832 on page 11,
2,267 on page 8 of Tugas 3 — and Tugas 3's page 1 lost 1,201 characters, which is exactly where
`Nama : …` and `NIM : …` sit. Two consequences, one of them dangerous: the scorers would have been
handed truncated analysis text, and the privacy gate passed *by accident* — the identifier was
discarded by the extractor rather than removed by the redactor, so the first fix that read more of
the page would have leaked it. Fixed by emitting both the table rows and the text outside the table
boxes, ordered by vertical position so a continuation stays next to its table. The regression test is
a no-text-lost invariant over a stubbed page, and `scripts/verify_import.py` now compares extracted
characters against a raw page dump and fails below 90% coverage — that check is what surfaced this.

**Defect 2: the guess path invented AI output that did not exist.** Tugas Akhir has no AI output and
no labels, yet the row-shape heuristic paired a short row with a long one and assigned 1,677
characters of the student's own work to the AI region — text that would then be excluded from
scoring. Fixed by requiring a question cue (a trailing `?`, or a question word) in addition to the
length bounds; an unlabelled document now honestly reports `method="none"`.

Both were found by running the pipeline over the real archive, not by reading the code. The lesson is
recorded here because the same class of error — a heuristic that looks right on a synthetic fixture —
is the one most likely to recur in phase 4.

## Dependencies

`pdfplumber==0.11.10` (2026-06-15), `python-docx==1.2.0` (2025-06-16) and `python-multipart==0.0.32`
(2026-06-04), all verified on PyPI on 2026-10-14. No OCR: an image-only page is flagged rather than
guessed at.
