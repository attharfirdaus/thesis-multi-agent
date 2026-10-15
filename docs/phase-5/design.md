# Phase 5 design — the lecturer UI

Two constraints shape this phase beyond "make screens".

**The UI is the last mile of the privacy design.** Every call to the API happens in the browser, never in
a Next.js server component, so the web server never touches student text — which is what keeps the
hosting decision (O-5) free of privacy consequences. That was already true of the auth screens and it
stays true of every screen here.

**Machine vocabulary must not reach a lecturer.** PRD §9 forbids showing agent, node, prompt or token to
the person doing the marking. The backend keeps its codes (`needs_review`, `cognitive_agent_failed`, and
the stored level `absent` for a not-present indicator, plus the English extraction warnings) because they
are stable values the thesis can count; the translation lives in exactly one place —
`frontend/lib/labels.ts` — and an unknown value falls back to a generic Indonesian sentence rather than
printing itself. The **export keeps the raw values**, because a research file is joined by machine rather
than read as prose.

That file also carries the one soft spot of this approach: `warningSentence()` matches the stored warning
text, so a backend that rewords a warning loses its translation and falls back to "Berkas diproses dengan
catatan yang belum dapat dijelaskan otomatis." A numeric code on the warning would be sturdier; until then
the failure is a generic sentence, never an English one.

## Screens

| Route | What it is | Requirements |
| --- | --- | --- |
| `/dasbor` | Assignment list with submission count and the newest run's state; create form; empty state naming the next step | FR-02 |
| `/tugas/[id]` | Upload (multi-file, per-file result), submission table with status flags, the evaluate control (create run → process in chunks → poll until done), progress from job counts, and resume-after-reload | FR-03, FR-06 |
| `/tugas/[id]/hasil` | Results table: sortable pseudonym / cognitive level / review column, filter by level, `Perlu Ditinjau` badge, and the two export links | FR-09, FR-12 |
| `/kiriman/[id]` | Split view: the student's analysis with every evidence span highlighted in place, per-score cards with the agent's rationale and its quoted evidence, the override control, the feedback editor, and the boundary correction | FR-05, FR-10, FR-11, FR-14, FR-19 |

Login and sign-up (`/masuk`, `/daftar`) already existed from phase 2 and are unchanged.

## The evidence highlighter

`frontend/lib/evidence.ts` slices `student_analysis_text` at the stored half-open offsets. Three details
matter, and each one is a bug if it is wrong:

- **Slice, never search.** The offsets are authoritative; searching the text for the quote would highlight
  the first occurrence, and a phrase the model quoted from the second paragraph would appear underlined in
  the first.
- **Merge adjacent and overlapping spans.** Two scores can quote the same passage; the pane must show one
  highlight carrying both scores rather than two overlapping marks.
- **Clamp stale offsets.** A submission can be re-segmented after scoring, which moves every offset; a span
  beyond the end of the text is dropped rather than blanking the pane.

The invariants kept: the slices always concatenate back to the exact source text, and an empty text renders
nothing.

## Overrides and feedback

An override is its own `lecturer_reviews` row: `system_scores` is never updated (FR-11), so agreement
between the system and the lecturer stays computable after the fact. The reason is required by the database
constraint *and* by the API, which answers 422 before the insert — the check exists twice because the
constraint is the guarantee and the API is the explanation. The new level must be one of the rubric levels
the scoring run froze, not one the caller invents.

Feedback is stored beside the generated text (`edited_text`, `generated_text`), never in place of it: both
go into the export, and "what the model wrote" versus "what the lecturer sent" is a distinction the thesis
needs. A blank edit stores NULL, meaning "no edit".

## Export

`GET /runs/{id}/export.csv` and `.xlsx`, one row per evidence span plus one row for a score whose quote
could not be located. The CSV carries a UTF-8 BOM so Excel reads Indonesian text as Indonesian. The
columns include the run's own metadata (`run_id`, `mode`, `model`, `temperature`, `seed`, `rubric_version`,
`started_at`, `finished_at`) because FR-13 requires every run to be traceable to the configuration that
produced it, and the review columns sit beside the system level rather than replacing it.

## API added this phase

