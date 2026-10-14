"""Repository interfaces — abstract base classes.

Concrete adapters live in `adapters/persistence/`. The API/services layer
depends only on these interfaces, never on SQLAlchemy or the driver.
"""

from __future__ import annotations

import abc
from typing import Optional

from ..domain.schemas import (
    BloomMasteryRecord,
    Decision,
    DecisionTrace,
    GenerationRecord,
    LearnerEvent,
    LearnerProfile,
    MasteryRecord,
    Outcome,
    PerEventResult,
    PackManifest,
)


class LearnerRepository(abc.ABC):
    @abc.abstractmethod
    async def create_learner(self, profile: LearnerProfile, device_id: str) -> None: ...

    @abc.abstractmethod
    async def get_learner(self, learner_id: str) -> Optional[LearnerProfile]: ...

    @abc.abstractmethod
    async def list_learners_on_device(self, device_id: str) -> list[LearnerProfile]: ...

    @abc.abstractmethod
    async def activate_learner_on_device(
        self, learner_id: str, device_id: str
    ) -> None: ...

    @abc.abstractmethod
    async def deactivate_learner_on_device(self, device_id: str) -> Optional[str]: ...

    @abc.abstractmethod
    async def get_active_learner_on_device(
        self, device_id: str
    ) -> Optional[LearnerProfile]: ...

    @abc.abstractmethod
    async def is_learner_linked(self, learner_id: str, device_id: str) -> bool:
        """True when the learner has an ACTIVE device_profiles link to the device."""
        ...


class DeviceRepository(abc.ABC):
    @abc.abstractmethod
    async def register_device(
        self, device_id: str, hardware_label: str, public_key_spki: str | None = None
    ) -> None: ...

    @abc.abstractmethod
    async def get_public_key(self, device_id: str) -> Optional[str]: ...

    @abc.abstractmethod
    async def is_revoked(self, device_id: str) -> bool: ...

    @abc.abstractmethod
    async def revoke_device(self, device_id: str) -> None: ...

    @abc.abstractmethod
    async def touch_last_seen(self, device_id: str) -> None: ...

    # ---- short-lived access tokens -------------------------------------
    @abc.abstractmethod
    async def issue_access_token(
        self, device_id: str, token_hash: str, issued_at: int, expires_at: int
    ) -> None: ...

    @abc.abstractmethod
    async def verify_access_token(self, token_hash: str) -> Optional[tuple[str, int]]:
        """Return (device_id, expires_at) if valid, unrevoked and unexpired."""
        ...

    @abc.abstractmethod
    async def revoke_access_tokens(self, device_id: str) -> None: ...

    # ---- rotating refresh tokens ----------------------------------------
    @abc.abstractmethod
    async def issue_refresh_token(
        self, device_id: str, token_hash: str, issued_at: int, expires_at: int
    ) -> str: ...

    @abc.abstractmethod
    async def consume_refresh_token(self, token_hash: str) -> Optional[str]:
        """Mark the refresh token used; return its device_id, or None."""
        ...

    @abc.abstractmethod
    async def revoke_refresh_tokens(self, device_id: str) -> None: ...

    # ---- signed-nonce challenges ----------------------------------------
    @abc.abstractmethod
    async def store_challenge(
        self, device_id: str, nonce: str, created_at: int, expires_at: int
    ) -> None: ...

    @abc.abstractmethod
    async def consume_challenge(self, device_id: str, nonce: str) -> bool:
        """Mark the nonce used; True when it existed, was unused, unexpired."""
        ...


class EventRepository(abc.ABC):
    @abc.abstractmethod
    async def insert_event(self, ev: LearnerEvent) -> PerEventResult: ...

    """Idempotent insert; returns ACCEPTED on first insert, DUPLICATE on repeats."""

    @abc.abstractmethod
    async def insert_rejected_tombstone(self, ev: LearnerEvent, reason: str) -> None:
        """Store a permanently rejected event as a tombstone so its (device, seq)
        is consumed and later events are not blocked. Diagnostic info kept."""
        ...

    @abc.abstractmethod
    async def event_with_same_seq(
        self, device_id: str, seq: int
    ) -> Optional[LearnerEvent]:
        """The stored event for (device_id, seq), if any (conflict detection)."""
        ...

    @abc.abstractmethod
    async def learner_attempt_ids(self, learner_id: str) -> set[str]:
        """attempt_ids already seen for this learner (first-time guard)."""
        ...

    @abc.abstractmethod
    async def list_events(
        self, learner_id: str, since_seq: int = 0, limit: int = 1000
    ) -> list[LearnerEvent]: ...

    @abc.abstractmethod
    async def get_sync_cursor(
        self, device_id: str, learner_id: str
    ) -> tuple[int, int]: ...

    """Return (last_acked_seq, last_server_seq)."""

    @abc.abstractmethod
    async def bump_sync_cursor(
        self, device_id: str, learner_id: str, last_acked_seq: int, last_server_seq: int
    ) -> None: ...

    @abc.abstractmethod
    async def move_to_dead_letter(
        self, ev: LearnerEvent, reason: str, error_code: str
    ) -> None: ...


