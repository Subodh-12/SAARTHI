"""Tests for Section 7.4 & Section 5: Object storage adapter, atomic promotion,
range downloads, checksum integrity, and error handling.
"""
from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path
import pytest

from app.adapters.storage import (
    LocalObjectStorage, IntegrityError, ObjectNotFoundError, StorageError
)


@pytest.fixture
def storage():
    tmpdir = tempfile.mkdtemp()
    return LocalObjectStorage(tmpdir)


@pytest.mark.asyncio
async def test_upload_and_download(storage):
    data = b"Hello, SAARTHI pack test content!"
    sha = hashlib.sha256(data).hexdigest()
    
    # Upload with matching checksum
    key = await storage.upload_artifact("test/pack.bin", data, expected_sha256=sha)
    assert key == "test/pack.bin"
    assert await storage.exists(key)
    assert await storage.get_size(key) == len(data)

    # Download full
    downloaded = await storage.download_artifact(key)
    assert downloaded == data


@pytest.mark.asyncio
async def test_upload_checksum_mismatch_raises(storage):
    data = b"valid data"
    bad_sha = "0000000000000000000000000000000000000000000000000000000000000000"
    
    with pytest.raises(IntegrityError):
        await storage.upload_artifact("bad.bin", data, expected_sha256=bad_sha)


@pytest.mark.asyncio
async def test_atomic_promotion(storage):
    data = b"pack archive version 1"
    temp_key = "tmp/upload_123.bin"
    final_key = "published/pack_sci9_ch1.bin"

    await storage.upload_artifact(temp_key, data)
    assert await storage.exists(temp_key)
    assert not await storage.exists(final_key)

    # Atomically promote
    await storage.promote_artifact(temp_key, final_key)
    assert not await storage.exists(temp_key)
    assert await storage.exists(final_key)
    assert await storage.download_artifact(final_key) == data


@pytest.mark.asyncio
async def test_range_download(storage):
    data = b"0123456789ABCDEF"
    key = await storage.upload_artifact("range.bin", data)

    # Range 0-3 -> b"0123"
    part1 = await storage.download_range(key, 0, 3)
    assert part1 == b"0123"

    # Range 10-15 -> b"ABCDEF"
    part2 = await storage.download_range(key, 10, 15)
    assert part2 == b"ABCDEF"


@pytest.mark.asyncio
async def test_missing_object_error(storage):
    with pytest.raises(ObjectNotFoundError):
        await storage.download_artifact("non_existent.bin")


@pytest.mark.asyncio
async def test_path_traversal_protection(storage):
    with pytest.raises(StorageError):
        await storage.download_artifact("../../etc/passwd")


@pytest.mark.asyncio
async def test_s3_storage_contract():
    import httpx
    from app.adapters.storage import S3MinIOStorage

    objects = {}

    def s3_handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path  # e.g. /my-bucket/path/key.bin
        parts = path.lstrip("/").split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ""

        if request.method == "PUT":
            copy_src = request.headers.get("x-amz-copy-source")
            if copy_src:
                src_key = copy_src.lstrip("/").split("/", 1)[1]
                if src_key not in objects:
                    return httpx.Response(404, text="Source not found")
                objects[key] = objects[src_key]
                return httpx.Response(200)
            objects[key] = request.content
            return httpx.Response(200)

        elif request.method == "GET":
            if key not in objects:
                return httpx.Response(404, text="Not found")
            content = objects[key]
            range_header = request.headers.get("Range")
            if range_header and range_header.startswith("bytes="):
                rng = range_header.replace("bytes=", "").split("-")
                start, end = int(rng[0]), int(rng[1])
                if start >= len(content) or end < start:
                    return httpx.Response(416, text="Invalid range")
                chunk = content[start : end + 1]
                return httpx.Response(206, content=chunk, headers={"Content-Range": f"bytes {start}-{end}/{len(content)}"})
            return httpx.Response(200, content=content)

        elif request.method == "HEAD":
            if key not in objects:
                return httpx.Response(404)
            return httpx.Response(200, headers={"Content-Length": str(len(objects[key]))})

        elif request.method == "DELETE":
            objects.pop(key, None)
            return httpx.Response(204)

        return httpx.Response(405)

    transport = httpx.MockTransport(s3_handler)
    client = httpx.AsyncClient(transport=transport)
    s3 = S3MinIOStorage(
        endpoint_url="http://s3.local:9000",
        bucket="my-bucket",
        access_key="test_key",
        secret_key="test_secret",
        client=client,
    )

    data = b"S3 pack data payload"
    sha = hashlib.sha256(data).hexdigest()

    # Upload
    key = await s3.upload_artifact("test/pack.tar.gz", data, expected_sha256=sha)
    assert key == "test/pack.tar.gz"
    assert await s3.exists(key)
    assert await s3.get_size(key) == len(data)

    # Download
    assert await s3.download_artifact(key) == data

    # Range download
    range_bytes = await s3.download_range(key, 0, 6)
    assert range_bytes == b"S3 pack"

    # Promote
    await s3.promote_artifact(key, "promoted/pack.tar.gz")
    assert not await s3.exists(key)
    assert await s3.exists("promoted/pack.tar.gz")
    assert await s3.download_artifact("promoted/pack.tar.gz") == data

    # Delete
    assert await s3.delete_artifact("promoted/pack.tar.gz")
    assert not await s3.exists("promoted/pack.tar.gz")

