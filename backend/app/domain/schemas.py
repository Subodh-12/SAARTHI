"""Pydantic v2 schemas — single source of truth for SAARTHI contracts.

OpenAPI is generated from these models by FastAPI automatically. The
TypeScript contracts in `frontend/src/generated/api.ts` are produced from
the OpenAPI schema by `scripts/gen_types.py`.
"""

from __future__ import annotations

import hashlib
import time
import unicodedata
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Any, Literal, Optional

from pydantic import BaseModel, Field, StringConstraints, field_validator, model_validator

from .bloom import BloomLevel, parse_bloom_level


# --------------------------------------------------------------------------- #
# Identifiers
# --------------------------------------------------------------------------- #
LearnerId = Annotated[str, StringConstraints(pattern=r"^lrn_[A-Za-z0-9]{16,32}$")]
DeviceId = Annotated[str, StringConstraints(pattern=r"^dev_[A-Za-z0-9]{16,32}$")]
ConceptId = Annotated[str, StringConstraints(pattern=r"^c[0-9]{4}$")]
ChapterId = Annotated[str, StringConstraints(pattern=r"^ch[0-9]{3}$")]
ChunkId = Annotated[str, StringConstraints(pattern=r"^chunk_[A-Za-z0-9_-]{8,64}$")]
QuestionId = Annotated[str, StringConstraints(pattern=r"^q_[A-Za-z0-9_-]{6,32}$")]
PackId = Annotated[str, StringConstraints(pattern=r"^pack_[a-z0-9_]+$")]


def new_request_id() -> str:
    return uuid.uuid4().hex


def new_learner_id() -> str:
    return "lrn_" + uuid.uuid4().hex[:24]


def new_device_id() -> str:
    return "dev_" + uuid.uuid4().hex[:24]


def new_decision_id() -> str:
    return "dec_" + uuid.uuid4().hex[:24]


def new_event_id() -> str:
    return "evt_" + uuid.uuid4().hex[:24]


def new_session_id() -> str:
    return "ses_" + uuid.uuid4().hex[:24]


# --------------------------------------------------------------------------- #
# Common enums (frozen at the end of Milestone 1 — Design v2 Appendix A)
# --------------------------------------------------------------------------- #
class NetworkState(str, Enum):
    ONLINE = "online"
    WEAK = "weak"
    OFFLINE = "offline"
    RECONNECTED = "reconnected"


class Action(str, Enum):
    REMEDIATE = "REMEDIATE"
    RETRY = "RETRY"
    REVISE = "REVISE"
    ADVANCE = "ADVANCE"


class DeliveryMode(str, Enum):
    RICH = "rich"
    CACHED = "cached"
    PREFETCH_THEN_OFFLINE = "prefetch_then_offline"


class BackgroundAction(str, Enum):
    SYNC = "SYNC"
    PREFETCH = "PREFETCH"


class EventType(str, Enum):
    SESSION_STARTED = "SESSION_STARTED"
    SESSION_ENDED = "SESSION_ENDED"
    CONTENT_VIEWED = "CONTENT_VIEWED"
    ANSWER_SUBMITTED = "ANSWER_SUBMITTED"
    QUESTION_ABANDONED = "QUESTION_ABANDONED"
    DOUBT_ASKED = "DOUBT_ASKED"
    DOUBT_ANSWERED = "DOUBT_ANSWERED"
    PACK_INSTALLED = "PACK_INSTALLED"
    DECISION_MADE_LOCAL = "DECISION_MADE_LOCAL"
    NETWORK_STATE_CHANGED = "NETWORK_STATE_CHANGED"


class EvidenceType(str, Enum):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIAL = "partial"
    NONE = "none"


class Outcome(str, Enum):
    """Per-event sync outcomes — Design v2 Section 8 (frozen)."""

    ACCEPTED = "ACCEPTED"
    DUPLICATE = "DUPLICATE"
    RETRYABLE = "RETRYABLE"
    REJECTED = "REJECTED"


