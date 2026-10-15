// Deterministic decision engine v2 — TypeScript mirror of
// backend/app/domain/decide.py (Design v2 Sections 6 + Appendix A).
// Consumes the SAME packages/ruleset/rules.json as the Python engine.
// Both implementations must pass the SAME test vectors
// (tests/fixtures/rule_vectors.json) with IDENTICAL outputs.
//
// Pure functions: no network, no LLM, no process-local memory. Mastery is
// an INTEGER in basis points (0..10000); the BKT update is exact integer
// arithmetic so Python and JavaScript cannot disagree through floats.

import rulesetRaw from "../generated/ruleset.json";

export const RULESET: Ruleset = rulesetRaw as Ruleset;

export interface Ruleset {
  version: string;
  ruleset_version: string;
  bkt_version: string;
  bkt: any;
  bands: any;
  guard: any;
  mastery: any;
  repetition_guard: any;
  target_selection: any;
  network: any;
  delivery: any;
  background_actions: any;
  retries: any;
  sync: any;
  pack: any;
  prefetch: any;
  doubt: any;
  auth: any;
  orchestration: any;
  translation: any;
  retrieval: any;
  generation: any;
  validation: any;
  bloom?: any;
}

export const SCALE = 10000;

export interface MasteryEntry {
  p_bp: number;
  attempts?: number;
  correct?: number;
  last_event_seq?: number;
}

export interface RecentEvent {
  seq: number;
  event_type: string;
  concept_id?: string | null;
  correct?: boolean | null;
  p_bp_after?: number | null;
  last_action?: string | null;
}

export interface DecisionInput {
  trigger_event_type: string;
  trigger_concept_id: string | null;
  trigger_correct: boolean | null;
  mastery: Record<string, MasteryEntry>;
  recent_events: RecentEvent[];
  prereqs: Record<string, string[]>;
  concept_order: string[];
  chapter_id_for_concept?: Record<string, string>;
  doubt_concept_hint?: string | null;
  env_network: "online" | "weak" | "offline" | "reconnected";
  installed_pack_versions: Record<string, number>;
  required_pack_for_concept?: Record<string, string>;
  storage_free_mb?: number;
  battery_saver?: boolean;
  outbox_nonempty?: boolean;
  ruleset_version: string;
  bloom_mastery?: Record<string, Record<string, MasteryEntry>>;
  available_bloom_levels_for_concept?: Record<string, string[]>;
}

export interface DecisionOutput {
  action: "REMEDIATE" | "RETRY" | "REVISE" | "ADVANCE";
  target_concept_id: string;
  delivery_mode: "cached" | "rich" | "prefetch_then_offline";
  background_actions: string[];
  reason_code: string;
  target_bloom_level?: string | null;
  needs_help: boolean;
  rule_index: number;
  fallback: boolean;
}

// --------------------------------------------------------------------------- //
// BKT — exact integer arithmetic (Appendix A)
// --------------------------------------------------------------------------- //
export function toBp(x: number): number {
  return Math.round(x * SCALE);
}

export interface BKTParams {
  p_init_bp: number;
  learn_bp: number;
  slip_bp: number;
  guess_bp: number;
  clamp_lo_bp: number;
  clamp_hi_bp: number;
}

export function bktParams(conceptId?: string): BKTParams {
  const b = RULESET.bkt;
  const overrides = (b.per_concept_overrides || {})[conceptId || ""] || {};
  const clamp = overrides.clamp_bp || b.clamp_bp || [100, 9900];
  return {
    p_init_bp: overrides.p_init_bp ?? b.p_init_bp ?? 2000,
    learn_bp: toBp(overrides.learn ?? b.learn ?? 0.15),
    slip_bp: toBp(overrides.slip ?? b.slip ?? 0.10),
    guess_bp: toBp(overrides.guess ?? b.guess ?? 0.20),
    clamp_lo_bp: clamp[0],
    clamp_hi_bp: clamp[1],
  };
}

