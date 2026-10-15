// Local persistence — v2 ProfileSession-backed API (Design v2 Section 7/9).
//
// All profile data lives in a per-learner IndexedDB database owned by
// `profile_session.ts`; the shared database holds device meta and packs.
// State mutations and their outbox event are written in ONE transaction
// there. This module keeps the ergonomics the screens already use and
// never relies on React state or localStorage for durable learner data.

import { Action, BackgroundAction, DeliveryMode, EventType,
         NetworkState } from "../generated/api";
import {
  BloomMasteryRow, DeviceMeta, DecisionRow, getActiveProfileSession, InstalledPack,
  MasteryRow, openProfileSession, ProfileSession,
  SharedProfileMeta,
} from "./profile_session";

// --------------------------------------------------------------------------- //
// Shapes used by screens (v2: mastery in integer basis points)
// --------------------------------------------------------------------------- //
export interface LocalProfile {
  learner_id: string;
  device_id: string;
  device_token: string;      // device-scoped access token (shared DB)
  refresh_token?: string;
  token_expires_at: number;
  display_label: string;
  created_at: number;
  active: boolean;
  has_pin?: boolean;
}

export type LocalPack = InstalledPack;

export interface LocalMastery {
  concept_id: string;
  p_bp: number;              // 0..10000 integer (v2)
  band: "weak" | "partial" | "mastered";
  attempts: number;
  correct: number;
  last_event_seq: number;
}

export interface LocalDecision {
  decision_id: string;
  action: Action;
  delivery_mode: DeliveryMode;
  background_actions: BackgroundAction[];
  target_concept_id: string;
  chapter_id: string;
  reason_code: string;
  reason_or: string;
  needs_help: boolean;
  network: NetworkState;
  produced_by: "local_engine" | "server_engine";
  source?: "server" | "local";
  ruleset_version?: string;
  created_at: number;
  trace_json?: string;
}

export interface OutboxEvent {
  event_id: string;
  device_id: string;
  learner_id: string;
  seq: number;
  client_ts: number;
  event_type: EventType | string;
  concept_id?: string | null;
  chapter_id?: string | null;
  question_id?: string | null;
  payload: Record<string, any>;
  outbox_state: "pending" | "inflight" | "acked" | "quarantined";
  retry_count: number;
}

// --------------------------------------------------------------------------- //
// Session helpers — screens open the profile session once at startup
// --------------------------------------------------------------------------- //
export async function ensureSession(profile: LocalProfile): Promise<ProfileSession> {
  return openProfileSession(profile.learner_id);
}

function requireSession(): ProfileSession {
  const s = getActiveProfileSession();
  if (!s) {
    throw new Error("no profile session open — call ensureSession() first");
  }
  return s;
}

// --------------------------------------------------------------------------- //
// Device identity + tokens (shared DB — never per-profile)
// --------------------------------------------------------------------------- //
const DEVICE_META_KEY = "saarthi-device";

export async function getDeviceMeta(): Promise<DeviceMeta | undefined> {
  const session = getActiveProfileSession();
  if (session) return session.getDeviceMeta(DEVICE_META_KEY);
  // No profile open yet — read through a throwaway session on the shared DB
  // is unnecessary: device registration happens after a session opens.
  return undefined;
}

export async function saveDeviceMeta(meta: DeviceMeta): Promise<void> {
  const session = requireSession();
  await session.putDeviceMeta(meta);
}

/** Token storage: device tokens live in the shared DB, scoped per device,
 * never inside a profile database (v2 local store layout). */
export async function saveDeviceToken(profile: LocalProfile): Promise<void> {
  const session = requireSession();
  const existing = await session.getDeviceMeta(DEVICE_META_KEY);
  await session.putDeviceMeta({
    device_id: profile.device_id,
    public_key_spki_b64: existing?.public_key_spki_b64,
    registered_at: existing?.registered_at ?? Date.now(),
  });
  await session.setSessionCache("device_token", {
    device_token: profile.device_token,
    refresh_token: profile.refresh_token,
    token_expires_at: profile.token_expires_at,
  });
}

export async function loadDeviceToken(): Promise<{
  device_token: string; refresh_token?: string; token_expires_at: number;
} | undefined> {
  const session = getActiveProfileSession();
  if (!session) return undefined;
  return session.getSessionCache("device_token");
}