class SyncEffect(str, Enum):
    MASTERY_UPDATED = "mastery_updated"
    NONE = "none"


# Stable sync rejection / no-effect reasons (never renamed, only added).
class SyncReason(str, Enum):
    REPEAT_SUBMISSION = "REPEAT_SUBMISSION"
    LEGACY_QUESTION = "LEGACY_QUESTION"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"
    UNKNOWN_EVENT_TYPE = "UNKNOWN_EVENT_TYPE"
    LEARNER_NOT_LINKED = "LEARNER_NOT_LINKED"
    DEVICE_REVOKED = "DEVICE_REVOKED"
    PAYLOAD_CONFLICT = "PAYLOAD_CONFLICT"
    SERVER_BUSY = "SERVER_BUSY"
    DB_TIMEOUT = "DB_TIMEOUT"


# --------------------------------------------------------------------------- #
# Learner / device / auth
# --------------------------------------------------------------------------- #
class LearnerProfileCreate(BaseModel):
    display_label: Annotated[str, StringConstraints(min_length=0, max_length=64)] = ""
    locale: Literal["or", "en"] = "or"
    grade: Literal["class9"] = "class9"
    subject: Literal["science"] = "science"
    # Optional LOCAL profile PIN. Never sent to the server for verification;
    # accepted only as an opaque, already-derived verifier string and stored
    # for display sync. The authoritative verifier never leaves the phone.
    pin_verifier: Optional[str] = None


class LearnerProfile(LearnerProfileCreate):
    learner_id: LearnerId
    created_at: int


class DeviceRegistration(BaseModel):
    """Register a physical device with its non-extractable WebCrypto
    ECDSA P-256 public key (SPKI, base64url). Returns the initial tokens."""
    public_key_spki_b64: Annotated[str, StringConstraints(min_length=16, max_length=512)]
    hardware_label: Annotated[str, StringConstraints(max_length=64)] = (
        "shared-android-low-end"
    )
    device_id: Optional[DeviceId] = None


class DeviceTokenResponse(BaseModel):
    device_id: DeviceId
    access_token: str
    access_expires_at: int
    refresh_token: str
    refresh_expires_at: int
    token_type: Literal["Bearer"] = "Bearer"


# Back-compat alias for older call sites/tests that still reference DeviceToken
DeviceToken = DeviceTokenResponse


class AuthChallenge(BaseModel):
    nonce: str
    expires_at: int


class AuthChallengeRequest(BaseModel):
    device_id: DeviceId


class AuthRenewRequest(BaseModel):
    device_id: DeviceId
    nonce: str
    signature_b64: Annotated[str, StringConstraints(min_length=16, max_length=1024)]


class RefreshRequest(BaseModel):
    device_id: DeviceId
    refresh_token: str


# Back-compat alias for older clients/tests that still read `device_token`.
class AuthResponse(BaseModel):
    learner_id: Optional[LearnerId] = None
    device_id: DeviceId
    device_token: str  # the access token
    token_expires_at: int
    refresh_token: Optional[str] = None
    refresh_expires_at: Optional[int] = None


# --------------------------------------------------------------------------- #
# Curriculum
# --------------------------------------------------------------------------- #
class GlossaryEntry(BaseModel):
    term_or: str
    term_en: str
    definition_or: str
    definition_en: str


class Concept(BaseModel):
    concept_id: ConceptId
    title_or: str
    title_en: str
    chapter_id: ChapterId
    prerequisites: list[ConceptId] = Field(default_factory=list)
    summary_or: str = ""
    source_refs: list[str] = Field(default_factory=list)


class Chunk(BaseModel):
    chunk_id: ChunkId
    concept_id: ConceptId
    chapter_id: ChapterId
    ordinal: int
    text_or: Annotated[str, StringConstraints(min_length=1, max_length=4000)]
    source_ref: str
    glossary_refs: list[str] = Field(default_factory=list)


