"""Export one run's scores as CSV or XLSX (FR-12, FR-16).

The shape is one row per evidence span, not per score: a thesis claim about a score is made of the
passages behind it, and a spreadsheet cell cannot hold two spans. A score whose quote failed the
evidence check keeps its row with the offsets empty rather than disappearing from the export, so the
counts still add up when the file is joined offline with the manual ratings.

The CSV is written with a BOM because the quotes and rationales are Indonesian and Excel on Windows
otherwise reads them as mojibake.
"""

import csv
import io
import uuid

from fastapi import APIRouter, HTTPException, Response, status
from openpyxl import Workbook
from psycopg.rows import dict_row

from app import db
from app.routers.auth import CurrentUser
from app.schemas import UserOut

router = APIRouter(tags=["export"])

# The research dataset's column order. Frozen: the analysis notebook reads these by position.
COLUMNS = [
    "assignment_title",
    "submission_pseudonym",
    "dimension",
    "indicator",
    "level",
    "rationale",
    "evidence_quote",
    "start_offset",
    "end_offset",
    "review_action",
    "review_new_level",
    "review_reason",
    "reviewed_at",
    "feedback_text",
    "run_id",
    "mode",
    "model",
    "temperature",
    "seed",
    "rubric_version",
    "started_at",
    "finished_at",
]

# One row per score per span, with the lecturer's newest review and the feedback the export must
# carry. `model`, `temperature`, `seed` and `rubric_version` come from the run's own snapshot, never
# from the current settings: an old run has to export as it ran (FR-13, PRD §11).
_EXPORT_SQL = """
select a.title as assignment_title,
       s.pseudonym,
       sc.dimension, sc.indicator, sc.level, sc.rationale,
       e.quote as evidence_quote, e.start_offset, e.end_offset,
       lr.action as review_action, lr.new_level as review_new_level,
       lr.reason as review_reason, lr.reviewed_at,
       coalesce(f.edited_text, f.generated_text) as feedback_text,
       r.id as run_id, r.mode, r.model_config, r.started_at, r.finished_at,
       rv.version as rubric_version
from system_scores sc
join runs r on r.id = sc.run_id
join submissions s on s.id = sc.submission_id
join assignments a on a.id = r.assignment_id
left join rubric_versions rv on rv.id = r.rubric_version_id
left join evidence e on e.system_score_id = sc.id
left join feedback f on f.submission_id = sc.submission_id
left join lateral (
    select action, new_level, reason, reviewed_at from lecturer_reviews
    where system_score_id = sc.id
    order by reviewed_at desc, id desc limit 1
) lr on true
where sc.run_id = %s
order by s.pseudonym, sc.dimension, sc.indicator, e.start_offset
"""


def _stamp(value) -> str | None:
    return None if value is None else value.isoformat()


def _cells(row: dict) -> list:
    """One export row, in `COLUMNS` order. `None` becomes an empty cell in both formats."""
    config = row["model_config"] or {}
    return [
        row["assignment_title"],
        row["pseudonym"],
        row["dimension"],
        row["indicator"],
        row["level"],
        row["rationale"],
        row["evidence_quote"],
        row["start_offset"],
        row["end_offset"],
        row["review_action"],
        row["review_new_level"],
        row["review_reason"],
        _stamp(row["reviewed_at"]),
        row["feedback_text"],
        str(row["run_id"]),
        row["mode"],
        config.get("model"),
        config.get("temperature"),
        config.get("seed"),
        row["rubric_version"],
        _stamp(row["started_at"]),
        _stamp(row["finished_at"]),
    ]


def _rows(run_id: uuid.UUID, user: UserOut) -> list[dict]:
    """The run's export rows, or 404 when it is not this lecturer's."""
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        run = cur.execute("select id from runs where id = %s", (run_id,)).fetchone()
        if run is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found.")
        return cur.execute(_EXPORT_SQL, (run_id,)).fetchall()


