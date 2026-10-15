// Centralised API client — typed contracts, timeouts, typed errors.
// All components use this; no scattered `fetch` in components.
//
// v2 changes:
// - The API base URL comes from build-time env (VITE_API_URL); the
//   localhost fallback exists ONLY in dev builds — production assets never
//   bake in a localhost URL (repair brief 7.4).
// - Device-bound auth: short-lived access token + rotating refresh token;
//   401 triggers exactly one renewal+retry, then the caller sees the error
//   and sync pauses in AUTH_PENDING (learning never blocks).
// - Learner-specific responses are never cached by the service worker and
//   never persisted outside the profile store.

import {
  AuthChallenge, AuthRenewRequest, AuthResponse, DeviceRegistration,
  DeviceTokenResponse, DoubtRequest, DoubtResponse, HealthResponse,
  LearnerEvent, LearnerProfile, LearnerProfileCreate, LearnerState,
  PackDownloadInfo, PackManifest, Problem, RefreshRequest,
  AssessmentSubmission, AssessmentResult, Decision, DecisionTrace,
  SyncRequest, SyncResponse,
} from "../generated/api";
import type {
  GameState, RelayState, RoomDetail, RoomMessage,
} from "../screens/rooms/types";
import { Outcome } from "../generated/api";

const DEFAULT_TIMEOUT_MS = 10_000;

export function apiBaseUrl(): string {
  return _apiUrl();
}

function _apiUrl(): string {
  const fromEnv = import.meta.env.VITE_API_URL as string | undefined;
  if (fromEnv) return fromEnv.replace(/\/$/, "");
  // Dev-only fallback: never baked into production assets.
  if (import.meta.env.DEV) return "http://127.0.0.1:8000";
  throw new Error(
    "VITE_API_URL is not configured for this production build");
}

export class SaarthiApiError extends Error {
  constructor(public problem: Problem | null, message: string,
              public status: number = 0) {
    super(message);
  }
  get error_code(): string | undefined { return this.problem?.error_code; }
  get request_id(): string | undefined { return this.problem?.request_id; }
}

// --------------------------------------------------------------------------- //
// In-memory token holder (refreshed from the profile store by the app shell)
// --------------------------------------------------------------------------- //
let accessToken: string | null = null;
let refreshToken: string | null = null;
let deviceId: string | null = null;

export const auth = {
  setTokens(access: string | null, refresh: string | null, devId: string | null) {
    accessToken = access;
    refreshToken = refresh;
    deviceId = devId;
  },
  get accessToken() { return accessToken; },
  get refreshToken() { return refreshToken; },
  get deviceId() { return deviceId; },
  clear() {
    accessToken = null;
    refreshToken = null;
    deviceId = null;
  },
};

/** Back-compat for older call sites. */
export const api_auth = auth;

let renewalInflight: Promise<boolean> | null = null;

/** Renew the access token using the rotating refresh token; on failure
 * fall back to the signed-nonce challenge path when a device key exists. */
export async function renewAuthIfNeeded(): Promise<boolean> {
  if (!refreshToken || !deviceId) return false;
  if (renewalInflight) return renewalInflight;
  renewalInflight = (async () => {
    try {
      const body: RefreshRequest = { device_id: deviceId!, refresh_token: refreshToken! };
      const tokens = await request<DeviceTokenResponse>("/api/v1/auth/refresh", {
        method: "POST", body: JSON.stringify(body), skipAuth: true,
      });
      auth.setTokens(tokens.access_token, tokens.refresh_token, tokens.device_id);
      return true;
    } catch {
      return false;
    } finally {
      renewalInflight = null;
    }
  })();
  return renewalInflight;
}

async function request<T>(
  path: string, opts: RequestInit & { skipAuth?: boolean } = {},
  timeoutMs: number = DEFAULT_TIMEOUT_MS,
): Promise<T> {
  const url = `${_apiUrl()}${path}`;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((opts.headers as Record<string, string>) || {}),
  };
  if (!opts.skipAuth && accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }
  if (deviceId) headers["X-Device-Id"] = deviceId;
  try {
    const resp = await fetch(url, { ...opts, headers, signal: ctrl.signal });
    if (!resp.ok) {
      let problem: Problem | null = null;
      try { problem = await resp.json(); } catch { /* not problem+json */ }
      throw new SaarthiApiError(problem, `HTTP ${resp.status}`, resp.status);
    }
    return await resp.json() as T;
  } catch (e: any) {
    if (e.name === "AbortError") {
      throw new SaarthiApiError(null, "Request timed out", 0);
    }
    throw e;
  } finally {
    clearTimeout(timer);
  }
}

