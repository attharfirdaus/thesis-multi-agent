"""The real identifier, held outside Neon (DECISIONS.md, 2026-10-16).

`student_identities` lived in Postgres until a privacy review flagged it as the highest-harm table in
the system and Atthar decided it must not sit in any managed, third-party database. The backend
already runs on his own machine (DECISIONS.md, 2026-10-14), so this is a Fernet-encrypted SQLite file
next to it instead — a second local file is the smallest move that actually gets the value out of
Neon, with no new service to run.

Tenancy has no help from row-level security here, unlike every Postgres table: every read and write
below takes `owner_id` and filters by it in the query itself, not only in the caller, because an
application-code mistake is the only thing standing between one lecturer and another lecturer's
students' names.

Nothing in `app/agents/*` or `app/llm/*` imports this module. The LLM-facing pipeline reads
`submissions.ai_output_text` / `student_analysis_text`, which `redact.py` has already stripped of
identifiers; this module exists for the lecturer's own screen, never for a provider payload.
"""

import sqlite3
from collections.abc import Iterable
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID

from cryptography.fernet import Fernet

from app.config import get_settings


def _fernet() -> Fernet:
    key = get_settings().identity_encryption_key
    if not key:
        raise RuntimeError(
            "IDENTITY_ENCRYPTION_KEY is not configured. Generate one with: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    return Fernet(key.encode())


@contextmanager
def _connect():
    path = Path(get_settings().identity_db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        conn.execute(
            "create table if not exists student_identities ("
            "submission_id text primary key, owner_id text not null, encrypted_identifier blob not null)"
        )
        yield conn
        conn.commit()
    finally:
        conn.close()


def store(submission_id: UUID, owner_id: UUID, real_identifier: str) -> None:
    """Capture the one identifier ingest is allowed to keep. Called once, from `_store()` in
    `app/routers/ingest.py`, before redaction would have deleted this same value from the text."""
    token = _fernet().encrypt(real_identifier.encode())
    with _connect() as conn:
        conn.execute(
            "insert or replace into student_identities (submission_id, owner_id, encrypted_identifier) "
            "values (?, ?, ?)",
            (str(submission_id), str(owner_id), token),
        )


def delete(submission_id: UUID) -> None:
    """The other half of `DELETE /submissions/{id}`: Postgres can no longer cascade this row for us,
    since it is not a foreign key into Postgres any more, so the router calls this explicitly."""
    with _connect() as conn:
        conn.execute("delete from student_identities where submission_id = ?", (str(submission_id),))


def read_many(submission_ids: Iterable[UUID], owner_id: UUID) -> dict[UUID, str]:
    """Real names for the given submissions, scoped to `owner_id`. A submission with no captured
    identifier, or owned by someone else, is simply absent — a missing name is not an error here, it
    is what an unlabelled file or another lecturer's row looks like."""
    ids = list(submission_ids)
    if not ids:
        return {}
    fernet = _fernet()
    placeholders = ",".join("?" for _ in ids)
    with _connect() as conn:
        rows = conn.execute(
            "select submission_id, encrypted_identifier from student_identities "  # noqa: S608 — `?` marks only
            f"where owner_id = ? and submission_id in ({placeholders})",
            (str(owner_id), *(str(i) for i in ids)),
        ).fetchall()
    return {UUID(submission_id): fernet.decrypt(token).decode() for submission_id, token in rows}


def read(submission_id: UUID, owner_id: UUID) -> str | None:
    return read_many([submission_id], owner_id).get(submission_id)
