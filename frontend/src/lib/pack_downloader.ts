// Resumable Pack Downloader (Design Document v2 Sections 5 and 10).
//
// Requirements:
// - Download resumable segments of 512 KB using HTTP Range requests.
// - Verify Content-Range, archive size, and SHA-256 checksum of downloaded bytes.
// - Resume an incomplete transfer without re-downloading verified data.
// - Atomic installation upon full verification; retain old pack on failure.
// - Enforce pack compatibility with min_app_version.
// - Never mark a partially downloaded pack as installed.

import { api } from "../api/client";
import { saveInstalledPack, getInstalledPacks } from "../store/db";

export const SEGMENT_SIZE = 512 * 1024; // 512 KB segments (Section 10)
export const CURRENT_APP_VERSION = "1.0.0";

export interface DownloadProgress {
  downloadedBytes: number;
  totalBytes: number;
  segmentIndex: number;
  totalSegments: number;
  percent: number;
}

export interface PackDownloadOptions {
  pack_id: string;
  version: string;
  expected_byte_size: number;
  expected_checksum_sha256: string;
  min_app_version?: string;
  onProgress?: (p: DownloadProgress) => void;
}

export interface DownloadResult {
  success: boolean;
  error?: string;
  bytesDownloaded?: number;
  resumed?: boolean;
}

// In-memory or session-based partial chunks cache (resumable across interruptions)
const partialSegmentsCache = new Map<string, Uint8Array[]>();

export function clearPartialDownload(pack_id: string, version: string) {
  const key = `${pack_id}:${version}`;
  partialSegmentsCache.delete(key);
}

function isVersionCompatible(minAppVersion?: string): boolean {
  if (!minAppVersion) return true;
  // Simple semver compare: major.minor.patch
  const parse = (v: string) => v.split(".").map((n) => parseInt(n, 10) || 0);
  const [cMaj, cMin, cPat] = parse(CURRENT_APP_VERSION);
  const [mMaj, mMin, mPat] = parse(minAppVersion);
  if (cMaj !== mMaj) return cMaj > mMaj;
  if (cMin !== mMin) return cMin > mMin;
  return cPat >= mPat;
}

export async function downloadPackResumable(options: PackDownloadOptions): Promise<DownloadResult> {
  const {
    pack_id,
    version,
    expected_byte_size,
    expected_checksum_sha256,
    min_app_version,
    onProgress,
  } = options;

  // 1. Enforce compatibility
  if (!isVersionCompatible(min_app_version)) {
    return {
      success: false,
      error: `Pack requires app version >= ${min_app_version}, current is ${CURRENT_APP_VERSION}`,
    };
  }

  // 2. Storage guard check (warn at 50 MB, minimum 25 MB free)
  if (typeof navigator !== "undefined" && navigator.storage && navigator.storage.estimate) {
    try {
      const estimate = await navigator.storage.estimate();
      if (estimate.quota && estimate.usage) {
        const freeBytes = estimate.quota - estimate.usage;
        if (freeBytes < 25 * 1024 * 1024) {
          return { success: false, error: "Storage full (less than 25 MB free)" };
        }
      }
    } catch {
      // Storage estimation optional
    }
  }

  const base = await api.apiBaseUrl();
  const url = `${base}/api/v1/packs/${pack_id}/versions/${version}/download`;
  const key = `${pack_id}:${version}`;

  let segments = partialSegmentsCache.get(key) || [];
  let downloadedBytes = segments.reduce((sum, s) => sum + s.byteLength, 0);
  const wasResumed = downloadedBytes > 0;

  const totalBytes = expected_byte_size;
  const totalSegments = Math.ceil(totalBytes / SEGMENT_SIZE);

  try {
    let currentByte = downloadedBytes;

    while (currentByte < totalBytes) {
      const start = currentByte;
      const end = Math.min(start + SEGMENT_SIZE - 1, totalBytes - 1);

      const resp = await fetch(url, {
        headers: {
          Range: `bytes=${start}-${end}`,
        },
      });

      if (resp.status !== 206 && resp.status !== 200) {
        throw new Error(`Download failed with HTTP ${resp.status}`);
      }

      const buf = await resp.arrayBuffer();
      const chunk = new Uint8Array(buf);

      // Verify received slice size
      const expectedChunkSize = end - start + 1;
      if (resp.status === 206 && chunk.byteLength !== expectedChunkSize) {
        throw new Error(`Chunk size mismatch: expected ${expectedChunkSize}, got ${chunk.byteLength}`);
      }

      segments.push(chunk);
      partialSegmentsCache.set(key, segments);

      currentByte += chunk.byteLength;
      downloadedBytes = currentByte;

      if (onProgress) {
        onProgress({
          downloadedBytes,
          totalBytes,
          segmentIndex: segments.length,
          totalSegments,
          percent: Math.round((downloadedBytes / totalBytes) * 100),
        });
      }
    }

    // Combine all segments into one continuous Uint8Array
    const fullBuffer = new Uint8Array(downloadedBytes);
    let offset = 0;
    for (const seg of segments) {
      fullBuffer.set(seg, offset);
      offset += seg.byteLength;
    }

    // Validate SHA-256 checksum of full archive
    const digest = await crypto.subtle.digest("SHA-256", fullBuffer);
    const hashHex = Array.from(new Uint8Array(digest))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");

    if (hashHex.toLowerCase() !== expected_checksum_sha256.toLowerCase()) {
      clearPartialDownload(pack_id, version);
      return {
        success: false,
        error: `Checksum mismatch: expected ${expected_checksum_sha256}, got ${hashHex}`,
      };
    }

    // Atomic install: save pack to shared database
    let manifestText = "";
    try {
      manifestText = new TextDecoder().decode(fullBuffer);
    } catch {
      manifestText = JSON.stringify({ pack_id, version, checksum_sha256: hashHex });
    }

    await saveInstalledPack({
      pack_id,
      version,
      byte_size: downloadedBytes,
      checksum_sha256: hashHex,
      installed_at: Date.now(),
      manifest_json: manifestText,
    });

    // Cleanup temporary partial segments
    clearPartialDownload(pack_id, version);

    return {
      success: true,
      bytesDownloaded: downloadedBytes,
      resumed: wasResumed,
    };
  } catch (err: any) {
    return {
      success: false,
      error: err?.message || String(err),
      bytesDownloaded: downloadedBytes,
      resumed: wasResumed,
    };
  }
}
