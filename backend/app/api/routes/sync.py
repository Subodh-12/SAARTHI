"""Sync route — POST /sync (per-event outcomes, v2 Section 8).

A failed batch transaction returns HTTP 503 with every event RETRYABLE so
the phone keeps the events in its outbox and backs off with jitter.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response

from ...domain.schemas import SyncRequest, SyncResponse
from ..middleware import require_device_auth

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("", response_model=SyncResponse)
async def sync(
    body: SyncRequest,
    request: Request,
    response: Response,
    ctx: tuple[str, str] = Depends(require_device_auth),
):
    device_id, learner_id = ctx
    # Ownership: the request's device/learner are always the auth-resolved
    # ones — the client can never sync another learner's events.
    body.device_id = device_id  # type: ignore[assignment]
    body.learner_id = learner_id  # type: ignore[assignment]
    sync_svc = request.app.state.sync_service
    resp = await sync_svc.sync(body)
    # A batch whose every event is RETRYABLE maps to HTTP 503 (v2: "If it
    # fails, every event in it is returned RETRYABLE with HTTP 503").
    if resp.results and all(
            r.outcome.value == "RETRYABLE" for r in resp.results):
        response.status_code = 503
    return resp


__all__ = ["router"]
