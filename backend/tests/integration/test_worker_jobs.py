"""Tests for Section 7.2 & Section 5: Arq worker, durable job repository,
reconciliation of expired leases, retry exponential backoff, and admin visibility.
"""
from __future__ import annotations

import os
import tempfile
import time
import pytest
from httpx import ASGITransport, AsyncClient

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{tempfile.mktemp(suffix='.db')}"
os.environ["PERSISTENCE_BACKEND"] = "sqlite"

from sqlalchemy import text
from fastapi.testclient import TestClient

from app.domain.schemas import JobStatus
from app.adapters.persistence import get_persistence
from app.adapters.persistence.repositories import SqlJobRepository
from app.worker.worker import JobWorker, NonRetryableError, RetryableJobError
from app.main import create_app


@pytest.fixture
async def job_setup():
    p = await get_persistence()
    repo = SqlJobRepository(p)
    async with p.session() as s:
        await s.execute(text("DELETE FROM jobs"))
        await s.commit()
    yield p, repo


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.mark.asyncio
async def test_job_enqueue_and_deduplication(job_setup):
    p, repo = job_setup
    
    # Enqueue a job with a dedupe key
    job1 = await repo.enqueue(
        job_type="build_pack",
        payload={"pack_id": "sci9-ch1", "version": 3},
        dedupe_key="pack:sci9-ch1:3",
        max_attempts=3,
    )
    assert job1.job_id
    assert job1.status == JobStatus.QUEUED
    assert job1.attempts == 0
    assert job1.dedupe_key == "pack:sci9-ch1:3"

    # Enqueue same job with same dedupe_key: returns existing job (idempotent)
    job2 = await repo.enqueue(
        job_type="build_pack",
        payload={"pack_id": "sci9-ch1", "version": 3},
        dedupe_key="pack:sci9-ch1:3",
    )
    assert job2.job_id == job1.job_id


@pytest.mark.asyncio
async def test_job_worker_execution_success(job_setup):
    p, repo = job_setup
    worker = JobWorker(p, worker_id="test_worker_1")

    job = await repo.enqueue(
        job_type="test_job",
        payload={"result": "all_good"},
        dedupe_key=f"test:{time.time()}",
    )

    # Worker acquires and executes
    executed = await worker.run_once()
    assert executed is not None
    assert executed.job_id == job.job_id

    # Check status is SUCCEEDED
    jobs = await repo.list_jobs(statuses=[JobStatus.SUCCEEDED.value])
    succeeded_ids = [j.job_id for j in jobs]
    assert job.job_id in succeeded_ids


@pytest.mark.asyncio
async def test_job_worker_non_retryable_error_goes_to_dead(job_setup):
    p, repo = job_setup
    worker = JobWorker(p, worker_id="test_worker_2")

    job = await repo.enqueue(
        job_type="test_job",
        payload={"fail_permanent": True},
        dedupe_key=f"perm:{time.time()}",
    )

    executed = await worker.run_once()
    assert executed is not None

    # Status must be DEAD immediately without reaching max attempts
    jobs = await repo.list_jobs(statuses=[JobStatus.DEAD.value])
    dead_ids = [j.job_id for j in jobs]
    assert job.job_id in dead_ids


@pytest.mark.asyncio
async def test_job_worker_retryable_backoff(job_setup):
    p, repo = job_setup
    worker = JobWorker(p, worker_id="test_worker_3")

    job = await repo.enqueue(
        job_type="test_job",
        payload={"fail_retryable": True},
        dedupe_key=f"retry:{time.time()}",
        max_attempts=3,
    )

    # Attempt 1 -> fails with retryable error
    await worker.run_once()
    jobs = await repo.list_jobs(statuses=[JobStatus.RETRY.value])
    retry_job = next(j for j in jobs if j.job_id == job.job_id)
    assert retry_job.attempts == 1
    assert retry_job.status == JobStatus.RETRY
    assert retry_job.next_run_at > retry_job.created_at


@pytest.mark.asyncio
async def test_reconciler_recovers_expired_leases(job_setup):
    p, repo = job_setup
    worker = JobWorker(p, worker_id="test_worker_4")

    # Enqueue and acquire job with expired lease
    job = await repo.enqueue(
        job_type="test_job",
        payload={"result": "ok"},
        dedupe_key=f"lease:{time.time()}",
    )
    # Acquire with 0-second lease so it expires immediately
    acquired = await repo.acquire_next_job("crashed_worker", lease_duration_s=0)
    assert acquired is not None

    time.sleep(0.01)
    reconciled = await worker.reconcile()
    assert reconciled >= 1

    # Job is re-enqueued to retry status
    jobs = await repo.list_jobs(statuses=[JobStatus.RETRY.value])
    assert any(j.job_id == job.job_id for j in jobs)


def test_admin_jobs_endpoint(client):
    # Enqueue a test job via admin endpoint
    res = client.post(
        "/api/v1/admin/jobs/enqueue",
        json={"type": "build_pack", "payload": {"pack_id": "sci9-ch2", "version": 1}},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "build_pack"
    assert data["status"] == "queued"

    # Check GET /admin/jobs
    get_res = client.get("/api/v1/admin/jobs")
    assert get_res.status_code == 200
    status_data = get_res.json()
    assert "counts" in status_data
    assert "dead_jobs" in status_data
    assert "retrying_jobs" in status_data
    assert "all_jobs" in status_data

    # Test POST /admin/jobs/reconcile
    rec_res = client.post("/api/v1/admin/jobs/reconcile")
    assert rec_res.status_code == 200
    assert "reconciled_count" in rec_res.json()

