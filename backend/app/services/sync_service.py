"""Sync service v2 — transactional ingestion, per-event outcomes, replay.

Design v2 contract (Sections 5, 8, 9):

- The batch is ONE database transaction: idempotent event inserts, the
  mastery projection update in canonical sequence order, and the cursor
  advance commit together. A failed batch returns RETRYABLE for every
  event (HTTP 503 at the route) and nothing is partially applied.
- Exactly one outcome per submitted event: ACCEPTED, DUPLICATE,
  RETRYABLE or REJECTED. Rejected events are stored as tombstones so a
  rejected event never blocks later events; the phone quarantines them.
- PAYLOAD_CONFLICT: the same (device_id, seq) arriving with a different
  event_id or payload is a permanent rejection, recorded with diagnostics.
- The post-sync decision is computed AFTER the transaction commits; a
  failed decision never rolls back accepted events — the response says
  decision_status=deferred and the phone keeps its local decision.
- A late event (seq at or below the last applied seq) triggers a full
  rebuild of the learner's projection by replaying ALL accepted events in
  seq order. Incremental updates are used only when every incoming seq is
  newer than the last applied seq.
- Only valid, first-time graded answers (ANSWER_SUBMITTED) update
  mastery; repeats are ACCEPTED with reason REPEAT_SUBMISSION and unknown/
  legacy question revisions are ACCEPTED with reason LEGACY_QUESTION
  (both effect none). The server regrades from its own answer key.
"""
from __future__ import annotations

import json
from typing import Optional

from sqlalchemy import text

from ..content.pack_loader import PackContentIndex
from ..core.logging import get_logger
from ..core.metrics import get_registry
from ..core.settings import get_settings
from ..core.errors import ErrorCode, SaarthiError
from ..domain.bkt import (
    bkt_update_bp, mastery_band_bp, mastery_effect_for_event,
)
from ..domain.bloom import BloomLevel, parse_bloom_level
from ..domain.decide import decide
from ..domain.ruleset import get_ruleset
from ..domain.schemas import (
    BloomMasteryRecord, EventType, LearnerEvent, MasteryRecord, NetworkState, Outcome,
    PerEventResult, SyncEffect, SyncReason, SyncRequest, SyncResponse,
)
from ..repositories import (
    DecisionRepository, EventRepository, MasteryRepository, PackRepository,
)
from ..adapters.persistence import Persistence

log = get_logger("saarthi.sync")


def _etype(ev: LearnerEvent) -> str:
    return ev.event_type.value if hasattr(ev.event_type, "value") else str(ev.event_type)


