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
