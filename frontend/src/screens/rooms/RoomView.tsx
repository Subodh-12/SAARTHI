// Room view: shared chat + Doubt Relay + Find the Mistake.
// Realtime is a polling fallback (2s) — clean and testable, no WS in this app.
import { useCallback, useEffect, useRef, useState } from "react";
import { api, SaarthiApiError } from "../../api/client";
import type { GameState, RelayState, RoomDetail } from "./types";

interface Props {
  roomId: string;
  profile: { learner_id: string; display_label: string };
  onExit: () => void;
  onLeft: () => void;
}

const fmtTime = (ms: number) =>
  new Date(ms).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

const errText = (e: unknown, fallback: string) =>
  e instanceof SaarthiApiError
    ? (e.error_code === "not_a_member" ? "You are not a member of this room."
       : e.error_code === "room_not_found" ? "This room no longer exists."
       : `${fallback} (${e.error_code ?? e.message})`)
    : fallback;

type Panel = "chat" | "activity" | "history";

export function RoomView({ roomId, profile, onExit, onLeft }: Props) {
  const [detail, setDetail] = useState<RoomDetail | null>(null);
  const [error, setError] = useState("");
  const [fatal, setFatal] = useState("");
  const [panel, setPanel] = useState<Panel>("chat");
  const [activeRelayId, setActiveRelayId] = useState<string | null>(null);
  const [activeGameId, setActiveGameId] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const d = await api.getRoom(roomId);
      setDetail(d); setError("");
      // Track the newest open activity so the activity panel follows it.
      const acts = await api.listRoomActivities(roomId);
      const open = acts.activities.find(
        (a) => a.status !== "completed" && a.activity_type === "doubt_relay");
      if (open) setActiveRelayId(open.activity_id);
      const openGame = acts.activities.find(
        (a) => a.status !== "completed" && a.activity_type === "find_the_mistake");
      if (openGame) setActiveGameId(openGame.activity_id);
    } catch (e) {
      setFatal(errText(e, "Could not load room."));
    }
  }, [roomId]);

  useEffect(() => {
    void refresh();
    // Polling fallback for realtime + presence heartbeat.
    const i = setInterval(() => {
      void api.roomHeartbeat(roomId).catch(() => {});
      void refresh();
    }, 3000);
    return () => clearInterval(i);
  }, [roomId, refresh]);

  if (fatal) {
    return (
      <div className="space-y-3">
        <div className="banner-err border rounded-lg px-4 py-3 text-sm">{fatal}</div>
        <button className="btn-secondary" onClick={onExit}>← Back to rooms</button>
      </div>
    );
  }
  if (!detail) return <div className="card text-sm text-slate-500">Loading room…</div>;

  const { room } = detail;
  const expiresIn = room.expires_at ? room.expires_at - Date.now() : null;

  const leave = async () => {
    try { await api.leaveRoom(roomId); } catch { /* best effort */ }
    onLeft();
  };

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="card">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <button className="text-slate-400 hover:text-slate-700"
                      onClick={onExit} aria-label="Back">←</button>
              <h2 className="font-bold truncate">{room.title}</h2>
            </div>
            <div className="text-xs text-slate-500">
              {room.chapter_title || room.subject}
              {room.learning_topic ? ` · ${room.learning_topic}` : ""}
              {" · "}
              <span className="font-mono">{room.room_code}</span>
            </div>
          </div>
          <button className="text-xs text-rose-600 hover:underline shrink-0"
                  onClick={leave}>Leave room</button>
        </div>
        <div className="flex flex-wrap items-center gap-2 mt-2">
          {room.members.map((m) => (
            <span key={m.learner_id}
                  className={`inline-flex items-center gap-1 text-xs rounded-full px-2 py-0.5 border
                    ${m.online ? "bg-emerald-50 border-emerald-200 text-emerald-800"
                               : "bg-slate-50 border-slate-200 text-slate-500"}`}>
              {m.role === "host" ? "👑 " : ""}{m.display_label}
            </span>
          ))}
          <span className="text-xs text-slate-400">
            {room.member_count}/{room.capacity}
          </span>
        </div>
        {expiresIn !== null && expiresIn > 0 && (
          <p className="text-xs text-amber-700 mt-2">
            ⏳ Everyone left — room is deleted in {Math.round(expiresIn / 60000)} min
            unless a member rejoins.
          </p>
        )}
      </div>

      {/* Panel tabs */}
      <div className="flex gap-2">
        {([["chat", "Chat"], ["activity", "Activity"], ["history", "History & summary"]] as [Panel, string][])
          .map(([p, label]) => (
          <button key={p}
                  className={`px-3 py-1.5 rounded-lg text-sm font-semibold border ${
                    panel === p ? "bg-saarthi-600 text-white border-saarthi-600"
                                : "bg-white text-slate-700 border-slate-300"}`}
                  onClick={() => setPanel(p)}>
            {label}
          </button>
        ))}
      </div>
      {error && <div className="banner-err border rounded-lg px-3 py-2 text-xs">{error}</div>}

      {panel === "chat" && <ChatPanel roomId={roomId} detail={detail}
                                      onRefresh={refresh} />}
      {panel === "activity" && (
        <ActivityPanel roomId={roomId} learnerId={profile.learner_id}
                       relayId={activeRelayId} gameId={activeGameId}
                       onChanged={refresh}
                       onOpenRelay={setActiveRelayId} onOpenGame={setActiveGameId} />
      )}
      {panel === "history" && <HistoryPanel detail={detail} />}
    </div>
  );
}

