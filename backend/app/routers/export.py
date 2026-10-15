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


@router.get("/runs/{run_id}/export.csv")
def export_csv(run_id: uuid.UUID, user: CurrentUser) -> Response:
    rows = _rows(run_id, user)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(COLUMNS)
    for row in rows:
        writer.writerow(_cells(row))
    # The BOM is what makes Excel read the Indonesian text as UTF-8 instead of the local code page.
    body = "\ufeff" + buffer.getvalue()
    return Response(
        content=body.encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="run-{run_id}-scores.csv"'},
    )


@router.get("/runs/{run_id}/export.xlsx")
def export_xlsx(run_id: uuid.UUID, user: CurrentUser) -> Response:
    rows = _rows(run_id, user)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Scores"
    sheet.append(COLUMNS)
    for row in rows:
        sheet.append(_cells(row))
    buffer = io.BytesIO()
    workbook.save(buffer)
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="run-{run_id}-scores.xlsx"'},
    )
