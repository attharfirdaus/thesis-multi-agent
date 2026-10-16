"""Runs: start an evaluation, drive its jobs, read the results (FR-06, FR-13).

Why `process` is a separate endpoint rather than a background daemon: the `jobs` table carries FORCE
ROW LEVEL SECURITY, so a worker that claims jobs across lecturers would need either a privileged role
or a SECURITY DEFINER function. Both were rejected in phase 2's design — the runtime role must stay
subject to the policies. The consequence is deliberate: a batch advances while its owner drives it,
which is exactly what a single-lecturer artefact needs, and it also means an interrupted run is resumed
by calling this endpoint again rather than by waiting for a daemon.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request, status
from psycopg.rows import dict_row

from app import db
from app.config import get_settings
from app.jobs.queue import enqueue_run
from app.jobs.worker import process_run
from app.routers.auth import CurrentUser
from app.schemas import (
    EvidenceOut,
    InFlightOut,
    RunOut,
    RunResultsOut,
    ScoreOut,
    SubmissionResultOut,
)
from app.security import require_csrf

router = APIRouter(tags=["runs"])


def _count(row: dict | None) -> int:
    """An aggregate `select count(*)` always returns a row; mypy cannot know that, and a missing row
    should read as zero rather than explode."""
    return int(row["n"]) if row else 0


def _run_out(cur, run_id: uuid.UUID, *, processed: int = 0, failed: int = 0) -> RunOut:
    """The run as the lecturer's screen reads it: status, job counts, what needs review, what is in flight.

    One builder for the three endpoints that return a run, so a field added here — `in_flight` was —
    cannot show up on one screen and be missing on another.
    """
    run = cur.execute("select id, status, mode from runs where id = %s", (run_id,)).fetchone()
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found.")
    counts = cur.execute(
        "select status, count(*) as n from jobs where run_id = %s group by status", (run_id,)
    ).fetchall()
    needs_review = _count(
        cur.execute(
            "select count(*) as n from submissions s join jobs j on j.submission_id = s.id "
            "where j.run_id = %s and jsonb_array_length(s.review_flags) > 0",
            (run_id,),
        ).fetchone()
    )
    in_flight = [
        InFlightOut(**row)
        for row in cur.execute(
            "select s.id as submission_id, s.pseudonym from jobs j "
            "join submissions s on s.id = j.submission_id "
            "where j.run_id = %s and j.status = 'running' order by s.pseudonym",
            (run_id,),
        ).fetchall()
    ]
    return RunOut(
        id=run["id"],
        status=run["status"],
        mode=run["mode"],
        jobs={row["status"]: row["n"] for row in counts},
        needs_review=needs_review,
        processed=processed,
        failed=failed,
        in_flight=in_flight,
    )


def _model_config() -> dict:
    """What FR-13 requires a run to remember. The API key is deliberately not part of it."""
    settings = get_settings()
    return {
        "base_url": settings.llm_base_url,
        "model": settings.llm_model,
        "temperature": settings.llm_temperature,
        "seed": settings.llm_seed,
        "max_attempts": settings.llm_max_attempts,
        # The timeout is not a scoring parameter, but it decides whether a call gets the chance to
        # score at all: a dimension that failed on three timeouts is only explicable if the run says
        # what the budget was (FR-13 asks for the parameters, and this one changed after 2026-10-16).
        "timeout_seconds": settings.llm_timeout_seconds,
        # Bounds the answer's length, and a truncated answer is a failed attempt rather than a score,
        # so a run cannot be reproduced without it.
        "max_tokens": settings.llm_max_tokens,
    }


@router.post("/assignments/{assignment_id}/runs", response_model=RunOut, status_code=status.HTTP_201_CREATED)
def create_run(
    assignment_id: uuid.UUID,
    request: Request,
    user: CurrentUser,
    mode: Annotated[str, Query(pattern="^(multi_agent|single_agent)$")] = "multi_agent",
    only_ungraded: Annotated[bool, Query()] = False,
) -> RunOut:
    """Snapshot the configuration and queue one job per submission (PRD §10 `Run`).

    `only_ungraded=true` queues only the submissions no run has scored yet, which is what a lecturer
    uploading a new batch wants: the ones already marked are left alone. The default stays "every
    submission" because PRD §11 measures run-to-run variance by scoring the same text repeatedly, so
    re-grading has to remain reachable — it is a choice, not an accident.
    """
    require_csrf(request)
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        assignment = cur.execute(
            "select rubric_version_id from assignments where id = %s", (assignment_id,)
        ).fetchone()
        if assignment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found.")
        rubric_version_id = assignment["rubric_version_id"]

        # Two plain queries rather than one with a conditional predicate: which submissions a run covers
        # is the thing the lecturer just chose, and it should be readable here.
        ungraded_only = (
            "select s.id from submissions s where s.assignment_id = %s "
            "and not exists (select 1 from system_scores sc where sc.submission_id = s.id) "
            "order by s.created_at"
        )
        every_submission = "select id from submissions where assignment_id = %s order by created_at"
        submissions = [
            row["id"]
            for row in cur.execute(
                ungraded_only if only_ungraded else every_submission, (assignment_id,)
            ).fetchall()
        ]
        if not submissions:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Every submission in this assignment has already been graded."
                if only_ungraded
                else "This assignment has no submissions to evaluate.",
            )

        prompt_versions = cur.execute(
            "select id from prompt_versions where owner_id = %s", (user.id,)
        ).fetchall()
        if not prompt_versions:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No prompt versions are seeded for this account; run scripts/seed_rubric.py first.",
            )

        created = cur.execute(
            "insert into runs (owner_id, assignment_id, mode, model_config, rubric_version_id, "
            "prompt_version_ids, status) values (%s, %s, %s, %s, %s, %s, 'queued') returning id",
            (
                user.id,
                assignment_id,
                mode,
                _psycopg_json(_model_config()),
                rubric_version_id,
                [row["id"] for row in prompt_versions],
            ),
        ).fetchone()
        if created is None:  # INSERT ... RETURNING always yields a row; this satisfies the type checker
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Run was not created."
            )
        run_id = created["id"]

        enqueue_run(conn, owner_id=user.id, run_id=run_id, submission_ids=submissions)

    return RunOut(id=run_id, status="queued", mode=mode, jobs={"queued": len(submissions)}, needs_review=0)


@router.post("/runs/{run_id}/process", response_model=RunOut)
def process_jobs(
    run_id: uuid.UUID,
    request: Request,
    user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=200)] = 10,
) -> RunOut:
    """Run up to `limit` queued jobs. The worker stores each result as its job finishes, so a pass that is
    interrupted — or cancelled — leaves exactly the submissions it completed, not an empty run."""
    require_csrf(request)
    summary = process_run(user.id, run_id, limit=limit)

    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        unfinished = _count(
            cur.execute(
                "select count(*) as n from jobs where run_id = %s and status in ('queued', 'running')",
                (run_id,),
            ).fetchone()
        )
        # A cancelled run stays cancelled: this pass may finish the submission it was already
        # grading, but it must not relabel the run as running again.
        cur.execute(
            "update runs set status = %s, finished_at = now() "
            "where id = %s and owner_id = %s and status <> 'cancelled'",
            ("running" if unfinished else "done", run_id, user.id),
        )
        return _run_out(
            cur, run_id, processed=summary.get("done", 0), failed=summary.get("failed", 0)
        )


@router.post("/runs/{run_id}/cancel", response_model=RunOut)
def cancel_run(run_id: uuid.UUID, request: Request, user: CurrentUser) -> RunOut:
    """Stop the queue: this run's queued jobs are cancelled and the run is marked cancelled.

    A submission already being graded is **not** stopped. The server-side request that holds it does not
    see the client go away, and interrupting it mid-call would leave a half-written submission; it
    finishes and stores its scores. The response says exactly that, with the counts and the submission
    still in flight, rather than implying a clean stop.
    """
    require_csrf(request)
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        run = cur.execute("select id, status from runs where id = %s", (run_id,)).fetchone()
        if run is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found.")
        if run["status"] in ("done", "failed", "cancelled"):
            # Cancelling a finished run would relabel a completed evaluation as a stopped one, and the
            # thesis reads that status to know what it is looking at.
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="This run has already finished."
            )
        cur.execute(
            "update jobs set status = 'cancelled', updated_at = now() "
            "where run_id = %s and owner_id = %s and status = 'queued'",
            (run_id, user.id),
        )
        # `finished_at` is when the queue stopped, which is the honest reading for a cancelled run even
        # when one submission is still being graded.
        cur.execute(
            "update runs set status = 'cancelled', finished_at = now() "
            "where id = %s and owner_id = %s",
            (run_id, user.id),
        )
        return _run_out(cur, run_id)


@router.get("/runs/{run_id}", response_model=RunOut)
def get_run(run_id: uuid.UUID, user: CurrentUser) -> RunOut:
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        return _run_out(cur, run_id)


@router.get("/runs/{run_id}/results", response_model=RunResultsOut)
def get_results(run_id: uuid.UUID, user: CurrentUser) -> RunResultsOut:
    """Every score with its evidence span and the synthesis feedback (FR-10, FR-14)."""
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        run = cur.execute(
            # The rubric row the run froze, for the readable name of each level code.
            "select r.id, r.status, rv.descriptors "
            "from runs r left join rubric_versions rv on rv.id = r.rubric_version_id "
            "where r.id = %s",
            (run_id,),
        ).fetchone()
        if run is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found.")

        rows = cur.execute(
            "select s.id as submission_id, s.pseudonym, s.review_flags, "
            "       sc.dimension, sc.indicator, sc.level, sc.rationale, sc.id as score_id, "
            "       e.quote, e.start_offset, e.end_offset, f.generated_text "
            "from submissions s "
            "join jobs j on j.submission_id = s.id and j.run_id = %s "
            "left join system_scores sc on sc.submission_id = s.id and sc.run_id = %s "
            "left join evidence e on e.system_score_id = sc.id "
            "left join feedback f on f.submission_id = s.id "
            "order by s.pseudonym, sc.dimension, sc.indicator",
            (run_id, run_id),
        ).fetchall()

    submissions: dict[uuid.UUID, SubmissionResultOut] = {}
    for row in rows:
        entry = submissions.setdefault(
            row["submission_id"],
            SubmissionResultOut(
                submission_id=row["submission_id"],
                pseudonym=row["pseudonym"],
                review_flags=list(row["review_flags"] or []),
                scores=[],
                feedback_text=row["generated_text"],
            ),
        )
        if row["dimension"] is None:
            continue
        score = next(
            (
                s
                for s in entry.scores
                if s.dimension == row["dimension"] and s.indicator == row["indicator"]
            ),
            None,
        )
        if score is None:
            score = ScoreOut(
                dimension=row["dimension"],
                indicator=row["indicator"],
                level=row["level"],
                rationale=row["rationale"],
                evidence=[],
            )
            entry.scores.append(score)
        if row["quote"] is not None:
            score.evidence.append(
                EvidenceOut(
                    quote=row["quote"],
                    start_offset=row["start_offset"],
                    end_offset=row["end_offset"],
                )
            )

    return RunResultsOut(
        run_id=run["id"],
        status=run["status"],
        submissions=list(submissions.values()),
        level_names=dict((run["descriptors"] or {}).get("levels") or {}),
    )


def _psycopg_json(value):
    from psycopg.types.json import Jsonb

    return Jsonb(value)