class QuestionOption(BaseModel):
    index: int
    text_or: str
    misconception_tag: Optional[str] = None
    explanation_or: Optional[str] = None

    def __str__(self) -> str:
        return self.text_or


class Question(BaseModel):
    question_id: QuestionId
    concept_id: ConceptId
    chapter_id: ChapterId
    bloom_level: BloomLevel = BloomLevel.REMEMBER
    qtype: Literal["mcq", "short_answer"]
    prompt_or: Annotated[str, StringConstraints(min_length=1, max_length=1000)]
    options: list[QuestionOption] = Field(default_factory=list)
    correct_option: Optional[int] = None
    rubric_or: Optional[str] = None
    expected_concepts: list[str] = Field(default_factory=list)
    explanation_or: str
    difficulty: Literal["easy", "medium", "hard"]
    misconception_tag: Optional[str] = None
    source_ref: str
    revision: int = 1
    answer_key_hash: str = ""
    status: Literal["active", "legacy"] = "active"

    @field_validator("options", mode="before")
    @classmethod
    def _validate_options(cls, v: Any) -> list[QuestionOption]:
        if not v:
            return []
        res: list[QuestionOption] = []
        for i, item in enumerate(v):
            if isinstance(item, str):
                res.append(QuestionOption(index=i, text_or=item))
            elif isinstance(item, dict):
                idx = item.get("index", i)
                res.append(QuestionOption(
                    index=idx,
                    text_or=item.get("text_or", ""),
                    misconception_tag=item.get("misconception_tag"),
                    explanation_or=item.get("explanation_or"),
                ))
            elif isinstance(item, QuestionOption):
                res.append(item)
            else:
                res.append(QuestionOption(index=i, text_or=str(item)))
        return res

    @field_validator("bloom_level", mode="before")
    @classmethod
    def _validate_bloom_level(cls, v: Any) -> BloomLevel:
        if v is None:
            return BloomLevel.REMEMBER
        return parse_bloom_level(v)


class Chapter(BaseModel):
    chapter_id: ChapterId
    subject: Literal["science"] = "science"
    grade: Literal["class9"] = "class9"
    title_or: str
    title_en: str
    summary_or: str = ""
    source_refs: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Environment + mastery + events
# --------------------------------------------------------------------------- #
class EnvironmentSnapshot(BaseModel):
    network: NetworkState = NetworkState.ONLINE
    measured_rtt_ms: Optional[int] = None
    measured_downlink_kbps: Optional[int] = None
    battery_saver: bool = False
    free_storage_mb: Optional[int] = None
    installed_pack_versions: dict[str, int] = Field(default_factory=dict)
    ruleset_version: str = "1.0.0"


class MasteryRecord(BaseModel):
    concept_id: ConceptId
    p_bp: int = Field(2000, ge=0, le=10000)
    band: Literal["weak", "partial", "mastered"] = "weak"
    attempts: int = 0
    correct: int = 0
    last_event_seq: int = 0


class BloomMasteryRecord(BaseModel):
    concept_id: ConceptId
    bloom_level: BloomLevel
    p_bp: int = Field(2000, ge=0, le=10000)
    band: Literal["weak", "partial", "mastered"] = "weak"
    attempts: int = 0
    correct: int = 0
    last_event_seq: int = 0


