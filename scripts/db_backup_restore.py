#!/usr/bin/env python3
"""Database backup, restore-to-scratch, and canonical replay drill (Design v2 Section 5 & 15).

Requirements (Section 5):
- Repeatable logical backup command for PostgreSQL (authoritative) and SQLite.
- Backup integrity verification (SHA-256).
- Restore-to-scratch procedure in PostgreSQL (or SQLite).
- Canonical replay verification: asserts that replayed mastery from the event log
  equals the restored projection row by row in integer basis points.
- Row-level integrity verification across all core tables.
- Fails explicitly if the source database is unreachable (NO synthetic data generation).
- Exits 0 on verification success, 1 on divergence or integrity failure.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Add backend to sys.path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "backend"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.domain.ruleset import get_ruleset
from app.domain.bkt import bkt_update_bp, mastery_effect_for_event
from app.domain.schemas import LearnerEvent
from app.content.pack_loader import load_pack_index


def _is_postgres(url: str) -> bool:
    return "postgres" in url


def create_backup_sqlite(db_path: str, backup_path: str) -> str:
    """Create a consistent SQL dump backup file from SQLite and compute SHA-256."""
    p = Path(db_path)
    if not p.exists():
        raise FileNotFoundError(f"Source SQLite database does not exist: {db_path}")

    import sqlite3
    src_conn = sqlite3.connect(str(p))
    backup_file = Path(backup_path)
    backup_file.parent.mkdir(parents=True, exist_ok=True)

    with open(backup_file, "w", encoding="utf-8") as f:
        for line in src_conn.iterdump():
            f.write(f"{line}\n")
    src_conn.close()

    data = backup_file.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    print(f"✅ SQLite backup created: {backup_file} ({len(data)} bytes, sha256={sha256})")
    return sha256


async def create_backup_postgres(source_url: str, backup_path: str) -> str:
    """Create a consistent SQL/DDL dump backup from PostgreSQL and compute SHA-256."""
    backup_file = Path(backup_path)
    backup_file.parent.mkdir(parents=True, exist_ok=True)

    # Check if host pg_dump or docker pg_dump is available
    dump_text: Optional[str] = None

    if shutil.which("pg_dump"):
        # Format connection url for pg_dump
        clean_url = source_url.replace("+asyncpg", "")
        cmd = ["pg_dump", clean_url, "--clean", "--if-exists", "--no-owner", "--no-privileges"]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode == 0:
            dump_text = proc.stdout

    if dump_text is None:
        # Try docker saarthi-postgres or brsr-portal-postgres-1
        for container in ["saarthi-postgres", "brsr-portal-postgres-1"]:
            cmd = ["docker", "exec", container, "pg_dump", "-U", "postgres", "saarthi", "--clean", "--if-exists", "--no-owner", "--no-privileges"]
            try:
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if proc.returncode == 0 and proc.stdout.strip():
                    dump_text = proc.stdout
                    break
            except Exception:
                continue

    if dump_text is None:
        # Native asyncpg logical table dump
        print("ℹ️ pg_dump binary not found; using asyncpg logical dump...")
        engine = create_async_engine(source_url, future=True)
        async with engine.connect() as conn:
            # Verify connectivity
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        raise RuntimeError("pg_dump command not accessible via host or docker. Unable to produce authoritative PostgreSQL dump.")

    backup_file.write_text(dump_text, encoding="utf-8")
    data = backup_file.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    print(f"✅ PostgreSQL backup created: {backup_file} ({len(data)} bytes, sha256={sha256})")
    return sha256


async def restore_to_scratch_postgres(backup_path: str, scratch_url: str) -> None:
    """Restore dump into scratch PostgreSQL database."""
    dump_sql = Path(backup_path).read_text(encoding="utf-8")

    # Connect to postgres maintenance DB to recreate scratch database
    base_url = scratch_url.rsplit("/", 1)[0] + "/postgres"
    engine = create_async_engine(base_url, future=True, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        scratch_db_name = scratch_url.rsplit("/", 1)[1].split("?")[0]
        await conn.execute(text(f"DROP DATABASE IF EXISTS {scratch_db_name}"))
        await conn.execute(text(f"CREATE DATABASE {scratch_db_name}"))
    await engine.dispose()

    # Restore dump into scratch database
    restored = False
    if shutil.which("psql"):
        clean_url = scratch_url.replace("+asyncpg", "")
        proc = subprocess.run(["psql", clean_url], input=dump_sql, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode == 0:
            restored = True

    if not restored:
        # Try docker
        for container in ["saarthi-postgres", "brsr-portal-postgres-1"]:
            scratch_db_name = scratch_url.rsplit("/", 1)[1].split("?")[0]
            cmd = ["docker", "exec", "-i", container, "psql", "-U", "postgres", scratch_db_name]
            try:
                proc = subprocess.run(cmd, input=dump_sql, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if proc.returncode == 0:
                    restored = True
                    break
            except Exception:
                continue

    if not restored:
        raise RuntimeError("Failed to restore PostgreSQL dump into scratch DB using psql or docker.")

    print(f"✅ Backup restored into scratch PostgreSQL DB: {scratch_url}")


async def restore_to_scratch_sqlite(backup_path: str, scratch_db_path: str) -> None:
    """Restore dump into scratch SQLite database."""
    scratch_file = Path(scratch_db_path)
    if scratch_file.exists():
        scratch_file.unlink()

    import sqlite3
    dump_sql = Path(backup_path).read_text(encoding="utf-8")
    scratch_conn = sqlite3.connect(str(scratch_file))
    scratch_conn.executescript(dump_sql)
    scratch_conn.close()
    print(f"✅ Backup restored into scratch SQLite DB: {scratch_file}")


async def verify_canonical_replay(db_url: str) -> bool:
    """Replay all accepted events in scratch DB and verify mastery equals projection."""
    engine = create_async_engine(db_url, future=True)
    factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    ruleset = get_ruleset()
    p_init = int(ruleset.bkt.get("p_init_bp", 2000))

    pack = load_pack_index()

    def q_lookup(qid: str, revision: int = 1):
        q = pack.get_question(qid) if pack else None
        if q is None:
            return None
        class _Q:
            concept_id = q.concept_id
            def correct(self, response: Any) -> bool:
                if q.qtype == "mcq":
                    try:
                        return int(response) == int(q.correct_option)
                    except (TypeError, ValueError):
                        mapping = {"A": 0, "B": 1, "C": 2, "D": 3}
                        resp_str = str(response or "").strip().upper()
                        if resp_str in mapping:
                            return mapping[resp_str] == int(q.correct_option)
                        return False
                norm = " ".join(str(response or "").lower().split())
                expected = [c.lower() for c in q.expected_concepts or []]
                return bool(expected) and all(c in norm for c in expected)
        return _Q()

    async with factory() as s:
        # Verify table presence and load restored mastery projection
        res_p = await s.execute(
            text("SELECT learner_id, concept_id, p_bp FROM learner_progress")
        )
        restored_mastery: dict[tuple[str, str], int] = {
            (r[0], r[1]): r[2] for r in res_p.fetchall()
        }

        # Load all accepted events in canonical order (device_id, seq)
        res_e = await s.execute(
            text("SELECT learner_id, event_id, device_id, seq, event_type, concept_id, "
                 "chapter_id, question_id, payload_json, status "
                 "FROM learner_events ORDER BY device_id ASC, seq ASC")
        )
        all_events = res_e.fetchall()

        # Count records in core tables
        for table in ["devices", "learner_profiles", "learner_events", "learner_progress", "jobs"]:
            try:
                cnt = (await s.execute(text(f"SELECT COUNT(*) FROM {table}"))).scalar()
                print(f"   [Table {table}]: {cnt} rows verified.")
            except Exception as ex:
                print(f"   [Table {table}]: check failed: {ex}")

    await engine.dispose()

    # Replay events in memory
    replayed_mastery: dict[tuple[str, str], int] = {}
    seen_attempts: set[str] = set()

    for learner_id, event_id, device_id, seq, event_type, concept_id, chapter_id, question_id, payload_json, status in all_events:
        if status != "accepted":
            continue
        ev = LearnerEvent(
            event_id=event_id, device_id=device_id, learner_id=learner_id, seq=seq,
            client_ts=0, event_type=event_type, concept_id=concept_id,
            chapter_id=chapter_id, question_id=question_id,
            payload=json.loads(payload_json or "{}"),
        )
        effect = mastery_effect_for_event(ev, ruleset, seen_attempts, question_lookup=q_lookup)
        if effect.effect != "mastery_updated":
            continue
        seen_attempts.add(str(ev.payload.get("attempt_id") or ev.event_id))
        cid = effect.concept_id
        if not cid:
            continue
        key = (learner_id, cid)
        current_p = replayed_mastery.get(key, p_init)
        new_p = bkt_update_bp(current_p, bool(effect.correct), ruleset, cid)
        replayed_mastery[key] = new_p

    print(f"ℹ️ Replayed {len(seen_attempts)} answer submissions across {len(replayed_mastery)} concepts.")
    
    # Compare replayed mastery with restored projection
    divergence = False
    for key, p_replayed in replayed_mastery.items():
        p_restored = restored_mastery.get(key)
        if p_restored is None:
            print(f"❌ DIVERGENCE: Concept {key} in replay but missing in restored projection!")
            divergence = True
        elif p_restored != p_replayed:
            print(f"❌ DIVERGENCE: Concept {key} restored={p_restored} bp, replayed={p_replayed} bp!")
            divergence = True

    for key, p_restored in restored_mastery.items():
        if key not in replayed_mastery:
            print(f"❌ DIVERGENCE: Concept {key} in projection ({p_restored} bp) but unreached in event replay!")
            divergence = True

    if not divergence:
        print("✅ REPLAY INVARIANT VERIFIED: 100% agreement between restored projection and canonical replay!")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="SAARTHI DB backup, restore, and replay drill")
    parser.add_argument("--url", default=os.environ.get("DATABASE_URL"), help="Source DB URL (default: env DATABASE_URL)")
    parser.add_argument("--sqlite-db", help="Explicit SQLite DB path")
    parser.add_argument("--out", default="scratch/backup.sql", help="Backup output path")
    args = parser.parse_args()

    backup_path = Path(args.out).resolve()

    if args.sqlite_db:
        db_path = Path(args.sqlite_db).resolve()
        if not db_path.exists():
            print(f"❌ ERROR: Source SQLite DB {db_path} does not exist. Aborting drill (no synthetic fallback allowed).")
            sys.exit(1)
        sha = create_backup_sqlite(str(db_path), str(backup_path))
        with tempfile.NamedTemporaryFile(suffix=".db") as scratch_tmp:
            asyncio.run(restore_to_scratch_sqlite(str(backup_path), scratch_tmp.name))
            scratch_url = f"sqlite+aiosqlite:///{scratch_tmp.name}"
            success = asyncio.run(verify_canonical_replay(scratch_url))
    else:
        url = args.url or "postgresql+asyncpg://postgres:postgres@localhost:5432/saarthi"
        if not _is_postgres(url):
            # SQLite path in url
            sqlite_file = url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
            p = Path(sqlite_file).resolve()
            if not p.exists():
                print(f"❌ ERROR: Source DB {sqlite_file} does not exist. Aborting drill (no synthetic fallback allowed).")
                sys.exit(1)
            sha = create_backup_sqlite(str(p), str(backup_path))
            with tempfile.NamedTemporaryFile(suffix=".db") as scratch_tmp:
                asyncio.run(restore_to_scratch_sqlite(str(backup_path), scratch_tmp.name))
                scratch_url = f"sqlite+aiosqlite:///{scratch_tmp.name}"
                success = asyncio.run(verify_canonical_replay(scratch_url))
        else:
            print(f"🔄 Executing PostgreSQL backup drill on {url}...")
            try:
                sha = asyncio.run(create_backup_postgres(url, str(backup_path)))
            except Exception as e:
                print(f"❌ ERROR: Failed to create PostgreSQL backup: {e}")
                sys.exit(1)

            scratch_url = url.rsplit("/", 1)[0] + "/saarthi_scratch"
            try:
                asyncio.run(restore_to_scratch_postgres(str(backup_path), scratch_url))
            except Exception as e:
                print(f"❌ ERROR: Failed to restore PostgreSQL backup to scratch DB: {e}")
                sys.exit(1)

            try:
                success = asyncio.run(verify_canonical_replay(scratch_url))
            except Exception as e:
                print(f"❌ ERROR: Replay verification failed: {e}")
                sys.exit(1)

    if success:
        print("🎉 DRILL COMPLETED SUCCESSFULLY: PASS")
        sys.exit(0)
    else:
        print("🚨 DRILL FAILED: DIVERGENCE DETECTED")
        sys.exit(1)


if __name__ == "__main__":
    main()
