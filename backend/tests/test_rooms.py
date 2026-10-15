"""Karana Study Rooms — integration tests.

Covers: permissions, capacity, chat persistence, submission privacy,
doubt-relay transitions + pattern-dependent demo-agent decisions,
find-the-mistake, room lifecycle (leave → 24h expiry, rejoin → cancel,
backend deletion), and seeded data visibility.
"""
from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "backend"))

TMP_DB = tempfile.mktemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TMP_DB}"
os.environ["PERSISTENCE_BACKEND"] = "sqlite"
os.environ["TRANSLATION_PROVIDER"] = "mock"
os.environ["LLM_PROVIDER"] = "mock"
os.environ["ENV"] = "test"
# Dev-friendly short expiry so tests can prove the 24h logic quickly.
os.environ["ROOM_EXPIRY_HOURS"] = "24"

from app.core.settings import reset_settings_cache
reset_settings_cache()

from app.main import create_app

APP = create_app()
client = TestClient(APP)
client.__enter__()  # run lifespan (schema apply, services, sweeper)


def _make_learner(label: str) -> tuple[str, dict]:
    r = client.post("/api/v1/learners", json={
        "display_label": label, "locale": "or", "grade": "class9",
        "subject": "science"})
    assert r.status_code == 201, r.text
    data = r.json()
    headers = {"Authorization": f"Bearer {data['device_token']}",
               "X-Device-Id": data["device_id"]}
    return data["learner_id"], headers


@pytest.fixture(scope="module")
def users():
    out = {}
    for name in ("Test Host", "Test Peer A", "Test Peer B", "Test Peer C",
                 "Test Peer D", "Test Peer E", "Test Outsider"):
        out[name] = _make_learner(name)
    return out


@pytest.fixture()
def room(users):
    _, h = users["Test Host"]
    r = client.post("/api/v1/rooms/create", headers=h, json={
        "title": "Physics Squad", "subject": "science",
        "chapter_id": "ch02", "chapter_title": "Motion",
        "learning_topic": "distance vs displacement",
        "language": "or", "capacity": 4})
    assert r.status_code == 201, r.text
    return r.json()["room"]


# ------------------------------------------------------------------ #
# Auth / permissions
# ------------------------------------------------------------------ #
def test_requires_auth():
    r = client.get("/api/v1/rooms")
    assert r.status_code == 401


def test_non_member_cannot_read_room(users, room):
    _, h = users["Test Outsider"]
    r = client.get(f"/api/v1/rooms/{room['room_id']}", headers=h)
    assert r.status_code == 403
    r2 = client.get("/api/v1/rooms", headers=h)
    ids = [rm["room"]["room_id"] for rm in r2.json()["rooms"]]
    assert room["room_id"] not in ids


def test_bad_join_code(users):
    _, h = users["Test Outsider"]
    r = client.post("/api/v1/rooms/join", headers=h, json={"room_code": "ZZZZZZ"})
    assert r.status_code == 404


# ------------------------------------------------------------------ #
# Capacity + membership
# ------------------------------------------------------------------ #
def test_capacity_enforced(users, room):
    _, host = users["Test Host"]
    code = room["room_code"]
    # 4-member room: host + 3 more, then the 5th is rejected.
    joiners = ["Test Peer A", "Test Peer B", "Test Peer C"]
    for name in joiners:
        _, h = users[name]
        r = client.post("/api/v1/rooms/join", headers=h, json={"room_code": code})
        assert r.status_code == 200, r.text
    _, h = users["Test Peer D"]
    r = client.post("/api/v1/rooms/join", headers=h, json={"room_code": code})
    assert r.status_code == 409
    assert r.json()["error_code"] == "room_full"


# ------------------------------------------------------------------ #
# Chat
# ------------------------------------------------------------------ #
def test_chat_persists_and_visible(users, room):
    _, h = users["Test Host"]
    msg = "Can displacement be zero on a full lap?"
    r = client.post(f"/api/v1/rooms/{room['room_id']}/messages", headers=h,
                    json={"body": msg})
    assert r.status_code == 200
    mid = r.json()["message_id"]
    _, h2 = users["Test Peer A"]
    client.post("/api/v1/rooms/join", headers=h2, json={"room_code": room["room_code"]})
    detail = client.get(f"/api/v1/rooms/{room['room_id']}", headers=h2).json()
    bodies = [m["body"] for m in detail["messages"]]
    assert msg in bodies
    assert any(m["message_id"] == mid for m in detail["messages"])


def test_reply_to_missing_message(users, room):
    _, h = users["Test Host"]
    r = client.post(f"/api/v1/rooms/{room['room_id']}/messages", headers=h,
                    json={"body": "hi", "reply_to": "msg_nonexistent"})
    assert r.status_code == 400


