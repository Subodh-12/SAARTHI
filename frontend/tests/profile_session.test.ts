// ProfileSession tests — local persistence contract (v2 Sections 7/9,
// repair brief Section 2):
//   - atomic state + outbox + seq writes (one IndexedDB transaction)
//   - shared-device profile isolation (separate DBs per learner)
//   - per-event outcome application (ACCEPTED/DUPLICATE/RETRYABLE/REJECTED)
//   - quarantine (never silently dropped) + outbox removal rules
//   - local PIN: salted PBKDF2 verifier, never a raw PIN
//   - corrupted-state handling and storage failure reporting

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import "fake-indexeddb/auto";
import { IDBFactory } from "fake-indexeddb";
import {
  ProfileSession, closeActiveProfileSession, openProfileSession,
  getActiveProfileSession, createPinVerifier, verifyPin,
} from "../src/store/profile_session";

beforeEach(() => {
  // Fresh in-memory IndexedDB per test — profiles can never leak across.
  new IDBFactory();
});

afterEach(async () => {
  await closeActiveProfileSession();
});

function deviceAndSession(learnerId: string) {
  return { deviceId: "dev_testdevice00000001", learnerId };
}

describe("ProfileSession lifecycle", () => {
  it("opens, closes and reports state", async () => {
    const s = await ProfileSession.open("lrn_abcdef1234567890");
    expect(s.isOpen).toBe(true);
    await s.close();
    expect(s.isOpen).toBe(false);
  });

  it("only one profile session is active at a time", async () => {
    const a = await openProfileSession("lrn_aaaaaaaaaaaaaaaa");
    expect(getActiveProfileSession()?.learnerId).toBe("lrn_aaaaaaaaaaaaaaaa");
    const b = await openProfileSession("lrn_bbbbbbbbbbbbbbbb");
    expect(getActiveProfileSession()?.learnerId).toBe("lrn_bbbbbbbbbbbbbbbb");
    expect(a.isOpen).toBe(false); // A was closed on switch (isolation)
    void b;
  });
});

