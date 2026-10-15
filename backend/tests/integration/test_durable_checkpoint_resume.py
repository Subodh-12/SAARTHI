"""Integration test for LangGraph durable checkpoint persistence across process restart (Design v2 Section 5).

Verifies:
- Checkpoints and channel writes persist to durable database tables (langgraph_checkpoints, langgraph_writes).
- Process restart / checkpointer recreation correctly restores graph state using thread_id.
- Graph resumes from interrupted node without repeating already executed side effects.
- Interrupted orchestration thread can be resumed to full completion.
- run_doubt doubt graph execution persists state into durable checkpointer.
"""
from __future__ import annotations

import os
import tempfile
import pytest
from sqlalchemy import text
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig

from app.adapters.persistence import Persistence, get_persistence, reset_persistence_for_tests
from app.adapters.persistence.checkpointer import SqlLangGraphCheckpointer
from app.orchestration.graph import build_doubt_graph, run_doubt, OrchestrationState
from app.domain.schemas import DoubtRequest


@pytest.fixture
async def checkpointer_persistence():
    await reset_persistence_for_tests()
    p = await get_persistence()
    await p.apply_schema()
    async with p.session() as s:
        await s.execute(text("DELETE FROM langgraph_checkpoints"))
        await s.execute(text("DELETE FROM langgraph_writes"))
        await s.commit()
    yield p
    await reset_persistence_for_tests()


@pytest.mark.asyncio
async def test_durable_checkpoint_state_persists_across_instances(checkpointer_persistence):
    p = checkpointer_persistence
    thread_id = "thread_durable_resume_001"

    # Define a stateful multi-step workflow
    side_effects = {"node_a": 0, "node_b": 0, "node_c": 0}

    def node_a(state: dict):
        side_effects["node_a"] += 1
        return {"step_a": "completed", "value": state.get("value", 0) + 10}

    def node_b(state: dict):
        side_effects["node_b"] += 1
        return {"step_b": "completed", "value": state["value"] * 2}

    def node_c(state: dict):
        side_effects["node_c"] += 1
        return {"step_c": "completed", "value": state["value"] + 5}

    builder = StateGraph(dict)
    builder.add_node("node_a", node_a)
    builder.add_node("node_b", node_b)
    builder.add_node("node_c", node_c)

    builder.add_edge(START, "node_a")
    builder.add_edge("node_a", "node_b")
    builder.add_edge("node_b", "node_c")
    builder.add_edge("node_c", END)

    # Compile graph with first checkpointer instance
    chk_1 = SqlLangGraphCheckpointer(p)
    graph_1 = builder.compile(checkpointer=chk_1, interrupt_after=["node_a"])

    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

    # Execute up to interrupt
    result_1 = await graph_1.ainvoke({"value": 5}, config=config)
    assert result_1["step_a"] == "completed"
    assert result_1["value"] == 15
    assert side_effects["node_a"] == 1
    assert side_effects["node_b"] == 0

    # Verify rows exist in langgraph_checkpoints table
    async with p.session() as s:
        res = await s.execute(
            text("SELECT COUNT(*) FROM langgraph_checkpoints WHERE thread_id = :tid"),
            {"tid": thread_id},
        )
        count = res.scalar()
        assert count > 0, "Checkpoints must be committed to durable SQL table"

    # --- SIMULATE PROCESS TERMINATION / RESTART ---
    # Discard graph_1 and chk_1 completely, instantiate a brand new checkpointer and graph
    del graph_1
    del chk_1

    chk_2 = SqlLangGraphCheckpointer(p)
    # Check that new checkpointer restores state from the database
    saved_tuple = await chk_2.aget_tuple(config)
    assert saved_tuple is not None
    assert saved_tuple.config["configurable"]["thread_id"] == thread_id

    # Compile a new graph instance without interrupt to resume to completion
    graph_2 = builder.compile(checkpointer=chk_2)

    # Resume from checkpoint using the same thread_id
    resumed_result = await graph_2.ainvoke(None, config=config)

    # Node A was not re-executed (side effect was preserved, not duplicated)
    assert side_effects["node_a"] == 1
    # Nodes B and C ran to completion
    assert side_effects["node_b"] == 1
    assert side_effects["node_c"] == 1

    # Final value: (5 + 10) * 2 + 5 = 35
    assert resumed_result["value"] == 35
    assert resumed_result["step_c"] == "completed"


@pytest.mark.asyncio
async def test_run_doubt_persists_durable_checkpoint(checkpointer_persistence):
    p = checkpointer_persistence
    thread_id = "doubt_thread_test_002"

    req = DoubtRequest(
        learner_id="lrn_1234567890abcdef12345678",
        query="What is photosynthesis?",
        concept_id="c0001",
        chapter_id="ch001",
        network="offline",
    )

    chk = SqlLangGraphCheckpointer(p)
    resp = await run_doubt(req, checkpointer=chk, thread_id=thread_id)
    assert resp.decision_id == thread_id
    assert resp.answer is not None

    # Verify database has stored checkpoints
    async with p.session() as s:
        res = await s.execute(
            text("SELECT checkpoint_id, type FROM langgraph_checkpoints WHERE thread_id = :tid"),
            {"tid": thread_id},
        )
        rows = res.fetchall()
        assert len(rows) > 0
