# DECISIONS — multi-agent LLM evaluation system

Format: `date · decision · options considered · decided by`. Newest first within each phase.
Every provider/model/library fact cited in this project carries a source URL and an access date.

## Open decisions

No model or provider decision remains open. The hosting decisions (O-2, O-3, O-5) were re-taken twice — on 2026-10-07 (VM dropped) and again on 2026-10-14 (Cloud Run dropped for a card-free host) — see the newest entries; the older ones are kept as the record of what was chosen and why it changed. What is still open lives in PRD section 14 — the supervisors' metacognitive rubric, institutional ethics clearance, the validation-subset size, the SUS instrument, the feedback-text format, and how the two synthetic calibration examples are validated. The few-shot calibration itself is settled: Atthar supplied it on 2026-10-15.

## 2026-10-16 (later still) — Deleting a submission, and one fact one warning

**Atthar asked for "a feature to delete student posts"** (submissions). `DELETE /submissions/{id}` answers 204
and removes the submission and everything derived from it: scores, their evidence, agent traces, feedback,
queue entries, redaction counts and the pseudonym mapping. All of it cascades from `submissions`, so this is
one delete rather than a cleanup sequence that can half-finish — and a half-deleted submission is worse here
than anywhere else, because the rows a lecturer can no longer see are still rows about a student.

- **Refused (409) while a job for that submission is queued or being graded.** The worker holds that
  submission's text and would try to store a result for a row that no longer exists; the failure would take
  the whole pass down, not just that submission, and the lecturer would have deleted something the app kept
  grading. The screen shows the reason and keeps the row.
- **Deleting an assignment was not built.** He asked for submissions, no requirement covers an assignment
  delete, and one click that takes a whole class is not a control to invent.
- Verification: 128 backend tests (three new — the cascade reaching every dependent table and the run's own
  results view, the 409 while a job is in flight, and the single warning below), each of the two new guards
  proven to fail when its behaviour is removed.
- **The UI half landed and was verified live** (throwaway account, real backend): a `Tindakan` column with one
  destructive control per row whose accessible name carries the pseudonym, a confirmation naming what
  disappears and that it is final, the endpoint's Indonesian 409 shown verbatim with the row kept, and on
  success the row gone with "Kiriman S-… beserta nilainya sudah dihapus." — the card's count moving from 2 to
  1 kiriman. The delete also forced a real fix: `load()` reused the run object it already held when the ids
  matched, so the run's counters would have gone stale after a delete, since a submission's job rows cascade
  with it; it now takes the API's fresh status and counters.

**And a bug his screenshot showed: the same sentence twice in one cell.** "Bagian keluaran AI tidak
terdeteksi…" appeared twice for two submissions. Root cause was in the data, not the screen: the segmenter
reports the no-AI case (`segment.NO_AI_WARNING`) and the ingest router appended its own phrasing of the same
fact, so two stored strings mapped to one Indonesian sentence. The router no longer adds it — one fact, one
warning, and the layer that knows how the boundary was decided is the layer that reports it. Rows already
stored still carry both, so the UI de-duplicates rendered warnings by sentence, the same way it de-duplicates
flag sentences.

## 2026-10-16 (later) — Three UI asks from Atthar: transparency, cursors, cancel

The owner's list, verbatim, and what each one turned out to require.

- **"Add process transparency while a task is being graded."** `RunOut` gained
  `in_flight: [{submission_id, pseudonym}]` — the submissions whose job is `running` right now — so the
  screen can name what it is reading ("Sedang menilai S-009a702e") instead of only counting. Granularity is
  honest: the API reports per submission, not per agent, so the UI does not claim to know which step of the
  pipeline is running. The indeterminate bar and the elapsed timer stay, since a provider call still
  reports no progress of its own.
- **"Change the cursor to a pointer when hovering over any button."** Root cause: Tailwind's preflight
  leaves buttons at `cursor: default`, so every button in the app showed a text cursor. Fixed once in the
  shared `Button` primitive rather than per screen, with `cursor-not-allowed` for the disabled state —
  the distinction is the information the cursor carries, and a hover pointer on a dead button would be a
  lie about what a click does.
- **"Add a cancel button while the grading process is underway."** New endpoint
  `POST /runs/{id}/cancel`, migration `0005` (both `runs.status` and `jobs.status` needed `cancelled` in
  their check constraints), and the semantics recorded in `docs/phase-5/design.md`: **the queue stops, the
  process does not** — a submission already claimed finishes and stores its scores, and the response says
  so with the counts and the in-flight submission named. Cancelling a finished run is a 409, because
  rewriting a completed evaluation as a stopped one is a mistake nobody would see on screen. A cancelled
  run stays cancelled through the next pass, so the control cannot be undone by the very work it stopped.

Verified: 124 backend tests (three new: the in-flight report, the not-resurrected cancelled run, and the
409 on a finished run), ruff and mypy clean, migration applied to the app's database. Then verified against
the running app with a throwaway account, because the tests cannot see the queue from outside:

| What was checked live | Result |
| --- | --- |
| `in_flight` while grading | `jobs: {running: 1}`, `in_flight: ['S-c37c51e5']` — the submission is named |
| cancel mid-flight | `status: cancelled`, `jobs: {running: 1}`, in-flight submission still named |
| cancel again | 409 |
| after the in-flight submission finished | run stayed `cancelled`, job `done`, 5 scores and feedback stored — the documented "one graded submission, not a resumed run" |
| cancel a finished run | 409, and the run stayed `done` |

**Three more defects that only the live pass could show**, all fixed in the same work:

- **The run's status lagged its own work.** While a pass was grading, `GET /runs/{id}` still answered
  `queued` — the status was only written at the end of the request — and a run driven from the command line
  stayed `running` for as long as nobody called the API again. Both now settle through the worker: the run
  moves to `running` when the first job is claimed and to `done` when nothing is left, which is what the
  screen and the thesis read. Verified live through both paths.
- **LangGraph's checkpoint serde did not know our state types.** It warned on every `CognitiveResult`,
  `MetacognitiveResult`, `SynthesisResult` and `EvidenceSpan` while resuming and states that a future
  version will refuse to deserialise them at all — which would break every resumable run on an upgrade,
  silently until someone needed to resume. The saver now names them explicitly
  (`CHECKPOINT_STATE_TYPES`) instead of relying on the permissive default. Verified live: zero warnings in a
  full pass afterwards.
- **The command line graded submissions and threw the scores away.** Only the API endpoint called
  `persist_submission_result`, so `python -m app.jobs.worker` — documented as a driver of the same call and
  used as the resume path — completed jobs, reported `{"done": 1}` and stored nothing. A cancelled run
  showed the same shape: the counts said "2 selesai" while the results were empty, because the endpoint
  persisted once, after the whole pass returned. Both are fixed by persisting inside the worker as each job
  finishes, in the same transaction that marks the job done, so a job can never be `done` with nothing
  stored. Verified live and by a test that fails without it (`assert 0 > 0`); the endpoint's duplicate
  persist loop is gone.

**The UI half landed** in the same commit as the worker changes (its message only names those): a 3-second
poll of `GET /runs/{id}` while a process call is open — necessary because `in_flight` is only populated
mid-call, since the process response arrives after the submission it claimed is already done — so the card
can read "Sedang menilai S-…", "N dari M selesai" and the non-zero counters; one base-layer CSS rule giving
every button a pointer cursor and every disabled control `not-allowed` (which required dropping
`disabled:pointer-events-none`, since hit-testing skipped the disabled button and the cursor was never
shown); and a cancel control that confirms with what is lost and what is not, aborts the request, and
reports the returned state.