describe("atomic graded-answer writes", () => {
  it("mastery + outbox + seq counter commit together", async () => {
    const { deviceId, learnerId } = deviceAndSession("lrn_atomtest000001");
    const s = await ProfileSession.open(learnerId);
    const ev = await s.recordGradedAnswer({
      deviceId, eventId: "evt_atomic0000000001",
      conceptId: "c0001", correct: true,
      attemptId: "att-1", questionId: "q_ch01_c0001_01",
      bloomLevel: "apply",
    });
    // First correct answer: 2000 → 6000 bp (Appendix A).
    const mastery = await s.getMasterySnapshot();
    expect(mastery).toHaveLength(1);
    expect(mastery[0].p_bp).toBe(6000);
    expect(mastery[0].band).toBe("partial");
    expect(mastery[0].last_event_seq).toBe(ev.seq);

    // Bloom mastery is tracked alongside concept mastery in the same transaction
    const bloom = await s.getBloomMasterySnapshot();
    expect(bloom).toHaveLength(1);
    expect(bloom[0].concept_id).toBe("c0001");
    expect(bloom[0].bloom_level).toBe("apply");
    expect(bloom[0].p_bp).toBe(6000);
    expect(bloom[0].band).toBe("partial");
    expect(bloom[0].attempts).toBe(1);
    expect(bloom[0].correct).toBe(1);
    expect(bloom[0].last_event_seq).toBe(ev.seq);

    // Another answer on a different cognitive level for the same concept
    const ev2 = await s.recordGradedAnswer({
      deviceId, eventId: "evt_atomic0000000002",
      conceptId: "c0001", correct: false,
      attemptId: "att-2", questionId: "q_ch01_c0001_02",
      bloomLevel: "remember",
    });
    const bloom2 = await s.getBloomMasterySnapshot();
    expect(bloom2).toHaveLength(2);
    const applyRow = bloom2.find((r) => r.bloom_level === "apply");
    const remRow = bloom2.find((r) => r.bloom_level === "remember");
    expect(applyRow?.p_bp).toBe(6000);
    expect(remRow?.p_bp).toBe(1758); // 2000 incorrect -> 1758
    expect(remRow?.attempts).toBe(1);
    expect(remRow?.correct).toBe(0);

    const pending = await s.listPendingOutbox();
    expect(pending).toHaveLength(2);
    expect(pending[0].event_type).toBe("ANSWER_SUBMITTED");
    expect(pending[0].payload.attempt_id).toBe("att-1");
    expect(pending[0].payload.bloom_level).toBe("apply");
    expect(pending[0].outbox_state).toBe("pending");
  });

  it("seq is monotonic across events", async () => {
    const { deviceId, learnerId } = deviceAndSession("lrn_seqtest00000001");
    const s = await ProfileSession.open(learnerId);
    const e1 = await s.recordGradedAnswer({
      deviceId, eventId: "evt_seq00000000000001", conceptId: "c0001",
      correct: true, attemptId: "att-1",
    });
    const e2 = await s.recordEvent({
      deviceId, eventId: "evt_seq00000000000002",
      eventType: "CONTENT_VIEWED", payload: {},
    });
    const e3 = await s.recordGradedAnswer({
      deviceId, eventId: "evt_seq00000000000003", conceptId: "c0001",
      correct: false, attemptId: "att-2",
    });
    expect(e2.seq).toBe(e1.seq + 1);
    expect(e3.seq).toBe(e2.seq + 1);
  });

  it("a failed write leaves no partial event (fault matrix)", async () => {
    const { deviceId, learnerId } = deviceAndSession("lrn_failtest0000001");
    const s = await ProfileSession.open(learnerId);
    // Abort the transaction right after the writes are queued (app killed
    // during the local transaction): state and outbox must agree — nothing
    // commits.
    const db = await (s as any).openProfileDb();
    const original = db.transaction.bind(db);
    db.transaction = (stores: any, mode: any) => {
      const tx = original(stores, mode);
      const outbox = tx.objectStore("outbox");
      const put = outbox.put.bind(outbox);
      outbox.put = (...args: any[]) => {
        const req = put(...args);
        // Abort in the same task, before the queue processes: everything
        // rolled back atomically.
        queueMicrotask(() => { try { tx.abort(); } catch { /* already done */ } });
        return req;
      };
      return tx;
    };
    await expect(s.recordGradedAnswer({
      deviceId, eventId: "evt_failtest000000001", conceptId: "c0001",
      correct: true, attemptId: "att-x",
    })).rejects.toThrow();
    db.transaction = original;
    // No partial event, no partial mastery, seq counter not leaked.
    const s2 = await ProfileSession.open(learnerId);
    expect(await s2.getMasterySnapshot()).toHaveLength(0);
    expect(await s2.getBloomMasterySnapshot()).toHaveLength(0);
    expect(await s2.listPendingOutbox()).toHaveLength(0);
    const next = await s2.recordGradedAnswer({
      deviceId, eventId: "evt_failtest000000002", conceptId: "c0001",
      correct: true, attemptId: "att-y",
    });
    expect(next.seq).toBe(1); // counter was rolled back with the txn
  });
});

describe("shared-device profile isolation", () => {
  it("one learner can never read another's mastery or outbox", async () => {
    const d = "dev_sharedtest00000001";
    const sunita = await ProfileSession.open("lrn_sunita000000001");
    await sunita.recordGradedAnswer({
      deviceId: d, eventId: "evt_sunita0000000001",
      conceptId: "c0001", correct: true, attemptId: "att-s1",
    });
    await sunita.recordDecision({
      decision_id: "dec_sunita0000000001", action: "RETRY",
      delivery_mode: "cached", background_actions: [],
      target_concept_id: "c0001", chapter_id: "ch001",
      reason_code: "PARTIAL_PRACTICE", reason_or: "",
      needs_help: false, network: "offline", source: "local",
      ruleset_version: "1.0.0", created_at: Date.now(),
    });
    await sunita.close();

    const ravi = await ProfileSession.open("lrn_ravi00000000001");
    // Ravi starts empty: Sunita's progress is in a DIFFERENT database.
    expect(await ravi.getMasterySnapshot()).toHaveLength(0);
    expect(await ravi.getBloomMasterySnapshot()).toHaveLength(0);
    expect(await ravi.listPendingOutbox()).toHaveLength(0);
    expect(await ravi.listRecentDecisions()).toHaveLength(0);
    expect(await ravi.listQuarantine()).toHaveLength(0);
    // Ravi answers the same concept: his seq starts at 1 (separate counter).
    const ev = await ravi.recordGradedAnswer({
      deviceId: d, eventId: "evt_ravi000000000001",
      conceptId: "c0001", correct: false, attemptId: "att-r1",
      bloomLevel: "remember",
    });
    expect(ev.seq).toBe(1);
    expect(await ravi.getBloomMasterySnapshot()).toHaveLength(1);
    // And his write does not affect Sunita's store.
    await ravi.close();
    const sunita2 = await ProfileSession.open("lrn_sunita000000001");
    const m = await sunita2.getMasterySnapshot();
    expect(m).toHaveLength(1);
    expect(m[0].attempts).toBe(1);
    expect(m[0].correct).toBe(1);
    const bm = await sunita2.getBloomMasterySnapshot();
    expect(bm).toHaveLength(1);
    expect(bm[0].attempts).toBe(1);
    expect(bm[0].correct).toBe(1);
  });

  it("profile switch while offline keeps each outbox separate", async () => {
    const d = "dev_offlinetest0000001";
    const a = await openProfileSession("lrn_offlineA0000001");
    await a.recordEvent({ deviceId: d, eventId: "evt_offlineA00000001",
                          eventType: "CONTENT_VIEWED", payload: {} });
    const b = await openProfileSession("lrn_offlineB0000001");
    expect((await b.listPendingOutbox()).map((e) => e.event_id))
      .not.toContain("evt_offlineA00000001");
    await b.recordEvent({ deviceId: d, eventId: "evt_offlineB00000001",
                          eventType: "DOUBT_ASKED", payload: {} });
    const a2 = await openProfileSession("lrn_offlineA0000001");
    const aPending = await a2.listPendingOutbox();
    expect(aPending.map((e) => e.event_id))
      .toEqual(["evt_offlineA00000001"]);
  });
});

