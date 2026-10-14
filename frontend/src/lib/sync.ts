// Sync engine v2 — outbox protocol per Design v2 Sections 8 + 9.
//
//   1. Trigger: network online/weak, app foreground, or 5-minute timer.
//   2. Send the oldest 100 outbox events in seq order (one profile).
//   3. Apply per-event outcomes: ACCEPTED/DUPLICATE → remove; REJECTED →
//      quarantine then remove (one transaction); RETRYABLE → keep + backoff.
//   4. Replace local mastery with the server's, then re-apply local events
//      created after the snapshot (rebase).
//   5. A server decision is stored as a pending suggestion, never shown
//      mid-activity (non-blocking reconnect).
//
// Failure behaviour: exponential backoff (5s, 15s, 60s, 300s) with ±20%
// jitter; partial failures never delete unacknowledged events; auth expiry
// pauses sync in AUTH_PENDING without blocking local learning.

import { api, SaarthiApiError } from "../api/client";
import {
  applySyncOutcomes, getActiveProfile, getMasterySnapshot,
  listPendingOutbox, LocalProfile, recordDecision, OutboxEvent,
} from "../store/db";
import { RULESET } from "../engine/decide";
import { EventType, LearnerEvent, NetworkState, Outcome,
         PerEventResult } from "../generated/api";

let inflight = false;
let nextRetryAt = 0;
let retryStep = 0;
let authPending = false;

const BACKOFF_S: number[] = RULESET.sync?.backoff_s ?? [5, 15, 60, 300];
const JITTER = RULESET.sync?.backoff_jitter ?? 0.2;
const BATCH_SIZE: number = RULESET.sync?.batch_size ?? 100;

export type SyncPauseReason = "auth_pending" | "offline" | "no_profile";

export function isSyncPaused(): SyncPauseReason | null {
  if (authPending) return "auth_pending";
  return null;
}

function sleep(ms: number) { return new Promise((r) => setTimeout(r, ms)); }

function jitteredDelayMs(step: number): number {
  const base = Math.min(BACKOFF_S[step] ?? BACKOFF_S[BACKOFF_S.length - 1], 300);
  const j = JITTER;
  const delay = base * (1 - j + Math.random() * 2 * j);
  return Math.round(delay * 1000);
}

export interface SyncResult {
  ok: boolean;
  reason?: string;
  accepted?: number;
  quarantined?: number;
  deferred?: boolean;
  paused?: SyncPauseReason;
}

function toWireEvent(e: OutboxEvent): LearnerEvent {
  return {
    event_id: e.event_id,
    device_id: e.device_id,
    learner_id: e.learner_id,
    seq: e.seq,
    type: e.event_type as EventType,
    client_ts: e.client_ts,
    payload: e.payload,
    concept_id: e.concept_id ?? null,
    chapter_id: e.chapter_id ?? null,
    question_id: e.question_id ?? null,
  };
}

/** Mark the batch inflight (visual state only — a crash leaves them
 * pending, and resending is safe by (device_id, seq) idempotency). */
async function markInflight(pending: OutboxEvent[]): Promise<void> {
  // The outbox rows are authoritative in the profile DB; inflight marking
  // is in-memory only so an app kill never loses the "pending" state.
  void pending;
}