// --------------------------------------------------------------------------- //
// Profile registry (shared DB; metadata only — no progress data)
// --------------------------------------------------------------------------- //
export async function saveProfile(profile: LocalProfile): Promise<void> {
  const session = await openProfileSession(profile.learner_id);
  try {
    await session.putProfileMeta({
      learner_id: profile.learner_id,
      device_id: profile.device_id,
      display_label: profile.display_label,
      created_at: profile.created_at,
      active: profile.active,
      has_pin: !!profile.has_pin,
    });
    if (profile.active) {
      await session.setActiveProfileMeta(profile.learner_id);
    }
    await saveDeviceToken(profile);
  } finally {
    // Keep the newly-opened session as the active one when this profile is
    // becoming active; otherwise close it.
    if (!profile.active) await session.close();
  }
}

export async function getActiveProfile(): Promise<LocalProfile | undefined> {
  const session = getActiveProfileSession();
  let meta: SharedProfileMeta | undefined;
  if (session) {
    meta = await session.getActiveProfileMeta();
  }
  if (!meta) return undefined;
  const token = await session!.getSessionCache("device_token") as
    { device_token: string; refresh_token?: string; token_expires_at: number }
    | undefined;
  if (!token) return undefined;
  return {
    learner_id: meta.learner_id,
    device_id: meta.device_id,
    device_token: token.device_token,
    refresh_token: token.refresh_token,
    token_expires_at: token.token_expires_at,
    display_label: meta.display_label,
    created_at: meta.created_at,
    active: meta.active,
    has_pin: meta.has_pin,
  };
}

export async function setActiveProfile(learner_id: string): Promise<void> {
  const session = await openProfileSession(learner_id);
  await session.setActiveProfileMeta(learner_id);
}

export async function listProfiles(): Promise<SharedProfileMeta[]> {
  const session = getActiveProfileSession();
  if (!session) return [];
  return session.listProfileMeta();
}

// --------------------------------------------------------------------------- //
// Event recording (atomic: state change + outbox event + seq counter)
// --------------------------------------------------------------------------- //
export async function recordAssessmentEvent(
  learner_id: string, device_id: string, event_id: string,
  concept_id: string, question: {
    question_id?: string; chapter_id?: string; revision?: number; bloom_level?: string;
  } | null, correct: boolean, attempt_id: string,
  selected_option?: number, answer_text?: string,
  duration_ms: number = 0,
): Promise<OutboxEvent> {
  const session = requireSession();
  const row = await session.recordGradedAnswer({
    deviceId: device_id,
    eventId: event_id,
    conceptId: concept_id,
    chapterId: question?.chapter_id,
    questionId: question?.question_id,
    bloomLevel: question?.bloom_level,
    correct,
    attemptId: attempt_id,
    revision: question?.revision ?? 1,
    response: selected_option ?? answer_text ?? null,
    durationMs: duration_ms,
  });
  return row as unknown as OutboxEvent;
}

export async function recordDoubtEvent(
  learner_id: string, device_id: string, event_id: string,
  query: string, decision_id: string,
): Promise<OutboxEvent> {
  const session = requireSession();
  const row = await session.recordEvent({
    deviceId: device_id,
    eventId: event_id,
    eventType: EventType.DOUBT_ASKED,
    payload: { query, decision_id, last_action: "DOUBT" },
  });
  return row as unknown as OutboxEvent;
}

export async function recordSimpleEvent(
  device_id: string, event_type: EventType | string,
  payload: Record<string, any>,
  concept_id?: string | null,
): Promise<OutboxEvent> {
  const session = requireSession();
  const event_id = "evt_" + crypto.randomUUID().replace(/-/g, "").slice(0, 24);
  const row = await session.recordEvent({
    deviceId: device_id, eventId: event_id, eventType: event_type,
    payload, conceptId: concept_id ?? null,
  });
  return row as unknown as OutboxEvent;
}

/** Next seq for display purposes; the authoritative increment happens
 * inside the recording transaction. */
