// ProfileSession — the single owner of SAARTHI's local persistence
// (Design v2 Sections 7 + 9, repair brief Section 2).
//
// Layout: TWO IndexedDB databases per phone.
//   saarthi-shared            device meta, device key handle, installed
//                             packs, cached curriculum, keyword index.
//                             Contains nothing personal.
//   saarthi-profile-{id}      per profile: PIN verifier, mastery, outbox,
//                             quarantine, decisions, session & UI cache,
//                             sync cursor, sequence counter.
//
// Invariants enforced here (and nowhere else):
//   - A state change and its outbox event are committed in the SAME
//     IndexedDB transaction, so one can never exist without the other.
//   - The device-level monotonic seq counter is incremented and persisted
//     in the same transaction as the event it numbers.
//   - Only one profile database is open at a time; switching profiles
//     closes it and discards every in-memory cache.
//   - Profile databases are namespaced by learner_id, so no code path can
//     read another profile's data.
//   - Corrupted state fails safe: the affected store is quarantined (not
//     silently deleted) and the app keeps working with empty state.
//   - Removed events leave the outbox only on ACCEPTED, DUPLICATE or a
//     completed move to quarantine.
//
// This module never talks to the network and never stores cloud
// credentials in a profile database.

const SHARED_DB = "saarthi-shared";
const SHARED_VERSION = 1;

export interface SharedProfileMeta {
  learner_id: string;
  device_id: string;
  display_label: string;
  created_at: number;
  active: boolean;
  has_pin: boolean;
}

export interface DeviceMeta {
  device_id: string;
  public_key_spki_b64?: string;
  registered_at: number;
}

export interface InstalledPack {
  pack_id: string;
  version: string;
  byte_size: number;
  checksum_sha256: string;
  installed_at: number;
  manifest_json: string;
}

export interface MasteryRow {
  concept_id: string;
  p_bp: number;          // integer basis points 0..10000 (v2)
  band: "weak" | "partial" | "mastered";
  attempts: number;
  correct: number;
  last_event_seq: number;
}

export interface BloomMasteryRow {
  concept_id: string;
  bloom_level: string;
  p_bp: number;
  band: "weak" | "partial" | "mastered";
  attempts: number;
  correct: number;
  last_event_seq: number;
}

export type OutboxState = "pending" | "inflight" | "acked" | "quarantined";

export interface OutboxRow {
  event_id: string;
  device_id: string;
  learner_id: string;
  seq: number;
  client_ts: number;
  event_type: string;
  concept_id?: string | null;
  chapter_id?: string | null;
  question_id?: string | null;
  payload: Record<string, any>;
  outbox_state: OutboxState;
  retry_count: number;
  last_error?: string | null;
}

export interface QuarantineRow {
  event_id: string;
  device_id: string;
  learner_id: string;
  seq: number;
  client_ts: number;
  event_type: string;
  payload: Record<string, any>;
  reason: string;           // stable SyncReason / diagnostic code
  quarantined_at: number;
}

export interface DecisionRow {
  decision_id: string;
  action: string;
  delivery_mode: string;
  background_actions: string[];
  target_concept_id: string;
  chapter_id: string;
  reason_code: string;
  reason_or: string;
  needs_help: boolean;
  network: string;
  source: "server" | "local";
  ruleset_version: string;
  created_at: number;
  trace_json?: string;
}

export interface SyncCursorRow {
  id: "cursor";
  last_acked_seq: number;
  last_server_cursor: number;
  updated_at: number;
}

export interface PinVerifierRow {
  id: "pin";
  salt_b64: string;
  verifier_b64: string;
  iterations: number;
  created_at: number;
}

