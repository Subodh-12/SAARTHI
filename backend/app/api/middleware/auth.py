"""Auth middleware — device-bound token verification + ownership enforcement.

Design v2 Section 6/8: authentication protects server requests but never
gates local learning. Every learner-specific endpoint enforces the active
learner/device/profile ownership; cross-profile and cross-device access is
denied (403 FORBIDDEN), missing/invalid tokens are 401.
"""
from __future__ import annotations

from fastapi import Request, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ...core.errors import ErrorCode, SaarthiError
from ...services import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_auth_service(request: Request) -> AuthService:
    """Build an AuthService from app-state repositories (set at startup)."""
    auth = getattr(request.app.state, "auth_service", None)
    if auth is None:
        raise SaarthiError(ErrorCode.INTERNAL_ERROR, status=500,
                           detail="auth service not initialised")
    return auth


async def require_device_auth(
    request: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth: AuthService = Depends(get_auth_service),
) -> tuple[str, str]:
    """Return (device_id, learner_id). Raise 401 on missing/invalid token,
    403 DEVICE_REVOKED when the device has been revoked."""
    if creds is None or creds.scheme.lower() != "bearer" or not creds.credentials:
        raise SaarthiError(ErrorCode.UNAUTHENTICATED, status=401,
                           detail="missing Bearer token")
    try:
        device_id, learner_id = await auth.verify_device_token(creds.credentials)
    except PermissionError as e:
        raise SaarthiError(ErrorCode.TOKEN_INVALID, status=401, detail=str(e))
    if learner_id is None:
        # Auth succeeded but no learner profile is active on this device:
        # authorization for learner-scoped data is denied (403), never a
        # token error — the client may create/activate a profile next.
        raise SaarthiError(ErrorCode.FORBIDDEN, status=403,
                           detail="no active learner on this device")
    request.state.device_id = device_id
    request.state.learner_id = learner_id
    return device_id, learner_id


async def require_learner_access(
    learner_id: str,
    ctx: tuple[str, str] = Depends(require_device_auth),
    auth: AuthService = Depends(get_auth_service),
) -> tuple[str, str]:
    """Ownership enforcement for learner-specific endpoints.

    The path/body learner_id must match the token's active learner AND be
    actively linked to the token's device (v2 Section 6)."""
    device_id, token_learner_id = ctx
    if learner_id != token_learner_id:
        raise SaarthiError(ErrorCode.FORBIDDEN, status=403,
                           detail="cross-profile access denied")
    await auth.verify_learner_access(device_id, learner_id)
    return device_id, learner_id


__all__ = ["require_device_auth", "require_learner_access", "get_auth_service",
           "bearer_scheme"]
