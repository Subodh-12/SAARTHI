"""Karana Study Rooms — Pydantic contracts.

Room-scoped data is temporary (deleted 24h after the room empties).
Personal learner progress is never stored here.
"""
from __future__ import annotations

import time
import uuid
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

ACTIVITY_TYPES = ("doubt_relay", "find_the_mistake")
ACTIVITY_STATUSES = ("collecting", "revealed", "followup", "discussion",
                     "verification", "completed")


def new_room_id() -> str:
    return f"room_{uuid.uuid4().hex[:12]}"


def new_message_id() -> str:
    return f"msg_{uuid.uuid4().hex[:12]}"


def new_activity_id() -> str:
    return f"act_{uuid.uuid4().hex[:12]}"


def new_submission_id() -> str:
    return f"sub_{uuid.uuid4().hex[:12]}"


def new_decision_id() -> str:
    return f"dec_{uuid.uuid4().hex[:12]}"


def new_result_id() -> str:
    return f"ver_{uuid.uuid4().hex[:12]}"


def new_summary_id() -> str:
    return f"sum_{uuid.uuid4().hex[:12]}"


def now_ms() -> int:
    return int(time.time() * 1000)


class RoomCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    subject: str = "science"
    chapter_id: str = ""
    chapter_title: str = ""
    learning_topic: str = Field(default="", max_length=200)
    language: Literal["or", "en", "or-en"] = "or"
    capacity: int = Field(default=6, ge=4, le=6)


class RoomMember(BaseModel):
    learner_id: str
    display_label: str
    role: Literal["host", "member"] = "member"
    online: bool = False


class RoomSummary(BaseModel):
    """Landing-page view of a room (no chat content)."""
    room_id: str
    room_code: str
    title: str
    subject: str
    chapter_id: str
    chapter_title: str
    learning_topic: str
    language: str
    capacity: int
    member_count: int
    members: List[RoomMember] = []
    is_member: bool = False
    status: str = "active"
    created_at: int
    last_activity_at: int
    expires_at: Optional[int] = None
    recent_activity: List[str] = []


class RoomJoinRequest(BaseModel):
    room_code: str = Field(min_length=4, max_length=12)


class RoomMessage(BaseModel):
    message_id: str
    room_id: str
    learner_id: Optional[str] = None
    sender_label: str = ""
    sender_kind: Literal["member", "karana", "system"] = "member"
    kind: Literal["chat", "reply", "system", "summary"] = "chat"
    reply_to: Optional[str] = None
    body: str
    created_at: int


class MessagePost(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    reply_to: Optional[str] = None


class RoomDetail(BaseModel):
    room: RoomSummary
    messages: List[RoomMessage] = []
    summaries: List["RoomSessionSummary"] = []


class RoomSessionSummary(BaseModel):
    """Persistent record of one completed learning activity."""
    summary_id: str
    activity_type: str = "doubt_relay"
    original_question: str
    explanation: str = ""
    verification: dict = {}
    unresolved: List[str] = []
    created_at: int


# ---- Doubt Relay ---- #
class RelayStart(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    # Optional stable relay-bank item ID (e.g. "rel-matter-evaporation").
    # When present it is used instead of fuzzy question matching.
    bank_item_id: Optional[str] = None


class RelaySubmission(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class RelayState(BaseModel):
    activity_id: str
    activity_type: str = "doubt_relay"
    status: str
    question: str = ""
    my_submission: Optional[str] = None
    submission_count: int = 0
    eligible_count: int = 0
    # Only populated after reveal:
    submissions: List[dict] = []
    followup: Optional[dict] = None
    explanation: Optional[str] = None
    pattern: Optional[str] = None
    verification: Optional[dict] = None
    verification_result: Optional[dict] = None
    trace: List[dict] = []
    created_at: int
    updated_at: int


class GameSubmission(BaseModel):
    mistake_line: str = Field(min_length=1, max_length=500)
    reasoning: str = Field(default="", max_length=2000)


class GameState(BaseModel):
    activity_id: str
    activity_type: str = "find_the_mistake"
    status: str
    problem: Optional[dict] = None
    my_submission: Optional[dict] = None
    submission_count: int = 0
    eligible_count: int = 0
    submissions: List[dict] = []
    expected: Optional[dict] = None
    followup: Optional[dict] = None
    created_at: int
    updated_at: int


class GameStart(BaseModel):
    pass


class VerificationSubmit(BaseModel):
    selected_option: int = Field(ge=0, le=5)


class RoomDeleted(BaseModel):
    room_id: str
    deleted: bool
