"""Security middleware — rate limiting, request-size limit, security headers.

Design v2 Section 6/14: per-device rate limiting, request size limits and
strict production CORS/security headers. The rate limiter is an in-process
token bucket (Redis is the production home; losing it never loses durable
state — it only resets limits).
"""
from __future__ import annotations

import time

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ...core.settings import get_settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Minimal, API-appropriate security headers on every response."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Cache-Control", "no-store")
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject bodies larger than settings.max_request_bytes with 413."""

    async def dispatch(self, request: Request, call_next):
        s = get_settings()
        length = request.headers.get("content-length")
        if length is not None and length.isdigit() and int(length) > s.max_request_bytes:
            return JSONResponse(
                status_code=413,
                content={"title": "Payload Too Large", "status": 413,
                         "error_code": "request_too_large",
                         "detail": f"body exceeds {s.max_request_bytes} bytes"},
            )
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token bucket keyed by device (Bearer hash) or client IP.

    Only mutating endpoints are limited; health/readiness stay open for
    probes. Exceeding the limit returns 429 RATE_LIMITED with Retry-After.
    """

    def __init__(self, app):
        super().__init__(app)
        self._buckets: dict[str, tuple[float, float]] = {}  # key -> (tokens, last)
        self._last_sweep = time.monotonic()

    async def dispatch(self, request: Request, call_next):
        s = get_settings()
        path = request.url.path
        if request.method in ("GET", "HEAD") or path.endswith(("/health", "/readiness")):
            return await call_next(request)
        auth = request.headers.get("authorization", "")
        key = auth[-32:] if auth.startswith("Bearer ") else (request.client.host if request.client else "?")
        now = time.monotonic()
        rate = max(1, s.rate_limit_per_minute) / 60.0
        tokens, last = self._buckets.get(key, (float(s.rate_limit_per_minute), now))
        tokens = min(float(s.rate_limit_per_minute), tokens + (now - last) * rate)
        if tokens < 1.0:
            retry_after = int(max(1, (1.0 - tokens) / rate))
            return JSONResponse(
                status_code=429,
                headers={"Retry-After": str(retry_after)},
                content={"title": "Too Many Requests", "status": 429,
                         "error_code": "rate_limited",
                         "detail": "rate limit exceeded; back off with jitter"},
            )
        self._buckets[key] = (tokens - 1.0, now)
        # Occasional sweep so idle keys do not accumulate forever.
        if now - self._last_sweep > 300:
            self._buckets = {k: v for k, v in self._buckets.items()
                             if now - v[1] < 3600}
            self._last_sweep = now
        return await call_next(request)


__all__ = ["SecurityHeadersMiddleware", "RequestSizeLimitMiddleware",
           "RateLimitMiddleware"]