class LearnerEvent(BaseModel):
    """Event: created on the phone, immutable (Design v2 Section 8).

    JSON uses the v2 wire name ``type``; Python uses ``event_type``."""

    event_id: str  # client-generated, idempotent
    device_id: DeviceId
    learner_id: LearnerId
    seq: int  # monotonic per-device sequence, persisted in the same txn
    event_type: EventType = Field(alias="type")
    client_ts: int  # epoch ms, client clock; display/analytics only
    payload: dict[str, Any] = Field(default_factory=dict)
    concept_id: Optional[str] = None
    chapter_id: Optional[str] = None
    question_id: Optional[str] = None

    model_config = {"populate_by_name": True}

    @model_validator(mode="before")
    @classmethod
    def _reconcile_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Accept legacy 'ts' for 'client_ts'
            if "client_ts" not in data and "ts" in data:
                data["client_ts"] = data["ts"]
            # Accept legacy lowercase wire types
            raw_type = data.get("type") or data.get("event_type")
            legacy_map = {
                "lesson_opened": "CONTENT_VIEWED",
                "mcq_answered": "ANSWER_SUBMITTED",
                "doubt_asked": "DOUBT_ASKED",
                "pack_installed": "PACK_INSTALLED",
            }
            if raw_type in legacy_map:
                data["type"] = legacy_map[raw_type]
            elif isinstance(raw_type, str):
                upper = raw_type.upper()
                if upper in {e.value for e in EventType}:
                    data["type"] = upper
        return data

    # Back-compat alias for older call sites/tests that used `.ts`.
    @property
    def ts(self) -> int:
        return self.client_ts


class PerEventResult(BaseModel):
    event_id: str
    seq: int
    outcome: Outcome
    effect: Optional[SyncEffect] = None
    reason: Optional[SyncReason] = None
    detail: str = ""


class SyncRequest(BaseModel):
    device_id: DeviceId
    learner_id: LearnerId
    from_seq: int = 0  # exclusive lower bound; client cursor
    events: list[LearnerEvent] = Field(default_factory=list)


class DecisionSummary(BaseModel):
    decision_id: str
    action: Action
    target_concept_id: str
    target_bloom_level: Optional[BloomLevel] = None
    delivery_mode: DeliveryMode
    background_actions: list[BackgroundAction]
    reason_code: str
    needs_help: bool = False
    ruleset_version: str


class SyncResponse(BaseModel):
    results: list[PerEventResult]
    mastery: list[MasteryRecord]
    bloom_mastery: list[BloomMasteryRecord] = Field(default_factory=list)
    decision: Optional[Decision] = None
    decision_status: Literal["computed", "deferred"] = "deferred"
    server_cursor: int
    ruleset_version: str
    # Back-compat fields for existing clients/tests
    accepted: list[PerEventResult] = Field(default_factory=list)
    server_learner_seq: int = 0
    canonical_mastery: list[MasteryRecord] = Field(default_factory=list)
    canonical_bloom_mastery: list[BloomMasteryRecord] = Field(default_factory=list)
    next_decision: Optional[Decision] = None


# --------------------------------------------------------------------------- #
# Assessment
# --------------------------------------------------------------------------- #
class AssessmentSubmission(BaseModel):
    question_id: QuestionId
    revision: int = 1
    attempt_id: Optional[str] = None
    selected_option: Optional[int] = None  # for MCQ
    answer_text: Optional[str] = None  # for short-answer
    duration_ms: int = 0
    submitted_at: int
    correct_claim: Optional[bool] = None
    seq: int = 0


class AssessmentResult(BaseModel):
    question_id: QuestionId
    attempt_id: Optional[str] = None
    correct: bool
    evidence: EvidenceType
    explanation_or: str
    concept_id: ConceptId
    bloom_level: Optional[BloomLevel] = None
    mastery_after: MasteryRecord
    bloom_mastery_after: Optional[BloomMasteryRecord] = None
    next_decision_id: str
    misconception_tag: Optional[str] = None
    remediation_or: Optional[str] = None


# --------------------------------------------------------------------------- #
# Decisions / trace
# --------------------------------------------------------------------------- #
class Decision(BaseModel):
    decision_id: str
    learner_id: Optional[LearnerId] = None
    ruleset_version: str
    target_concept_id: str
    target_bloom_level: Optional[BloomLevel] = None
    action: Action
    delivery_mode: DeliveryMode
    background_actions: list[BackgroundAction]
    reason_code: str
    reason_or: str
    needs_help: bool = False
    chapter_id: str = ""
    suggested_question_id: Optional[QuestionId] = None
    suggested_chunk_id: Optional[ChunkId] = None
    network: NetworkState = NetworkState.ONLINE
    source: Literal["server", "local"] = "server"
    produced_by: Literal["local_engine", "server_engine"] = "server_engine"
    created_at: int = 0


