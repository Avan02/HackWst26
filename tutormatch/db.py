"""TigerData connection and queries.

Everything that touches the database lives here. Import the helpers; don't
open your own connections.

    from tutormatch.db import fetch_all, fetch_one, execute
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from .config import settings

_pool: ConnectionPool | None = None

# Managed TigerData tiers cap connections, and four developers plus a deployed
# app add up fast. Keep this small.
_MAX_POOL = 8


def get_pool() -> ConnectionPool:
    global _pool
    if not settings.tiger_url:
        raise RuntimeError(
            "TIGER_URL is not set. Put your TigerData connection string in .env"
        )
    if _pool is None:
        _pool = ConnectionPool(
            settings.tiger_url,
            min_size=1,
            max_size=_MAX_POOL,
            kwargs={"row_factory": dict_row},
            open=True,
        )
    return _pool


@contextmanager
def cursor() -> Iterator[psycopg.Cursor]:
    """Yield a cursor inside a transaction that commits on clean exit."""
    with get_pool().connection() as conn:
        with conn.cursor() as cur:
            yield cur


def fetch_all(sql: str, params: tuple | dict | None = None) -> list[dict[str, Any]]:
    with cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def fetch_one(sql: str, params: tuple | dict | None = None) -> dict[str, Any] | None:
    with cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def execute(sql: str, params: tuple | dict | None = None) -> int:
    with cursor() as cur:
        cur.execute(sql, params)
        return cur.rowcount


def ping() -> dict[str, Any]:
    """Connectivity + extension check. Used by scripts and /api/health."""
    row = fetch_one(
        """
        SELECT version() AS pg_version,
               (SELECT extversion FROM pg_extension WHERE extname = 'timescaledb') AS timescaledb,
               (SELECT extversion FROM pg_extension WHERE extname = 'vector')      AS pgvector
        """
    )
    return row or {}


def apply_schema(path: Path | None = None) -> None:
    """Run schema.sql. Idempotent - safe to re-run."""
    sql_path = path or Path(__file__).resolve().parent.parent / "schema.sql"
    sql = sql_path.read_text(encoding="utf-8")
    with get_pool().connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()


# ----------------------------------------------------------------- user data


def upsert_user(
    auth_sub: str,
    *,
    name: str | None = None,
    email: str | None = None,
    avatar_url: str | None = None,
    role: str = "student",
    wallet_address: str | None = None,
) -> dict[str, Any]:
    """Create the user row if it's their first time, otherwise refresh it.

    This is the Auth0 -> TigerData bridge. Rather than configuring an Auth0
    Post-Login Action (which needs dashboard setup and is slow to debug), we
    call this on the first authenticated request. Same outcome, normal stack
    traces when it goes wrong.
    """
    return fetch_one(
        """
        INSERT INTO users (auth_sub, role, name, email, avatar_url, wallet_address)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (auth_sub) DO UPDATE SET
            name           = COALESCE(EXCLUDED.name, users.name),
            email          = COALESCE(EXCLUDED.email, users.email),
            avatar_url     = COALESCE(EXCLUDED.avatar_url, users.avatar_url),
            wallet_address = COALESCE(EXCLUDED.wallet_address, users.wallet_address)
        RETURNING *
        """,
        (auth_sub, role, name, email, avatar_url, wallet_address),
    ) or {}


def get_user(auth_sub: str) -> dict[str, Any] | None:
    return fetch_one("SELECT * FROM users WHERE auth_sub = %s", (auth_sub,))


def save_learner_profile(
    user_id: str,
    *,
    subjects: list[str],
    pace: str,
    goals: str,
    raw_answers: dict[str, Any],
    profile_sentence: str,
    style_vector: list[float],
) -> None:
    execute(
        """
        INSERT INTO learner_profiles
            (user_id, subjects, pace, goals, raw_answers, profile_sentence, style_vector, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, now())
        ON CONFLICT (user_id) DO UPDATE SET
            subjects         = EXCLUDED.subjects,
            pace             = EXCLUDED.pace,
            goals            = EXCLUDED.goals,
            raw_answers      = EXCLUDED.raw_answers,
            profile_sentence = EXCLUDED.profile_sentence,
            style_vector     = EXCLUDED.style_vector,
            updated_at       = now()
        """,
        (user_id, subjects, pace, goals, psycopg.types.json.Json(raw_answers),
         profile_sentence, str(style_vector)),
    )


def get_learner_profile(user_id: str) -> dict[str, Any] | None:
    return fetch_one("SELECT * FROM learner_profiles WHERE user_id = %s", (user_id,))
