"""SQLAlchemy repository implementations (v2).

All repositories depend on the interface in `repositories/interfaces.py`,
not on the FastAPI request layer. They share a single `Persistence` engine.
The sync batch transaction lives in SyncService, which uses
`Persistence.transaction()` so events, mastery projection and cursor move
atomically (Design v2 Section 5/8).
"""
from __future__ import annotations

import json
import time
import uuid
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.schemas import (
    Action, BackgroundAction, DeliveryMode, Decision, DecisionTrace,
    GenerationRecord, LearnerEvent, LearnerProfile, MasteryRecord,
    NetworkState, Outcome, PackManifest, PerEventResult, SyncEffect,
    SyncReason, TraceStep, new_learner_id,
)
from ...repositories.interfaces import (
    DecisionRepository, DeviceRepository, EventRepository,
    GenerationRecordRepository, LearnerRepository, MasteryRepository,
    PackRepository,
)
from . import Persistence


def _now_ms() -> int:
    return int(time.time() * 1000)


def _server_seq_next() -> int:
    # Use millisecond timestamp + random suffix for ordering tie-break.
    # For Postgres this would be a SEQUENCE; SQLite uses this composite.
    return _now_ms() * 1000 + (uuid.uuid4().int & 0xFFFF)


_DECISION_COLS = (
    "decision_id, learner_id, ruleset_version, target_concept_id, action, "
    "delivery_mode, background_actions_json, reason_code, reason_or, "
    "needs_help, chapter_id, suggested_question_id, suggested_chunk_id, "
    "network, source, produced_by, created_at"
)


def _row_to_decision(row) -> Decision:
    return Decision(
        decision_id=row[0], learner_id=row[1], ruleset_version=row[2],
        target_concept_id=row[3], action=Action(row[4]),
        delivery_mode=DeliveryMode(row[5]),
        background_actions=[BackgroundAction(a) for a in json.loads(row[6])],
        reason_code=row[7], reason_or=row[8], needs_help=bool(row[9]),
        chapter_id=row[10] or "",
        suggested_question_id=row[11], suggested_chunk_id=row[12],
        network=NetworkState(row[13]), source=row[14] or "server",
        produced_by=row[15] or "server_engine", created_at=row[16] or 0,
    )