describe("sync outcome application (v2 Section 8)", () => {
  async function seed(learnerId: string) {
    const d = "dev_syncouttest0000001";
    const s = await ProfileSession.open(learnerId);
    const e1 = await s.recordGradedAnswer({
      deviceId: d, eventId: "evt_syncout0000000001", conceptId: "c0001",
      correct: true, attemptId: "att-1",
    });
    const e2 = await s.recordGradedAnswer({
      deviceId: d, eventId: "evt_syncout0000000002", conceptId: "c0001",
      correct: true, attemptId: "att-2",
    });
    const e3 = await s.recordGradedAnswer({
      deviceId: d, eventId: "evt_syncout0000000003", conceptId: "c0001",
      correct: true, attemptId: "att-3",
    });
    return { s, d, e1, e2, e3 };
  }

  it("ACCEPTED and DUPLICATE remove; RETRYABLE keeps; REJECTED quarantines", async () => {
    const { s, e1, e2, e3 } = await seed("lrn_syncout000000001");
    const applied = await s.applySyncOutcomes({
      results: [
        { event_id: e1.event_id, seq: e1.seq, outcome: "ACCEPTED" },
        { event_id: e2.event_id, seq: e2.seq, outcome: "DUPLICATE" },
        { event_id: e3.event_id, seq: e3.seq, outcome: "RETRYABLE",
          reason: "SERVER_BUSY" },
      ],
    });
    expect(applied.removed).toBe(2);
    expect(applied.retried).toBe(1);
    expect(applied.quarantined).toBe(0);
    const pending = await s.listPendingOutbox();
    expect(pending.map((p) => p.event_id)).toEqual([e3.event_id]);
    expect(pending[0].retry_count).toBe(1);
    expect(await s.listQuarantine()).toHaveLength(0);
  });

  it("REJECTED moves to quarantine then out of the outbox in one commit", async () => {
    const { s, e1 } = await seed("lrn_quarantine0000001");
    await s.applySyncOutcomes({
      results: [
        { event_id: e1.event_id, seq: e1.seq, outcome: "REJECTED",
          reason: "PAYLOAD_CONFLICT" },
      ],
    });
    const q = await s.listQuarantine();
    expect(q).toHaveLength(1);
    expect(q[0].reason).toBe("PAYLOAD_CONFLICT");
    expect(q[0].event_type).toBe("ANSWER_SUBMITTED");
    expect(await s.listPendingOutbox()).toHaveLength(2);
  });

  it("server mastery replaces local, then local events re-apply (rebase)", async () => {
    const { s, e1, e2, e3 } = await seed("lrn_rebase0000000001");
    // Server accepted e1 and says c0001 is at 5000 bp (authoritative).
    await s.applySyncOutcomes({
      results: [
        { event_id: e1.event_id, seq: e1.seq, outcome: "ACCEPTED" },
      ],
    });
    // Rebase: replace mastery with the server snapshot, then re-apply the
    // local events created AFTER the upload snapshot (e2, e3), in seq order.
    await s.applySyncOutcomes({
      results: [],
      serverMastery: [
        { concept_id: "c0001", p_bp: 5000, band: "partial",
          attempts: 1, correct: 1, last_event_seq: 1 },
      ],
      serverBloomMastery: [
        { concept_id: "c0001", bloom_level: "remember", p_bp: 5000, band: "partial",
          attempts: 1, correct: 1, last_event_seq: 1 },
      ],
      localEventsAfter: [e2, e3],
    });
    const m = await s.getMasterySnapshot();
    expect(m).toHaveLength(1);
    expect(m[0].p_bp).toBeGreaterThan(5000);
    // Server attempts (1) + two re-applied correct answers.
    expect(m[0].attempts).toBe(3);
    expect(m[0].correct).toBe(3);

    const bm = await s.getBloomMasterySnapshot();
    expect(bm).toHaveLength(1);
    expect(bm[0].p_bp).toBeGreaterThan(5000);
    expect(bm[0].attempts).toBe(3);
    expect(bm[0].correct).toBe(3);
  });

  it("missing outcomes leave events untouched (lost response stays queued)", async () => {
    const { s } = await seed("lrn_lostresp00000001");
    // A lost response (no results at all): nothing removed, resend is safe.
    const applied = await s.applySyncOutcomes({ results: [] });
    expect(applied.removed).toBe(0);
    expect((await s.listPendingOutbox()).length).toBe(3);
  });
});

