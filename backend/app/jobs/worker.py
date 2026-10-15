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
from contextlib import contextmanager
from uuid import UUID

from psycopg.rows import dict_row

from app import db
from app.agents.graph import evaluate_submission
from app.agents.models import GraphState
from app.config import get_settings
from app.jobs.queue import claim_jobs

# A submission that fails this many times is not retried: the model or the prompt is wrong, not the
# network, and the lecturer should see the job in the failed list rather than wait on it.
MAX_ATTEMPTS = 3

# Jobs claimed per pass. The graph call takes seconds and no transaction is held across it, so this
# bounds only how much of a large batch one call picks up.
BATCH = 25


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
                   runs.prompt_version_ids,
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
        cur.execute(
            "select template from prompt_versions where id = any(%s) and agent_name = 'calibration'",
            (row["prompt_version_ids"],),
        )
        calibration = cur.fetchone()
        # The stored row is a JSON *object* (`{"examples": [...], "interim": true}`) because the seed
        # script records those flags, while the prompt builders want the example list itself. The
        # translation belongs here, so neither side has to know the other's shape. An empty list is
        # passed through rather than filled in: the builders refuse an uncalibrated agent (PRD §6),
        # and that refusal is the failure this job should show.
        parsed = json.loads(calibration["template"]) if calibration else []
        examples = parsed.get("examples", []) if isinstance(parsed, dict) else parsed
        prompts: dict = {"calibration": examples}
    return GraphState(
        owner_id=str(owner_id),
        run_id=str(run_id),
        submission_id=str(submission_id),
        rubric={
            # The prompt states which rubric version produced the score, so a thesis claim about a
            # past run can be traced to the rubric that was in force (PRD §11).
            "version": row["rubric_version"],
            **{key: row[key] for key in ("dimensions", "levels", "indicators", "descriptors")},
        },
        prompts=prompts,
        student_analysis_text=row["student_analysis_text"] or "",
        ai_output_text=row["ai_output_text"] or "",
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


def _mark_done(owner_id: UUID, job_id: UUID) -> None:
    with db.tenant_tx(owner_id) as conn, conn.cursor() as cur:
        cur.execute(
            "update jobs set status = 'done', updated_at = now() where id = %s and owner_id = %s",
            (job_id, owner_id),
        )


@contextmanager
def _checkpointer():
    """A LangGraph saver for the duration of one batch pass (PRD §6).

    One connection for the whole pass rather than one per submission: the saver writes on every node
    transition, so a connection per submission would add a connect to each of the two dozen jobs a pass
    can claim. Missing checkpoint tables are a loud failure — `scripts/setup_checkpointer.py` is part of
    setting up a database, and silently running without checkpointing would hide that.
    """
    from langgraph.checkpoint.postgres import PostgresSaver

    with PostgresSaver.from_conn_string(get_settings().database_url) as saver:
        yield saver


def _run_one(owner_id: UUID, job: dict, summary: dict, checkpointer=None) -> None:
    """Run one claimed job and record its outcome against the summary it is part of."""
    try:
        with db.tenant_tx(owner_id) as conn:
            state = _load_state(
                conn, owner_id=owner_id, run_id=job["run_id"], submission_id=job["submission_id"]
            )
        # Outside tenant context on purpose: the graph calls a provider and can take seconds, and
        # holding a transaction across that would pin a pooled connection for the whole batch.
        result = evaluate_submission(state, checkpointer=checkpointer)
    except Exception as error:  # noqa: BLE001 — a failed submission must never fail the batch
        summary["failed" if _record_failure(owner_id, job, error) else "skipped"] += 1
        return

    # A graph that produced nothing has not evaluated anything. Without this guard the job would be
    # marked done and the submission would look evaluated while carrying zero scores — which is how a
    # KeyError inside a prompt builder stayed invisible for a whole test run.
    if not any(result.get(agent) for agent in ("cognitive", "metacognitive", "synthesis")):
        failure = RuntimeError("no agent produced output: " + "; ".join(result.get("errors", [])))
        summary["failed" if _record_failure(owner_id, job, failure) else "skipped"] += 1
        return

    _mark_done(owner_id, job["id"])
    summary["done"] += 1
    summary["states"].append(result)


def process_run(owner_id: UUID, run_id: UUID, limit: int | None = None) -> dict:
    """Claim this run's queued jobs once each, run them, and summarise what happened.

    `limit` caps how many jobs this call takes; `None` takes one full batch. Nothing loops until
    the queue is empty: a job that fails is put back with its attempt recorded, and a submission
    that needs three attempts therefore needs three passes, so an offline provider cannot burn a
    whole batch's retries in one call.

    Returns `claimed`, `done`, `failed` (out of retries), `skipped` (failed, will be retried) and
    `states`, the final `GraphState` of each finished submission for the caller to persist. The
    first three plus `skipped` always add up to `claimed`.
    """
    summary: dict = {"claimed": 0, "done": 0, "failed": 0, "skipped": 0, "states": []}
    with db.tenant_tx(owner_id) as conn:
        _requeue_stale(conn, owner_id=owner_id, run_id=run_id)
        jobs = claim_jobs(conn, owner_id=owner_id, limit=BATCH if limit is None else limit)
    summary["claimed"] = len(jobs)
    with _checkpointer() as saver:
        for job in jobs:
            _run_one(owner_id, job, summary, checkpointer=saver)
    return summary


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