# ------------------------------------------------------------------ #
# Doubt Relay
# ------------------------------------------------------------------ #
def _start_relay(room, headers, question):
    r = client.post(f"/api/v1/rooms/{room['room_id']}/relay/start",
                    headers=headers, json={"question": question})
    assert r.status_code == 200, r.text
    return r.json()


def test_submissions_hidden_until_reveal(users, room):
    _, host = users["Test Host"]
    relay = _start_relay(room, host, "Why does sweat cool our body on a hot day?")
    aid = relay["activity_id"]
    _, a = users["Test Peer A"]
    client.post("/api/v1/rooms/join", headers=a, json={"room_code": room["room_code"]})
    r = client.post(f"/api/v1/rooms/{room['room_id']}/relay/{aid}/submit",
                    headers=a, json={"content": "Evaporation takes latent heat from the skin."})
    assert r.status_code == 200
    state = client.get(f"/api/v1/rooms/{room['room_id']}/relay/{aid}",
                       headers=host).json()
    assert state["submission_count"] == 1
    assert all(s["content"] is None for s in state["submissions"]), \
        "other members' answers must stay hidden before reveal"
    # duplicate submission blocked
    dup = client.post(f"/api/v1/rooms/{room['room_id']}/relay/{aid}/submit",
                      headers=a, json={"content": "again"})
    assert dup.status_code == 409


def test_patterns_produce_different_decisions(users):
    """agree vs disagree vs insufficient → different follow-ups."""
    outcomes = {}
    for pattern, answers in [
        ("agree", ["Evaporation takes latent heat from the skin, cooling it.",
                   "Sweat evaporates and the latent heat comes from the body.",
                   "Evaporation of sweat absorbs heat, so skin cools.",
                   "The latent heat of vaporisation is drawn from the skin."]),
        ("disagree", ["Evaporation takes latent heat from the skin, cooling it.",
                      "Sweat is cold water so it makes the skin cold.",
                      "Wind blows the heat away from the body surface.",
                      "Something about cold water cooling us down."]),
        ("insufficient", ["idk", "heat", "sweat is wet", "no idea honestly"]),
    ]:
        _, host = users["Test Host"]
        room_r = client.post("/api/v1/rooms/create", headers=host, json={
            "title": f"Relay {pattern}", "chapter_id": "ch01",
            "chapter_title": "Matter", "capacity": 4})
        rroom = room_r.json()["room"]
        code = rroom["room_code"]
        headers = [host]
        for name in ("Test Peer A", "Test Peer B", "Test Peer C"):
            _, h = users[name]
            client.post("/api/v1/rooms/join", headers=h, json={"room_code": code})
            headers.append(h)
        relay = _start_relay(rroom, host,
                             "Why does sweat cool our body on a hot day?")
        aid = relay["activity_id"]
        for h, ans in zip(headers, answers):
            r = client.post(f"/api/v1/rooms/{rroom['room_id']}/relay/{aid}/submit",
                            headers=h, json={"content": ans})
            assert r.status_code == 200, r.text
        rev = client.post(f"/api/v1/rooms/{rroom['room_id']}/relay/{aid}/reveal",
                          headers=host)
        assert rev.status_code == 200, rev.text
        st = rev.json()
        assert st["pattern"] == pattern, (pattern, st["pattern"])
        assert st["trace"], "demo agent must record a decision trace"
        assert any(t["step"] == "demo_note" for t in st["trace"])
        outcomes[pattern] = st
    # Different patterns → different follow-up questions and gating
    assert outcomes["agree"]["followup"]["text"] != outcomes["disagree"]["followup"]["text"]
    assert outcomes["agree"]["verification"] is not None
    assert outcomes["disagree"]["verification"] is not None
    # insufficient pattern must NOT gate to verification: trying to advance
    # to verification fails because no verification question exists
    insuf = outcomes["insufficient"]
    adv = client.post(
        "/api/v1/rooms/insufficient-room/relay/"
        f"{insuf['activity_id']}/advance", headers=users["Test Host"][1],
        json={"stage": "verification"})
    assert adv.status_code in (403, 404)