export async function nextSeq(): Promise<number> {
  const session = requireSession();
  const pending = await session.listPendingOutbox(100000);
  const maxPending = pending.length ? pending[pending.length - 1].seq : 0;
  const cursor = await session.getSyncCursor();
  return Math.max(maxPending, cursor.last_acked_seq) + 1;
}

// --------------------------------------------------------------------------- //
// Outbox / sync result application
// --------------------------------------------------------------------------- //
export async function listPendingOutbox(limit = 100): Promise<OutboxEvent[]> {
  return requireSession().listPendingOutbox(limit) as unknown as
    Promise<OutboxEvent[]>;
}

export type SyncOutcome =
  | "ACCEPTED" | "DUPLICATE" | "RETRYABLE" | "REJECTED";

export async function applySyncOutcomes(
  results: Array<{
    event_id: string; seq: number; outcome: SyncOutcome; reason?: string | null;
  }>,
  serverMastery?: MasteryRow[],
  serverBloomMastery?: BloomMasteryRow[],
): Promise<{
  removed: number; quarantined: number; retried: number;
}> {
  const session = requireSession();
  // Rebase: re-apply local events created after the upload snapshot, in
  // seq order (v2 Section 9 step 5).
  const maxAcked = Math.max(0, ...results
    .filter((r) => r.outcome === "ACCEPTED" || r.outcome === "DUPLICATE")
    .map((r) => r.seq));
  const localEventsAfter = (await session.listPendingOutbox(100000))
    .filter((e) => e.seq > maxAcked);
  return session.applySyncOutcomes({ results, serverMastery, serverBloomMastery, localEventsAfter });
}

export async function listQuarantined() {
  return requireSession().listQuarantine();
}

// --------------------------------------------------------------------------- //
// Mastery + decisions
// --------------------------------------------------------------------------- //
export async function getMasterySnapshot(): Promise<LocalMastery[]> {
  return requireSession().getMasterySnapshot() as unknown as
    Promise<LocalMastery[]>;
}

export type LocalBloomMastery = BloomMasteryRow;

export async function getBloomMasterySnapshot(): Promise<BloomMasteryRow[]> {
  return requireSession().getBloomMasterySnapshot();
}

export async function recordDecision(d: LocalDecision): Promise<void> {
  const row: DecisionRow = {
    decision_id: d.decision_id,
    action: d.action,
    delivery_mode: d.delivery_mode,
    background_actions: d.background_actions as string[],
    target_concept_id: d.target_concept_id,
    chapter_id: d.chapter_id,
    reason_code: d.reason_code,
    reason_or: d.reason_or,
    needs_help: d.needs_help,
    network: d.network,
    source: d.source ?? (d.produced_by === "local_engine" ? "local" : "server"),
    ruleset_version: d.ruleset_version ?? "",
    created_at: d.created_at,
    trace_json: d.trace_json,
  };
  await requireSession().recordDecision(row);
}

export async function listRecentDecisions(limit: number = 5): Promise<LocalDecision[]> {
  const rows = await requireSession().listRecentDecisions(limit);
  return rows.map((r) => ({
    decision_id: r.decision_id,
    action: r.action as Action,
    delivery_mode: r.delivery_mode as DeliveryMode,
    background_actions: r.background_actions as BackgroundAction[],
    target_concept_id: r.target_concept_id,
    chapter_id: r.chapter_id,
    reason_code: r.reason_code,
    reason_or: r.reason_or,
    needs_help: r.needs_help,
    network: r.network as NetworkState,
    produced_by: r.source === "local" ? "local_engine" : "server_engine",
    source: r.source,
    ruleset_version: r.ruleset_version,
    created_at: r.created_at,
    trace_json: r.trace_json,
  }));
}

// --------------------------------------------------------------------------- //
// Packs (shared DB — content only, nothing personal)
// --------------------------------------------------------------------------- //
export async function saveInstalledPack(pack: LocalPack): Promise<void> {
  await requireSession().putInstalledPack(pack);
}

export async function getInstalledPacks(): Promise<LocalPack[]> {
  const session = getActiveProfileSession();
  if (!session) return [];
  return session.listInstalledPacks();
}

export async function getFirstInstalledPack(): Promise<LocalPack | undefined> {
  const packs = await getInstalledPacks();
  return packs[0];
}
