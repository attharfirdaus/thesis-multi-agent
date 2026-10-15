"""Create the LangGraph checkpoint tables, as the owner role, once.

Usage:  uv run python -m scripts.setup_checkpointer

Why this is separate from `scripts/migrate.py`: the checkpoint schema belongs to LangGraph, not to
this project, and the library provides it through `PostgresSaver.setup()`. That call issues DDL, and
the runtime role deliberately has no DDL rights — `thesis_app` may not create tables, because a role
that can create tables can also alter the policies that make tenancy work. So the tables are created
here, by the migrator role, and the runtime role only ever inserts and selects.

Idempotent: the library's own migrations are guarded, so re-running is safe.
Checkpoint tables are owned by the migrator, like every other table here, so the runtime role needs
explicit DML on them. If a future LangGraph release adds another table, the failure is a loud
permission error and this list is what to extend.
"""

import os
import sys

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import sql

CHECKPOINT_TABLES = (
    "checkpoints",
    "checkpoint_blobs",
    "checkpoint_writes",
    "checkpoint_migrations",
)

RUNTIME_ROLE = "thesis_app"


def dsn() -> str:
    url = os.environ.get("MIGRATION_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if url:
        return url
    from app.config import get_settings

    settings = get_settings()
    url = settings.migration_database_url or settings.database_url
    if not url:
        sys.exit("Set MIGRATION_DATABASE_URL (preferred) or DATABASE_URL, or create backend/.env.")
    return url


def setup(url: str) -> None:
    """Create the checkpoint tables and let the runtime role use them. Idempotent."""
    with PostgresSaver.from_conn_string(url) as saver:
        saver.setup()

    # The runtime role is not the owner on purpose, so it needs the grant explicitly. psycopg's own
    # SQL composition builds the statement, which is both the safe way and the readable one.
    with psycopg.connect(url, autocommit=True) as conn:
        role_exists = conn.execute(
            "select 1 from pg_roles where rolname = %s", (RUNTIME_ROLE,)
        ).fetchone()
        if role_exists:
            conn.execute(
                sql.SQL("grant select, insert, update, delete on {} to {}").format(
                    sql.SQL(", ").join(sql.Identifier(table) for table in CHECKPOINT_TABLES),
                    sql.Identifier(RUNTIME_ROLE),
                )
            )


def main() -> int:
    setup(dsn())
    print("Checkpoint tables are in place.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
