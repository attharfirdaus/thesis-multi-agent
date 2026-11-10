"""Ingestion: batch upload (FR-03), listing, and the lecturer's boundary correction (FR-05).

The uploaded file is read into memory, extracted, segmented, redacted and then dropped. Nothing about
the original document is stored — no filename, no metadata, no raw text — because the file carries the
student's name where the extracted text does not have to. The only identifier that survives is the one
`app.ingest.identity_store` captures, deliberately, so the lecturer knows whose work they are
reviewing — held outside Neon, in a local encrypted file, never in this app's own tables.

Segmenting and redacting (`_prepare`) are kept apart from inserting rows (`_persist`), and
`upload_submissions` runs every file's `_prepare` before opening the transaction that runs every
file's `_persist`. The reason is the LLM segmentation fallback (`app.ingest.llm_segment`, tried when
the rule-based segmenter finds no label): a provider call can take several seconds, and a Postgres
transaction held open for that long, once per file in a batch, is a connection-pool and lock-
contention risk the free-tier database does not need. Identity capture, redaction-event counting and
the actual insert touch nothing external, so they stay in `_persist`, inside the transaction, as fast
as they always were.
"""

import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app import db
from app.agents.segments import split_segments, stored
from app.ingest.extract import extract, extract_zip
from app.ingest.identity import extract_identity
from app.ingest.identity_store import delete as delete_identity
from app.ingest.identity_store import read_many as read_identities
from app.ingest.identity_store import store as store_identity
from app.ingest.llm_segment import llm_segment
from app.ingest.models import ExtractedDocument, RedactionEvent
from app.ingest.redact import redact
from app.ingest.segment import segment
from app.llm.client import ProviderClient
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


# A label line of the identity block the assignment template opens with ("Nama : …", "NIM : …").
_IDENTITY_LINE = re.compile(
    r"^\s*(?:nama|nim|nip|kelas|prodi|program studi|mata kuliah)\b[^\n:|]*[:|]", re.IGNORECASE
)

DUPLICATE = "This file duplicates a submission already in this assignment."
NO_ANALYSIS = "No analysis text could be read from this file."


def strip_header(text: str) -> str:
    """The analysis without the document header above it: the title line and the identity block.

    The header is not analysis, but it was stored as the start of the first sentence, and on both real
    submissions graded on 2026-11-10 an agent took "Tugas 1: Analisis COSO" as evidence that the student
    refers to the task requirements (`orientasi`). Only the first lines are looked at, and only when an
    identity label is among them, so a document without the block is returned untouched.
    """
    lines = text.split("\n")
    identity = [i for i, line in enumerate(lines[:8]) if _IDENTITY_LINE.match(line)]
    if not identity:
        return text
    # What stands above the block goes with it only when it reads as a title: one or two short lines
    # that are not sentences. Prose above the block is the student's and stays.
    above = lines[: identity[0]]
    titled = len(above) <= 2 and all(len(line) <= 100 and not line.rstrip().endswith(".") for line in above)
    kept = [
        line
        for i, line in enumerate(lines)
        if i not in identity and not (titled and i < identity[0])
    ]
    return "\n".join(kept).lstrip() or text


def drop_checkpoints(cur, thread_pattern: str) -> None:
    """Remove LangGraph checkpoints whose thread (`run:submission`) matches. They are LangGraph's
    tables, outside the foreign keys, and a checkpoint left by an interrupted job holds the
    submission's text: deleting the submission has to reach it."""
    for table in ("checkpoint_writes", "checkpoint_blobs", "checkpoints"):
        cur.execute(f"delete from {table} where thread_id like %s", (thread_pattern,))  # noqa: S608


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


@dataclass
class _Prepared:
    """One extracted document, already segmented and redacted — everything `_persist` needs, with
    nothing left in it that an external call has not already finished with."""

    doc: ExtractedDocument
    ai_text: str
    analysis_text: str
    method: str
    has_ai_output: bool
    warnings: list[str] = field(default_factory=list)
    redaction_counts: dict[str, int] = field(default_factory=dict)


def _prepare(doc: ExtractedDocument, client: ProviderClient | None = None) -> _Prepared:
    """Segment and redact one extracted document. No database access: a slow LLM call here must
    never hold the batch's Postgres transaction open (see the module docstring)."""
    result = segment(doc)
    llm_events: list[RedactionEvent] = []

    if result.method != "label":
        # Rule-based segmentation found no label — every student retypes the assignment template
        # differently, so this is the normal case, not a failure (DECISIONS.md, 2026-10-17). Redact
        # the whole document before the LLM ever sees it (PRD §4): the provider client re-checks the
        # payload again on the way out, but that is the second gate, not the only one.
        whole = redact(doc.text)
        llm_result = llm_segment(whole.text, client)
        if llm_result is not None:
            result = llm_result
            llm_events = whole.events  # the one real redaction pass behind this submission's text

    if result.method == "llm":
        ai_text, analysis_text = result.ai_output_text, result.student_analysis_text
        events = llm_events
    else:
        # Label, or the LLM path was unavailable or untrustworthy and the rule-based guess stands:
        # either way this text has never been redacted yet.
        ai = redact(result.ai_output_text)
        analysis = redact(result.student_analysis_text)
        ai_text, analysis_text = ai.text, analysis.text
        events = [*ai.events, *analysis.events]

    analysis_text = strip_header(analysis_text)
    warnings = [*doc.warnings, *result.warnings]
    if not analysis_text.strip() and not ai_text.strip():
        warnings.append("No extractable text was found in this file.")
    # The segmenter already reports the no-AI-output case (`segment.NO_AI_WARNING`) because it is the layer
    # that knows how the boundary was decided. The router used to append a second phrasing of the same fact,
    # which is why the lecturer's screen showed that sentence twice (seen live, 2026-10-16): one fact, one
    # warning.

    counts: dict[str, int] = {}
    for event in events:
        counts[event.cls.value] = counts.get(event.cls.value, 0) + event.count

    return _Prepared(
        doc=doc,
        ai_text=ai_text,
        analysis_text=analysis_text,
        method=result.method,
        has_ai_output=bool(ai_text.strip()),
        warnings=warnings,
        redaction_counts=counts,
    )