/** Request with one automatic 401 → renew → retry cycle. */
async function requestWithRenewal<T>(
  path: string, opts: RequestInit = {}, timeoutMs?: number,
): Promise<T> {
  try {
    return await request<T>(path, opts, timeoutMs);
  } catch (e) {
    if (e instanceof SaarthiApiError && e.status === 401) {
      const renewed = await renewAuthIfNeeded();
      if (renewed) return await request<T>(path, opts, timeoutMs);
    }
    throw e;
  }
}

// --------------------------------------------------------------------------- //
// API surface
// --------------------------------------------------------------------------- //
export const api = {
  apiBaseUrl,

  setAuth: (token: string, deviceIdArg: string, refresh?: string) => {
    auth.setTokens(token, refresh ?? null, deviceIdArg);
  },
  clearAuth: () => auth.clear(),

  health: () => request<HealthResponse>("/api/v1/health"),

  // ---- device + auth (v2) ---------------------------------------------
  registerDevice: (body: DeviceRegistration) =>
    request<DeviceTokenResponse>("/api/v1/devices", {
      method: "POST", body: JSON.stringify(body), skipAuth: true,
    }),
  authChallenge: (device_id: string) =>
    request<AuthChallenge>("/api/v1/auth/challenge", {
      method: "POST",
      body: JSON.stringify({ device_id }),
      skipAuth: true,
    }),
  authRenew: (body: AuthRenewRequest) =>
    request<DeviceTokenResponse>("/api/v1/auth/renew", {
      method: "POST", body: JSON.stringify(body), skipAuth: true,
    }),
  authRefresh: (body: RefreshRequest) =>
    request<DeviceTokenResponse>("/api/v1/auth/refresh", {
      method: "POST", body: JSON.stringify(body), skipAuth: true,
    }),

  // ---- learners ----------------------------------------------------------
  createLearner: (body: LearnerProfileCreate) =>
    requestWithRenewal<AuthResponse>("/api/v1/learners", {
      method: "POST", body: JSON.stringify(body),
    }),
  getCurrentLearner: () =>
    requestWithRenewal<LearnerProfile>("/api/v1/learners/me"),
  listLearners: () =>
    requestWithRenewal<LearnerProfile[]>("/api/v1/learners"),
  activateLearner: (learner_id: string) =>
    requestWithRenewal<AuthResponse>(`/api/v1/learners/${learner_id}/activate`,
                                     { method: "POST" }),
  renewToken: () =>
    requestWithRenewal<AuthResponse>("/api/v1/learners/auth/renew",
                                     { method: "POST" }),

  // ---- content -------------------------------------------------------------
  listChapters: () => requestWithRenewal("/api/v1/content/chapters"),
  getConcept: (cid: string) =>
    requestWithRenewal(`/api/v1/content/concepts/${cid}`),
  listChunksForConcept: (cid: string) =>
    requestWithRenewal(`/api/v1/content/concepts/${cid}/chunks`),
  getChunk: (cid: string) =>
    requestWithRenewal(`/api/v1/content/chunks/${cid}`),
  getNextQuestion: (cid: string, difficulty?: string) =>
    requestWithRenewal(
      `/api/v1/content/concepts/${cid}/questions/next${difficulty ? `?difficulty=${difficulty}` : ""}`),

  // ---- assessments ------------------------------------------------------------
  submitAssessment: (sub: AssessmentSubmission, seq: number) =>
    requestWithRenewal<AssessmentResult>("/api/v1/assessments", {
      method: "POST",
      body: JSON.stringify(sub),
      headers: { "X-Event-Seq": String(seq) },
    }),

  // ---- decisions ----------------------------------------------------------------
  nextDecision: (network: "online" | "weak" | "offline" | "reconnected" = "online") =>
    requestWithRenewal<Decision>("/api/v1/decisions/next", {
      method: "POST",
      body: JSON.stringify({ network }),
    }),
  getDecision: (id: string) =>
    requestWithRenewal<Decision>(`/api/v1/decisions/${id}`),
  getDecisionTrace: (id: string) =>
    requestWithRenewal<DecisionTrace>(`/api/v1/decisions/${id}/trace`),

  // ---- doubts -----------------------------------------------------------------
  askDoubt: (req: DoubtRequest) =>
    requestWithRenewal<DoubtResponse>("/api/v1/doubts/query", {
      method: "POST",
      body: JSON.stringify(req),
    }),

  // ---- sync --------------------------------------------------------------------
  sync: (req: SyncRequest) =>
    requestWithRenewal<SyncResponse>("/api/v1/sync", {
      method: "POST",
      body: JSON.stringify(req),
    }, 20_000),

  // ---- packs ---------------------------------------------------------------------
  listPackManifests: () =>
    requestWithRenewal<PackManifest[]>("/api/v1/packs/manifest"),
  getPackDownloadInfo: (pack_id: string, version: string) =>
    requestWithRenewal<PackDownloadInfo>(
      `/api/v1/packs/${pack_id}/versions/${version}`),

<<<<<<< HEAD
  getLearnerState: () =>
    requestWithRenewal<LearnerState>("/api/v1/state"),

  // ---- Karana Study Rooms (live network feature; needs connectivity) ---- //
  createRoom: (body: Record<string, unknown>) =>
    request<RoomDetail>("/api/v1/rooms/create", {
      method: "POST", body: JSON.stringify(body),
    }),
  joinRoom: (room_code: string) =>
    request<RoomDetail>("/api/v1/rooms/join", {
      method: "POST", body: JSON.stringify({ room_code }),
    }),
  listRooms: () => request<{ rooms: RoomDetail[] }>("/api/v1/rooms"),
  getRoom: (room_id: string) =>
    request<RoomDetail>(`/api/v1/rooms/${room_id}`),
  leaveRoom: (room_id: string) =>
    request<{ left: boolean }>(`/api/v1/rooms/${room_id}/leave`, { method: "POST" }),
  roomHeartbeat: (room_id: string) =>
    request<{ ok: boolean }>(`/api/v1/rooms/${room_id}/heartbeat`, { method: "POST" }),
  postRoomMessage: (room_id: string, body: string, reply_to?: string) =>
    request<RoomMessage>(`/api/v1/rooms/${room_id}/messages`, {
      method: "POST", body: JSON.stringify({ body, reply_to: reply_to ?? null }),
    }),
  startRelay: (room_id: string, question: string) =>
    request<RelayState>(`/api/v1/rooms/${room_id}/relay/start`, {
      method: "POST", body: JSON.stringify({ question }),
    }),
  getRelay: (room_id: string, activity_id: string) =>
    request<RelayState>(`/api/v1/rooms/${room_id}/relay/${activity_id}`),
  submitRelay: (room_id: string, activity_id: string, content: string) =>
    request<RelayState>(`/api/v1/rooms/${room_id}/relay/${activity_id}/submit`, {
      method: "POST", body: JSON.stringify({ content }),
    }),
  revealRelay: (room_id: string, activity_id: string) =>
    request<RelayState>(`/api/v1/rooms/${room_id}/relay/${activity_id}/reveal`,
      { method: "POST" }),
  advanceRelay: (room_id: string, activity_id: string, stage: string) =>
    request<RelayState>(`/api/v1/rooms/${room_id}/relay/${activity_id}/advance`, {
      method: "POST", body: JSON.stringify({ stage }),
    }),
  verifyRelay: (room_id: string, activity_id: string, selected_option: number) =>
    request<RelayState>(`/api/v1/rooms/${room_id}/relay/${activity_id}/verify`, {
      method: "POST", body: JSON.stringify({ selected_option }),
    }),
  startGame: (room_id: string) =>
    request<GameState>(`/api/v1/rooms/${room_id}/game/start`, { method: "POST" }),
  getGame: (room_id: string, activity_id: string) =>
    request<GameState>(`/api/v1/rooms/${room_id}/game/${activity_id}`),
  submitGame: (room_id: string, activity_id: string,
               mistake_line: string, reasoning: string) =>
    request<GameState>(`/api/v1/rooms/${room_id}/game/${activity_id}/submit`, {
      method: "POST",
      body: JSON.stringify({ mistake_line, reasoning }),
    }),
  revealGame: (room_id: string, activity_id: string) =>
    request<GameState>(`/api/v1/rooms/${room_id}/game/${activity_id}/reveal`,
      { method: "POST" }),
  listRoomActivities: (room_id: string) =>
    request<{ activities: { activity_id: string; activity_type: string;
                            status: string; created_at: number }[] }>(
      `/api/v1/rooms/${room_id}/activities`),
  expireSweep: () =>
    request<{ deleted_room_ids: string[] }>(
      "/api/v1/rooms/admin/expire-sweep", { method: "POST" }),

  renewAuthIfNeeded,
  updateSyncCursor: async () => {
    // The authoritative cursor lives in the profile session store; sync.ts
    // already applies it through applySyncOutcomes. Kept as a no-op hook.
  },
};

export { Outcome } from "../generated/api";
export type { LearnerEvent };