/** Half-up rounding of the positive integer division n/d — the identical
 * formula lives in Python (`round_half_up_div`). */
export function roundHalfUpDiv(n: number, d: number): number {
  if (d <= 0) throw new Error("denominator must be positive");
  return Math.floor((2 * n + d) / (2 * d));
}

/** Exact Appendix A update from the stored integer mastery (basis points). */
export function bktUpdateBp(pBp: number, correct: boolean,
                            conceptId?: string): number {
  const params = bktParams(conceptId);
  const p = Math.max(0, Math.min(SCALE, Math.floor(pBp)));
  const S = params.slip_bp, G = params.guess_bp, L = params.learn_bp;
  let num: number, den: number;
  if (correct) {
    num = p * (SCALE - S);
    den = num + (SCALE - p) * G;
  } else {
    num = p * S;
    den = num + (SCALE - p) * (SCALE - G);
  }
  let posteriorNum = num, posteriorDen = den;
  if (den <= 0) { posteriorNum = p; posteriorDen = SCALE; }
  const n = posteriorNum * SCALE + (posteriorDen - posteriorNum) * L;
  const d = posteriorDen;
  const q = roundHalfUpDiv(n, d);
  return Math.max(params.clamp_lo_bp, Math.min(params.clamp_hi_bp, q));
}

/** Back-compat alias (v2 integer contract). */
export function bktUpdate(pBp: number, correct: boolean,
                          conceptId?: string): number {
  return bktUpdateBp(pBp, correct, conceptId);
}

export function masteryBandBp(pBp: number): "weak" | "partial" | "mastered" {
  if (pBp < (RULESET.bands.weak_below_bp ?? 4000)) return "weak";
  if (pBp < (RULESET.bands.mastered_at_bp ?? 8500)) return "partial";
  return "mastered";
}

// --------------------------------------------------------------------------- //
// Reason strings (developer fallbacks; i18n dict overrides)
// --------------------------------------------------------------------------- //
export const REASON_MESSAGES: Record<string, string> = {};

const DEFAULT_REASON_OR: Record<string, string> = {
  STATE_INVALID_FALLBACK: "ଅସ୍ଥାୟୀ ସମସ୍ୟା। ପୁଣି ଚେଷ୍ଟା କର।",
  COLD_START: "ପ୍ରଥମ ଧାରଣା ଆରମ୍ଭ କର।",
  WEAK_PREREQ_GAP: "ପ୍ରଥମେ ଆଧାର ଧାରଣା ବଦ୍ଧ କର।",
  WEAK_CONCEPT: "ଏହି ଧାରଣା ପୁଣି ଶିଖ।",
  WRONG_RETRY: "ଉତ୍ତର ଭୁଲ ଥିଲା। ପୁଣି ଚେଷ୍ଟା କର।",
  PARTIAL_PRACTICE: "ଭଲ ହେଲା! ଆଉ ଏକ ଅଭ୍ୟାସ କର।",
  MASTERED_ADVANCE: "ବାହ୍! ପରବର୍ତ୍ତୀ ଧାରଣା କୁ ଯାଅ।",
  NO_GAIN_ALT_CONTENT: "ଅନ୍ୟ ଉପାୟରେ ପାଠ ପଢ।",
  NO_GAIN_REMEDIATE_PREREQ: "ପ୍ରଥମେ ଆଧାର ଧାରଣା ବଦ୍ଧ କର।",
  INTERVENTIONS_EXHAUSTED: "ଶିକ୍ଷକଙ୍କ ସହିତ ଯୋଗାଯୋଗ କର।",
  SLICE_COMPLETE: "ସମସ୍ତ ପାଠ ସମ୍ପୂର୍ଣ୍ଣ! ପୁଣି ରିଭିଜନ୍ କର।",
  BLOCKED_BY_PREREQ: "ପ୍ରଥମେ ଆଧାର ଧାରଣା ଶିଖ।",
  CONTENT_NOT_AVAILABLE_OFFLINE: "ଏହି ପାଠ ଅଫଲାଇନ୍ ଉପଲବ୍ଧ ନାହିଁ। ଅନ୍ୟ ପାଠ ପଢ।",
};

