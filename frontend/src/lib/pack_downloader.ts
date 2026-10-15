// Resumable Pack Downloader (Design Document v2 Sections 5 and 10).
//
// Requirements:
// - Download resumable segments of 512 KB using HTTP Range requests.
// - Verify Content-Range, archive size, and SHA-256 checksum of downloaded bytes.
// - Resume an incomplete transfer without re-downloading verified data.
// - Durable partial segment storage surviving browser or application restart.
// - Atomic installation upon full verification; retain old pack on failure.
// - Enforce pack compatibility with min_app_version.
// - Never mark a partially downloaded pack as installed.
// - Correct decompression of gzip archives into valid JSON.
// - Full schema validation before committing pack.

import { api } from "../api/client";
import { saveInstalledPack } from "../store/db";
import {
  deletePartialDownload,
  getPartialDownload,
  putPartialDownload,
  PartialDownloadSegment,
  getActiveProfileSession,
  getActiveSharedProfile,
} from "../store/profile_session";

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
  segment_size?: number;
  onProgress?: (p: DownloadProgress) => void;
}

export interface DownloadResult {
  success: boolean;
  error?: string;
  bytesDownloaded?: number;
  resumed?: boolean;
}

export async function clearPartialDownload(pack_id: string, version: string): Promise<void> {
  const key = `${pack_id}:${version}`;
  await deletePartialDownload(key);
}

function isVersionCompatible(minAppVersion?: string): boolean {
  if (!minAppVersion) return true;
  const parse = (v: string) => v.split(".").map((n) => parseInt(n, 10) || 0);
  const [cMaj, cMin, cPat] = parse(CURRENT_APP_VERSION);
  const [mMaj, mMin, mPat] = parse(minAppVersion);
  if (cMaj !== mMaj) return cMaj > mMaj;
  if (cMin !== mMin) return cMin > mMin;
  return cPat >= mPat;
}

export async function decompressArchive(bytes: Uint8Array): Promise<string> {
  // Check gzip magic bytes (0x1f, 0x8b)
  if (bytes.length >= 2 && bytes[0] === 0x1f && bytes[1] === 0x8b) {
    if (typeof DecompressionStream !== "undefined") {
      const resp = new Response(bytes as unknown as BodyInit);
      const stream = resp.body?.pipeThrough(new DecompressionStream("gzip"));
      if (stream) {
        return await new Response(stream).text();
      }
    }
    throw new Error("DecompressionStream is not supported in this runtime environment");
  }
  return new TextDecoder("utf-8").decode(bytes);
}

