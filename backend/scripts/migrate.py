"""Apply migrations/*.sql in filename order, recording each in schema_migrations.

Usage:  uv run python scripts/migrate.py           (uses MIGRATION_DATABASE_URL, else DATABASE_URL)

Numbered plain-SQL files rather than a migration framework: the schema is one file today, and a
framework can be added when there is a second one.
"""

import os
import pathlib
import sys

import psycopg

MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parent.parent / "migrations"


def dsn() -> str:
    url = os.environ.get("MIGRATION_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not url:
        sys.exit("Set MIGRATION_DATABASE_URL (preferred) or DATABASE_URL before migrating.")
    return url


def run(dsn_url: str) -> list[str]:
    applied: list[str] = []
    with psycopg.connect(dsn_url, autocommit=True) as conn:
        conn.execute(
            "create table if not exists schema_migrations ("
            " version text primary key, applied_at timestamptz not null default now())"
        )
        done = {row[0] for row in conn.execute("select version from schema_migrations")}
        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if path.name in done:
                continue
            with conn.transaction():
                conn.execute(path.read_text())
                conn.execute("insert into schema_migrations (version) values (%s)", (path.name,))
            applied.append(path.name)
    return applied


if __name__ == "__main__":
    names = run(dsn())
    print("applied:", ", ".join(names) if names else "nothing (already up to date)")
