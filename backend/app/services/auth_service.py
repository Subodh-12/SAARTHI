"""Auth service v2 — device-bound tokens, no passwords, no PII.

Design v2 Section 8 contract:

- A physical phone generates a NON-EXTRACTABLE WebCrypto ECDSA P-256 key
  pair and registers the public key at POST /devices. The server stores
  the public key; it never sees private key material.
- Tokens: short-lived ACCESS token (24h) + ROTATING refresh token (30d),
  lifetimes from the shared ruleset (`auth.access_ttl_h`, `refresh_ttl_d`).
- Normal renewal: POST /auth/refresh with the refresh token (single use,
  rotated on every renewal).
- Long offline period: POST /auth/challenge returns a nonce; the phone
  signs it with the device key and POST /auth/renew exchanges the
  signature for new tokens. No password or PIN is involved, and the
  outbox is untouched.
- Authentication protects network calls only; it never gates local
  learning. When auth is pending or expired the client pauses sync in an
  AUTH_PENDING state and keeps learning.
- DEVICE_REVOKED: all tokens die; the client quarantines pending events
  and continues learning locally.
- The local profile PIN is never sent to the server and is never treated
  as authentication.
"""
from __future__ import annotations

import base64
import hashlib
import secrets
import time

from ..core.errors import ErrorCode, SaarthiError
from ..core.settings import get_settings
from ..domain.ruleset import get_ruleset
from ..domain.schemas import (
    AuthResponse, DeviceTokenResponse, LearnerProfile, LearnerProfileCreate,
    new_device_id, new_learner_id,
)
from ..repositories import (
    DeviceRepository, LearnerRepository,
)