function reasonOr(code: string): string {
  return REASON_MESSAGES[code] || DEFAULT_REASON_OR[code] || "ଆଗାମୀ କାମ ଜାରି ରଖ।";
}

// --------------------------------------------------------------------------- //
// Deterministic helpers
// --------------------------------------------------------------------------- //
function weakestPrereq(cid: string, inp: DecisionInput): string | null {
  let best: [number, string] | null = null;
  for (const pre of inp.prereqs[cid] || []) {
    const p = inp.mastery[pre]?.p_bp ?? 0;
    const key: [number, string] = [p, pre];
    if (best === null || key < best) best = key;
  }
  return best ? best[1] : null;
}

function prereqsMastered(cid: string, inp: DecisionInput): boolean {
  const masteredAt = RULESET.bands.mastered_at_bp ?? 8500;
  return (inp.prereqs[cid] || []).every(
    (pre) => (inp.mastery[pre]?.p_bp ?? 0) >= masteredAt);
}

function firstConceptWithoutPrereqs(inp: DecisionInput): string | null {
  for (const cid of inp.concept_order) {
    if (!(inp.prereqs[cid] || []).length) return cid;
  }
  return null;
}

function nextEligibleConcept(inp: DecisionInput,
                             after?: string | null): string | null {
  const masteredAt = RULESET.bands.mastered_at_bp ?? 8500;
  let started = after === undefined || after === null;
  for (const cid of inp.concept_order) {
    if (!started) {
      if (cid === after) started = true;
      continue;
    }
    if ((inp.mastery[cid]?.p_bp ?? 0) >= masteredAt) continue;
    if (prereqsMastered(cid, inp)) return cid;
  }
  return null;
}

function lowestMasteryWithMasteredPrereqs(inp: DecisionInput): string | null {
  let best: [number, number, string] | null = null;
  inp.concept_order.forEach((cid, idx) => {
    if (!prereqsMastered(cid, inp)) return;
    const p = inp.mastery[cid]?.p_bp ?? 0;
    const key: [number, number, string] = [p, idx, cid];
    if (best === null || key < best) best = key;
  });
  return best ? best[2] : null;
}

function graphDistance(fromCid: string, toCid: string,
                       inp: DecisionInput, maxDepth = 6): number {
  if (fromCid === toCid) return 0;
  const adj: Record<string, Set<string>> = {};
  for (const [cid, pres] of Object.entries(inp.prereqs || {})) {
    for (const pre of pres || []) {
      (adj[cid] ||= new Set()).add(pre);
      (adj[pre] ||= new Set()).add(cid);
    }
  }
  let frontier = new Set([fromCid]);
  const seen = new Set([fromCid]);
  for (let depth = 1; depth <= maxDepth; depth++) {
    const nxt = new Set<string>();
    for (const node of frontier) {
      for (const nb of adj[node] || []) {
        if (seen.has(nb)) continue;
        if (nb === toCid) return depth;
        seen.add(nb);
        nxt.add(nb);
      }
    }
    frontier = nxt;
    if (!frontier.size) break;
  }
  return maxDepth + 1;
}

function targetPackInstalled(cid: string, inp: DecisionInput): boolean {
  const packId = (inp.required_pack_for_concept || {})[cid];
  if (!packId) return true;
  return packId in (inp.installed_pack_versions || {});
}

