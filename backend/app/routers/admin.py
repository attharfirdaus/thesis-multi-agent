"""The admin area of Bab III.3: users, rubric versions, prompt versions and model configuration, and the
run log. Technical vocabulary (agent, prompt) is allowed here and nowhere else in the UI.

Rubric and prompt versions are per owner (tenant-scoped), so the admin edits the rubric their own runs
use. Users are not tenant-scoped, which is why listing them is gated on the role and not on RLS.
"""

import uuid

from fastapi import APIRouter, HTTPException, Request, status
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app import db
from app.routers.auth import CurrentUser
from app.routers.runs import _model_config
from app.schemas import (
    AdminConfigOut,
    AdminRunOut,
    AdminUserOut,
    PromptVersionOut,
    RubricIn,
    RubricVersionOut,
    TraceOut,
    UserOut,
)
from app.security import require_csrf

router = APIRouter(prefix="/admin", tags=["admin"])


def _admin(user: UserOut) -> UserOut:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only.")
    return user


@router.get("/users", response_model=list[AdminUserOut])
def list_users(user: CurrentUser) -> list[AdminUserOut]:
    _admin(user)
    with db.plain_tx() as conn, conn.cursor(row_factory=dict_row) as cur:
        rows = cur.execute(
            "select id, email, name, role, created_at from users order by created_at"
        ).fetchall()
    return [AdminUserOut(**row) for row in rows]


@router.get("/rubric", response_model=list[RubricVersionOut])
def list_rubrics(user: CurrentUser) -> list[RubricVersionOut]:
    """Every rubric version, newest first."""
    _admin(user)
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        rows = cur.execute(
            "select id, version, levels, indicators, descriptors, frozen_at, created_at "
            "from rubric_versions order by version desc"
        ).fetchall()
    return [RubricVersionOut(**row) for row in rows]


@router.post("/rubric", response_model=RubricVersionOut, status_code=status.HTTP_201_CREATED)
def create_rubric(payload: RubricIn, request: Request, user: CurrentUser) -> RubricVersionOut:
    """KF-12: save the rubric as a new version. The admin's assignments move to it; every past run keeps
    the version it snapshotted, so nothing already scored changes."""
    require_csrf(request)
    _admin(user)
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        newest = cur.execute("select coalesce(max(version), 0) as v from rubric_versions").fetchone()
        created = cur.execute(
            "insert into rubric_versions (owner_id, version, dimensions, levels, indicators, descriptors) "
            "values (%s, %s, %s, %s, %s, %s) "
            "returning id, version, levels, indicators, descriptors, frozen_at, created_at",
            (
                user.id,
                (newest["v"] if newest else 0) + 1,
                Jsonb(["cognitive", "metacognitive"]),
                Jsonb(payload.levels),
                Jsonb(payload.indicators),
                Jsonb(payload.descriptors),
            ),
        ).fetchone()
        if created is None:  # INSERT ... RETURNING always yields a row; this satisfies the type checker
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not saved.")
        cur.execute("update assignments set rubric_version_id = %s", (created["id"],))
    return RubricVersionOut(**created)


@router.get("/config", response_model=AdminConfigOut)
def get_config(user: CurrentUser) -> AdminConfigOut:
    """The model configuration a new run would snapshot, and the prompt versions it would reference."""
    _admin(user)
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        rows = cur.execute(
            "select id, agent_name, version, frozen_at, created_at from prompt_versions "
            "order by agent_name, version desc"
        ).fetchall()
    return AdminConfigOut(llm=_model_config(), prompt_versions=[PromptVersionOut(**row) for row in rows])


@router.get("/runs", response_model=list[AdminRunOut])
def list_runs(user: CurrentUser) -> list[AdminRunOut]:
    _admin(user)
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        rows = cur.execute(
            "select r.id, r.assignment_id, a.title as assignment_title, r.mode, r.status, "
            "r.repetition_group, r.repetition_index, r.repetitions, r.final_evaluation, "
            "r.model_unavailable, r.model_config ->> 'model' as model, r.created_at "
            "from runs r join assignments a on a.id = r.assignment_id order by r.created_at desc"
        ).fetchall()
    return [AdminRunOut(**row) for row in rows]


@router.get("/runs/{run_id}/traces", response_model=list[TraceOut])
def run_traces(run_id: uuid.UUID, user: CurrentUser) -> list[TraceOut]:
    """The run log: every agent step's input, structured output, latency and error (KNF-04)."""
    _admin(user)
    with db.tenant_tx(user.id) as conn, conn.cursor(row_factory=dict_row) as cur:
        if cur.execute("select 1 from runs where id = %s", (run_id,)).fetchone() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found.")
        rows = cur.execute(
            "select t.id, s.pseudonym as submission_pseudonym, t.agent_name, t.input_ref, "
            "t.output_json, t.latency_ms, t.error, t.created_at "
            "from agent_traces t left join submissions s on s.id = t.submission_id "
            "where t.run_id = %s order by s.pseudonym, t.created_at",
            (run_id,),
        ).fetchall()
    return [TraceOut(**row) for row in rows]