class AuthService:
    def __init__(self, learners: LearnerRepository, devices: DeviceRepository) -> None:
        self.learners = learners
        self.devices = devices
        self.s = get_settings()

    # ------------------------------------------------------------------ #
    # Lifetimes (ruleset is the source of truth)
    # ------------------------------------------------------------------ #
    def _auth_ttl(self) -> tuple[int, int]:
        auth = get_ruleset().auth or {}
        access_h = int(auth.get("access_ttl_h", 24))
        refresh_d = int(auth.get("refresh_ttl_d", 30))
        return access_h * 3600, refresh_d * 86400

    # ------------------------------------------------------------------ #
    # Device registration (ECDSA P-256 public key)
    # ------------------------------------------------------------------ #
    async def register_device(self, public_key_spki_b64: str,
                              hardware_label: str = "shared-android-low-end",
                              device_id: str | None = None) -> DeviceTokenResponse:
        if not public_key_spki_b64 or len(public_key_spki_b64) < 16:
            raise SaarthiError(ErrorCode.VALIDATION_ERROR, status=422,
                               detail="public_key_spki_b64 is required")
        did = device_id or new_device_id()
        await self.devices.register_device(did, hardware_label,
                                           public_key_spki_b64)
        return await self._issue_tokens(did)

    # ------------------------------------------------------------------ #
    # Learners
    # ------------------------------------------------------------------ #
    async def create_learner(self, device_id: str,
                             create: LearnerProfileCreate) -> AuthResponse:
        if await self.devices.is_revoked(device_id):
            raise SaarthiError(ErrorCode.DEVICE_REVOKED, status=403,
                               detail="device is revoked")
        learner_id = new_learner_id()
        now_ms = int(time.time() * 1000)
        profile = LearnerProfile(
            learner_id=learner_id,
            display_label=create.display_label,
            locale=create.locale, grade=create.grade, subject=create.subject,
            pin_verifier=create.pin_verifier, created_at=now_ms,
        )
        await self.learners.create_learner(profile, device_id)
        await self.learners.activate_learner_on_device(learner_id, device_id)
        tokens = await self._issue_tokens(device_id)
        return self._with_learner(tokens, learner_id)

    async def activate(self, learner_id: str, device_id: str) -> AuthResponse:
        if await self.devices.is_revoked(device_id):
            raise SaarthiError(ErrorCode.DEVICE_REVOKED, status=403,
                               detail="device is revoked")
        profile = await self.learners.get_learner(learner_id)
        if not profile:
            raise SaarthiError(ErrorCode.LEARNER_NOT_FOUND, status=404,
                               detail=f"unknown learner: {learner_id}")
        await self.learners.activate_learner_on_device(learner_id, device_id)
        tokens = await self._issue_tokens(device_id)
        return self._with_learner(tokens, learner_id)

    # ------------------------------------------------------------------ #
    # Token renewal paths
    # ------------------------------------------------------------------ #
    async def refresh(self, device_id: str, refresh_token: str) -> DeviceTokenResponse:
        """Rotate: the presented refresh token is consumed (single use) and
        a fresh pair is issued. Reuse of a consumed token fails closed."""
        token_hash = self._hash_token(refresh_token)
        owner = await self.devices.consume_refresh_token(token_hash)
        if owner is None or owner != device_id:
            raise SaarthiError(ErrorCode.TOKEN_INVALID, status=401,
                               detail="invalid or already-used refresh token")
        if await self.devices.is_revoked(device_id):
            raise SaarthiError(ErrorCode.DEVICE_REVOKED, status=403,
                               detail="device is revoked")
        return await self._issue_tokens(device_id)

    async def new_challenge(self, device_id: str) -> tuple[str, int]:
        """Signed-nonce challenge for renewal after prolonged offline periods."""
        if await self.devices.is_revoked(device_id):
            raise SaarthiError(ErrorCode.DEVICE_REVOKED, status=403,
                               detail="device is revoked")
        if not await self.devices.get_public_key(device_id):
            raise SaarthiError(ErrorCode.DEVICE_UNKNOWN, status=404,
                               detail="device not registered")
        nonce = secrets.token_urlsafe(32)
        ttl = int(get_ruleset().auth.get("challenge_ttl_s", 300))
        now_ms = int(time.time() * 1000)
        await self.devices.store_challenge(device_id, nonce, now_ms,
                                           now_ms + ttl * 1000)
        return nonce, now_ms + ttl * 1000

    async def renew_with_signature(self, device_id: str, nonce: str,
                                   signature_b64: str) -> DeviceTokenResponse:
        """Verify the ECDSA P-256 signature over the nonce with the stored
        device public key, then issue fresh tokens."""
        public_key_spki = await self.devices.get_public_key(device_id)
        if not public_key_spki:
            raise SaarthiError(ErrorCode.DEVICE_UNKNOWN, status=404,
                               detail="device not registered")
        if await self.devices.is_revoked(device_id):
            raise SaarthiError(ErrorCode.DEVICE_REVOKED, status=403,
                               detail="device is revoked")
        if not await self.devices.consume_challenge(device_id, nonce):
            raise SaarthiError(ErrorCode.TOKEN_INVALID, status=401,
                               detail="unknown, expired or already-used nonce")
        if not _verify_p256_signature(public_key_spki, nonce, signature_b64):
            raise SaarthiError(ErrorCode.TOKEN_INVALID, status=401,
                               detail="signature verification failed")
        return await self._issue_tokens(device_id)

    async def renew_token(self, device_id: str) -> AuthResponse:
        """Access-token renewal (the route enforces a valid access token)."""
        active = await self.learners.get_active_learner_on_device(device_id)
        if not active:
            raise SaarthiError(ErrorCode.LEARNER_NOT_FOUND, status=404,
                               detail=f"no active learner on device {device_id}")
        tokens = await self._issue_tokens(device_id)
        return self._with_learner(tokens, active.learner_id)

    # ------------------------------------------------------------------ #
    # Verification (middleware)
    # ------------------------------------------------------------------ #
    async def verify_device_token(self, token: str) -> tuple[str, str | None]:
        """Return (device_id, learner_id) for a valid access token.

        Authentication is device-scoped: a valid token on a device with no
        active learner returns (device_id, None). Learner-specific endpoints
        turn that into 403 — auth never gates local learning and the client
        can renew/rebind without re-registering the device."""
        token_hash = self._hash_token(token)
        info = await self.devices.verify_access_token(token_hash)
        if not info:
            raise PermissionError("invalid or expired access token")
        device_id, _exp = info
        if await self.devices.is_revoked(device_id):
            raise SaarthiError(ErrorCode.DEVICE_REVOKED, status=403,
                               detail="device is revoked")
        active = await self.learners.get_active_learner_on_device(device_id)
        return device_id, (active.learner_id if active else None)

    async def verify_learner_access(self, device_id: str, learner_id: str) -> None:
        """Ownership check: the learner must be actively linked to THIS device
        (v2: every learner-specific endpoint enforces learner/device/profile
        ownership; cross-profile and cross-device access is denied)."""
        if not await self.learners.is_learner_linked(learner_id, device_id):
            raise SaarthiError(ErrorCode.FORBIDDEN, status=403,
                               detail="learner is not linked to this device")

    # ------------------------------------------------------------------ #
    # Token issuing
    # ------------------------------------------------------------------ #
    async def _issue_tokens(self, device_id: str) -> DeviceTokenResponse:
        access_ttl_s, refresh_ttl_s = self._auth_ttl()
        now_ms = int(time.time() * 1000)
        access = secrets.token_urlsafe(self.s.device_token_bytes)
        await self.devices.issue_access_token(device_id, self._hash_token(access),
                                              now_ms, now_ms + access_ttl_s * 1000)
        refresh = secrets.token_urlsafe(self.s.device_token_bytes)
        await self.devices.issue_refresh_token(device_id, self._hash_token(refresh),
                                               now_ms, now_ms + refresh_ttl_s * 1000)
        # Rotation: consumption of the presented token (single use) invalidates
        # it; revoked devices already had every token class revoked.
        await self.devices.touch_last_seen(device_id)
        return DeviceTokenResponse(
            device_id=device_id,
            access_token=access,
            access_expires_at=now_ms + access_ttl_s * 1000,
            refresh_token=refresh,
            refresh_expires_at=now_ms + refresh_ttl_s * 1000,
        )

    def _with_learner(self, tokens: DeviceTokenResponse,
                      learner_id: str) -> AuthResponse:
        return AuthResponse(
            learner_id=learner_id,
            device_id=tokens.device_id,
            device_token=tokens.access_token,
            token_expires_at=tokens.access_expires_at,
            refresh_token=tokens.refresh_token,
            refresh_expires_at=tokens.refresh_expires_at,
        )

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# ECDSA P-256 verification (server side of the WebCrypto device key)
# --------------------------------------------------------------------------- #
def _verify_p256_signature(public_key_spki_b64: str, nonce: str,
                           signature_b64: str) -> bool:
    """Verify an ECDSA P-256 signature over the UTF-8 nonce bytes
    (SHA-256, matching the browser WebCrypto `sign` parameters:
    `{name: 'ECDSA', hash: 'SHA-256'}`). WebCrypto produces raw r||s;
    `cryptography` expects DER — both are accepted."""
    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives.asymmetric.utils import (
            encode_dss_signature as _enc_dss,
        )
        from cryptography.hazmat.primitives.serialization import (
            load_der_public_key, load_pem_public_key,
        )
        from cryptography.exceptions import InvalidSignature
    except Exception:  # pragma: no cover — cryptography is a hard dependency
        raise SaarthiError(ErrorCode.INTERNAL_ERROR, status=500,
                           detail="server missing 'cryptography' package; "
                                  "cannot verify device signatures")
    try:
        spki = base64.urlsafe_b64decode(_pad_b64(public_key_spki_b64))
        try:
            public_key = load_der_public_key(spki)
        except Exception:
            public_key = load_pem_public_key(spki)
        if not isinstance(public_key, ec.EllipticCurvePublicKey) or \
                public_key.curve.name != "secp256r1":
            return False
        sig = base64.urlsafe_b64decode(_pad_b64(signature_b64))
        data = nonce.encode("utf-8")
        algo = ec.ECDSA(hashes.SHA256())
        try:
            public_key.verify(sig, data, algo)
            return True
        except InvalidSignature:
            pass
        # WebCrypto ECDSA produces raw r||s (64 bytes); convert to DER.
        if len(sig) == 64:
            r = int.from_bytes(sig[:32], "big")
            s = int.from_bytes(sig[32:], "big")
            try:
                public_key.verify(_enc_dss(r, s), data, algo)
                return True
            except InvalidSignature:
                return False
        return False
    except SaarthiError:
        raise
    except Exception:
        return False


def encode_dss_signature(r: int, s: int) -> bytes:
    """Minimal DER encode of an ECDSA signature (rfc3279) without the
    asymmetric.utils dependency surface."""
    def _len(n: int) -> bytes:
        if n < 0x80:
            return bytes([n])
        out = n.to_bytes((n.bit_length() + 7) // 8, "big")
        return bytes([0x80 | len(out)]) + out

    def _int(x: int) -> bytes:
        b = x.to_bytes((x.bit_length() + 7) // 8 or 1, "big")
        if b[0] & 0x80:
            b = b"\x00" + b
        return b"\x02" + _len(len(b)) + b

    body = _int(r) + _int(s)
    return b"\x30" + _len(len(body)) + body


def _pad_b64(value: str) -> str:
    return value + "=" * (-len(value) % 4)


__all__ = ["AuthService", "_verify_p256_signature", "encode_dss_signature"]