function nearestInstalledConcept(inp: DecisionInput): string | null {
  const target = inp.trigger_concept_id ||
    (selectTargetConcept(inp)[0] as string);
  if (!target) return null;
  let best: [number, number, string] | null = null;
  inp.concept_order.forEach((cid, idx) => {
    if (!targetPackInstalled(cid, inp)) return;
    const dist = graphDistance(target, cid, inp);
    const key: [number, number, string] = [dist, idx, cid];
    if (best === null || key < best) best = key;
  });
  return best ? best[2] : null;
}

// --------------------------------------------------------------------------- //
// Target selection + guard state
// --------------------------------------------------------------------------- //
function selectTargetConcept(inp: DecisionInput): [string, string] {
  if (inp.trigger_concept_id && inp.concept_order.includes(inp.trigger_concept_id)) {
    return [inp.trigger_concept_id, "last_graded"];
  }
  if (inp.doubt_concept_hint && inp.concept_order.includes(inp.doubt_concept_hint)) {
    return [inp.doubt_concept_hint, "doubt_hint"];
  }
  const cid = lowestMasteryWithMasteredPrereqs(inp);
  return [cid || "", "lowest_mastery"];
}

function gradedOnTarget(inp: DecisionInput, target: string): RecentEvent[] {
  return inp.recent_events.filter(
    (e) => e.event_type === "ANSWER_SUBMITTED" && e.concept_id === target
      && e.p_bp_after !== null && e.p_bp_after !== undefined);
}

export function guardState(inp: DecisionInput,
                           target: string): [number, boolean] {
  const guard = RULESET.guard || RULESET.repetition_guard || {};
  const minGain = guard.min_gain_bp ?? 200;
  const graded = gradedOnTarget(inp, target);
  let cycleStart = 0;
  for (let k = 1; k < graded.length; k++) {
    if ((graded[k].p_bp_after || 0) - (graded[k - 1].p_bp_after || 0) >= minGain) {
      cycleStart = k;
    }
  }
  const attemptsWithoutGain = Math.max(0, graded.length - cycleStart);
  const cycleStartSeq = graded.length ? graded[cycleStart].seq : 0;
  const alt = inp.recent_events.some(
    (e) => e.concept_id === target && e.last_action === "REVISE"
      && e.seq >= cycleStartSeq);
  return [attemptsWithoutGain, alt];
}

// --------------------------------------------------------------------------- //
// Delivery + background actions
// --------------------------------------------------------------------------- //
export function selectDeliveryMode(inp: DecisionInput,
                                   target: string):
  "cached" | "rich" | "prefetch_then_offline" {
  const network = inp.env_network;
  if (network === "offline") return "cached";
  if (targetPackInstalled(target, inp)) {
    return (RULESET.delivery[network] || "cached");
  }
  if (network === "online" || network === "reconnected") {
    return "prefetch_then_offline";
  }
  return "cached";
}

export function selectBackgroundActions(inp: DecisionInput,
                                        target: string,
                                        reasonCode = ""): string[] {
  const network = inp.env_network;
  const actions = new Set<string>();
  if (network !== "offline" && inp.outbox_nonempty) actions.add("SYNC");
  const prefetchOk =
    (
      ((network === "online" || network === "reconnected") && !targetPackInstalled(target, inp))
      || (reasonCode === "CONTENT_NOT_AVAILABLE_OFFLINE")
    )
    && !inp.battery_saver
    && (inp.storage_free_mb ?? 1_000_000) >= (RULESET.prefetch.min_free_mb ?? 150);
  if (prefetchOk) actions.add("PREFETCH");
  return Array.from(actions).sort(
    (a, b) => ["PREFETCH", "SYNC"].indexOf(a) - ["PREFETCH", "SYNC"].indexOf(b));
}

export const CANONICAL_BLOOM_LEVELS = [
  "remember", "understand", "apply", "analyze", "evaluate", "create",
];