class TraceStep(BaseModel):
    step_id: str
    node: str
    stage: Optional[str] = None
    tool: Optional[str] = None
    provider: Optional[str] = None
    ruleset_version: Optional[str] = None
    model_id: Optional[str] = None
    status: Literal["ok", "error", "skipped", "fallback"]
    error_code: Optional[str] = None
    duration_ms: int
    retry: Optional[int] = None
    fallback: Optional[str] = None
    input_summary: dict[str, Any] = Field(default_factory=dict)
    output_summary: dict[str, Any] = Field(default_factory=dict)
    redacted: bool = True


class DecisionTrace(BaseModel):
    decision_id: str
    trace: list[TraceStep]


# --------------------------------------------------------------------------- #
# Doubt / retrieval / generation / translation
# --------------------------------------------------------------------------- #
class DoubtRequest(BaseModel):
    query: Annotated[str, StringConstraints(min_length=1, max_length=1000)]
    learner_id: LearnerId
    pack_ids: list[PackId] = Field(default_factory=list)
    concept_hint: Optional[str] = None


class RetrievedChunk(BaseModel):
    chunk_id: ChunkId
    concept_id: ConceptId
    chapter_id: ChapterId
    text_or: str
    source_ref: str
    score: float
    matched_terms: list[str] = Field(default_factory=list)


class RetrievedResult(BaseModel):
    chunks: list[RetrievedChunk]
    provider: str
    model_id: Optional[str] = None
    confidence: float = 0.0


class GeneratedAnswer(BaseModel):
    text_or: str
    citations: list[ChunkId] = Field(default_factory=list)
    chapter_refs: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    provenance: Literal["extractive", "llm_grounded", "basic"] = "extractive"
    basic_answer_status: Optional[str] = (
        None  # e.g. "provider_unavailable" / "out_of_lessons"
    )


class GenerationRecord(BaseModel):
    """Audit record for every generated text (Design v2 Sections 4/7)."""
    record_id: str
    decision_id: str
    provider: str
    model_id: Optional[str] = None
    prompt_version: str
    prompt_hash: str
    params: dict[str, Any] = Field(default_factory=dict)
    chunk_ids: list[str] = Field(default_factory=list)
    output_or: str = ""
    validation_results: dict[str, Any] = Field(default_factory=dict)
    fallback_used: bool = False
    created_at: int = 0


class DoubtResponse(BaseModel):
    answer: GeneratedAnswer
    retrieved: RetrievedResult
    decision_id: str
    translated_query: Optional[str] = None
    used_translation_tool: bool = False
    generation_record: Optional[GenerationRecord] = None


# --------------------------------------------------------------------------- #
# Packs
# --------------------------------------------------------------------------- #
class PackManifest(BaseModel):
    pack_id: PackId
    version: str
    content_version: str
    language: Literal["or", "en"] = "or"
    byte_size: int
    checksum_sha256: str
    archive_sha256: str = ""
    archive_byte_size: int = 0
    min_app_version: str
    chapters: list[ChapterId]
    licence: str
    source_refs: list[str] = Field(default_factory=list)
    created_at: int


class PackDownloadInfo(BaseModel):
    pack_id: PackId
    version: str
    url: str
    byte_size: int
    checksum_sha256: str
    archive_sha256: str = ""
    archive_byte_size: int = 0