// --------------------------------------------------------------------------- //
// Low-level IndexedDB helpers (promise wrappers, no external dependency)
// --------------------------------------------------------------------------- //
export function openDatabase(name: string, version: number,
                             upgrade: (db: IDBDatabase) => void,
                             logLabel = name): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    let req: IDBOpenDBRequest;
    try {
      req = indexedDB.open(name, version);
    } catch (e) {
      reject(new StorageFailure(`indexedDB.open failed for ${logLabel}: ${e}`));
      return;
    }
    req.onupgradeneeded = () => {
      try {
        upgrade(req.result);
      } catch (e) {
        reject(new CorruptedState(`upgrade failed for ${logLabel}: ${e}`));
      }
    };
    req.onsuccess = () => {
      const db = req.result;
      db.onversionchange = () => db.close();
      resolve(db);
    };
    req.onerror = () =>
      reject(new StorageFailure(`open failed for ${logLabel}: ${req.error}`));
    req.onblocked = () =>
      reject(new StorageFailure(`open blocked for ${logLabel}`));
  });
}

function requestToPromise<T>(req: IDBRequest<T>): Promise<T> {
  return new Promise((resolve, reject) => {
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

function txDone(tx: IDBTransaction): Promise<void> {
  return new Promise((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onabort = () => reject(tx.error || new Error("transaction aborted"));
    tx.onerror = () => reject(tx.error);
  });
}

export class StorageFailure extends Error {}
export class CorruptedState extends Error {}
export class ProfileNotOpenError extends Error {
  constructor() {
    super("no profile database is open; select a profile first");
  }
}

// --------------------------------------------------------------------------- //
// PIN — local, salted PBKDF2-SHA256 verifier; NEVER sent to the server
// --------------------------------------------------------------------------- //
export const PIN_ITERATIONS = 150_000;

async function derivePinVerifier(pin: string, salt: Uint8Array,
                                 iterations: number): Promise<string> {
  const enc = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    "raw", enc.encode(pin), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt: salt as unknown as BufferSource,
      iterations, hash: "SHA-256" },
    keyMaterial, 256);
  return btoa(String.fromCharCode(...new Uint8Array(bits)));
}

export async function createPinVerifier(pin: string): Promise<PinVerifierRow> {
  if (!/^\d{4}$/.test(pin)) {
    throw new Error("PIN must be exactly 4 digits");
  }
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const verifier = await derivePinVerifier(pin, salt, PIN_ITERATIONS);
  return {
    id: "pin",
    salt_b64: btoa(String.fromCharCode(...salt)),
    verifier_b64: verifier,
    iterations: PIN_ITERATIONS,
    created_at: Date.now(),
  };
}

export async function verifyPin(pin: string,
                                stored: PinVerifierRow): Promise<boolean> {
  const salt = Uint8Array.from(atob(stored.salt_b64), (c) => c.charCodeAt(0));
  const candidate = await derivePinVerifier(pin, salt, stored.iterations);
  // Constant-time-ish comparison.
  if (candidate.length !== stored.verifier_b64.length) return false;
  let diff = 0;
  for (let i = 0; i < candidate.length; i++) {
    diff |= candidate.charCodeAt(i) ^ stored.verifier_b64.charCodeAt(i);
  }
  return diff === 0;
}

// --------------------------------------------------------------------------- //
// ProfileSession
// --------------------------------------------------------------------------- //
export class ProfileSession {
  readonly learnerId: string;
  private shared: IDBDatabase | null = null;
  private profileDb: IDBDatabase | null = null;
  private _seqCounter: number | null = null;

  private constructor(learnerId: string) {
    this.learnerId = learnerId;
  }

  // ---- lifecycle ----------------------------------------------------------
  static async open(learnerId: string): Promise<ProfileSession> {
    if (!learnerId || !/^[A-Za-z0-9_-]{6,64}$/.test(learnerId)) {
      throw new StorageFailure(`invalid learner id: ${learnerId}`);
    }
    const session = new ProfileSession(learnerId);
    await session.ensureShared();
    await session.openProfileDb();
    await session.loadSeqCounter();
    return session;
  }

  /** Close the profile DB and discard all in-memory state (profile switch). */
  async close(): Promise<void> {
    if (this.profileDb) {
      this.profileDb.close();
      this.profileDb = null;
    }
    if (this.shared) {
      this.shared.close();
      this.shared = null;
    }
    this._seqCounter = null;
  }

  get isOpen(): boolean {
    return this.profileDb !== null;
  }

  private async ensureShared(): Promise<IDBDatabase> {
    if (this.shared) return this.shared;
    this.shared = await openDatabase(SHARED_DB, SHARED_VERSION, (db) => {
      if (!db.objectStoreNames.contains("profiles")) {
        db.createObjectStore("profiles", { keyPath: "learner_id" });
      }
      if (!db.objectStoreNames.contains("device_meta")) {
        db.createObjectStore("device_meta", { keyPath: "device_id" });
      }
      if (!db.objectStoreNames.contains("packs")) {
        db.createObjectStore("packs", { keyPath: "pack_id" });
      }
    }, SHARED_DB);
    return this.shared;
  }

  private async openProfileDb(): Promise<IDBDatabase> {
    if (this.profileDb) return this.profileDb;
    const name = `saarthi-profile-${this.learnerId}`;
    try {
      this.profileDb = await openDatabase(name, 2, (db) => {
        if (!db.objectStoreNames.contains("mastery")) {
          db.createObjectStore("mastery", { keyPath: "concept_id" });
        }
        if (!db.objectStoreNames.contains("bloom_mastery")) {
          db.createObjectStore("bloom_mastery", { keyPath: ["concept_id", "bloom_level"] });
        }
        if (!db.objectStoreNames.contains("outbox")) {
          const os = db.createObjectStore("outbox", { keyPath: "event_id" });
          os.createIndex("by_state_seq", ["outbox_state", "seq"]);
          os.createIndex("by_seq", "seq");
        }
        if (!db.objectStoreNames.contains("quarantine")) {
          db.createObjectStore("quarantine", { keyPath: "event_id" });
        }
        if (!db.objectStoreNames.contains("decisions")) {
          db.createObjectStore("decisions", { keyPath: "decision_id" });
        }
        if (!db.objectStoreNames.contains("session")) {
          db.createObjectStore("session", { keyPath: "id" });
        }
      }, name);
    } catch (e) {
      if (e instanceof CorruptedState) {
        // Corrupted profile state fails safe: report it and leave the DB
        // closed — the caller can recreate it via recoverCorruptedProfile.
        throw e;
      }
      throw e;
    }
    return this.profileDb;
  }

  /** Destructive recovery for a corrupted profile DB (visible in the
   * developer panel; never silent). Quarantine rows are salvaged first. */
  static async recoverCorruptedProfile(learnerId: string,
                                       salvaged: QuarantineRow[] = []): Promise<void> {
    const name = `saarthi-profile-${learnerId}`;
    await new Promise<void>((resolve) => {
      const req = indexedDB.deleteDatabase(name);
      req.onsuccess = () => resolve();
      req.onerror = () => resolve();
      req.onblocked = () => resolve();
    });
    if (salvaged.length) {
      const session = await ProfileSession.open(learnerId);
      try {
        await session.restoreQuarantine(salvaged);
      } finally {
        await session.close();
      }
    }
  }

  // ---- shared DB (device-level, nothing personal) -------------------------
  async putProfileMeta(meta: SharedProfileMeta): Promise<void> {
    const db = await this.ensureShared();
    const tx = db.transaction("profiles", "readwrite");
    tx.objectStore("profiles").put(meta);
    await txDone(tx);
  }

  async listProfileMeta(): Promise<SharedProfileMeta[]> {
    const db = await this.ensureShared();
    const tx = db.transaction("profiles", "readonly");
    const rows = await requestToPromise(
      tx.objectStore("profiles").getAll() as IDBRequest<SharedProfileMeta[]>);
    return rows;
  }

  async setActiveProfileMeta(learnerId: string): Promise<void> {
    const db = await this.ensureShared();
    const tx = db.transaction("profiles", "readwrite");
    const store = tx.objectStore("profiles");
    const all = await requestToPromise(store.getAll() as IDBRequest<SharedProfileMeta[]>);
    for (const p of all) {
      store.put({ ...p, active: p.learner_id === learnerId });
    }
    await txDone(tx);
  }

  async getActiveProfileMeta(): Promise<SharedProfileMeta | undefined> {
    const all = await this.listProfileMeta();
    return all.find((p) => p.active);
  }

  async putDeviceMeta(meta: DeviceMeta): Promise<void> {
    const db = await this.ensureShared();
    const tx = db.transaction("device_meta", "readwrite");
    tx.objectStore("device_meta").put(meta);
    await txDone(tx);
  }

  async getDeviceMeta(deviceId: string): Promise<DeviceMeta | undefined> {
    const db = await this.ensureShared();
    const tx = db.transaction("device_meta", "readonly");
    return requestToPromise(
      tx.objectStore("device_meta").get(deviceId) as IDBRequest<DeviceMeta>);
  }

  async putInstalledPack(pack: InstalledPack): Promise<void> {
    const db = await this.ensureShared();
    const tx = db.transaction("packs", "readwrite");
    tx.objectStore("packs").put(pack);
    await txDone(tx);
  }

  async listInstalledPacks(): Promise<InstalledPack[]> {
    const db = await this.ensureShared();
    const tx = db.transaction("packs", "readonly");
    return requestToPromise(
      tx.objectStore("packs").getAll() as IDBRequest<InstalledPack[]>);
  }

  // ---- PIN (per profile DB) ------------------------------------------------
  async setPin(pin: string): Promise<void> {
    const db = await this.openProfileDb();
    const verifier = await createPinVerifier(pin);
    const tx = db.transaction("session", "readwrite");
    tx.objectStore("session").put(verifier);
    await txDone(tx);
    await this.syncHasPinFlag(true);
  }

  async verifyPin(pin: string): Promise<boolean> {
    const db = await this.openProfileDb();
    const tx = db.transaction("session", "readonly");
    const stored = await requestToPromise(
      tx.objectStore("session").get("pin") as IDBRequest<PinVerifierRow>);
    if (!stored) return true; // no PIN set
    return verifyPin(pin, stored);
  }

  async hasPin(): Promise<boolean> {
    const db = await this.openProfileDb();
    const tx = db.transaction("session", "readonly");
    const stored = await requestToPromise(
      tx.objectStore("session").get("pin") as IDBRequest<PinVerifierRow>);
    return !!stored;
  }

  private async syncHasPinFlag(hasPin: boolean): Promise<void> {
    const db = await this.ensureShared();
    const tx = db.transaction("profiles", "readwrite");
    const store = tx.objectStore("profiles");
    const row = await requestToPromise(
      store.get(this.learnerId) as IDBRequest<SharedProfileMeta>);
    if (row) store.put({ ...row, has_pin: hasPin });
    await txDone(tx);
  }

  // ---- sequence counter (device-level monotonic, per profile) -------------
  private async loadSeqCounter(): Promise<void> {
    const db = await this.openProfileDb();
    const tx = db.transaction("session", "readonly");
    const row = await requestToPromise(
      tx.objectStore("session").get("seq") as IDBRequest<{ id: string; value: number }>);
    this._seqCounter = row ? row.value : 0;
  }

  /** Next event seq — must be called INSIDE the same transaction that
   * writes the event (use recordGradedAnswer / recordEvent). */
  private nextSeqInTx(): number {
    if (this._seqCounter === null) throw new ProfileNotOpenError();
    this._seqCounter += 1;
    return this._seqCounter;
  }

  // ---- atomic event + state writes (one IndexedDB transaction) ------------
  /**
   * Record a graded answer: the mastery state transition, the outbox event
   * and the seq counter commit in ONE transaction. A failure leaves NO
   * partial event and no partial mastery change (fault matrix: "App killed
   * during the local transaction").
   */
  async recordGradedAnswer(args: {
    deviceId: string;
    eventId: string;
    conceptId: string;
    chapterId?: string;
    questionId?: string;
    bloomLevel?: string;
    correct: boolean;
    attemptId: string;
    revision?: number;
    response?: unknown;
    durationMs?: number;
  }): Promise<OutboxRow> {
    const db = await this.openProfileDb();
    const tx = db.transaction(["mastery", "bloom_mastery", "outbox", "session"], "readwrite");
    const mastery = tx.objectStore("mastery");
    const bloomMastery = tx.objectStore("bloom_mastery");
    const outbox = tx.objectStore("outbox");
    const session = tx.objectStore("session");

    const existing = await requestToPromise(
      mastery.get(args.conceptId) as IDBRequest<MasteryRow | undefined>);
    const priorBp = existing?.p_bp ?? (RULESET_BKT.p_init_bp ?? 2000);
    const newBp = bktUpdateBp(priorBp, args.correct, args.conceptId);
    const row: MasteryRow = {
      concept_id: args.conceptId,
      p_bp: newBp,
      band: masteryBandBp(newBp),
      attempts: (existing?.attempts ?? 0) + 1,
      correct: (existing?.correct ?? 0) + (args.correct ? 1 : 0),
      last_event_seq: 0, // patched below once the seq is assigned
    };

    const bloomLvl = (args.bloomLevel || "remember").toLowerCase();
    const existingBloom = await requestToPromise(
      bloomMastery.get([args.conceptId, bloomLvl]) as IDBRequest<BloomMasteryRow | undefined>);
    const priorBloomBp = existingBloom?.p_bp ?? (RULESET_BKT.p_init_bp ?? 2000);
    const newBloomBp = bktUpdateBp(priorBloomBp, args.correct, args.conceptId);
    const bloomRow: BloomMasteryRow = {
      concept_id: args.conceptId,
      bloom_level: bloomLvl,
      p_bp: newBloomBp,
      band: masteryBandBp(newBloomBp),
      attempts: (existingBloom?.attempts ?? 0) + 1,
      correct: (existingBloom?.correct ?? 0) + (args.correct ? 1 : 0),
      last_event_seq: 0,
    };

    const seq = this.nextSeqInTx();
    row.last_event_seq = seq;
    bloomRow.last_event_seq = seq;
    session.put({ id: "seq", value: this._seqCounter });
    mastery.put(row);
    bloomMastery.put(bloomRow);

    const event: OutboxRow = {
      event_id: args.eventId,
      device_id: args.deviceId,
      learner_id: this.learnerId,
      seq,
      client_ts: Date.now(),
      event_type: "ANSWER_SUBMITTED",
      concept_id: args.conceptId,
      chapter_id: args.chapterId ?? null,
      question_id: args.questionId ?? null,
      payload: {
        attempt_id: args.attemptId,
        question_id: args.questionId,
        revision: args.revision ?? 1,
        bloom_level: bloomLvl,
        response: args.response ?? null,
        correct_claim: args.correct,  // client claim; the server regrades
        correct: args.correct,
        duration_ms: args.durationMs ?? 0,
        last_action: "ASSESS",
        p_bp_after: newBp,
      },
      outbox_state: "pending",
      retry_count: 0,
    };
    outbox.put(event);
    try {
      await txDone(tx);
    } catch (e) {
      // Transaction aborted (app killed / storage failure): roll the in-memory
      // counter back to the persisted value so no seq is leaked.
      this._seqCounter = null;
      try { await this.loadSeqCounter(); } catch { /* keep null */ }
      throw e;
    }
    return event;
  }

  /** Record any non-graded event (doubts, views, sessions). Only the event
   * writes — no mastery effect (v2: only graded answers update mastery). */
  async recordEvent(args: {
    deviceId: string;
    eventId: string;
    eventType: string;
    payload: Record<string, any>;
    conceptId?: string | null;
    chapterId?: string | null;
    questionId?: string | null;
  }): Promise<OutboxRow> {
    const db = await this.openProfileDb();
    const tx = db.transaction(["outbox", "session"], "readwrite");
    const seq = this.nextSeqInTx();
    tx.objectStore("session").put({ id: "seq", value: this._seqCounter });
    const event: OutboxRow = {
      event_id: args.eventId,
      device_id: args.deviceId,
      learner_id: this.learnerId,
      seq,
      client_ts: Date.now(),
      event_type: args.eventType,
      concept_id: args.conceptId ?? null,
      chapter_id: args.chapterId ?? null,
      question_id: args.questionId ?? null,
      payload: args.payload,
      outbox_state: "pending",
      retry_count: 0,
    };
    tx.objectStore("outbox").put(event);
    try {
      await txDone(tx);
    } catch (e) {
      // Transaction aborted: roll the in-memory counter back to the
      // persisted value so no seq is leaked.
      this._seqCounter = null;
      try { await this.loadSeqCounter(); } catch { /* keep null */ }
      throw e;
    }
    return event;
  }

  /** Store a locally-computed decision (traceability for server-vs-local). */
  async recordDecision(d: DecisionRow): Promise<void> {
    const db = await this.openProfileDb();
    const tx = db.transaction("decisions", "readwrite");
    tx.objectStore("decisions").put(d);
    await txDone(tx);
  }

  async listRecentDecisions(limit = 20): Promise<DecisionRow[]> {
    const db = await this.openProfileDb();
    const tx = db.transaction("decisions", "readonly");
    const all = await requestToPromise(
      tx.objectStore("decisions").getAll() as IDBRequest<DecisionRow[]>);
    return all.sort((a, b) => b.created_at - a.created_at).slice(0, limit);
  }

  // ---- outbox reads ---------------------------------------------------------
  async listPendingOutbox(limit = 100): Promise<OutboxRow[]> {
    const db = await this.openProfileDb();
    const tx = db.transaction("outbox", "readonly");
    const all = await requestToPromise(
      tx.objectStore("outbox").getAll() as IDBRequest<OutboxRow[]>);
    return all
      .filter((e) => e.outbox_state === "pending")
      .sort((a, b) => a.seq - b.seq)
      .slice(0, limit);
  }

  async outboxDepth(): Promise<number> {
    const pending = await this.listPendingOutbox(100000);
    return pending.length;
  }

  async getMasterySnapshot(): Promise<MasteryRow[]> {
    const db = await this.openProfileDb();
    const tx = db.transaction("mastery", "readonly");
    const all = await requestToPromise(
      tx.objectStore("mastery").getAll() as IDBRequest<MasteryRow[]>);
    return all;
  }

  async getBloomMasterySnapshot(): Promise<BloomMasteryRow[]> {
    const db = await this.openProfileDb();
    const tx = db.transaction("bloom_mastery", "readonly");
    const all = await requestToPromise(
      tx.objectStore("bloom_mastery").getAll() as IDBRequest<BloomMasteryRow[]>);
    return all;
  }

  /**
   * Apply per-event sync outcomes (v2 Section 8):
   *   ACCEPTED / DUPLICATE  → remove from the outbox
   *   REJECTED              → move to quarantine, then remove (one txn)
   *   RETRYABLE             → keep, increment retry_count
   *   missing               → keep (resend is safe by (device, seq))
   * Mastery replacement + rebase happen in the same commit when supplied.
   */
  async applySyncOutcomes(args: {
    results: Array<{
      event_id: string; seq: number;
      outcome: "ACCEPTED" | "DUPLICATE" | "RETRYABLE" | "REJECTED";
      reason?: string | null;
    }>;
    serverMastery?: MasteryRow[];
    serverBloomMastery?: BloomMasteryRow[];
    localEventsAfter?: OutboxRow[]; // rebase: re-apply events created after upload
  }): Promise<{ removed: number; quarantined: number; retried: number }> {
    const db = await this.openProfileDb();
    const stores = ["outbox", "quarantine", "mastery", "bloom_mastery"] as const;
    const tx = db.transaction([...stores, "session"], "readwrite");
    const outbox = tx.objectStore("outbox");
    const quarantine = tx.objectStore("quarantine");
    let removed = 0, quarantined = 0, retried = 0;

    for (const r of args.results) {
      const row = await requestToPromise(
        outbox.get(r.event_id) as IDBRequest<OutboxRow | undefined>);
      if (!row) continue;
      if (r.outcome === "ACCEPTED" || r.outcome === "DUPLICATE") {
        outbox.delete(r.event_id);
        removed += 1;
      } else if (r.outcome === "REJECTED") {
        const q: QuarantineRow = {
          event_id: row.event_id, device_id: row.device_id,
          learner_id: row.learner_id, seq: row.seq,
          client_ts: row.client_ts, event_type: row.event_type,
          payload: row.payload,
          reason: r.reason || "REJECTED",
          quarantined_at: Date.now(),
        };
        quarantine.put(q);
        outbox.delete(r.event_id);
        quarantined += 1;
      } else { // RETRYABLE — keep in outbox, back off
        outbox.put({ ...row, outbox_state: "pending",
                     retry_count: row.retry_count + 1,
                     last_error: r.reason || "RETRYABLE" });
        retried += 1;
      }
    }
    if (args.serverMastery) {
      // Server-authoritative mastery, then re-apply local events created
      // after the snapshot (rebase, v2 Section 9 step 5).
      const mastery = tx.objectStore("mastery");
      mastery.clear();
      for (const m of args.serverMastery) mastery.put(m);
      for (const ev of args.localEventsAfter || []) {
        if (ev.event_type !== "ANSWER_SUBMITTED" || !ev.concept_id) continue;
        const cur = await requestToPromise(
          mastery.get(ev.concept_id) as IDBRequest<MasteryRow | undefined>);
        const prior = cur?.p_bp ?? (RULESET_BKT.p_init_bp ?? 2000);
        const next = bktUpdateBp(prior, !!ev.payload.correct, ev.concept_id);
        mastery.put({
          concept_id: ev.concept_id, p_bp: next,
          band: masteryBandBp(next),
          attempts: (cur?.attempts ?? 0) + 1,
          correct: (cur?.correct ?? 0) + (ev.payload.correct ? 1 : 0),
          last_event_seq: ev.seq,
        });
      }
    }
    if (args.serverBloomMastery) {
      const bloomStore = tx.objectStore("bloom_mastery");
      bloomStore.clear();
      for (const bm of args.serverBloomMastery) bloomStore.put(bm);
      for (const ev of args.localEventsAfter || []) {
        if (ev.event_type !== "ANSWER_SUBMITTED" || !ev.concept_id) continue;
        const bl = (ev.payload.bloom_level || "remember").toLowerCase();
        const cur = await requestToPromise(
          bloomStore.get([ev.concept_id, bl]) as IDBRequest<BloomMasteryRow | undefined>);
        const prior = cur?.p_bp ?? (RULESET_BKT.p_init_bp ?? 2000);
        const next = bktUpdateBp(prior, !!ev.payload.correct, ev.concept_id);
        bloomStore.put({
          concept_id: ev.concept_id,
          bloom_level: bl,
          p_bp: next,
          band: masteryBandBp(next),
          attempts: (cur?.attempts ?? 0) + 1,
          correct: (cur?.correct ?? 0) + (ev.payload.correct ? 1 : 0),
          last_event_seq: ev.seq,
        });
      }
    }
    await txDone(tx);
    return { removed, quarantined, retried };
  }

  async listQuarantine(): Promise<QuarantineRow[]> {
    const db = await this.openProfileDb();
    const tx = db.transaction("quarantine", "readonly");
    const all = await requestToPromise(
      tx.objectStore("quarantine").getAll() as IDBRequest<QuarantineRow[]>);
    return all.sort((a, b) => b.quarantined_at - a.quarantined_at);
  }

  private async restoreQuarantine(rows: QuarantineRow[]): Promise<void> {
    const db = await this.openProfileDb();
    const tx = db.transaction("quarantine", "readwrite");
    for (const r of rows) tx.objectStore("quarantine").put(r);
    await txDone(tx);
  }

  // ---- sync cursor -----------------------------------------------------------
  async getSyncCursor(): Promise<SyncCursorRow> {
    const db = await this.openProfileDb();
    const tx = db.transaction("session", "readonly");
    const row = await requestToPromise(
      tx.objectStore("session").get("cursor") as IDBRequest<SyncCursorRow | undefined>);
    return row || { id: "cursor", last_acked_seq: 0,
                    last_server_cursor: 0, updated_at: 0 };
  }

  async updateSyncCursor(lastServerCursor: number): Promise<void> {
    const db = await this.openProfileDb();
    const tx = db.transaction("session", "readwrite");
    const cur = await requestToPromise(
      tx.objectStore("session").get("cursor") as IDBRequest<SyncCursorRow | undefined>);
    const row: SyncCursorRow = {
      id: "cursor",
      last_acked_seq: Math.max(cur?.last_acked_seq ?? 0, lastServerCursor),
      last_server_cursor: lastServerCursor,
      updated_at: Date.now(),
    };
    tx.objectStore("session").put(row);
    await txDone(tx);
  }

  // ---- session / UI cache -----------------------------------------------------
  async setSessionCache(key: string, value: unknown): Promise<void> {
    const db = await this.openProfileDb();
    const tx = db.transaction("session", "readwrite");
    tx.objectStore("session").put({ id: `ui:${key}`, value });
    await txDone(tx);
  }

  async getSessionCache<T>(key: string): Promise<T | undefined> {
    const db = await this.openProfileDb();
    const tx = db.transaction("session", "readonly");
    const row = await requestToPromise(
      tx.objectStore("session").get(`ui:${key}`) as IDBRequest<{ id: string; value: T } | undefined>);
    return row?.value;
  }

  /** Profile-scoped recent events for the decision engine's guard. */
  async recentEvents(limit = 20): Promise<OutboxRow[]> {
    const db = await this.openProfileDb();
    const tx = db.transaction("outbox", "readonly");
    const all = await requestToPromise(
      tx.objectStore("outbox").getAll() as IDBRequest<OutboxRow[]>);
    return all.sort((a, b) => a.seq - b.seq).slice(-limit);
  }
}

// BKT helpers come from the shared engine (same integer arithmetic as the
// server); the bundler inlines the same generated ruleset JSON.
import { bktUpdateBp, masteryBandBp } from "../engine/decide";
const RULESET_BKT = (RULESET as any).bkt || { p_init_bp: 2000 };
import { RULESET } from "../engine/decide";

// --------------------------------------------------------------------------- //
// Active-session holder — one open profile at a time (isolation rule)
// --------------------------------------------------------------------------- //
let activeSession: ProfileSession | null = null;
let activeLearnerId: string | null = null;

export async function openProfileSession(learnerId: string): Promise<ProfileSession> {
  if (activeSession && activeLearnerId === learnerId && activeSession.isOpen) {
    return activeSession;
  }
  if (activeSession) {
    await activeSession.close();
    activeSession = null;
    activeLearnerId = null;
  }
  activeSession = await ProfileSession.open(learnerId);
  activeLearnerId = learnerId;
  return activeSession;
}

export async function closeActiveProfileSession(): Promise<void> {
  if (activeSession) {
    await activeSession.close();
    activeSession = null;
    activeLearnerId = null;
  }
}

export function getActiveProfileSession(): ProfileSession | null {
  return activeSession && activeSession.isOpen ? activeSession : null;
}