export function selectTargetBloomLevel(
  action: string,
  targetConceptId: string,
  reasonCode: string,
  inp: DecisionInput,
  ruleset: Ruleset,
): string | null {
  if (!targetConceptId) {
    return null;
  }

  const bloomCfg = ruleset.bloom || {};
  const levelsAll: string[] = bloomCfg.levels || CANONICAL_BLOOM_LEVELS;
  const foundational: string[] = bloomCfg.foundational_levels || ["remember", "understand"];
  const higherOrder: string[] = bloomCfg.higher_order_levels || ["apply", "analyze", "evaluate", "create"];
  const proficientAtBp: number = Number(bloomCfg.proficient_at_bp ?? 7000);
  const masteredAtBp: number = Number(bloomCfg.mastered_at_bp ?? 8500);

  const conceptAvail = (inp.available_bloom_levels_for_concept || {})[targetConceptId];
  let availLevels: string[];
  if (conceptAvail && conceptAvail.length > 0) {
    availLevels = levelsAll.filter((lvl) => conceptAvail.includes(lvl));
    if (availLevels.length === 0) {
      availLevels = [...conceptAvail];
    }
  } else {
    availLevels = [...levelsAll];
  }
  if (availLevels.length === 0) {
    availLevels = ["remember"];
  }

  const conceptBloomM = (inp.bloom_mastery || {})[targetConceptId] || {};

  function getLevelBp(lvl: string): number {
    if (conceptBloomM[lvl] && typeof conceptBloomM[lvl].p_bp === "number") {
      return conceptBloomM[lvl].p_bp;
    }
    if (lvl === "remember" && inp.mastery[targetConceptId]) {
      return inp.mastery[targetConceptId].p_bp;
    }
    const bktCfg = ruleset.bkt || {};
    return Number(bktCfg.p_init_bp ?? 2000);
  }

  let chosen: string;
  if (action === "ADVANCE") {
    chosen = availLevels[0];
  } else if (action === "REMEDIATE") {
    let cand = availLevels.filter((lvl) => foundational.includes(lvl));
    if (cand.length === 0) cand = availLevels;
    const below = cand.filter((lvl) => getLevelBp(lvl) < proficientAtBp);
    chosen = below.length > 0 ? below[0] : cand[0];
  } else if (action === "REVISE") {
    if (reasonCode === "SLICE_COMPLETE") {
      const hoCand = availLevels.filter((lvl) => higherOrder.includes(lvl));
      chosen = hoCand.length > 0 ? hoCand[hoCand.length - 1] : availLevels[availLevels.length - 1];
    } else {
      const cand = availLevels.filter((lvl) => foundational.includes(lvl));
      chosen = cand.length > 0 ? cand[0] : availLevels[0];
    }
  } else if (action === "RETRY") {
    let firstUnproficient: string | null = null;
    for (const lvl of levelsAll) {
      if (getLevelBp(lvl) < proficientAtBp) {
        firstUnproficient = lvl;
        break;
      }
    }
    let desired: string;
    if (firstUnproficient !== null) {
      desired = firstUnproficient;
    } else {
      let firstUnmastered: string | null = null;
      for (const lvl of levelsAll) {
        if (getLevelBp(lvl) < masteredAtBp) {
          firstUnmastered = lvl;
          break;
        }
      }
      desired = firstUnmastered !== null ? firstUnmastered : levelsAll[levelsAll.length - 1];
    }

    if (availLevels.includes(desired)) {
      chosen = desired;
    } else {
      const desiredIdx = levelsAll.indexOf(desired);
      const lowerAvail = availLevels.filter((lvl) => {
        const idx = levelsAll.indexOf(lvl);
        return (idx >= 0 ? idx : 0) <= (desiredIdx >= 0 ? desiredIdx : levelsAll.length - 1);
      });
      chosen = lowerAvail.length > 0 ? lowerAvail[lowerAvail.length - 1] : availLevels[availLevels.length - 1];
    }
  } else {
    chosen = availLevels[0];
  }

  if (!availLevels.includes(chosen)) {
    chosen = availLevels[0];
  }
  return chosen;
}