def _csv_response(columns: list[str], rows: list[list], filename: str) -> Response:
    """CSV with the BOM: it is what makes Excel read Indonesian text as UTF-8, not the local code page."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(columns)
    for row in rows:
        writer.writerow(row)
    return Response(
        content=("\ufeff" + buffer.getvalue()).encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _xlsx_response(
    columns: list[str], rows: list[list], filename: str, sheet_title: str = "Scores"
) -> Response:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_title
    sheet.append(columns)
    for row in rows:
        sheet.append(row)
    buffer = io.BytesIO()
    workbook.save(buffer)
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/runs/{run_id}/export.csv")
def export_csv(run_id: uuid.UUID, user: CurrentUser) -> Response:
    """FR-12: this run's scores, for the lecturer's own review."""
    rows = _rows(run_id, user)
    return _csv_response(COLUMNS, [_cells(row) for row in rows], f"run-{run_id}-scores.csv")


@router.get("/runs/{run_id}/export.xlsx")
def export_xlsx(run_id: uuid.UUID, user: CurrentUser) -> Response:
    """FR-12, same rows as the CSV."""
    rows = _rows(run_id, user)
    return _xlsx_response(COLUMNS, [_cells(row) for row in rows], f"run-{run_id}-scores.xlsx")


# --------------------------------------------------------------------------- research dataset (FR-16)

#: One row per score, across every run of an assignment that produced any, with `mode` and the run's status
#: as columns. The thesis joins this offline with the two-lecturer rating sheet on
#: (submission_pseudonym, dimension, indicator) and pivots by `mode`; that is why it is per assignment rather
#: than per run, and why nothing here is renamed into display vocabulary.
RESEARCH_COLUMNS = [
    "assignment_title",
    "assignment_course",
    "submission_pseudonym",
    "mode",
    "dimension",
    "indicator",
    "system_level",
    "rationale",
    "evidence_quote",
    "start_offset",
    "end_offset",
    "review_action",
    "review_new_level",
    "review_reason",
    "reviewed_at",
    "feedback_text",
    "run_id",
    "run_status",
    "model",
    "temperature",
    "seed",
    "max_tokens",
    "rubric_version",
    "started_at",
    "finished_at",
]

_RESEARCH_SQL = """
select a.title as assignment_title,
       a.course as assignment_course,
       s.pseudonym as submission_pseudonym,
       r.id as run_id, r.mode, r.status as run_status, r.model_config, r.started_at, r.finished_at,
       rv.version as rubric_version,
       sc.dimension, sc.indicator, sc.level as system_level, sc.rationale,
       e.quote as evidence_quote, e.start_offset, e.end_offset,
       lr.action as review_action, lr.new_level as review_new_level, lr.reason as review_reason,
       lr.reviewed_at,
       at.output_json ->> 'feedback_text' as feedback_text
from assignments a
join runs r on r.assignment_id = a.id
join rubric_versions rv on rv.id = r.rubric_version_id
join jobs j on j.run_id = r.id
join submissions s on s.id = j.submission_id
join system_scores sc on sc.run_id = r.id and sc.submission_id = s.id
left join evidence e on e.system_score_id = sc.id
left join agent_traces at on at.run_id = r.id and at.submission_id = s.id and at.agent_name = 'synthesis'
left join lateral (
    select action, new_level, reason, reviewed_at from lecturer_reviews
    where system_score_id = sc.id order by reviewed_at desc limit 1
) lr on true
where a.id = %s
order by s.pseudonym, r.mode, sc.dimension, sc.indicator
"""


def _research_rows(assignment_id: uuid.UUID, user: UserOut) -> list[dict]:
    """The assignment's research rows, or 404 when it is not this lecturer's.

    Inner joins all the way to `system_scores` on purpose: a run that produced no scores contributes nothing
    to a dataset about scores, and its absence is visible in the app rather than as blank rows here.
    """
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        assignment = cur.execute("select id from assignments where id = %s", (assignment_id,)).fetchone()
        if assignment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found.")
        return cur.execute(_RESEARCH_SQL, (assignment_id,)).fetchall()


def _research_cells(row: dict) -> list:
    """One research row, in `RESEARCH_COLUMNS` order."""
    config = row["model_config"] or {}
    return [
        row["assignment_title"],
        row["assignment_course"],
        row["submission_pseudonym"],
        row["mode"],
        row["dimension"],
        row["indicator"],
        row["system_level"],
        row["rationale"],
        row["evidence_quote"],
        row["start_offset"],
        row["end_offset"],
        row["review_action"],
        row["review_new_level"],
        row["review_reason"],
        _stamp(row["reviewed_at"]),
        row["feedback_text"],
        str(row["run_id"]),
        row["run_status"],
        config.get("model"),
        config.get("temperature"),
        config.get("seed"),
        config.get("max_tokens"),
        row["rubric_version"],
        _stamp(row["started_at"]),
        _stamp(row["finished_at"]),
    ]


@router.get("/assignments/{assignment_id}/research-export.csv")
def research_export_csv(assignment_id: uuid.UUID, user: CurrentUser) -> Response:
    """FR-16: the dataset the thesis joins with the manually collected rating sheet."""
    rows = _research_rows(assignment_id, user)
    return _csv_response(
        RESEARCH_COLUMNS,
        [_research_cells(row) for row in rows],
        f"assignment-{assignment_id}-research.csv",
    )


@router.get("/assignments/{assignment_id}/research-export.xlsx")
def research_export_xlsx(assignment_id: uuid.UUID, user: CurrentUser) -> Response:
    """FR-16, same rows as the CSV, one sheet named `Scores`."""
    rows = _research_rows(assignment_id, user)
    return _xlsx_response(
        RESEARCH_COLUMNS,
        [_research_cells(row) for row in rows],
        f"assignment-{assignment_id}-research.xlsx",
        sheet_title="Scores",
    )
