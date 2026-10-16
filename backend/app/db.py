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
            # Neon's pooler runs PgBouncer in transaction mode:
            # prepare_threshold=None disables server-side named prepared statements,
            # which break when subsequent queries on the same client hit different backend connections.
            #
            # `check` is what survives Neon's free tier suspending an idle compute: the server closes
            # the socket, the client does not know, and the next query on that pooled connection raised
            # "SSL connection has been closed unexpectedly", turning a `/auth/me` into a 500 (seen live,
            # 2026-10-16). It costs one round trip per checkout, deliberately paid on a free tier.
            # [UNVERIFIED locally]: local Postgres closes the connection in a way psycopg_pool already
            # detects, so no test here can reproduce the silent death; the evidence is the documented
            # remedy plus the absence of those 500s in use.
            check=ConnectionPool.check_connection,
            kwargs={"autocommit": False, "prepare_threshold": None},
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
