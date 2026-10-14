"""Learner routes — profile create / get / list / activate.

Every learner-specific endpoint enforces device/profile ownership (v2
Section 6): the token's device must hold the active link to the learner.
The optional local PIN verifier is accepted only as an opaque string and
is NEVER used for server authentication.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from ...core.errors import ErrorCode, SaarthiError
from ...core.settings import get_settings
from ...domain.schemas import new_device_id
from ...domain.schemas import (
    AuthResponse, DeviceTokenResponse, LearnerProfile, LearnerProfileCreate,
)
from ..middleware import get_auth_service, require_device_auth
from ...services import AuthService

router = APIRouter(prefix="/learners", tags=["learners"])


@router.post("", response_model=AuthResponse, status_code=201)
async def create_learner(
    body: LearnerProfileCreate,
    request: Request,
    auth: AuthService = Depends(get_auth_service),
):
    """Create a learner profile linked to the calling device.

    The device is identified by the Bearer access token when present
    (registered devices); otherwise a legacy X-Device-Id header is honoured
    for low-friction onboarding. A brand-new call without either registers
    an ephemeral device that the client upgrades to a keyed device later."""
    device_id = ""
    creds = request.headers.get("authorization", "")
    if creds.startswith("Bearer ") and creds[7:].strip():
        # Token-authenticated creation: reuse the token's device
        try:
            device_id, _ = await auth.verify_device_token(creds[7:].strip())
        except PermissionError:
            raise SaarthiError(ErrorCode.TOKEN_INVALID, status=401,
                               detail="invalid access token")
    if not device_id:
        device_id = request.headers.get("X-Device-Id") or ""
        if device_id and await auth.devices.is_revoked(device_id):
            raise SaarthiError(ErrorCode.DEVICE_REVOKED, status=403,
                               detail="device is revoked")
    if not device_id:
        # Auto-register an anonymous device for low-friction onboarding.
        device_id = new_device_id()
        await auth.devices.register_device(device_id, "shared-android-low-end")
    # Learner data minimality (v2 N8): only display_label/locale/grade/subject
    # are accepted — no contacts, phone numbers or location.
    return await auth.create_learner(device_id, body)


@router.get("/me", response_model=LearnerProfile)
async def get_current_learner(
    ctx: tuple[str, str] = Depends(require_device_auth),
    auth: AuthService = Depends(get_auth_service),
):
    _device_id, learner_id = ctx
    p = await auth.learners.get_learner(learner_id)
    if not p:
        raise SaarthiError(ErrorCode.LEARNER_NOT_FOUND, status=404,
                           detail=f"learner {learner_id} not found")
    return p


@router.get("", response_model=list[LearnerProfile])
async def list_learners(
    ctx: tuple[str, str] = Depends(require_device_auth),
    auth: AuthService = Depends(get_auth_service),
):
    """Learner profiles on THIS device only (never another device's)."""
    device_id, _learner_id = ctx
    return await auth.learners.list_learners_on_device(device_id)


@router.post("/{learner_id}/activate", response_model=AuthResponse)
async def activate_learner(
    learner_id: str,
    request: Request,
    ctx: tuple[str, str] = Depends(require_device_auth),
    auth: AuthService = Depends(get_auth_service),
):
    """Activate a profile on the CALLING device; the learner must already be
    linked to it (cross-device activation is denied)."""
    device_id, _token_learner = ctx
    if not await auth.learners.is_learner_linked(learner_id, device_id):
        raise SaarthiError(ErrorCode.FORBIDDEN, status=403,
                           detail="learner is not linked to this device")
    return await auth.activate(learner_id, device_id)


@router.post("/auth/renew", response_model=AuthResponse)
async def renew_token(
    ctx: tuple[str, str] = Depends(require_device_auth),
    auth: AuthService = Depends(get_auth_service),
):
    device_id, _learner_id = ctx
    return await auth.renew_token(device_id)


__all__ = ["router"]
