"""The bounded runner that turns queued jobs into finished graph states (FR-06).

One function, two entry points: the API request that starts a run calls `process_run`, and
`uv run python -m app.jobs.worker --owner <email> --run <id>` is the same call after a crash.

The worker does not persist results. It returns the final `GraphState` of every submission it
finished and the caller writes the scores, evidence and feedback from it; and it knows nothing
about HTTP, because resuming from the command line has no request to answer. A job that fails is
never fatal to the batch (PRD §11): the failure is recorded on that job, the rest of the batch runs,
and the job is retried until `MAX_ATTEMPTS` is reached.
"""

import argparse
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app import db
from app.agents.graph import evaluate_submission
from app.agents.models import GraphState
from app.agents.persist import persist_submission_result
from app.agents.segments import from_stored, stored
from app.config import get_settings
from app.jobs.queue import claim_jobs
from app.llm.client import ModelUnavailable

# A submission that fails this many times is not retried: the model or the prompt is wrong, not the
# network, and the lecturer should see the job in the failed list rather than wait on it.
MAX_ATTEMPTS = 3

# Jobs claimed per pass. The graph call takes seconds and no transaction is held across it, so this
# bounds only how much of a large batch one call picks up.
BATCH = 25

#: The Pydantic types the graph writes into its state, and therefore into the checkpoints. LangGraph's
#: serde needs them named to keep deserialising them across an upgrade; see `_checkpointer`.
CHECKPOINT_STATE_TYPES = (
    "CognitiveResult",
    "MetacognitiveResult",
    "SegmentLevel",
    "SegmentIndicators",
    "IndicatorFinding",
    "SynthesisResult",
    "SingleAgentResult",
    "EvidenceSpan",
)
#: Types the graph state holds that live outside `app.agents.models`.
CHECKPOINT_EXTRA_TYPES = (("app.agents.segments", "Segment"),)


def _requeue_stale(conn, *, owner_id: UUID, run_id: UUID) -> None:
    """Return this run's `running` jobs to the queue.

    A job is `running` only between the claim and the outcome, so a row still `running` when a pass
    starts belongs to a process that died in that window. Re-queueing it is what makes the command
    line a resume rather than a riddle: the crash costs the interrupted submission one attempt, not
    the remainder of the batch.

    One driver per run is assumed — the API call and the CLI are not pointed at the same run at the
    same time. Two drivers would re-queue each other's in-flight jobs.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            update jobs set status = 'queued', updated_at = now()
            where owner_id = %s and run_id = %s and status = 'running'
            """,
            (owner_id, run_id),
        )


def _load_state(conn, *, owner_id: UUID, run_id: UUID, submission_id: UUID) -> GraphState:
    """Assemble the graph's input from what this run froze when it was created.

    The rubric and the calibration examples come from the run's own `rubric_version_id` and
    `prompt_version_ids`, never from the newest version, so re-running an old run reproduces it
    (PRD §11). The run's other prompt rows are loaded and dropped: they are the snapshot PRD §10
    records for the thesis, while the templates the agents actually prompt with live in
    `app.agents.prompts`. Only the two redacted segments of the submission are read — nothing else
    about a submitted document survives ingest, and nothing else may reach a provider.
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            select submissions.student_analysis_text, submissions.ai_output_text,
                   submissions.analysis_segments,
                   runs.prompt_version_ids, runs.mode, runs.model_config,
                   rubric_versions.version as rubric_version,
                   rubric_versions.dimensions, rubric_versions.levels,
                   rubric_versions.indicators, rubric_versions.descriptors
            from submissions, runs
            left join rubric_versions on rubric_versions.id = runs.rubric_version_id
            where submissions.id = %s and runs.id = %s
            """,
            (submission_id, run_id),
        )
        row = cur.fetchone()
        if row is None:
            raise LookupError(f"run {run_id} has no submission {submission_id} for its owner")
        if row["dimensions"] is None:
            raise LookupError(f"run {run_id} has no rubric version, so nothing can be scored against it")
        # The run is scored by the model it snapshotted, or not at all (KNF-04): a configuration that
        # now names another model would silently change what the run measures.
        configured = get_settings().llm_model
        snapshot = (row["model_config"] or {}).get("model")
        if snapshot and configured and snapshot != configured:
            raise ModelUnavailable(
                f"run {run_id} was created with model {snapshot!r}, but {configured!r} is configured"
            )
        cur.execute(
            "select template from prompt_versions where id = any(%s) and agent_name = 'calibration'",
            (row["prompt_version_ids"],),
        )
        calibration = cur.fetchone()
        # The stored row is the per-agent calibration block plus its provenance flags (Atthar's
        # content, PRD §14); each prompt builder reads its own agent's slice. A missing row stays an
        # empty dict so the builders refuse the run instead of skipping the calibration.
        prompts: dict = {"calibration": json.loads(calibration["template"]) if calibration else {}}
        # KF-05: score the split that was stored before measurement. A row imported before 0008 has
        # none, so the same rule is applied once and stored here, before this run's first agent call.
        text = row["student_analysis_text"] or ""
        segments = from_stored(row["analysis_segments"], text)
        if row["analysis_segments"] is None and text.strip():
            cur.execute(
                "update submissions set analysis_segments = %s where id = %s",
                (Jsonb(stored(segments)), submission_id),
            )
    return GraphState(
        owner_id=str(owner_id),
        run_id=str(run_id),
        submission_id=str(submission_id),
        # Selects the graph `evaluate_submission` runs (FR-15); set once here so the worker's CLI
        # and the API both route through the same place.
        mode=row["mode"],
        rubric={
            # The prompt states which rubric version produced the score, so a thesis claim about a
            # past run can be traced to the rubric that was in force (PRD §11).
            "version": row["rubric_version"],
            **{key: row[key] for key in ("dimensions", "levels", "indicators", "descriptors")},
        },
        prompts=prompts,
        student_analysis_text=text,
        segments=segments,
        ai_output_text=row["ai_output_text"] or "",
    )