// ------------------------------------------------------------------ //
// Chat
// ------------------------------------------------------------------ //
function ChatPanel({ roomId, detail, onRefresh }: {
  roomId: string; detail: RoomDetail; onRefresh: () => void;
}) {
  const [text, setText] = useState("");
  const [replyTo, setReplyTo] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottom.current?.scrollIntoView({ block: "end" });
  }, [detail.messages.length]);

  const send = async () => {
    if (!text.trim() || busy) return;
    setBusy(true);
    try {
      await api.postRoomMessage(roomId, text.trim(), replyTo ?? undefined);
      setText(""); setReplyTo(null);
      await onRefresh();
    } catch (e) {
      alert(errText(e, "Message failed"));
    } finally { setBusy(false); }
  };

  const byId = new Map(detail.messages.map((m) => [m.message_id, m]));

  return (
    <div className="card flex flex-col">
      <div className="max-h-80 overflow-y-auto space-y-2 pr-1">
        {detail.messages.length === 0 && (
          <p className="text-sm text-slate-400 text-center py-6">
            No messages yet — say namaskar!
          </p>
        )}
        {detail.messages.map((m) => {
          if (m.sender_kind === "system") {
            return (
              <div key={m.message_id}
                   className="text-xs text-slate-500 text-center py-1">
                {m.body}
                <span className="ml-1 opacity-60">{fmtTime(m.created_at)}</span>
              </div>
            );
          }
          if (m.sender_kind === "karana") {
            return (
              <div key={m.message_id}
                   className="rounded-xl border border-violet-200 bg-violet-50 px-3 py-2">
                <div className="text-xs font-bold text-violet-800 mb-0.5">
                  🤖 Karana <span className="font-normal opacity-60">(demo agent · simulated)</span>
                  <span className="ml-1 opacity-60">{fmtTime(m.created_at)}</span>
                </div>
                <p className="text-sm text-violet-950 whitespace-pre-wrap">{m.body}</p>
              </div>
            );
          }
          return (
            <div key={m.message_id} className="group">
              {m.reply_to && byId.get(m.reply_to) && (
                <div className="text-[11px] text-slate-400 border-l-2 border-slate-300
                                pl-2 mb-0.5 truncate">
                  ↩ {byId.get(m.reply_to)!.sender_label || "System"}:{" "}
                  {byId.get(m.reply_to)!.body.slice(0, 60)}
                </div>
              )}
              <div className="rounded-xl bg-white border border-slate-200 px-3 py-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-700">
                    {m.sender_label || "Member"}
                  </span>
                  <span className="text-[10px] text-slate-400 opacity-0 group-hover:opacity-100">
                    <button className="underline" onClick={() => setReplyTo(m.message_id)}>
                      reply
                    </button>
                  </span>
                </div>
                <p className="text-sm whitespace-pre-wrap">{m.body}</p>
                <span className="text-[10px] text-slate-400">{fmtTime(m.created_at)}</span>
              </div>
            </div>
          );
        })}
        <div ref={bottom} />
      </div>
      {replyTo && (
        <div className="text-xs text-slate-500 mt-2">
          Replying to message{" "}
          <button className="underline" onClick={() => setReplyTo(null)}>cancel</button>
        </div>
      )}
      <div className="flex gap-2 mt-3">
        <input className="input flex-1" placeholder="Type a message…"
               value={text} onChange={(e) => setText(e.target.value)}
               onKeyDown={(e) => e.key === "Enter" && send()} />
        <button className="btn-primary" disabled={busy || !text.trim()} onClick={send}>
          Send
        </button>
      </div>
    </div>
  );
}

