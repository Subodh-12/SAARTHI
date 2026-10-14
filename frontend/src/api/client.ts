// Centralised API client — typed contracts, timeouts, typed errors.
// All components use this; no scattered `fetch` in components.

import {
  AuthResponse, DoubtRequest, DoubtResponse, HealthResponse,
  LearnerProfile, LearnerProfileCreate, PackManifest, PackDownloadInfo,
  Decision, DecisionTrace, AssessmentSubmission, AssessmentResult,
  SyncRequest, SyncResponse, LearnerState, Problem,
} from "../generated/api";
import type {
  GameState, RelayState, RoomDetail, RoomMessage,
} from "../screens/rooms/types";
import { Outcome } from "../generated/api";

const DEFAULT_TIMEOUT_MS = 10_000;

export class SaarthiApiError extends Error {
  constructor(public problem: Problem | null, message: string) {
    super(message);
  }
  get error_code(): string | undefined { return this.problem?.error_code; }
  get request_id(): string | undefined { return this.problem?.request_id; }
}

function getToken(): string | null {
  const raw = localStorage.getItem("saarthi.device_token");
  return raw;
}
function setToken(t: string | null) {
  if (t) localStorage.setItem("saarthi.device_token", t);
  else localStorage.removeItem("saarthi.device_token");
}
function getDeviceId(): string | null {
  return localStorage.getItem("saarthi.device_id");
}
function setDeviceId(d: string | null) {
  if (d) localStorage.setItem("saarthi.device_id", d);
  else localStorage.removeItem("saarthi.device_id");
}

async function request<T>(
  path: string, opts: RequestInit = {}, timeoutMs: number = DEFAULT_TIMEOUT_MS,
): Promise<T> {
  const url = `${import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"}${path}`;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(opts.headers as Record<string, string> | undefined),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const deviceId = getDeviceId();
  if (deviceId) headers["X-Device-Id"] = deviceId;
  try {
    const resp = await fetch(url, { ...opts, headers, signal: ctrl.signal });
    if (!resp.ok) {
      let problem: Problem | null = null;
      try { problem = await resp.json(); } catch { /* ignore */ }
      throw new SaarthiApiError(problem, `HTTP ${resp.status}`);
    }
    return await resp.json() as T;
  } catch (e: any) {
    if (e.name === "AbortError") {
      throw new SaarthiApiError(null, "Request timed out");
    }
    throw e;
  } finally {
    clearTimeout(timer);
  }
}

// --------------------------------------------------------------------------- //
// API surface
// --------------------------------------------------------------------------- //
export const api = {
  setAuth: (token: string, deviceId: string) => { setToken(token); setDeviceId(deviceId); },
  clearAuth: () => { setToken(null); setDeviceId(null); },

  health: () => request<HealthResponse>("/api/v1/health"),

  createLearner: (body: LearnerProfileCreate) =>
    request<AuthResponse>("/api/v1/learners", {
      method: "POST", body: JSON.stringify(body),
    }),
  getCurrentLearner: () =>
    request<LearnerProfile>("/api/v1/learners/me"),
  activateLearner: (learner_id: string) =>
    request<AuthResponse>(`/api/v1/learners/${learner_id}/activate`, { method: "POST" }),
  renewToken: () =>
    request<AuthResponse>("/api/v1/learners/auth/renew", { method: "POST" }),

  listChapters: () => request("/api/v1/content/chapters"),
  getConcept: (cid: string) => request(`/api/v1/content/concepts/${cid}`),
  listChunksForConcept: (cid: string) =>
    request(`/api/v1/content/concepts/${cid}/chunks`),
  getChunk: (cid: string) => request(`/api/v1/content/chunks/${cid}`),
  getNextQuestion: (cid: string, difficulty?: string) =>
    request(`/api/v1/content/concepts/${cid}/questions/next${difficulty ? `?difficulty=${difficulty}` : ""}`),

  submitAssessment: (sub: AssessmentSubmission, seq: number) =>
    request<AssessmentResult>("/api/v1/assessments", {
      method: "POST",
      body: JSON.stringify(sub),
      headers: { "X-Event-Seq": String(seq) },
    }),

  nextDecision: (network: "online" | "weak" | "offline" | "reconnected" = "online") =>
    request<Decision>("/api/v1/decisions/next", {
      method: "POST",
      body: JSON.stringify({ network }),
    }),
  getDecision: (id: string) => request<Decision>(`/api/v1/decisions/${id}`),
  getDecisionTrace: (id: string) =>
    request<DecisionTrace>(`/api/v1/decisions/${id}/trace`),

  askDoubt: (req: DoubtRequest) =>
    request<DoubtResponse>("/api/v1/doubts/query", {
      method: "POST",
      body: JSON.stringify(req),
    }),

  sync: (req: SyncRequest) =>
    request<SyncResponse>("/api/v1/sync", {
      method: "POST",
      body: JSON.stringify(req),
      // sync can take longer; allow 20s
    }, 20_000),

  listPackManifests: () => request<PackManifest[]>("/api/v1/packs/manifest"),
  getPackDownloadInfo: (pack_id: string, version: string) =>
    request<PackDownloadInfo>(`/api/v1/packs/${pack_id}/versions/${version}`),

  getLearnerState: () => request<LearnerState>("/api/v1/state"),

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
};

export { Outcome };
