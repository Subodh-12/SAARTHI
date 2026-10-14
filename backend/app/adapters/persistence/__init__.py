"""Persistence adapter — SQLAlchemy async engine + tiny migration runner.

Backend defaults to SQLite (`aiosqlite`); selecting `postgres` requires a
`postgres*` DATABASE_URL. The repository layer talks to repositories that
depend on the interface, never the driver directly.
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ...core.logging import get_logger
from ...core.settings import get_settings

log = get_logger("saarthi.persistence")

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class Persistence:
    """Wraps a SQLAlchemy AsyncEngine + session factory.

    The class is the seam where we could swap to Postgres/MinIO/Redis without
    touching callers. Workers do not own durable state — all state lives here.
    """

    def __init__(self, engine: AsyncEngine, factory: "sessionmaker[AsyncSession]") -> None:
        self.engine = engine
        self.factory = factory

    @classmethod
    def from_settings(cls) -> "Persistence":
        s = get_settings()
        url = s.database_url
        engine = create_async_engine(
            url, echo=s.db_echo, pool_size=s.db_pool_size if "postgres" in url else 5,
            future=True,
        )
        factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        return cls(engine, factory)

    async def apply_schema(self) -> None:
        """Apply schema.sql to the connected DB, then migrate a prior
        schema in place (guarded column additions). Idempotent."""
        sql = SCHEMA_PATH.read_text(encoding="utf-8")
        # SQLite + async: use raw_connection for batch DDL.
        async with self.engine.begin() as conn:
            # split on semicolons (statements only, no procedures)
            for stmt in _split_statements(sql):
                stmt = stmt.strip()
                if not stmt:
                    continue
                await conn.exec_driver_sql(stmt) if hasattr(conn, "exec_driver_sql") else await conn.execute(_text(stmt))
            await _migrate_prior_schema(conn)
        log.info("schema_applied path=%s", SCHEMA_PATH)

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self.factory() as session:
            yield session

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        """One explicit database transaction (Design v2 Section 5).

        The sync batch uses this so event inserts, the mastery projection
        and the cursor advance commit together — or not at all.
        """
        async with self.factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def dispose(self) -> None:
        await self.engine.dispose()


def _split_statements(sql: str) -> list[str]:
    """Naive SQL splitter — good enough for our DDL (no procedures)."""
    out: list[str] = []
    cur: list[str] = []
    for line in sql.splitlines():
        line = line.strip()
        if not line or line.startswith("--"):
            continue
        cur.append(line)
        if line.endswith(";"):
            out.append("\n".join(cur))
            cur = []
    if cur:
        out.append("\n".join(cur))
    return out


def _text(stmt: str):
    from sqlalchemy import text
    return text(stmt)


# --------------------------------------------------------------------------- #
# Prior-schema migrations (guarded, idempotent column additions)
# --------------------------------------------------------------------------- #
async def _table_exists(conn, table: str) -> bool:
    from sqlalchemy import text
    if "sqlite" in str(conn.dialect.name):
        res = await conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=:t"),
            {"t": table})
    else:
        res = await conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = current_schema() AND table_name = :t"),
            {"t": table})
    return res.fetchone() is not None


async def _columns(conn, table: str) -> set[str]:
    from sqlalchemy import text
    if "sqlite" in str(conn.dialect.name):
        res = await conn.execute(text(f"PRAGMA table_info({table})"))
        return {row[1] for row in res.fetchall()}
    res = await conn.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = current_schema() AND table_name = :t"),
        {"t": table})
    return {row[0] for row in res.fetchall()}


_MIGRATIONS: list[tuple[str, str, str]] = [
    # (table, column, DDL to add it when missing)
    ("learner_progress", "p_bp",
     "ALTER TABLE learner_progress ADD COLUMN p_bp INTEGER"),
    ("learner_progress", "bkt_version",
     "ALTER TABLE learner_progress ADD COLUMN bkt_version TEXT NOT NULL DEFAULT '1'"),
    ("learner_progress", "last_event_seq",
     "ALTER TABLE learner_progress ADD COLUMN last_event_seq INTEGER"),
    ("learner_events", "status",
     "ALTER TABLE learner_events ADD COLUMN status TEXT NOT NULL DEFAULT 'accepted'"),
    ("learner_events", "effect", "ALTER TABLE learner_events ADD COLUMN effect TEXT"),
    ("learner_events", "reason", "ALTER TABLE learner_events ADD COLUMN reason TEXT"),
    ("learner_events", "client_ts",
     "ALTER TABLE learner_events ADD COLUMN client_ts INTEGER"),
    ("decisions", "needs_help",
     "ALTER TABLE decisions ADD COLUMN needs_help INTEGER NOT NULL DEFAULT 0"),
    ("decisions", "source",
     "ALTER TABLE decisions ADD COLUMN source TEXT NOT NULL DEFAULT 'server'"),
    ("decisions", "trigger_event_id",
     "ALTER TABLE decisions ADD COLUMN trigger_event_id TEXT"),
    ("questions", "revision",
     "ALTER TABLE questions ADD COLUMN revision INTEGER NOT NULL DEFAULT 1"),
    ("questions", "answer_key_hash",
     "ALTER TABLE questions ADD COLUMN answer_key_hash TEXT NOT NULL DEFAULT ''"),
    ("questions", "status",
     "ALTER TABLE questions ADD COLUMN status TEXT NOT NULL DEFAULT 'active'"),
    ("learner_devices", "status",
     "ALTER TABLE learner_devices ADD COLUMN status TEXT NOT NULL DEFAULT 'active'"),
]


async def _migrate_prior_schema(conn) -> None:
    """Apply guarded column additions for databases created by the prior
    (v1) schema. Backfills integer mastery from the old float column."""
    from sqlalchemy import text
    if not await _table_exists(conn, "learner_progress"):
        return  # fresh database — schema.sql already created everything
    existing = await _columns(conn, "learner_progress")
    if "p_known" in existing and "p_bp" not in existing:
        await conn.execute(text(
            "ALTER TABLE learner_progress ADD COLUMN p_bp INTEGER"))
        # Backfill: half-up rounding of the stored float — floor(x + 0.5)
        # is exactly half-up for this domain (values live in [0.01, 0.99],
        # so the float product never sits on a .5 boundary of its own).
        await conn.execute(text(
            "UPDATE learner_progress SET p_bp = "
            "CAST(p_known * 10000 + 0.5 AS INTEGER)"))
        log.info("migrated learner_progress.p_known -> p_bp")
    for table, column, ddl in _MIGRATIONS:
        cols = await _columns(conn, table)
        if table == "learner_progress" and "p_bp" in cols:
            if column in cols:
                continue
            await conn.execute(text(ddl))
            log.info("migrated %s.%s", table, column)
            continue
        if column not in cols:
            await conn.execute(text(ddl))
            log.info("migrated %s.%s", table, column)
    # devices.public_key_spki / revoked_at / last_seen_at
    if await _table_exists(conn, "devices"):
        cols = await _columns(conn, "devices")
        for column, ddl in (
            ("public_key_spki", "ALTER TABLE devices ADD COLUMN public_key_spki TEXT"),
            ("revoked_at", "ALTER TABLE devices ADD COLUMN revoked_at INTEGER"),
            ("last_seen_at", "ALTER TABLE devices ADD COLUMN last_seen_at INTEGER"),
        ):
            if column not in cols:
                await conn.execute(text(ddl))
                log.info("migrated devices.%s", column)

    # device_tokens: in legacy schema device_id was a PRIMARY KEY.
    # In v2, devices can hold multiple unexpired access tokens during renewals.
    if await _table_exists(conn, "device_tokens"):
        if "sqlite" in str(conn.dialect.name):
            res = await conn.execute(text("PRAGMA table_info(device_tokens)"))
            rows = res.fetchall()
            pk_col = next((row[1] for row in rows if row[1] == "device_id" and row[5] == 1), None)
            if pk_col:
                await conn.execute(text(
                    "CREATE TABLE device_tokens_v2 ("
                    "  device_id TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,"
                    "  token_hash TEXT NOT NULL,"
                    "  issued_at INTEGER NOT NULL,"
                    "  expires_at INTEGER NOT NULL,"
                    "  revoked INTEGER NOT NULL DEFAULT 0"
                    ")"
                ))
                await conn.execute(text(
                    "INSERT INTO device_tokens_v2 (device_id, token_hash, issued_at, expires_at, revoked) "
                    "SELECT device_id, token_hash, issued_at, expires_at, revoked FROM device_tokens"
                ))
                await conn.execute(text("DROP TABLE device_tokens"))
                await conn.execute(text("ALTER TABLE device_tokens_v2 RENAME TO device_tokens"))
                await conn.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_device_tokens_hash "
                    "ON device_tokens (token_hash, revoked, expires_at)"
                ))
                log.info("migrated device_tokens (removed legacy PRIMARY KEY on device_id)")
        else:
            try:
                await conn.execute(text("ALTER TABLE device_tokens DROP CONSTRAINT IF EXISTS device_tokens_pkey"))
            except Exception:
                pass

    # learner_events: legacy schema had `ts NOT NULL`, whereas v2 canonical schema uses `client_ts`.
    # When ts is present with NOT NULL, migrate to canonical schema preserving all data.
    if await _table_exists(conn, "learner_events"):
        if "sqlite" in str(conn.dialect.name):
            res = await conn.execute(text("PRAGMA table_info(learner_events)"))
            rows = res.fetchall()
            ts_row = next((r for r in rows if r[1] == "ts"), None)
            if ts_row and ts_row[3] == 1:  # ts column is NOT NULL
                await conn.execute(text("PRAGMA foreign_keys = OFF"))
                await conn.execute(text(
                    "CREATE TABLE learner_events_v2 ("
                    "  device_id TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,"
                    "  learner_id TEXT NOT NULL REFERENCES learner_profiles(learner_id) ON DELETE CASCADE,"
                    "  seq INTEGER NOT NULL,"
                    "  event_id TEXT NOT NULL,"
                    "  client_ts INTEGER NOT NULL,"
                    "  event_type TEXT NOT NULL,"
                    "  concept_id TEXT,"
                    "  chapter_id TEXT,"
                    "  question_id TEXT,"
                    "  payload_json TEXT NOT NULL DEFAULT '{}',"
                    "  status TEXT NOT NULL DEFAULT 'accepted',"
                    "  effect TEXT,"
                    "  reason TEXT,"
                    "  received_at INTEGER NOT NULL,"
                    "  server_seq INTEGER,"
                    "  PRIMARY KEY (device_id, seq),"
                    "  UNIQUE (event_id)"
                    ")"
                ))
                has_client_ts = any(r[1] == "client_ts" for r in rows)
                ts_expr = "COALESCE(client_ts, ts, received_at, 0)" if has_client_ts else "COALESCE(ts, received_at, 0)"
                has_status = any(r[1] == "status" for r in rows)
                status_expr = "COALESCE(status, 'accepted')" if has_status else "'accepted'"
                has_payload = any(r[1] == "payload_json" for r in rows)
                payload_expr = "COALESCE(payload_json, '{}')" if has_payload else "'{}'"
                await conn.execute(text(f"""
                    INSERT INTO learner_events_v2
                    (device_id, learner_id, seq, event_id, client_ts, event_type,
                     concept_id, chapter_id, question_id, payload_json, status,
                     effect, reason, received_at, server_seq)
                    SELECT
                      device_id, learner_id, seq, event_id,
                      {ts_expr},
                      event_type, concept_id, chapter_id, question_id,
                      {payload_expr},
                      {status_expr},
                      effect, reason, received_at, server_seq
                    FROM learner_events
                """))
                await conn.execute(text("DROP TABLE learner_events"))
                await conn.execute(text("ALTER TABLE learner_events_v2 RENAME TO learner_events"))
                await conn.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_events_learner_seq "
                    "ON learner_events (learner_id, server_seq)"
                ))
                await conn.execute(text("PRAGMA foreign_keys = ON"))
                log.info("migrated learner_events (canonical client_ts schema, preserved data)")


# --------------------------------------------------------------------------- #
# Lifecycle helpers
# --------------------------------------------------------------------------- #
_singleton: Optional[Persistence] = None


async def get_persistence() -> Persistence:
    global _singleton
    if _singleton is None:
        _singleton = Persistence.from_settings()
        await _singleton.apply_schema()
    return _singleton


async def dispose_persistence() -> None:
    global _singleton
    if _singleton is not None:
        await _singleton.dispose()
        _singleton = None


async def reset_persistence_for_tests() -> Persistence:
    """Test helper — recreates the schema from scratch on a fresh DB file."""
    global _singleton
    if _singleton is not None:
        await _singleton.dispose()
        _singleton = None
    s = get_settings()
    if s.persistence_backend == "sqlite":
        # wipe the DB file for a clean slate
        db_path = s.database_url.split("///")[-1]
        if db_path and db_path != ":memory:" and os.path.exists(db_path):
            os.remove(db_path)
    _singleton = Persistence.from_settings()
    await _singleton.apply_schema()
    return _singleton


__all__ = [
    "Persistence",
    "get_persistence",
    "dispose_persistence",
    "reset_persistence_for_tests",
    "SCHEMA_PATH",
]
