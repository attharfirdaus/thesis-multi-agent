"""Phase 2 gate, at the API level: sign up, log in, stay logged in, log out.
Plus the two security properties that are easy to get wrong: cookie handling and tenant isolation."""

import uuid

import psycopg
import pytest
from pydantic import ValidationError

from app import db
from app.config import Settings

GOOD_PASSWORD = "kata-sandi-panjang-2026"


def signup(client, email="dosen@example.ac.id", name="Dosen Uji"):
    response = client.post("/auth/signup", json={"email": email, "name": name, "password": GOOD_PASSWORD})
    assert response.status_code == 201, response.text
    return response


def test_health(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["database"] == "ok"


def test_signup_then_me_then_logout(client):
    signup(client)
    me = client.get("/auth/me")
    assert me.status_code == 200
    assert me.json()["user"]["email"] == "dosen@example.ac.id"
    assert me.json()["user"]["role"] == "lecturer"

    csrf = client.cookies.get("ta_csrf")
    out = client.post("/auth/logout", headers={"X-CSRF-Token": csrf})
    assert out.status_code == 204
    assert client.get("/auth/me").status_code == 401


def test_me_without_session_is_401(client):
    assert client.get("/auth/me").status_code == 401


def test_session_cookie_is_httponly_and_csrf_is_not(client):
    response = signup(client)
    raw = response.headers.get_list("set-cookie")
    session_cookie = next(c for c in raw if c.startswith("ta_session="))
    csrf_cookie = next(c for c in raw if c.startswith("ta_csrf="))
    assert "httponly" in session_cookie.lower()
    assert "httponly" not in csrf_cookie.lower()
    assert "samesite=lax" in session_cookie.lower()


def test_short_password_rejected(client):
    response = client.post(
        "/auth/signup", json={"email": "a@example.ac.id", "name": "A", "password": "short"}
    )
    assert response.status_code == 422


def test_duplicate_email_rejected(client):
    signup(client)
    response = client.post(
        "/auth/signup", json={"email": "DOSEN@example.ac.id", "name": "Lain", "password": GOOD_PASSWORD}
    )
    assert response.status_code == 409


def test_login_with_wrong_password_is_401_and_does_not_leak_existence(client):
    signup(client)
    client.post("/auth/logout", headers={"X-CSRF-Token": client.cookies.get("ta_csrf")})
    wrong = client.post(
        "/auth/login", json={"email": "dosen@example.ac.id", "password": "salah-sekali"}
    )
    unknown = client.post(
        "/auth/login", json={"email": "tidak-ada@example.ac.id", "password": "salah-sekali"}
    )
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json()["detail"] == unknown.json()["detail"]


def test_login_works_and_logout_requires_csrf(client):
    signup(client)
    csrf = client.cookies.get("ta_csrf")
    client.post("/auth/logout", headers={"X-CSRF-Token": csrf})

    login = client.post("/auth/login", json={"email": "dosen@example.ac.id", "password": GOOD_PASSWORD})
    assert login.status_code == 200
    assert client.get("/auth/me").status_code == 200

    # A state-changing request without the CSRF header must be refused.
    assert client.post("/auth/logout").status_code == 403
    assert client.get("/auth/me").status_code == 200  # still signed in


def test_login_is_rate_limited(client):
    from app.config import get_settings

    signup(client)
    client.post("/auth/logout", headers={"X-CSRF-Token": client.cookies.get("ta_csrf")})
    limit = get_settings().login_max_attempts
    codes = [
        client.post("/auth/login", json={"email": "dosen@example.ac.id", "password": "salah"}).status_code
        for _ in range(limit)
    ]
    assert codes == [401] * limit
    blocked = client.post("/auth/login", json={"email": "dosen@example.ac.id", "password": "salah"})
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers


def test_cookie_samesite_setting():
    """'none' is what a cross-site deployment needs; anything else must be rejected at startup
    rather than producing a cookie the browser silently drops."""
    base = {"DATABASE_URL": "postgresql://user:pw@localhost:5432/db"}
    assert Settings(**base).cookie_samesite == "lax"
    assert Settings(**base, COOKIE_SAMESITE="none").cookie_samesite == "none"
    with pytest.raises(ValidationError):
        Settings(**base, COOKIE_SAMESITE="bogus")


def test_row_level_security_isolates_lecturers(client):
    """The core tenant promise: one lecturer's rows are invisible to another, enforced in the DB."""
    signup(client, email="dosen.a@example.ac.id", name="Dosen A")
    user_a = uuid.UUID(client.get("/auth/me").json()["user"]["id"])
    csrf_a = client.cookies.get("ta_csrf")

    with db.tenant_tx(user_a) as conn:
        row = conn.execute(
            "insert into assignments (owner_id, title, course) values (%s, %s, %s) returning id",
            (user_a, "Tugas A", "MRTI"),
        ).fetchone()
        assignment_a = row[0]

    # A sees their own row.
    with db.tenant_tx(user_a) as conn:
        assert conn.execute("select count(*) from assignments").fetchone()[0] == 1

    # No tenant context at all: nothing is visible (this also catches context leaking
    # between pooled connections).
    with db.plain_tx() as conn:
        assert conn.execute("select count(*) from assignments").fetchone()[0] == 0

    client.post("/auth/logout", headers={"X-CSRF-Token": csrf_a})
    signup(client, email="dosen.b@example.ac.id", name="Dosen B")
    user_b = uuid.UUID(client.get("/auth/me").json()["user"]["id"])

    with db.tenant_tx(user_b) as conn:
        assert conn.execute("select count(*) from assignments").fetchone()[0] == 0
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            # Writing a row owned by someone else must fail the WITH CHECK clause.
            conn.execute(
                "insert into assignments (owner_id, title, course) values (%s, %s, %s)",
                (user_a, "Curi", "MRT"),
            )

    # The row A wrote is still there, untouched.
    with db.tenant_tx(user_a) as conn:
        assert (
            conn.execute("select title from assignments where id = %s", (assignment_a,)).fetchone()[0]
            == "Tugas A"
        )