def _flag_model_unavailable(owner_id: UUID, job: dict, error: Exception) -> None:
    """Fail the job without retrying and mark the run (KNF-04): retrying cannot bring a model back,
    and the run must say why it stopped rather than look like a run that merely failed."""
    with db.tenant_tx(owner_id) as conn:
        conn.execute(
            "update jobs set status = 'failed', attempts = attempts + 1, last_error = %s, "
            "updated_at = now() where id = %s and owner_id = %s",
            (f"{type(error).__name__}: {error}", job["id"], owner_id),
        )
        conn.execute(
            "update runs set model_unavailable = true where id = %s and owner_id = %s",
            (job["run_id"], owner_id),
        )


def _record_failure(owner_id: UUID, job: dict, error: Exception) -> bool:
    """Count the failed attempt, keep the reason, and report whether the job is finished.

    The verdict is computed in SQL from `attempts + 1` so two recorders cannot both read the old
    count and both decide the job still has retries left.
    """
    with db.tenant_tx(owner_id) as conn, conn.cursor() as cur:
        cur.execute(
            """
            update jobs
            set attempts = attempts + 1,
                last_error = %s,
                status = case when attempts + 1 >= %s then 'failed' else 'queued' end,
                updated_at = now()
            where id = %s and owner_id = %s
            returning status
            """,
            (f"{type(error).__name__}: {error}", MAX_ATTEMPTS, job["id"], owner_id),
        )
        row = cur.fetchone()
    if row is None:
        raise LookupError(f"job {job['id']} is no longer visible to its owner")
    return row[0] == "failed"


def _finish(owner_id: UUID, job: dict, state: GraphState) -> None:
    """Store the submission's result and mark its job done, in one transaction.

    Both, or neither: a job marked `done` with nothing stored is a failure that looks like success. This is
    also where the command line stopped persisting — the API endpoint was the only caller of
    `persist_submission_result`, so `python -m app.jobs.worker` graded submissions and threw the scores
    away, which is the exact opposite of what a resume tool may do (found live, 2026-10-16).
    """
    with db.tenant_tx(owner_id) as conn:
        persist_submission_result(
            conn,
            owner_id=owner_id,
            run_id=job["run_id"],
            submission_id=UUID(str(state["submission_id"])),
            state=state,
        )
        conn.execute(
            "update jobs set status = 'done', updated_at = now() where id = %s and owner_id = %s",
            (job["id"], owner_id),
        )


