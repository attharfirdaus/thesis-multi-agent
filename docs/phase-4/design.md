# Phase 4 design — the agent pipeline

Two constraints shaped this phase, and one of them is now lifted. **The gate cannot be demonstrated
without calibration examples** — the graph refuses to score against an empty block (PRD §6), and the
content is Atthar's (PRD §14), which he supplied on 2026-10-15. And **it could not be demonstrated
against the real provider without a key** — Atthar supplied Cloudflare Workers AI credentials on
2026-10-15, so the gate has since been run for real on the four archived submissions; the measurements
are at the bottom of this file and in DECISIONS.md.

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

## The calibration block

The calibration is the one piece of prompt content that is not the coding agent's to write (PRD §14), so
it lives in a file, not in code: `backend/scripts/calibration.json`, seeded into a versioned
`PromptVersion` row by `scripts/seed_rubric.py --calibration` (that file is the default). It is keyed by
agent — six Bloom examples for the cognitive agent, five SRL examples for the metacognitive one — because
two agents with different rubrics cannot share one example list without each being prompted with the
other's material. A file missing either block is refused when it is read, not at the first job that
reaches that agent.

Three deliberate alignments came out of adopting it, all recorded in DECISIONS.md:

- the level scale is the six Bloom codes (`C1`…`C6`) with the names as `RubricVersion.descriptors.levels`,
  because that is what the examples return and what the agents therefore produce;
- `Strength` is `lemah | sedang | kuat`, the words the calibration uses and the words a lecturer reads;
- the JSON field names inside the examples were rewritten to the agent schemas (`evidence_quote`,
  `present`, `indicator`), and the zero-code example is expressed as the schema's own shape. An example
  whose keys differ from the schema the answer is validated against teaches the wrong shape; this is the
  only place the supplied text was altered, and it is flagged for Atthar to veto.

`catatan_sumber` — which marks the two synthetic examples and the zero-code case — is stripped when the
block is rendered, so provenance never becomes model input. Two of the six Bloom examples (C5, C6) are
synthetic: no real example exists at those levels in the archive, and how they are validated against
biasing the agent remains an open question in PRD §14.

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
| `tests/test_prompts.py` | The shipped calibration reaches both prompts, each agent sees only its own block, provenance notes stay out, and a calibration file missing an agent block is refused |
| `tests/test_graph.py` | Per-agent behaviour: retry on a bad answer, the review flag on a quote that cannot be located, a failed synthesis retry keeping the first synthesis |
| `tests/test_jobs.py` | Claim exclusivity, `attempts` on failure, a failed submission not failing the batch, stale-lease recovery |
| `tests/test_real_corpus.py` | The four real archived PDFs in `samples/`: 4 imported → 4 jobs done → run `done`; every returned span reproduces its quote inside the real Indonesian text (`text[start:end] == quote`); feedback present per submission; checkpoints written |
| One run against the real provider, 2026-10-15 | The four archived PDFs, no stub: 4/4 imported, 4/4 jobs `done`, run `done`, 12 provider calls, 11 usable first try, 1 retried, 1 failed on a ReadTimeout without failing the batch, latency 19.98–85.77 s per call (mean 44.47 s), 3 quotes located, 342 checkpoints |

Measured 2026-10-15 on the real corpus with the provider stubbed: 20 evidence spans across the four
submissions, 20 `system_scores`, 12 `agent_traces`, 24 LangGraph checkpoint rows.

The provider stub answers with a slice of the submission's own stored text, so the offsets still have to
be computed by the real evidence code — a stub that returns a canned quote would have made the offset
assertion meaningless.

## What the real run showed, and what it left open

Measured 2026-10-15 against `@cf/google/gemma-4-26b-a4b-it` (temperature 0, `seed` unset), four archived
submissions, no stub:

- **JSON adherence is good enough to build on:** 11 of 12 calls returned a valid object on the first
  attempt; the one retry succeeded on the second. Cloudflare's JSON mode is hint-level, and at this sample
  size it held.
- **A provider failure does not take the batch with it:** one cognitive call timed out three times, that
  submission was flagged `cognitive_agent_failed`, its metacognitive findings were stored, and the run
  finished `done` with `needs_review = 1`.
- **Latency is the binding cost, not correctness:** 19.98–85.77 s per call, mean 44.47 s, 13.5 minutes for
  four submissions. That is the number PRD §11's performance target has to be set from. **Superseded
  2026-10-16:** most of that time was the model deliberating, not the provider serving — the model is a
  reasoning model and the request did not disable thinking, so the same calls now answer in 1.5–8 s. The new
  numbers, the mechanism and the fix are in DECISIONS.md; PRD §11's target should be re-derived from them.
- **`exact` string equality is the wrong evidence metric.** Three quotes were stored and all three were
  located, but none matched the stored text character for character: the differences were line breaks, and
  the normalised comparison was equal in all three cases. A paraphrase would fail both tests, which is
  what the check is for.
- **The metacognitive agent reported all four codes absent on all four submissions (16/16)**, each with its
  own rationale. Either these analyses really contain no self-regulation traces, or the calibration biases
  the agent toward `absent`. Raised to Atthar; not tuned here, because the calibration is his content and
  adjusting it until it produces more `true`s would be fitting the instrument to the result.
- **Still unmeasured:** the provider's `seed` parameter was never exercised, so the reproducibility stance
  has no measurement behind it; and run-to-run variance (3–5 repeats per dimension, PRD §11) is not
  implemented, so nothing here says how stable these scores are between calls. Both are open in PRD §14.
- **`single_agent` mode is stored, not implemented.** The run records the mode it was created with, but
  both modes execute the multi-agent path; the single-agent baseline is phase 6 (PRD §13).

## Defects this gate run found

**`agent_traces.latency_ms` was null in every row** — 12 of 12. The client measured the latency, and the
code deliberately dropped it, on the argument that a state key carrying only a metric was not worth having.
PRD §10 lists the column and PRD §11 asks for per-step observability, and the run was paying 20–86 s per
call while discarding the number. Fixed with a `latencies` channel in `GraphState` (merge reducer, because
the two analysis agents write it in parallel), filled by each node from its own `Completion`, written by
`persist`; a failed synthesis retry keeps the first call's latency, because that call's result is the one
stored. Tests cover both the state and the stored trace rows.

The class of error is the same as phase 3's: **a value the pipeline already pays for, discarded before it
reaches the record**, invisible to unit tests because every unit test supplied its own metric. It took a
real run against a real provider, with real seconds, to make it visible.

## Dependencies

`pydantic==2.13.5`, `pydantic-settings==2.15.0`, `psycopg[binary,pool]==3.3.6`, `langgraph==1.2.15`,
`langgraph-checkpoint-postgres==3.1.2`, `httpx==0.28.1` — all verified on PyPI on 2026-10-14, before
they were pinned (`pyproject.toml`). `langgraph-checkpoint-postgres` is pinned one minor behind the same
day's 3.2.0 on purpose: the boring pin is the one to debug from.