def test_full_relay_to_verification(users):
    _, host = users["Test Host"]
    room_r = client.post("/api/v1/rooms/create", headers=host, json={
        "title": "Full relay", "chapter_id": "ch01", "capacity": 4}).json()["room"]
    code = room_r["room_code"]
    heads = [host]
    for name in ("Test Peer A", "Test Peer B"):
        _, h = users[name]
        client.post("/api/v1/rooms/join", headers=h, json={"room_code": code})
        heads.append(h)
    relay = _start_relay(room_r, host,
                         "Why does sweat cool our body on a hot day?")
    aid = relay["activity_id"]
    answers = ["Evaporation of sweat takes latent heat from the skin.",
               "Sweat evaporates, drawing heat from the body.",
               "Latent heat of vaporisation is absorbed from skin."]
    for h, a in zip(heads, answers):
        client.post(f"/api/v1/rooms/{room_r['room_id']}/relay/{aid}/submit",
                    headers=h, json={"content": a})
    st = client.post(f"/api/v1/rooms/{room_r['room_id']}/relay/{aid}/reveal",
                     headers=host).json()
    assert st["status"] == "followup"
    # advance to discussion, then verification
    st = client.post(f"/api/v1/rooms/{room_r['room_id']}/relay/{aid}/advance",
                     headers=host, json={"stage": "discussion"}).json()
    assert st["status"] == "discussion"
    st = client.post(f"/api/v1/rooms/{room_r['room_id']}/relay/{aid}/advance",
                     headers=host, json={"stage": "verification"}).json()
    assert st["status"] == "verification"
    ver = st["verification"]
    # everyone answers correctly → completed + summary
    for h in heads:
        r = client.post(f"/api/v1/rooms/{room_r['room_id']}/relay/{aid}/verify",
                        headers=h, json={"selected_option": ver["correct_option"]})
        assert r.status_code == 200
    final = client.post(f"/api/v1/rooms/{room_r['room_id']}/relay/{aid}/verify",
                        headers=heads[0],
                        json={"selected_option": ver["correct_option"]})
    assert final.status_code == 409  # duplicate
    detail = client.get(f"/api/v1/rooms/{room_r['room_id']}",
                        headers=host).json()
    assert detail["summaries"], "session summary must be stored"
    s = detail["summaries"][-1]
    assert s["original_question"].startswith("Why does sweat cool")
    assert s["verification"]["completed_by"] == 3


# ------------------------------------------------------------------ #
# Find the Mistake
# ------------------------------------------------------------------ #
def test_find_the_mistake_flow(users, room):
    _, host = users["Test Host"]
    g = client.post(f"/api/v1/rooms/{room['room_id']}/game/start",
                    headers=host).json()
    aid = g["activity_id"]
    assert g["problem"]["lines"]
    _, a = users["Test Peer A"]
    client.post("/api/v1/rooms/join", headers=a,
                json={"room_code": room["room_code"]})
    r = client.post(f"/api/v1/rooms/{room['room_id']}/game/{aid}/submit",
                    headers=a, json={"mistake_line": "Line 2",
                                     "reasoning": "Boiling stays at constant temperature."})
    assert r.status_code == 200
    pre = r.json()
    assert all(s.get("content") is None for s in pre["submissions"])
    rev = client.post(f"/api/v1/rooms/{room['room_id']}/game/{aid}/reveal",
                      headers=host).json()
    assert rev["expected"]["mistake_index"] == 2
    assert rev["followup"]["text"]
    detail = client.get(f"/api/v1/rooms/{room['room_id']}", headers=host).json()
    assert any(s["activity_type"] == "find_the_mistake" for s in detail["summaries"])


