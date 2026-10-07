"""Signup, login, logout, and the current-user lookup.

Cookie layout:
  ta_session — httpOnly, the session token (stored only as a SHA-256 hash in the DB)
  ta_csrf    — readable by the browser, echoed back in the X-CSRF-Token header on
               state-changing requests (double submit; see security.require_csrf)

Row factories are set per cursor, never on the connection: pooled connections are shared, so
mutating `conn.row_factory` would leak that choice into whatever request reuses the connection.
"""

import datetime as dt
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from psycopg.rows import dict_row

from app import db, security
from app.config import get_settings
from app.schemas import LoginIn, MeOut, SignupIn, UserOut
from app.security import require_csrf

router = APIRouter(prefix="/auth", tags=["auth"])

SESSION_TTL = dt.timedelta(days=14)


def _set_session_cookies(response: Response, token: str, csrf: str) -> None:
    settings = get_settings()
    max_age = int(dt.timedelta(days=settings.session_ttl_days).total_seconds())
    common: dict[str, Any] = {
        "max_age": max_age,
        "httponly": True,
        "secure": settings.cookie_secure,
        "samesite": "lax",
        "domain": settings.cookie_domain,
        "path": "/",
    }
    response.set_cookie(settings.session_cookie_name, token, **common)
    response.set_cookie(
        settings.csrf_cookie_name,
        csrf,
        max_age=max_age,
        httponly=False,
        secure=settings.cookie_secure,
        samesite="lax",
        domain=settings.cookie_domain,
        path="/",
    )


def _clear_session_cookies(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(settings.session_cookie_name, path="/", domain=settings.cookie_domain)
    response.delete_cookie(settings.csrf_cookie_name, path="/", domain=settings.cookie_domain)


def _create_session(cur, user_id) -> tuple[str, str]:
    token, csrf = security.new_token(), security.new_token()
    cur.execute(
        "insert into sessions (user_id, token_hash, csrf_token, expires_at) "
        "values (%s, %s, %s, now() + %s)",
        (user_id, security.token_hash(token), security.token_hash(csrf), SESSION_TTL),
    )
    return token, csrf


def current_user(request: Request) -> UserOut:
    """Resolve the session cookie to a user, or 401. Used as a dependency."""
    token = request.cookies.get(get_settings().session_cookie_name)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not signed in.")
    digest = security.token_hash(token)
    with db.plain_tx() as conn, conn.cursor(row_factory=dict_row) as cur:
        row = cur.execute(
            "select u.id, u.email, u.name, u.role, s.expires_at "
            "from sessions s join users u on u.id = s.user_id "
            "where s.token_hash = %s",
            (digest,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session not found.")
        if row["expires_at"] <= dt.datetime.now(dt.UTC):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired.")
        cur.execute("update sessions set last_seen_at = now() where token_hash = %s", (digest,))
    return UserOut(id=row["id"], email=row["email"], name=row["name"], role=row["role"])


CurrentUser = Annotated[UserOut, Depends(current_user)]


@router.post("/signup", response_model=MeOut, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupIn, response: Response) -> MeOut:
    security.check_password_strength(payload.password)
    email = payload.email.lower()
    password_hash = security.hash_password(payload.password)
    with db.plain_tx() as conn, conn.cursor(row_factory=dict_row) as cur:
        exists = cur.execute("select 1 from users where email = %s", (email,)).fetchone()
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")
        row = cur.execute(
            "insert into users (email, name, password_hash, role) "
            "values (%s, %s, %s, 'lecturer') returning id, email, name, role",
            (email, payload.name, password_hash),
        ).fetchone()
        if row is None:  # an insert with RETURNING always yields a row; this satisfies the type checker
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create the account."
            )
        token, csrf = _create_session(cur, row["id"])
    _set_session_cookies(response, token, csrf)
    return MeOut(user=UserOut(id=row["id"], email=row["email"], name=row["name"], role=row["role"]))


@router.post("/login", response_model=MeOut)
def login(payload: LoginIn, request: Request, response: Response) -> MeOut:
    email = payload.email.lower()
    security.check_login_rate(request, email)
    with db.plain_tx() as conn, conn.cursor(row_factory=dict_row) as cur:
        row = cur.execute(
            "select id, email, name, role, password_hash from users where email = %s", (email,)
        ).fetchone()
        if row is None or not security.verify_password(row["password_hash"], payload.password):
            security.note_failed_login(request, email)
            # Same message for an unknown email and a wrong password: do not leak which accounts exist.
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password."
            )
        token, csrf = _create_session(cur, row["id"])
    security.clear_login_attempts(request, email)
    _set_session_cookies(response, token, csrf)
    return MeOut(user=UserOut(id=row["id"], email=row["email"], name=row["name"], role=row["role"]))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response) -> Response:
    require_csrf(request)
    token = request.cookies.get(get_settings().session_cookie_name)
    if token:
        with db.plain_tx() as conn:
            conn.execute("delete from sessions where token_hash = %s", (security.token_hash(token),))
    _clear_session_cookies(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=MeOut)
def me(user: CurrentUser) -> MeOut:
    return MeOut(user=user)
