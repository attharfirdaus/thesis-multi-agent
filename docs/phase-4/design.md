# Phase 4 design — the agent pipeline

Constraint that shapes everything below: **this gate can be demonstrated with no provider key, but not
with no calibration examples.** The graph refuses to score against an empty calibration row (PRD §6), and
the content of those examples is Atthar's (PRD §14) — so every end-to-end run in this phase, including
the one recorded at the bottom, uses a clearly-labelled fixture that must never be seeded as the real
row. `scripts/seed_rubric` therefore writes the calibration row *empty* and flagged `pending_atthar`.

## The graph (PRD §6)

```
START → preprocess ─┬→ cognitive      ─┬→ synthesis → evidence → END
                    └→ metacognitive  ─┘
```

- **Orchestrator: no LLM.** Routing is the LangGraph edge set above. Decision O-1 (2026-10-06) chose a
  rule-based orchestrator, so there is no routing model to score, no router prompt to version and no
  routing tokens to pay for.
- **preprocess** assembles each agent's two turns from the *run's own snapshot*: `rubric_version_id` and
  `prompt_version_ids` as frozen when the run was created, never the newest versions (PRD §11). Rubric
  values reach the prompt as data — no Bloom level and no SRL code is a literal in a template, so the
  supervisors' guideline can replace all of it without a code change. Calibration is mandatory for the
  two analysis agents: an empty list raises `MissingCalibration` and the run is refused rather than
  silently degraded. The student's text is passed inside `<teks_mahasiswa>` delimiters and the system
  turn states it is data, never an instruction — a submission is untrusted input.
- **cognitive** and **metacognitive** run independently off preprocess. Both are the same configured
  model (O-1): one provider, one data-use policy for all pseudonymised student text.
- **synthesis** consumes both and produces the per-student rationale and feedback text.
- **evidence** is the check that makes a score defensible: every quote an agent returned must be
  findable in the text that was scored. A quote that fails twice is *kept* with a `needs review` flag
  rather than discarding the score (PRD §6, FR-09), so a lecturer sees a flagged claim instead of a
  missing row and the thesis can report the failure rate honestly. The one synthesis retry is given the
  failure reason; if the retry fails, the first synthesis is kept — a failed retry must not cost a usable
  explanation.

## Provider client — the single egress point

`app/llm/client.py` is the only place submission text leaves the process, which is what makes the
privacy claim checkable rather than aspirational:

- the payload is re-checked for identifiers immediately before the POST and the call is **blocked**, not
  warned about (PRD §11);
- the answer is validated against the caller's Pydantic schema, so a hallucinated field is a retry and
  not a wrong score;
- up to `LLM_MAX_ATTEMPTS` (default 3) attempts, then the error is raised and the *job* owns the retry;
- `temperature` and `seed` come from configuration and are part of the run's `model_config` snapshot;
- no model name, no account id and no provider URL appears in code — they are `LLM_BASE_URL`,
  `LLM_MODEL`, `LLM_API_KEY` (PRD §11).

Cloudflare's JSON mode is hint-level ("can't guarantee that the model responds according to the
requested JSON Schema", recorded in DECISIONS.md), which is exactly why schema validation, the attempt
count and the review flag exist rather than being assumed away.

## Job queue and worker

`app/jobs/queue.py` claims with `FOR UPDATE SKIP LOCKED` and `status = 'running'` is the lease for the
interval a provider call takes. The claim commits **before** the graph runs: a transaction is never held
across a network call, so a slow provider cannot pin a pooled connection for the batch.

- `MAX_ATTEMPTS = 3`, and `attempts` is incremented when an attempt **fails**, so a process that dies
  mid-submission does not spend one of the job's retries.
- A failed submission never fails the batch (`_run_one` catches, records, continues).
- `_requeue_stale` returns this run's `running` rows to `queued` at the start of a pass, which is what
  makes the CLI a resume rather than a riddle: a crash costs one attempt, not the rest of the batch.
- The API (`POST /runs/{id}/process`) and `python -m app.jobs.worker` are two drivers of the same call.
  One driver per run is assumed; two would requeue each other's in-flight jobs.
- `limit` bounds what one call takes, so an offline provider cannot burn a whole batch's retries in one
  pass and the UI stays responsive between batches.

