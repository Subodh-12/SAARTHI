"""Seed demo data for Karana Study Rooms (dev/demo environments).

Idempotent: seeds only when no study rooms exist. Creates fictional
learners + two Class 9 Science rooms with realistic chat, one completed
Doubt Relay, one active relay with conflicting answers, one completed
Find the Mistake game, verification outcomes and a room summary.

Never seeds real student data, credentials, or production secrets.
"""
from __future__ import annotations

import json
import time

from sqlalchemy import text

from ..adapters.persistence import Persistence
from ..core.logging import get_logger

log = get_logger("saarthi.rooms_seed")

_now = lambda: int(time.time() * 1000)
MIN = 60_000
HOUR = 3_600_000

FICTIONAL_LEARNERS = [
    ("seed-lrn-anita", "Anita (demo)"),
    ("seed-lrn-bikash", "Bikash (demo)"),
    ("seed-lrn-cutta", "Cuttacki (demo)"),
    ("seed-lrn-deepa", "Deepa (demo)"),
    ("seed-lrn-ebrahim", "Ebrahim (demo)"),
    ("seed-lrn-fakir", "Fakir (demo)"),
]


def _msg(mid, rid, lid, kind, body, ts, sender_kind="member", reply=None):
    return {"message_id": mid, "room_id": rid, "learner_id": lid,
            "sender_kind": sender_kind, "kind": kind, "reply_to": reply,
            "body": body, "created_at": ts}


async def seed_rooms_if_empty(persistence: Persistence, expiry_hours: int = 24) -> None:
    async with persistence.session() as s:
        n = (await s.execute(text("SELECT COUNT(*) c FROM study_rooms"))).scalar_one()
    if n:
        return
    log.info("seeding demo study rooms")
    await _seed(persistence, expiry_hours)


async def reseed_rooms(persistence: Persistence, expiry_hours: int = 24) -> int:
    """Wipe all room-scoped data and reseed. Dev/demo only."""
    async with persistence.session() as s:
        for table in ("room_summaries", "verification_results", "activity_decisions",
                      "activity_submissions", "room_activities", "room_messages",
                      "room_members", "study_rooms"):
            await s.execute(text(f"DELETE FROM {table}"))
        await s.commit()
    await _seed(persistence, expiry_hours)
    return 3


