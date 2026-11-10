"""The lecturer's reading and judging of one submission: its scores with their evidence (FR-10,
FR-14), the override that never touches the system score (FR-11), and the edited feedback (FR-19).

Every score shown comes from the *latest* run that scored this submission, not from any run: after a
re-run the detail view must show what the pipeline currently says, and an older run's scores are only
reachable through its own results endpoint.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request, status
from psycopg.rows import dict_row

from app import db
from app.ingest.identity_store import read as read_identity
from app.routers.auth import CurrentUser
from app.schemas import (
    AcceptAllOut,
    CommentIn,
    CommentOut,
    EvidenceOut,
    ExclusionPatch,
    FeedbackOut,
    FeedbackPatch,
    ReviewIn,
    ReviewOut,
    RubricOut,
    RunRefOut,
    SegmentScoreOut,
    SubmissionDetailOut,
    SubmissionScoreOut,
    SynthesisOut,
    UnlocatedQuoteOut,
)
from app.security import require_csrf

router = APIRouter(tags=["reviews"])


@router.get("/submissions/{submission_id}", response_model=SubmissionDetailOut)
def get_submission(
    submission_id: uuid.UUID,
    user: CurrentUser,
    run_id: Annotated[uuid.UUID | None, Query(alias="run")] = None,
) -> SubmissionDetailOut:
    """The split view: the student's text, every score with its quote, and how the lecturer judged it.

    A submission that has never been scored is not an error — the lecturer opens it right after
    uploading, before any run exists — so the texts come back with `run`, `rubric` and `scores` empty.

    `run` names the run whose scores to show; without it the newest run that scored the submission is
    used. An earlier run's scores, and the reviews the lecturer attached to them, stay reachable this way
    after a re-grade.
    """
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        submission = cur.execute(
            "select id, assignment_id, pseudonym, segmentation_status, import_warnings, "
            "       review_flags, created_at, exclusion_reason, "
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
            "and (%s::uuid is null or r.id = %s) "
            "order by r.created_at desc, r.repetition_index desc limit 1",
            (submission_id, run_id, run_id),
        ).fetchone()
        synthesis = None
        unlocated: list[UnlocatedQuoteOut] = []

        scores: list[SubmissionScoreOut] = []
        segment_scores: list[SegmentScoreOut] = []
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
            by_segment_id: dict[uuid.UUID, SegmentScoreOut] = {}
            for row in cur.execute(
                "select sc.id, sc.dimension, sc.indicator, sc.level, sc.rationale, sc.distribution, "
                "       sc.segment_index, sc.segment_start, sc.segment_end, "
                "       e.quote, e.start_offset, e.end_offset "
                "from system_scores sc left join evidence e on e.system_score_id = sc.id "
                "where sc.run_id = %s and sc.submission_id = %s "
                "order by sc.segment_index nulls first, sc.dimension, sc.indicator, sc.id",
                (run["id"], submission_id),
            ).fetchall():
                # Text-level scores are what the lecturer judges; segment labels show what they rest on
                # (Bab III.6). Both carry their own evidence.
                score: SubmissionScoreOut | SegmentScoreOut | None
                if row["segment_index"] is None:
                    score = by_id.get(row["id"])
                    if score is None:
                        score = SubmissionScoreOut(
                            id=row["id"],
                            dimension=row["dimension"],
                            indicator=row["indicator"],
                            level=row["level"],
                            rationale=row["rationale"],
                            distribution=row["distribution"],
                        )
                        by_id[row["id"]] = score
                        scores.append(score)
                else:
                    score = by_segment_id.get(row["id"])
                    if score is None:
                        score = SegmentScoreOut(
                            id=row["id"],
                            segment_index=row["segment_index"],
                            segment_start=row["segment_start"],
                            segment_end=row["segment_end"],
                            dimension=row["dimension"],
                            indicator=row["indicator"],
                            level=row["level"],
                            rationale=row["rationale"],
                        )
                        by_segment_id[row["id"]] = score
                        segment_scores.append(score)
                if row["quote"] is not None:  # a left join still yields one row for a scoreless span
                    score.evidence.append(
                        EvidenceOut(
                            quote=row["quote"],
                            start_offset=row["start_offset"],
                            end_offset=row["end_offset"],
                        )
                    )

            # Text-level scores and segment labels alike carry the lecturer's comments and reviews (KF-09).
            commentable: dict[uuid.UUID, SubmissionScoreOut | SegmentScoreOut] = {**by_id, **by_segment_id}
            for row in cur.execute(
                "select id, system_score_id, body, created_at from score_comments "
                "where system_score_id = any(%s) order by created_at",
                (list(commentable),),
            ).fetchall():
                commentable[row["system_score_id"]].comments.append(CommentOut(**row))

            # The newest review per score. A lecturer who changes their mind records a second row —
            # FR-11 keeps the history — and only the latest one is the state of the score now.
            for row in cur.execute(
                "select distinct on (system_score_id) "
                "       system_score_id, action, new_level, reason, reviewed_at "
                "from lecturer_reviews where system_score_id = any(%s) "
                "order by system_score_id, reviewed_at desc",
                (list(commentable),),
            ).fetchall():
                reviews.append(ReviewOut(**row))

            # What the synthesis step wrote for the lecturer (FR-14): its explanation and every mismatch
            # it found between a rationale and its quote. The flag alone said "something does not match".
            # This run's own flags and unlocated quotes (0010); the submission row holds the newest run's.
            job = cur.execute(
                "select review_flags, unlocated_quotes from jobs "
                "where run_id = %s and submission_id = %s order by updated_at desc limit 1",
                (run["id"], submission_id),
            ).fetchone()
            if job is not None:
                submission["review_flags"] = job["review_flags"]
                unlocated = [UnlocatedQuoteOut(**item) for item in job["unlocated_quotes"] or []]
            trace = cur.execute(
                "select output_json from agent_traces where run_id = %s and submission_id = %s "
                "and agent_name = 'synthesis' and output_json is not null limit 1",
                (run["id"], submission_id),
            ).fetchone()
            if trace is not None:
                synthesis = SynthesisOut(
                    rationale=trace["output_json"].get("rationale") or "",
                    inconsistencies=list(trace["output_json"].get("inconsistencies") or []),
                )

        feedback = cur.execute(
            "select generated_text, edited_text, edited_by, exported_at from feedback "
            "where submission_id = %s and (run_id is null or %s::uuid is null or run_id = %s) "
            "order by created_at desc limit 1",
            (submission_id, run["id"] if run else None, run["id"] if run else None),
        ).fetchone()

    return SubmissionDetailOut(
        **submission,
        real_name=read_identity(submission_id, user.id),
        rubric=rubric,
        run=None
        if run is None
        else RunRefOut(id=run["id"], status=run["status"], mode=run["mode"]),
        scores=scores,
        segment_scores=segment_scores,
        synthesis=synthesis,
        unlocated_quotes=unlocated,
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
            "select sc.id, sc.dimension, r.rubric_version_id from system_scores sc "
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
            # The level has to be one the run's own scale offered. An override is the lecturer
            # disagreeing with the score, not with the scale: a Bloom level for the cognitive
            # dimension, presence or absence for a (nominal) metacognitive indicator.
            allowed = (
                list(rubric["levels"] or []) if rubric is not None else []
            ) if score["dimension"] == "cognitive" else ["present", "absent"]
            if payload.new_level not in allowed:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"new_level must be one of {allowed}.",
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


@router.post("/submissions/{submission_id}/accept-all", response_model=AcceptAllOut)
def accept_all(
    submission_id: uuid.UUID, request: Request, user: CurrentUser, run: uuid.UUID
) -> AcceptAllOut:
    """Accept every score of this run on this submission that has no review yet, in one statement.

    A submission carries five text-level scores and five per segment; accepting them one request at a
    time is hundreds of clicks. A score the lecturer already judged — accepted or overridden — is left
    exactly as it is.
    """
    require_csrf(request)
    with db.tenant_tx(user.id) as conn:
        accepted = conn.execute(
            "insert into lecturer_reviews (owner_id, system_score_id, action) "
            "select %s, sc.id, 'accept' from system_scores sc "
            "where sc.submission_id = %s and sc.run_id = %s "
            "and not exists (select 1 from lecturer_reviews lr where lr.system_score_id = sc.id)",
            (user.id, submission_id, run),
        ).rowcount
    return AcceptAllOut(accepted=accepted)


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


@router.post(
    "/system_scores/{score_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED
)
def comment_score(
    score_id: uuid.UUID, payload: CommentIn, request: Request, user: CurrentUser
) -> CommentOut:
    """KF-08: a lecturer's comment on a score. It judges nothing, so it never changes the score's
    review state and is stored apart from `lecturer_reviews`."""
    require_csrf(request)
    body = payload.body.strip()
    if not body:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="A comment cannot be empty."
        )
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        if cur.execute("select 1 from system_scores where id = %s", (score_id,)).fetchone() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Score not found.")
        created = cur.execute(
            "insert into score_comments (owner_id, system_score_id, body) values (%s, %s, %s) "
            "returning id, system_score_id, body, created_at",
            (user.id, score_id, body),
        ).fetchone()
    if created is None:  # INSERT ... RETURNING always yields a row; this satisfies the type checker
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not saved.")
    return CommentOut(**created)


@router.patch("/submissions/{submission_id}/exclusion", response_model=ExclusionPatch)
def set_exclusion(
    submission_id: uuid.UUID, payload: ExclusionPatch, request: Request, user: CurrentUser
) -> ExclusionPatch:
    """Tabel III.4: mark a submission as outside the evaluation set, with the reason, or put it back.
    The submission is still evaluated in the app; the research export carries the flag."""
    require_csrf(request)
    with db.tenant_tx(user.id) as conn:
        updated = conn.execute(
            "update submissions set exclusion_reason = %s where id = %s returning exclusion_reason",
            (payload.reason, submission_id),
        ).fetchone()
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")
    return ExclusionPatch(reason=updated[0])