| Endpoint | Requirement |
| --- | --- |
| `GET /assignments`, `POST /assignments`, `GET /assignments/{id}` | FR-02, and the dashboard's counts without a query per row |
| `GET /submissions/{id}` | FR-10, FR-14: the texts, the scores with their spans, the rubric of the run that produced them, the reviews, the feedback |
| `POST /system_scores/{id}/review` | FR-11 |
| `PATCH /submissions/{id}/feedback` | FR-19 |
| `GET /runs/{id}/export.csv`, `GET /runs/{id}/export.xlsx` | FR-12 |

`submissions.review_flags` (phase 4) and the segmentation endpoint (phase 3) are the other pieces the UI
reads. No endpoint returns `student_identities.real_identifier`: the pseudonym is the only name the
lecturer UI receives, which is the point of FR-04.

## Verification

| Level | What it covers |
| --- | --- |
| `backend/tests/test_lecturer_api.py` (9 tests) | Override needs a reason and a known level; the system score is unchanged afterwards; the detail follows the newest run and carries its rubric; an unscored submission is not an error; the export header, BOM, one row per span, and the XLSX sheet; **a second lecturer reaches nothing** — every endpoint answers 404 and writes nothing |
| Mutation checks by the implementer | Breaking the export's `left join` and the detail's run ordering each made the corresponding test fail, so the tests bind the behaviour rather than the shape |
| Live pass, real backend, throwaway account | `GET /submissions/{id}` with `assignment_id` and the rubric's `C1..C6`; an override without a reason rejected with 422 and with one stored as `override`/`C5`; the feedback edit stored beside the generated text; the CSV with a BOM and 10 rows for 2 submissions × 5 scores; the XLSX at 6,918 bytes |
| Frontend static checks | `npx tsc --noEmit`, `npm run lint` and a production build, all clean; a runnable check over the offset slicer, the document join and the label fallbacks (`npm run check:evidence`, 11 assertion groups) — zero-dependency, run by Node's own TypeScript support |
| My own walkthrough, real backend and real provider | Two archived PDFs imported and scored in a throwaway account: the dashboard card with its count and run badge; a deliberately broken file rejected with "Berkas ini gagal dibaca." and its raw error behind a collapsed `Detail teknis`, with the batch unaffected; the results table sortable and filterable with no machine word left in it; the detail page showing exactly one `<mark>` whose text is the stored quote, the rationale, the review state after an override submitted **through the UI** ("Tinjauan terakhir: diubah menjadi C6") and after one `Terima` ("diterima"); the feedback editor saved ("Umpan balik tersimpan."); the boundary handle reporting "Batas di karakter 3774 dari 6462"; and the CSV downloaded by clicking the link — `run-<id>-scores.csv`, 7,259 bytes, filename taken from `Content-Disposition` |

## Deliberate omissions, stated rather than hidden

- **The results table shows review state from `review_flags` only.** It says `Perlu Ditinjau` or `Sesuai`;
  it does not yet show that a lecturer already overrode a score, which would need the reviews in the results
  payload. FR-09 asks for the flag, not for the override state, so this is a known gap rather than a
  half-built feature.
- **Per-file ingest errors have no error code.** The API returns the extractor's English message, so the UI
  shows an Indonesian sentence and puts the raw text behind a `Detail teknis` disclosure. Extraction
  *warnings* are translated by matching their stored text (see above); a `code` field on both would remove
  the guessing.
- **Boundary correction moves the boundary; it does not edit the text.** FR-05 asks for correcting the
  boundary, and the endpoint takes an offset. The screen shows read-only previews plus one explicit
  boundary control, so nobody retypes an analysis into a field that cannot save it.
- **No JavaScript test runner.** The project has none, and adding one is a dependency decision rather than
  a coding one. The one piece of non-trivial frontend logic (the offset slicer) has a runnable check
  instead; everything else is covered by the live pass.
- **`feedback.exported_at` is never written.** The column exists in PRD §10 but no requirement says when it
  should be stamped, and stamping it on a GET would give a read request a side effect. Raised as a
  micro-decision rather than guessed.
- **`single_agent` mode is still stored-but-not-implemented, and run-to-run variance is still absent** —
  both unchanged from phase 4, and both recorded in PRD §14 / DECISIONS.md.

## Dependencies

No new frontend dependency (React, Next.js and the existing `components/ui/*` primitives cover it).
Backend: `openpyxl==3.1.5`, verified on PyPI on 2026-10-15, added only for the XLSX half of FR-12 — the CSV
half is the standard library.