// --------------------------------------------------------------------------- //
// Trajectory check
// --------------------------------------------------------------------------- //
const VALID_ACTIONS = ["REMEDIATE", "RETRY", "REVISE", "ADVANCE"];
const VALID_DELIVERY = ["cached", "rich", "prefetch_then_offline"];
const VALID_BACKGROUND = ["SYNC", "PREFETCH"];

export function trajectoryCheck(out: DecisionOutput,
                                inp: DecisionInput): boolean {
  if (out.target_concept_id && !inp.concept_order.includes(out.target_concept_id)) return false;
  if (!VALID_ACTIONS.includes(out.action)) return false;
  if (!(out.reason_code in DEFAULT_REASON_OR)) return false;
  if (!VALID_DELIVERY.includes(out.delivery_mode)) return false;
  if (out.delivery_mode === "rich" && inp.env_network === "offline") return false;
  if (out.background_actions.some((a) => !VALID_BACKGROUND.includes(a))) return false;
  const sorted = [...out.background_actions].sort(
    (a, b) => ["PREFETCH", "SYNC"].indexOf(a) - ["PREFETCH", "SYNC"].indexOf(b));
  if (out.background_actions.join(",") !== sorted.join(",")) return false;
  if (out.target_bloom_level && !CANONICAL_BLOOM_LEVELS.includes(out.target_bloom_level)) return false;
  if (inp.ruleset_version !== RULESET.ruleset_version) return false;
  return true;
}

// --------------------------------------------------------------------------- //
// Typed engine error (unknown ruleset / invalid state)
// --------------------------------------------------------------------------- //
export function engineError(inp: DecisionInput): string | null {
  if (inp.ruleset_version !== RULESET.ruleset_version) return "RULESET_UNKNOWN";
  for (const m of Object.values(inp.mastery)) {
    if (!Number.isInteger(m.p_bp) || m.p_bp < 0 || m.p_bp > SCALE) {
      return "STATE_INVALID";
    }
  }
  if (inp.trigger_correct !== null && inp.trigger_correct !== undefined
      && !inp.trigger_concept_id) return "STATE_INVALID";
  return null;
}

export function stateIsValid(inp: DecisionInput): boolean {
  return engineError(inp) === null;
}

// --------------------------------------------------------------------------- //
// Top-level decide()
// --------------------------------------------------------------------------- //
function finish(inp: DecisionInput,
                action: DecisionOutput["action"],
                target: string, reasonCode: string,
                needsHelp: boolean, ruleIndex: number, fallback = false):
  DecisionOutput {
  let outTarget = target;
  let reason = reasonCode;
  if (outTarget && !targetPackInstalled(outTarget, inp)
      && inp.env_network === "offline") {
    const nearest = nearestInstalledConcept(inp);
    if (nearest && nearest !== outTarget) {
      outTarget = nearest;
      reason = "CONTENT_NOT_AVAILABLE_OFFLINE";
    } else {
      // No pack installed at all → fallback decision (v2 edge behaviour).
      return {
        action: "RETRY", target_concept_id: outTarget,
        delivery_mode: "cached", background_actions: [],
        reason_code: "STATE_INVALID_FALLBACK",
        target_bloom_level: outTarget ? "remember" : null,
        needs_help: false,
        rule_index: 0, fallback: true,
      };
    }
  }
  const targetBloom = selectTargetBloomLevel(action, outTarget, reason, inp, RULESET);
  const out: DecisionOutput = {
    action, target_concept_id: outTarget,
    delivery_mode: selectDeliveryMode(inp, outTarget),
    background_actions: selectBackgroundActions(inp, outTarget, reason),
    reason_code: reason,
    target_bloom_level: targetBloom,
    needs_help: needsHelp,
    rule_index: ruleIndex, fallback,
  };
  if (!trajectoryCheck(out, inp)) {
    const tgt = (inp.trigger_concept_id
      && inp.concept_order.includes(inp.trigger_concept_id))
      ? inp.trigger_concept_id
      : (inp.concept_order[0] || "");
    return {
      action: "RETRY", target_concept_id: tgt,
      delivery_mode: "cached", background_actions: [],
      reason_code: "STATE_INVALID_FALLBACK",
      target_bloom_level: tgt ? "remember" : null,
      needs_help: false,
      rule_index: 0, fallback: true,
    };
  }
  return out;
}

