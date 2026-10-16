"""Ingestion: batch upload (FR-03), listing, and the lecturer's boundary correction (FR-05).

The uploaded file is read into memory, extracted, segmented, redacted and then dropped. Nothing about
the original document is stored — no filename, no metadata, no raw text — because the file carries the
student's name where the extracted text does not have to. The only identifier that survives is the one
`app.ingest.identity_store` captures, deliberately, so the lecturer knows whose work they are
reviewing — held outside Neon, in a local encrypted file, never in this app's own tables.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app import db
from app.ingest.extract import extract, extract_zip
from app.ingest.identity import extract_identity
from app.ingest.identity_store import delete as delete_identity
from app.ingest.identity_store import read_many as read_identities
from app.ingest.identity_store import store as store_identity
from app.ingest.models import ExtractedDocument
from app.ingest.redact import redact
from app.ingest.segment import segment
from app.routers.auth import CurrentUser
from app.schemas import ImportedSubmission, ImportResult, SegmentationPatch, SubmissionOut
from app.security import require_csrf

router = APIRouter(tags=["ingest"])

# A class batch is small documents. The cap keeps a mis-selected file from occupying the worker.
MAX_FILE_BYTES = 20 * 1024 * 1024

# Interpolated into the three queries below. It is a module-level constant and never user input,
# which is why the SQL-injection lint is silenced at those call sites rather than here.
_SUBMISSION_COLUMNS = (
    "id, assignment_id, pseudonym, segmentation_status, import_warnings, "
    "coalesce(ai_output_text, '') as ai_output_text, coalesce(student_analysis_text, '') as analysis"
)


def _as_out(row: dict, real_name: str | None = None) -> SubmissionOut:
    return SubmissionOut(
        id=row["id"],
        assignment_id=row["assignment_id"],
        pseudonym=row["pseudonym"],
        real_name=real_name,
        segmentation_status=row["segmentation_status"],
        has_ai_output=bool(row["ai_output_text"].strip()),
        analysis_chars=len(row["analysis"]),
        import_warnings=list(row["import_warnings"] or []),
    )


def _store(cur, owner_id: uuid.UUID, assignment_id: uuid.UUID, doc: ExtractedDocument) -> ImportedSubmission:
    """Segment, redact and persist one extracted document."""
    result = segment(doc)
    ai = redact(result.ai_output_text)
    analysis = redact(result.student_analysis_text)

    warnings = [*doc.warnings, *result.warnings]
    if not analysis.text.strip() and not ai.text.strip():
        warnings.append("No extractable text was found in this file.")
    # The segmenter already reports the no-AI-output case (`segment.NO_AI_WARNING`) because it is the layer
    # that knows how the boundary was decided. The router used to append a second phrasing of the same fact,
    # which is why the lecturer's screen showed that sentence twice (seen live, 2026-10-16): one fact, one
    # warning.

    pseudonym = f"S-{uuid.uuid4().hex[:8]}"
    row = cur.execute(
        "insert into submissions (owner_id, assignment_id, pseudonym, ai_output_text, "
        "student_analysis_text, segmentation_status, import_warnings) "
        "values (%s, %s, %s, %s, %s, %s, %s) returning id",
        (
            owner_id,
            assignment_id,
            pseudonym,
            ai.text,
            analysis.text,
            "segmented" if analysis.text.strip() else "failed",
            Jsonb(warnings),
        ),
    ).fetchone()
    submission_id = row["id"]

    # The identity is captured from the pre-redaction document: the filename always carries the name
    # in this archive, and the labelled line carries it when the student filled the template in.
    # Held outside Neon (DECISIONS.md, 2026-10-16): `identity_store`, never this transaction, never a
    # table an agent's query could ever reach.
    real_identifier = extract_identity(doc.filename, doc.text)
    if real_identifier:
        store_identity(submission_id, owner_id, real_identifier)

    counts: dict[str, int] = {}
    for event in (*ai.events, *analysis.events):
        counts[event.cls.value] = counts.get(event.cls.value, 0) + event.count
    for cls, count in counts.items():
        cur.execute(
            "insert into redaction_events (owner_id, submission_id, cls, count) values (%s, %s, %s, %s)",
            (owner_id, submission_id, cls, count),
        )

    return ImportedSubmission(
        filename=doc.filename,
        status="imported",
        submission_id=submission_id,
        pseudonym=pseudonym,
        segmentation_method=result.method,
        has_ai_output=result.has_ai_output,
        removed_by_class=counts,
        warnings=warnings,
    )


@router.post(
    "/assignments/{assignment_id}/submissions",
    response_model=ImportResult,
    status_code=status.HTTP_201_CREATED,
)
def upload_submissions(
    assignment_id: uuid.UUID,
    request: Request,
    files: Annotated[list[UploadFile], File(description="PDF, DOCX, TXT or ZIP")],
    user: CurrentUser,
) -> ImportResult:
    require_csrf(request)
    imported: list[ImportedSubmission] = []

    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        exists = cur.execute("select 1 from assignments where id = %s", (assignment_id,)).fetchone()
        if exists is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found.")

        for upload in files:
            name = upload.filename or "unnamed"
            try:
                data = upload.file.read()
                if len(data) > MAX_FILE_BYTES:
                    raise ValueError(f"File is larger than {MAX_FILE_BYTES // (1024 * 1024)} MB.")

                if name.lower().endswith(".zip"):
                    documents, errors = extract_zip(name, data)
                    # Each message already names the offending member, so the zip's own name is
                    # enough in the filename field.
                    imported.extend(
                        ImportedSubmission(filename=name, status="failed", error=message)
                        for message in errors
                    )
                else:
                    documents = [extract(name, data)]

                for doc in documents:
                    imported.append(_store(cur, user.id, assignment_id, doc))
            except Exception as exc:  # one bad file must not fail the batch (FR-03)
                imported.append(ImportedSubmission(filename=name, status="failed", error=str(exc)))

    return ImportResult(assignment_id=assignment_id, files=imported)


@router.get("/assignments/{assignment_id}/submissions", response_model=list[SubmissionOut])
def list_submissions(assignment_id: uuid.UUID, user: CurrentUser) -> list[SubmissionOut]:
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        rows = cur.execute(
            f"select {_SUBMISSION_COLUMNS} from submissions where assignment_id = %s order by created_at",  # noqa: S608
            (assignment_id,),
        ).fetchall()
    names = read_identities((row["id"] for row in rows), user.id)
    return [_as_out(row, names.get(row["id"])) for row in rows]


@router.delete("/submissions/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_submission(submission_id: uuid.UUID, request: Request, user: CurrentUser) -> None:
    """Remove a submission and everything derived from it.

    One delete, not a cleanup dance: every dependent row — scores, their evidence, agent traces, feedback,
    queue entries, redaction counts and the pseudonym mapping — cascades from `submissions`, so a
    half-deleted submission cannot happen. That matters more here than elsewhere: the rows a lecturer cannot
    see any more are still rows about a student.

    Refused while a job for this submission is queued or running. The worker holds that submission's text
    and would try to store a result for a row that no longer exists, which fails the whole pass rather than
    the one submission, and the lecturer would have deleted something the app kept grading.
    """
    require_csrf(request)
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        row = cur.execute("select id from submissions where id = %s", (submission_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")
        busy = cur.execute(
            "select count(*) as n from jobs "
            "where submission_id = %s and status in ('queued', 'running')",
            (submission_id,),
        ).fetchone()
        if busy and busy["n"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This submission is still queued or being graded; stop the run first.",
            )
        cur.execute("delete from submissions where id = %s", (submission_id,))
        # Not a foreign-key cascade any more (DECISIONS.md, 2026-10-16): the identity now lives
        # outside Postgres, so deleting it is this router's job. Done inside the same transaction so
        # a failure here rolls the submission delete back too, rather than leaving the submission
        # gone from Postgres while its name still sits in the local store.
        delete_identity(submission_id)


@router.patch("/submissions/{submission_id}/segmentation", response_model=SubmissionOut)
def correct_segmentation(
    submission_id: uuid.UUID,
    payload: SegmentationPatch,
    request: Request,
    user: CurrentUser,
) -> SubmissionOut:
    """Move the boundary. `analysis_start` is an offset into the combined text
    (`ai_output_text` + newline + `student_analysis_text`): everything before it is AI output,
    everything after is the student's own analysis."""
    require_csrf(request)
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        row = cur.execute(
            f"select {_SUBMISSION_COLUMNS} from submissions where id = %s", (submission_id,)  # noqa: S608
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")

        combined = f"{row['ai_output_text']}\n{row['analysis']}" if row["ai_output_text"] else row["analysis"]
        if payload.analysis_start > len(combined):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"analysis_start is past the end of the document ({len(combined)} characters).",
            )
        ai_text = combined[: payload.analysis_start].strip()
        analysis_text = combined[payload.analysis_start :].strip()
        if not analysis_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="The student's analysis cannot be empty.",
            )

        updated = cur.execute(
            f"update submissions set ai_output_text = %s, student_analysis_text = %s, "  # noqa: S608
            f"segmentation_status = 'confirmed' where id = %s returning {_SUBMISSION_COLUMNS}",
            (ai_text, analysis_text, submission_id),
        ).fetchone()
        if updated is None:  # the row cannot vanish inside the transaction; satisfies the type checker
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")

    return _as_out(updated, read_identities([submission_id], user.id).get(submission_id))