**And one gap of mine that the live run exposed:** I told the frontend that the flag vocabulary was "exactly
five values, exhaustive". It is six — `evidence_unverified` reaches `review_flags` — and the screen showed
"Perlu ditinjau dosen." twice for it. The mapping is now six sentences, the list de-duplicates identical
statements, and the runnable check no longer trusts anyone's memory: it reads the flag constants out of
`backend/app/agents/` and fails if a code has no sentence or a sentence has no code. That guard was proven to
fail on both kinds of gap before it was accepted.

## 2026-10-16 — First real use: four defects found and fixed

Context: Atthar ran the app on his own account — one assignment ("ISO"), one submission (the 9,155-character
ISO 31000 analysis from `samples/`), and he pressed Evaluate twice, three minutes apart. No test in the suite
would have found any of the four; they needed a person, a real provider and a real database.

1. **A job claim could cross runs.** `claim_jobs` filtered by owner, not by run, so `POST /runs/A/process`
   could execute run B's job and persist its scores under **run A's** rubric, prompts and model snapshot.
   The run is the unit the thesis traces a score back to, so that quietly corrupts the research record —
   and it is what let two runs score the same submission at once. Fixed with a `run_id` predicate; the new
   test fails when the filter is neutralised (checked by mutation, since a green test proves nothing about
   what it binds). `_requeue_stale` was already run-scoped, which is what made the old behaviour incoherent.
2. **The screen could start a second run and showed no sign of life.** PRD §9 says long work never blocks
   the screen and must show progress; the page did neither. The controls now resume an unfinished run rather
   than create another (with a ref guard against a double press), show an indeterminate bar plus elapsed
   seconds while a request is in flight, and stay enabled when a lease is stale — because a stale `running`
   job disables the only control that could clear it, and `_requeue_stale` is only reached through that
   control. Self-healing on load closes the same loop after a crash or a closed tab.
3. **Neon closed an idle connection and the API answered 500** with `SSL connection has been closed
   unexpectedly` on `/auth/me`. The pool now checks a connection on checkout. **Stated plainly: this is
   `[UNVERIFIED]` locally** — local Postgres closes a connection in a way psycopg_pool already detects, so
   the silent death cannot be reproduced here. A test was written for it, found to pass with *and* without
   the guard, and deleted rather than kept as false coverage. The evidence is the documented remedy for
   exactly this failure plus the absence of those 500s in use.
4. **A failure recorded neither of the two numbers that explain it.** An agent that failed left
   `latency_ms` null (the client reports a latency only for a call that returned), and the run snapshot did
   not record the timeout budget that decided whether the dimension got a chance at all. Both are now
   recorded; the failure path measures its own duration, which is the number that says the provider is sick.

**The failure itself, observed twice:** the cognitive agent timed out three times on that 9,155-character
analysis — the *same document* that timed out for the cognitive agent in my 2026-10-15 gate run — while the
metacognitive (30 s) and synthesis (39 s) calls on it succeeded. So this is document-dependent and
reproducible, not noise, and it is the first real constraint on the PRD §11 performance claim: a free-tier
provider asked to score a 9k-character Indonesian analysis with a 4k-character calibration block does not
reliably answer inside the 120-second budget that was configured.

**Measured, rather than assumed: raising the budget is not the fix.** The same prompt (16,530 characters)
was sent again with one attempt and a **300-second** timeout, and it timed out again at 300.1 s — no
response, not a slow response.

**Root cause: the configured model is a reasoning model, and its deliberation was eating the whole token
budget.** With no `max_tokens` in the request, generation is unbounded. With one, the response came back in
8.2 s with `finish_reason: length`, **empty `content`**, and 1,024 tokens of `reasoning`; at 4,096 tokens it
spent 67.6 s deliberating and still returned empty content. The answer lives in `content`, the deliberation
in `reasoning`, and they share the budget — so the cognitive agent could never answer. The metacognitive and
synthesis calls only succeeded because their prompts happened to stop deliberating in time.

**The fix is one request field, and which one was measured rather than assumed.** Sent to the real endpoint,
same prompt, 512-token cap:

| Parameter | Result |
| --- | --- |
| `reasoning_effort: "none"` | accepted and **ignored** — `finish_reason: length`, 1,900 reasoning characters, empty content |
| `reasoning_effort: "minimal"` | accepted and **ignored** — 2,020 reasoning characters, empty content |
| `thinking: false` | accepted and **ignored** — 2,135 reasoning characters, empty content |
| `reasoning: {"effort": "none"}` | accepted and **ignored** — 1,880 reasoning characters, empty content |
| **`chat_template_kwargs: {"enable_thinking": false}`** | **`finish_reason: stop`, 427 characters of valid JSON, zero reasoning, 5.7 s** |

The client now sends that field, `max_tokens` is capped at 1,024 (real answers measure 750–1,046 characters,
so there is ~4× headroom), and both are recorded in the run's snapshot because they decide whether a
dimension can be scored at all. **Verified end to end on the owner's own submission:** the cognitive call
that never returned now answers in **1.5 s** with one attempt — level C2, a verbatim quote, and an Indonesian
rationale.

**What this changes beyond the bug.** The 20–86 s latencies recorded during the phase-4 gate were mostly
deliberation, not provider slowness: with thinking disabled the same calls answer in 1.5–8 s, and the neuron
cost drops with them (`prompt_tokens 4,078 / completion 1,024` per cognitive call). PRD §11's performance
target and the free-tier quota math should be re-derived from the new numbers rather than the old ones. The
tradeoff is stated rather than hidden: a reasoning-disabled model may classify depth less carefully, and that
quality question is unmeasured — the alternative measured today was not a better answer, it was **no answer at
all**.

## 2026-10-15 (late) — Phase 5: the lecturer UI, built and walked through on the real stack

Scope from PRD §13's phase-5 line, against the P0 requirements behind it: assignment list and creation
(FR-02), upload with per-file results (FR-03), boundary correction (FR-05), run controls with progress and
resume (FR-06), results table (FR-09), submission detail with highlighted evidence (FR-10), override with a
required reason (FR-11), CSV and XLSX export (FR-12), per-score explanation (FR-14), editable feedback
(FR-19). Screens: `/dasbor`, `/tugas/[id]`, `/tugas/[id]/hasil`, `/kiriman/[id]`.

- **Eight new endpoints** (`GET/POST /assignments`, `GET /assignments/{id}`, `GET /submissions/{id}`,
  `POST /system_scores/{id}/review`, `PATCH /submissions/{id}/feedback`, `GET /runs/{id}/export.csv|.xlsx`).
  The contract was frozen before the work was split, so the UI was written against the shapes rather than
  against whatever happened to exist. Options considered: reusing `/runs/{id}/results` for the detail view
  (rejected — the detail needs the texts, the rubric of the scoring run, the reviews and the feedback in one
  read, and the run view does not carry them).
- **An override is a new `lecturer_reviews` row; `system_scores` is never updated** (FR-11), so system-versus-
  lecturer agreement stays computable after the fact. The reason is enforced by the database constraint *and*
  by the API, which answers 422 before the insert; the new level must be one of the levels the scoring run
  froze. Verified live: an override without a reason is rejected, with one it is stored.