@contextmanager
def _checkpointer():
    """A LangGraph saver for one job (PRD §6).

    Missing checkpoint tables are a loud failure — `scripts/setup_checkpointer.py` is part of
    setting up a database, and silently running without checkpointing would hide that.

    The serde allows exactly the Pydantic types the graph puts in its state. Without that, LangGraph falls
    back to a permissive default: it warned on every one of them while resuming and says a future version
    will refuse to deserialise them at all (seen live, 2026-10-16). Naming them here means an upgrade
    cannot quietly break every resumable run.
    """
    from langgraph.checkpoint.postgres import PostgresSaver
    from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

    with psycopg.connect(
        get_settings().database_url,
        autocommit=True,
        prepare_threshold=0,
        row_factory=dict_row,
    ) as conn:
        yield PostgresSaver(
            conn,
            serde=JsonPlusSerializer(
                allowed_msgpack_modules=[
                    ("app.agents.models", name) for name in CHECKPOINT_STATE_TYPES
                ]
                + list(CHECKPOINT_EXTRA_TYPES)
            ),
        )


def _run_one(owner_id: UUID, job: dict) -> str:
    """Run one claimed job and return its outcome: `done`, `failed` (out of retries) or `skipped`
    (failed, will be retried).

    Each job opens its own saver: jobs of one pass run on separate threads, and a job is tens of
    seconds of provider calls against one connect.
    """
    thread_id = f"{job['run_id']}:{job['submission_id']}"
    with _checkpointer() as saver:
        try:
            with db.tenant_tx(owner_id) as conn:
                state = _load_state(
                    conn, owner_id=owner_id, run_id=job["run_id"], submission_id=job["submission_id"]
                )
            # Outside tenant context on purpose: the graph calls a provider and can take seconds, and
            # holding a transaction across that would pin a pooled connection for the whole batch.
            result = evaluate_submission(state, checkpointer=saver)
        except ModelUnavailable as error:
            _flag_model_unavailable(owner_id, job, error)
            saver.delete_thread(thread_id)
            return "failed"
        except Exception as error:  # noqa: BLE001 — a failed submission must never fail the batch
            if not _record_failure(owner_id, job, error):
                return "skipped"  # its checkpoint stays: the retry resumes from it
            saver.delete_thread(thread_id)
            return "failed"

    # A graph that produced nothing has not evaluated anything. Without this guard the job would be
    # marked done and the submission would look evaluated while carrying zero scores — which is how a
    # KeyError inside a prompt builder stayed invisible for a whole test run.
    if not any(result.get(agent) for agent in ("cognitive", "metacognitive", "synthesis")):
        failure = RuntimeError("no agent produced output: " + "; ".join(result.get("errors", [])))
        return "failed" if _record_failure(owner_id, job, failure) else "skipped"

    _finish(owner_id, job, result)
    return "done"


# Runs being driven by this process. Two drivers on one run re-queue each other's in-flight jobs and
# grade a submission twice — which is what leaving the assignment page and coming back did (seen
# 2026-11-10). A crashed process loses this set with everything else, so `_requeue_stale` stays right.
# ponytail: in-process registry, one API process assumed (README: the API runs locally). Move to a
# heartbeat lease on `jobs` if the API ever runs more than one worker; the CLI is still on its honour.
_driving: set[UUID] = set()
_driving_lock = threading.Lock()


def is_driving(run_id: UUID) -> bool:
    return run_id in _driving


def _begin(run_id: UUID) -> bool:
    with _driving_lock:
        if run_id in _driving:
            return False
        _driving.add(run_id)
        return True


def process_run(owner_id: UUID, run_id: UUID, limit: int | None = None) -> dict:
    """Claim this run's queued jobs once each, run them, and summarise what happened.

    `limit` caps how many jobs this call takes; `None` takes one full batch. Nothing loops until
    the queue is empty: a job that fails is put back with its attempt recorded, and a submission
    that needs three attempts therefore needs three passes, so an offline provider cannot burn a
    whole batch's retries in one call.

    Returns `claimed`, `done`, `failed` (out of retries) and `skipped` (failed, will be retried). The first
    three plus `skipped` always add up to `claimed`. Results are stored by `_finish` as each job completes,
    not returned: the caller has nothing left to persist. `busy` is true, with nothing claimed, when this
    process is already driving the run.
    """
    if not _begin(run_id):
        return {"claimed": 0, "done": 0, "failed": 0, "skipped": 0, "busy": True}
    try:
        return _process_pass(owner_id, run_id, limit)
    finally:
        _driving.discard(run_id)


