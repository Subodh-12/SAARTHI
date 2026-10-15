"""Object storage adapter (Design Document v2 Section 5, 7.4 & 14).

Storage roles (Section 5):
- Object storage: Source assets and downloadable pack artifacts.
- Packs written under a temporary key, verified, then promoted atomically.
- Supports MinIO locally and S3-compatible production storage.
- Local filesystem adapter provided for offline / local-first development.
"""
from __future__ import annotations

import abc
import hashlib
import os
import shutil
from pathlib import Path
from typing import Any, Optional

from ..core.logging import get_logger
from ..core.settings import get_settings

log = get_logger("saarthi.storage")


class StorageError(Exception):
    """Base error for object storage operations."""
    pass


class ObjectNotFoundError(StorageError):
    pass


class IntegrityError(StorageError):
    pass


class ObjectStorage(abc.ABC):
    """Abstract interface for object storage."""

    @abc.abstractmethod
    async def upload_artifact(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        expected_sha256: Optional[str] = None,
    ) -> str:
        """Upload an artifact. If expected_sha256 is provided, verifies integrity."""
        ...

    @abc.abstractmethod
    async def download_artifact(self, key: str) -> bytes:
        """Download complete artifact bytes."""
        ...

    @abc.abstractmethod
    async def download_range(self, key: str, start: int, end: int) -> bytes:
        """Download byte range [start, end] inclusive."""
        ...

    @abc.abstractmethod
    async def promote_artifact(self, temp_key: str, final_key: str) -> None:
        """Atomically promote a verified temporary artifact to final location."""
        ...

    @abc.abstractmethod
    async def delete_artifact(self, key: str) -> bool:
        """Delete artifact by key."""
        ...

    @abc.abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if artifact exists."""
        ...

    @abc.abstractmethod
    async def get_size(self, key: str) -> int:
        """Return byte size of artifact."""
        ...


class LocalObjectStorage(ObjectStorage):
    """Local filesystem storage adapter (used for local dev, tests, and offline runs)."""

    def __init__(self, base_dir: Path | str) -> None:
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, key: str) -> Path:
        # Sanitize key to prevent path traversal
        clean_key = Path(key).as_posix().lstrip("/")
        target = (self.base_dir / clean_key).resolve()
        if not str(target).startswith(str(self.base_dir)):
            raise StorageError(f"path traversal detected: {key}")
        return target

    async def upload_artifact(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        expected_sha256: Optional[str] = None,
    ) -> str:
        if expected_sha256:
            actual_sha = hashlib.sha256(data).hexdigest()
            if actual_sha.lower() != expected_sha256.lower():
                raise IntegrityError(f"checksum mismatch: expected {expected_sha256}, got {actual_sha}")

        target = self._path_for(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Write via temporary file for atomic write
        tmp_target = target.with_suffix(".tmp_" + os.urandom(4).hex())
        tmp_target.write_bytes(data)
        os.replace(tmp_target, target)
        return key

    async def download_artifact(self, key: str) -> bytes:
        target = self._path_for(key)
        if not target.exists() or not target.is_file():
            raise ObjectNotFoundError(f"object not found: {key}")
        return target.read_bytes()

    async def download_range(self, key: str, start: int, end: int) -> bytes:
        target = self._path_for(key)
        if not target.exists() or not target.is_file():
            raise ObjectNotFoundError(f"object not found: {key}")
        size = target.stat().st_size
        if start < 0 or start >= size or end < start:
            raise StorageError(f"invalid byte range: {start}-{end} for size {size}")
        with open(target, "rb") as f:
            f.seek(start)
            return f.read(end - start + 1)

    async def promote_artifact(self, temp_key: str, final_key: str) -> None:
        src = self._path_for(temp_key)
        dst = self._path_for(final_key)
        if not src.exists() or not src.is_file():
            raise ObjectNotFoundError(f"temp object not found: {temp_key}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        os.replace(src, dst)

    async def delete_artifact(self, key: str) -> bool:
        target = self._path_for(key)
        if target.exists() and target.is_file():
            target.unlink()
            return True
        return False

    async def exists(self, key: str) -> bool:
        target = self._path_for(key)
        return target.exists() and target.is_file()

    async def get_size(self, key: str) -> int:
        target = self._path_for(key)
        if not target.exists() or not target.is_file():
            raise ObjectNotFoundError(f"object not found: {key}")
        return target.stat().st_size


import httpx


class S3MinIOStorage(ObjectStorage):
    """S3-compatible / MinIO storage adapter using actual S3 REST API calls."""

    def __init__(
        self,
        endpoint_url: str,
        bucket: str,
        access_key: str,
        secret_key: str,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.endpoint_url = endpoint_url.rstrip("/")
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key
        self._client = client

    def _client_context(self) -> httpx.AsyncClient:
        if self._client is not None:
            return self._client
        return httpx.AsyncClient(timeout=30.0)

    def _url_for(self, key: str) -> str:
        clean_key = key.lstrip("/")
        return f"{self.endpoint_url}/{self.bucket}/{clean_key}"

    def _headers(self, extra: Optional[dict[str, str]] = None) -> dict[str, str]:
        import base64
        headers = {}
        if self.access_key and self.secret_key:
            auth_str = f"{self.access_key}:{self.secret_key}"
            headers["Authorization"] = f"Basic {base64.b64encode(auth_str.encode()).decode()}"
        if extra:
            headers.update(extra)
        return headers

    async def upload_artifact(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        expected_sha256: Optional[str] = None,
    ) -> str:
        if expected_sha256:
            actual_sha = hashlib.sha256(data).hexdigest()
            if actual_sha.lower() != expected_sha256.lower():
                raise IntegrityError(f"checksum mismatch: expected {expected_sha256}, got {actual_sha}")

        url = self._url_for(key)
        headers = self._headers({"Content-Type": content_type, "Content-Length": str(len(data))})
        client = self._client_context()
        try:
            resp = await client.put(url, content=data, headers=headers)
            if resp.status_code not in (200, 201, 204):
                raise StorageError(f"upload failed for {key}: HTTP {resp.status_code} - {resp.text}")
            return key
        except httpx.RequestError as e:
            raise StorageError(f"upload connection error: {e}")
        finally:
            if self._client is None:
                await client.aclose()

    async def download_artifact(self, key: str) -> bytes:
        url = self._url_for(key)
        headers = self._headers()
        client = self._client_context()
        try:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 404:
                raise ObjectNotFoundError(f"object not found: {key}")
            if resp.status_code != 200:
                raise StorageError(f"download failed for {key}: HTTP {resp.status_code} - {resp.text}")
            return resp.content
        except httpx.RequestError as e:
            raise StorageError(f"download connection error: {e}")
        finally:
            if self._client is None:
                await client.aclose()

    async def download_range(self, key: str, start: int, end: int) -> bytes:
        url = self._url_for(key)
        headers = self._headers({"Range": f"bytes={start}-{end}"})
        client = self._client_context()
        try:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 404:
                raise ObjectNotFoundError(f"object not found: {key}")
            if resp.status_code == 416:
                raise StorageError(f"invalid byte range: {start}-{end}")
            if resp.status_code not in (200, 206):
                raise StorageError(f"range download failed: HTTP {resp.status_code}")
            return resp.content
        except httpx.RequestError as e:
            raise StorageError(f"range download connection error: {e}")
        finally:
            if self._client is None:
                await client.aclose()

    async def promote_artifact(self, temp_key: str, final_key: str) -> None:
        final_url = self._url_for(final_key)
        source_header = f"/{self.bucket}/{temp_key.lstrip('/')}"
        headers = self._headers({"x-amz-copy-source": source_header})
        client = self._client_context()
        try:
            resp = await client.put(final_url, headers=headers)
            if resp.status_code == 404:
                raise ObjectNotFoundError(f"temp object not found: {temp_key}")
            if resp.status_code not in (200, 201, 204):
                raise StorageError(f"promotion failed from {temp_key} to {final_key}: HTTP {resp.status_code}")
            await self.delete_artifact(temp_key)
        except httpx.RequestError as e:
            raise StorageError(f"promotion connection error: {e}")
        finally:
            if self._client is None:
                await client.aclose()

    async def delete_artifact(self, key: str) -> bool:
        url = self._url_for(key)
        headers = self._headers()
        client = self._client_context()
        try:
            resp = await client.delete(url, headers=headers)
            return resp.status_code in (200, 204)
        except httpx.RequestError as e:
            raise StorageError(f"delete connection error: {e}")
        finally:
            if self._client is None:
                await client.aclose()

    async def exists(self, key: str) -> bool:
        url = self._url_for(key)
        headers = self._headers()
        client = self._client_context()
        try:
            resp = await client.head(url, headers=headers)
            return resp.status_code == 200
        except httpx.RequestError:
            return False
        finally:
            if self._client is None:
                await client.aclose()

    async def get_size(self, key: str) -> int:
        url = self._url_for(key)
        headers = self._headers()
        client = self._client_context()
        try:
            resp = await client.head(url, headers=headers)
            if resp.status_code == 404:
                raise ObjectNotFoundError(f"object not found: {key}")
            if resp.status_code != 200:
                raise StorageError(f"head failed for {key}: HTTP {resp.status_code}")
            cl = resp.headers.get("Content-Length")
            if cl is None:
                raise StorageError("missing Content-Length header")
            return int(cl)
        except httpx.RequestError as e:
            raise StorageError(f"get_size connection error: {e}")
        finally:
            if self._client is None:
                await client.aclose()


_storage_singleton: Optional[ObjectStorage] = None


def get_object_storage() -> ObjectStorage:
    global _storage_singleton
    if _storage_singleton is None:
        s = get_settings()
        if getattr(s, "object_storage_backend", "local") == "s3" or getattr(s, "object_storage_backend", "local") == "minio":
            _storage_singleton = S3MinIOStorage(
                endpoint_url=getattr(s, "minio_url", "http://localhost:9000"),
                bucket=getattr(s, "minio_bucket", "saarthi-packs"),
                access_key=getattr(s, "minio_access_key", "saarthi"),
                secret_key=getattr(s, "minio_secret_key", "saarthi123"),
            )
        else:
            base = Path(__file__).resolve().parents[3] / "packs"
            _storage_singleton = LocalObjectStorage(base)
    return _storage_singleton


__all__ = [
    "ObjectStorage",
    "LocalObjectStorage",
    "S3MinIOStorage",
    "StorageError",
    "ObjectNotFoundError",
    "IntegrityError",
    "get_object_storage",
]
