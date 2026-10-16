"""`identity_store` has no row-level security to fall back on (DECISIONS.md, 2026-10-16): every
query filters by `owner_id` itself, so the one thing worth mutation-testing here is that filter.
"""

import uuid

import pytest

from app.ingest import identity_store


def test_a_stored_name_round_trips_encrypted_at_rest():
    submission_id, owner_id = uuid.uuid4(), uuid.uuid4()
    identity_store.store(submission_id, owner_id, "Budi Santoso")

    assert identity_store.read(submission_id, owner_id) == "Budi Santoso"

    import sqlite3

    from app.config import get_settings

    conn = sqlite3.connect(get_settings().identity_db_path)
    raw = conn.execute(
        "select encrypted_identifier from student_identities where submission_id = ?",
        (str(submission_id),),
    ).fetchone()[0]
    conn.close()
    assert b"Budi Santoso" not in raw


def test_another_owner_cannot_read_a_name_even_with_the_right_submission_id():
    submission_id = uuid.uuid4()
    owner, other = uuid.uuid4(), uuid.uuid4()
    identity_store.store(submission_id, owner, "Budi Santoso")

    assert identity_store.read(submission_id, other) is None
    assert identity_store.read(submission_id, owner) == "Budi Santoso"


def test_read_many_only_returns_the_calling_owners_rows():
    owner, other = uuid.uuid4(), uuid.uuid4()
    mine = uuid.uuid4()
    theirs = uuid.uuid4()
    identity_store.store(mine, owner, "Milik Saya")
    identity_store.store(theirs, other, "Milik Lain")

    names = identity_store.read_many([mine, theirs], owner)

    assert names == {mine: "Milik Saya"}


def test_read_many_with_no_ids_does_not_touch_the_store():
    assert identity_store.read_many([], uuid.uuid4()) == {}


def test_delete_removes_the_row_and_is_a_no_op_for_an_absent_one():
    submission_id, owner_id = uuid.uuid4(), uuid.uuid4()
    identity_store.store(submission_id, owner_id, "Budi Santoso")

    identity_store.delete(submission_id)
    assert identity_store.read(submission_id, owner_id) is None

    identity_store.delete(submission_id)  # does not raise


def test_storing_again_for_the_same_submission_replaces_the_name():
    submission_id, owner_id = uuid.uuid4(), uuid.uuid4()
    identity_store.store(submission_id, owner_id, "Nama Lama")
    identity_store.store(submission_id, owner_id, "Nama Baru")

    assert identity_store.read(submission_id, owner_id) == "Nama Baru"


def test_reading_without_a_configured_key_fails_loudly(monkeypatch):
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "identity_encryption_key", None)
    with pytest.raises(RuntimeError, match="IDENTITY_ENCRYPTION_KEY"):
        identity_store.read(uuid.uuid4(), uuid.uuid4())