export async function trySyncNow(): Promise<SyncResult> {
  if (inflight) return { ok: false, reason: "already_inflight" };
  const now = Date.now();
  if (nextRetryAt > now) {
    return { ok: false, reason: `backoff_until_${nextRetryAt - now}ms` };
  }
  const profile: LocalProfile | undefined = await getActiveProfile();
  if (!profile) return { ok: false, reason: "no_profile", paused: "no_profile" };

  const pending = await listPendingOutbox(BATCH_SIZE);
  if (pending.length === 0) {
    retryStep = 0;
    return { ok: true, accepted: 0 };
  }

  inflight = true;
  try {
    await markInflight(pending);
    const fromSeq = Math.max(0, Math.min(...pending.map((e) => e.seq)) - 1);
    const resp = await api.sync({
      device_id: profile.device_id,
      learner_id: profile.learner_id,
      from_seq: fromSeq,
      events: pending.map(toWireEvent),
    });
    // Exactly one outcome per submitted event; unknown/missing events stay
    // in the outbox and are resent (idempotent by (device_id, seq)).
    const results = (resp.results || resp.accepted || []).map(
      (r: PerEventResult) => ({
        event_id: r.event_id, seq: r.seq, outcome: r.outcome,
        reason: r.reason ?? null,
      }));
    // Server-authoritative mastery + rebase of local events created after
    // the upload snapshot (v2 Section 9 step 5).
    const serverMastery = resp.mastery?.length ? resp.mastery : undefined;
    const serverBloomMastery = resp.bloom_mastery?.length ? resp.bloom_mastery : undefined;
    const applied = await applySyncOutcomes(results, serverMastery, serverBloomMastery as any);
    // Preserve local decisions; store the server decision as a separate
    // record (traceability: source stays distinct, v2 Section 9).
    if (resp.decision) {
      await recordDecision({
        decision_id: resp.decision.decision_id,
        action: resp.decision.action,
        delivery_mode: resp.decision.delivery_mode,
        background_actions: resp.decision.background_actions,
        target_concept_id: resp.decision.target_concept_id,
        chapter_id: resp.decision.chapter_id ?? "",
        reason_code: resp.decision.reason_code,
        reason_or: resp.decision.reason_or ?? "",
        needs_help: !!resp.decision.needs_help,
        network: NetworkState.RECONNECTED,
        produced_by: "server_engine",
        source: "server",
        ruleset_version: resp.decision.ruleset_version,
        created_at: resp.decision.created_at || Date.now(),
        trace_json: "[]",
      });
    }
    await api.updateSyncCursor?.();
    nextRetryAt = 0;
    retryStep = 0;
    authPending = false;
    // Remaining outbox? Callers loop until the outbox drains.
    const remaining = await listPendingOutbox(1);
    return {
      ok: true,
      accepted: results.filter((r) => r.outcome === Outcome.ACCEPTED).length,
      quarantined: applied.quarantined,
      deferred: resp.decision_status === "deferred",
      reason: remaining.length ? "more_events_pending" : undefined,
    };
  } catch (e: any) {
    // 401 → renew auth, retry once; otherwise pause in AUTH_PENDING.
    if (e instanceof SaarthiApiError && e.status === 401) {
      const renewed = await api.renewAuthIfNeeded();
      if (renewed) {
        // Retry once immediately after renewal.
        inflight = false;
        return trySyncNow();
      }
      authPending = true; // learning continues; sync paused
      return { ok: false, reason: "auth_expired", paused: "auth_pending" };
    }
    if (e instanceof SaarthiApiError && e.status === 403) {
      // DEVICE_REVOKED (or forbidden): quarantine pending events; keep
      // learning locally (v2 Section 8 step 5).
      const outcomes = pending.map((ev) => ({
        event_id: ev.event_id, seq: ev.seq, outcome: Outcome.REJECTED,
        reason: "DEVICE_REVOKED",
      }));
      const applied = await applySyncOutcomes(outcomes);
      authPending = true;
      return { ok: false, reason: "device_revoked",
               quarantined: applied.quarantined, paused: "auth_pending" };
    }
    // Transient failure: bounded exponential backoff with jitter. No event
    // is removed — a partial failure never deletes unacknowledged events.
    const delay = jitteredDelayMs(retryStep);
    retryStep = Math.min(retryStep + 1, BACKOFF_S.length - 1);
    nextRetryAt = Date.now() + delay;
    return { ok: false, reason: `error: ${e?.message || e}` };
  } finally {
    inflight = false;
  }
}

let loopRunning = false;
export function startSyncLoop() {
  if (loopRunning) return;
  loopRunning = true;
  setInterval(async () => {
    // Only sync when online or reconnected; AUTH_PENDING pauses silently.
    if (authPending) return;
    const state = (await import("../lib/network")).networkMonitor.getState();
    if (state === NetworkState.OFFLINE) return;
    await trySyncNow();
  }, 10_000);
}

export function resetSyncBackoffForTests() {
  inflight = false;
  nextRetryAt = 0;
  retryStep = 0;
  authPending = false;
}

export async function packInstallAvailable(pack_id: string, version: string,
                                           byte_size: number,
                                           checksum_sha256: string): Promise<boolean> {
  const base = await api.apiBaseUrl();
  const url = `${base}/api/v1/packs/${pack_id}/versions/${version}/download`;
  try {
    const resp = await fetch(url);
    if (!resp.ok) return false;
    const blob = await resp.blob();
    const buf = await blob.arrayBuffer();
    const digest = await crypto.subtle.digest("SHA-256", buf);
    const hashHex = Array.from(new Uint8Array(digest))
      .map((b) => b.toString(16).padStart(2, "0")).join("");
    if (hashHex !== checksum_sha256) return false;
    const text = await blob.text();
    const { saveInstalledPack } = await import("../store/db");
    await saveInstalledPack({
      pack_id, version, byte_size, checksum_sha256,
      installed_at: Date.now(),
      manifest_json: text,
    });
    return true;
  } catch {
    return false;
  }
}

export async function getInstalledPack(): Promise<{
  pack_id: string; version: string; manifest_json: string;
} | undefined> {
  const { getInstalledPacks } = await import("../store/db");
  const packs = await getInstalledPacks();
  return packs[0];
}

// Guard against unused-import lint.
void sleep;
void getMasterySnapshot;