// ------------------------------------------------------------------ //
// Doubt Relay + Find the Mistake
// ------------------------------------------------------------------ //
function ActivityPanel({ roomId, learnerId, relayId, gameId, onChanged,
                         onOpenRelay, onOpenGame }: {
  roomId: string; learnerId: string;
  relayId: string | null; gameId: string | null;
  onChanged: () => void;
  onOpenRelay: (id: string | null) => void;
  onOpenGame: (id: string | null) => void;
}) {
  const [starting, setStarting] = useState<"relay" | "game" | null>(null);

  const startRelay = async () => {
    const q = prompt("Post your doubt — the group will answer independently first:");
    if (!q || q.trim().length < 3) return;
    setStarting("relay");
    try {
      const st = await api.startRelay(roomId, q.trim());
      onOpenRelay(st.activity_id);
      onChanged();
    } catch (e) { alert(errText(e, "Could not start relay")); }
    finally { setStarting(null); }
  };

  const startGame = async () => {
    setStarting("game");
    try {
      const st = await api.startGame(roomId);
      onOpenGame(st.activity_id);
      onChanged();
    } catch (e) { alert(errText(e, "Could not start game")); }
    finally { setStarting(null); }
  };

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <button className="btn-primary flex-1" disabled={starting !== null}
                onClick={startRelay}>
          {starting === "relay" ? "…" : "🔥 Start Doubt Relay"}
        </button>
        <button className="btn-secondary flex-1" disabled={starting !== null}
                onClick={startGame}>
          {starting === "game" ? "…" : "🕵️ Find the Mistake"}
        </button>
      </div>
      {relayId && <RelayCard roomId={roomId} activityId={relayId} learnerId={learnerId}
                             onChanged={onChanged} />}
      {gameId && <GameCard roomId={roomId} activityId={gameId} onChanged={onChanged} />}
    </div>
  );
}

const STATUS_LABEL: Record<string, string> = {
  collecting: "Collecting independent answers",
  revealed: "Answers revealed",
  followup: "Karana follow-up — discuss!",
  discussion: "Group discussion",
  verification: "Verification question",
  completed: "Completed",
};

