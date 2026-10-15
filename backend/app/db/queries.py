import json
from datetime import date, datetime
from typing import Any

import psycopg

from app.db.pool import get_connection

# ==========================================
# USER QUERIES (Argon2id + Roles)
# ==========================================

async def get_user_by_username(username: str) -> dict[str, Any] | None:
    query = """
        SELECT id, username, password_hash, role, is_active, created_at
        FROM users
        WHERE username = %s;
    """
    async with get_connection() as conn:
        async with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            await cur.execute(query, (username,))
            return await cur.fetchone()


async def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    query = """
        SELECT id, username, password_hash, role, is_active, created_at
        FROM users
        WHERE id = %s;
    """
    async with get_connection() as conn:
        async with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            await cur.execute(query, (user_id,))
            return await cur.fetchone()


async def create_user(
    username: str, password_hash: str, role: str = "viewer"
) -> dict[str, Any]:
    query = """
        INSERT INTO users (username, password_hash, role, is_active)
        VALUES (%s, %s, %s, TRUE)
        ON CONFLICT (username) DO UPDATE
        SET password_hash = EXCLUDED.password_hash,
            role = EXCLUDED.role,
            is_active = TRUE
        RETURNING id, username, role, is_active, created_at;
    """
    async with get_connection() as conn:
        async with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            await cur.execute(query, (username, password_hash, role))
            await conn.commit()
            return await cur.fetchone()


# ==========================================
# REFRESH TOKEN QUERIES
# ==========================================

async def create_refresh_token(
    user_id: int, token_hash: str, expires_at: datetime
) -> dict[str, Any]:
    query = """
        INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
        VALUES (%s, %s, %s)
        RETURNING id, user_id, token_hash, expires_at, revoked_at;
    """
    async with get_connection() as conn:
        async with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            await cur.execute(query, (user_id, token_hash, expires_at))
            await conn.commit()
            return await cur.fetchone()


async def get_refresh_token_by_hash(token_hash: str) -> dict[str, Any] | None:
    query = """
        SELECT id, user_id, token_hash, expires_at, revoked_at
        FROM refresh_tokens
        WHERE token_hash = %s;
    """
    async with get_connection() as conn:
        async with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            await cur.execute(query, (token_hash,))
            return await cur.fetchone()


async def revoke_refresh_token(token_hash: str) -> bool:
    query = """
        UPDATE refresh_tokens
        SET revoked_at = now()
        WHERE token_hash = %s AND revoked_at IS NULL;
    """
    async with get_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, (token_hash,))
            await conn.commit()
            return cur.rowcount > 0


# ==========================================
# SOURCES & SNAPSHOTS
# ==========================================

async def get_all_sources() -> list[dict[str, Any]]:
    query = """
        SELECT id, name, url, is_nse
        FROM sources
        ORDER BY is_nse DESC, id ASC;
    """
    async with get_connection() as conn:
        async with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            await cur.execute(query)
            return await cur.fetchall()


async def get_all_snapshots() -> list[dict[str, Any]]:
    query = """
        SELECT card, payload, as_of, fetched_at, status, last_error, version
        FROM snapshots
        ORDER BY card ASC;
    """
    async with get_connection() as conn:
        async with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            await cur.execute(query)
            return await cur.fetchall()


async def get_snapshot_by_card(card: str) -> dict[str, Any] | None:
    query = """
        SELECT card, payload, as_of, fetched_at, status, last_error, version
        FROM snapshots
        WHERE card = %s;
    """
    async with get_connection() as conn:
        async with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            await cur.execute(query, (card,))
            return await cur.fetchone()


async def upsert_snapshot(
    card: str,
    payload: dict[str, Any],
    as_of: date | None,
    status: str,
    last_error: str | None = None
) -> None:
    query = """
        INSERT INTO snapshots (card, payload, as_of, fetched_at, status, last_error, version)
        VALUES (%s, %s::jsonb, %s, now(), %s, %s, 1)
        ON CONFLICT (card) DO UPDATE
        SET payload = CASE WHEN %s = 'fresh' THEN EXCLUDED.payload ELSE snapshots.payload END,
            as_of = CASE WHEN %s = 'fresh' THEN EXCLUDED.as_of ELSE snapshots.as_of END,
            fetched_at = now(),
            status = EXCLUDED.status,
            last_error = EXCLUDED.last_error,
            version = snapshots.version + 1;
    """
    payload_json = json.dumps(payload)
    async with get_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                query,
                (card, payload_json, as_of, status, last_error, status, status)
            )
            await conn.commit()


# ==========================================
# OBSERVATIONS & COLLECTOR RUNS
# ==========================================

async def insert_observation(
    indicator: str,
    series: str,
    period: str,
    period_start: date | None,
    value: float | None,
    unit: str,
    is_estimate: bool,
    source_id: str,
    as_of: date,
    raw_ref: str | None = None
) -> None:
    query = """
        INSERT INTO observations (
            indicator, series, period, period_start, value, unit,
            is_estimate, source_id, as_of, fetched_at, raw_ref
        ) VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, now(), %s
        )
        ON CONFLICT (indicator, series, period, as_of) DO UPDATE
        SET value = EXCLUDED.value,
            unit = EXCLUDED.unit,
            is_estimate = EXCLUDED.is_estimate,
            fetched_at = now(),
            raw_ref = EXCLUDED.raw_ref;
    """
    async with get_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                query,
                (
                    indicator, series, period, period_start, value, unit,
                    is_estimate, source_id, as_of, raw_ref
                )
            )
            await conn.commit()


async def get_observations(
    indicator: str,
    from_date: date | None = None,
    to_date: date | None = None
) -> list[dict[str, Any]]:
    if from_date and to_date:
        query = """
            SELECT indicator, series, period, period_start, value, unit, is_estimate, source_id, as_of, fetched_at
            FROM observations
            WHERE indicator = %s AND as_of >= %s AND as_of <= %s
            ORDER BY as_of ASC, period ASC;
        """
        params = (indicator, from_date, to_date)
    elif from_date:
        query = """
            SELECT indicator, series, period, period_start, value, unit, is_estimate, source_id, as_of, fetched_at
            FROM observations
            WHERE indicator = %s AND as_of >= %s
            ORDER BY as_of ASC, period ASC;
        """
        params = (indicator, from_date)
    elif to_date:
        query = """
            SELECT indicator, series, period, period_start, value, unit, is_estimate, source_id, as_of, fetched_at
            FROM observations
            WHERE indicator = %s AND as_of <= %s
            ORDER BY as_of ASC, period ASC;
        """
        params = (indicator, to_date)
    else:
        query = """
            SELECT indicator, series, period, period_start, value, unit, is_estimate, source_id, as_of, fetched_at
            FROM observations
            WHERE indicator = %s
            ORDER BY as_of ASC, period ASC;
        """
        params = (indicator,)

    async with get_connection() as conn:
        async with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            await cur.execute(query, params)
            return await cur.fetchall()


async def record_collector_run(
    job: str,
    started_at: datetime,
    finished_at: datetime,
    ok: bool,
    http_status: int | None = None,
    duration_ms: int | None = None,
    note: str | None = None
) -> None:
    query = """
        INSERT INTO collector_runs (job, started_at, finished_at, ok, http_status, duration_ms, note)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    async with get_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                query,
                (job, started_at, finished_at, ok, http_status, duration_ms, note)
            )
            await conn.commit()