def drive_run(owner_id: UUID, run_id: UUID) -> bool:
    """Drive the run to its end on a background thread; False when it is already being driven.

    The request that starts it returns at once, so no HTTP response waits minutes on provider calls
    (one long submission took 145 s, measured 2026-11-10) and the page polls the run instead. Passes
    repeat while they claim anything: a failing job runs out of attempts, a cancelled run has nothing
    queued, so the loop ends.
    """
    if not _begin(run_id):
        return False

    def work() -> None:
        try:
            while _process_pass(owner_id, run_id, None)["claimed"]:
                pass
        finally:
            _driving.discard(run_id)

    threading.Thread(target=work, name=f"run-{run_id}", daemon=True).start()
    return True


def _process_pass(owner_id: UUID, run_id: UUID, limit: int | None) -> dict:
    summary: dict = {"claimed": 0, "done": 0, "failed": 0, "skipped": 0, "busy": False}
    with db.tenant_tx(owner_id) as conn:
        _requeue_stale(conn, owner_id=owner_id, run_id=run_id)
        jobs = claim_jobs(
            conn, owner_id=owner_id, run_id=run_id, limit=BATCH if limit is None else limit
        )
        if jobs:
            # FR-13 keeps the run's own timestamps, and nobody wrote `started_at` before this. It marks
            # the first claim rather than the creation of the run, so a run left queued overnight says
            # when it actually began; `coalesce` keeps a resumed pass from moving the moment. The status
            # moves with it: a run reading `queued` while a job is being graded is a status that lies to
            # the screen watching it (seen live, 2026-10-16), and `status = 'queued'` keeps a cancelled
            # run cancelled.
            conn.execute(
                "update runs set status = 'running', "
                "started_at = coalesce(started_at, now()) "
                "where id = %s and owner_id = %s and status = 'queued'",
                (run_id, owner_id),
            )
    summary["claimed"] = len(jobs)
    if jobs:
        workers = min(get_settings().run_concurrency, len(jobs))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for outcome in pool.map(lambda job: _run_one(owner_id, job), jobs):
                summary[outcome] += 1
    _settle_run(owner_id, run_id)
    return summary


def _settle_run(owner_id: UUID, run_id: UUID) -> None:
    """A run with nothing queued or running is finished — including when the command line drove it.

    This is the only place a run becomes `done` and the only place `finished_at` is written for one:
    the API endpoint used to stamp it after every pass, so a run still grading already carried a finish
    time (seen 2026-11-10). The status predicate keeps a cancelled run cancelled.
    """
    with db.tenant_tx(owner_id) as conn, conn.cursor() as cur:
        cur.execute(
            "update runs set status = 'done', finished_at = coalesce(finished_at, now()) "
            "where id = %s and owner_id = %s and status in ('queued', 'running') "
            "and not exists ("
            "  select 1 from jobs where jobs.run_id = runs.id and jobs.status in ('queued', 'running')"
            ")",
            (run_id, owner_id),
        )


def _owner_id(email: str) -> UUID:
    """Resolve the owner by email. `users` is not tenant-scoped, so this is the one non-tenant read."""
    with db.plain_tx() as conn:
        row = conn.execute("select id from users where email = %s", (email.lower(),)).fetchone()
    if row is None:
        raise SystemExit(f"no user with email {email}")
    return row[0]


def main(argv: list[str] | None = None) -> int:
    """Resume a run from the command line. Exits non-zero while anything is unfinished."""
    parser = argparse.ArgumentParser(description="Resume the queued evaluation jobs of one run.")
    parser.add_argument("--owner", required=True, help="the owner's email")
    parser.add_argument("--run", required=True, help="the run id")
    args = parser.parse_args(argv)

    db.open_pool()
    try:
        summary = process_run(_owner_id(args.owner), UUID(args.run))
    finally:
        db.close_pool()
    print(json.dumps({key: summary[key] for key in ("claimed", "done", "failed", "skipped")}))
    # Non-zero when a submission did not finish, including the retryable case: a script resuming a
    # batch wants to know the batch is not complete, and `skipped` is work the queue still owes.
    return 1 if summary["failed"] or summary["skipped"] else 0


if __name__ == "__main__":
    sys.exit(main())