## Checkpointing

The graph is compiled with LangGraph's Postgres saver and the **submission id is the thread**, so an
interrupted submission resumes at its last completed step instead of paying for the whole pipeline
again. One saver per batch pass, not per submission: the saver writes on every node transition, and a
connection per job would add a connect to each of the 25 jobs a pass can claim.

The tables are LangGraph's, not ours, so they are created by `scripts/setup_checkpointer.py` rather than
by a migration, and that script also grants DML to the runtime role — the runtime role is deliberately
not the owner, so without the grant the first checkpoint write fails. Missing tables are a loud failure,
never a silent downgrade to no checkpointing. CI, `scripts/dev.sh` and the test fixtures all run the
script.

## Persistence and the evidence contract

`system_scores` and `evidence` are written per submission from the final graph state; `evidence` carries
`start_offset`/`end_offset` into the stored (redacted) `student_analysis_text`, which is the contract the
lecturer's evidence view rests on. `GET /runs/{id}/results` returns scores with their spans and the
feedback text in one response (FR-10, FR-14).

Migration `0004_run_flags.sql` adds `submissions.review_flags` (a `jsonb` list of machine-written
reasons). PRD §6 saves a score *with* a needs-review flag rather than discarding it, and there was no
column for it — without this the flag would have been computed and thrown away. A list, not a boolean,
because the reasons differ: an unlocated quote, an agent that produced nothing, an indicator the agent
was unsure about. FR-09 needs to say which.

## Gate evidence (PRD §13 phase 4)

| Level | What it proves |
| --- | --- |
| `tests/test_runs_api.py` | The whole path over HTTP on a synthetic docx: create run → `process` → jobs counted → results with spans and feedback |
| `tests/test_runs_api.py`, calibration tests | An empty calibration row refuses the run; the refusal reaches the job's `last_error` |
| `tests/test_graph.py` | Per-agent behaviour: retry on a bad answer, the review flag on a quote that cannot be located, a failed synthesis retry keeping the first synthesis |
| `tests/test_jobs.py` | Claim exclusivity, `attempts` on failure, a failed submission not failing the batch, stale-lease recovery |
| `tests/test_real_corpus.py` | The four real archived PDFs in `samples/`: 4 imported → 4 jobs done → run `done`; every returned span reproduces its quote inside the real Indonesian text (`text[start:end] == quote`); feedback present per submission; checkpoints written |

Measured 2026-10-15 on the real corpus with the provider stubbed: 20 evidence spans across the four
submissions, 20 `system_scores`, 12 `agent_traces`, 24 LangGraph checkpoint rows.

The provider stub answers with a slice of the submission's own stored text, so the offsets still have to
be computed by the real evidence code — a stub that returns a canned quote would have made the offset
assertion meaningless.

## What is not verified, and why

- **No real provider call.** No API key exists in this environment, so JSON-mode adherence, latency, the
  retry path against a real 429/5xx, and Bahasa Indonesia scoring quality are all unmeasured. Everything
  PRD §7 says about the model's competence remains the provider's own documentation until a key exists.
- **The calibration content is empty.** By design (PRD §14): the examples are Atthar's, and the seeded
  row says `pending_atthar`. A real run therefore refuses until they are supplied — verified, including
  the job-level error text.
- **Run-to-run variance is not implemented (PRD §11).** One LLM call per dimension per submission, not
  3–5 with mean ± SD. Not a silent omission: recorded in DECISIONS.md and raised with Atthar, because it
  changes run semantics and multiplies batch cost.
- **`single_agent` mode is stored, not implemented.** The run records the mode it was created with, but
  both modes execute the multi-agent path; the single-agent baseline is phase 6 (PRD §13).

## Dependencies

`pydantic==2.13.5`, `pydantic-settings==2.15.0`, `psycopg[binary,pool]==3.3.6`, `langgraph==1.2.15`,
`langgraph-checkpoint-postgres==3.1.2`, `httpx==0.28.1` — all verified on PyPI on 2026-10-14, before
they were pinned (`pyproject.toml`). `langgraph-checkpoint-postgres` is pinned one minor behind the same
day's 3.2.0 on purpose: the boring pin is the one to debug from.
