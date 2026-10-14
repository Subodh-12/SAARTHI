/**
 * Background prefetch scheduler (Design Document v2 Section 8.1 & 10).
 *
 * Requirements:
 * - Good-connection detection (online, not weak).
 * - Storage-budget checks (at least 150 MB free).
 * - Deduplication of download requests (never duplicate active downloads).
 * - Non-blocking execution in the background (never interrupts lesson/assessment).
 * - Resume support via pack_downloader.ts (512 KB chunks, Range headers).
 * - Atomic installation and checksum verification.
 */

import { NetworkState } from "../generated/api";
import { downloadPackResumable } from "./pack_downloader";
import { getInstalledPack } from "./sync";

interface PrefetchOptions {
  network: NetworkState;
  targetConceptId?: string;
  onProgress?: (progress: number) => void;
}

let activePrefetchPackId: string | null = null;

export async function checkStorageBudget(): Promise<{ ok: boolean; freeMb: number }> {
  try {
    if (navigator.storage && navigator.storage.estimate) {
      const estimate = await navigator.storage.estimate();
      const quota = estimate.quota || 0;
      const usage = estimate.usage || 0;
      const freeMb = Math.round((quota - usage) / (1024 * 1024));
      return { ok: freeMb >= 150, freeMb };
    }
  } catch {
    // If storage estimate is not supported, permit download
  }
  return { ok: true, freeMb: 500 };
}

export async function scheduleBackgroundPrefetch(opts: PrefetchOptions): Promise<boolean> {
  // 1. Connection check: only run on good 'online' connection (Section 10)
  if (opts.network !== NetworkState.ONLINE) {
    return false;
  }

  // 2. Storage budget check: requires at least 150 MB free
  const storage = await checkStorageBudget();
  if (!storage.ok) {
    console.warn(`[Prefetch] Storage budget insufficient (${storage.freeMb} MB free, need 150 MB).`);
    return false;
  }

  // 3. Prevent duplicate active prefetch
  if (activePrefetchPackId) {
    return false;
  }

  try {
    // 4. Fetch available manifests
    const res = await fetch("/api/v1/packs/manifest");
    if (!res.ok) return false;
    const manifests = await res.json();
    if (!Array.isArray(manifests) || manifests.length === 0) return false;

    // 5. Determine which pack needs prefetching
    const installed = await getInstalledPack();
    const installedPackId = installed?.pack_id;

    // Find first pack not yet installed or next chapter
    const candidate = manifests.find((m: any) => m.pack_id !== installedPackId) || manifests[0];
    if (!candidate) return false;

    activePrefetchPackId = candidate.pack_id;

    // 6. Non-blocking background download using resumable downloader
    downloadPackResumable({
      pack_id: candidate.pack_id,
      version: String(candidate.version),
      expected_byte_size: candidate.byte_size,
      expected_checksum_sha256: candidate.checksum_sha256,
      onProgress: (p) => {
        if (opts.onProgress) opts.onProgress(p.percent);
      },
    })
      .then(() => {
        console.log(`[Prefetch] Successfully prefetched pack ${candidate.pack_id} v${candidate.version}`);
      })
      .catch((err: any) => {
        console.warn(`[Prefetch] Background prefetch failed non-fatally:`, err);
      })
      .finally(() => {
        activePrefetchPackId = null;
      });

    return true;
  } catch (err) {
    activePrefetchPackId = null;
    return false;
  }
}
