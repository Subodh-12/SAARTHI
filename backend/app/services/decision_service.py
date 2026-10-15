"""Decision service — wraps the pure v2 decide() + persistence.

Builds the normalised, deterministic DecisionInput from committed state
(profile-scoped mastery in integer basis points, recent events, installed
packs) and persists the decision with needs_help and source. A failing
trajectory check inside the engine yields the fallback decision
(STATE_INVALID_FALLBACK) which is logged at high severity.
"""
from __future__ import annotations

import time
from typing import Optional

from ..content.pack_loader import PackContentIndex
from ..domain.decide import (
    DecisionInput, DecisionOutput, MasteryEntry, RecentEvent, decide,
    engine_error,
)
from ..domain.ruleset import get_ruleset
from ..domain.schemas import (
    Action, BackgroundAction, BloomLevel, Decision, DecisionTrace, DeliveryMode,
    EventType, LearnerEvent, MasteryRecord, NetworkState, TraceStep, new_decision_id,
)
from ..i18n.reasons_or import REASON_MESSAGES
from ..repositories import DecisionRepository, MasteryRepository


class DecisionService:
    def __init__(self, pack: PackContentIndex, mastery: MasteryRepository,
                 decisions: DecisionRepository) -> None:
        self.pack = pack
        self.mastery = mastery
        self.decisions = decisions

    async def build_input(self, learner_id: str, env_network: NetworkState,
                          trigger_event_type: str = "SESSION_STARTED",
                          trigger_concept_id: Optional[str] = None,
                          trigger_correct: Optional[bool] = None,
                          recent_events: Optional[list[LearnerEvent]] = None,
                          doubt_concept_hint: Optional[str] = None,
                          storage_free_mb: int = 1_000_000,
                          battery_saver: bool = False,
                          outbox_nonempty: bool = False,
                          trigger_evidence: Optional[str] = None) -> DecisionInput:
        ruleset = get_ruleset()
        mastery_records = await self.mastery.get_mastery(learner_id)
        mastery_dict = {
            m.concept_id: MasteryEntry(p_bp=m.p_bp, attempts=m.attempts,
                                       correct=m.correct,
                                       last_event_seq=m.last_event_seq)
            for m in mastery_records
        }
        get_bloom_mastery = getattr(self.mastery, "get_bloom_mastery", None)
        bloom_records = await get_bloom_mastery(learner_id) if callable(get_bloom_mastery) else []
        bloom_dict: dict[str, dict[str, MasteryEntry]] = {}
        for bm in bloom_records:
            cid = bm.concept_id
            bl = bm.bloom_level.value if hasattr(bm.bloom_level, "value") else str(bm.bloom_level)
            bloom_dict.setdefault(cid, {})[bl] = MasteryEntry(
                p_bp=bm.p_bp, attempts=bm.attempts, correct=bm.correct,
                last_event_seq=bm.last_event_seq,
            )
        available_bloom: dict[str, list[str]] = {}
        for cid in self.pack.concept_order:
            method = getattr(self.pack, "available_bloom_levels_for_concept", None)
            if callable(method):
                available_bloom[cid] = method(cid)
            else:
                q = next((q for q in self.pack.questions.values() if q.concept_id == cid), None)
                available_bloom[cid] = [getattr(q, "bloom_level", "remember")] if q else []
        recent: list[RecentEvent] = []
        for e in (recent_events or [])[-20:]:
            etype = e.event_type.value if hasattr(e.event_type, "value") else str(e.event_type)
            p_after = e.payload.get("p_bp_after")
            recent.append(RecentEvent(
                seq=e.seq,
                event_type=etype,
                concept_id=e.concept_id,
                correct=(bool(e.payload.get("correct"))
                         if etype == "ANSWER_SUBMITTED" and "correct" in e.payload else None),
                p_bp_after=(int(p_after) if isinstance(p_after, (int, float)) else None),
                last_action=e.payload.get("last_action"),
            ))
        # Sort concept order by (chapter, concept id) — canonical chapter order
        concept_order = list(self.pack.concept_order)
        chapter_map = dict(self.pack.chapter_for_concept)
        normalized_trigger_evidence = trigger_evidence or (
            "correct" if trigger_correct is True else
            "incorrect" if trigger_correct is False else None
        )
        installed_pack_versions = getattr(self.pack, "installed_pack_versions", None)
        required_pack_for_concept = getattr(self.pack, "required_pack_for_concept", None)
        return DecisionInput(
            trigger_event_type=trigger_event_type,
            trigger_concept_id=trigger_concept_id,
            trigger_correct=trigger_correct,
            trigger_evidence=normalized_trigger_evidence,
            mastery=mastery_dict,
            recent_events=recent,
            prereqs=self.pack.prereqs,
            concept_order=concept_order,
            chapter_id_for_concept=chapter_map,
            doubt_concept_hint=doubt_concept_hint,
            env_network=env_network.value if hasattr(env_network, "value") else str(env_network),
            installed_pack_versions=installed_pack_versions() if callable(installed_pack_versions) else {},
            required_pack_for_concept=required_pack_for_concept() if callable(required_pack_for_concept) else {},
            storage_free_mb=storage_free_mb,
            battery_saver=battery_saver,
            outbox_nonempty=outbox_nonempty,
            ruleset_version=ruleset.ruleset_version,
            bloom_mastery=bloom_dict,
            available_bloom_levels_for_concept=available_bloom,
        )

    async def next_decision(
        self, learner_id: str, env_network: NetworkState,
        produced_by: str = "server_engine",
        source: str = "server",
        trigger_event_type: str = "SESSION_STARTED",
        trigger_concept_id: Optional[str] = None,
        trigger_correct: Optional[bool] = None,
        recent_events: Optional[list[LearnerEvent]] = None,
        doubt_concept_hint: Optional[str] = None,
        trigger_evidence: Optional[str] = None,
    ) -> Decision:
        ruleset = get_ruleset()
        inp = await self.build_input(
            learner_id, env_network, trigger_event_type, trigger_concept_id,
            trigger_correct, recent_events, doubt_concept_hint,
            trigger_evidence=trigger_evidence,
        )
        # Typed engine error (unknown ruleset / invalid state) is surfaced in
        # the trace; decide() still returns the safe fallback decision.
        engine_err = engine_error(inp, ruleset)
        out: DecisionOutput = decide(inp, ruleset, REASON_MESSAGES)
        if engine_err:
            from ..core.logging import get_logger
            get_logger("saarthi.decision").error(
                "decision_fallback learner=%s error=%s reason=%s",
                learner_id, engine_err, out.reason_code)
        action_value = out.action.value if hasattr(out.action, "value") else str(out.action)
        delivery_value = (out.delivery_mode.value if hasattr(out.delivery_mode, "value")
                          else str(out.delivery_mode))
        background_values = [
            BackgroundAction(a.value if hasattr(a, "value") else str(a))
            for a in (out.background_actions or [])
        ]
        decision = Decision(
            decision_id=new_decision_id(),
            learner_id=learner_id,
            ruleset_version=ruleset.ruleset_version,
            target_concept_id=out.target_concept_id,
            target_bloom_level=BloomLevel(out.target_bloom_level) if out.target_bloom_level else None,
            action=Action(action_value),
            delivery_mode=DeliveryMode(delivery_value),
            background_actions=background_values,
            reason_code=out.reason_code,
            reason_or=REASON_MESSAGES.get(out.reason_code, out.reason_code),
            needs_help=out.needs_help,
            chapter_id=self.pack.chapter_for_concept.get(out.target_concept_id, ""),
            network=env_network,
            source="server" if source == "server" else "local",  # type: ignore[arg-type]
            produced_by="server_engine" if produced_by == "server_engine" else "local_engine",
            created_at=int(time.time() * 1000),
        )
        await self.decisions.save_decision(decision)
        # Structured decision trace (Phase 5): explains target selection,
        # action choice, and — when the trigger was an incorrect response —
        # the verification-gate state. Summaries carry only IDs/counts;
        # raw learner answers are never logged (redacted=True default).
        m = inp.mastery.get(out.target_concept_id)
        steps = [
            TraceStep(
                step_id="select_target", node="decision_engine", status="ok", duration_ms=0,
                ruleset_version=ruleset.ruleset_version,
                output_summary={"target_concept_id": out.target_concept_id,
                                "reason_code": out.reason_code},
            ),
            TraceStep(
                step_id="select_action", node="decision_engine", status="ok", duration_ms=0,
                output_summary={
                    "action": action_value,
                    "trigger_evidence": inp.trigger_evidence,
                    "target_mastery_p": m.p_bp if m else None,
                },
            ),
        ]
        if inp.trigger_evidence in ("incorrect", "partial"):
            steps.append(TraceStep(
                step_id="verification_gate", node="decision_engine", status="ok", duration_ms=0,
                output_summary={
                    "note": "incorrect response: candidate-cause diagnosis and "
                            "verification evidence are tracked on the assessment "
                            "result; mastery is updated exactly once per accepted "
                            "event",
                },
            ))
        await self.decisions.save_trace(
            decision.decision_id,
            DecisionTrace(decision_id=decision.decision_id, trace=steps))
        return decision

    async def get_decision(self, decision_id: str) -> Optional[Decision]:
        return await self.decisions.get_decision(decision_id)

    async def get_decision_for_learner(self, decision_id: str,
                                       learner_id: str) -> Optional[Decision]:
        return await self.decisions.get_decision_for_learner(decision_id, learner_id)

    async def get_trace(self, decision_id: str):
        return await self.decisions.get_trace(decision_id)