# --------------------------------------------------------------------------- #
# Learner repository
# --------------------------------------------------------------------------- #
class SqlLearnerRepository(LearnerRepository):
    def __init__(self, persistence: Persistence) -> None:
        self.p = persistence

    async def create_learner(self, profile: LearnerProfile, device_id: str) -> None:
        async with self.p.session() as s:
            await s.execute(
                text("INSERT OR IGNORE INTO devices (device_id, hardware_label, created_at) "
                     "VALUES (:did, :lbl, :ts)"),
                {"did": device_id, "lbl": "shared-android-low-end", "ts": profile.created_at},
            )
            # v2: one ACTIVE device per learner — clear the previous active link.
            await s.execute(
                text("UPDATE learner_profiles SET active_device_id = NULL "
                     "WHERE active_device_id = :did"),
                {"did": device_id},
            )
            await s.execute(
                text("INSERT INTO learner_profiles (learner_id, display_label, locale, "
                     "grade, subject, pin_hash, created_at, active_device_id) "
                     "VALUES (:lid, :lbl, :loc, :g, :sub, :pin, :ts, :did)"),
                {"lid": profile.learner_id, "lbl": profile.display_label,
                 "loc": profile.locale, "g": profile.grade, "sub": profile.subject,
                 "pin": profile.pin_verifier if hasattr(profile, "pin_verifier") else profile.pin_hash,
                 "ts": profile.created_at, "did": device_id},
            )
            await s.execute(
                text("INSERT INTO learner_devices (learner_id, device_id, status, first_seen_at, last_active_at) "
                     "VALUES (:lid, :did, 'active', :ts, :ts) "
                     "ON CONFLICT(learner_id, device_id) DO UPDATE SET "
                     "last_active_at = :ts, status = 'active'"),
                {"lid": profile.learner_id, "did": device_id, "ts": profile.created_at},
            )
            await s.commit()

    async def get_learner(self, learner_id: str) -> Optional[LearnerProfile]:
        async with self.p.session() as s:
            res = await s.execute(
                text("SELECT learner_id, display_label, locale, grade, subject, pin_hash, created_at "
                     "FROM learner_profiles WHERE learner_id = :lid"),
                {"lid": learner_id},
            )
            row = res.fetchone()
            if not row:
                return None
            return LearnerProfile(
                learner_id=row[0], display_label=row[1], locale=row[2],
                grade=row[3], subject=row[4], pin_verifier=row[5], created_at=row[6],
            )

    async def list_learners_on_device(self, device_id: str) -> list[LearnerProfile]:
        async with self.p.session() as s:
            res = await s.execute(
                text("SELECT lp.learner_id, lp.display_label, lp.locale, lp.grade, "
                     "lp.subject, lp.pin_hash, lp.created_at "
                     "FROM learner_profiles lp JOIN learner_devices ld "
                     "ON lp.learner_id = ld.learner_id "
                     "WHERE ld.device_id = :did AND ld.status = 'active' "
                     "ORDER BY lp.created_at"),
                {"did": device_id},
            )
            out = []
            for row in res.fetchall():
                out.append(LearnerProfile(
                    learner_id=row[0], display_label=row[1], locale=row[2],
                    grade=row[3], subject=row[4], pin_verifier=row[5], created_at=row[6],
                ))
            return out

    async def activate_learner_on_device(self, learner_id: str, device_id: str) -> None:
        async with self.p.session() as s:
            await s.execute(
                text("UPDATE learner_profiles SET active_device_id = NULL "
                     "WHERE active_device_id = :did"),
                {"did": device_id},
            )
            await s.execute(
                text("UPDATE learner_profiles SET active_device_id = :did "
                     "WHERE learner_id = :lid"),
                {"lid": learner_id, "did": device_id},
            )
            await s.execute(
                text("INSERT INTO learner_devices (learner_id, device_id, status, first_seen_at, last_active_at) "
                     "VALUES (:lid, :did, 'active', :ts, :ts) "
                     "ON CONFLICT(learner_id, device_id) DO UPDATE SET "
                     "last_active_at = :ts, status = 'active'"),
                {"lid": learner_id, "did": device_id, "ts": _now_ms()},
            )
            await s.commit()

    async def deactivate_learner_on_device(self, device_id: str) -> Optional[str]:
        async with self.p.session() as s:
            res = await s.execute(
                text("SELECT learner_id FROM learner_profiles WHERE active_device_id = :did"),
                {"did": device_id},
            )
            row = res.fetchone()
            await s.execute(
                text("UPDATE learner_profiles SET active_device_id = NULL "
                     "WHERE active_device_id = :did"),
                {"did": device_id},
            )
            await s.commit()
            return row[0] if row else None

    async def get_active_learner_on_device(self, device_id: str) -> Optional[LearnerProfile]:
        async with self.p.session() as s:
            res = await s.execute(
                text("SELECT learner_id, display_label, locale, grade, subject, pin_hash, created_at "
                     "FROM learner_profiles WHERE active_device_id = :did"),
                {"did": device_id},
            )
            row = res.fetchone()
            if not row:
                return None
            return LearnerProfile(
                learner_id=row[0], display_label=row[1], locale=row[2],
                grade=row[3], subject=row[4], pin_verifier=row[5], created_at=row[6],
            )

    async def is_learner_linked(self, learner_id: str, device_id: str) -> bool:
        async with self.p.session() as s:
            res = await s.execute(
                text("SELECT 1 FROM learner_devices "
                     "WHERE learner_id = :lid AND device_id = :did AND status = 'active'"),
                {"lid": learner_id, "did": device_id},
            )
            return res.fetchone() is not None