function RelayCard({ roomId, activityId, learnerId, onChanged }: {
  roomId: string; activityId: string; learnerId: string; onChanged: () => void;
}) {
  const [state, setState] = useState<RelayState | null>(null);
  const [answer, setAnswer] = useState("");
  const [selected, setSelected] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      setState(await api.getRelay(roomId, activityId));
      setError("");
    } catch (e) { setError(errText(e, "Could not load relay")); }
  }, [roomId, activityId]);

  useEffect(() => {
    void load();
    const i = setInterval(load, 3000);
    return () => clearInterval(i);
  }, [load]);

  if (error) return <div className="banner-err border rounded-lg px-3 py-2 text-xs">{error}</div>;
  if (!state) return <div className="card text-sm text-slate-500">Loading relay…</div>;

  const act = (fn: () => Promise<RelayState>) => async () => {
    setBusy(true);
    try { setState(await fn()); onChanged(); }
    catch (e) { alert(errText(e, "Action failed")); }
    finally { setBusy(false); }
  };

  const needsMyAnswer = !state.my_submission && state.status === "collecting";
  const revealed = state.status !== "collecting";

  return (
    <div className="card border-l-4 border-l-amber-500 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-bold uppercase tracking-wide text-amber-700">
          Doubt Relay
        </span>
        <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
          {STATUS_LABEL[state.status] ?? state.status}
        </span>
      </div>
      <p className="font-semibold">{state.question}</p>

      {/* Step 1–2: independent submission */}
      {state.status === "collecting" && (
        <>
          <p className="text-xs text-slate-500">
            Submitted: {state.submission_count}/{state.eligible_count} —
            answers stay hidden until reveal.
          </p>
          <div className="space-y-1">
            {state.submissions.map((s) => (
              <div key={s.learner_id} className="text-xs text-slate-600 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
                {s.display_label} submitted
              </div>
            ))}
          </div>
          {needsMyAnswer ? (
            <div className="space-y-2">
              <textarea className="input min-h-20" placeholder="Write YOUR answer first — you won't see others' until everyone submits or the host reveals."
                        value={answer} onChange={(e) => setAnswer(e.target.value)} />
              <button className="btn-primary w-full" disabled={busy || !answer.trim()}
                      onClick={act(async () => {
                        const st = await api.submitRelay(roomId, activityId, answer.trim());
                        setAnswer("");
                        return st;
                      })}>
                Submit my answer
              </button>
            </div>
          ) : (
            <div className="text-xs bg-slate-50 border border-slate-200 rounded-lg p-2">
              ✅ You submitted. Waiting for others or reveal.
              <button className="underline ml-1" disabled={busy}
                      onClick={act(() => api.revealRelay(roomId, activityId))}>
                Reveal now
              </button>
            </div>
          )}
        </>
      )}

      {/* Step 3–4: revealed answers + demo decision */}
      {revealed && (
        <div className="space-y-2">
          <div className="text-xs font-semibold">
            Answers ({state.pattern && (
              <span className={
                state.pattern === "agree" ? "text-emerald-700"
                : state.pattern === "disagree" ? "text-rose-700" : "text-amber-700"}>
                group pattern: {state.pattern}
              </span>
            )}):
          </div>
          {state.submissions.map((s) => (
            <div key={s.learner_id}
                 className="text-sm rounded-lg bg-white border border-slate-200 px-2 py-1.5">
              <span className="text-xs font-semibold text-slate-600">
                {s.display_label}:
              </span> {s.content ?? "—"}
            </div>
          ))}
          {state.followup && (
            <div className="rounded-xl border border-violet-200 bg-violet-50 px-3 py-2">
              <div className="text-xs font-bold text-violet-800 mb-0.5">
                🤖 Karana (demo agent · simulated)
              </div>
              <p className="text-sm text-violet-950">{state.followup.text}</p>
            </div>
          )}
          {state.status === "followup" && (
            <button className="btn-secondary w-full text-sm" disabled={busy}
                    onClick={act(() => api.advanceRelay(roomId, activityId, "discussion"))}>
              We discussed it → show explanation
            </button>
          )}
          {state.explanation && (state.status === "discussion"
                                 || state.status === "verification"
                                 || state.status === "completed") && (
            <div className="rounded-xl border border-violet-200 bg-violet-50 px-3 py-2">
              <div className="text-xs font-bold text-violet-800 mb-0.5">
                🤖 Karana explanation (demo agent · simulated)
              </div>
              <p className="text-sm text-violet-950">{state.explanation}</p>
            </div>
          )}
          {(state.status === "discussion" || state.status === "followup") &&
           state.verification && (
            <button className="btn-primary w-full text-sm" disabled={busy}
                    onClick={act(() => api.advanceRelay(roomId, activityId, "verification"))}>
              Start verification question
            </button>
          )}
        </div>
      )}

      {/* Step 7: verification */}
      {state.status === "verification" && state.verification && (
        <div className="space-y-2 border-t pt-3">
          <p className="text-sm font-semibold">
            ✅ Fresh verification question (your result stays private):
          </p>
          <p className="text-sm">{state.verification.question}</p>
          {state.verification.options.map((o, i) => (
            <button key={i}
                    className={`option-btn text-sm ${
                      selected === i ? "option-selected" : ""}`}
                    onClick={() => setSelected(i)}>
              {String.fromCharCode(65 + i)}. {o}
            </button>
          ))}
          <button className="btn-primary w-full text-sm"
                  disabled={busy || selected === null || !!state.verification_result}
                  onClick={act(() => api.verifyRelay(roomId, activityId, selected!))}>
            Submit answer
          </button>
          {state.verification_result && (
            <p className={`text-sm font-semibold ${
              state.verification_result.correct
                ? "text-emerald-700" : "text-rose-700"}`}>
              {state.verification_result.correct
                ? "✅ Correct — nice work!" : "❌ Not quite — revisit the explanation."}
            </p>
          )}
        </div>
      )}

      {/* Step 8: completed */}
      {state.status === "completed" && (
        <p className="text-sm text-emerald-700 font-semibold">
          ✅ Session complete — summary stored in room history.
          {state.verification?.group &&
            ` Group verification: ${state.verification.group.correct}/${state.verification.group.total} correct.`}
        </p>
      )}

      {/* Demo-agent decision trace */}
      {state.trace.length > 0 && (
        <details className="text-xs text-slate-500">
          <summary className="cursor-pointer">
            Demo-agent decision trace (deterministic, simulated)
          </summary>
          <ul className="mt-1 space-y-0.5 list-disc list-inside">
            {state.trace.map((t, i) => (
              <li key={i}><b>{t.step}</b>: {t.detail}</li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}

function GameCard({ roomId, activityId, onChanged }: {
  roomId: string; activityId: string; onChanged: () => void;
}) {
  const [state, setState] = useState<GameState | null>(null);
  const [line, setLine] = useState("");
  const [reasoning, setReasoning] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try { setState(await api.getGame(roomId, activityId)); }
    catch { /* transient */ }
  }, [roomId, activityId]);

  useEffect(() => {
    void load();
    const i = setInterval(load, 3000);
    return () => clearInterval(i);
  }, [load]);

  if (!state?.problem) return <div className="card text-sm text-slate-500">Loading game…</div>;

  const act = (fn: () => Promise<GameState>) => async () => {
    setBusy(true);
    try { setState(await fn()); onChanged(); }
    catch (e) { alert(errText(e, "Action failed")); }
    finally { setBusy(false); }
  };
  const revealed = state.status !== "collecting";

  return (
    <div className="card border-l-4 border-l-teal-500 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-bold uppercase tracking-wide text-teal-700">
          Find the Mistake
        </span>
        <span className="text-xs px-2 py-0.5 rounded-full bg-teal-100 text-teal-800">
          {STATUS_LABEL[state.status] ?? state.status}
        </span>
      </div>
      <p className="font-semibold">{state.problem.title}</p>
      <ol className="text-sm space-y-1 list-decimal list-inside bg-slate-50 border
                     border-slate-200 rounded-lg p-2">
        {state.problem.lines.map((l, i) => (
          <li key={i}>{l}</li>
        ))}
      </ol>
      <p className="text-xs text-slate-500">
        One line contains a seeded error. Submitted: {state.submission_count}/{state.eligible_count}.
        Reasoning counts more than speed.
      </p>

      {state.status === "collecting" && !state.my_submission && (
        <div className="space-y-2">
          <input className="input" placeholder='Which line is wrong? (e.g. "Line 2")'
                 value={line} onChange={(e) => setLine(e.target.value)} />
          <textarea className="input min-h-16" placeholder="Explain your reasoning…"
                    value={reasoning} onChange={(e) => setReasoning(e.target.value)} />
          <button className="btn-primary w-full" disabled={busy || !line.trim()}
                  onClick={act(async () => {
                    const st = await api.submitGame(roomId, activityId,
                                                   line.trim(), reasoning.trim());
                    setLine(""); setReasoning("");
                    return st;
                  })}>
            Submit my finding
          </button>
        </div>
      )}
      {state.status === "collecting" && state.my_submission && (
        <div className="text-xs bg-slate-50 border border-slate-200 rounded-lg p-2">
          ✅ You submitted. Waiting for others.
          <button className="underline ml-1" disabled={busy}
                  onClick={act(() => api.revealGame(roomId, activityId))}>
            Reveal now
          </button>
        </div>
      )}

      {revealed && state.expected && (
        <div className="space-y-2">
          <div className="text-sm rounded-lg bg-white border border-slate-200 px-2 py-1.5">
            <b>Expected answer:</b> {state.expected.answer}
          </div>
          <div className="rounded-xl border border-violet-200 bg-violet-50 px-3 py-2">
            <div className="text-xs font-bold text-violet-800 mb-0.5">
              🤖 Karana (demo agent · simulated)
            </div>
            <p className="text-sm text-violet-950">{state.expected.explanation}</p>
          </div>
          {state.group_stats && (
            <p className="text-xs text-slate-500">
              {state.group_stats.found}/{state.group_stats.total} found the error;
              {" "}{state.group_stats.reasoned}/{state.group_stats.total} gave reasoning.
            </p>
          )}
          {state.followup && (
            <div className="rounded-xl border border-violet-200 bg-violet-50 px-3 py-2">
              <div className="text-xs font-bold text-violet-800 mb-0.5">
                🤖 Karana follow-up (demo agent · simulated)
              </div>
              <p className="text-sm text-violet-950">{state.followup.text}</p>
            </div>
          )}
          <p className="text-xs text-emerald-700">
            ✅ Result stored in room history.
          </p>
        </div>
      )}
    </div>
  );
}

// ------------------------------------------------------------------ //
// History / search / summary
// ------------------------------------------------------------------ //
function HistoryPanel({ detail }: { detail: RoomDetail }) {
  const [q, setQ] = useState("");
  const messages = q.trim()
    ? detail.messages.filter((m) =>
        m.body.toLowerCase().includes(q.trim().toLowerCase()))
    : detail.messages;

  return (
    <div className="space-y-3">
      {detail.summaries.length > 0 && (
        <div className="card space-y-2">
          <h3 className="font-semibold text-sm">Room summary — key outcomes</h3>
          {detail.summaries.slice().reverse().map((s) => (
            <div key={s.summary_id}
                 className="rounded-lg border border-slate-200 bg-white p-2 text-sm">
              <div className="text-xs uppercase tracking-wide text-slate-400">
                {s.activity_type === "find_the_mistake"
                  ? "Find the Mistake" : "Doubt Relay"} · {fmtTime(s.created_at)}
              </div>
              <p className="font-medium">{s.original_question}</p>
              <p className="text-slate-600 text-sm">{s.explanation}</p>
              {s.unresolved.length > 0 && (
                <div className="mt-1">
                  <span className="text-xs font-bold text-amber-700">Unresolved:</span>
                  <ul className="list-disc list-inside text-xs text-amber-800">
                    {s.unresolved.map((u, i) => <li key={i}>{u}</li>)}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
      <div className="card">
        <input className="input mb-2" placeholder="Search room history…"
               value={q} onChange={(e) => setQ(e.target.value)} />
        <div className="max-h-72 overflow-y-auto space-y-1.5">
          {messages.length === 0 && (
            <p className="text-sm text-slate-400 text-center py-4">
              {q ? "No matching messages." : "No messages yet."}
            </p>
          )}
          {messages.map((m) => (
            <div key={m.message_id} className="text-sm border-b border-slate-100 pb-1">
              <span className="text-xs text-slate-400">{fmtTime(m.created_at)} </span>
              <span className={
                m.sender_kind === "karana" ? "font-bold text-violet-700"
                : m.sender_kind === "system" ? "text-slate-500 italic"
                : "font-semibold"}>
                {m.sender_kind === "karana" ? "Karana (demo)"
                 : m.sender_kind === "system" ? "system" : m.sender_label}:
              </span>{" "}
              {m.body}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