def _persist(cur, owner_id: uuid.UUID, assignment_id: uuid.UUID, prepared: _Prepared) -> ImportedSubmission:
    """The database-only half: given an already segmented-and-redacted document, insert its rows."""
    # Both refusals report the file as failed instead of storing a row nobody can grade: an empty one
    # was queued by every run and failed each time, and a second copy was graded and exported twice.
    if not prepared.analysis_text.strip():
        raise ValueError(NO_ANALYSIS)
    if cur.execute(
        "select 1 from submissions where assignment_id = %s and student_analysis_text = %s "
        "and coalesce(ai_output_text, '') = %s limit 1",
        (assignment_id, prepared.analysis_text, prepared.ai_text),
    ).fetchone():
        raise ValueError(DUPLICATE)
    pseudonym = f"S-{uuid.uuid4().hex[:8]}"
    row = cur.execute(
        "insert into submissions (owner_id, assignment_id, pseudonym, ai_output_text, "
        "student_analysis_text, segmentation_status, import_warnings, analysis_segments) "
        "values (%s, %s, %s, %s, %s, %s, %s, %s) returning id",
        (
            owner_id,
            assignment_id,
            pseudonym,
            prepared.ai_text,
            prepared.analysis_text,
            "segmented" if prepared.analysis_text.strip() else "failed",
            Jsonb(prepared.warnings),
            # KF-05: the assessed segments are stored at import, before any measurement starts.
            Jsonb(stored(split_segments(prepared.analysis_text))),
        ),
    ).fetchone()
    submission_id = row["id"]

    # The identity is captured from the pre-redaction document: the filename always carries the name
    # in this archive, and the labelled line carries it when the student filled the template in.
    # Held outside Neon (DECISIONS.md, 2026-10-16): `identity_store`, never this transaction, never a
    # table an agent's query could ever reach.
    real_identifier = extract_identity(prepared.doc.filename, prepared.doc.text)
    if real_identifier:
        store_identity(submission_id, owner_id, real_identifier)

    for cls, count in prepared.redaction_counts.items():
        cur.execute(
            "insert into redaction_events (owner_id, submission_id, cls, count) values (%s, %s, %s, %s)",
            (owner_id, submission_id, cls, count),
        )

    return ImportedSubmission(
        filename=prepared.doc.filename,
        status="imported",
        submission_id=submission_id,
        pseudonym=pseudonym,
        segmentation_method=prepared.method,
        has_ai_output=prepared.has_ai_output,
        removed_by_class=prepared.redaction_counts,
        warnings=prepared.warnings,
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

    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        exists = cur.execute("select 1 from assignments where id = %s", (assignment_id,)).fetchone()
    if exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found.")

    imported: list[ImportedSubmission] = []
    extracted: list[ExtractedDocument] = []
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

            extracted.extend(documents)
        except Exception as exc:  # one bad file must not fail the batch (FR-03)
            imported.append(ImportedSubmission(filename=name, status="failed", error=str(exc)))

    # Side by side: a file without a label costs one provider call of several seconds, and a class
    # batch of them in sequence kept the upload request open for minutes.
    def prepare(doc: ExtractedDocument) -> _Prepared | ImportedSubmission:
        try:
            return _prepare(doc)
        except Exception as exc:  # one bad file must not fail the batch (FR-03)
            return ImportedSubmission(filename=doc.filename, status="failed", error=str(exc))

    prepared: list[_Prepared] = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for outcome in pool.map(prepare, extracted):
            if isinstance(outcome, _Prepared):
                prepared.append(outcome)
            else:
                imported.append(outcome)

    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        for item in prepared:
            try:
                imported.append(_persist(cur, user.id, assignment_id, item))
            except Exception as exc:  # one bad file must not fail the batch (FR-03)
                imported.append(
                    ImportedSubmission(filename=item.doc.filename, status="failed", error=str(exc))
                )

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
        drop_checkpoints(cur, f"%:{submission_id}")
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

        busy = cur.execute(
            "select 1 from jobs where submission_id = %s and status in ('queued', 'running') limit 1",
            (submission_id,),
        ).fetchone()
        if busy:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This submission is still queued or being graded; stop the run first.",
            )
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
            f"analysis_segments = %s, segmentation_status = 'confirmed' "
            f"where id = %s returning {_SUBMISSION_COLUMNS}",
            # A moved boundary changes the analysis, so its stored segments are re-split with it (KF-05).
            (ai_text, analysis_text, Jsonb(stored(split_segments(analysis_text))), submission_id),
        ).fetchone()
        if updated is None:  # the row cannot vanish inside the transaction; satisfies the type checker
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")
        # Every stored score points into the text that just changed: its segments, its quotes and
        # their offsets. Left in place they highlighted unrelated words (seen 2026-11-10), so they go,
        # with their evidence, reviews and comments, and the submission reads as not yet graded.
        cur.execute("delete from system_scores where submission_id = %s", (submission_id,))
        cur.execute("delete from feedback where submission_id = %s", (submission_id,))
        cur.execute("update submissions set review_flags = '[]'::jsonb where id = %s", (submission_id,))

    return _as_out(updated, read_identities([submission_id], user.id).get(submission_id))
