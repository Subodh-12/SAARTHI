import { useEffect, useState } from "react";
import { api } from "../api/client";
import { listRecentDecisions, listPendingOutbox, listQuarantined, LocalDecision, OutboxEvent } from "../store/db";
import { getInstalledPack } from "../lib/sync";
import { checkStorageBudget } from "../lib/prefetch_scheduler";
import { DecisionTrace } from "../generated/api";
import { t } from "../i18n/or";

type DevTab = "decisions" | "sync" | "pack" | "jobs";

export function DevTraceScreen() {
  const [tab, setTab] = useState<DevTab>("decisions");
  const [decisions, setDecisions] = useState<LocalDecision[]>([]);
  const [trace, setTrace] = useState<DecisionTrace | null>(null);
  const [selectedDecision, setSelectedDecision] = useState<string | null>(null);
  const [pendingOutbox, setPendingOutbox] = useState<OutboxEvent[]>([]);
  const [quarantined, setQuarantined] = useState<any[]>([]);
  const [installedPack, setInstalledPack] = useState<any | null>(null);
  const [storage, setStorage] = useState<{ ok: boolean; freeMb: number }>({ ok: true, freeMb: 0 });
  const [jobsData, setJobsData] = useState<any | null>(null);
  const [diagnostics, setDiagnostics] = useState<any | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    listRecentDecisions(20).then(setDecisions).catch(() => {});
    listPendingOutbox(50).then(setPendingOutbox).catch(() => {});
    listQuarantined().then(setQuarantined).catch(() => {});
    getInstalledPack().then(setInstalledPack).catch(() => {});
    checkStorageBudget().then(setStorage).catch(() => {});

    // Try fetching online diagnostic data if backend reachable
    fetch("/api/v1/diagnostics")
      .then((r) => (r.ok ? r.json() : null))
      .then(setDiagnostics)
      .catch(() => {});

    fetch("/api/v1/admin/jobs")
      .then((r) => (r.ok ? r.json() : null))
      .then(setJobsData)
      .catch(() => {});
  }, []);

  const loadTrace = async (decision_id: string) => {
    setSelectedDecision(decision_id);
    setTrace(null);
    setError("");
    try {
      if (decision_id.startsWith("local_")) {
        setTrace({ decision_id, trace: [] });
      } else {
        const t = await api.getDecisionTrace(decision_id);
        setTrace(t);
      }
    } catch (e: any) {
      setError(e.message || String(e));
    }
  };

  return (
    <div className="space-y-4">
      {/* Dev Navigation Tabs */}
      <div className="flex bg-slate-200 p-1 rounded-xl gap-1 text-xs font-semibold">
        <button
          onClick={() => setTab("decisions")}
          className={`flex-1 py-1.5 rounded-lg transition ${
            tab === "decisions" ? "bg-white text-saarthi-700 shadow-sm" : "text-slate-600 hover:text-slate-900"
          }`}
        >
          {t("dev_trace_title")}
        </button>
        <button
          onClick={() => setTab("sync")}
          className={`flex-1 py-1.5 rounded-lg transition ${
            tab === "sync" ? "bg-white text-saarthi-700 shadow-sm" : "text-slate-600 hover:text-slate-900"
          }`}
        >
          Sync & Outbox ({pendingOutbox.length})
        </button>
        <button
          onClick={() => setTab("pack")}
          className={`flex-1 py-1.5 rounded-lg transition ${
            tab === "pack" ? "bg-white text-saarthi-700 shadow-sm" : "text-slate-600 hover:text-slate-900"
          }`}
        >
          Pack & Storage
        </button>
        <button
          onClick={() => setTab("jobs")}
          className={`flex-1 py-1.5 rounded-lg transition ${
            tab === "jobs" ? "bg-white text-saarthi-700 shadow-sm" : "text-slate-600 hover:text-slate-900"
          }`}
        >
          Jobs & System
        </button>
      </div>

      {/* Tab: Decisions & Trace */}
      {tab === "decisions" && (
        <>
          <div className="card">
            <h2 className="font-semibold mb-2 odia">{t("dev_trace_title")}</h2>
            <div className="text-xs text-slate-500 mb-3">
              {decisions.length} recent decisions (most recent first)
            </div>
            <ul className="text-xs space-y-1 max-h-72 overflow-y-auto">
              {decisions.map((d) => (
                <li key={d.decision_id}>
                  <button
                    className={`text-left w-full p-2 rounded hover:bg-slate-50 ${
                      selectedDecision === d.decision_id ? "bg-saarthi-50 border-l-4 border-saarthi-600" : ""
                    }`}
                    onClick={() => loadTrace(d.decision_id)}
                  >
                    <div className="font-mono text-[10px] text-slate-500">{d.decision_id}</div>
                    <div className="odia font-semibold text-slate-800">
                      {d.action} · {d.target_concept_id} · {d.reason_code}
                    </div>
                    <div className="text-[10px] text-slate-500">
                      {d.produced_by} · {d.network} · {new Date(d.created_at).toLocaleTimeString()}
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {error && (
            <div className="card">
              <div className="banner-err text-sm px-3 py-2 rounded">{error}</div>
            </div>
          )}

          {trace && (
            <div className="card">
              <h3 className="font-semibold mb-2 text-sm">Trace: {trace.decision_id}</h3>
              {trace.trace.length === 0 ? (
                <p className="text-sm text-slate-500 odia">
                  {"ଏହି ନିଷ୍ପତ୍ତି ସ୍ଥାନୀୟ ଇଞ୍ଜିନରୁ — ଟ୍ରେସ ନାହିଁ।"}
                </p>
              ) : (
                <ol className="text-xs space-y-2">
                  {trace.trace.map((step, i) => (
                    <li key={step.step_id} className="border-l-2 border-saarthi-300 pl-3">
                      <div className="font-mono text-[10px] text-slate-500">
                        #{i + 1} {step.node} {step.tool && `· ${step.tool}`} {step.provider && `· ${step.provider}`}
                      </div>
                      <div className="odia">
                        Status: <b>{step.status}</b> · {step.duration_ms}ms
                        {step.error_code && ` · ${step.error_code}`}
                        {step.fallback && ` · fallback=${step.fallback}`}
                      </div>
                      {step.input_summary && Object.keys(step.input_summary).length > 0 && (
                        <div className="text-[10px] text-slate-500 mt-1 font-mono">
                          in: {JSON.stringify(step.input_summary)}
                        </div>
                      )}
                      {step.output_summary && Object.keys(step.output_summary).length > 0 && (
                        <div className="text-[10px] text-slate-500 font-mono">
                          out: {JSON.stringify(step.output_summary)}
                        </div>
                      )}
                    </li>
                  ))}
                </ol>
              )}
            </div>
          )}
        </>
      )}

      {/* Tab: Sync & Outbox */}
      {tab === "sync" && (
        <div className="space-y-4">
          <div className="card">
            <h3 className="font-semibold text-sm mb-2">Pending Outbox Events ({pendingOutbox.length})</h3>
            {pendingOutbox.length === 0 ? (
              <p className="text-xs text-slate-500">Outbox is clean. All local events synced to server.</p>
            ) : (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {pendingOutbox.map((evt) => (
                  <div key={evt.event_id} className="p-2 border rounded text-xs bg-slate-50">
                    <div className="flex justify-between items-center">
                      <span className="font-mono font-bold text-saarthi-700">seq: {evt.seq}</span>
                      <span className="text-[10px] bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded">
                        {evt.outbox_state}
                      </span>
                    </div>
                    <div className="font-semibold mt-1">{evt.event_type}</div>
                    <div className="text-[10px] text-slate-500 font-mono">id: {evt.event_id}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card">
            <h3 className="font-semibold text-sm mb-2 text-rose-800">Quarantine & Dead Letters ({quarantined.length})</h3>
            {quarantined.length === 0 ? (
              <p className="text-xs text-slate-500">No quarantined events. Ingest integrity is nominal.</p>
            ) : (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {quarantined.map((q, idx) => (
                  <div key={idx} className="p-2 border border-rose-200 bg-rose-50 rounded text-xs">
                    <div className="font-bold text-rose-900">{q.event_type || "EVENT"}</div>
                    <div className="text-xs text-rose-700 mt-1">Reason: {q.reason || "Validation failure"}</div>
                    <div className="text-[10px] font-mono text-slate-600 mt-1">seq: {q.seq} · id: {q.event_id}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab: Pack & Storage */}
      {tab === "pack" && (
        <div className="space-y-4">
          <div className="card space-y-2 text-xs">
            <h3 className="font-semibold text-sm text-slate-800">Active Installed Pack</h3>
            {installedPack ? (
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg space-y-1">
                <div className="flex justify-between">
                  <span className="font-semibold text-emerald-900">Pack ID:</span>
                  <span className="font-mono">{installedPack.pack_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-semibold text-emerald-900">Version:</span>
                  <span>{installedPack.version}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-semibold text-emerald-900">Installed At:</span>
                  <span>{new Date(installedPack.installed_at).toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-semibold text-emerald-900">Integrity:</span>
                  <span className="font-semibold text-emerald-700">✓ SHA-256 Verified</span>
                </div>
                {installedPack.archive_sha256 && (
                  <div className="mt-1">
                    <span className="font-semibold text-emerald-900">Checksum:</span>
                    <div className="font-mono text-[9px] text-slate-600 break-all">{installedPack.archive_sha256}</div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-800">
                No offline pack currently installed. Local lessons will use bundled fallbacks.
              </div>
            )}
          </div>

          <div className="card space-y-2 text-xs">
            <h3 className="font-semibold text-sm text-slate-800">Device Storage Budget</h3>
            <div className="p-3 bg-slate-50 border rounded-lg space-y-1">
              <div className="flex justify-between items-center">
                <span>Free Storage:</span>
                <span className="font-bold text-sm">{storage.freeMb} MB</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Prefetch Allowed (&ge;150 MB):</span>
                <span className={`font-bold ${storage.ok ? "text-emerald-600" : "text-rose-600"}`}>
                  {storage.ok ? "✓ Allowed" : "✗ Budget Low"}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab: Jobs & System */}
      {tab === "jobs" && (
        <div className="space-y-4">
          <div className="card space-y-2 text-xs">
            <h3 className="font-semibold text-sm text-slate-800">Background Worker Jobs (PostgreSQL)</h3>
            {jobsData ? (
              <div className="space-y-3">
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="p-2 bg-slate-100 rounded">
                    <div className="text-lg font-bold">{jobsData.counts?.queued ?? 0}</div>
                    <div className="text-[10px] text-slate-500">Queued</div>
                  </div>
                  <div className="p-2 bg-emerald-50 rounded text-emerald-800">
                    <div className="text-lg font-bold">{jobsData.counts?.succeeded ?? 0}</div>
                    <div className="text-[10px]">Succeeded</div>
                  </div>
                  <div className="p-2 bg-rose-50 rounded text-rose-800">
                    <div className="text-lg font-bold">{jobsData.counts?.dead ?? 0}</div>
                    <div className="text-[10px]">Dead</div>
                  </div>
                </div>
                {jobsData.dead_jobs && jobsData.dead_jobs.length > 0 && (
                  <div className="border border-rose-200 rounded p-2 bg-rose-50">
                    <div className="font-bold text-rose-900 mb-1">Dead Jobs:</div>
                    {jobsData.dead_jobs.map((j: any) => (
                      <div key={j.job_id} className="text-[10px] font-mono text-rose-700">
                        {j.type} [{j.job_id}] — attempts: {j.attempts}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <p className="text-slate-500">Backend jobs status unavailable (offline or worker detached).</p>
            )}
          </div>

          <div className="card space-y-2 text-xs">
            <h3 className="font-semibold text-sm text-slate-800">Runtime Diagnostics</h3>
            {diagnostics ? (
              <div className="bg-slate-50 p-2 rounded font-mono text-[10px] space-y-1">
                <div>Environment: {diagnostics.environment || "production"}</div>
                <div>App Version: {diagnostics.app_version || "2.0.0"}</div>
                <div>Storage Backend: {diagnostics.storage_backend || "local"}</div>
                <div>Persistence: {diagnostics.persistence_backend || "postgres"}</div>
              </div>
            ) : (
              <p className="text-slate-500">Backend diagnostics unavailable while offline.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
