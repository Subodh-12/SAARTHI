"""Device registration + auth renewal routes (Design v2 Section 8).

- POST /devices        register a device with its ECDSA P-256 public key
- POST /auth/refresh   rotate refresh tokens (normal renewal)
- POST /auth/challenge signed-nonce challenge after prolonged offline
- POST /auth/renew     exchange the nonce signature for fresh tokens
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from ...core.errors import ErrorCode, SaarthiError
from ...domain.schemas import (
    AuthChallenge, AuthChallengeRequest, AuthRenewRequest, DeviceRegistration,
    DeviceTokenResponse, RefreshRequest,
)
from ..middleware import get_auth_service
from ...services import AuthService

router = APIRouter(tags=["auth"])


@router.post("/devices", response_model=DeviceTokenResponse, status_code=201)
async def register_device(
    body: DeviceRegistration,
    request: Request,
    auth: AuthService = Depends(get_auth_service),
):
    """Register a physical device with its non-extractable WebCrypto
    ECDSA P-256 public key (SPKI, base64url). Returns the initial token pair."""
    return await auth.register_device(
        body.public_key_spki_b64, body.hardware_label, device_id=body.device_id
    )


@router.post("/auth/refresh", response_model=DeviceTokenResponse)
async def refresh_tokens(body: RefreshRequest,
                         auth: AuthService = Depends(get_auth_service)):
    """Normal renewal: consume the rotating refresh token, issue a new pair."""
    return await auth.refresh(body.device_id, body.refresh_token)


@router.post("/auth/challenge", response_model=AuthChallenge)
async def auth_challenge(body: AuthChallengeRequest,
                         auth: AuthService = Depends(get_auth_service)):
    """Long offline period: get a nonce to sign with the device key."""
    nonce, expires_at = await auth.new_challenge(body.device_id)
    return AuthChallenge(nonce=nonce, expires_at=expires_at)


@router.post("/auth/renew", response_model=DeviceTokenResponse)
async def auth_renew(body: AuthRenewRequest,
                     auth: AuthService = Depends(get_auth_service)):
    """Exchange the nonce signature (device key) for fresh tokens."""
    return await auth.renew_with_signature(body.device_id, body.nonce,
                                           body.signature_b64)


__all__ = ["router"]
