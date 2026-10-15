"""Doubt service — entry point for the doubt branch.

Wraps the orchestration graph, then persists the GENERATION RECORD
(providers never write to the database — the service layer does, v2
Section 5). The deterministic learning-action engine is never touched by
translation or generation.
"""
from __future__ import annotations

from typing import Optional

from ..content.pack_loader import PackContentIndex
from ..domain.schemas import DecisionTrace, DoubtRequest, DoubtResponse
from ..orchestration.graph import OrchestrationState, run_doubt
from ..repositories import DecisionRepository, GenerationRecordRepository


class DoubtService:
    def __init__(self, pack: PackContentIndex,
                 decisions: DecisionRepository,
                 generation_records: GenerationRecordRepository | None = None) -> None:
        self.pack = pack
        self.decisions = decisions
        self.generation_records = generation_records

    async def ask(self, req: DoubtRequest) -> DoubtResponse:
        resp = await run_doubt(req)
        # Persist the generation record (audit trail for generated text).
        if self.generation_records is not None and resp.generation_record is not None:
            try:
                await self.generation_records.save(resp.generation_record)
            except Exception as e:  # noqa: BLE001 — audit failure never breaks the answer
                from ..core.logging import get_logger
                get_logger("saarthi.doubt").warning(
                    "generation_record_persist_failed err=%s", e)
        return resp