class MasteryRepository(abc.ABC):
    @abc.abstractmethod
    async def get_mastery(self, learner_id: str) -> list[MasteryRecord]: ...

    @abc.abstractmethod
    async def upsert_mastery(
        self,
        learner_id: str,
        concept_id: str,
        p_bp: int,
        band: str,
        attempts: int,
        correct: int,
        last_event_seq: int,
        bkt_version: str = "1",
    ) -> None: ...

    @abc.abstractmethod
    async def replace_mastery_snapshot(
        self, learner_id: str, snapshot: list[MasteryRecord]
    ) -> None: ...

    @abc.abstractmethod
    async def get_bloom_mastery(
        self, learner_id: str, concept_id: Optional[str] = None
    ) -> list[BloomMasteryRecord]: ...

    @abc.abstractmethod
    async def upsert_bloom_mastery(
        self,
        learner_id: str,
        concept_id: str,
        bloom_level: str,
        p_bp: int,
        band: str,
        attempts: int,
        correct: int,
        last_event_seq: int,
        bkt_version: str = "1",
    ) -> None: ...

    @abc.abstractmethod
    async def replace_bloom_mastery_snapshot(
        self, learner_id: str, snapshot: list[BloomMasteryRecord]
    ) -> None: ...


class DecisionRepository(abc.ABC):
    @abc.abstractmethod
    async def save_decision(self, decision: Decision) -> None: ...

    @abc.abstractmethod
    async def save_trace(self, decision_id: str, trace: DecisionTrace) -> None: ...

    @abc.abstractmethod
    async def get_decision(self, decision_id: str) -> Optional[Decision]: ...

    @abc.abstractmethod
    async def get_decision_for_learner(self, decision_id: str,
                                       learner_id: str) -> Optional[Decision]:
        """Ownership-enforcing read: returns the decision only when it belongs
        to learner_id (prevents cross-profile access)."""
        ...

    @abc.abstractmethod
    async def get_trace(self, decision_id: str) -> Optional[DecisionTrace]: ...

    @abc.abstractmethod
    async def list_recent_decisions(
        self, learner_id: str, limit: int = 10
    ) -> list[Decision]: ...


class GenerationRecordRepository(abc.ABC):
    @abc.abstractmethod
    async def save(self, record: GenerationRecord) -> None: ...

    @abc.abstractmethod
    async def list_for_decision(self, decision_id: str) -> list[GenerationRecord]: ...


class PackRepository(abc.ABC):
    @abc.abstractmethod
    async def upsert_pack_manifest(self, manifest: PackManifest) -> None: ...

    @abc.abstractmethod
    async def list_pack_manifests(self) -> list[PackManifest]: ...

    @abc.abstractmethod
    async def get_pack_manifest(
        self, pack_id: str, version: str
    ) -> Optional[PackManifest]: ...

    @abc.abstractmethod
    async def record_installed_pack(
        self, device_id: str, pack_id: str, version: str, byte_size: int, checksum: str
    ) -> None: ...

    @abc.abstractmethod
    async def list_installed_packs(self, device_id: str) -> list[tuple[str, str]]: ...


class JobRepository(abc.ABC):
    """Durable job repository (Design v2 Section 5 & 14).
    PostgreSQL/SQLite job table is the source of truth, so a lost queue loses nothing.
    """
    @abc.abstractmethod
    async def enqueue(
        self,
        job_type: str,
        payload: dict,
        dedupe_key: Optional[str] = None,
        max_attempts: int = 6,
        delay_s: int = 0,
    ) -> "JobRecord": ...

    @abc.abstractmethod
    async def acquire_next_job(
        self, worker_id: str, lease_duration_s: int = 60
    ) -> Optional["JobRecord"]: ...

    @abc.abstractmethod
    async def complete_job(self, job_id: str) -> None: ...

    @abc.abstractmethod
    async def fail_job(
        self, job_id: str, error: str, retryable: bool
    ) -> None: ...

    @abc.abstractmethod
    async def reconcile_expired_leases(self) -> int: ...

    @abc.abstractmethod
    async def list_jobs(
        self, statuses: Optional[list[str]] = None, limit: int = 50
    ) -> list["JobRecord"]: ...

    @abc.abstractmethod
    async def count_by_status(self) -> dict[str, int]: ...


__all__ = [
    "LearnerRepository",
    "DeviceRepository",
    "EventRepository",
    "MasteryRepository",
    "DecisionRepository",
    "GenerationRecordRepository",
    "PackRepository",
    "JobRepository",
]
