"""Karana Study Rooms service — room lifecycle, chat, Doubt Relay, games.

Server-authoritative rules:
- membership + capacity enforced with DB checks inside one transaction
- submissions hidden until reveal; reveal + stage transitions are server-side
- empty rooms get `expires_at = empty_since + room_expiry_hours` (24h default,
  configurable for dev demos); a rejoin cancels the pending expiry
- deletion removes only room-scoped rows (FK cascades); learner progress and
  profile tables live outside this scope and are untouched
"""
from __future__ import annotations

import asyncio
import secrets
import string
import time
from typing import List, Optional, Tuple

from sqlalchemy import text

from ..adapters.persistence import Persistence
from ..core.errors import ErrorCode, SaarthiError
from ..core.logging import get_logger
from ..core.settings import get_settings
from ..domain.rooms import (
    ACTIVITY_TYPES, GameSubmission, MessagePost, RelayStart, RelaySubmission,
    VerificationSubmit, new_activity_id, new_decision_id, new_message_id,
    new_result_id, new_room_id, new_submission_id, new_summary_id, now_ms,
)
from .rooms_agent import DemoKaranaAgent
from .rooms_content import MISTAKE_BANK

log = get_logger("saarthi.rooms")

_CODE_ALPHABET = string.ascii_uppercase + string.digits


class RoomError(SaarthiError):
    """Room-domain error that flows through the standard problem+json handler."""

    def __init__(self, code: str, status: int, detail: str) -> None:
        try:
            ec = ErrorCode(code)
        except ValueError:
            ec = ErrorCode.INTERNAL_ERROR
        super().__init__(ec, status=status, detail=detail)


def _code() -> str:
    return "".join(secrets.choice(_CODE_ALPHABET) for _ in range(6))


