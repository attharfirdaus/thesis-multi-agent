"""Connection pool and the two transaction shapes this app has.

`plain_tx()` is for the auth tables only (users, sessions): resolving a session token to a
user has to happen before any tenant context exists.

`tenant_tx(user_id)` is everything else. It issues `SET LOCAL app.current_user_id`, which is
what the row-level-security policies on the tenant tables compare `owner_id` against. The
runtime role is not the table owner and the policies are FORCEd, so forgetting this call
returns zero rows rather than someone else's data.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

from psycopg import Connection
from psycopg_pool import ConnectionPool

from app.config import get_settings

_pool: ConnectionPool | None = None


def pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            get_settings().database_url,
            min_size=1,
            max_size=5,
            open=False,
            kwargs={"autocommit": False},
        )
    return _pool


def open_pool() -> None:
    pool().open()


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


@contextmanager
def plain_tx() -> Iterator[Connection]:
    with pool().connection() as conn:
        yield conn


@contextmanager
def tenant_tx(user_id: UUID) -> Iterator[Connection]:
    with pool().connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select set_config('app.current_user_id', %s, true)", (str(user_id),))
        yield conn