# --------------------------------------------------------------------------- #
# Device repository (keys, tokens, challenges)
# --------------------------------------------------------------------------- #
class SqlDeviceRepository(DeviceRepository):
    def __init__(self, persistence: Persistence) -> None:
        self.p = persistence

    async def register_device(self, device_id: str, hardware_label: str,
                              public_key_spki: str | None = None) -> None:
        async with self.p.session() as s:
            await s.execute(
                text("INSERT INTO devices (device_id, hardware_label, public_key_spki, "
                     "created_at, last_seen_at) VALUES (:did, :lbl, :pk, :ts, :ts) "
                     "ON CONFLICT(device_id) DO UPDATE SET "
                     "public_key_spki = COALESCE(excluded.public_key_spki, devices.public_key_spki), "
                     "last_seen_at = :ts"),
                {"did": device_id, "lbl": hardware_label, "pk": public_key_spki, "ts": _now_ms()},
            )
            await s.commit()

    async def get_public_key(self, device_id: str) -> Optional[str]:
        async with self.p.session() as s:
            res = await s.execute(
                text("SELECT public_key_spki FROM devices WHERE device_id = :did"),
                {"did": device_id},
            )
            row = res.fetchone()
            return row[0] if row else None

    async def is_revoked(self, device_id: str) -> bool:
        async with self.p.session() as s:
            res = await s.execute(
                text("SELECT revoked_at FROM devices WHERE device_id = :did"),
                {"did": device_id},
            )
            row = res.fetchone()
            return bool(row and row[0])

    async def revoke_device(self, device_id: str) -> None:
        """Mark the device revoked. Tokens are deliberately left intact so a
        revoked device gets the typed 403 DEVICE_REVOKED (client quarantines
        pending events) instead of a generic 401."""
        async with self.p.session() as s:
            await s.execute(
                text("UPDATE devices SET revoked_at = :ts WHERE device_id = :did"),
                {"did": device_id, "ts": _now_ms()},
            )
            await s.commit()

    async def touch_last_seen(self, device_id: str) -> None:
        async with self.p.session() as s:
            await s.execute(
                text("UPDATE devices SET last_seen_at = :ts WHERE device_id = :did"),
                {"did": device_id, "ts": _now_ms()},
            )
            await s.commit()

    # ---- access tokens ---------------------------------------------------
    async def issue_access_token(self, device_id: str, token_hash: str,
                                 issued_at: int, expires_at: int) -> None:
        """Issue an access token. Previous access tokens stay valid until
        their own expiry — a renewal must never strand an in-flight request
        (v2: AUTH_PENDING only when tokens genuinely expire)."""
        async with self.p.session() as s:
            await s.execute(
                text("INSERT INTO device_tokens (device_id, token_hash, issued_at, expires_at, revoked) "
                     "VALUES (:did, :h, :i, :e, 0)"),
                {"did": device_id, "h": token_hash, "i": issued_at, "e": expires_at},
            )
            await s.commit()

    async def verify_access_token(self, token_hash: str) -> Optional[tuple[str, int]]:
        """Return (device_id, expires_at) if the token is valid and unexpired.

        Revocation is deliberately NOT checked here: a revoked device must
        produce the typed 403 DEVICE_REVOKED (so the client quarantines
        pending events), not a generic 401."""
        async with self.p.session() as s:
            res = await s.execute(
                text("SELECT device_id, expires_at FROM device_tokens "
                     "WHERE token_hash = :h AND revoked = 0 AND expires_at > :now"),
                {"h": token_hash, "now": _now_ms()},
            )
            row = res.fetchone()
            return (row[0], row[1]) if row else None

    async def revoke_access_tokens(self, device_id: str) -> None:
        async with self.p.session() as s:
            await s.execute(
                text("UPDATE device_tokens SET revoked = 1 WHERE device_id = :did"),
                {"did": device_id},
            )
            await s.commit()

    # ---- refresh tokens ----------------------------------------------------
    async def issue_refresh_token(self, device_id: str, token_hash: str,
                                  issued_at: int, expires_at: int) -> str:
        rid = uuid.uuid4().hex
        async with self.p.session() as s:
            await s.execute(
                text("INSERT INTO refresh_tokens (id, device_id, token_hash, issued_at, "
                     "expires_at, revoked) VALUES (:id, :did, :h, :i, :e, 0)"),
                {"id": rid, "did": device_id, "h": token_hash,
                 "i": issued_at, "e": expires_at},
            )
            await s.commit()
        return rid

    async def consume_refresh_token(self, token_hash: str) -> Optional[str]:
        async with self.p.session() as s:
            res = await s.execute(
                text("SELECT id, device_id, expires_at, used_at, revoked FROM refresh_tokens "
                     "WHERE token_hash = :h"),
                {"h": token_hash},
            )
            row = res.fetchone()
            if not row or row[3] is not None or row[4]:
                return None
            if row[2] <= _now_ms():
                return None
            await s.execute(
                text("UPDATE refresh_tokens SET used_at = :now WHERE id = :id"),
                {"id": row[0], "now": _now_ms()},
            )
            await s.commit()
            return row[1]

    async def revoke_refresh_tokens(self, device_id: str) -> None:
        async with self.p.session() as s:
            await s.execute(
                text("UPDATE refresh_tokens SET revoked = 1 WHERE device_id = :did"),
                {"did": device_id},
            )
            await s.commit()

    # ---- challenges ----------------------------------------------------------
    async def store_challenge(self, device_id: str, nonce: str,
                              created_at: int, expires_at: int) -> None:
        async with self.p.session() as s:
            await s.execute(
                text("INSERT INTO auth_challenges (nonce, device_id, created_at, expires_at) "
                     "VALUES (:n, :did, :c, :e)"),
                {"n": nonce, "did": device_id, "c": created_at, "e": expires_at},
            )
            await s.commit()

    async def consume_challenge(self, device_id: str, nonce: str) -> bool:
        async with self.p.session() as s:
            res = await s.execute(
                text("SELECT expires_at, used_at FROM auth_challenges "
                     "WHERE nonce = :n AND device_id = :did"),
                {"n": nonce, "did": device_id},
            )
            row = res.fetchone()
            if not row or row[1] is not None or row[0] <= _now_ms():
                return False
            await s.execute(
                text("UPDATE auth_challenges SET used_at = :now WHERE nonce = :n"),
                {"n": nonce, "now": _now_ms()},
            )
            await s.commit()
            return True


