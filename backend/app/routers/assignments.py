"""Assignments: the dashboard list, creation, and the assignment detail the UI navigates into.

The list screen is the first thing a lecturer sees, and it shows a count and a run status per row. A
query per assignment would make that screen cost one round trip per row, so the counts and the newest
run are folded into the list query and the job counters into a second one for all of the runs at once.

No response here reads `student_identities.real_identifier`: the pseudonym is the only name the
lecturer UI receives (FR-04).
"""

import uuid

from fastapi import APIRouter, HTTPException, Request, status
from psycopg.rows import dict_row

from app import db
from app.routers.auth import CurrentUser
from app.schemas import (
    AssignmentCreate,
    AssignmentDetailOut,
    AssignmentSummaryOut,
    LatestRunOut,
    RunOut,
    SubmissionSummaryOut,
)
from app.security import require_csrf

router = APIRouter(tags=["assignments"])

# The newest run per assignment and the status counts of every job on the screen are read in two
# queries, never one per assignment: the dashboard lists them all at once.
def _jobs_by_run(cur, run_ids: list[uuid.UUID]) -> dict[uuid.UUID, dict[str, int]]:
    """`{run_id: {status: count}}` for every run on the screen, from one query."""
    if not run_ids:
        return {}
    counts: dict[uuid.UUID, dict[str, int]] = {}
    for row in cur.execute(
        "select run_id, status, count(*) as n from jobs where run_id = any(%s) group by run_id, status",
        (run_ids,),
    ).fetchall():
        counts.setdefault(row["run_id"], {})[row["status"]] = row["n"]
    return counts


def _summary(row: dict) -> SubmissionSummaryOut:
    return SubmissionSummaryOut(
        id=row["id"],
        assignment_id=row["assignment_id"],
        pseudonym=row["pseudonym"],
        segmentation_status=row["segmentation_status"],
        has_ai_output=bool(row["ai_output_text"].strip()),
        analysis_chars=len(row["student_analysis_text"]),
        import_warnings=list(row["import_warnings"] or []),
        review_flags=list(row["review_flags"] or []),
    )


@router.get("/assignments", response_model=list[AssignmentSummaryOut])
def list_assignments(user: CurrentUser) -> list[AssignmentSummaryOut]:
    """Newest first: the assignment the lecturer just made is the one they are working on."""
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        rows = cur.execute(
            "select a.id, a.title, a.course, a.prompt_text, a.created_at, "
            "       (select count(*) from submissions s where s.assignment_id = a.id) as submission_count, "
            "       latest.id as run_id, latest.status as run_status "
            "from assignments a "
            "left join lateral (select id, status from runs where assignment_id = a.id "
            "                   order by created_at desc limit 1) latest on true "
            "order by a.created_at desc"
        ).fetchall()
        jobs = _jobs_by_run(cur, [row["run_id"] for row in rows if row["run_id"] is not None])

    return [
        AssignmentSummaryOut(
            id=row["id"],
            title=row["title"],
            course=row["course"],
            prompt_text=row["prompt_text"],
            created_at=row["created_at"],
            submission_count=row["submission_count"],
            latest_run=None
            if row["run_id"] is None
            else LatestRunOut(
                id=row["run_id"], status=row["run_status"], jobs=jobs.get(row["run_id"], {})
            ),
        )
        for row in rows
    ]


@router.post("/assignments", response_model=AssignmentSummaryOut, status_code=status.HTTP_201_CREATED)
def create_assignment(
    payload: AssignmentCreate, request: Request, user: CurrentUser
) -> AssignmentSummaryOut:
    """FR-02. A new assignment is pinned to the owner's newest rubric version, as `RubricVersion` is
    immutable once a run has used it: the run that scores this assignment snapshots it from there."""
    require_csrf(request)
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        rubric = cur.execute(
            "select id from rubric_versions where owner_id = %s order by version desc limit 1",
            (user.id,),
        ).fetchone()
        if rubric is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No rubric version is seeded for this account; run scripts/seed_rubric.py first.",
            )
        created = cur.execute(
            "insert into assignments (owner_id, title, course, prompt_text, rubric_version_id) "
            "values (%s, %s, %s, %s, %s) returning id, title, course, prompt_text, created_at",
            (user.id, payload.title, payload.course, payload.prompt_text, rubric["id"]),
        ).fetchone()
        if created is None:  # INSERT ... RETURNING always yields a row; this satisfies the type checker
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Assignment was not created."
            )

    return AssignmentSummaryOut(**created, submission_count=0, latest_run=None)


@router.get("/assignments/{assignment_id}", response_model=AssignmentDetailOut)
def get_assignment(assignment_id: uuid.UUID, user: CurrentUser) -> AssignmentDetailOut:
    """One assignment with its submissions and its runs, both newest first (FR-09)."""
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        assignment = cur.execute(
            "select a.id, a.title, a.course, a.prompt_text, a.created_at, "
            "       (select count(*) from submissions s where s.assignment_id = a.id) as submission_count "
            "from assignments a where a.id = %s",
            (assignment_id,),
        ).fetchone()
        if assignment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found.")

        submissions = [
            _summary(row)
            for row in cur.execute(
                "select id, assignment_id, pseudonym, segmentation_status, import_warnings, "
                "       review_flags, coalesce(ai_output_text, '') as ai_output_text, "
                "       coalesce(student_analysis_text, '') as student_analysis_text "
                "from submissions where assignment_id = %s order by created_at desc",
                (assignment_id,),
            ).fetchall()
        ]
        runs = cur.execute(
            # A run needs review when one of its submissions carries a flag from the pipeline
            # (PRD §6). Counted inside the same query rather than one lookup per run.
            "select r.id, r.status, r.mode, "
            "       (select count(*) from submissions s join jobs j on j.submission_id = s.id "
            "        where j.run_id = r.id and jsonb_array_length(s.review_flags) > 0) as needs_review "
            "from runs r where r.assignment_id = %s order by r.created_at desc",
            (assignment_id,),
        ).fetchall()
        jobs = _jobs_by_run(cur, [run["id"] for run in runs])

    return AssignmentDetailOut(
        **assignment,
        submissions=submissions,
        latest_run=None
        if not runs
        else LatestRunOut(
            id=runs[0]["id"], status=runs[0]["status"], jobs=jobs.get(runs[0]["id"], {})
        ),
        runs=[
            RunOut(
                id=run["id"],
                status=run["status"],
                mode=run["mode"],
                jobs=jobs.get(run["id"], {}),
                needs_review=run["needs_review"],
            )
            for run in runs
        ],
    )
