import { useEffect, useState } from "react";
import { api, SaarthiApiError } from "../api/client";
import {
  listRecentDecisions, LocalDecision, getMasterySnapshot, recordDecision,
} from "../store/db";
import { decide, RULESET } from "../engine/decide";
import {
  Action, Decision, MasteryRecord, NetworkState,
} from "../generated/api";
import { t } from "../i18n/or";
import { getInstalledPack } from "../lib/sync";

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
      }
      setMastery((await getMasterySnapshot()) as any);
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
        <div className="text-xs text-slate-600 odia">
          {t("nav_lesson")}: {decision.chapter_id} · {decision.target_concept_id}
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
          <ul className="text-sm space-y-1">
            {mastery.map((m) => (
              <li key={m.concept_id} className="flex justify-between">
                <span>{m.concept_id}</span>
                <span>{m.band} · {Math.round(m.p_bp / 100)}%</span>
              </li>
            ))}
          </ul>
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