# --------------------------------------------------------------------------- #
# Event repository — idempotent insert + tombstones + cursors
# --------------------------------------------------------------------------- #
_EVENT_SELECT = (
    "SELECT event_id, device_id, learner_id, seq, client_ts, event_type, "
    "concept_id, chapter_id, question_id, payload_json, status, effect, reason "
    "FROM learner_events"
)


def _row_to_event(row) -> LearnerEvent:
    return LearnerEvent(
        event_id=row[0], device_id=row[1], learner_id=row[2], seq=row[3],
        client_ts=row[4] or 0, event_type=row[5], concept_id=row[6],
        chapter_id=row[7], question_id=row[8],
        payload=json.loads(row[9] or "{}"),
    )


class SqlEventRepository(EventRepository):
    def __init__(self, persistence: Persistence) -> None:
        self.p = persistence

    async def insert_event(self, ev: LearnerEvent) -> PerEventResult:
        """Idempotent: (device_id, seq) is the unique key; (event_id) is also unique."""
        async with self.p.session() as s:
            result = await self._insert_event_session(s, ev)
            await s.commit()
            return result

    async def _insert_event_session(self, s: AsyncSession, ev: LearnerEvent) -> PerEventResult:
        existing = await s.execute(
            text("SELECT event_id, event_type, payload_json, status FROM learner_events "
                 "WHERE device_id = :did AND seq = :seq"),
            {"did": ev.device_id, "seq": ev.seq},
        )
        row = existing.fetchone()
        if row:
            if row[0] == ev.event_id:
                return PerEventResult(
                    event_id=ev.event_id, seq=ev.seq, outcome=Outcome.DUPLICATE,
                    detail="event already accepted (same event_id)")
            # Same (device_id, seq) with a DIFFERENT event_id or payload:
            # permanent PAYLOAD_CONFLICT (client bug or tampering).
            return PerEventResult(
                event_id=ev.event_id, seq=ev.seq, outcome=Outcome.REJECTED,
                effect=SyncEffect.NONE, reason=SyncReason.PAYLOAD_CONFLICT,
                detail="same (device_id, seq) stored with a different event_id/payload")
        existing_id = await s.execute(
            text("SELECT seq, status FROM learner_events WHERE event_id = :eid"),
            {"eid": ev.event_id},
        )
        row2 = existing_id.fetchone()
        if row2:
            return PerEventResult(
                event_id=ev.event_id, seq=ev.seq, outcome=Outcome.DUPLICATE,
                detail="event_id already accepted at a different seq")
        server_seq = _server_seq_next()
        await s.execute(
            text("INSERT INTO learner_events "
                 "(device_id, learner_id, seq, event_id, client_ts, event_type, "
                 " concept_id, chapter_id, question_id, payload_json, "
                 " status, received_at, server_seq) "
                 "VALUES (:did, :lid, :seq, :eid, :ts, :et, :cid, :chid, :qid, "
                 " :payload, 'accepted', :recv, :sseq)"),
            {"did": ev.device_id, "lid": ev.learner_id, "seq": ev.seq,
             "eid": ev.event_id, "ts": ev.client_ts, "et": ev.event_type.value
             if hasattr(ev.event_type, "value") else str(ev.event_type),
             "cid": ev.concept_id, "chid": ev.chapter_id, "qid": ev.question_id,
             "payload": json.dumps(ev.payload, ensure_ascii=False),
             "recv": _now_ms(), "sseq": server_seq},
        )
        return PerEventResult(event_id=ev.event_id, seq=ev.seq,
                              outcome=Outcome.ACCEPTED, detail="")

    async def insert_rejected_tombstone(self, ev: LearnerEvent, reason: str) -> None:
        """Rejected tombstone: consumes the (device, seq) slot, records
        diagnostics, never applies mastery effect. Idempotent. Both writes
        happen in ONE session (SQLite locks the whole file per write)."""
        async with self.p.session() as s:
            existing = await s.execute(
                text("SELECT event_id FROM learner_events WHERE device_id = :did AND seq = :seq"),
                {"did": ev.device_id, "seq": ev.seq},
            )
            if not existing.fetchone():
                await s.execute(
                    text("INSERT INTO learner_events "
                         "(device_id, learner_id, seq, event_id, client_ts, event_type, "
                         " concept_id, chapter_id, question_id, payload_json, "
                         " status, effect, reason, received_at, server_seq) "
                         "VALUES (:did, :lid, :seq, :eid, :ts, :et, :cid, :chid, :qid, "
                         " :payload, 'rejected', 'none', :reason, :recv, :sseq)"),
                    {"did": ev.device_id, "lid": ev.learner_id, "seq": ev.seq,
                     "eid": ev.event_id, "ts": ev.client_ts,
                     "et": ev.event_type.value if hasattr(ev.event_type, "value") else str(ev.event_type),
                     "cid": ev.concept_id, "chid": ev.chapter_id, "qid": ev.question_id,
                     "payload": json.dumps(ev.payload, ensure_ascii=False),
                     "reason": reason, "recv": _now_ms(), "sseq": _server_seq_next()},
                )
            await s.execute(
                text("INSERT OR REPLACE INTO dead_letter_events "
                     "(event_id, device_id, learner_id, seq, reason, last_error_code, "
                     " received_at, dead_at) VALUES (:eid, :did, :lid, :seq, :r, :ec, :recv, :now)"),
                {"eid": ev.event_id, "did": ev.device_id, "lid": ev.learner_id,
                 "seq": ev.seq, "r": reason, "ec": reason,
                 "recv": _now_ms(), "now": _now_ms()},
            )
            await s.commit()

    async def event_with_same_seq(self, device_id: str, seq: int) -> Optional[LearnerEvent]:
        async with self.p.session() as s:
            res = await s.execute(
                text(_EVENT_SELECT + " WHERE device_id = :did AND seq = :seq"),
                {"did": device_id, "seq": seq},
            )
            row = res.fetchone()
            return _row_to_event(row) if row else None

    async def list_events(self, learner_id: str, since_seq: int = 0,
                          limit: int = 1000) -> list[LearnerEvent]:
        """Accepted events in canonical order (seq ascending); rejected
        tombstones are skipped in replay."""
        async with self.p.session() as s:
            res = await s.execute(
                text(_EVENT_SELECT + " WHERE learner_id = :lid AND status = 'accepted' "
                     "AND server_seq > :ss ORDER BY seq, server_seq LIMIT :n"),
                {"lid": learner_id, "ss": since_seq, "n": limit},
            )
            return [_row_to_event(row) for row in res.fetchall()]

    async def learner_attempt_ids(self, learner_id: str) -> set[str]:
        async with self.p.session() as s:
            res = await s.execute(
                text("SELECT payload_json FROM learner_events "
                     "WHERE learner_id = :lid AND event_type = 'ANSWER_SUBMITTED' "
                     "AND status = 'accepted'"),
                {"lid": learner_id},
            )
            out = set()
            for (payload_json,) in res.fetchall():
                try:
                    aid = (json.loads(payload_json or "{}") or {}).get("attempt_id")
                except Exception:
                    aid = None
                if aid:
                    out.add(str(aid))
            return out

    async def get_sync_cursor(self, device_id: str, learner_id: str) -> tuple[int, int]:
        async with self.p.session() as s:
            res = await s.execute(
                text("SELECT last_acked_seq, last_server_seq FROM sync_cursors "
                     "WHERE device_id = :did AND learner_id = :lid"),
                {"did": device_id, "lid": learner_id},
            )
            row = res.fetchone()
            return (row[0], row[1]) if row else (0, 0)

    async def bump_sync_cursor(self, device_id: str, learner_id: str,
                                last_acked_seq: int, last_server_seq: int) -> None:
        async with self.p.session() as s:
            await s.execute(
                text("INSERT INTO sync_cursors (device_id, learner_id, last_acked_seq, "
                     "last_server_seq, last_acked_at) VALUES (:did, :lid, :s, :ss, :ts) "
                     "ON CONFLICT(device_id, learner_id) DO UPDATE SET "
                     " last_acked_seq = :s, last_server_seq = :ss, last_acked_at = :ts"),
                {"did": device_id, "lid": learner_id, "s": last_acked_seq,
                 "ss": last_server_seq, "ts": _now_ms()},
            )
            await s.commit()

    async def move_to_dead_letter(self, ev: LearnerEvent, reason: str,
                                    error_code: str) -> None:
        async with self.p.session() as s:
            await s.execute(
                text("INSERT OR REPLACE INTO dead_letter_events "
                     "(event_id, device_id, learner_id, seq, reason, last_error_code, "
                     " received_at, dead_at) VALUES (:eid, :did, :lid, :seq, :r, :ec, :recv, :now)"),
                {"eid": ev.event_id, "did": ev.device_id, "lid": ev.learner_id,
                 "seq": ev.seq, "r": reason, "ec": error_code,
                 "recv": _now_ms(), "now": _now_ms()},
            )
            await s.commit()


