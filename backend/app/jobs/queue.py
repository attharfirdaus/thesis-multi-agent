"""The Postgres-backed queue for phase 4's evaluation jobs (PRD §8, FR-06).

A job is one submission inside one run. The table is the queue: no broker, no worker daemon, no
in-process task registry, because the artefact runs on one lecturer's machine and the batch it
carries is a class.

There is deliberately no cross-tenant claim. `jobs` has FORCE row-level security and the runtime
role is not the table owner, so a claim query can only see one owner's rows; and the two ways
around that were rejected — a BYPASSRLS role, or a SECURITY DEFINER claim function — because the
runtime role must stay subject to the tenant policies. That is the property phase 2 verified and
the reason nothing here opens a transaction of its own: every function takes a connection the
caller opened with `db.tenant_tx(owner_id)`, and the owner is passed explicitly as well so the
tenant being served is visible at the call site.

The consequence is intentional: a run progresses while its owner drives it — the API request that
started it, or `python -m app.jobs.worker` — and stops when nobody drives it. A queue is the right
shape for a single-lecturer local artefact; an always-on daemon able to claim for any owner is not.
"""

from collections.abc import Sequence
from uuid import UUID

from psycopg import Connection
from psycopg.rows import dict_row


def enqueue_run(conn: Connection, *, owner_id: UUID, run_id: UUID, submission_ids: Sequence[UUID]) -> int:
    """Queue one job per submission and return how many were queued.

    One statement over the whole batch: the batch is the unit the caller has in hand, and a
    per-submission insert loop would only be slower at the same count. Jobs start `queued` with
    zero attempts, so re-enqueueing a run that is already queued would duplicate its work — the
    retry path is `status`, not a second `enqueue_run` call (see `app.jobs.worker`).
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into jobs (owner_id, run_id, submission_id)
            select %s, %s, queued.submission_id from unnest(%s::uuid[]) as queued(submission_id)
            """,
            (owner_id, run_id, list(submission_ids)),
        )
        return cur.rowcount


def claim_jobs(conn: Connection, *, owner_id: UUID, limit: int) -> list[dict]:
    """Claim up to `limit` queued jobs of this owner, marking them `running`.

    Called with a `db.tenant_tx(owner_id)` connection; `owner_id` is repeated in the predicate so
    the query states which tenant it serves rather than relying on the policy alone.

    `FOR UPDATE SKIP LOCKED` is what makes a claim exclusive: a second claimant steps over the rows
    this transaction has locked instead of blocking on them or handing the same job out twice. The
    claim commits before the graph runs, because the graph takes seconds and a transaction must not
    be held open across provider calls; `running` is the lease for that interval, and
    `worker._requeue_stale` is what releases a lease whose holder died.

    `attempts` is not incremented here: an attempt is counted when it fails, so a process that
    crashes mid-submission does not spend one of the job's retries.
    """
    if limit < 1:
        return []
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            with claimed as (
                select id from jobs
                where owner_id = %s and status = 'queued'
                order by created_at
                limit %s
                for update skip locked
            )
            update jobs set status = 'running', updated_at = now()
            from claimed
            where jobs.id = claimed.id
            returning jobs.id, jobs.run_id, jobs.submission_id, jobs.attempts
            """,
            (owner_id, limit),
        )
        return cur.fetchall()
