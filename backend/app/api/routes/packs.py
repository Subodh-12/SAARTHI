"""Pack routes — manifest list, download with HTTP Range support for resumable transfers."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from ...core.settings import get_settings
from ...domain.schemas import PackDownloadInfo, PackManifest
from ..middleware import require_device_auth

router = APIRouter(prefix="/packs", tags=["packs"])


@router.get("/manifest", response_model=list[PackManifest])
async def list_pack_manifests(request: Request):
    pack_repo = request.app.state.pack_repository
    return await pack_repo.list_pack_manifests()


@router.get("/{pack_id}/versions/{version}", response_model=PackDownloadInfo)
async def get_pack_download_info(
    pack_id: str, version: str,
    request: Request,
    ctx: tuple[str, str] = Depends(require_device_auth),
):
    pack_repo = request.app.state.pack_repository
    m = await pack_repo.get_pack_manifest(pack_id, version)
    if not m:
        raise HTTPException(status_code=404, detail="pack not found")
    base = str(request.base_url)
    url = f"{base}api/v1/packs/{pack_id}/versions/{version}/download"
    return PackDownloadInfo(
        pack_id=m.pack_id,
        version=m.version,
        url=url,
        byte_size=m.archive_byte_size if m.archive_byte_size else m.byte_size,
        checksum_sha256=m.checksum_sha256,
        archive_sha256=m.archive_sha256 if m.archive_sha256 else m.checksum_sha256,
        archive_byte_size=m.archive_byte_size if m.archive_byte_size else m.byte_size,
    )


@router.get("/{pack_id}")
async def get_pack_by_id(
    pack_id: str,
    request: Request,
    ctx: tuple[str, str] = Depends(require_device_auth),
):
    """Section 8 alias: GET /packs/{id}."""
    pack_repo = request.app.state.pack_repository
    manifests = await pack_repo.list_pack_manifests()
    matching = [m for m in manifests if m.pack_id == pack_id]
    if not matching:
        raise HTTPException(status_code=404, detail="pack not found")
    latest = matching[0]
    return await get_pack_download_info(pack_id, latest.version, request, ctx)


@router.get("/{pack_id}/versions/{version}/download")
async def download_pack(
    pack_id: str, version: str,
    request: Request,
    ctx: tuple[str, str] = Depends(require_device_auth),
):
    s = get_settings()
    p_path = Path(s.packs_dir) / f"{pack_id}-{version}.srt.tar.gz"
    media_type = "application/gzip"
    if not p_path.exists():
        p_path = Path(s.packs_dir) / f"{pack_id}-{version}.json"
        media_type = "application/json"
        if not p_path.exists():
            raise HTTPException(status_code=404, detail="pack file not found")

    file_size = p_path.stat().st_size
    range_header = request.headers.get("range") or request.headers.get("Range")

    pack_repo = request.app.state.pack_repository
    device_id, _ = ctx
    m = await pack_repo.get_pack_manifest(pack_id, version)

    etag = f'"{m.archive_sha256 or m.checksum_sha256}"' if m else f'"{hashlib.sha256(p_path.read_bytes()).hexdigest()}"'

    if range_header:
        # Range header format: bytes=start-end or bytes=start-
        range_match = re.match(r"^bytes=(\d+)-(\d+)?$", range_header.strip())
        if not range_match:
            return Response(
                status_code=416,
                headers={"Content-Range": f"bytes */{file_size}"},
            )
        start = int(range_match.group(1))
        end_str = range_match.group(2)
        end = int(end_str) if end_str is not None else file_size - 1

        if start >= file_size or start > end:
            return Response(
                status_code=416,
                headers={"Content-Range": f"bytes */{file_size}"},
            )

        end = min(end, file_size - 1)
        length = end - start + 1

        with open(p_path, "rb") as f:
            f.seek(start)
            data = f.read(length)

        # Full install marked when the final byte of the archive is served
        if end == file_size - 1 and m:
            await pack_repo.record_installed_pack(
                device_id, pack_id, version,
                m.archive_byte_size or m.byte_size,
                m.archive_sha256 or m.checksum_sha256,
            )

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(length),
            "ETag": etag,
            "Content-Disposition": f'attachment; filename="{p_path.name}"',
        }
        return Response(content=data, status_code=206, headers=headers, media_type=media_type)

    # Full non-range download
    if m:
        await pack_repo.record_installed_pack(
            device_id, pack_id, version,
            m.archive_byte_size or m.byte_size,
            m.archive_sha256 or m.checksum_sha256,
        )

    with open(p_path, "rb") as f:
        data = f.read()

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
        "ETag": etag,
        "Content-Disposition": f'attachment; filename="{p_path.name}"',
    }
    return Response(content=data, status_code=200, headers=headers, media_type=media_type)


__all__ = ["router"]