# --------------------------------------------------------------------------- #
# Mastery repository (integer basis points)
# --------------------------------------------------------------------------- #
class SqlMasteryRepository(MasteryRepository):
    def __init__(self, persistence: Persistence) -> None:
        self.p = persistence

    async def get_mastery(self, learner_id: str) -> list[MasteryRecord]:
        async with self.p.session() as s:
            res = await s.execute(
                text("SELECT concept_id, p_bp, band, attempts, correct, last_event_seq, bkt_version "
                     "FROM learner_progress WHERE learner_id = :lid"),
                {"lid": learner_id},
            )
            return [MasteryRecord(
                concept_id=row[0], p_bp=int(row[1] if row[1] is not None else 2000),
                band=row[2] or "weak",
                attempts=int(row[3] or 0), correct=int(row[4] or 0),
                last_event_seq=int(row[5] or 0),
            ) for row in res.fetchall()]

    async def upsert_mastery(self, learner_id: str, concept_id: str,
                              p_bp: int, band: str, attempts: int,
                              correct: int, last_event_seq: int,
                              bkt_version: str = "1") -> None:
        async with self.p.session() as s:
            await s.execute(
                text("INSERT INTO learner_progress (learner_id, concept_id, p_bp, bkt_version, band, "
                     "attempts, correct, last_event_seq) "
                     "VALUES (:lid, :cid, :p, :bv, :b, :a, :c, :seq) "
                     "ON CONFLICT(learner_id, concept_id) DO UPDATE SET "
                     " p_bp = :p, bkt_version = :bv, band = :b, attempts = :a, correct = :c, "
                     " last_event_seq = :seq"),
                {"lid": learner_id, "cid": concept_id, "p": int(p_bp),
                 "bv": bkt_version, "b": band, "a": attempts, "c": correct,
                 "seq": last_event_seq},
            )
            await s.commit()

    async def replace_mastery_snapshot(self, learner_id: str,
                                        snapshot: list[MasteryRecord]) -> None:
        """Used by sync_service after canonical replay — updates each concept
        row from the replayed event log (the event log is the source of truth)."""
        async with self.p.session() as s:
            for m in snapshot:
                await s.execute(
                    text("INSERT INTO learner_progress (learner_id, concept_id, p_bp, band, "
                         "attempts, correct, last_event_seq) "
                         "VALUES (:lid, :cid, :p, :b, :a, :c, :seq) "
                         "ON CONFLICT(learner_id, concept_id) DO UPDATE SET "
                         " p_bp = :p, band = :b, attempts = :a, correct = :c, "
                         " last_event_seq = :seq"),
                    {"lid": learner_id, "cid": m.concept_id, "p": int(m.p_bp),
                     "b": m.band, "a": m.attempts, "c": m.correct,
                     "seq": int(m.last_event_seq or 0)},
                )
            await s.commit()


