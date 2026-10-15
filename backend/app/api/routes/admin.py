"""Admin routes for operator visibility into durable background jobs (Design v2 Section 5 & 8).

Endpoints:
- GET /admin/jobs: Dead and retrying jobs, summary counts, and recent queue entries.
- POST /admin/jobs/reconcile: Force immediate reconciliation of expired leases.
- POST /admin/jobs/enqueue: Enqueue a background job with deduplication key.
"""
from __future__ import annotations

from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from ...domain.schemas import JobsAdminResponse, JobRecord, JobStatus
from ...core.logging import get_logger

log = get_logger("saarthi.admin")

router = APIRouter(prefix="/admin", tags=["admin"])


class EnqueueJobRequest(BaseModel):
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    dedupe_key: Optional[str] = None
    max_attempts: int = 6
    delay_s: int = 0


class ReconcileResponse(BaseModel):
    reconciled_count: int


@router.get("/jobs", response_model=JobsAdminResponse)
async def get_jobs_status(request: Request, limit: int = 50):
    """List dead and retrying jobs and status counts (operators and developer panel)."""
    job_repo = getattr(request.app.state, "job_repository", None)
    if not job_repo:
        raise HTTPException(status_code=500, detail="job repository not initialized")

    counts = await job_repo.count_by_status()
    dead_jobs = await job_repo.list_jobs(statuses=[JobStatus.DEAD.value], limit=limit)
    retrying_jobs = await job_repo.list_jobs(statuses=[JobStatus.RETRY.value], limit=limit)
    all_jobs = await job_repo.list_jobs(limit=limit)

    return JobsAdminResponse(
        counts=counts,
        dead_jobs=dead_jobs,
        retrying_jobs=retrying_jobs,
        all_jobs=all_jobs,
    )


@router.post("/jobs/reconcile", response_model=ReconcileResponse)
async def reconcile_jobs(request: Request):
    """Reconcile expired worker leases immediately."""
    job_repo = getattr(request.app.state, "job_repository", None)
    if not job_repo:
        raise HTTPException(status_code=500, detail="job repository not initialized")

    count = await job_repo.reconcile_expired_leases()
    return ReconcileResponse(reconciled_count=count)


@router.post("/jobs/enqueue", response_model=JobRecord)
async def enqueue_job(req: EnqueueJobRequest, request: Request):
    """Enqueue a job to the durable job repository."""
    job_repo = getattr(request.app.state, "job_repository", None)
    if not job_repo:
        raise HTTPException(status_code=500, detail="job repository not initialized")

    job = await job_repo.enqueue(
        job_type=req.type,
        payload=req.payload,
        dedupe_key=req.dedupe_key,
        max_attempts=req.max_attempts,
        delay_s=req.delay_s,
    )
    return job


__all__ = ["router"]
