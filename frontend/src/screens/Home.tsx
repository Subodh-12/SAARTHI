import { useEffect, useState } from "react";
import { api, SaarthiApiError } from "../api/client";
import {
  listRecentDecisions, LocalDecision, getMasterySnapshot, getBloomMasterySnapshot,
  LocalBloomMastery, recordDecision,
} from "../store/db";
import { decide, RULESET } from "../engine/decide";
import {
  Action, BackgroundAction, Decision, MasteryRecord, NetworkState,
} from "../generated/api";
import { t } from "../i18n/or";
import { getInstalledPack } from "../lib/sync";
import { bloomLabel, bloomDescription, isValidBloomLevel, BloomLevel } from "../engine/bloom";
import { scheduleBackgroundPrefetch } from "../lib/prefetch_scheduler";

interface Props {
  profile: { learner_id: string; device_id: string; display_label: string };
  network: NetworkState;
  onNavigate: (t: "home" | "lesson" | "doubt" | "packs" | "dev") => void;
  outboxDepth: number;
}

export function HomeScreen({ profile, network, onNavigate, outboxDepth }: Props) {
  const [decision, setDecision] = useState<Decision | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [mastery, setMastery] = useState<MasteryRecord[]>([]);
  const [bloomMastery, setBloomMastery] = useState<LocalBloomMastery[]>([]);
  const [recentDecisions, setRecentDecisions] = useState<LocalDecision[]>([]);

  useEffect(() => {
    void loadHome();
  }, []);

  async function loadHome() {
    setLoading(true); setError("");
    try {
      if (network === NetworkState.OFFLINE) {
        // Local decision engine (pure, no network) — v2 input shape with
        // integer basis-point mastery.
        const snap = await getMasterySnapshot();
        const masteryDict: Record<string, { p_bp: number; attempts: number; correct: number }> = {};
        for (const m of snap) masteryDict[m.concept_id] = {
          p_bp: m.p_bp, attempts: m.attempts, correct: m.correct,
        };
        // Concept order from installed pack
        const pack = await getInstalledPack();
        let concept_order: string[] = [];
        const chapter_for_concept: Record<string, string> = {};
        const prereqs: Record<string, string[]> = {};
        let packId: string | undefined;
        if (pack) {
          const m = JSON.parse(pack.manifest_json);
          packId = m.manifest?.pack_id ?? pack.pack_id;
          concept_order = m.concepts.map((c: any) => c.concept_id);
          for (const c of m.concepts) {
            chapter_for_concept[c.concept_id] = c.chapter_id;
            prereqs[c.concept_id] = c.prerequisites || [];
          }
        }
        const recent = await listRecentDecisions(10);
        const out = decide({
          trigger_event_type: "SESSION_STARTED",
          trigger_concept_id: null,
          trigger_correct: null,
          mastery: masteryDict,
          recent_events: recent.map((d, i) => ({
            seq: i + 1, event_type: "DECISION_MADE_LOCAL",
            concept_id: d.target_concept_id, correct: null,
            p_bp_after: null, last_action: d.action,
          })),
          prereqs, env_network: network,
          installed_pack_versions: pack && packId
            ? { [packId]: parseInt(pack.version.split(".")[0], 10) || 1 } : {},
          required_pack_for_concept: Object.fromEntries(
            concept_order.map((cid) => [cid, packId || ""])),
          ruleset_version: RULESET.ruleset_version,
          concept_order,
          chapter_id_for_concept: chapter_for_concept,
        });
        const localDecision: Decision = {
          decision_id: `local_${Date.now()}`,
          learner_id: profile.learner_id,
          ruleset_version: RULESET.ruleset_version,
          target_concept_id: out.target_concept_id,
          action: out.action as Action,
          delivery_mode: out.delivery_mode as any,
          background_actions: out.background_actions as any,
          reason_code: out.reason_code,
          reason_or: out.reason_code,
          needs_help: out.needs_help,
          chapter_id: (chapter_for_concept[out.target_concept_id] || ""),
          network, produced_by: "local_engine", source: "local",
          created_at: Date.now(),
          suggested_chunk_id: null,
          suggested_question_id: null,
        };
        setDecision(localDecision);
        await recordDecision({ ...localDecision, trace_json: "[]" } as any);
      } else {
        const d = await api.nextDecision(network);
        setDecision(d);
        await recordDecision({ ...d, trace_json: "[]" } as any);
        if (d?.background_actions?.includes(BackgroundAction.PREFETCH)) {
          void scheduleBackgroundPrefetch({ network, targetConceptId: d.target_concept_id });
        }
      }
      setMastery((await getMasterySnapshot()) as any);
      setBloomMastery(await getBloomMasterySnapshot());
      setRecentDecisions(await listRecentDecisions(5));
    } catch (e: any) {
      setError(e instanceof SaarthiApiError ? e.message : (e.message || String(e)));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="card odia">{t("loading")}</div>;
  }
  if (error) {
    return (
      <div className="card">
        <div className="banner-err text-sm px-3 py-2 rounded mb-3">{error}</div>
        <button className="btn-secondary w-full" onClick={loadHome}>{t("retry")}</button>
      </div>
    );
  }
  if (!decision) {
    return <div className="card odia">{t("empty")}</div>;
  }

  return (
    <div className="space-y-4">
      <div className="card">
        <div className="text-xs text-slate-500 mb-1 odia">{t("home_next")}</div>
        <div className="text-xl font-bold mb-2">
          <ActionBadge action={decision.action} />
          <span className="ml-2 odia">{decision.reason_or}</span>
        </div>
        <div className="text-xs text-slate-600 odia flex items-center flex-wrap gap-1">
          <span>{t("nav_lesson")}: {decision.chapter_id} · {decision.target_concept_id}</span>
          {decision.target_bloom_level && isValidBloomLevel(decision.target_bloom_level) && (
            <span
              className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs bg-indigo-100 text-indigo-800 font-semibold"
              title={bloomDescription(decision.target_bloom_level as BloomLevel, "or")}
            >
              🎯 ଲକ୍ଷ୍ୟ: {bloomLabel(decision.target_bloom_level as BloomLevel, "or")} ({bloomLabel(decision.target_bloom_level as BloomLevel, "en")})
            </span>
          )}
        </div>
        <div className="text-xs text-slate-500 mt-1 odia">
          ({decision.produced_by === "local_engine" ? "ସ୍ଥାନୀୟ" : "ସର୍ଭର"} ନିଷ୍ପତ୍ତି)
        </div>
        {decision.needs_help && (
          <div className="banner-warn text-sm px-3 py-2 rounded mt-2 odia">
            {t("ask_teacher_prompt")}
          </div>
        )}
        <button className="btn-primary w-full mt-4"
                onClick={() => onNavigate("lesson")}>
          {t("lesson_read")}
        </button>
      </div>

      <div className="card">
        <h3 className="font-semibold mb-2 odia">{t("home_mastered")}</h3>
        {mastery.length === 0 ? (
          <p className="text-sm text-slate-500 odia">{t("empty")}</p>
        ) : (
          <div className="space-y-3">
            {mastery.map((m) => {
              const bms = bloomMastery.filter((bm) => bm.concept_id === m.concept_id);
              return (
                <div key={m.concept_id} className="border-b border-slate-100 pb-2 last:border-b-0 last:pb-0">
                  <div className="flex justify-between text-sm font-medium">
                    <span>{m.concept_id}</span>
                    <span>{m.band} · {Math.round(m.p_bp / 100)}%</span>
                  </div>
                  {bms.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1.5">
                      {bms.map((bm) => {
                        const lvl = bm.bloom_level as BloomLevel;
                        const valid = isValidBloomLevel(lvl);
                        return (
                          <span
                            key={bm.bloom_level}
                            className={`text-xs px-1.5 py-0.5 rounded font-mono ${
                              bm.band === "mastered"
                                ? "bg-emerald-100 text-emerald-800"
                                : bm.band === "partial"
                                ? "bg-amber-100 text-amber-800"
                                : "bg-slate-100 text-slate-600"
                            }`}
                            title={valid ? bloomDescription(lvl, "or") : undefined}
                          >
                            {valid ? bloomLabel(lvl, "or") : bm.bloom_level}: {Math.round(bm.p_bp / 100)}%
                          </span>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="card">
        <h3 className="font-semibold mb-2 odia">{t("home_outbox")}</h3>
        <div className="text-2xl font-bold">{outboxDepth}</div>
        <div className="text-xs text-slate-500 odia">{t("state_syncing")}</div>
        {network !== NetworkState.OFFLINE && outboxDepth > 0 && (
          <button className="btn-secondary mt-3 text-sm" onClick={async () => {
            const { trySyncNow } = await import("../lib/sync");
            await trySyncNow();
            await loadHome();
          }}>
            {t("state_syncing")}
          </button>
        )}
      </div>

      {recentDecisions.length > 0 && (
        <div className="card">
          <h3 className="font-semibold mb-2 odia">{"ଶେଷ ନିଷ୍ପତ୍ତି"}</h3>
          <ul className="text-xs space-y-1 text-slate-600">
            {recentDecisions.map((d, i) => (
              <li key={i}>{new Date(d.created_at).toLocaleString()} · {d.action} · {d.target_concept_id}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function ActionBadge({ action }: { action: Action }) {
  const map: Record<Action, string> = {
    [Action.REMEDIATE]: "🔁 ପୁନଃଶିକ୍ଷ",
    [Action.RETRY]: "✋ ପୁଣି ଚେଷ୍ଟା",
    [Action.REVISE]: "📖 ପୁନଃବିବରଣ",
    [Action.ADVANCE]: "🚀 ଆଗକୁ ଯାଅ",
  };
  return <span className="odia inline-block px-2 py-1 bg-saarthi-100 text-saarthi-800 rounded">{map[action]}</span>;
}