async def _seed(p: Persistence, expiry_hours: int) -> None:
    now = _now()
    async with p.session() as s:
        # Fictional learner profiles (no device binding; demo identities).
        for lid, label in FICTIONAL_LEARNERS:
            await s.execute(text(
                "INSERT OR IGNORE INTO learner_profiles (learner_id, display_label, "
                "locale, grade, subject, created_at) VALUES (:lid, :lbl, 'or', "
                "'class9', 'science', :ts)"), {"lid": lid, "lbl": label, "ts": now})

        # ---------------- Room 1: Matter in Our Surroundings ---------------- #
        r1 = "room-seed-matter"
        t0 = now - 26 * HOUR
        await s.execute(text(
            "INSERT INTO study_rooms (room_id, room_code, title, subject, chapter_id, "
            "chapter_title, learning_topic, language, capacity, status, created_by, "
            "created_at, last_activity_at) VALUES (:r, 'KRN7X2', :t, 'science', "
            "'ch01', 'Matter in Our Surroundings', 'Evaporation and latent heat', "
            "'or', 6, 'active', 'seed-lrn-anita', :t0, :t4)"),
            {"r": r1, "t": "Evaporation Doubt Busters", "t0": t0, "t4": now - 40 * MIN})
        members1 = ["seed-lrn-anita", "seed-lrn-bikash", "seed-lrn-cutta",
                    "seed-lrn-deepa", "seed-lrn-ebrahim"]
        for i, m in enumerate(members1):
            await s.execute(text(
                "INSERT INTO room_members (room_id, learner_id, role, joined_at, "
                "last_seen_at) VALUES (:r, :m, :role, :ts, :ls)"),
                {"r": r1, "m": m, "role": "host" if i == 0 else "member",
                 "ts": t0 + i * MIN, "ls": now - (60 if i < 3 else 9000) * 1000})

        msgs1 = [
            ("m1-1", "seed-lrn-anita", "chat", "Namaskar! Today let's finish evaporation before the test.", t0 + 5 * MIN),
            ("m1-2", "seed-lrn-bikash", "chat", "Ready. I still get confused between evaporation and boiling.", t0 + 7 * MIN),
            ("m1-3", "KARANA", "chat", "Karana demo agent here (simulated, no AI model): a good way to separate them is that boiling happens throughout the liquid at a fixed temperature, while evaporation happens only at the surface at any temperature.", t0 + 8 * MIN),
            ("m1-4", "seed-lrn-deepa", "reply", "So my wet clothes dry even in winter because of surface evaporation?", t0 + 12 * MIN, "m1-2"),
            ("m1-5", "seed-lrn-anita", "chat", "Exactly, Deepa. That is why I started a doubt relay on sweating — submit your answers!", t0 + 15 * MIN),
        ]
        for m in msgs1:
            mid, who, kind, body, ts = m[:5]
            reply = m[5] if len(m) > 5 else None
            lid = None if who == "KARANA" else who
            await s.execute(text(
                "INSERT INTO room_messages (message_id, room_id, learner_id, sender_kind, "
                "kind, reply_to, body, created_at) VALUES (:mid, :r, :lid, :sk, :k, :rp, :b, :ts)"),
                {"mid": mid, "r": r1, "lid": lid,
                 "sk": "karana" if who == "KARANA" else "member",
                 "k": kind, "rp": reply, "b": body, "ts": ts})

        # Completed doubt relay in room 1
        act1 = "act-seed-r1-done"
        await s.execute(text(
            "INSERT INTO room_activities (activity_id, room_id, activity_type, status, "
            "payload_json, created_by, created_at, updated_at) VALUES "
            "(:a, :r, 'doubt_relay', 'completed', :pl, 'seed-lrn-anita', :ts, :ts)"),
            {"a": act1, "r": r1, "ts": now - 20 * HOUR,
             "pl": json.dumps({
                 "question": "Why does sweat cool our body on a hot day?",
                 "pattern": "disagree",
                 "explanation": "Evaporating sweat draws latent heat of vaporisation from the skin.",
                 "followup": {"text": "Compare: where does the 'cold' come from if sweat leaves the body at skin temperature?"},
                 "verification": {"question": "Why does sprinkling water on a roof cool the room below?",
                                  "options": ["Water is always colder than air",
                                              "Evaporating water absorbs latent heat from the roof",
                                              "Water reflects sunlight away",
                                              "Water conducts heat into the ground"],
                                  "correct_option": 1},
                 "trace": [{"step": "classify", "detail": "Pattern = disagree: 3 of 5 mentioned evaporation."},
                           {"step": "demo_note", "detail": "demo agent"}],
                 "agent_demo": True,
                 "unresolved": ["Bikash's follow-up about boiling vs evaporation was left open."]})})
        for lid, content in [("seed-lrn-anita", "Sweat evaporates and takes heat away from the skin."),
                             ("seed-lrn-bikash", "Sweat is cold water so it makes skin cold."),
                             ("seed-lrn-cutta", "Evaporation of sweat absorbs latent heat from our body."),
                             ("seed-lrn-deepa", "Wind blows the heat away from the skin surface."),
                             ("seed-lrn-ebrahim", "Evaporation needs latent heat which it takes from the skin.")]:
            await s.execute(text(
                "INSERT INTO activity_submissions (submission_id, activity_id, room_id, "
                "learner_id, content, created_at) VALUES (:sid, :a, :r, :lid, :c, :ts)"),
                {"sid": f"sub-seed-{lid[-6:]}", "a": act1, "r": r1, "lid": lid,
                 "c": content, "ts": now - 20 * HOUR + MIN})
        for lid, correct in [("seed-lrn-anita", 1), ("seed-lrn-cutta", 1),
                             ("seed-lrn-ebrahim", 1), ("seed-lrn-bikash", 0),
                             ("seed-lrn-deepa", 0)]:
            await s.execute(text(
                "INSERT INTO verification_results (result_id, activity_id, room_id, "
                "learner_id, question_id, selected_option, correct, created_at) VALUES "
                "(:rid, :a, :r, :lid, 'rel-matter-evaporation', :opt, :cor, :ts)"),
                {"rid": f"ver-seed-{lid[-6:]}", "a": act1, "r": r1, "lid": lid,
                 "opt": correct, "cor": 1 if correct == 1 else 0, "ts": now - 19 * HOUR})
        await s.execute(text(
            "INSERT INTO room_summaries (summary_id, room_id, original_question, "
            "explanation, activity_type, verification_json, unresolved_json, created_at) "
            "VALUES (:sid, :r, :q, :ex, 'doubt_relay', :vj, :uj, :ts)"),
            {"sid": "sum-seed-r1", "r": r1, "ts": now - 19 * HOUR,
             "q": "Why does sweat cool our body on a hot day?",
             "ex": "Evaporating sweat draws latent heat of vaporisation from the skin, cooling it.",
             "vj": json.dumps({"completed_by": 5, "group_total": 5, "correct": 3}),
             "uj": json.dumps(["Bikash's follow-up about boiling vs evaporation was left open."])})

        # Completed Find the Mistake in room 1
        gact1 = "act-seed-r1-game"
        await s.execute(text(
            "INSERT INTO room_activities (activity_id, room_id, activity_type, status, "
            "payload_json, created_by, created_at, updated_at) VALUES "
            "(:a, :r, 'find_the_mistake', 'revealed', :pl, 'seed-lrn-cutta', :ts, :ts)"),
            {"a": gact1, "r": r1, "ts": now - 3 * HOUR,
             "pl": json.dumps({"problem_id": "mist-boiling-temp", "mistake_index": 2,
                               "followup": {"text": "If boiling water cannot get hotter, how does a pressure cooker cook food faster?"},
                               "group_stats": {"found": 3, "reasoned": 4, "total": 4},
                               "trace": [{"step": "observe", "detail": "4 submissions; 3 found line 2."}],
                               "agent_demo": True})})
        for lid, line, reasoning in [
                ("seed-lrn-anita", "Line 2", "Boiling stays at the boiling point; extra heat becomes latent heat."),
                ("seed-lrn-bikash", "Line 1", "I thought boiling point changes at altitude."),
                ("seed-lrn-cutta", "Line 2", "Temperature cannot rise once boiling starts, so more fuel changes nothing."),
                ("seed-lrn-deepa", "Line 2", "The heat goes into turning water to steam, not raising temperature.")]:
            await s.execute(text(
                "INSERT INTO activity_submissions (submission_id, activity_id, room_id, "
                "learner_id, content, created_at) VALUES (:sid, :a, :r, :lid, :c, :ts)"),
                {"sid": f"subg-{lid[-6:]}", "a": gact1, "r": r1, "lid": lid, "ts": now - 3 * HOUR + MIN,
                 "c": json.dumps({"mistake_line": line, "reasoning": reasoning})})
        await s.execute(text(
            "INSERT INTO room_summaries (summary_id, room_id, original_question, "
            "explanation, activity_type, verification_json, unresolved_json, created_at) "
            "VALUES (:sid, :r, :q, :ex, 'find_the_mistake', :vj, :uj, :ts)"),
            {"sid": "sum-seed-r1-game", "r": r1, "ts": now - 3 * HOUR,
             "q": "Find the Mistake: mist-boiling-temp",
             "ex": "Line 2 is wrong: boiling water stays at its boiling point; extra heat goes into latent heat of vaporisation.",
             "vj": json.dumps({"found": 3, "reasoned": 4, "total": 4}),
             "uj": json.dumps(["Bikash needs to revisit boiling point vs altitude."])})
        await s.execute(text(
            "INSERT INTO room_messages (message_id, room_id, learner_id, sender_kind, kind, "
            "body, created_at) VALUES ('m1-g1', :r, NULL, 'karana', 'chat', "
            "'Find the Mistake reveal! 3 of 4 spotted the seeded error. If boiling water cannot get hotter, how does a pressure cooker cook food faster?', :ts)"),
            {"r": r1, "ts": now - 3 * HOUR + 2 * MIN})

        # Unresolved doubt message
        await s.execute(text(
            "INSERT INTO room_messages (message_id, room_id, learner_id, sender_kind, kind, "
            "body, created_at) VALUES ('m1-u1', :r, 'seed-lrn-bikash', 'member', 'chat', "
            "'Still unresolved for me: does evaporation also happen while water is boiling?', :ts)"),
            {"r": r1, "ts": now - 40 * MIN})

        # ---------------- Room 2: Motion — active conflicting relay -------- #
        r2 = "room-seed-motion"
        t1 = now - 5 * HOUR
        await s.execute(text(
            "INSERT INTO study_rooms (room_id, room_code, title, subject, chapter_id, "
            "chapter_title, learning_topic, language, capacity, status, created_by, "
            "created_at, last_activity_at) VALUES (:r, 'KRN3QM', :t, 'science', "
            "'ch02', 'Motion', 'Distance vs displacement', 'or', 4, 'active', "
            "'seed-lrn-fakir', :t1, :t2)"),
            {"r": r2, "t": "Motion Marathon Squad", "t1": t1, "t2": now - 10 * MIN})
        for i, m in enumerate(["seed-lrn-fakir", "seed-lrn-bikash",
                               "seed-lrn-deepa", "seed-lrn-ebrahim"]):
            await s.execute(text(
                "INSERT INTO room_members (room_id, learner_id, role, joined_at, "
                "last_seen_at) VALUES (:r, :m, :role, :ts, :ls)"),
                {"r": r2, "m": m, "role": "host" if i == 0 else "member",
                 "ts": t1 + i * MIN, "ls": now - 5 * MIN})
        msgs2 = [
            ("m2-1", "seed-lrn-fakir", "chat", "Round trip practice today. I posted a doubt relay — everyone answer on your own first!", t1 + 4 * MIN),
            ("m2-2", "seed-lrn-deepa", "chat", "Submitted. I think I got it but not sure.", t1 + 9 * MIN),
        ]
        for m in msgs2:
            await s.execute(text(
                "INSERT INTO room_messages (message_id, room_id, learner_id, sender_kind, "
                "kind, reply_to, body, created_at) VALUES (:mid, :r, :lid, 'member', :k, NULL, :b, :ts)"),
                {"mid": m[0], "r": r2, "lid": m[1], "k": m[2], "b": m[3], "ts": m[4]})
        act2 = "act-seed-r2-open"
        await s.execute(text(
            "INSERT INTO room_activities (activity_id, room_id, activity_type, status, "
            "payload_json, created_by, created_at, updated_at) VALUES "
            "(:a, :r, 'doubt_relay', 'collecting', :pl, 'seed-lrn-fakir', :ts, :ts)"),
            {"a": act2, "r": r2, "ts": now - 30 * MIN,
             "pl": json.dumps({"question": "Can the distance travelled by an object be less than the magnitude of its displacement? Why?"})})
        for lid, content in [("seed-lrn-fakir", "Never — distance counts the whole path, displacement is just start-to-end straight line."),
                             ("seed-lrn-bikash", "Yes, sometimes distance can be smaller if the object takes a shortcut."),
                             ("seed-lrn-deepa", "No, because displacement is the shortest path, so distance is always equal or bigger.")]:
            await s.execute(text(
                "INSERT INTO activity_submissions (submission_id, activity_id, room_id, "
                "learner_id, content, created_at) VALUES (:sid, :a, :r, :lid, :c, :ts)"),
                {"sid": f"sub2-{lid[-6:]}", "a": act2, "r": r2, "lid": lid,
                 "c": content, "ts": now - 25 * MIN})

        # ---------------- Room 3: expired-eligible dev room ---------------- #
        r3 = "room-seed-expiring"
        t2 = now - 48 * HOUR
        await s.execute(text(
            "INSERT INTO study_rooms (room_id, room_code, title, subject, chapter_id, "
            "chapter_title, learning_topic, language, capacity, status, created_by, "
            "created_at, empty_since, expires_at, last_activity_at) VALUES "
            "(:r, 'KRNXPL', 'Tissues Leftover Circle', 'science', 'ch03', 'Tissues', "
            "'Plant vs animal tissues', 'or', 5, 'active', 'seed-lrn-cutta', :t2, "
            ":empty, :exp, :empty)"),
            {"r": r3, "t2": t2,
             "empty": now - int(0.9 * expiry_hours * HOUR),
             "exp": now - int(0.9 * expiry_hours * HOUR) + expiry_hours * HOUR})
        await s.execute(text(
            "INSERT INTO room_members (room_id, learner_id, role, joined_at, last_seen_at) "
            "VALUES (:r, 'seed-lrn-cutta', 'host', :ts, :ts)"), {"r": r3, "ts": t2})
        await s.execute(text(
            "INSERT INTO room_messages (message_id, room_id, learner_id, sender_kind, kind, "
            "body, created_at) VALUES ('m3-1', :r, NULL, 'system', 'system', "
            "'Expiry-demo room (dev): empty for most of its window — will be deleted by the backend sweeper when the deadline passes.', :ts)"),
            {"r": r3, "ts": t2})
        await s.commit()
    log.info("demo rooms seeded (3 rooms)")


async def reset_and_reseed(persistence: Persistence) -> int:
    s = None
    from ..core.settings import get_settings
    hours = get_settings().room_expiry_hours
    return await reseed_rooms(persistence, hours)
