"""Password hashing, session tokens, CSRF tokens, and login throttling."""

import hashlib
import secrets
import time
from collections import defaultdict, deque

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException, Request, status

from app.config import get_settings

_hasher = PasswordHasher()
MIN_PASSWORD_LENGTH = 10


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False
    except Exception:
        # Malformed or obsolete hash: treat as a failed login, never a 500.
        return False


def new_token() -> str:
    return secrets.token_urlsafe(32)


def token_hash(token: str) -> bytes:
    return hashlib.sha256(token.encode("utf-8")).digest()


def check_password_strength(password: str) -> None:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters.",
        )


# In-process login throttling. One process, one host: a per-process counter is enough here.
# ponytail: in-memory limiter, move to Postgres if the app ever runs more than one worker.
_attempts: dict[str, deque[float]] = defaultdict(deque)


def _key(request: Request, email: str) -> str:
    client = request.client.host if request.client else "unknown"
    return f"{client}|{email.lower()}"


def check_login_rate(request: Request, email: str) -> None:
    settings = get_settings()
    window, limit = settings.login_window_seconds, settings.login_max_attempts
    now = time.monotonic()
    bucket = _attempts[_key(request, email)]
    while bucket and now - bucket[0] > window:
        bucket.popleft()
    if len(bucket) >= limit:
        retry_after = int(window - (now - bucket[0])) + 1
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
            headers={"Retry-After": str(retry_after)},
        )


def note_failed_login(request: Request, email: str) -> None:
    _attempts[_key(request, email)].append(time.monotonic())


def clear_login_attempts(request: Request, email: str) -> None:
    _attempts.pop(_key(request, email), None)


def require_csrf(request: Request) -> None:
    """Double-submit check for state-changing requests made with a session cookie."""
    cookie = request.cookies.get(get_settings().csrf_cookie_name)
    header = request.headers.get("x-csrf-token")
    if not cookie or not header or not secrets.compare_digest(cookie, header):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF check failed.")
