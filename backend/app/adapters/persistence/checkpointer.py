"""Durable PostgreSQL and SQLite checkpointer for LangGraph (Design v2 Section 5).

Persists graph state, execution checkpoints, and channel writes across process
restarts into `langgraph_checkpoints` and `langgraph_writes` tables.
Ensures resumption from interrupted executions without duplicate side effects.
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import Any, AsyncIterator, Iterator, Optional, Sequence

from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    SerializerProtocol,
    get_checkpoint_id,
)
from langchain_core.runnables import RunnableConfig
from sqlalchemy import text

from ...core.logging import get_logger
from . import Persistence

log = get_logger("saarthi.checkpointer")


class SqlLangGraphCheckpointer(BaseCheckpointSaver):
    """PostgreSQL and SQLite durable checkpointer for LangGraph workflows."""

    def __init__(self, persistence: Persistence, serde: Optional[SerializerProtocol] = None) -> None:
        super().__init__(serde=serde)
        self.p = persistence

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return None
        checkpoint_ns = config.get("configurable", {}).get("checkpoint_ns", "")
        checkpoint_id = get_checkpoint_id(config)

        async with self.p.session() as s:
            if checkpoint_id:
                res = await s.execute(
                    text(
                        "SELECT checkpoint_id, parent_checkpoint_id, type, metadata_json, blob, config_json "
                        "FROM langgraph_checkpoints "
                        "WHERE thread_id = :tid AND checkpoint_ns = :ns AND checkpoint_id = :cid"
                    ),
                    {"tid": thread_id, "ns": checkpoint_ns, "cid": checkpoint_id},
                )
            else:
                res = await s.execute(
                    text(
                        "SELECT checkpoint_id, parent_checkpoint_id, type, metadata_json, blob, config_json "
                        "FROM langgraph_checkpoints "
                        "WHERE thread_id = :tid AND checkpoint_ns = :ns "
                        "ORDER BY checkpoint_id DESC LIMIT 1"
                    ),
                    {"tid": thread_id, "ns": checkpoint_ns},
                )
            row = res.fetchone()
            if not row:
                return None

            cid, parent_cid, ctype, meta_json, blob_data, cfg_json = row

            try:
                if blob_data:
                    checkpoint = self.serde.loads_typed((ctype, blob_data))
                else:
                    checkpoint = json.loads(cfg_json or "{}")
            except Exception as e:
                log.warning("failed_deserializing_checkpoint cid=%s err=%s", cid, e)
                return None

            try:
                metadata = json.loads(meta_json or "{}")
            except Exception:
                metadata = {}

            # Load pending writes if any
            w_res = await s.execute(
                text(
                    "SELECT task_id, channel, type, blob FROM langgraph_writes "
                    "WHERE thread_id = :tid AND checkpoint_ns = :ns AND checkpoint_id = :cid "
                    "ORDER BY created_at ASC"
                ),
                {"tid": thread_id, "ns": checkpoint_ns, "cid": cid},
            )
            writes_rows = w_res.fetchall()
            pending_writes = []
            for tid_val, ch, w_type, w_blob in writes_rows:
                try:
                    val = self.serde.loads_typed((w_type, w_blob)) if w_blob else None
                    pending_writes.append((tid_val, ch, val))
                except Exception:
                    pass

            parent_config = (
                {
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_ns": checkpoint_ns,
                        "checkpoint_id": parent_cid,
                    }
                }
                if parent_cid
                else None
            )

            final_config = {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": cid,
                }
            }

            return CheckpointTuple(
                config=final_config,
                checkpoint=checkpoint,
                metadata=metadata,
                parent_config=parent_config,
                pending_writes=pending_writes,
            )

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        thread_id = config.get("configurable", {}).get("thread_id", "")
        checkpoint_ns = config.get("configurable", {}).get("checkpoint_ns", "")
        checkpoint_id = checkpoint["id"]
        parent_checkpoint_id = config.get("configurable", {}).get("checkpoint_id")

        ctype, blob = self.serde.dumps_typed(checkpoint)
        meta_json = json.dumps(metadata or {}, default=str, ensure_ascii=False)
        cfg_json = json.dumps(config or {}, default=str, ensure_ascii=False)
        now = int(time.time() * 1000)

        async with self.p.session() as s:
            await s.execute(
                text(
                    "INSERT INTO langgraph_checkpoints "
                    "(thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, type, config_json, metadata_json, blob, created_at) "
                    "VALUES (:tid, :ns, :cid, :pid, :type, :cfg, :meta, :blob, :now) "
                    "ON CONFLICT (thread_id, checkpoint_ns, checkpoint_id) DO UPDATE SET "
                    "parent_checkpoint_id = :pid, type = :type, config_json = :cfg, metadata_json = :meta, blob = :blob, created_at = :now"
                ),
                {
                    "tid": thread_id,
                    "ns": checkpoint_ns,
                    "cid": checkpoint_id,
                    "pid": parent_checkpoint_id,
                    "type": ctype,
                    "cfg": cfg_json,
                    "meta": meta_json,
                    "blob": blob,
                    "now": now,
                },
            )
            await s.commit()

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            }
        }

    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        thread_id = config.get("configurable", {}).get("thread_id", "")
        checkpoint_ns = config.get("configurable", {}).get("checkpoint_ns", "")
        checkpoint_id = config.get("configurable", {}).get("checkpoint_id", "")
        now = int(time.time() * 1000)

        async with self.p.session() as s:
            for channel, value in writes:
                wtype, blob = self.serde.dumps_typed(value)
                await s.execute(
                    text(
                        "INSERT INTO langgraph_writes "
                        "(thread_id, checkpoint_ns, checkpoint_id, task_id, channel, type, blob, created_at) "
                        "VALUES (:tid, :ns, :cid, :task_id, :ch, :type, :blob, :now) "
                        "ON CONFLICT (thread_id, checkpoint_ns, checkpoint_id, task_id, channel) DO UPDATE SET "
                        "type = :type, blob = :blob, created_at = :now"
                    ),
                    {
                        "tid": thread_id,
                        "ns": checkpoint_ns,
                        "cid": checkpoint_id,
                        "task_id": str(task_id),
                        "ch": str(channel),
                        "type": wtype,
                        "blob": blob,
                        "now": now,
                    },
                )
            await s.commit()

    async def alist(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> AsyncIterator[CheckpointTuple]:
        if not config:
            return
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return
        checkpoint_ns = config.get("configurable", {}).get("checkpoint_ns", "")
        lim = limit or 50

        async with self.p.session() as s:
            res = await s.execute(
                text(
                    "SELECT checkpoint_id FROM langgraph_checkpoints "
                    "WHERE thread_id = :tid AND checkpoint_ns = :ns "
                    "ORDER BY checkpoint_id DESC LIMIT :lim"
                ),
                {"tid": thread_id, "ns": checkpoint_ns, "lim": lim},
            )
            cids = [r[0] for r in res.fetchall()]

        for cid in cids:
            tup = await self.aget_tuple(
                {"configurable": {"thread_id": thread_id, "checkpoint_ns": checkpoint_ns, "checkpoint_id": cid}}
            )
            if tup:
                yield tup

    async def adelete_thread(self, thread_id: str) -> None:
        async with self.p.session() as s:
            await s.execute(text("DELETE FROM langgraph_checkpoints WHERE thread_id = :tid"), {"tid": thread_id})
            await s.execute(text("DELETE FROM langgraph_writes WHERE thread_id = :tid"), {"tid": thread_id})
            await s.commit()

    # Synchronous fallbacks using an event loop
    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, self.aget_tuple(config)).result()
        return asyncio.run(self.aget_tuple(config))

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, self.aput(config, checkpoint, metadata, new_versions)).result()
        return asyncio.run(self.aput(config, checkpoint, metadata, new_versions))

    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                pool.submit(asyncio.run, self.aput_writes(config, writes, task_id, task_path)).result()
                return
        asyncio.run(self.aput_writes(config, writes, task_id, task_path))

    def list(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        async def _collect():
            items = []
            async for item in self.alist(config, filter=filter, before=before, limit=limit):
                items.append(item)
            return items
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                items = pool.submit(asyncio.run, _collect()).result()
        else:
            items = asyncio.run(_collect())
        for it in items:
            yield it

    def delete_thread(self, thread_id: str) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                pool.submit(asyncio.run, self.adelete_thread(thread_id)).result()
                return
        asyncio.run(self.adelete_thread(thread_id))
