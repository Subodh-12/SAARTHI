"""Arq worker + durable PostgreSQL job runner (Design v2 Section 5 & 14).

Rules (Section 5):
- Arq runs the jobs; the PostgreSQL/SQLite job table is the source of truth,
  so a lost queue loses nothing.
- Job record: job_id, type, payload, dedupe_key, status (queued, running,
  succeeded, retry, dead), attempts, max_attempts, next_run_at, lease_expires_at, last_error.
- Recovery: A reconciler runs every minute and re-enqueues any job that is
  queued or running with an expired lease.
- Retryable errors: Timeouts, rate limits, 5xx: exponential backoff from 5 s,
  factor 2, plus or minus 20% jitter, cap 10 min, at most 6 attempts.
- Non-retryable errors: Failed publication gate, invalid input: go straight to dead.
- Idempotency: Jobs carry a dedupe key such as pack:{pack_id}:{version};
  running a job twice produces the same artifact.
- Visibility: Dead jobs are listed by an admin endpoint and counted in the developer panel.
"""
from __future__ import annotations

import asyncio
import os
import random
import time
from typing import Any, Optional

from ..core.logging import get_logger
from ..core.settings import get_settings
from ..domain.schemas import JobRecord, JobStatus
from ..adapters.persistence import Persistence, get_persistence
from ..adapters.persistence.repositories import SqlJobRepository

log = get_logger("saarthi.worker")


class NonRetryableError(Exception):
    """Errors that should immediately fail the job to DEAD state."""
    pass


class RetryableJobError(Exception):
    """Errors that should trigger exponential backoff retry."""
    pass


async def execute_job_payload(job_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Execute the concrete logic for a given job type."""
    log.info("executing_job type=%s payload=%s", job_type, payload)
    
    if job_type == "build_pack":
        pack_id = payload.get("pack_id")
        version = payload.get("version", 1)
        if not pack_id:
            raise NonRetryableError("missing_pack_id")
        # In a real environment, executes pack building logic
        return {"status": "ok", "pack_id": pack_id, "version": version}

    elif job_type == "rebuild_index":
        chapter_id = payload.get("chapter_id")
        return {"status": "ok", "indexed_chapter": chapter_id}

    elif job_type == "reconcile_cron":
        return {"status": "ok", "reconciled": True}

    elif job_type == "test_job":
        # Used by test suites
        if payload.get("fail_permanent"):
            raise NonRetryableError("forced_permanent_failure")
        if payload.get("fail_retryable"):
            raise RetryableJobError("forced_retryable_failure")
        return {"result": payload.get("result", "success")}

    else:
        raise NonRetryableError(f"unknown_job_type: {job_type}")


class JobWorker:
    """Worker engine that acquires and runs jobs from the durable database."""

    def __init__(self, persistence: Persistence, worker_id: Optional[str] = None) -> None:
        self.p = persistence
        self.repo = SqlJobRepository(persistence)
        self.worker_id = worker_id or f"worker_{os.getpid()}_{random.randint(1000, 9999)}"
        self._running = False

    async def run_once(self) -> Optional[JobRecord]:
        """Attempt to acquire and execute a single job."""
        job = await self.repo.acquire_next_job(self.worker_id, lease_duration_s=60)
        if not job:
            return None

        log.info("worker_acquired_job worker=%s job_id=%s type=%s attempt=%d",
                 self.worker_id, job.job_id, job.type, job.attempts)
        try:
            await execute_job_payload(job.type, job.payload)
            await self.repo.complete_job(job.job_id)
            log.info("worker_job_succeeded job_id=%s", job.job_id)
        except NonRetryableError as e:
            log.warning("worker_job_permanent_fail job_id=%s err=%s", job.job_id, str(e))
            await self.repo.fail_job(job.job_id, str(e), retryable=False)
        except Exception as e:
            is_retryable = not isinstance(e, NonRetryableError)
            log.warning("worker_job_retryable_fail job_id=%s err=%s retryable=%s",
                        job.job_id, str(e), is_retryable)
            await self.repo.fail_job(job.job_id, str(e), retryable=is_retryable)

        return job

    async def reconcile(self) -> int:
        """Run reconciliation for expired leases."""
        count = await self.repo.reconcile_expired_leases()
        if count > 0:
            log.info("reconciled_expired_jobs count=%d", count)
        return count

    async def run_loop(self, poll_interval_s: float = 1.0, max_iterations: Optional[int] = None) -> None:
        """Background worker loop polling database for queued jobs."""
        self._running = True
        iterations = 0
        last_reconcile = 0.0

        while self._running:
            if max_iterations is not None and iterations >= max_iterations:
                break
            iterations += 1

            now = time.time()
            if now - last_reconcile >= 60.0:
                await self.reconcile()
                last_reconcile = now

            job = await self.run_once()
            if not job:
                await asyncio.sleep(poll_interval_s)

    def stop(self) -> None:
        self._running = False


# Arq integration functions
async def build_pack_job(ctx: dict, pack_id: str, version: int = 1) -> dict:
    return await execute_job_payload("build_pack", {"pack_id": pack_id, "version": version})


async def rebuild_index_job(ctx: dict, chapter_id: str) -> dict:
    return await execute_job_payload("rebuild_index", {"chapter_id": chapter_id})


async def reconcile_jobs_task(ctx: dict) -> int:
    p = ctx.get("persistence") or await get_persistence()
    worker = JobWorker(p)
    return await worker.reconcile()


async def run_worker() -> None:
    p = await get_persistence()
    worker = JobWorker(p)
    log.info("starting_saarthi_durable_worker worker_id=%s", worker.worker_id)
    await worker.run_loop()


class WorkerSettings:
    """Arq WorkerSettings configuration."""
    functions = [build_pack_job, rebuild_index_job, reconcile_jobs_task]
    redis_settings = None  # Configured from settings in production
    max_jobs = 10
    poll_delay = 1.0