# --------------------------------------------------------------------------- #
# Decision repository
# --------------------------------------------------------------------------- #
class SqlDecisionRepository(DecisionRepository):
    def __init__(self, persistence: Persistence) -> None:
        self.p = persistence

    async def save_decision(self, decision: Decision) -> None:
        async with self.p.session() as s:
            await s.execute(
                text("INSERT INTO decisions (decision_id, learner_id, ruleset_version, "
                     "target_concept_id, action, delivery_mode, background_actions_json, "
                     "reason_code, reason_or, needs_help, chapter_id, suggested_question_id, "
                     "suggested_chunk_id, network, source, produced_by, created_at) "
                     "VALUES (:did, :lid, :rv, :tcid, :a, :dm, :ba, :rc, :ro, :nh, :chid, :sq, :sc, :n, :src, :pb, :ts)"),
                {"did": decision.decision_id,
                 "lid": decision.learner_id or "",
                 "rv": decision.ruleset_version, "tcid": decision.target_concept_id,
                 "a": decision.action.value, "dm": decision.delivery_mode.value,
                 "ba": json.dumps([a.value for a in decision.background_actions]),
                 "rc": decision.reason_code, "ro": decision.reason_or,
                 "nh": 1 if decision.needs_help else 0,
                 "chid": decision.chapter_id,
                 "sq": decision.suggested_question_id,
                 "sc": decision.suggested_chunk_id,
                 "n": decision.network.value, "src": decision.source,
                 "pb": decision.produced_by,
                 "ts": decision.created_at or _now_ms()},
            )
            await s.commit()

    async def save_trace(self, decision_id: str, trace: DecisionTrace) -> None:
        async with self.p.session() as s:
            await s.execute(
                text("DELETE FROM decision_traces WHERE decision_id = :did"),
                {"did": decision_id},
            )
            for i, step in enumerate(trace.trace):
                await s.execute(
                    text("INSERT INTO decision_traces (decision_id, step_ordinal, step_id, "
                         "node, tool, provider, ruleset_version, model_id, status, "
                         "error_code, duration_ms, retry, fallback, input_summary_json, "
                         "output_summary_json, redacted) "
                         "VALUES (:did, :ord, :sid, :n, :t, :p, :rv, :m, :s, :ec, :d, :r, :f, :i, :o, :red)"),
                    {"did": decision_id, "ord": i, "sid": step.step_id, "n": step.node,
                     "t": step.tool, "p": step.provider,
                     "rv": step.ruleset_version, "m": step.model_id,
                     "s": step.status, "ec": step.error_code, "d": step.duration_ms,
                     "r": step.retry, "f": step.fallback,
                     "i": json.dumps(step.input_summary, ensure_ascii=False),
                     "o": json.dumps(step.output_summary, ensure_ascii=False),
                     "red": 1 if step.redacted else 0},
                )
            await s.commit()

    async def get_decision(self, decision_id: str) -> Optional[Decision]:
        async with self.p.session() as s:
            res = await s.execute(
                text(f"SELECT {_DECISION_COLS} FROM decisions WHERE decision_id = :did"),
                {"did": decision_id},
            )
            row = res.fetchone()
            return _row_to_decision(row) if row else None

    async def get_decision_for_learner(self, decision_id: str,
                                       learner_id: str) -> Optional[Decision]:
        async with self.p.session() as s:
            res = await s.execute(
                text(f"SELECT {_DECISION_COLS} FROM decisions "
                     "WHERE decision_id = :did AND learner_id = :lid"),
                {"did": decision_id, "lid": learner_id},
            )
            row = res.fetchone()
            return _row_to_decision(row) if row else None

    async def get_trace(self, decision_id: str) -> Optional[DecisionTrace]:
        async with self.p.session() as s:
            res = await s.execute(
                text("SELECT step_id, node, tool, provider, ruleset_version, model_id, "
                     "status, error_code, duration_ms, retry, fallback, "
                     "input_summary_json, output_summary_json, redacted "
                     "FROM decision_traces WHERE decision_id = :did ORDER BY step_ordinal"),
                {"did": decision_id},
            )
            steps = []
            for row in res.fetchall():
                steps.append(TraceStep(
                    step_id=row[0], node=row[1], tool=row[2], provider=row[3],
                    ruleset_version=row[4], model_id=row[5], status=row[6],
                    error_code=row[7], duration_ms=row[8], retry=row[9],
                    fallback=row[10],
                    input_summary=json.loads(row[11] or "{}"),
                    output_summary=json.loads(row[12] or "{}"),
                    redacted=bool(row[13]),
                ))
            if not steps:
                return None
            return DecisionTrace(decision_id=decision_id, trace=steps)

    async def list_recent_decisions(self, learner_id: str, limit: int = 10) -> list[Decision]:
        async with self.p.session() as s:
            res = await s.execute(
                text(f"SELECT {_DECISION_COLS} FROM decisions "
                     "WHERE learner_id = :lid ORDER BY created_at DESC LIMIT :n"),
                {"lid": learner_id, "n": limit},
            )
            return [_row_to_decision(row) for row in res.fetchall()]