- **Machine codes stay in the API; the Indonesian lives in the UI.** `needs_review`,
  `cognitive_agent_failed`, and the rest are stable identifiers the thesis can count, and `absent` is the
  stored level for a not-present indicator. PRD §9 forbids that vocabulary in front of a lecturer, so the
  translation sits in `frontend/lib/labels.ts` (flags, presence levels and extraction warnings in one place),
  with an unknown value falling back to a generic sentence instead of printing itself. The **export
  deliberately keeps the raw values** — a research file is joined by machine, not read for prose.
- **Export shape: one row per evidence span, plus a row for a score whose quote could not be located**, with
  the run's metadata columns (`run_id`, `mode`, `model`, `temperature`, `seed`, `rubric_version`,
  `started_at`, `finished_at`) because FR-13 makes the run the unit of traceability. CSV carries a UTF-8 BOM
  so Excel reads Indonesian text as Indonesian; XLSX is `openpyxl==3.1.5`, the only new dependency, added
  for the half of FR-12 the standard library cannot do.
- **The detail response gained `assignment_id`.** Two lines, because a detail page whose only exit is the
  browser's back button is a dead end.
- **Boundary correction moves the boundary; it does not edit text.** FR-05 asks for the boundary, the
  endpoint takes an offset, so the screen shows read-only previews and one range handle. A pair of textareas
  that silently cannot save was rejected as a trap.

**Three defects found while integrating, none of which a test would have caught:**

1. **The combined-document separator.** `PATCH /submissions/{id}/segmentation` defines its document as
   `ai_output_text + "\n" + analysis`; the editor reconstructed it with a space, so every dragged boundary
   was off by one character and the default position happened to hide it. Fixed in the UI, with the rule and
   its source named in a comment, and pinned by the runnable check. No backend test crosses the API/UI
   boundary, which is exactly why this survived a green suite.
2. **`runs.started_at` was never written by anyone** (found while building the export, which emitted an empty
   column). Now stamped on the first job claim rather than at creation, so a run queued overnight reports
   when it actually began; the `is null` guard keeps a resumed pass from moving it.
3. **`system_scores.level = 'absent'`** was rendered raw in the results table and the detail card, the same
   PRD §9 violation as the flags. Mapped in the UI now; the export is unchanged.

**Verification.** 120 backend tests (9 new, including "a second lecturer reaches nothing" across every new
endpoint, and two mutation checks by the implementer that each broke a test on purpose), ruff and mypy clean.
Frontend: `npx tsc --noEmit`, `npm run lint` and a production build clean, plus `npm run check:evidence`
(9 assertion groups over the offset slicer, the document join and the flag sentences — zero-dependency, run
by Node's own TypeScript support). My own live pass ran against the real backend and the real provider with a
throwaway account: two archived PDFs imported and scored, a broken file rejected with an Indonesian sentence
and its raw error behind a disclosure, both screens read, one override submitted through the UI and one score
accepted (the page reporting "Tinjauan terakhir: diubah menjadi C6"), the feedback editor saved, and the CSV
downloaded by clicking the link (`run-<id>-scores.csv`, 7,259 bytes, filename from `Content-Disposition`).
The email in the UI came from the throwaway account, which was deleted afterwards along with its run; the
owner's own database still holds only his account, the seeded rubric and the calibration.

**Stated gaps rather than hidden ones** (also in `docs/phase-5/design.md`): the results table shows review
*flags*, not whether a lecturer already overrode a score; per-file ingest errors carry no error code, so the
UI shows a generic Indonesian sentence plus a technical disclosure; `feedback.exported_at` is never stamped
because no requirement says when and a GET should not write; the project has no JavaScript test runner, so one
runnable check covers the only non-trivial frontend logic; `single_agent` mode and run-to-run variance are
still absent (phase 6 / PRD §14). **Atthar's own walkthrough — "one lecturer, no help given" — has not
happened yet; that is his gate, and this entry does not claim it.**

## 2026-10-15 (night) — Phase 4 gate approved by Atthar; phase 5 (lecturer UI) begins

Atthar approved the phase-4 gate after the real-provider run above and asked for phase 5 to be built
("Setujui gate fase 4, bangun UI fase 5"). The gate as PRD §13 states it — *one batch evaluates end-to-end
with evidence and an explanation per score* — was demonstrated on the four archived submissions against
Cloudflare Workers AI, with the numbers recorded in the entry above. Approval was given knowing the two
gaps stated there: `seed` unexercised and run-to-run variance unimplemented.

**Still open, and not decided by this approval:** which phase owns PRD §11's run-to-run variance (3–5
repeats per dimension, mean ± SD). He chose to proceed to phase 5 with the question open; phase 5 does not
implement it, and no phase-5 screen may imply that a stored score is stable across calls.

