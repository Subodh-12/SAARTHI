"""Karana Study Rooms routes — /api/v1/rooms."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from ...core.errors import ErrorCode, SaarthiError
from ...domain.rooms import (
    GameStart, GameSubmission, MessagePost, RelayStart, RelaySubmission,
    RoomCreate, RoomJoinRequest, VerificationSubmit,
)
from ..middleware import require_device_auth
from .learners import get_display_label

router = APIRouter(prefix="/rooms", tags=["study-rooms"])


def _svc(request: Request):
    svc = getattr(request.app.state, "rooms_service", None)
    if svc is None:
        raise SaarthiError(ErrorCode.INTERNAL_ERROR, status=500,
                           detail="rooms service not initialised")
    return svc


@router.post("/create", status_code=201)
async def create_room_route(body: RoomCreate, request: Request,
                            auth=Depends(require_device_auth)):
    device_id, learner_id = auth
    label = await get_display_label(request, learner_id)
    return await _svc(request).create_room(learner_id, label, body)


@router.post("/join")
async def join_room(body: RoomJoinRequest, request: Request,
                    auth=Depends(require_device_auth)):
    device_id, learner_id = auth
    label = await get_display_label(request, learner_id)
    return await _svc(request).join_room(learner_id, label, body.room_code)


@router.get("")
async def list_rooms(request: Request, auth=Depends(require_device_auth)):
    _, learner_id = auth
    rooms = await _svc(request).list_rooms(learner_id)
    return {"rooms": rooms}


@router.get("/{room_id}")
async def room_detail(room_id: str, request: Request,
                      auth=Depends(require_device_auth)):
    _, learner_id = auth
    return await _svc(request).get_room_detail(room_id, learner_id)


@router.post("/{room_id}/leave")
async def leave_room(room_id: str, request: Request,
                     auth=Depends(require_device_auth)):
    _, learner_id = auth
    await _svc(request).leave_room(room_id, learner_id)
    return {"left": True}


@router.post("/{room_id}/heartbeat")
async def heartbeat(room_id: str, request: Request,
                    auth=Depends(require_device_auth)):
    _, learner_id = auth
    await _svc(request).heartbeat(room_id, learner_id)
    return {"ok": True}


@router.post("/{room_id}/messages")
async def post_message(room_id: str, body: MessagePost, request: Request,
                       auth=Depends(require_device_auth)):
    _, learner_id = auth
    label = await get_display_label(request, learner_id)
    msg = await _svc(request).post_message(room_id, learner_id, label, body)
    return msg


# ---- Doubt Relay ---- #
@router.post("/{room_id}/relay/start")
async def start_relay(room_id: str, body: RelayStart, request: Request,
                      auth=Depends(require_device_auth)):
    _, learner_id = auth
    return await _svc(request).start_relay(room_id, learner_id, body)


@router.get("/{room_id}/relay/{activity_id}")
async def get_relay(room_id: str, activity_id: str, request: Request,
                    auth=Depends(require_device_auth)):
    _, learner_id = auth
    return await _svc(request).get_relay(room_id, activity_id, learner_id)


@router.post("/{room_id}/relay/{activity_id}/submit")
async def submit_relay(room_id: str, activity_id: str, body: RelaySubmission,
                       request: Request, auth=Depends(require_device_auth)):
    _, learner_id = auth
    return await _svc(request).submit_relay(room_id, activity_id, learner_id, body)


@router.post("/{room_id}/relay/{activity_id}/reveal")
async def reveal_relay(room_id: str, activity_id: str, request: Request,
                       auth=Depends(require_device_auth)):
    _, learner_id = auth
    return await _svc(request).reveal_relay(room_id, activity_id, learner_id)


@router.post("/{room_id}/relay/{activity_id}/advance")
async def advance_relay(room_id: str, activity_id: str, request: Request,
                        auth=Depends(require_device_auth)):
    import json
    body = await request.json()
    stage = (body or {}).get("stage", "")
    _, learner_id = auth
    return await _svc(request).advance_relay(room_id, activity_id, learner_id, stage)


@router.post("/{room_id}/relay/{activity_id}/verify")
async def verify_relay(room_id: str, activity_id: str, body: VerificationSubmit,
                       request: Request, auth=Depends(require_device_auth)):
    _, learner_id = auth
    return await _svc(request).complete_verification(
        room_id, activity_id, learner_id, body)


# ---- Find the Mistake ---- #
@router.post("/{room_id}/game/start")
async def start_game(room_id: str, request: Request,
                     auth=Depends(require_device_auth)):
    _, learner_id = auth
    return await _svc(request).start_game(room_id, learner_id)


@router.get("/{room_id}/game/{activity_id}")
async def get_game(room_id: str, activity_id: str, request: Request,
                   auth=Depends(require_device_auth)):
    _, learner_id = auth
    return await _svc(request).get_game(room_id, activity_id, learner_id)


@router.post("/{room_id}/game/{activity_id}/submit")
async def submit_game(room_id: str, activity_id: str, body: GameSubmission,
                      request: Request, auth=Depends(require_device_auth)):
    _, learner_id = auth
    return await _svc(request).submit_game(room_id, activity_id, learner_id, body)


@router.post("/{room_id}/game/{activity_id}/reveal")
async def reveal_game(room_id: str, activity_id: str, request: Request,
                      auth=Depends(require_device_auth)):
    _, learner_id = auth
    return await _svc(request).reveal_game(room_id, activity_id, learner_id)


@router.get("/{room_id}/activities")
async def list_activities(room_id: str, request: Request,
                          auth=Depends(require_device_auth)):
    _, learner_id = auth
    return {"activities": await _svc(request).list_activities(room_id, learner_id)}


# ---- Admin/dev: expiry sweep trigger ---- #
@router.post("/admin/expire-sweep")
async def expire_sweep(request: Request, auth=Depends(require_device_auth)):
    """Runs the same expiry sweep as the background task; usable in dev/tests
    to demonstrate deletion without waiting for the timer."""
    deleted = await _svc(request).expire_due_rooms()
    return {"deleted_room_ids": deleted}


__all__ = ["router"]