# --------------------------------------------------------------------------- #
# Generation record repository (providers never write here directly —
# the orchestration/service layer persists the record after validation.)
# --------------------------------------------------------------------------- #
class SqlGenerationRecordRepository(GenerationRecordRepository):
    def __init__(self, persistence: Persistence) -> None:
        self.p = persistence

    async def save(self, record: GenerationRecord) -> None:
        async with self.p.session() as s:
            await s.execute(
                text("INSERT INTO generation_records (record_id, decision_id, provider, "
                     "model_id, prompt_version, prompt_hash, params_json, chunk_ids_json, "
                     "output_or, validation_results_json, fallback_used, created_at) "
                     "VALUES (:rid, :did, :p, :m, :pv, :ph, :params, :chunks, :out, :val, :fb, :ts)"),
                {"rid": record.record_id, "did": record.decision_id,
                 "p": record.provider, "m": record.model_id,
                 "pv": record.prompt_version, "ph": record.prompt_hash,
                 "params": json.dumps(record.params, ensure_ascii=False),
                 "chunks": json.dumps(record.chunk_ids),
                 "out": record.output_or,
                 "val": json.dumps(record.validation_results, ensure_ascii=False),
                 "fb": 1 if record.fallback_used else 0,
                 "ts": record.created_at or _now_ms()},
            )
            await s.commit()

    async def list_for_decision(self, decision_id: str) -> list[GenerationRecord]:
        async with self.p.session() as s:
            res = await s.execute(
                text("SELECT record_id, decision_id, provider, model_id, prompt_version, "
                     "prompt_hash, params_json, chunk_ids_json, output_or, "
                     "validation_results_json, fallback_used, created_at "
                     "FROM generation_records WHERE decision_id = :did ORDER BY created_at"),
                {"did": decision_id},
            )
            return [GenerationRecord(
                record_id=r[0], decision_id=r[1], provider=r[2], model_id=r[3],
                prompt_version=r[4], prompt_hash=r[5],
                params=json.loads(r[6] or "{}"),
                chunk_ids=json.loads(r[7] or "[]"),
                output_or=r[8] or "",
                validation_results=json.loads(r[9] or "{}"),
                fallback_used=bool(r[10]), created_at=r[11] or 0,
            ) for r in res.fetchall()]