# --------------------------------------------------------------------------- #
# Typed tool error (provider contract — Design v2 Section 5)
# --------------------------------------------------------------------------- #
class ToolError(BaseModel):
    error_code: Literal[
        "TIMEOUT",
        "RATE_LIMITED",
        "UNAVAILABLE",
        "BAD_OUTPUT",
        "LOW_CONFIDENCE",
        "UNSUPPORTED_LANGUAGE",
        "QUOTA_EXHAUSTED",
        # granular orchestration codes retained for typed diagnostics
        "ACCESS_RESTRICTED",
        "MODEL_DOWNLOAD_FAILED",
        "MISSING_WEIGHTS",
        "NOT_GROUNDED",
        "SCHEMA_INVALID",
    ] = "UNAVAILABLE"
    detail_dev: str = ""  # never shown to learners
    detail: str = ""  # back-compat alias of detail_dev
    provider: Optional[str] = None
    model_id: Optional[str] = None
    retryable: bool = False

    def model_post_init(self, __ctx) -> None:
        if self.detail_dev and not self.detail:
            self.detail = self.detail_dev
        elif self.detail and not self.detail_dev:
            self.detail_dev = self.detail


# --------------------------------------------------------------------------- #
# API responses
# --------------------------------------------------------------------------- #
class LearnerState(BaseModel):
    learner_id: LearnerId
    device_id: DeviceId
    mastery: list[MasteryRecord]
    bloom_mastery: list[BloomMasteryRecord] = Field(default_factory=list)
    active_pack_versions: dict[str, int]
    last_decision_id: Optional[str] = None
    outbox_depth: int = 0


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    RETRY = "retry"
    DEAD = "dead"


class JobRecord(BaseModel):
    job_id: str
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    dedupe_key: Optional[str] = None
    status: JobStatus = JobStatus.QUEUED
    attempts: int = 0
    max_attempts: int = 6
    next_run_at: int
    lease_expires_at: Optional[int] = None
    last_error: Optional[str] = None
    created_at: int
    updated_at: int


class JobsAdminResponse(BaseModel):
    counts: dict[str, int]
    dead_jobs: list[JobRecord]
    retrying_jobs: list[JobRecord]
    all_jobs: list[JobRecord]


class HealthResponse(BaseModel):
    status: str
    project: str = "SAARTHI"
    app_version: str
    env: str
    persistence: str
    translation_provider: str
    llm_provider: str
    retrieval_provider: str
    ruleset_version: str
    bkt_version: str
    has_hf_token: bool
    has_llm_key: bool
    request_id: str


__all__ = [
    # ids
    "LearnerId",
    "DeviceId",
    "ConceptId",
    "ChapterId",
    "ChunkId",
    "QuestionId",
    "PackId",
    "new_request_id",
    "new_learner_id",
    "new_device_id",
    "new_decision_id",
    "new_event_id",
    "new_session_id",
    # enums
    "NetworkState",
    "Action",
    "DeliveryMode",
    "BackgroundAction",
    "EventType",
    "EvidenceType",
    "Outcome",
    "SyncEffect",
    "SyncReason",
    "BloomLevel",
    # learner/auth
    "LearnerProfileCreate",
    "LearnerProfile",
    "DeviceRegistration",
    "DeviceTokenResponse",
    "DeviceToken",
    "AuthChallenge",
    "AuthChallengeRequest",
    "AuthRenewRequest",
    "RefreshRequest",
    "AuthResponse",
    # curriculum
    "GlossaryEntry",
    "Concept",
    "Chunk",
    "QuestionOption",
    "Question",
    "Chapter",
    # env/mastery/event
    "EnvironmentSnapshot",
    "MasteryRecord",
    "BloomMasteryRecord",
    "LearnerEvent",
    "PerEventResult",
    "SyncRequest",
    "SyncResponse",
    "DecisionSummary",
    # assessment
    "AssessmentSubmission",
    "AssessmentResult",
    # decision/trace
    "Decision",
    "TraceStep",
    "DecisionTrace",
    # doubt/retrieval/generation/translation
    "DoubtRequest",
    "RetrievedChunk",
    "RetrievedResult",
    "GeneratedAnswer",
    "GenerationRecord",
    "DoubtResponse",
    "ToolError",
    # pack
    "PackManifest",
    "PackDownloadInfo",
    # api
    "LearnerState",
    "HealthResponse",
    # jobs
    "JobStatus",
    "JobRecord",
    "JobsAdminResponse",
]