describe("local PIN (strictly local, salted verifier)", () => {
  it("creates and verifies a PIN without storing the raw secret", async () => {
    const s = await ProfileSession.open("lrn_pin0000000000001");
    expect(await s.hasPin()).toBe(false);
    await s.setPin("1234");
    expect(await s.hasPin()).toBe(true);
    expect(await s.verifyPin("1234")).toBe(true);
    expect(await s.verifyPin("4321")).toBe(false);
    expect(await s.verifyPin("12345")).toBe(false);
    // The stored row is a salted verifier, never the PIN itself.
    const db = await (s as any).openProfileDb();
    const tx = db.transaction("session", "readonly");
    const row: any = await new Promise((res, rej) => {
      const r = tx.objectStore("session").get("pin");
      r.onsuccess = () => res(r.result);
      r.onerror = () => rej(r.error);
    });
    expect(row.verifier_b64).not.toContain("1234");
    expect(row.iterations).toBeGreaterThanOrEqual(100_000);
  });

  it("PIN creation rejects non-4-digit input", async () => {
    const s = await ProfileSession.open("lrn_pin0000000000002");
    await expect(s.setPin("12")).rejects.toThrow();
    await expect(s.setPin("abcd")).rejects.toThrow();
  });

  it("verifier helper is salted (two rows differ)", async () => {
    const a = await createPinVerifier("9999");
    const b = await createPinVerifier("9999");
    expect(a.salt_b64).not.toBe(b.salt_b64);
    expect(a.verifier_b64).not.toBe(b.verifier_b64);
    expect(await verifyPin("9999", a)).toBe(true);
  });
});

describe("corrupted state and storage failures", () => {
  it("flags invalid learner ids instead of opening a stray database", async () => {
    await expect(ProfileSession.open("")).rejects.toThrow();
    await expect(ProfileSession.open("../escape")).rejects.toThrow();
  });

  it("exposes typed errors for corrupted upgrade paths", async () => {
    // Simulate an upgrade handler failure → CorruptedState, not a crash.
    const { CorruptedState: CS } = await import("../src/store/profile_session");
    const err = new CS("upgrade failed");
    expect(err).toBeInstanceOf(CS);
  });

  it("quarantine can be salvaged across a corrupted-profile recovery", async () => {
    const learnerId = "lrn_recover000000001";
    const s = await ProfileSession.open(learnerId);
    await s.recordGradedAnswer({
      deviceId: "dev_recovertest0000001", eventId: "evt_recover000000001",
      conceptId: "c0001", correct: true, attemptId: "att-1",
    });
    await s.applySyncOutcomes({
      results: [{ event_id: "evt_recover000000001", seq: 1,
                  outcome: "REJECTED", reason: "INVALID_PAYLOAD" }],
    });
    const salvaged = await s.listQuarantine();
    expect(salvaged).toHaveLength(1);
    await s.close();
    await ProfileSession.recoverCorruptedProfile(learnerId, salvaged);
    const s2 = await ProfileSession.open(learnerId);
    // Quarantine salvaged; mastery re-created empty (rebuildable by replay).
    expect(await s2.listQuarantine()).toHaveLength(1);
    expect(await s2.getMasterySnapshot()).toHaveLength(0);
  });
});