export function decide(inp: DecisionInput): DecisionOutput {
  const weakBelow = RULESET.bands.weak_below_bp ?? 4000;
  const masteredAt = RULESET.bands.mastered_at_bp ?? 8500;
  const guardCfg = RULESET.guard || RULESET.repetition_guard || {};
  const attemptsAllowed = guardCfg.attempts_without_gain ?? 3;

  // Rule 0: invalid state or unknown ruleset → safe fallback.
  const err = engineError(inp);
  if (err !== null) {
    const target = (inp.trigger_concept_id
      && inp.concept_order.includes(inp.trigger_concept_id))
      ? inp.trigger_concept_id : "";
    if (!target) {
      const first = firstConceptWithoutPrereqs(inp)
        || inp.concept_order[0] || "";
      if (first) {
        return {
          action: "ADVANCE", target_concept_id: first,
          delivery_mode: selectDeliveryMode(inp, first),
          background_actions: selectBackgroundActions(inp, first),
          reason_code: "STATE_INVALID_FALLBACK",
          target_bloom_level: "remember",
          needs_help: false,
          rule_index: 0, fallback: true,
        };
      }
      return {
        action: "RETRY", target_concept_id: "",
        delivery_mode: "cached", background_actions: [],
        reason_code: "STATE_INVALID_FALLBACK",
        target_bloom_level: null,
        needs_help: false,
        rule_index: 0, fallback: true,
      };
    }
    return {
      action: "RETRY", target_concept_id: target,
      delivery_mode: selectDeliveryMode(inp, target),
      background_actions: selectBackgroundActions(inp, target),
      reason_code: "STATE_INVALID_FALLBACK",
      target_bloom_level: "remember",
      needs_help: false,
      rule_index: 0, fallback: true,
    };
  }

  // Rule 1: cold start.
  if (Object.keys(inp.mastery).length === 0) {
    const first = firstConceptWithoutPrereqs(inp);
    if (first !== null) {
      return finish(inp, "ADVANCE", first, "COLD_START", false, 1);
    }
    // Every concept has prereqs: remediate the weakest blocked one.
    const blocked = mostBlockedPrereq(inp);
    if (blocked !== null) {
      return finish(inp, "REMEDIATE", blocked, "BLOCKED_BY_PREREQ", false, 1);
    }
    return finish(inp, "RETRY", "", "STATE_INVALID_FALLBACK", false, 1, true);
  }

  // Target selection.
  const [target] = selectTargetConcept(inp);
  if (!target) {
    return finish(inp, "RETRY", "", "STATE_INVALID_FALLBACK", false, 0, true);
  }
  const m = inp.mastery[target];
  if (m === undefined || (m.attempts === 0 && (inp.trigger_correct === null || inp.trigger_correct === undefined))) {
    // Target has never been attempted: advance if prereqs are mastered, else remediate prereq gap
    if (prereqsMastered(target, inp)) {
      return finish(inp, "ADVANCE", target, "MASTERED_ADVANCE", false, 7);
    } else {
      const weakest = weakestPrereq(target, inp) || mostBlockedPrereq(inp);
      if (weakest !== null) {
        return finish(inp, "REMEDIATE", weakest, "BLOCKED_BY_PREREQ", false, 7);
      }
    }
  }
  const p = m?.p_bp ?? (RULESET.bkt.p_init_bp ?? 2000);

  // Rule 2: repeated-attempt guard.
  const [attemptsWithoutGain, altShown] = guardState(inp, target);
  if (attemptsWithoutGain >= attemptsAllowed) {
    if (!altShown) {
      return finish(inp, "REVISE", target, "NO_GAIN_ALT_CONTENT", false, 2);
    }
    const weakest = weakestPrereq(target, inp);
    if (weakest !== null) {
      const preP = inp.mastery[weakest]?.p_bp ?? 0;
      if (preP < masteredAt) {
        return finish(inp, "REMEDIATE", weakest,
                      "NO_GAIN_REMEDIATE_PREREQ", false, 2);
      }
    }
    // Terminal: never advance while T is below mastered.
    return finish(inp, "REVISE", target, "INTERVENTIONS_EXHAUSTED", true, 2);
  }

  // Rules 3-4: weak concept / weak prerequisite.
  if (p < weakBelow) {
    const weakest = weakestPrereq(target, inp);
    if (weakest !== null) {
      const preP = inp.mastery[weakest]?.p_bp ?? 0;
      if (preP < weakBelow) {
        return finish(inp, "REMEDIATE", weakest, "WEAK_PREREQ_GAP", false, 3);
      }
    }
    return finish(inp, "REMEDIATE", target, "WEAK_CONCEPT", false, 4);
  }

  // Rules 5-6: partial mastery.
  if (p < masteredAt) {
    let lastCorrect = inp.trigger_correct;
    if (lastCorrect === null || lastCorrect === undefined) {
      for (let i = inp.recent_events.length - 1; i >= 0; i--) {
        const e = inp.recent_events[i];
        if (e.event_type === "ANSWER_SUBMITTED" && e.correct !== null
            && e.correct !== undefined) {
          lastCorrect = e.correct;
          break;
        }
      }
    }
    if (lastCorrect === false) {
      return finish(inp, "RETRY", target, "WRONG_RETRY", false, 5);
    }
    return finish(inp, "RETRY", target, "PARTIAL_PRACTICE", false, 6);
  }

  // Rule 7: mastered → advance.
  const nxt = nextEligibleConcept(inp, target);
  if (nxt !== null) {
    return finish(inp, "ADVANCE", nxt, "MASTERED_ADVANCE", false, 7);
  }
  const allMastered = inp.concept_order.every(
    (cid) => (inp.mastery[cid]?.p_bp ?? 0) >= masteredAt);
  if (allMastered) {
    let oldest = inp.concept_order[0];
    let oldestSeq = inp.mastery[oldest]?.last_event_seq ?? 0;
    for (const cid of inp.concept_order) {
      const seq = inp.mastery[cid]?.last_event_seq ?? 0;
      if (seq < oldestSeq || (seq === oldestSeq && cid < oldest)) {
        oldest = cid;
        oldestSeq = seq;
      }
    }
    return finish(inp, "REVISE", oldest, "SLICE_COMPLETE", false, 7);
  }
  const unmet = mostBlockedPrereq(inp);
  if (unmet !== null) {
    return finish(inp, "REMEDIATE", unmet, "BLOCKED_BY_PREREQ", false, 7);
  }
  return finish(inp, "RETRY", target, "STATE_INVALID_FALLBACK", false, 7, true);
}

function mostBlockedPrereq(inp: DecisionInput): string | null {
  const blocked = new Set<string>();
  for (const pres of Object.values(inp.prereqs || {})) {
    for (const pre of pres || []) blocked.add(pre);
  }
  let best: [number, string] | null = null;
  for (const cid of blocked) {
    const p = inp.mastery[cid]?.p_bp ?? 0;
    const key: [number, string] = [p, cid];
    if (best === null || key < best) best = key;
  }
  return best ? best[1] : null;
}

/** Convenience wrapper for the reason string (parity with Python's
 * `_reason_or` via the shipped i18n dict). */
export function reasonText(code: string): string {
  return reasonOr(code);
}