Phase 5 scope, from PRD §13 ("Results table, submission detail with evidence and plain-language
explanation, feedback text editor, override, export") and the P0 requirements behind it: FR-02 assignment
create/list, FR-03 upload, FR-06 run progress, FR-09 results table, FR-10 detail with highlighted
evidence, FR-11 override with a required reason, FR-12 CSV/XLSX export, FR-14 explanation per score,
FR-19 editable feedback. Its gate is a walkthrough with one lecturer and no help given — Atthar's, not the
agent's.

## 2026-10-15 (evening) — Phase 4 gate run against the real provider: the four archived submissions

First run with no stub. `@cf/google/gemma-4-26b-a4b-it`, `LLM_TEMPERATURE=0`, `LLM_SEED` unset, the four
archived PDFs from `samples/`, driven over HTTP through the app's own upload → run → process → results
path against a throwaway database. Credentials were supplied by Atthar and verified before the run.

**Throughput and reliability.** 4/4 imported, 4/4 jobs `done`, run `done`, `needs_review=1`, 342
LangGraph checkpoint rows. 12 provider calls: **11 usable on the first attempt** (JSON mode held on the
first answer), 1 retried once and then succeeded, and **1 failed after 3 attempts with a ReadTimeout** —
that submission's cognitive dimension was flagged `cognitive_agent_failed`, its metacognitive findings
were still stored, and the batch finished normally. That is PRD §6's "a failed submission never fails the
batch" exercised for real rather than asserted.

**Latency per call: min 19.98 s, max 85.77 s, mean 44.47 s**; the batch took 807 s (13.5 min) for four
submissions at prompt sizes of 10.0k–25.9k characters. This is the number the PRD §11 performance target
gets set from, and it is the reason the trace fix below matters.

**Evidence check.** Three quotes were stored across the run, one per scored submission. All three were
located, and **zero of three match the stored text character for character** — the difference is line
breaks only, and the normalised comparison is equal in all three cases. The lesson is recorded because it
is easy to misread: exact string equality is the wrong metric; `normalise()` equality is the right one,
and a paraphrase would fail both.

**Substantive finding — the metacognitive agent reported `present: false` for all four codes on all four
submissions (16/16)**, each with its own Indonesian rationale ("Tidak ada jejak perencanaan atau
penetapan tujuan belajar..."). Two readings, and the app cannot choose between them: either these four
archived analyses genuinely carry no self-regulation traces — they are framework comparisons written to
answer a prompt — or the calibration biases the agent toward `absent`, since the zero-code example is one
of five and the instruction warns that affective expression is not a code. **Raised to Atthar as the gate's
main substantive question; not tuned by the agent**, because the calibration and the rubric are his
content (PRD §14) and quietly rewriting them to produce more `true`s would be fitting the instrument to
the result.

**Defect found by this run and fixed the same day: `agent_traces.latency_ms` was null in every row** (12
of 12). The client measures it, and the previous code deliberately dropped it, arguing that a state key
carrying only a metric was not worth it — but PRD §10 lists the column and PRD §11 asks for per-step
observability, and this run was paying 20–86 s per call while throwing the measurement away. Fixed with a
`latencies` channel in `GraphState` (a merge reducer, because the two analysis agents write it in
parallel), filled by each node from its own `Completion` and written by `persist`. A failed synthesis
retry keeps the first call's latency, since that call's result is the one stored. Tests at both levels:
the graph state carries all three agents' values, and the trace rows carry them after a full HTTP batch.

**Still unmeasured, stated plainly:** the provider's `seed` parameter was never exercised (`LLM_SEED`
unset, so no `seed` in the request body), so PRD §11's reproducibility claim has no measurement behind it
yet; and run-to-run variance (3–5 repeats per dimension) is still not implemented, so nothing here says
how stable these scores are across calls.

## 2026-10-15 (later) — Calibration supplied by Atthar; the rubric now speaks his vocabulary

Atthar answered PRD §14 with the few-shot calibration: six Bloom examples for the cognitive agent (C1–C4
from the archive, **C5 and C6 marked SYNTHETIC** because no real example exists at those levels) and five
SRL examples for the metacognitive agent (one per code plus a zero-code case). The content is his; the
coding agent did not author or reword it.

- **Stored as data, one block per agent, in `backend/scripts/calibration.json`** and seeded into
  `PromptVersion` (`agent_name = 'calibration'`, v1) by `scripts/seed_rubric.py --calibration`, which now
  defaults to that file. Options: one shared example list (what the schema had) or per-agent blocks. Two
  agents with different rubrics cannot share one list — each would be prompted with the other's examples —
  so the row is keyed by agent, and a file missing either block is refused when it is read, not at the
  first job. Decided by the agent; the content by Atthar.
- **Level vocabulary is now the six Bloom codes (`C1`…`C6`) with their names in
  `RubricVersion.descriptors.levels`.** Options: keep the Indonesian Bloom names the interim seed wrote,
  or adopt the codes Atthar's own examples return. The rubric stores what the agents return, so the codes
  win; the names travel as descriptors. No threshold is seeded — that stays the supervisors' guideline's
  job (PRD §13). Seeded to his Neon database on 2026-10-15: rubric v1, prompts v1, calibration v1.
- **`Strength` is `lemah | sedang | kuat`, not `low | medium | high`.** His calibration writes those
  words and they land in `system_scores.level` where a lecturer reads them, so translating them would
  have created a second vocabulary for the same rubric value.
- **JSON field names inside the examples were aligned to the agent schemas** (`evidence_quote`,
  `present`, `indicator` instead of `evidence`, `presence`, `kode`), and the negative example — which he
  wrote as `{"semua_kode": false}` — is expressed as the schema's own shape, four findings with
  `present: false`. Reason: the examples are what the model imitates, and an example whose keys differ
  from the schema it is validated against teaches the wrong shape. **This is the one place his text was
  altered; the assessment content, rationales and principles are verbatim.** Flagged for his review.
- **Provenance notes do not reach the prompt:** `catatan_sumber` (used to mark the two synthetic examples
  and the zero-code case) is stripped when the block is rendered, so the reader-facing annotation never
  becomes model input. Verified: no `catatan_sumber`, no `SYNTHETIC`, and no cross-agent leakage in
  either rendered prompt.
- **Still open from the same PRD §14 item:** how the two synthetic examples (C5, C6) are validated so
  they do not bias the agent toward one phrasing. Marking them is not the same as validating them.

## 2026-10-15 — Phase 4 built: the agent pipeline, its queue and its evidence contract

Format of the entries below: decision · options considered · who decided. The design narrative and the
gate evidence are in `docs/phase-4/design.md`.

- **The graph runs the two analysis agents in parallel, then synthesis, then the evidence check** — one
  rule-based orchestrator, no routing LLM. Options: a sequential chain (simpler, half the latency
  budget) or an LLM router (can adapt the agent set per submission). The PRD §6 topology is what was
  specified and what the figure in the thesis documents; a router would add a second thing to evaluate
  for no gate-relevant capability. Decided by the PRD, implementation choice by the agent.
- **A quote that fails the evidence check twice is kept with a `submissions.review_flags` entry, not
  discarded.** Options: drop the score, or keep it unflagged. Dropping loses data the thesis needs
  (the failure rate is itself a result); keeping it unflagged would hide a fabrication from the
  lecturer. `review_flags` is a `jsonb` list, not a boolean, so FR-09 can say *why* (migration
  `0004_run_flags.sql`, 2026-10-15). Decided by PRD §6, shape chosen by the agent.
- **The worker compiles the graph with LangGraph's Postgres saver, thread = submission id, one saver per
  batch pass.** Options: no checkpointer (job-level retry only — simpler, and it already resumes a
  *submission* from scratch, which is acceptable for a 3-attempt queue) or a saver per job (a connect per
  job on a 25-job pass). PRD §6/§8 name Postgres checkpointing, so it is wired rather than dropped; one
  saver per pass keeps the cost at one connection. Checkpoint tables are LangGraph's, so
  `scripts/setup_checkpointer.py` creates them and grants the runtime role — not a migration.
- **Retry budget: `MAX_ATTEMPTS = 3` per job, `BATCH = 25` per pass, `limit` on the API.** Options: an
  unbounded pass (a batch could pin a worker for minutes with a slow provider, and an offline provider
  would burn every retry in one call) or per-submission retries only. The bounded pass keeps the UI
  responsive and makes a failure cost one pass, not one batch.
- **Run-to-run variance (PRD §11: 3–5 repeats per dimension, mean ± SD) is *not* implemented**: phase 4
  makes one LLM call per dimension per submission. Options: implement it now, inside the pipeline, or
  take it in phase 6 with the other research features. Not decided by the agent, because it changes run
  semantics and multiplies the batch's token cost — raised to Atthar and recorded in PRD §14.
- **Verification ran with a stubbed provider**, because no API key exists in this environment: the real
  corpus (`samples/`, the four archived AI-permitted submissions) was pushed through ingest → jobs →
  graph → persistence → results with a stub that quotes each submission's own text. 20 evidence spans
  were checked to reproduce their quote at their offsets in the real Indonesian text; 24 checkpoint rows
  were written. **Consequence, stated plainly:** JSON-mode adherence, latency and Bahasa Indonesia
  scoring quality are unmeasured until a key exists, and the calibration examples remain empty
  (`pending_atthar`), so a real run refuses with `MissingCalibration` by design.

## 2026-10-14 (later) — Hosting settled: local backend + optional tunnel; Neon role corrected

**Decision.** The API runs on the owner's Mac — natively via `scripts/dev.sh`, or in Docker for production-image parity — against Neon. For remote demonstrations it is exposed through a **Cloudflare Quick Tunnel**, which needs no account and no card. Render, Cloud Run and every other card-verified host are closed: the same card fails verification everywhere, including Render's manual Web Service flow, which was the last card-free candidate.

**The tunnel works, and the cookie consequence is measured rather than assumed.** Exercised end to end on 2026-10-14: `cloudflared tunnel --url http://127.0.0.1:8000` printed a public HTTPS URL with no account, and `GET /healthz` through it returned `{"status":"ok","database":"ok"}`. A browser A/B test run from the live Vercel page — a *different site* from the tunnel — measured exactly what happens:

| API cookie setting | Signup | Then `GET /auth/me` |
| --- | --- | --- |
| `COOKIE_SAMESITE=lax` (the old default) | 201 | **401** — the browser silently withheld the cookie on the cross-site fetch |
| `COOKIE_SAMESITE=none` + `COOKIE_SECURE=true` | 201 | **200**, authenticated as the right user |

That is why `COOKIE_SAMESITE` was added to the configuration. Localhost and same-host setups keep `lax`/`false`; only the Vercel-plus-tunnel topology needs `none`.

**Correction found while testing: the runtime role was bypassing row-level security.** `backend/.env` pointed both connection URLs at the Neon **owner** role, and measurement showed `thesis_owner` has `rolbypassrls = true` (it is a member of `neon_superuser`). With that role every tenancy policy in the schema is inert, so the guarantee this project is built on — enforced in PRD §11 and covered by an RLS test — was *not in force* on the deployed database. The two design roles exist and are correct: `thesis_migrator` (`bypassrls = false`) owns the tenant tables with `rls = true, forced = true`, and `thesis_app` (`bypassrls = false`) is the runtime role. The fix is configuration only: `DATABASE_URL` must use **`thesis_app`** on the pooled host, and `MIGRATION_DATABASE_URL` **`thesis_migrator`** on the direct host. The Neon database is also named `thesis`, not `neondb` as the runbook assumed.

**Accepted costs of running locally:** the machine must be on for anyone else to reach the API; a Quick Tunnel URL changes on every restart and Cloudflare documents Quick Tunnels as development-only; and Vercel bakes `NEXT_PUBLIC_API_BASE` in at build time, so a new tunnel URL needs a redeploy. The defence itself should run fully locally.

## 2026-10-14 — Backend host changed again: Render Free (no card available)

**Decision.** The backend runs as a **Render Free web service** in Singapore, built from the existing `backend/Dockerfile` through `render.yaml`. Everything else stands: Neon PostgreSQL (Singapore), the Vercel frontend, Cloudflare Workers AI. This supersedes the Cloud Run decision of 2026-10-07 (O-2).

**Why.** Atthar cannot obtain a Google Cloud billing account — the card is rejected with `OR_MIVEM_02`, which "generally indicate[s] that Google Payments was unable to complete the payment method verification". That is an issuer/card-type failure, not a form-entry one, and Cloud Run requires an active billing account. Cloud Run is therefore *payment*-blocked, not technically blocked.

**What was verified before switching (2026-10-14).** Render is the only card-free, durable, ASGI-capable host found: "No credit card is required"; free web services are 0.1 CPU / 512 MB with 750 instance-hours per month (more than a 31-day month), a Singapore region, HTTPS with custom domains, native Python with `uv.lock` detection or a Dockerfile, and documented responses of up to 100 minutes. Evidence: `docs/phase-2/cardfree-paas.md`, `cardfree-serverless.md`.

**Alternatives rejected, each with the reason:** Hugging Face Spaces (Gradio/Docker Spaces need PRO, and only ports 80/443/8080 are allowed, so Neon on 5432 is unreachable); Koyeb (card plus a $29 pre-authorisation hold, and new signups are Pro-only); Fly.io (no free tier); Railway ($1/month credit cannot keep a service online); Northflank and Qoddi (payment method mandatory); PythonAnywhere (restricted outbound, WSGI-first, 5-minute worker kill); Back4App Containers (the free container lives 60 minutes); AWS Lambda (card-free at signup, but the Free plan expires after six months and the account is then suspended with the data erased); Red Hat OpenShift Developer Sandbox (card-free and Python-capable, but a 30-day trial); Modal (its billing docs require a payment method on file — a second report read the signup page as card-free, so treat Modal as uncertain rather than available); Cloudflare Workers (128 MB and 10 ms CPU, too small for this app); Vercel Hobby for the API (300-second cap, and its free tier is permitted to use content for product improvement); Google Cloud Starter Tier (genuinely card-free Cloud Run, but it only accepts applications built inside Google AI Studio and states "You can't enable other Google Cloud APIs within that same project", so this image cannot go there).

**Risks accepted, named rather than hidden:**

1. Render "may suspend a Free web service that initiates an uncommonly high volume of traffic over the public internet", and its own examples include "Accessing an external database" and "Invoking external APIs" — precisely this application's pattern. There is no published threshold and the only remedy is a paid plan.
2. A 15-minute idle spin-down with a ~one-minute cold start.
3. "Render might restart a Free web service at any time" — survivable only because LangGraph state is checkpointed in Postgres and jobs are resumable, which the PRD already required.
4. 0.1 CPU / 512 MB sits at the bottom edge of the estimated 250–400 MB footprint.
5. The 5 GB monthly egress allowance is shared with the LLM API calls.

**Escape hatch.** If Render suspends the service or the instance proves too small, Modal Starter or Leapcell can run the batch, and Cloud Run becomes possible again if a card ever works. None of those moves changes the application: same image, same Neon, same frontend.

**Correction, same day — the Blueprint flow, not Render, was the payment gate.** The first deploy attempt used Render's **Blueprint** flow, which demanded a card and rejected it (the same card Google rejects). Evidence that this is flow-specific rather than account-wide: Render's public API declares `402 Payment Required` ("You must enter payment information to perform this request") on `POST /services` — the endpoint a Blueprint uses — while its own tutorial says "This tutorial uses free Render resources. **No payment is required.**", the signup page collects no card, and a 2026 user report records the identical experience ("Blueprint deployment also requires a card on file") with manual creation working instead. Render's Blueprint spec also defaults an omitted `plan` field to the paid `0.5c-512mb` instance, so a Blueprint without an explicit free plan creates a paid service. **The payment-free path is New → Web Service → Free**, with `plan: free` set explicitly in `render.yaml` for the record. Evidence: `docs/phase-2/billing-free-hosts.md`.

**Separately: the card itself is the blocker.** The same card fails verification at both Google and Render, so every host that requires card verification is closed until that changes. A card that supports international online transactions and 3-D Secure would reopen Cloud Run, IBM Code Engine and Azure for this project — that is a bank-side fix, not a provider choice.

## 2026-10-07 — Architecture reversed: no virtual machine (decided by Atthar)

**Decision.** Deploy on managed services only: the FastAPI + LangGraph API on **Google Cloud Run** (`asia-southeast1`), the database on **Neon PostgreSQL** (Singapore), the frontend on **Vercel Hobby** (Cloudflare Pages as the drop-in alternative), and LLM inference through **Cloudflare Workers AI** (`@cf/google/gemma-4-26b-a4b-it`, per O-1). No VM, no SSH, no OS patching, no reverse proxy, no firewall rules. This supersedes O-2 (Oracle Always Free ARM VM), O-3 (Postgres self-hosted on that VM) and O-5 (frontend served from it).

**Why the reversal (Atthar's reason).** A VM carries ongoing administration — SSH, OS updates, firewall, TLS renewal, monitoring — that is disproportionate for a thesis prototype whose subject is the multi-agent pipeline, not server operations. Explicit instruction: do not reintroduce a VM without a concrete technical blocker.

**Why the VM is not technically required** (verified 2026-10-07; evidence in `docs/phase-2/arch-*.md`):

1. **The reason the VM was chosen disappeared.** It was chosen on 2026-10-06 because the backend loaded an IndoBERT checkpoint and needed ≈1.3–2.0 GB resident, and because a batch run needed a process that would not be recycled. O-4 removed the model on the same day; the backend now holds no weights, no torch and no GPU requirement.
2. **LangGraph in library mode needs no long-lived server.** Its own docs require long-lived API + queue-worker containers only for the managed Agent Server; the checkpointed library path runs inside any process and resumes from a `thread_id`. Their serverless warning is scoped to the Agent Server binary, not to the library.
3. **It writes nothing to disk.** Checked directly: no temp files, no subprocesses, no in-process background tasks in `backend/app`. Uploads are parsed in memory.
4. **The batch shape fits a request.** Cloud Run allows a request up to 60 minutes, and a batch is decomposed so each submission is an independently retried invocation, with LangGraph state checkpointed in Postgres — which is the resumability the PRD already required, without a worker host or a queue service.

**What the VM bought, and why it is not needed.** Control, no cold start, and a single vendor. Control is not a requirement — nothing in the PRD needs a fixed outbound IP, a persistent disk or a cron daemon. A cold start of a few seconds is invisible for a lecturer-initiated batch. Vendor count rises from one to three, which is the tradeoff Atthar accepted in exchange for near-zero operational work.

**Constraints accepted with this architecture:**

- Neon suspends compute after 5 minutes idle and wakes automatically on the next query — no manual unpause before a demonstration, unlike the alternative that pauses for a week and needs an operator.
- Neon's pooler runs PgBouncer in **transaction mode**, so server-side prepared statements had to be disabled: `prepare_threshold=None` on the connection pool (`backend/app/db.py`). Tenant context already used `SET LOCAL` (never plain `SET`), which is what makes pooled connections safe for the row-level-security design.
- The compute host and the database host now process student documents during extraction and redaction, before anything is sent to an LLM. Both were checked against the fixed rule that no provider may train on content: Cloud Run and Neon both pass (`docs/phase-2/arch-privacy-topology.md`).
- **Documents are never persisted.** Migration `0002_no_raw_document_storage.sql` drops `file_ref` and `raw_text`; only the redacted segments survive, because scores and evidence offsets point at them. No object storage exists in this architecture.
- Vercel Hobby is excluded from Vercel's DPA and its terms permit training on free-tier content — acceptable only because the frontend never receives student text (the browser calls the API directly). If the clause or the data stance becomes a problem, Cloudflare Pages is the drop-in replacement.

**Residual risks, recorded rather than hidden:** (a) Vercel Hobby's "non-commercial personal use only" clause; (b) `StudentIdentity.real_identifier` still lives in the managed database — the privacy review recommends keeping the identity mapping outside any managed database, which is a change to FR-04 and needs Atthar's decision; (c) the Cloudflare Workers AI key is a production secret and must live in Secret Manager.

**Local development is unchanged:** uv + npm + Homebrew PostgreSQL, started by `scripts/dev.sh`. The development machine still has no container runtime; Cloud Build builds the production image in the cloud.

## 2026-10-07 — Phase 2 start: environment, versions and the local stack

### Decided

- **No containers on the development machine** (Atthar). Local development is uv + npm + Homebrew PostgreSQL, started by `scripts/dev.sh`, with no Compose file. [Partially superseded 2026-10-07: production now runs a container image, but Cloud Build builds it in the cloud, so the development machine still needs no container runtime.] PRD §8, §13 updated accordingly.
- **Pins verified 2026-10-07** (PyPI/npm/registry metadata and project release schedules; full table with sources in `docs/phase-2/phase2-version-pins.md`): Python **3.13** (LangGraph 1.2.14 declares 3.10–3.13 only, so 3.14 would put the orchestration library outside its declared support), Node **24 LTS**, Next.js **16.3.8**, React 19.2.8, Tailwind **4.3.3**, shadcn CLI **4.21.2**, FastAPI **0.142.2**, Uvicorn 0.54.0, Pydantic **2.13.5**, psycopg **3.3.6** `[binary]`, PostgreSQL **18.6**, uv **0.12.23**.
- **Boring-pin rule:** releases published hours before retrieval are skipped in favour of the previous patch (Next 16.4.0 → 16.3.8; shadcn 4.21.3 → 4.21.2), while routine patch bumps are taken (LangGraph 1.2.14, psycopg 3.3.6). Rationale: a regression in the toolchain costs thesis days; one patch of soak costs nothing.
- **TypeScript stays 5.x** (create-next-app resolved `^5`). TypeScript 7 is the native Go compiler rewrite and does not expose the JS compiler API, which non-Next tooling still consumes.
- **Region: Singapore** for everything that offers a choice. [Superseded 2026-10-07 for the Oracle reasoning: the tenancy's permanent home region no longer applies. Cloud Run runs in `asia-southeast1` and Neon is provisioned in a Singapore region.]
- **Hostname:** [superseded 2026-10-07 — Cloud Run provides an HTTPS `*.run.app` URL with a managed certificate, so no DuckDNS name and no reverse proxy are needed.]
- **Dependencies are installed when the phase that uses them starts**: LangGraph and psycopg's checkpointer are *pinned now* but not installed until phase 4, so the phase-2 lockfile stays small.

### Schema and auth decisions (implemented)

- **Two database roles.** `thesis_migrator` owns the schema; `thesis_app` is what the API connects as. A table owner bypasses RLS unless `FORCE` is set (set), and a superuser bypasses it regardless — hence a plain non-superuser runtime role.
- **One uniform tenant policy.** Every tenant table carries `owner_id` and one policy compares it with `app.current_user_id()`, set per transaction by `SET LOCAL`. Denormalising `owner_id` onto leaf tables was chosen over multi-level join policies: uniform, auditable, and no recursive policy evaluation.
- **`users` and `sessions` are deliberately not row-level-secured.** Resolving a session token to a user happens before any tenant context exists; both tables are reachable only through the auth code path. Every other table is covered.
- **Row factories are set per cursor, never on the connection.** Pooled connections are shared, and mutating `conn.row_factory` leaked a dict factory into a later request — caught by the RLS test, not by review.
- **Session and CSRF cookies**: session is httpOnly, CSRF is readable and echoed in `X-CSRF-Token` (double submit), both SameSite=Lax, `Secure` off locally and on in production, no `Domain` unless set.
- **Login throttling is in-process** (5 attempts / 15 min per IP+email). One process, one host: a Postgres-backed limiter is the upgrade path if the app ever runs multiple workers.
- **The frontend fetches in the browser, never in a server component**, so no hosting provider processes student text (keeps O-5 and O-7 consistent). The API error strings are mapped to Indonesian in the client; message codes arrive with the language toggle (FR-18).

### Verified on 2026-10-07 (local)

- PostgreSQL 18.6 running locally; `scripts/bootstrap_db.sh` creates roles and both databases; `0001_init.sql` applies.
- `ruff check` clean, `mypy app` clean, **10/10 backend tests pass**, including DB-enforced tenant isolation (a lecturer cannot read or write another's rows) and no-context-means-no-rows.
- Frontend `eslint`, `tsc --noEmit` and `next build` clean.
- Real browser walkthrough: signup → dashboard (name shown), logout → login → dashboard, wrong password → inline Indonesian error, session cookie httpOnly, CSRF cookie JS-readable.

### Note on phase-1 access dates

Phase-1 pages were fetched late in the evening of 2026-10-06 local (UTC+7); a few provider pages carry their own `last_updated` stamp of 2026-10-07 because the fetch crossed local midnight. Phase-1 evidence files are dated 2026-10-06; phase-2 research is dated 2026-10-07.

## 2026-10-06 — Phase 1 gate, part 2: hosting, frontend and the privacy rules (decided by Atthar)

### O-2 resolved — backend host: Oracle Cloud Always Free ARM VM

- **Decision:** 2 OCPU / 12 GB RAM / 200 GB block volume, always-on, Singapore region; systemd services; Caddy reverse proxy for TLS; Docker optional, not required.
- **Options considered:** Render free, Koyeb free, Railway free (all 512 MB class), Google Cloud Run, Hugging Face Spaces, Oracle Always Free.
- **Why:** no cold start, no invocation or credit cap, no egress bill, and no third party inside the student-data path. The 512 MB class became technically possible again after O-4 removed the model weights, but adds 0.1 CPU and idle spin-downs for no benefit once a VM is in the design. Limits verified 2026-10-06: `docs/phase-1/phase1-hosting-free-tiers.md`.
- **Risks accepted and to manage:** OCI may reclaim an A1 instance when CPU, network and memory all stay below the 20th percentile over a 7-day window — the workload must keep the instance visibly active; OS patching, database backups (`pg_dump`) and certificate renewal are ours; signup requires a card for identity verification (no charge unless upgraded).

### O-3 resolved — PostgreSQL self-hosted on the same VM (agent's choice, per Atthar's instruction)

- **Decision:** PostgreSQL on the Oracle VM, auth inside the FastAPI app, submission files on the VM block volume. Documented fallback: Supabase (Postgres + Auth + Storage).
- **Options considered:** Supabase free, Neon free, Oracle Autonomous DB (the three on the open list), plus self-hosting on the VM.
- **Why:** (1) Oracle Autonomous DB cannot back the LangGraph checkpointer — LangGraph ships savers for Postgres and SQLite only (verified 2026-10-06), so the Oracle option is ruled out technically, not by preference; (2) `StudentIdentity.real_identifier` is the highest-harm table in the system and must not sit in a third-party free database; (3) both managed free tiers add a demo-day failure mode (Supabase pauses after 7 days of low activity and needs a manual unpause; Neon scales to zero after 5 minutes) and neither covers auth and file storage without a second service; (4) the VM already exists under O-2, so this removes dependencies rather than adding them.
- **Cost accepted:** auth is ours to get right — argon2id hashing, httpOnly/Secure/SameSite cookies, CSRF protection on state-changing requests, login rate limiting, and row-level security enforced in Postgres, not only in the UI. If that proves too risky in phase 2, Supabase is the fallback with the same SQL schema.

### O-5 resolved — frontend served from the same Oracle VM (agent's choice, per Atthar's instruction)

- **Decision:** Next.js `output: 'standalone'` behind Caddy on the same VM as the backend. Managed fallback if that proves heavy: Azure Static Web Apps Free.
- **Research:** 12 candidates against SSR support, limits, idle behaviour, TLS, free-tier clauses, privacy and logs, every row sourced and dated → `docs/phase-1/phase1-frontend-hosting.md`.
- **Why not a provider:** Vercel Hobby is the only free tier whose written terms are a genuine risk — "Hobby teams are restricted to non-commercial personal use only", and its definition of commercial reaches "a paid employee or consultant writing the code". Cloudflare Workers Free caps CPU at 10 ms per invocation while Cloudflare's own docs say SSR "typically use[s] 10-20 ms" (Error 1102); Netlify Free is a 300-credit hard cap (~15 GB bandwidth) and may delete a project "without notice"; Render Free is 512 MB / 0.1 CPU with a 15-minute spin-down; Deno Deploy shuts idle apps down after ~20–30 seconds; Firebase Spark cannot serve SSR at all; GitHub Pages is static-only and bans SaaS use. The VM has no clause, no cold start and no cap.
- **Why it also satisfies O-7:** with the frontend on the same host, server-side rendering reads student text over localhost, so no frontend provider ever processes it. On any managed host that would have required client-side fetching as a workaround.

### O-6 resolved — no provider that trains on prompts

- **Decision:** a route whose free tier may train on or human-review prompt content may never be configured. The chosen provider satisfies this: Cloudflare states it "does not use your Customer Content to (1) train any AI models made available on Workers AI or (2) improve any Cloudflare or third-party services".
- **Consequence:** OpenRouter's free endpoints, the Google AI Studio free tier, Mistral Free mode and the BytePlus/Volcano reward programs are permanently excluded, whatever their capability. Any future swap re-verifies the stance from the provider's own page and records the source and date here.
- **Also accepted:** the chosen model is on Cloudflare's free list today, but Cloudflare publishes no deprecation policy — so the run records its model version, and a withdrawn model flags the run rather than silently re-pointing it (PRD §11).

### O-7 resolved — no identifying data leaves; minimum necessary segment only

- **Decision:** send only the text segment the calling agent needs, with identifiers removed. A provider never receives data that can identify a student. Still the supervisors' call: institutional ethics clearance (PRD §14).
- **Design consequences, now in PRD §5 (FR-04), §6 and §11:**
  1. **Minimisation, not relabelling, on the egress path.** An identifier found inside the analysis text is deleted, not replaced with a stable per-student code, so a provider cannot link two submissions from the same student. Internal storage keeps the FR-04 mapping for review and linkage; that mapping never leaves the VM.
  2. **No submission reference in the payload.** Correlation lives in AgentTrace locally.
  3. **Defence in depth.** Ingest filters first; the provider client — the single egress point — re-checks each payload and blocks the call instead of sending a detected identifier, flagging the submission for review.
  4. **Files and images are never sent.** Screenshots are extracted to text locally first.
  5. **Never sent:** the submission file, filename, document metadata, images, the AI-output segment to an agent that does not need it, the pseudonymisation mapping, or any identifier.
- **Residual risk, stated rather than hidden:** text that is not an identifier can still be quasi-identifying (a distinctive anecdote, a rare combination of course and cohort). Minimisation reduces this; it does not eliminate it, which is why the ethics clearance question stays open with the supervisors.

## 2026-10-06 — Phase 1 gate: O-4 reversed, O-1 resolved (decided by Atthar)

### O-4 reversed — IndoBERT fine-tuning dropped

- **Options considered:** (a) label archived submissions with Bloom levels, fine-tune an IndoBERT base, evaluate, then load the checkpoint into the backend (PRD §7a); (b) stub the cognitive agent with the keyword baseline (Baseline 1 in the SLR metric sheet) and swap in the real classifier later.
- **Decision: neither.** The cognitive dimension is served by an LLM cognitive agent with few-shot prompting — the same approach as the metacognitive agent — as a separate agent, not merged into one call.
- **Why (Atthar's reason):** only tens of archived submissions exist, and the higher-order Bloom levels likely have zero or near-zero examples; a classifier cannot predict a class it never saw in training. This is a data-size problem, not something more tuning fixes.
- **Supported by the phase-1 evidence:** no provenance-clear fine-tuned Indonesian Bloom classifier exists publicly (5 community checkpoints, reported accuracy 0.49–0.58, most with no model card, no license and no documented training data); the strongest published result (Baharuddin & Naufal, JISEBI 9(2):253-263, 2023, 97%) released its dataset but not its weights; and no public dataset of labelled student analysis text with Bloom levels was found in any language, not only Indonesian. See `docs/phase-1/phase1-indobert-checkpoints.md`.
- **Consequence:** no model weights and no inference framework in the backend; the RAM floor drops (see the updated PRD §8 row). PRD §2, §5 (FR-07/FR-14/FR-15), §6, §7, §7a (superseded, kept as the record), §8, §11, §12, §13, §14 updated the same day. The old IndoBERT labelling question in §14 is replaced by the few-shot calibration question (below), and the token-attribution question now applies to LLM-produced cognitive scores.

### O-1 resolved — one model, one provider, per role

| Role | Model | Decided by |
| --- | --- | --- |
| Orchestrator | No LLM — LangGraph routing is rule-based | agent recommendation, accepted by Atthar |
| Cognitive agent | Cloudflare Workers AI `@cf/google/gemma-4-26b-a4b-it` | agent recommendation, accepted by Atthar |
| Metacognitive agent | same model | same |
| Synthesis agent | same model | same |

- **Why this model:** best Bahasa Indonesia evidence among free open-weight routes (SEA-HELM, Sep 2026 — Gemma 4 31B **79.75**, Qwen 3.6 **77.96**, SEA-LION v4.5 27B **76.51**, gpt-oss-120b **72.28**); 256k context; native function calling; the largest free token budget of the candidates (~1.10M input tokens/day inside Cloudflare's 10,000 Neurons/day), which is what has to absorb the new 3–5 run-to-run variance requirement; and Cloudflare's published position that it does not use Customer Content to train AI models or to improve Cloudflare or third-party services. One provider means one data-use policy for all pseudonymised student text.
- **Cognitive agent defaults to the same model, per instruction:** nothing in the criteria table justifies a second provider. The runner-up, Groq `openai/gpt-oss-120b`, wins on structured output (constrained decoding — "Never errors or produces invalid JSON") but loses on Bahasa Indonesia evidence (72.28 vs 79.75) and on free quota (200K tokens/day cannot absorb 3–5 cognitive runs × ~30 submissions plus the other agents), and Groq's own two live pages contradict each other on its free limits. Recorded as the alternative; not configured.
- **Accepted residual risk:** Cloudflare's JSON Mode is hint-level — "Workers AI can't guarantee that the model responds according to the requested JSON Schema". Mitigated by schema validation, retry, and the existing "needs review" flag (PRD §6); to be measured when phase 4 runs. A single-model design also means one outage hits every dimension — the config-driven client (PRD §8) is what makes a swap a config change.
- **Sources:** `docs/phase-1/phase1-providers-primary.md`, `phase1-aggregators-regional.md`, `phase1-indo-llm-capability.md` (all fetched 2026-10-06).
- **New open question recorded (PRD §14):** who writes the few-shot example for a Bloom level with zero real examples, and how that synthetic example is validated so it does not bias the agent toward one phrasing. Also recorded: the multi-agent justification must now argue consistency and auditability, not raw accuracy (D1/D2/J3).

## Phase 1 — Research and decisions (2026-10-06)

- **2026-10-06 · Interim metacognitive rubric fixed to G1's four SRL codes (elaborasi, organisasi, orientasi, evaluasi), stored as data (RubricVersion), flagged interim pending the supervisors' guideline · no alternative adopted; supervisors' rubric not yet received · decided by PRD §13 working rule (Atthar previously).**
- **2026-10-06 · No LLM, no hosting provider, no IndoBERT checkpoint chosen by the agent in phase 1 · options only · reserved for Atthar. (Partly superseded the same day: O-1 and O-4 were then decided by Atthar — see the gate entry above. O-2/O-3/O-5/O-6/O-7 remain open.)** PRD §7/§8/§7a.
- **2026-10-06 · All phase-1 provider limits, licences and models treated as facts only when read from a primary page on 2026-10-06; claims that could not be verified on a live page are recorded as `[UNVERIFIED]` with the reason · decided by agent, per PRD §13 ("verify … record the source and date").** Evidence archived in `docs/phase-1/` (16 files).
- **2026-10-06 · Local inference stays ruled out (PRD §7); no exception taken for Hugging Face Spaces self-hosted inference.**
- **2026-10-06 · Phase-1 submission corpus = the 4 AI-output submissions in the repo root (`Tugas 1–4 … .pdf`, MRTI semester 2). 5 further own submissions (Tugas 5–8, Tugas Akhir) contain no AI output at all and were read as structure evidence only. Other students' variants do not exist locally yet · consequence: FR-05 design is deferred until real variants exist · stated by Atthar, recorded by agent.**
- **2026-10-06 · AI evidence files written to `docs/phase-1/` (research only, no application code) · decided by agent.**

## Findings that constrain later phases (not choices)

- Groq no longer serves Llama on the free tier (Enterprise/"ContactSales"; deprecation page records Llama 3.1 8B + 3.3 70B shutdown 2026-08-16). GitHub Models retired entirely 2026-07-30. Together AI free Llama endpoints removed 2025-11-13 / 2026-03-06. → Any thesis text naming "Llama 3.1 via Ollama" (PRD §7) is obsolete on both counts (local inference ruled out; free hosted Llama gone at those providers).
- Hugging Face free accounts can no longer create Gradio or Docker Spaces (HTTP 402; PRO $9/month required) → the PRD §8 "Hugging Face Spaces free" backend option is dead as written.
- Render free = 512 MB RAM / 0.1 CPU. **Updated 2026-10-06 after O-4:** with no model weights in the backend (no torch, no transformers), the resident floor drops from ≈1.3–2.0 GB to an estimated ≈250–400 MB, so the 512 MB-class hosts (Render, Koyeb, Railway) are no longer ruled out on RAM — the remaining costs are 0.1 CPU and idle spin-downs, and the estimate must be confirmed by measurement in phase 2. Docker was never the blocker on any host: none requires it for a native Python service.
- No fine-tuned IndoBERT Bloom classifier with clean provenance exists publicly (5 community checkpoints, 0.49–0.58 accuracy, mostly no card/license/dataset), and no public dataset of labelled student-analysis Bloom data exists in any language. **Superseded as a plan (O-4, 2026-10-06):** the labelling pass is not needed because there is no fine-tuning — but the same constraint carries over to the cognitive agent's few-shot examples, which Atthar must author or validate rather than the agent inventing them (PRD §14).
- Free-tier data policy is the binding constraint, not capability: the strongest Indonesian numbers today belong to general models (Gemma 4 31B 79.75, Qwen 3.6 77.96 on SEA-HELM Sep 2026), while several free routes (Gemini free tier, OpenRouter free endpoints, Mistral free mode, Volcano/BytePlus rewards) train on or human-review prompt content.

## Verification log

| Date | Verified | Source |
| --- | --- | --- |
| 2026-10-06 | Free-tier limits, licences, model IDs and data-use terms for 23 providers + 43 models | see `docs/phase-1/*.md`, every claim URL-cited |
| 2026-10-06 | Free-tier hosting limits: Vercel, Render, HF Spaces, Koyeb, Fly.io, Railway, PythonAnywhere, Oracle, Cloud Run, Azure, Supabase, Neon | `docs/phase-1/phase1-hosting-free-tiers.md` |
| 2026-10-06 | Frontend hosting for Next.js App Router on 12 free candidates (limits, idle behaviour, free-tier clauses, privacy, logs) | `docs/phase-1/phase1-frontend-hosting.md` |
| 2026-10-06 | LangGraph checkpoint savers: Postgres and SQLite only — Oracle Autonomous DB cannot back the checkpointer | [docs.langchain.com — checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers) |
| 2026-10-06 | Vercel Hobby fair-use clause: "non-commercial personal use only", including "a paid employee or consultant writing the code" | [vercel.com/docs/limits/fair-use-guidelines](https://vercel.com/docs/limits/fair-use-guidelines) |