export function validatePackPayload(parsed: any, expectedPackId: string): void {
  if (!parsed || typeof parsed !== "object") {
    throw new Error("Invalid pack format: root payload must be an object");
  }
  if (!parsed.manifest || typeof parsed.manifest !== "object") {
    throw new Error("Invalid pack format: manifest object missing");
  }
  if (parsed.manifest.pack_id !== expectedPackId) {
    throw new Error(
      `Invalid pack format: pack_id mismatch (got ${parsed.manifest.pack_id}, expected ${expectedPackId})`
    );
  }
  if (
    !Array.isArray(parsed.chapters) ||
    !Array.isArray(parsed.concepts) ||
    !Array.isArray(parsed.chunks) ||
    !Array.isArray(parsed.questions) ||
    !Array.isArray(parsed.glossary)
  ) {
    throw new Error(
      "Invalid pack format: chapters, concepts, chunks, questions, or glossary are missing or not arrays"
    );
  }
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

  // 1. Enforce version compatibility
  if (!isVersionCompatible(min_app_version)) {
    return {
      success: false,
      error: `Pack requires app version >= ${min_app_version}, current is ${CURRENT_APP_VERSION}`,
    };
  }

  // 2. Storage guard check (minimum 25 MB free)
  if (typeof navigator !== "undefined" && navigator.storage && navigator.storage.estimate) {
    try {
      const estimate = await navigator.storage.estimate();
      if (estimate.quota !== undefined && estimate.usage !== undefined) {
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
  const totalBytes = expected_byte_size;
  const segmentSize = options.segment_size || SEGMENT_SIZE;
  const totalSegments = Math.ceil(totalBytes / segmentSize) || 1;

  // 3. Load durable partial download segments from IndexedDB
  let segments: PartialDownloadSegment[] = [];
  let downloadedBytes = 0;
  let wasResumed = false;

  try {
    const existing = await getPartialDownload(key);
    if (existing) {
      if (
        existing.expected_byte_size === expected_byte_size &&
        existing.expected_checksum_sha256.toLowerCase() === expected_checksum_sha256.toLowerCase()
      ) {
        // Sort and verify continuity
        const sorted = [...existing.segments].sort((a, b) => a.start - b.start);
        let continuous = 0;
        for (const seg of sorted) {
          const expectedLen = seg.end - seg.start + 1;
          if (seg.start === continuous && seg.bytes.byteLength === expectedLen) {
            continuous = seg.end + 1;
            segments.push(seg);
          } else {
            break;
          }
        }
        downloadedBytes = continuous;
        if (downloadedBytes > 0) {
          wasResumed = true;
        }
      } else {
        await deletePartialDownload(key);
      }
    }
  } catch (err) {
    // If reading partial fails, start from 0
    segments = [];
    downloadedBytes = 0;
  }

  try {
    let currentByte = downloadedBytes;

    while (currentByte < totalBytes) {
      const start = currentByte;
      const end = Math.min(start + segmentSize - 1, totalBytes - 1);

      const resp = await fetch(url, {
        headers: {
          Range: `bytes=${start}-${end}`,
        },
      });

      if (resp.status === 416) {
        await deletePartialDownload(key);
        throw new Error(`Download range not satisfiable (HTTP 416) at bytes=${start}-${end}`);
      }

      if (resp.status !== 206 && resp.status !== 200) {
        throw new Error(`Download failed with HTTP ${resp.status}`);
      }

      const buf = await resp.arrayBuffer();
      const chunk = new Uint8Array(buf);

      if (resp.status === 200) {
        // Server returned the full file (ignored Range header)
        if (start === 0 && (chunk.byteLength === totalBytes || totalBytes === 0)) {
          segments = [{ start: 0, end: chunk.byteLength - 1, bytes: chunk }];
          currentByte = chunk.byteLength;
          downloadedBytes = currentByte;
          break;
        } else {
          throw new Error("Server returned HTTP 200 for partial range request; unexpected full body");
        }
      }

      // HTTP 206 Partial Content: validate Content-Range
      const contentRange = resp.headers.get("content-range");
      if (contentRange) {
        const match = contentRange.match(/bytes\s+(\d+)-(\d+)\/(\d+|\*)/i);
        if (match) {
          const rStart = parseInt(match[1], 10);
          const rEnd = parseInt(match[2], 10);
          const rTotal = match[3] !== "*" ? parseInt(match[3], 10) : totalBytes;
          if (rStart !== start || rEnd !== end || rTotal !== totalBytes) {
            throw new Error(
              `Content-Range header mismatch: expected ${start}-${end}/${totalBytes}, got ${contentRange}`
            );
          }
        }
      }

      const expectedChunkSize = end - start + 1;
      if (chunk.byteLength !== expectedChunkSize) {
        throw new Error(`Chunk size mismatch: expected ${expectedChunkSize}, got ${chunk.byteLength}`);
      }

      segments.push({ start, end, bytes: chunk });
      currentByte += chunk.byteLength;
      downloadedBytes = currentByte;

      // Persist partial segments durably into IndexedDB
      await putPartialDownload({
        id: key,
        pack_id,
        version,
        expected_byte_size: totalBytes,
        expected_checksum_sha256,
        updated_at: Date.now(),
        segments,
      });

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

    if (downloadedBytes !== totalBytes) {
      throw new Error(`Incomplete download: received ${downloadedBytes} bytes, expected ${totalBytes}`);
    }

    // Combine all segments into one continuous Uint8Array
    const fullBuffer = new Uint8Array(downloadedBytes);
    let offset = 0;
    for (const seg of segments) {
      fullBuffer.set(seg.bytes, offset);
      offset += seg.bytes.byteLength;
    }

    // Validate SHA-256 checksum of full archive
    const digest = await crypto.subtle.digest("SHA-256", fullBuffer as unknown as BufferSource);
    const hashHex = Array.from(new Uint8Array(digest))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");

    if (hashHex.toLowerCase() !== expected_checksum_sha256.toLowerCase()) {
      await clearPartialDownload(pack_id, version);
      return {
        success: false,
        error: `Checksum mismatch: expected ${expected_checksum_sha256}, got ${hashHex}`,
      };
    }

    // Decompress archive payload (gzip or plain JSON)
    const decompressedText = await decompressArchive(fullBuffer);

    // Validate pack schema
    let parsed: any;
    try {
      parsed = JSON.parse(decompressedText);
    } catch (e: any) {
      await clearPartialDownload(pack_id, version);
      return {
        success: false,
        error: `Decompressed pack is not valid JSON: ${e.message}`,
      };
    }

    try {
      validatePackPayload(parsed, pack_id);
    } catch (valErr: any) {
      await clearPartialDownload(pack_id, version);
      return {
        success: false,
        error: valErr.message,
      };
    }

    // Atomic install: save pack to shared database
    await saveInstalledPack({
      pack_id,
      version,
      byte_size: downloadedBytes,
      checksum_sha256: hashHex,
      installed_at: Date.now(),
      manifest_json: decompressedText,
    });

    // Cleanup durable temporary partial segments
    await clearPartialDownload(pack_id, version);

    // Record PACK_INSTALLED event if active session exists
    try {
      const session = getActiveProfileSession();
      if (session) {
        const profile = await getActiveSharedProfile();
        if (profile) {
          const eventId = `evt_${crypto.randomUUID().replace(/-/g, "").slice(0, 24)}`;
          await session.recordEvent({
            eventId,
            deviceId: profile.device_id,
            eventType: "PACK_INSTALLED",
            payload: {
              pack_id,
              version,
              byte_size: downloadedBytes,
              checksum_sha256: hashHex,
            },
          });
        }
      }
    } catch {
      // Event recording non-fatal to download success
    }

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