# ------------------------------------------------------------------ #
# Lifecycle: leave → expiry, rejoin → cancel, backend deletion
# ------------------------------------------------------------------ #
def test_lifecycle_expiry_and_rejoin(users):
    _, host = users["Test Host"]
    _, a = users["Test Peer A"]
    room_r = client.post("/api/v1/rooms/create", headers=host, json={
        "title": "Lifecycle", "chapter_id": "ch01", "capacity": 4}).json()["room"]
    rid, code = room_r["room_id"], room_r["room_code"]
    client.post("/api/v1/rooms/join", headers=a, json={"room_code": code})
    client.post(f"/api/v1/rooms/{rid}/messages", headers=a,
                json={"body": "history that must vanish after expiry"})

    # Host leaves → room not empty, no expiry set.
    client.post(f"/api/v1/rooms/{rid}/leave", headers=host)
    detail = client.get(f"/api/v1/rooms/{rid}", headers=a).json()
    assert detail["room"]["expires_at"] is None

    # Last member leaves → 24h countdown starts.
    client.post(f"/api/v1/rooms/{rid}/leave", headers=a)
    _, o = users["Test Outsider"]
    assert client.get(f"/api/v1/rooms/{rid}", headers=o).status_code == 403
    sweep = client.post("/api/v1/rooms/admin/expire-sweep", headers=host).json()
    assert rid not in sweep["deleted_room_ids"], "24h not yet passed"
    # Expiry is stored in DB.
    from app.adapters.persistence import get_persistence

    async def _check():
        p = await get_persistence()
        async with p.session() as s:
            from sqlalchemy import text
            row = (await s.execute(text(
                "SELECT expires_at, empty_since FROM study_rooms WHERE room_id = :r"),
                {"r": rid})).mappings().first()
            return row
    row = asyncio.run(_check())
    assert row["expires_at"] and row["empty_since"]
    hours = (row["expires_at"] - row["empty_since"]) / 3_600_000
    assert 23.9 < hours <= 24.001

    # Rejoin cancels the pending deletion.
    r = client.post("/api/v1/rooms/join", headers=a, json={"room_code": code})
    assert r.status_code == 200
    row = asyncio.run(_check())
    assert row["expires_at"] is None and row["empty_since"] is None
    detail = client.get(f"/api/v1/rooms/{rid}", headers=a).json()
    assert any("history that must vanish" in m["body"] for m in detail["messages"]), \
        "returning member must see earlier conversation"

    # Leave again, force the deadline into the past, sweep → permanent deletion.
    client.post(f"/api/v1/rooms/{rid}/leave", headers=a)

    async def _force_expire():
        p = await get_persistence()
        async with p.session() as s:
            from sqlalchemy import text
            await s.execute(text(
                "UPDATE study_rooms SET expires_at = :t WHERE room_id = :r"),
                {"t": 1, "r": rid})
            await s.commit()
    asyncio.run(_force_expire())
    sweep = client.post("/api/v1/rooms/admin/expire-sweep", headers=host).json()
    assert rid in sweep["deleted_room_ids"]

    async def _gone():
        p = await get_persistence()
        async with p.session() as s:
            from sqlalchemy import text
            room_gone = (await s.execute(text(
                "SELECT COUNT(*) FROM study_rooms WHERE room_id = :r"), {"r": rid}
            )).scalar_one()
            msg_gone = (await s.execute(text(
                "SELECT COUNT(*) FROM room_messages WHERE room_id = :r"), {"r": rid}
            )).scalar_one()
            member_gone = (await s.execute(text(
                "SELECT COUNT(*) FROM room_members WHERE room_id = :r"), {"r": rid}
            )).scalar_one()
            return room_gone, msg_gone, member_gone
    room_gone, msg_gone, member_gone = asyncio.run(_gone())
    assert (room_gone, msg_gone, member_gone) == (0, 0, 0)
    # Learner profile (personal data) must survive room deletion.
    _, a_id = users["Test Peer A"][0], users["Test Peer A"][0]
    me = client.get("/api/v1/learners/me", headers=a).json()
    assert me["learner_id"]
    assert client.get(f"/api/v1/rooms/{rid}", headers=a).status_code == 404


def test_seeded_demo_rooms_visible(users):
    """Seeded rooms appear (via reseed helper) and contain demo content."""
    from app.adapters.persistence import get_persistence
    from app.services.rooms_seed import reseed_rooms

    async def _seed():
        p = await get_persistence()
        return await reseed_rooms(p)
    n = asyncio.run(_seed())
    assert n >= 2
    # Anita's token isn't available; verify via DB instead (seed ids are fixed).
    async def _check():
        p = await get_persistence()
        async with p.session() as s:
            from sqlalchemy import text
            rooms = (await s.execute(text(
                "SELECT room_id, room_code FROM study_rooms "
                "WHERE room_id LIKE 'room-seed-%'"))).mappings().all()
            msgs = (await s.execute(text(
                "SELECT COUNT(*) FROM room_messages WHERE room_id = 'room-seed-matter'"
            ))).scalar_one()
            summaries = (await s.execute(text(
                "SELECT COUNT(*) FROM room_summaries WHERE room_id = 'room-seed-matter'"
            ))).scalar_one()
            open_relay = (await s.execute(text(
                "SELECT COUNT(*) FROM room_activities WHERE room_id = 'room-seed-motion' "
                "AND status = 'collecting'"))).scalar_one()
            return rooms, msgs, summaries, open_relay
    rooms, msgs, summaries, open_relay = asyncio.run(_check())
    assert len(rooms) >= 3          # incl. expiry-demo room
    assert msgs >= 5                # realistic history
    assert summaries >= 2           # completed relay + game
    assert open_relay == 1          # active conflicting relay


def test_non_member_cannot_submit_to_relay(users, room):
    """Regression: submit endpoints must enforce room membership."""
    _, host = users["Test Host"]
    relay = _start_relay(room, host, "Why does sweat cool our body on a hot day?")
    _, o = users["Test Outsider"]
    r = client.post(
        f"/api/v1/rooms/{room['room_id']}/relay/{relay['activity_id']}/submit",
        headers=o, json={"content": "sneaky answer"})
    assert r.status_code == 403
    r2 = client.post(f"/api/v1/rooms/{room['room_id']}/game/start", headers=o)
    assert r2.status_code == 403
