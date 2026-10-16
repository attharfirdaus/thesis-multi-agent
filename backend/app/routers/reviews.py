"""The lecturer's reading and judging of one submission: its scores with their evidence (FR-10,
FR-14), the override that never touches the system score (FR-11), and the edited feedback (FR-19).

Every score shown comes from the *latest* run that scored this submission, not from any run: after a
re-run the detail view must show what the pipeline currently says, and an older run's scores are only
reachable through its own results endpoint.
"""

import uuid

from fastapi import APIRouter, HTTPException, Request, status
from psycopg.rows import dict_row

from app import db
from app.ingest.identity_store import read as read_identity
from app.routers.auth import CurrentUser
from app.schemas import (
    EvidenceOut,
    FeedbackOut,
    FeedbackPatch,
    ReviewIn,
    ReviewOut,
    RubricOut,
    RunRefOut,
    SubmissionDetailOut,
    SubmissionScoreOut,
)
from app.security import require_csrf

router = APIRouter(tags=["reviews"])


@router.get("/submissions/{submission_id}", response_model=SubmissionDetailOut)
def get_submission(submission_id: uuid.UUID, user: CurrentUser) -> SubmissionDetailOut:
    """The split view: the student's text, every score with its quote, and how the lecturer judged it.

    A submission that has never been scored is not an error — the lecturer opens it right after
    uploading, before any run exists — so the texts come back with `run`, `rubric` and `scores` empty.
    """
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        submission = cur.execute(
            "select id, assignment_id, pseudonym, segmentation_status, import_warnings, "
            "       review_flags, created_at, "
            "       coalesce(ai_output_text, '') as ai_output_text, "
            "       coalesce(student_analysis_text, '') as student_analysis_text "
            "from submissions where id = %s",
            (submission_id,),
        ).fetchone()
        if submission is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")

        run = cur.execute(
            "select r.id, r.status, r.mode, r.rubric_version_id from runs r "
            "where exists (select 1 from system_scores sc "
            "              where sc.run_id = r.id and sc.submission_id = %s) "
            "order by r.created_at desc limit 1",
            (submission_id,),
        ).fetchone()

        scores: list[SubmissionScoreOut] = []
        rubric = None
        reviews: list[ReviewOut] = []
        if run is not None:
            rubric_row = cur.execute(
                "select version, levels, indicators, descriptors "
                "from rubric_versions where id = %s",
                (run["rubric_version_id"],),
            ).fetchone()
            if rubric_row is not None:
                rubric = RubricOut(
                    version=str(rubric_row["version"]),
                    levels=list(rubric_row["levels"] or []),
                    indicators=list(rubric_row["indicators"] or []),
                    level_names=dict((rubric_row["descriptors"] or {}).get("levels") or {}),
                )

            by_id: dict[uuid.UUID, SubmissionScoreOut] = {}
            for row in cur.execute(
                "select sc.id, sc.dimension, sc.indicator, sc.level, sc.rationale, "
                "       e.quote, e.start_offset, e.end_offset "
                "from system_scores sc left join evidence e on e.system_score_id = sc.id "
                "where sc.run_id = %s and sc.submission_id = %s "
                "order by sc.dimension, sc.indicator, sc.id",
                (run["id"], submission_id),
            ).fetchall():
                score = by_id.get(row["id"])
                if score is None:
                    score = SubmissionScoreOut(
                        id=row["id"],
                        dimension=row["dimension"],
                        indicator=row["indicator"],
                        level=row["level"],
                        rationale=row["rationale"],
                    )
                    by_id[row["id"]] = score
                    scores.append(score)
                if row["quote"] is not None:  # a left join still yields one row for a scoreless span
                    score.evidence.append(
                        EvidenceOut(
                            quote=row["quote"],
                            start_offset=row["start_offset"],
                            end_offset=row["end_offset"],
                        )
                    )

            # The newest review per score. A lecturer who changes their mind records a second row —
            # FR-11 keeps the history — and only the latest one is the state of the score now.
            for row in cur.execute(
                "select distinct on (system_score_id) "
                "       system_score_id, action, new_level, reason, reviewed_at "
                "from lecturer_reviews where system_score_id = any(%s) "
                "order by system_score_id, reviewed_at desc",
                (list(by_id),),
            ).fetchall():
                reviews.append(ReviewOut(**row))

        feedback = cur.execute(
            "select generated_text, edited_text, edited_by, exported_at from feedback "
            "where submission_id = %s order by created_at desc limit 1",
            (submission_id,),
        ).fetchone()

    return SubmissionDetailOut(
        **submission,
        real_name=read_identity(submission_id, user.id),
        rubric=rubric,
        run=None
        if run is None
        else RunRefOut(id=run["id"], status=run["status"], mode=run["mode"]),
        scores=scores,
        feedback=None if feedback is None else FeedbackOut(**feedback),
        reviews=reviews,
    )


@router.post(
    "/system_scores/{score_id}/review", response_model=ReviewOut, status_code=status.HTTP_201_CREATED
)
def review_score(
    score_id: uuid.UUID, payload: ReviewIn, request: Request, user: CurrentUser
) -> ReviewOut:
    """FR-11. An override is its own row; `system_scores` is never updated, so the agreement study can
    compare the system's level with the lecturer's (PRD §10, §12)."""
    require_csrf(request)
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        score = cur.execute(
            "select sc.id, r.rubric_version_id from system_scores sc "
            "join runs r on r.id = sc.run_id where sc.id = %s",
            (score_id,),
        ).fetchone()
        if score is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Score not found.")

        new_level, reason = None, None
        if payload.action == "override":
            reason = (payload.reason or "").strip()
            if not payload.new_level or not reason:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="An override needs a new level and a reason.",
                )
            rubric = cur.execute(
                "select levels from rubric_versions where id = %s", (score["rubric_version_id"],)
            ).fetchone()
            # The level has to be one the run's own rubric offered. An override is the lecturer
            # disagreeing with the score, not with the scale.
            if rubric is None or payload.new_level not in list(rubric["levels"] or []):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="new_level must be one of the rubric's levels.",
                )
            new_level = payload.new_level

        created = cur.execute(
            "insert into lecturer_reviews (owner_id, system_score_id, action, new_level, reason) "
            "values (%s, %s, %s, %s, %s) "
            "returning system_score_id, action, new_level, reason, reviewed_at",
            (user.id, score_id, payload.action, new_level, reason),
        ).fetchone()
        if created is None:  # INSERT ... RETURNING always yields a row; this satisfies the type checker
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="The review was not saved."
            )

    return ReviewOut(**created)


@router.patch("/submissions/{submission_id}/feedback", response_model=FeedbackOut)
def edit_feedback(
    submission_id: uuid.UUID, payload: FeedbackPatch, request: Request, user: CurrentUser
) -> FeedbackOut:
    """FR-19. The edit is stored beside the generated text, never in place of it: both are exported."""
    require_csrf(request)
    # Blank means the lecturer emptied the box, which reads as "keep the generated text".
    edited_text = (payload.edited_text or "").strip() or None
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        updated = cur.execute(
            "update feedback set edited_text = %s, edited_by = %s where submission_id = %s "
            "returning generated_text, edited_text, edited_by, exported_at",
            (edited_text, user.id if edited_text else None, submission_id),
        ).fetchone()
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No feedback has been generated for this submission yet.",
            )

    return FeedbackOut(**updated)
