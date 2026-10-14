// Shared rule vectors — TypeScript side (v2).
// Runs the SAME fixtures as the Python suite through the TS engine:
//   golden (hand-labelled), invalid (fallback), fuzz (parity snapshots),
//   and step-by-step integer BKT sequences (Appendix A parity).

import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  decide, DecisionInput, MasteryEntry, RULESET,
  bktUpdateBp, masteryBandBp, roundHalfUpDiv, engineError, SCALE,
} from "../src/engine/decide";

const fixturePath = resolve(__dirname, "../../tests/fixtures/rule_vectors.json");
const fixture = JSON.parse(readFileSync(fixturePath, "utf-8"));

function toInput(v: any): DecisionInput {
  const inp = v.input;
  const mastery: Record<string, MasteryEntry> = {};
  for (const [cid, m] of Object.entries<any>(inp.mastery || {})) {
    mastery[cid] = {
      p_bp: m.p_bp, attempts: m.attempts ?? 0, correct: m.correct ?? 0,
      last_event_seq: m.last_event_seq ?? 0,
    };
  }
  return {
    trigger_event_type: inp.trigger_event_type,
    trigger_concept_id: inp.trigger_concept_id ?? null,
    trigger_correct: inp.trigger_correct ?? null,
    mastery,
    recent_events: (inp.recent_events || []).map((e: any) => ({
      seq: e.seq, event_type: e.event_type, concept_id: e.concept_id ?? null,
      correct: e.correct ?? null, p_bp_after: e.p_bp_after ?? null,
      last_action: e.last_action ?? null,
    })),
    prereqs: inp.prereqs || {},
    concept_order: inp.concept_order || [],
    chapter_id_for_concept: inp.chapter_id_for_concept || {},
    doubt_concept_hint: inp.doubt_concept_hint ?? null,
    env_network: inp.env_network,
    installed_pack_versions: inp.installed_pack_versions || {},
    required_pack_for_concept: inp.required_pack_for_concept || {},
    storage_free_mb: inp.storage_free_mb ?? 1_000_000,
    battery_saver: !!inp.battery_saver,
    outbox_nonempty: !!inp.outbox_nonempty,
    ruleset_version: inp.ruleset_version,
  };
}

describe("ruleset", () => {
  it("version matches the shared fixture", () => {
    expect(fixture.ruleset_version).toBe(RULESET.ruleset_version);
    expect(fixture.bkt_version).toBe(RULESET.bkt_version);
  });
});

describe("golden vectors (hand-labelled, v2 Section 6)", () => {
  it.each(fixture.golden.map((v: any, i: number) => ({ v, i })))(
    "$v.name returns the labelled action",
    ({ v }: { v: any }) => {
      const out = decide(toInput(v));
      const expected = v.expected;
      expect(out.action).toBe(expected.action);
      expect(out.target_concept_id).toBe(expected.target_concept_id);
      expect(out.reason_code).toBe(expected.reason_code);
      expect(out.needs_help).toBe(expected.needs_help);
      expect(out.delivery_mode).toBe(expected.delivery_mode);
      expect(out.background_actions).toEqual(expected.background_actions);
    },
  );
});

describe("invalid inputs (identical fallback in both engines)", () => {
  it.each(fixture.invalid.map((v: any, i: number) => ({ v, i })))(
    "$v.name yields the typed fallback",
    ({ v }: { v: any }) => {
      const inp = toInput(v);
      expect(engineError(inp)).not.toBeNull();
      const out = decide(inp);
      expect(out.reason_code).toBe(v.expected.reason_code);
      expect(out.fallback).toBe(true);
      expect(["REMEDIATE", "RETRY", "REVISE", "ADVANCE"]).toContain(out.action);
    },
  );
});

describe("fuzz vectors (engine parity snapshots)", () => {
  it.each(fixture.fuzz.map((v: any, i: number) => ({ v, i })))(
    "$v.name matches the shared expectation",
    ({ v }: { v: any }) => {
      const out = decide(toInput(v));
      const expected = v.expected;
      expect(out.action).toBe(expected.action);
      expect(out.target_concept_id).toBe(expected.target_concept_id);
      expect(out.delivery_mode).toBe(expected.delivery_mode);
      expect(out.background_actions).toEqual(expected.background_actions);
      expect(out.reason_code).toBe(expected.reason_code);
      expect(out.needs_help).toBe(expected.needs_help);
    },
  );
});

describe("BKT update sequences (integer basis points, Appendix A)", () => {
  it.each(fixture.bkt.map((c: any, i: number) => ({ c, i })))(
    "$c.name reproduces the exact bp steps",
    ({ c }: { c: any }) => {
      let p = c.p_init_bp;
      for (let i = 0; i < c.steps.length; i++) {
        p = bktUpdateBp(p, c.steps[i].correct);
        expect(p).toBe(c.steps[i].p_bp);
        expect(masteryBandBp(p)).toBe(c.steps[i].band);
        expect(p).toBeGreaterThanOrEqual(100);
        expect(p).toBeLessThanOrEqual(9900);
      }
    },
  );

  it("half-up rounding matches the Python helper", () => {
    expect(roundHalfUpDiv(5, 2)).toBe(3);
    expect(roundHalfUpDiv(3, 2)).toBe(2);
    expect(roundHalfUpDiv(4, 2)).toBe(2);
    expect(roundHalfUpDiv(1, 3)).toBe(0);
    expect(roundHalfUpDiv(0, 7)).toBe(0);
    expect(() => roundHalfUpDiv(1, 0)).toThrow();
  });

  it("first correct answer from p_init is exactly 6000 bp", () => {
    expect(bktUpdateBp(2000, true)).toBe(6000);
  });

  it("replaying the same sequence is exact (replay invariant)", () => {
    const answers = [true, false, true, true, false];
    let a = 2000;
    for (const c of answers) a = bktUpdateBp(a, c);
    let b = 2000;
    for (const c of answers) b = bktUpdateBp(b, c);
    expect(a).toBe(b);
    expect(Number.isInteger(a)).toBe(true);
  });
});

describe("engine purity", () => {
  it("mastery is always an integer in [0, 10000] after updates", () => {
    for (const p0 of [0, 100, 2500, 5000, 9900]) {
      for (const correct of [true, false]) {
        const p = bktUpdateBp(p0, correct);
        expect(Number.isInteger(p)).toBe(true);
        expect(p).toBeGreaterThanOrEqual(0);
        expect(p).toBeLessThanOrEqual(SCALE);
      }
    }
  });
});
