"""Integration tests for pack checksum verification and resumable Range downloads.

Design Document v2 Sections 4.4, 4.5, 5, 10.
"""
from __future__ import annotations

import hashlib
import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from app.core.settings import reset_settings_cache
from app.domain.ruleset import reset_ruleset_cache
from app.content.pack_loader import reset_pack_cache
from app.main import create_app

TMP_DB = tempfile.mktemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TMP_DB}"
os.environ["PERSISTENCE_BACKEND"] = "sqlite"

reset_settings_cache()
reset_ruleset_cache()
reset_pack_cache()


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def _auth_headers(client):
    reg_resp = client.post(
        "/api/v1/devices",
        json={"public_key_spki_b64": "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE12345678901234567890123456789012"},
    )
    assert reg_resp.status_code == 201
    auth_data = reg_resp.json()
    token = auth_data["access_token"]
    device_id = auth_data["device_id"]
    headers = {"Authorization": f"Bearer {token}", "X-Device-Id": device_id}

    # Link an active learner
    lrn_resp = client.post(
        "/api/v1/learners",
        json={"display_label": "Sunita", "locale": "or", "grade": "class9", "subject": "science"},
        headers=headers,
    )
    assert lrn_resp.status_code == 201
    return headers


def test_pack_download_info_has_archive_hash(client):
    headers = _auth_headers(client)

    # 1. Manifest endpoint
    m_resp = client.get("/api/v1/packs/manifest")
    assert m_resp.status_code == 200
    manifests = m_resp.json()
    assert len(manifests) >= 1
    pack = manifests[0]
    pack_id = pack["pack_id"]
    version = pack["version"]

    # 2. Get pack download info
    info_resp = client.get(
        f"/api/v1/packs/{pack_id}/versions/{version}",
        headers=headers,
    )
    assert info_resp.status_code == 200
    info = info_resp.json()
    assert info["pack_id"] == pack_id
    assert info["version"] == version
    assert "url" in info
    assert info["byte_size"] > 0
    assert len(info["checksum_sha256"]) == 64
    assert len(info["archive_sha256"]) == 64
    assert info["archive_byte_size"] > 0

    # 3. GET /packs/{id} alias (Section 8)
    alias_resp = client.get(f"/api/v1/packs/{pack_id}", headers=headers)
    assert alias_resp.status_code == 200
    assert alias_resp.json()["pack_id"] == pack_id


def test_pack_resumable_range_download(client):
    headers = _auth_headers(client)

    m_resp = client.get("/api/v1/packs/manifest")
    pack = m_resp.json()[0]
    pack_id = pack["pack_id"]
    version = pack["version"]

    # Download full content
    full_resp = client.get(
        f"/api/v1/packs/{pack_id}/versions/{version}/download",
        headers=headers,
    )
    assert full_resp.status_code == 200
    assert full_resp.headers.get("Accept-Ranges") == "bytes"
    full_bytes = full_resp.content
    total_size = len(full_bytes)
    assert total_size > 0
    expected_sha = hashlib.sha256(full_bytes).hexdigest()

    # Resumable Range request Part 1: bytes=0-511
    part1_headers = dict(headers)
    part1_headers["Range"] = "bytes=0-511"
    part1_resp = client.get(
        f"/api/v1/packs/{pack_id}/versions/{version}/download",
        headers=part1_headers,
    )
    assert part1_resp.status_code == 206
    assert part1_resp.headers.get("Content-Range") == f"bytes 0-511/{total_size}"
    assert len(part1_resp.content) == 512
    assert part1_resp.content == full_bytes[:512]

    # Resumable Range request Part 2: bytes=512-
    part2_headers = dict(headers)
    part2_headers["Range"] = "bytes=512-"
    part2_resp = client.get(
        f"/api/v1/packs/{pack_id}/versions/{version}/download",
        headers=part2_headers,
    )
    assert part2_resp.status_code == 206
    assert part2_resp.headers.get("Content-Range") == f"bytes 512-{total_size - 1}/{total_size}"
    assert part2_resp.content == full_bytes[512:]

    # Assembled bytes match full file and checksum exactly
    assembled = part1_resp.content + part2_resp.content
    assert len(assembled) == total_size
    assert hashlib.sha256(assembled).hexdigest() == expected_sha

    # Invalid range returns 416
    invalid_headers = dict(headers)
    invalid_headers["Range"] = f"bytes={total_size + 1000}-"
    invalid_resp = client.get(
        f"/api/v1/packs/{pack_id}/versions/{version}/download",
        headers=invalid_headers,
    )
    assert invalid_resp.status_code == 416