# --------------------------------------------------------------------------- #
# Pack repository
# --------------------------------------------------------------------------- #
class SqlPackRepository(PackRepository):
    def __init__(self, persistence: Persistence) -> None:
        self.p = persistence

    async def upsert_pack_manifest(self, manifest: PackManifest) -> None:
        async with self.p.session() as s:
            await s.execute(
                text("INSERT INTO packs (pack_id, version, content_version, language, "
                     "byte_size, checksum_sha256, min_app_version, licence, "
                     "source_refs_json, created_at, published) "
                     "VALUES (:pid, :v, :cv, :lng, :sz, :cs, :mv, :lc, :sr, :ts, 1) "
                     "ON CONFLICT(pack_id, version) DO UPDATE SET "
                     " content_version = :cv, byte_size = :sz, checksum_sha256 = :cs, "
                     " min_app_version = :mv, licence = :lc, source_refs_json = :sr, "
                     " created_at = :ts, published = 1"),
                {"pid": manifest.pack_id, "v": manifest.version,
                 "cv": manifest.content_version, "lng": manifest.language,
                 "sz": manifest.byte_size, "cs": manifest.checksum_sha256,
                 "mv": manifest.min_app_version, "lc": manifest.licence,
                 "sr": json.dumps(manifest.source_refs, ensure_ascii=False),
                 "ts": manifest.created_at},
            )
            for ch in manifest.chapters:
                await s.execute(
                    text("INSERT OR IGNORE INTO pack_chapters (pack_id, version, chapter_id) "
                         "VALUES (:pid, :v, :chid)"),
                    {"pid": manifest.pack_id, "v": manifest.version, "chid": ch},
                )
            await s.commit()

    async def list_pack_manifests(self) -> list[PackManifest]:
        async with self.p.session() as s:
            res = await s.execute(text(
                "SELECT pack_id, version, content_version, language, byte_size, "
                "checksum_sha256, min_app_version, licence, source_refs_json, created_at "
                "FROM packs WHERE published = 1 ORDER BY pack_id, version"))
            out = []
            for row in res.fetchall():
                ch_res = await s.execute(
                    text("SELECT chapter_id FROM pack_chapters WHERE pack_id = :pid AND version = :v"),
                    {"pid": row[0], "v": row[1]},
                )
                chapters = [r[0] for r in ch_res.fetchall()]
                out.append(PackManifest(
                    pack_id=row[0], version=row[1], content_version=row[2],
                    language=row[3], byte_size=row[4], checksum_sha256=row[5],
                    min_app_version=row[6], licence=row[7],
                    source_refs=json.loads(row[8] or "[]"),
                    created_at=row[9], chapters=chapters,
                ))
            return out

    async def get_pack_manifest(self, pack_id: str, version: str) -> Optional[PackManifest]:
        items = await self.list_pack_manifests()
        for m in items:
            if m.pack_id == pack_id and m.version == version:
                return m
        return None

    async def record_installed_pack(self, device_id: str, pack_id: str, version: str,
                                      byte_size: int, checksum: str) -> None:
        async with self.p.session() as s:
            await s.execute(
                text("INSERT OR REPLACE INTO installed_packs (device_id, pack_id, version, "
                     "installed_at, byte_size, checksum_sha256) "
                     "VALUES (:did, :pid, :v, :ts, :sz, :cs)"),
                {"did": device_id, "pid": pack_id, "v": version,
                 "ts": _now_ms(), "sz": byte_size, "cs": checksum},
            )
            await s.commit()

    async def list_installed_packs(self, device_id: str) -> list[tuple[str, str]]:
        async with self.p.session() as s:
            res = await s.execute(
                text("SELECT pack_id, version FROM installed_packs WHERE device_id = :did"),
                {"did": device_id},
            )
            return [(r[0], r[1]) for r in res.fetchall()]


__all__ = [
    "SqlLearnerRepository", "SqlDeviceRepository", "SqlEventRepository",
    "SqlMasteryRepository", "SqlDecisionRepository",
    "SqlGenerationRecordRepository", "SqlPackRepository",
]