class SyncService:
    def __init__(self, events: EventRepository, mastery: MasteryRepository,
                 decisions: DecisionRepository, pack: PackContentIndex | None = None,
                 persistence: Persistence | None = None,
                 pack_repo: PackRepository | None = None) -> None:
        self.events = events
        self.mastery = mastery
        self.decisions = decisions
        self.pack = pack
        self.persistence = persistence
        self.pack_repo = pack_repo
        self.settings = get_settings()

    # ------------------------------------------------------------------ #
    # Entry point
    # ------------------------------------------------------------------ #
    async def sync(self, req: SyncRequest) -> SyncResponse:
        ruleset = get_ruleset()
        batch_size = int(ruleset.sync.get("batch_size", 100))
        if len(req.events) > batch_size:
            raise SaarthiError(ErrorCode.SYNC_BATCH_TOO_LARGE, status=400,
                               detail=f"batch > {batch_size} events")
        # Canonical submission order: strictly ascending seq.
        seqs = [e.seq for e in req.events]
        if seqs != sorted(seqs) or len(set(seqs)) != len(seqs):
            raise SaarthiError(ErrorCode.SYNC_ORDERING_CONFLICT, status=400,
                               detail="events must be in ascending seq order; "
                                      "sort and retry")

        results: dict[str, PerEventResult] = {}  # keyed by event_id

        # ---- Ownership: mismatch is a permanent, tombstoned rejection ----
        owned: list[LearnerEvent] = []
        for ev in req.events:
            if ev.learner_id != req.learner_id or ev.device_id != req.device_id:
                results[ev.event_id] = PerEventResult(
                    event_id=ev.event_id, seq=ev.seq, outcome=Outcome.REJECTED,
                    effect=SyncEffect.NONE, reason=SyncReason.LEARNER_NOT_LINKED,
                    detail="event learner/device mismatch",
                )
                await self.events.insert_rejected_tombstone(
                    ev, SyncReason.LEARNER_NOT_LINKED.value)
                get_registry().api_errors.inc(error_code="sync_event_rejected")
            else:
                owned.append(ev)

        # ---- ONE transaction: inserts + projection + cursor --------------
        transaction_failed = False
        if self.persistence is not None and owned:
            try:
                results.update(await self._ingest_transaction(req, owned, ruleset))
            except SaarthiError:
                raise
            except Exception as e:  # noqa: BLE001 — whole batch RETRYABLE
                log.warning("sync_batch_failed err=%s", e)
                transaction_failed = True
        elif owned:
            # Legacy path without a persistence handle (per-event commits).
            results.update(await self._ingest_per_event(owned, ruleset))

        if transaction_failed:
            for ev in owned:
                if ev.event_id not in results or \
                        results[ev.event_id].outcome in (Outcome.RETRYABLE,):
                    results[ev.event_id] = PerEventResult(
                        event_id=ev.event_id, seq=ev.seq, outcome=Outcome.RETRYABLE,
                        reason=SyncReason.SERVER_BUSY,
                        detail="batch transaction failed; nothing applied")
            return await self._assemble(req, results, ruleset,
                                        decision_status="deferred", decision=None)

        # ---- Late arrival → full replay; else projection already applied -
        accepted = [ev for ev in owned
                    if results.get(ev.event_id)
                    and results[ev.event_id].outcome == Outcome.ACCEPTED
                    and results[ev.event_id].effect == SyncEffect.MASTERY_UPDATED]
        if accepted:
            last_applied = await self._last_applied_seq(req.learner_id)
            if min(ev.seq for ev in accepted) <= last_applied:
                await self._rebuild_projection(req.learner_id, ruleset)

        # ---- Cursor -------------------------------------------------------
        acked = [r.seq for r in results.values()
                 if r.outcome in (Outcome.ACCEPTED, Outcome.DUPLICATE)]
        rejected = [r.seq for r in results.values() if r.outcome == Outcome.REJECTED]
        cursor = max(acked + rejected + [0])
        last_server_seq = (await self.events.get_sync_cursor(req.device_id, req.learner_id))[1]
        await self.events.bump_sync_cursor(req.device_id, req.learner_id,
                                           cursor, max(last_server_seq, cursor))

        # ---- Post-commit decision (never rolls back accepted events) -----
        decision: Optional[Decision] = None
        decision_status = "deferred"
        try:
            decision = await self._post_sync_decision(req, ruleset)
            decision_status = "computed"
        except Exception as e:  # noqa: BLE001
            log.warning("sync_next_decision_failed err=%s", e)

        return await self._assemble(req, results, ruleset,
                                    decision_status=decision_status,
                                    decision=decision)

    # ------------------------------------------------------------------ #
    # Transactional ingestion (Design v2 Section 5/8)
    # ------------------------------------------------------------------ #
    async def _ingest_transaction(self, req: SyncRequest, owned: list[LearnerEvent],
                                  ruleset) -> dict[str, PerEventResult]:
        from ..adapters.persistence.repositories import SqlEventRepository
        assert isinstance(self.events, SqlEventRepository)
        assert isinstance(self.persistence, Persistence)
        results: dict[str, PerEventResult] = {}
        async with self.persistence.transaction() as s:
            # 1. Idempotent inserts + immediate effect classification
            accepted: list[LearnerEvent] = []
            seen_attempt_ids = await self._session_attempt_ids(s, req.learner_id)
            for ev in owned:
                r = await self.events._insert_event_session(s, ev)
                if r.outcome != Outcome.ACCEPTED:
                    # DUPLICATE: keep as-is (no effect, no re-classification).
                    # REJECTED (PAYLOAD_CONFLICT): diagnostics, consumed seq.
                    if r.outcome == Outcome.REJECTED:
                        await self._session_dead_letter(
                            s, ev, r.reason.value if r.reason else "PAYLOAD_CONFLICT")
                    results[ev.event_id] = r
                    continue
                cls = self._classify(ev, seen_attempt_ids, ruleset)
                if cls.outcome == Outcome.REJECTED:
                    # Permanently invalid: tombstone the stored row so the seq
                    # is consumed and later events are not blocked.
                    await s.execute(
                        text("UPDATE learner_events SET status = 'rejected', "
                             "effect = 'none', reason = :reason WHERE event_id = :eid"),
                        {"reason": cls.reason.value if cls.reason else "INVALID_PAYLOAD",
                         "eid": ev.event_id})
                    await self._session_dead_letter(s, ev,
                                                    cls.reason.value if cls.reason else "INVALID_PAYLOAD")
                    results[ev.event_id] = cls
                    continue
                results[ev.event_id] = cls
                if cls.effect == SyncEffect.MASTERY_UPDATED:
                    accepted.append(ev)
                    seen_attempt_ids.add(str(ev.payload.get("attempt_id") or ev.event_id))
            # 2. Mastery projection in canonical order, inside the txn
            if accepted:
                last_applied = await self._session_last_applied_seq(s, req.learner_id)
                if min(ev.seq for ev in accepted) > last_applied:
                    await self._session_apply(s, req.learner_id, accepted, ruleset)
                else:
                    # Late/out-of-order arrival: rebuild by full replay.
                    await self._session_replay(s, req.learner_id, ruleset)
                for ev in accepted:
                    if _etype(ev) == "PACK_INSTALLED" and self.pack_repo is not None:
                        try:
                            payload = ev.payload or {}
                            p_id = payload.get("pack_id")
                            ver = payload.get("version")
                            if p_id and ver:
                                await self.pack_repo.record_installed_pack(
                                    ev.device_id, p_id, str(ver),
                                    int(payload.get("byte_size", 0)),
                                    str(payload.get("checksum_sha256", "")),
                                )
                        except Exception as ex:
                            log.warning("sync_pack_installed_record_failed err=%s", ex)
            # 3. Advance the device cursor inside the same txn
            acked = [r.seq for r in results.values()
                     if r.outcome in (Outcome.ACCEPTED, Outcome.DUPLICATE)]
            rejected = [r.seq for r in results.values()
                        if r.outcome == Outcome.REJECTED]
            cursor = max(acked + rejected + [0])
            await s.execute(
                text("INSERT INTO sync_cursors (device_id, learner_id, last_acked_seq, "
                     "last_server_seq, last_acked_at) VALUES (:did, :lid, :a, :sv, :ts) "
                     "ON CONFLICT(device_id, learner_id) DO UPDATE SET "
                     "last_acked_seq = MAX(sync_cursors.last_acked_seq, :a), "
                     "last_server_seq = MAX(sync_cursors.last_server_seq, :sv), "
                     "last_acked_at = :ts"),
                {"did": req.device_id, "lid": req.learner_id, "a": cursor,
                 "sv": cursor, "ts": int(__import__("time").time() * 1000)},
            )
        return results

    async def _session_dead_letter(self, s, ev: LearnerEvent, reason: str) -> None:
        await s.execute(
            text("INSERT OR REPLACE INTO dead_letter_events "
                 "(event_id, device_id, learner_id, seq, reason, last_error_code, "
                 " received_at, dead_at) VALUES (:eid, :did, :lid, :seq, :r, :ec, :recv, :now)"),
            {"eid": ev.event_id, "did": ev.device_id, "lid": ev.learner_id,
             "seq": ev.seq, "r": reason, "ec": reason,
             "recv": int(__import__("time").time() * 1000),
             "now": int(__import__("time").time() * 1000)})


    async def _ingest_per_event(self, owned: list[LearnerEvent],
                                ruleset) -> dict[str, PerEventResult]:
        results: dict[str, PerEventResult] = {}
        accepted: list[LearnerEvent] = []
        for ev in owned:
            try:
                r = await self.events.insert_event(ev)
            except Exception as e:  # noqa: BLE001
                log.warning("sync_insert_failed event_id=%s seq=%s err=%s",
                            ev.event_id, ev.seq, e)
                results[ev.event_id] = PerEventResult(
                    event_id=ev.event_id, seq=ev.seq, outcome=Outcome.RETRYABLE,
                    reason=SyncReason.SERVER_BUSY,
                    detail=f"transient: {type(e).__name__}")
                continue
            if r.outcome == Outcome.REJECTED and r.reason == SyncReason.PAYLOAD_CONFLICT:
                await self.events.move_to_dead_letter(
                    ev, SyncReason.PAYLOAD_CONFLICT.value, "PAYLOAD_CONFLICT")
            results[ev.event_id] = r
            if r.outcome == Outcome.ACCEPTED:
                accepted.append(ev)
        if accepted:
            last_applied = await self._last_applied_seq(owned[0].learner_id)
            if min(ev.seq for ev in accepted) > last_applied:
                await self._incremental_projection(owned[0].learner_id, accepted, ruleset)
            else:
                await self._rebuild_projection(owned[0].learner_id, ruleset)
            for ev in accepted:
                if _etype(ev) == "PACK_INSTALLED" and self.pack_repo is not None:
                    try:
                        payload = ev.payload or {}
                        p_id = payload.get("pack_id")
                        ver = payload.get("version")
                        if p_id and ver:
                            await self.pack_repo.record_installed_pack(
                                ev.device_id, p_id, str(ver),
                                int(payload.get("byte_size", 0)),
                                str(payload.get("checksum_sha256", "")),
                            )
                    except Exception as ex:
                        log.warning("sync_pack_installed_record_failed err=%s", ex)
        return results

    # ------------------------------------------------------------------ #
    # Effect classification (deterministic, per event)
    # ------------------------------------------------------------------ #
    def _classify(self, ev: LearnerEvent, seen_attempt_ids: set[str],
                  ruleset) -> PerEventResult:
        etype = _etype(ev)
        if etype not in {e.value for e in EventType}:
            return PerEventResult(
                event_id=ev.event_id, seq=ev.seq, outcome=Outcome.REJECTED,
                effect=SyncEffect.NONE, reason=SyncReason.UNKNOWN_EVENT_TYPE,
                detail=f"unknown event type {etype!r}")
        if etype != "ANSWER_SUBMITTED":
            return PerEventResult(
                event_id=ev.event_id, seq=ev.seq, outcome=Outcome.ACCEPTED,
                effect=SyncEffect.NONE, reason=None, detail="")
        effect = mastery_effect_for_event(ev, ruleset, seen_attempt_ids,
                                          question_lookup=self._question_lookup())
        if effect.reason == "REPEAT_SUBMISSION":
            return PerEventResult(
                event_id=ev.event_id, seq=ev.seq, outcome=Outcome.ACCEPTED,
                effect=SyncEffect.NONE, reason=SyncReason.REPEAT_SUBMISSION,
                detail="repeated attempt_id; no mastery effect")
        if effect.reason == "LEGACY_QUESTION":
            return PerEventResult(
                event_id=ev.event_id, seq=ev.seq, outcome=Outcome.ACCEPTED,
                effect=SyncEffect.NONE, reason=SyncReason.LEGACY_QUESTION,
                detail="unknown/legacy question revision; no mastery effect")
        if effect.reason == "INVALID_PAYLOAD":
            return PerEventResult(
                event_id=ev.event_id, seq=ev.seq, outcome=Outcome.REJECTED,
                effect=SyncEffect.NONE, reason=SyncReason.INVALID_PAYLOAD,
                detail="invalid ANSWER_SUBMITTED payload")
        return PerEventResult(
            event_id=ev.event_id, seq=ev.seq, outcome=Outcome.ACCEPTED,
            effect=SyncEffect.MASTERY_UPDATED, reason=None, detail="")

    # ------------------------------------------------------------------ #
    # Question lookup — the server regrades from its own key
    # ------------------------------------------------------------------ #
    def _question_lookup(self):
        if self.pack is None:
            return None

        class _Q:
            def __init__(self, q):
                self.q = q

            @property
            def concept_id(self):
                return self.q.concept_id

            def correct(self, response) -> bool:
                if self.q.qtype == "mcq":
                    try:
                        return int(response) == int(self.q.correct_option)
                    except (TypeError, ValueError):
                        return False
                norm = " ".join(str(response or "").lower().split())
                expected = [c.lower() for c in self.q.expected_concepts or []]
                return bool(expected) and all(c in norm for c in expected)

        def lookup(question_id, revision):
            q = self.pack.get_question(question_id) if self.pack else None
            if q is None:
                return None  # unknown question → LEGACY_QUESTION
            if revision is not None and str(revision) != str(getattr(q, "revision", 1)):
                return None  # event made against an unknown revision
            if getattr(q, "status", "active") != "active":
                return None
            return _Q(q)
        return lookup

    # ------------------------------------------------------------------ #
    # Projection helpers (session-scoped for the transaction; repo-scoped
    # for the legacy path)
    # ------------------------------------------------------------------ #
    async def _last_applied_seq(self, learner_id: str) -> int:
        current = await self.mastery.get_mastery(learner_id)
        return max((m.last_event_seq or 0 for m in current), default=0)

    async def _session_last_applied_seq(self, s, learner_id: str) -> int:
        res = await s.execute(
            text("SELECT MAX(last_event_seq) FROM learner_progress WHERE learner_id = :lid"),
            {"lid": learner_id},
        )
        row = res.fetchone()
        return int(row[0] or 0)

    async def _session_attempt_ids(self, s, learner_id: str) -> set[str]:
        res = await s.execute(
            text("SELECT payload_json FROM learner_events "
                 "WHERE learner_id = :lid AND event_type = 'ANSWER_SUBMITTED' "
                 "AND status = 'accepted'"),
            {"lid": learner_id},
        )
        out: set[str] = set()
        for (payload_json,) in res.fetchall():
            try:
                aid = (json.loads(payload_json or "{}") or {}).get("attempt_id")
            except Exception:
                aid = None
            if aid:
                out.add(str(aid))
        return out

    async def _session_mastery(self, s, learner_id: str) -> dict[str, MasteryRecord]:
        res = await s.execute(
            text("SELECT concept_id, p_bp, band, attempts, correct, last_event_seq "
                 "FROM learner_progress WHERE learner_id = :lid"),
            {"lid": learner_id},
        )
        return {row[0]: MasteryRecord(
            concept_id=row[0], p_bp=int(row[1] if row[1] is not None else 2000),
            band=row[2] or "weak", attempts=int(row[3] or 0),
            correct=int(row[4] or 0), last_event_seq=int(row[5] or 0),
        ) for row in res.fetchall()}

    async def _session_bloom_mastery(self, s, learner_id: str) -> dict[tuple[str, str], BloomMasteryRecord]:
        res = await s.execute(
            text("SELECT concept_id, bloom_level, p_bp, band, attempts, correct, last_event_seq "
                 "FROM learner_bloom_progress WHERE learner_id = :lid"),
            {"lid": learner_id},
        )
        return {(row[0], row[1]): BloomMasteryRecord(
            concept_id=row[0], bloom_level=parse_bloom_level(row[1]),
            p_bp=int(row[2] if row[2] is not None else 2000),
            band=row[3] or "weak", attempts=int(row[4] or 0),
            correct=int(row[5] or 0), last_event_seq=int(row[6] or 0),
        ) for row in res.fetchall()}

    async def _session_upsert(self, s, learner_id: str, cid: str, p_bp: int,
                              band: str, attempts: int, correct: int,
                              seq: int) -> None:
        await s.execute(
            text("INSERT INTO learner_progress (learner_id, concept_id, p_bp, band, "
                 "attempts, correct, last_event_seq, bkt_version) "
                 "VALUES (:lid, :cid, :p, :b, :a, :c, :seq, :bv) "
                 "ON CONFLICT(learner_id, concept_id) DO UPDATE SET "
                 "p_bp = :p, band = :b, attempts = :a, correct = :c, last_event_seq = :seq"),
            {"lid": learner_id, "cid": cid, "p": int(p_bp), "b": band,
             "a": attempts, "c": correct, "seq": int(seq),
             "bv": get_ruleset().bkt_version},
        )

    async def _session_upsert_bloom(self, s, learner_id: str, cid: str, bl: str,
                                    p_bp: int, band: str, attempts: int,
                                    correct: int, seq: int) -> None:
        await s.execute(
            text("INSERT INTO learner_bloom_progress (learner_id, concept_id, bloom_level, "
                 "p_bp, band, attempts, correct, last_event_seq, bkt_version) "
                 "VALUES (:lid, :cid, :bl, :p, :b, :a, :c, :seq, :bv) "
                 "ON CONFLICT(learner_id, concept_id, bloom_level) DO UPDATE SET "
                 "p_bp = :p, band = :b, attempts = :a, correct = :c, last_event_seq = :seq"),
            {"lid": learner_id, "cid": cid, "bl": bl, "p": int(p_bp), "b": band,
             "a": attempts, "c": correct, "seq": int(seq),
             "bv": get_ruleset().bkt_version},
        )

    def _event_bloom_level(self, ev: LearnerEvent) -> str:
        bl = ev.payload.get("bloom_level")
        if bl:
            return bl.lower()
        qid = ev.question_id or ev.payload.get("question_id")
        if qid and self.pack:
            q = self.pack.get_question(qid)
            if q and getattr(q, "bloom_level", None):
                lvl = q.bloom_level
                return (lvl.value if hasattr(lvl, "value") else str(lvl)).lower()
        return "remember"

    async def _session_apply(self, s, learner_id: str,
                             accepted: list[LearnerEvent], ruleset) -> None:
        """Apply mastery-updated events to the projection inside the open
        transaction, in canonical seq order, starting from stored integers."""
        current = await self._session_mastery(s, learner_id)
        current_bloom = await self._session_bloom_mastery(s, learner_id)
        for ev in sorted(accepted, key=lambda e: e.seq):
            cid = ev.concept_id or ev.payload.get("concept_id")
            if not cid:
                continue
            effect = mastery_effect_for_event(ev, ruleset, set(),
                                              question_lookup=self._question_lookup())
            correct = bool(effect.correct)
            m = current.get(cid)
            p_prior = m.p_bp if m else int(ruleset.bkt.get("p_init_bp", 2000))
            p_next = bkt_update_bp(p_prior, correct, ruleset, cid)
            attempts = (m.attempts if m else 0) + 1
            correct_n = (m.correct if m else 0) + (1 if correct else 0)
            band = mastery_band_bp(p_next, ruleset)
            await self._session_upsert(s, learner_id, cid, p_next, band,
                                       attempts, correct_n, ev.seq)
            current[cid] = MasteryRecord(concept_id=cid, p_bp=p_next, band=band,
                                         attempts=attempts, correct=correct_n,
                                         last_event_seq=ev.seq)

            bl_str = self._event_bloom_level(ev)
            bm = current_bloom.get((cid, bl_str))
            bm_prior = bm.p_bp if bm else int(ruleset.bkt.get("p_init_bp", 2000))
            bm_next = bkt_update_bp(bm_prior, correct, ruleset, cid)
            bm_attempts = (bm.attempts if bm else 0) + 1
            bm_correct_n = (bm.correct if bm else 0) + (1 if correct else 0)
            bm_band = mastery_band_bp(bm_next, ruleset)
            await self._session_upsert_bloom(s, learner_id, cid, bl_str, bm_next, bm_band,
                                             bm_attempts, bm_correct_n, ev.seq)
            current_bloom[(cid, bl_str)] = BloomMasteryRecord(
                concept_id=cid, bloom_level=parse_bloom_level(bl_str),
                p_bp=bm_next, band=bm_band, attempts=bm_attempts,
                correct=bm_correct_n, last_event_seq=ev.seq,
            )

    async def _session_replay(self, s, learner_id: str, ruleset) -> None:
        """Canonical replay inside the transaction: rebuild the projection
        from ALL accepted events in seq order (correctness oracle)."""
        res = await s.execute(
            text("SELECT event_id, device_id, learner_id, seq, client_ts, event_type, "
                 "concept_id, chapter_id, question_id, payload_json "
                 "FROM learner_events WHERE learner_id = :lid AND status = 'accepted' "
                 "ORDER BY seq, server_seq LIMIT 200000"),
            {"lid": learner_id},
        )
        events = [LearnerEvent(
            event_id=r[0], device_id=r[1], learner_id=r[2], seq=r[3],
            client_ts=r[4] or 0, event_type=r[5], concept_id=r[6],
            chapter_id=r[7], question_id=r[8],
            payload=json.loads(r[9] or "{}"),
        ) for r in res.fetchall()]
        seen: set[str] = set()
        current: dict[str, MasteryRecord] = {}
        current_bloom: dict[tuple[str, str], BloomMasteryRecord] = {}
        for ev in events:  # already in canonical order
            effect = mastery_effect_for_event(ev, ruleset, seen,
                                              question_lookup=self._question_lookup())
            if effect.effect != "mastery_updated":
                continue
            seen.add(str(ev.payload.get("attempt_id") or ev.event_id))
            cid = effect.concept_id
            m = current.get(cid)
            p_prior = m.p_bp if m else int(ruleset.bkt.get("p_init_bp", 2000))
            p_next = bkt_update_bp(p_prior, bool(effect.correct), ruleset, cid)
            attempts = (m.attempts if m else 0) + 1
            correct_n = (m.correct if m else 0) + (1 if effect.correct else 0)
            band = mastery_band_bp(p_next, ruleset)
            current[cid] = MasteryRecord(concept_id=cid, p_bp=p_next, band=band,
                                         attempts=attempts, correct=correct_n,
                                         last_event_seq=ev.seq)

            bl_str = self._event_bloom_level(ev)
            bm = current_bloom.get((cid, bl_str))
            bm_prior = bm.p_bp if bm else int(ruleset.bkt.get("p_init_bp", 2000))
            bm_next = bkt_update_bp(bm_prior, bool(effect.correct), ruleset, cid)
            bm_attempts = (bm.attempts if bm else 0) + 1
            bm_correct_n = (bm.correct if bm else 0) + (1 if effect.correct else 0)
            bm_band = mastery_band_bp(bm_next, ruleset)
            current_bloom[(cid, bl_str)] = BloomMasteryRecord(
                concept_id=cid, bloom_level=parse_bloom_level(bl_str),
                p_bp=bm_next, band=bm_band, attempts=bm_attempts,
                correct=bm_correct_n, last_event_seq=ev.seq,
            )

        for cid, m in current.items():
            await self._session_upsert(s, learner_id, cid, m.p_bp, m.band,
                                       m.attempts, m.correct, m.last_event_seq)
        for (cid, bl_str), bm in current_bloom.items():
            await self._session_upsert_bloom(s, learner_id, cid, bl_str, bm.p_bp, bm.band,
                                             bm.attempts, bm.correct, bm.last_event_seq)

    async def _incremental_projection(self, learner_id: str,
                                      accepted: list[LearnerEvent], ruleset) -> None:
        seen = await self.events.learner_attempt_ids(learner_id)
        current = {m.concept_id: m for m in await self.mastery.get_mastery(learner_id)}
        current_bloom = {(bm.concept_id, bm.bloom_level.value): bm
                         for bm in await self.mastery.get_bloom_mastery(learner_id)}
        for ev in sorted(accepted, key=lambda e: e.seq):
            effect = mastery_effect_for_event(ev, ruleset, seen,
                                              question_lookup=self._question_lookup())
            if effect.effect != "mastery_updated":
                continue
            seen.add(str(ev.payload.get("attempt_id") or ev.event_id))
            cid = effect.concept_id
            m = current.get(cid)
            p_prior = m.p_bp if m else int(ruleset.bkt.get("p_init_bp", 2000))
            p_next = bkt_update_bp(p_prior, bool(effect.correct), ruleset, cid)
            attempts = (m.attempts if m else 0) + 1
            correct_n = (m.correct if m else 0) + (1 if effect.correct else 0)
            band = mastery_band_bp(p_next, ruleset)
            await self.mastery.upsert_mastery(learner_id, cid, p_next, band,
                                              attempts, correct_n, ev.seq)
            current[cid] = MasteryRecord(concept_id=cid, p_bp=p_next, band=band,
                                         attempts=attempts, correct=correct_n,
                                         last_event_seq=ev.seq)

            bl_str = self._event_bloom_level(ev)
            bm = current_bloom.get((cid, bl_str))
            bm_prior = bm.p_bp if bm else int(ruleset.bkt.get("p_init_bp", 2000))
            bm_next = bkt_update_bp(bm_prior, bool(effect.correct), ruleset, cid)
            bm_attempts = (bm.attempts if bm else 0) + 1
            bm_correct_n = (bm.correct if bm else 0) + (1 if effect.correct else 0)
            bm_band = mastery_band_bp(bm_next, ruleset)
            await self.mastery.upsert_bloom_mastery(learner_id, cid, bl_str, bm_next, bm_band,
                                                   bm_attempts, bm_correct_n, ev.seq)
            current_bloom[(cid, bl_str)] = BloomMasteryRecord(
                concept_id=cid, bloom_level=parse_bloom_level(bl_str),
                p_bp=bm_next, band=bm_band, attempts=bm_attempts,
                correct=bm_correct_n, last_event_seq=ev.seq,
            )

    async def _rebuild_projection(self, learner_id: str, ruleset) -> None:
        all_events = await self.events.list_events(learner_id, since_seq=0, limit=200000)
        seen: set[str] = set()
        current: dict[str, MasteryRecord] = {}
        current_bloom: dict[tuple[str, str], BloomMasteryRecord] = {}
        for ev in sorted(all_events, key=lambda e: e.seq):
            effect = mastery_effect_for_event(ev, ruleset, seen,
                                              question_lookup=self._question_lookup())
            if effect.effect != "mastery_updated":
                continue
            seen.add(str(ev.payload.get("attempt_id") or ev.event_id))
            cid = effect.concept_id
            m = current.get(cid)
            p_prior = m.p_bp if m else int(ruleset.bkt.get("p_init_bp", 2000))
            p_next = bkt_update_bp(p_prior, bool(effect.correct), ruleset, cid)
            attempts = (m.attempts if m else 0) + 1
            correct_n = (m.correct if m else 0) + (1 if effect.correct else 0)
            band = mastery_band_bp(p_next, ruleset)
            current[cid] = MasteryRecord(concept_id=cid, p_bp=p_next, band=band,
                                         attempts=attempts, correct=correct_n,
                                         last_event_seq=ev.seq)

            bl_str = self._event_bloom_level(ev)
            bm = current_bloom.get((cid, bl_str))
            bm_prior = bm.p_bp if bm else int(ruleset.bkt.get("p_init_bp", 2000))
            bm_next = bkt_update_bp(bm_prior, bool(effect.correct), ruleset, cid)
            bm_attempts = (bm.attempts if bm else 0) + 1
            bm_correct_n = (bm.correct if bm else 0) + (1 if effect.correct else 0)
            bm_band = mastery_band_bp(bm_next, ruleset)
            current_bloom[(cid, bl_str)] = BloomMasteryRecord(
                concept_id=cid, bloom_level=parse_bloom_level(bl_str),
                p_bp=bm_next, band=bm_band, attempts=bm_attempts,
                correct=bm_correct_n, last_event_seq=ev.seq,
            )

        if current:
            await self.mastery.replace_mastery_snapshot(learner_id,
                                                        list(current.values()))
        if current_bloom:
            await self.mastery.replace_bloom_mastery_snapshot(learner_id,
                                                              list(current_bloom.values()))

    # ------------------------------------------------------------------ #
    # Post-commit decision (deterministic, server-side)
    # ------------------------------------------------------------------ #
    async def _post_sync_decision(self, req: SyncRequest, ruleset) -> Optional[Decision]:
        from ..services.decision_service import DecisionService
        if self.pack is None:
            return None
        ds = DecisionService(self.pack, self.mastery, self.decisions)
        last_event = req.events[-1] if req.events else None
        trigger_correct = None
        trigger_type = "SESSION_STARTED"
        trigger_concept = None
        if last_event is not None:
            trigger_type = _etype(last_event)
            trigger_concept = last_event.concept_id
            if trigger_type == "ANSWER_SUBMITTED":
                # Never trust a client-supplied correctness flag for the server
                # decision. Re-grade the submitted response against the active
                # packed question revision, just as the mastery projection does.
                lookup = self._question_lookup()
                payload = last_event.payload or {}
                question_id = payload.get("question_id") or last_event.question_id
                revision = payload.get("revision", 1)
                question = lookup(question_id, revision) if lookup and question_id else None
                resp = payload.get("response") if payload.get("response") is not None else payload.get("selected_option")
                trigger_correct = (bool(question.correct(resp))
                                   if question is not None else None)
                if trigger_concept is None and question is not None:
                    trigger_concept = question.concept_id
        return await ds.next_decision(
            learner_id=req.learner_id, env_network=NetworkState.RECONNECTED,
            produced_by="server_engine", source="server",
            trigger_event_type=trigger_type,
            trigger_concept_id=trigger_concept,
            trigger_correct=trigger_correct,
            recent_events=req.events[-20:],
        )

    # ------------------------------------------------------------------ #
    # Response assembly (one outcome per submitted event)
    # ------------------------------------------------------------------ #
    async def _assemble(self, req: SyncRequest, results: dict[str, PerEventResult],
                        ruleset, decision_status: str,
                        decision) -> SyncResponse:
        # Ensure every submitted event has exactly one result.
        for ev in req.events:
            if ev.event_id not in results:
                results[ev.event_id] = PerEventResult(
                    event_id=ev.event_id, seq=ev.seq, outcome=Outcome.RETRYABLE,
                    reason=SyncReason.SERVER_BUSY,
                    detail="no outcome recorded; resend safely (idempotent)")
        per_event = sorted(results.values(), key=lambda r: r.seq)
        mastery = await self.mastery.get_mastery(req.learner_id)
        bloom_mastery = await self.mastery.get_bloom_mastery(req.learner_id)
        acked = [r.seq for r in per_event
                 if r.outcome in (Outcome.ACCEPTED, Outcome.DUPLICATE)]
        rejected = [r.seq for r in per_event if r.outcome == Outcome.REJECTED]
        server_cursor = max(acked + rejected + [req.from_seq, 0])
        return SyncResponse(
            results=per_event,
            accepted=per_event,
            mastery=mastery,
            canonical_mastery=mastery,
            bloom_mastery=bloom_mastery,
            canonical_bloom_mastery=bloom_mastery,
            decision=decision,
            next_decision=decision,
            decision_status=decision_status,
            server_cursor=server_cursor,
            server_learner_seq=server_cursor,
            ruleset_version=ruleset.ruleset_version,
        )


__all__ = ["SyncService"]