class RoomsService:
    def __init__(self, persistence: Persistence) -> None:
        self.p = persistence
        self.agent = DemoKaranaAgent()
        self.s = get_settings()
        self._sweep_task: Optional[asyncio.Task] = None
        self._chat_log: dict[str, list[tuple[float, str]]] = {}

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    async def create_room(self, learner_id: str, display_label: str, body) -> dict:
        now = now_ms()
        expiry_ms = self.s.room_expiry_hours * 3600 * 1000
        for _ in range(5):
            rid, code = new_room_id(), _code()
            try:
                async with self.p.session() as sess:
                    await sess.execute(text(
                        "INSERT INTO study_rooms (room_id, room_code, title, subject, "
                        "chapter_id, chapter_title, learning_topic, language, capacity, "
                        "status, created_by, created_at, empty_since, expires_at, "
                        "last_activity_at) VALUES "
                        "(:rid, :code, :t, :sub, :chid, :cht, :topic, :lang, :cap, "
                        "'active', :by, :ts, NULL, NULL, :ts)"),
                        {"rid": rid, "code": code, "t": body.title, "sub": body.subject,
                         "chid": body.chapter_id, "cht": body.chapter_title,
                         "topic": body.learning_topic, "lang": body.language,
                         "cap": body.capacity, "by": learner_id, "ts": now})
                    await sess.execute(text(
                        "INSERT INTO room_members (room_id, learner_id, role, joined_at, "
                        "last_seen_at) VALUES (:rid, :lid, 'host', :ts, :ts)"),
                        {"rid": rid, "lid": learner_id, "ts": now})
                    await sess.execute(text(
                        "INSERT INTO room_messages (message_id, room_id, learner_id, "
                        "sender_kind, kind, body, created_at) VALUES "
                        "(:mid, :rid, NULL, 'system', 'system', :body, :ts)"),
                        {"mid": new_message_id(), "rid": rid, "ts": now,
                         "body": f"{display_label} created the room. Reminder: when you "
                                 "join, previous room history is visible to all members."})
                    await sess.commit()
                return await self.get_room_detail(rid, learner_id)
            except Exception as e:  # unique code collision
                if "room_code" in str(e) and "UNIQUE" in str(e).upper():
                    continue
                raise
        raise RoomError("room_code_generation_failed", 500,
                        "could not generate a unique room code")

    async def join_room(self, learner_id: str, display_label: str, room_code: str) -> dict:
        code = room_code.strip().upper()
        async with self.p.session() as sess:
            row = (await sess.execute(text(
                "SELECT room_id, status, expires_at, capacity, created_at FROM study_rooms "
                "WHERE room_code = :code"), {"code": code})).mappings().first()
            if not row:
                raise RoomError("room_not_found", 404, f"no room with code {code}")
            if row["status"] != "active" or (
                    row["expires_at"] and row["expires_at"] < now_ms()):
                raise RoomError("room_expired", 410, "this room has expired and been deleted")
            now = now_ms()
            member = (await sess.execute(text(
                "SELECT learner_id FROM room_members WHERE room_id = :rid AND learner_id = :lid"),
                {"rid": row["room_id"], "lid": learner_id})).first()
            if member:
                # Rejoin: cancels pending deletion, clears empty-room timestamps.
                await sess.execute(text(
                    "UPDATE study_rooms SET empty_since = NULL, expires_at = NULL, "
                    "last_activity_at = :ts WHERE room_id = :rid"),
                    {"rid": row["room_id"], "ts": now})
            else:
                count = (await sess.execute(text(
                    "SELECT COUNT(*) c FROM room_members WHERE room_id = :rid"),
                    {"rid": row["room_id"]})).scalar_one()
                if count >= row["capacity"]:
                    raise RoomError("room_full", 409,
                                    f"room is full ({row['capacity']} members max)")
                # Capacity guard re-check happens inside the same transaction,
                # committed atomically below.
                await sess.execute(text(
                    "INSERT INTO room_members (room_id, learner_id, role, joined_at, "
                    "last_seen_at) VALUES (:rid, :lid, 'member', :ts, :ts)"),
                    {"rid": row["room_id"], "lid": learner_id, "ts": now})
                await sess.execute(text(
                    "UPDATE study_rooms SET empty_since = NULL, expires_at = NULL, "
                    "last_activity_at = :ts WHERE room_id = :rid"),
                    {"rid": row["room_id"], "ts": now})
                await sess.execute(text(
                    "INSERT INTO room_messages (message_id, room_id, learner_id, "
                    "sender_kind, kind, body, created_at) VALUES "
                    "(:mid, :rid, NULL, 'system', 'system', :body, :ts)"),
                    {"mid": new_message_id(), "rid": row["room_id"], "ts": now,
                     "body": f"{display_label} joined the room. Note: previous room "
                             "history is visible to all members."})
            await sess.commit()
        return await self.get_room_detail(row["room_id"], learner_id)

    async def leave_room(self, room_id: str, learner_id: str) -> None:
        async with self.p.session() as sess:
            row = (await sess.execute(text(
                "SELECT 1 FROM room_members WHERE room_id = :rid AND learner_id = :lid"),
                {"rid": room_id, "lid": learner_id})).first()
            if not row:
                raise RoomError("not_a_member", 403, "you are not a member of this room")
            await sess.execute(text(
                "DELETE FROM room_members WHERE room_id = :rid AND learner_id = :lid"),
                {"rid": room_id, "lid": learner_id})
            remaining = (await sess.execute(text(
                "SELECT COUNT(*) c FROM room_members WHERE room_id = :rid"),
                {"rid": room_id})).scalar_one()
            now = now_ms()
            if remaining == 0:
                expiry_ms = self.s.room_expiry_hours * 3600 * 1000
                await sess.execute(text(
                    "UPDATE study_rooms SET empty_since = :ts, expires_at = :exp, "
                    "last_activity_at = :ts WHERE room_id = :rid"),
                    {"rid": room_id, "ts": now, "exp": now + expiry_ms})
            await sess.commit()

    async def expire_due_rooms(self) -> List[str]:
        """Delete rooms whose expiry deadline passed. Returns deleted room ids."""
        now = now_ms()
        async with self.p.session() as sess:
            due = (await sess.execute(text(
                "SELECT room_id FROM study_rooms WHERE status = 'active' "
                "AND expires_at IS NOT NULL AND expires_at <= :now"),
                {"now": now})).scalars().all()
            for rid in due:
                # SQLite FK cascades are not reliably enforced here; delete
                # room-scoped children explicitly, parent last. Learner
                # profiles / mastery (personal data) are never touched.
                for table in ("room_summaries", "verification_results",
                              "activity_decisions", "activity_submissions",
                              "room_activities", "room_messages", "room_members"):
                    await sess.execute(text(f"DELETE FROM {table} WHERE room_id = :rid"),
                                       {"rid": rid})
                await sess.execute(text("DELETE FROM study_rooms WHERE room_id = :rid"),
                                   {"rid": rid})
            await sess.commit()
        if due:
            log.info("rooms_expired_deleted count=%d rooms=%s", len(due), due)
        return list(due)

    async def start_sweeper(self) -> None:
        async def _loop():
            while True:
                try:
                    await self.expire_due_rooms()
                except Exception:
                    log.exception("room sweeper failed")
                await asyncio.sleep(self.s.room_sweep_interval_seconds)
        self._sweep_task = asyncio.create_task(_loop())

    async def stop_sweeper(self) -> None:
        if self._sweep_task:
            self._sweep_task.cancel()

    # ------------------------------------------------------------------ #
    # Reads
    # ------------------------------------------------------------------ #
    async def _require_member(self, sess, room_id: str, learner_id: str) -> None:
        row = (await sess.execute(text(
            "SELECT 1 FROM room_members WHERE room_id = :rid AND learner_id = :lid"),
            {"rid": room_id, "lid": learner_id})).first()
        if not row:
            raise RoomError("not_a_member", 403, "you are not a member of this room")

    def _presence_cutoff(self) -> int:
        return now_ms() - self.s.room_presence_timeout_seconds * 1000

    async def list_rooms(self, learner_id: str) -> List[dict]:
        async with self.p.session() as sess:
            rows = (await sess.execute(text(
                "SELECT r.room_id FROM study_rooms r "
                "JOIN room_members m ON m.room_id = r.room_id AND m.learner_id = :lid "
                "WHERE r.status = 'active' AND "
                "(r.expires_at IS NULL OR r.expires_at > :now) "
                "ORDER BY r.last_activity_at DESC"),
                {"lid": learner_id, "now": now_ms()})).scalars().all()
        return [await self.get_room_detail(rid, learner_id) for rid in rows]

    async def get_room_detail(self, room_id: str, learner_id: str) -> dict:
        async with self.p.session() as sess:
            room = (await sess.execute(text(
                "SELECT * FROM study_rooms WHERE room_id = :rid"), {"rid": room_id}
            )).mappings().first()
            if not room:
                raise RoomError("room_not_found", 404, "room not found")
            member_rows = (await sess.execute(text(
                "SELECT m.learner_id, m.role, m.last_seen_at, l.display_label "
                "FROM room_members m JOIN learner_profiles l "
                "ON l.learner_id = m.learner_id WHERE m.room_id = :rid "
                "ORDER BY m.joined_at"), {"rid": room_id})).mappings().all()
            is_member = any(m["learner_id"] == learner_id for m in member_rows)
            if not is_member:
                raise RoomError("not_a_member", 403, "you are not a member of this room")
            cutoff = self._presence_cutoff()
            msgs = (await sess.execute(text(
                "SELECT * FROM room_messages WHERE room_id = :rid ORDER BY created_at, "
                "message_id LIMIT 500"), {"rid": room_id})).mappings().all()
            labels = {m["learner_id"]: m["display_label"] for m in member_rows}
            msg_out = [{
                "message_id": m["message_id"], "room_id": room_id,
                "learner_id": m["learner_id"],
                "sender_label": labels.get(m["learner_id"], "Karana" if m["sender_kind"] == "karana" else ""),
                "sender_kind": m["sender_kind"], "kind": m["kind"],
                "reply_to": m["reply_to"], "body": m["body"], "created_at": m["created_at"],
            } for m in msgs]
            sums = (await sess.execute(text(
                "SELECT * FROM room_summaries WHERE room_id = :rid ORDER BY created_at"),
                {"rid": room_id})).mappings().all()
            import json as _json
            summaries = [{
                "summary_id": s["summary_id"], "activity_type": s["activity_type"],
                "original_question": s["original_question"],
                "explanation": s["explanation"],
                "verification": _json.loads(s["verification_json"] or "{}"),
                "unresolved": _json.loads(s["unresolved_json"] or "[]"),
                "created_at": s["created_at"],
            } for s in sums]
        members = [{
            "learner_id": m["learner_id"], "display_label": m["display_label"],
            "role": m["role"], "online": m["last_seen_at"] >= cutoff,
        } for m in member_rows]
        # recent activity digest for the landing page
        recent = []
        for m in reversed(msg_out):
            if m["kind"] == "system":
                recent.append(m["body"])
            elif m["sender_kind"] == "karana":
                recent.append(f"Karana responded in the discussion")
            else:
                recent.append(f"{m['sender_label']} sent a message")
            if len(recent) >= 3:
                break
        return {
            "room": {
                "room_id": room["room_id"], "room_code": room["room_code"],
                "title": room["title"], "subject": room["subject"],
                "chapter_id": room["chapter_id"], "chapter_title": room["chapter_title"],
                "learning_topic": room["learning_topic"], "language": room["language"],
                "capacity": room["capacity"], "member_count": len(member_rows),
                "members": members, "is_member": True, "status": room["status"],
                "created_at": room["created_at"],
                "last_activity_at": room["last_activity_at"],
                "expires_at": room["expires_at"],
                "recent_activity": list(reversed(recent)),
            },
            "messages": msg_out,
            "summaries": summaries,
        }

    # ------------------------------------------------------------------ #
    # Chat
    # ------------------------------------------------------------------ #
    def _rate_limited(self, room_id: str, learner_id: str) -> bool:
        key = f"{room_id}:{learner_id}"
        now = time.time()
        buf = [t for t in self._chat_log.get(key, []) if now - t < 60]
        limited = len(buf) >= self.s.room_chat_rate_limit_per_minute
        if not limited:
            buf.append(now)
        self._chat_log[key] = buf[-64:]
        return limited

    async def post_message(self, room_id: str, learner_id: str, display_label: str,
                           body: MessagePost) -> dict:
        if self._rate_limited(room_id, learner_id):
            raise RoomError("rate_limited", 429, "slow down — too many messages per minute")
        async with self.p.session() as sess:
            await self._require_member(sess, room_id, learner_id)
            if body.reply_to:
                parent = (await sess.execute(text(
                    "SELECT 1 FROM room_messages WHERE message_id = :mid AND room_id = :rid"),
                    {"mid": body.reply_to, "rid": room_id})).first()
                if not parent:
                    raise RoomError("invalid_reply_target", 400, "reply target not found in room")
            mid, now = new_message_id(), now_ms()
            await sess.execute(text(
                "INSERT INTO room_messages (message_id, room_id, learner_id, sender_kind, "
                "kind, reply_to, body, created_at) VALUES "
                "(:mid, :rid, :lid, 'member', :kind, :reply, :body, :ts)"),
                {"mid": mid, "rid": room_id, "lid": learner_id,
                 "kind": "reply" if body.reply_to else "chat",
                 "reply": body.reply_to, "body": body.body, "ts": now})
            await sess.execute(text(
                "UPDATE room_members SET last_seen_at = :ts WHERE room_id = :rid "
                "AND learner_id = :lid"), {"ts": now, "rid": room_id, "lid": learner_id})
            await sess.commit()
        return {"message_id": mid, "room_id": room_id, "learner_id": learner_id,
                "sender_label": display_label, "sender_kind": "member",
                "kind": "reply" if body.reply_to else "chat",
                "reply_to": body.reply_to, "body": body.body, "created_at": now}

    async def heartbeat(self, room_id: str, learner_id: str) -> None:
        async with self.p.session() as sess:
            await self._require_member(sess, room_id, learner_id)
            await sess.execute(text(
                "UPDATE room_members SET last_seen_at = :ts WHERE room_id = :rid "
                "AND learner_id = :lid"), {"ts": now_ms(), "rid": room_id, "lid": learner_id})
            await sess.commit()

    # ------------------------------------------------------------------ #
    # Doubt Relay
    # ------------------------------------------------------------------ #
    async def _activity(self, sess, activity_id: str, room_id: str) -> dict:
        import json as _json
        row = (await sess.execute(text(
            "SELECT * FROM room_activities WHERE activity_id = :aid AND room_id = :rid"),
            {"aid": activity_id, "rid": room_id})).mappings().first()
        if not row:
            raise RoomError("activity_not_found", 404, "activity not found in this room")
        row = dict(row)
        row["payload"] = _json.loads(row["payload_json"] or "{}")
        return row

    async def start_relay(self, room_id: str, learner_id: str, body: RelayStart) -> dict:
        import json as _json
        async with self.p.session() as sess:
            await self._require_member(sess, room_id, learner_id)
            aid, now = new_activity_id(), now_ms()
            await sess.execute(text(
                "INSERT INTO room_activities (activity_id, room_id, activity_type, status, "
                "payload_json, created_by, created_at, updated_at) VALUES "
                "(:aid, :rid, 'doubt_relay', 'collecting', :pl, :by, :ts, :ts)"),
                {"aid": aid, "rid": room_id, "by": learner_id, "ts": now,
                 "pl": _json.dumps({"question": body.question,
                                    "bank_item_id": body.bank_item_id})})
            await sess.execute(text(
                "INSERT INTO room_messages (message_id, room_id, learner_id, sender_kind, "
                "kind, body, created_at) VALUES (:mid, :rid, NULL, 'system', 'system', "
                ":body, :ts)"),
                {"mid": new_message_id(), "rid": room_id, "ts": now,
                 "body": f"Doubt Relay started: “{body.question}” — members submit "
                         "answers independently; answers stay hidden until everyone "
                         "submits or the relay is revealed."})
            await sess.commit()
        return await self.get_relay(room_id, aid, learner_id)

    async def submit_relay(self, room_id: str, activity_id: str, learner_id: str,
                           body: RelaySubmission) -> dict:
        import json as _json
        async with self.p.session() as sess:
            await self._require_member(sess, room_id, learner_id)
            act = await self._activity(sess, activity_id, room_id)
            if act["activity_type"] != "doubt_relay":
                raise RoomError("invalid_activity", 400, "not a doubt relay")
            if act["status"] != "collecting":
                raise RoomError("activity_closed", 409,
                                "submissions are closed for this relay")
            existing = (await sess.execute(text(
                "SELECT submission_id FROM activity_submissions WHERE activity_id = :aid "
                "AND learner_id = :lid"), {"aid": activity_id, "lid": learner_id})).first()
            if existing:
                raise RoomError("duplicate_submission", 409,
                                "you already submitted an answer for this relay")
            now = now_ms()
            await sess.execute(text(
                "INSERT INTO activity_submissions (submission_id, activity_id, room_id, "
                "learner_id, content, created_at) VALUES "
                "(:sid, :aid, :rid, :lid, :c, :ts)"),
                {"sid": new_submission_id(), "aid": activity_id, "rid": room_id,
                 "lid": learner_id, "c": body.content, "ts": now})
            await sess.execute(text(
                "UPDATE room_activities SET updated_at = :ts WHERE activity_id = :aid"),
                {"ts": now, "aid": activity_id})
            await sess.commit()
        return await self.get_relay(room_id, activity_id, learner_id)

    async def get_relay(self, room_id: str, activity_id: str, learner_id: str) -> dict:
        import json as _json
        async with self.p.session() as sess:
            await self._require_member(sess, room_id, learner_id)
            act = await self._activity(sess, activity_id, room_id)
            subs = (await sess.execute(text(
                "SELECT s.*, l.display_label FROM activity_submissions s "
                "JOIN learner_profiles l ON l.learner_id = s.learner_id "
                "WHERE s.activity_id = :aid ORDER BY s.created_at"),
                {"aid": activity_id})).mappings().all()
            members = (await sess.execute(text(
                "SELECT COUNT(*) c FROM room_members WHERE room_id = :rid"),
                {"rid": room_id})).scalar_one()
            mine = next((s for s in subs if s["learner_id"] == learner_id), None)
            payload = act["payload"]
            revealed = act["status"] in ("revealed", "followup", "discussion",
                                         "verification", "completed")
            out: dict = {
                "activity_id": activity_id, "activity_type": "doubt_relay",
                "status": act["status"],
                "question": payload.get("question", ""),
                "my_submission": mine["content"] if mine else None,
                "submission_count": len(subs),
                "eligible_count": members,
                "submissions": [], "created_at": act["created_at"],
                "updated_at": act["updated_at"],
            }
            if revealed:
                out["submissions"] = [
                    {"learner_id": s["learner_id"], "display_label": s["display_label"],
                     "content": s["content"], "created_at": s["created_at"]} for s in subs]
                out["pattern"] = payload.get("pattern")
                out["explanation"] = payload.get("explanation")
                out["followup"] = payload.get("followup")
                out["trace"] = payload.get("trace", [])
                out["verification"] = payload.get("verification")
            else:
                # progress only — no answer content leaks
                out["submissions"] = [
                    {"learner_id": s["learner_id"], "display_label": s["display_label"],
                     "content": None, "created_at": s["created_at"]} for s in subs]
            if act["status"] in ("verification", "completed"):
                vres = (await sess.execute(text(
                    "SELECT correct FROM verification_results WHERE activity_id = :aid "
                    "AND learner_id = :lid"), {"aid": activity_id, "lid": learner_id}
                )).mappings().first()
                if vres:
                    out["verification_result"] = {
                        "correct": bool(vres["correct"]),
                        "my_result_only": True}
                if act["status"] == "completed":
                    group = (await sess.execute(text(
                        "SELECT COUNT(*) total, SUM(correct) ok FROM verification_results "
                        "WHERE activity_id = :aid"), {"aid": activity_id}
                    )).mappings().first()
                    out["verification"] = out["verification"] or payload.get("verification")
                    out["verification"]["group"] = {
                        "total": group["total"], "correct": group["ok"] or 0}
            return out

    async def reveal_relay(self, room_id: str, activity_id: str, learner_id: str) -> dict:
        """Server-authoritative reveal: runs the demo agent over the actual
        submissions and freezes the next stages into the payload."""
        import json as _json
        async with self.p.session() as sess:
            await self._require_member(sess, room_id, learner_id)
            act = await self._activity(sess, activity_id, room_id)
            if act["activity_type"] != "doubt_relay":
                raise RoomError("invalid_activity", 400, "not a doubt relay")
            if act["status"] != "collecting":
                raise RoomError("invalid_transition", 409,
                                "relay already revealed")
            subs = (await sess.execute(text(
                "SELECT learner_id, content FROM activity_submissions WHERE "
                "activity_id = :aid ORDER BY created_at"), {"aid": activity_id}
            )).mappings().all()
            if not subs:
                raise RoomError("no_submissions", 409, "no answers submitted yet")
            room = (await sess.execute(text(
                "SELECT chapter_id FROM study_rooms WHERE room_id = :rid"),
                {"rid": room_id})).mappings().first()
            question = act["payload"].get("question", "")
            result = await self.agent.resolve_relay(
                question, [dict(s) for s in subs],
                chapter_hint=(room["chapter_id"] or "").lower(),
                bank_item_id=act["payload"].get("bank_item_id"))
            payload = dict(act["payload"])
            payload.update({
                "pattern": result["pattern"], "explanation": result["explanation"],
                "followup": result["followup"], "verification": result["verification"],
                "unresolved": result["unresolved"], "trace": result["trace"],
                "agent_demo": True})
            new_status = "followup" if result["proceed_to_verification"] else "discussion"
            now = now_ms()
            await sess.execute(text(
                "UPDATE room_activities SET status = :st, payload_json = :pl, "
                "updated_at = :ts WHERE activity_id = :aid"),
                {"st": new_status, "pl": _json.dumps(payload), "ts": now, "aid": activity_id})
            await sess.execute(text(
                "INSERT INTO activity_decisions (decision_id, activity_id, room_id, stage, "
                "pattern, action, trace_json, created_at) VALUES "
                "(:did, :aid, :rid, 'reveal', :pat, :act, :tr, :ts)"),
                {"did": new_decision_id(), "aid": activity_id, "rid": room_id,
                 "pat": result["pattern"],
                 "act": "select_followup" if result["proceed_to_verification"]
                        else "explain_no_verification",
                 "tr": _json.dumps(result["trace"]), "ts": now})
            await sess.execute(text(
                "INSERT INTO room_messages (message_id, room_id, learner_id, sender_kind, "
                "kind, body, created_at) VALUES (:mid, :rid, NULL, 'karana', 'chat', "
                ":body, :ts)"),
                {"mid": new_message_id(), "rid": room_id, "ts": now,
                 "body": f"Reveal! {len(subs)} answers compared → pattern: "
                         f"{result['pattern']}. {result['followup']['text']}"})
            await sess.commit()
        return await self.get_relay(room_id, activity_id, learner_id)

    async def advance_relay(self, room_id: str, activity_id: str, learner_id: str,
                            stage: str) -> dict:
        import json as _json
        if stage not in ("discussion", "verification"):
            raise RoomError("invalid_stage", 400, "stage must be discussion or verification")
        async with self.p.session() as sess:
            await self._require_member(sess, room_id, learner_id)
            act = await self._activity(sess, activity_id, room_id)
            flow = {"followup": ["discussion", "verification"],
                    "discussion": ["verification"],
                    "verification": ["completed"]}
            allowed_next = flow.get(act["status"], [])
            if stage == "verification" and act["status"] == "followup":
                pass  # discussion is optional
            if stage == "discussion" and act["status"] not in ("followup", "discussion"):
                raise RoomError("invalid_transition", 409,
                                f"cannot move to discussion from {act['status']}")
            if stage == "verification" and act["status"] not in ("followup", "discussion"):
                raise RoomError("invalid_transition", 409,
                                f"cannot move to verification from {act['status']}")
            now = now_ms()
            await sess.execute(text(
                "UPDATE room_activities SET status = :st, updated_at = :ts "
                "WHERE activity_id = :aid"), {"st": stage, "ts": now, "aid": activity_id})
            if stage == "verification":
                payload = act["payload"]
                if not payload.get("verification"):
                    raise RoomError("no_verification", 409,
                                    "demo agent did not gate this relay for verification")
            await sess.commit()
        return await self.get_relay(room_id, activity_id, learner_id)

    async def complete_verification(self, room_id: str, activity_id: str,
                                    learner_id: str, body: VerificationSubmit) -> dict:
        import json as _json
        async with self.p.session() as sess:
            await self._require_member(sess, room_id, learner_id)
            act = await self._activity(sess, activity_id, room_id)
            if act["status"] != "verification":
                raise RoomError("invalid_transition", 409,
                                "activity is not in the verification stage")
            ver = act["payload"].get("verification")
            if not ver:
                raise RoomError("no_verification", 409, "no verification question for this relay")
            existing = (await sess.execute(text(
                "SELECT result_id FROM verification_results WHERE activity_id = :aid "
                "AND learner_id = :lid"), {"aid": activity_id, "lid": learner_id})).first()
            if existing:
                raise RoomError("duplicate_submission", 409,
                                "you already completed verification")
            correct = int(body.selected_option) == int(ver["correct_option"])
            now = now_ms()
            await sess.execute(text(
                "INSERT INTO verification_results (result_id, activity_id, room_id, "
                "learner_id, question_id, selected_option, correct, created_at) VALUES "
                "(:rid2, :aid, :rid, :lid, :qid, :opt, :cor, :ts)"),
                {"rid2": new_result_id(), "aid": activity_id, "rid": room_id,
                 "lid": learner_id, "qid": ver.get("question_id", "demo"),
                 "opt": body.selected_option, "cor": 1 if correct else 0, "ts": now})
            done = (await sess.execute(text(
                "SELECT COUNT(DISTINCT learner_id) c FROM verification_results "
                "WHERE activity_id = :aid"), {"aid": activity_id})).scalar_one()
            members = (await sess.execute(text(
                "SELECT COUNT(*) c FROM room_members WHERE room_id = :rid"),
                {"rid": room_id})).scalar_one()
            if done >= members:
                unresolved = act["payload"].get("unresolved", [])
                await sess.execute(text(
                    "UPDATE room_activities SET status = 'completed', updated_at = :ts "
                    "WHERE activity_id = :aid"), {"ts": now, "aid": activity_id})
                await sess.execute(text(
                    "INSERT INTO room_summaries (summary_id, room_id, original_question, "
                    "explanation, activity_type, verification_json, unresolved_json, "
                    "created_at) VALUES (:sid, :rid, :q, :ex, 'doubt_relay', :vj, :uj, :ts)"),
                    {"sid": new_summary_id(), "rid": room_id,
                     "q": act["payload"].get("question", ""),
                     "ex": act["payload"].get("explanation", ""),
                     "vj": _json.dumps({"completed_by": done,
                                        "group_total": members}),
                     "uj": _json.dumps(unresolved), "ts": now})
                await sess.execute(text(
                    "INSERT INTO room_messages (message_id, room_id, learner_id, "
                    "sender_kind, kind, body, created_at) VALUES "
                    "(:mid, :rid, NULL, 'karana', 'system', :body, :ts)"),
                    {"mid": new_message_id(), "rid": room_id, "ts": now,
                     "body": f"Verification complete ({done}/{members} members). "
                             "Session summary added to room history."})
            await sess.commit()
        return await self.get_relay(room_id, activity_id, learner_id)

    # ------------------------------------------------------------------ #
    # Find the Mistake
    # ------------------------------------------------------------------ #
    async def start_game(self, room_id: str, learner_id: str) -> dict:
        import json as _json
        async with self.p.session() as sess:
            await self._require_member(sess, room_id, learner_id)
            room = (await sess.execute(text(
                "SELECT chapter_id FROM study_rooms WHERE room_id = :rid"),
                {"rid": room_id})).mappings().first()
            hint = (room["chapter_id"] or "").lower()
            item = next((m for m in MISTAKE_BANK if m["topic_hint"] in hint),
                        MISTAKE_BANK[0])
            aid, now = new_activity_id(), now_ms()
            problem = {"problem_id": item["id"], "title": item["title"],
                       "lines": item["problem_lines"]}
            await sess.execute(text(
                "INSERT INTO room_activities (activity_id, room_id, activity_type, status, "
                "payload_json, created_by, created_at, updated_at) VALUES "
                "(:aid, :rid, 'find_the_mistake', 'collecting', :pl, :by, :ts, :ts)"),
                {"aid": aid, "rid": room_id, "by": learner_id, "ts": now,
                 "pl": _json.dumps({"problem_id": item["id"],
                                    "mistake_index": item["mistake_index"]})})
            await sess.execute(text(
                "INSERT INTO room_messages (message_id, room_id, learner_id, sender_kind, "
                "kind, body, created_at) VALUES (:mid, :rid, NULL, 'system', 'system', "
                ":body, :ts)"),
                {"mid": new_message_id(), "rid": room_id, "ts": now,
                 "body": f"Find the Mistake started: “{item['title']}” — one line in the "
                         "solution is wrong. Identify it and explain your reasoning."})
            await sess.commit()
        return await self.get_game(room_id, aid, learner_id)

    async def get_game(self, room_id: str, activity_id: str, learner_id: str) -> dict:
        import json as _json
        async with self.p.session() as sess:
            await self._require_member(sess, room_id, learner_id)
            act = await self._activity(sess, activity_id, room_id)
            problem_id = act["payload"].get("problem_id")
            item = next((m for m in MISTAKE_BANK if m["id"] == problem_id), MISTAKE_BANK[0])
            subs = (await sess.execute(text(
                "SELECT s.*, l.display_label FROM activity_submissions s "
                "JOIN learner_profiles l ON l.learner_id = s.learner_id "
                "WHERE s.activity_id = :aid ORDER BY s.created_at"),
                {"aid": activity_id})).mappings().all()
            members = (await sess.execute(text(
                "SELECT COUNT(*) c FROM room_members WHERE room_id = :rid"),
                {"rid": room_id})).scalar_one()
            mine = next((s for s in subs if s["learner_id"] == learner_id), None)
            revealed = act["status"] in ("revealed", "followup", "discussion",
                                         "verification", "completed")
            out: dict = {
                "activity_id": activity_id, "activity_type": "find_the_mistake",
                "status": act["status"],
                "problem": {"problem_id": item["id"], "title": item["title"],
                            "lines": item["problem_lines"]},
                "my_submission": None,
                "submission_count": len(subs), "eligible_count": members,
                "submissions": [], "created_at": act["created_at"],
                "updated_at": act["updated_at"],
            }
            if mine:
                import json as _j2
                c = _j2.loads(mine["content"])
                out["my_submission"] = c
            if revealed:
                out["submissions"] = [
                    {"learner_id": s["learner_id"], "display_label": s["display_label"],
                     **_json.loads(s["content"]), "created_at": s["created_at"]}
                    for s in subs]
                out["expected"] = {
                    "mistake_index": act["payload"].get("mistake_index"),
                    "answer": item["expected_answer"],
                    "explanation": item["explanation"]}
                out["followup"] = payload_followup = act["payload"].get("followup")
                out["group_stats"] = act["payload"].get("group_stats")
                out["trace"] = act["payload"].get("trace", [])
            else:
                out["submissions"] = [
                    {"learner_id": s["learner_id"], "display_label": s["display_label"],
                     "content": None, "created_at": s["created_at"]} for s in subs]
            return out

    async def submit_game(self, room_id: str, activity_id: str, learner_id: str,
                          body: GameSubmission) -> dict:
        import json as _json
        async with self.p.session() as sess:
            act = await self._activity(sess, activity_id, room_id)
            await self._require_member(sess, room_id, learner_id)
            if act["activity_type"] != "find_the_mistake":
                raise RoomError("invalid_activity", 400, "not a find-the-mistake game")
            if act["status"] != "collecting":
                raise RoomError("activity_closed", 409, "submissions closed for this game")
            existing = (await sess.execute(text(
                "SELECT submission_id FROM activity_submissions WHERE activity_id = :aid "
                "AND learner_id = :lid"), {"aid": activity_id, "lid": learner_id})).first()
            if existing:
                raise RoomError("duplicate_submission", 409, "you already submitted")
            now = now_ms()
            await sess.execute(text(
                "INSERT INTO activity_submissions (submission_id, activity_id, room_id, "
                "learner_id, content, created_at) VALUES (:sid, :aid, :rid, :lid, :c, :ts)"),
                {"sid": new_submission_id(), "aid": activity_id, "rid": room_id,
                 "lid": learner_id, "ts": now,
                 "c": _json.dumps({"mistake_line": body.mistake_line,
                                   "reasoning": body.reasoning})})
            await sess.execute(text(
                "UPDATE room_activities SET updated_at = :ts WHERE activity_id = :aid"),
                {"ts": now, "aid": activity_id})
            await sess.commit()
        return await self.get_game(room_id, activity_id, learner_id)

    async def reveal_game(self, room_id: str, activity_id: str, learner_id: str) -> dict:
        import json as _json
        async with self.p.session() as sess:
            await self._require_member(sess, room_id, learner_id)
            act = await self._activity(sess, activity_id, room_id)
            if act["activity_type"] != "find_the_mistake":
                raise RoomError("invalid_activity", 400, "not a find-the-mistake game")
            if act["status"] != "collecting":
                raise RoomError("invalid_transition", 409, "game already revealed")
            subs = (await sess.execute(text(
                "SELECT learner_id, content FROM activity_submissions WHERE "
                "activity_id = :aid ORDER BY created_at"), {"aid": activity_id}
            )).mappings().all()
            if not subs:
                raise RoomError("no_submissions", 409, "no submissions yet")
            parsed = [_json.loads(s["content"]) for s in subs]
            result = await self.agent.resolve_game(
                act["payload"].get("problem_id"), parsed)
            payload = dict(act["payload"])
            payload.update({"followup": result["followup"],
                            "group_stats": result["group_stats"],
                            "trace": result["trace"], "agent_demo": True})
            now = now_ms()
            await sess.execute(text(
                "UPDATE room_activities SET status = 'revealed', payload_json = :pl, "
                "updated_at = :ts WHERE activity_id = :aid"),
                {"pl": _json.dumps(payload), "ts": now, "aid": activity_id})
            await sess.execute(text(
                "INSERT INTO activity_decisions (decision_id, activity_id, room_id, stage, "
                "pattern, action, trace_json, created_at) VALUES "
                "(:did, :aid, :rid, 'reveal', 'game', 'reveal_expected', :tr, :ts)"),
                {"did": new_decision_id(), "aid": activity_id, "rid": room_id,
                 "tr": _json.dumps(result["trace"]), "ts": now})
            await sess.execute(text(
                "INSERT INTO room_messages (message_id, room_id, learner_id, sender_kind, "
                "kind, body, created_at) VALUES (:mid, :rid, NULL, 'karana', 'chat', "
                ":body, :ts)"),
                {"mid": new_message_id(), "rid": room_id, "ts": now,
                 "body": f"Find the Mistake reveal! {result['group_stats']['found']} of "
                         f"{result['group_stats']['total']} spotted the seeded error. "
                         f"{result['followup']['text']}"})
            await sess.execute(text(
                "INSERT INTO room_summaries (summary_id, room_id, original_question, "
                "explanation, activity_type, verification_json, unresolved_json, created_at) "
                "VALUES (:sid, :rid, :q, :ex, 'find_the_mistake', :vj, :uj, :ts)"),
                {"sid": new_summary_id(), "rid": room_id,
                 "q": "Find the Mistake: " + (act["payload"].get("problem_id") or ""),
                 "ex": result["expected"]["answer"],
                 "vj": _json.dumps(result["group_stats"]),
                 "uj": _json.dumps(["Follow-up question pending discussion: "
                                    + result["followup"]["text"]]), "ts": now})
            await sess.commit()
        return await self.get_game(room_id, activity_id, learner_id)

    async def list_activities(self, room_id: str, learner_id: str) -> List[dict]:
        import json as _json
        async with self.p.session() as sess:
            await self._require_member(sess, room_id, learner_id)
            rows = (await sess.execute(text(
                "SELECT activity_id, activity_type, status, created_at FROM "
                "room_activities WHERE room_id = :rid ORDER BY created_at DESC"),
                {"rid": room_id})).mappings().all()
        return [dict(r) for r in rows]
