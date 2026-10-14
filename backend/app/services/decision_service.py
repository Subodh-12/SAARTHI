"""Decision service — wraps the pure decide() + persistence."""
from __future__ import annotations

import time
import uuid
from typing import Optional

from ..content.pack_loader import PackContentIndex
from ..domain.bkt import bkt_band
from ..domain.decide import DecisionInput, decide
from ..domain.ruleset import get_ruleset
from ..domain.schemas import (
    Action, BackgroundAction, Decision, DecisionTrace, DeliveryMode,
    LearnerEvent, MasteryRecord, NetworkState, TraceStep, new_decision_id,
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
                          trigger_event_type: str = "next_action_shown",
                          trigger_concept_id: Optional[str] = None,
                          trigger_evidence: str = "none",
                          recent_events: Optional[list[LearnerEvent]] = None) -> DecisionInput:
        mastery_records = await self.mastery.get_mastery(learner_id)
        mastery_dict = {
            m.concept_id: (m.p_known, m.band, m.attempts, m.correct)
            for m in mastery_records
        }
        recent = recent_events or []
        recent_dicts = [
            {
                "concept_id": e.concept_id,
                "payload": {"last_action": e.payload.get("last_action", "")}
            }
            for e in recent[-10:]
        ]
        return DecisionInput(
            trigger_event_type=trigger_event_type,
            trigger_concept_id=trigger_concept_id,
            trigger_evidence=trigger_evidence,
            mastery=mastery_dict,
            recent_events=recent_dicts,
            prereqs=self.pack.prereqs,
            env_network=env_network,
            installed_pack_versions={"pack_class9_science_or_v1": "1.0.0"},
            ruleset_version=get_ruleset().ruleset_version,
            concept_order=self.pack.concept_order,
            chapter_id_for_concept=self.pack.chapter_for_concept,
        )

    async def next_decision(
        self, learner_id: str, env_network: NetworkState,
        produced_by: str = "server_engine",
        trigger_event_type: str = "next_action_shown",
        trigger_concept_id: Optional[str] = None,
        trigger_evidence: str = "none",
        recent_events: Optional[list[LearnerEvent]] = None,
    ) -> Decision:
        ruleset = get_ruleset()
        inp = await self.build_input(
            learner_id, env_network, trigger_event_type, trigger_concept_id,
            trigger_evidence, recent_events,
        )
        out = decide(inp, ruleset, REASON_MESSAGES)
        decision = Decision(
            decision_id=new_decision_id(),
            learner_id=learner_id,
            ruleset_version=ruleset.ruleset_version,
            target_concept_id=out.target_concept_id,
            action=out.action,
            delivery_mode=out.delivery_mode,
            background_actions=out.background_actions,
            reason_code=out.reason_code,
            reason_or=out.reason_or,
            chapter_id=out.chapter_id,
            network=env_network,
            produced_by=produced_by,  # type: ignore[arg-type]
            created_at=int(time.time() * 1000),
            suggested_chunk_id=out.suggested_chunk_id,
            suggested_question_id=out.suggested_question_id,
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
                    "action": out.action.value,
                    "trigger_evidence": inp.trigger_evidence,
                    "target_mastery_p": m[0] if m else None,
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

    async def get_trace(self, decision_id: str):
        return await self.decisions.get_trace(decision_id)
