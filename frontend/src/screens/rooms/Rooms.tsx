// Karana Collective Learning Rooms — landing page.
// Live collaborative feature: create / join rooms, list rooms you belong to.
import { useEffect, useState } from "react";
import { api, SaarthiApiError } from "../../api/client";
import { getDraftValue, RoomDrafts, syncRoomDraftField } from "../../lib/roomDrafts";
import { t } from "../../i18n/or";
import type { RoomDetail } from "./types";

interface Props {
  profile: { learner_id: string; display_label: string };
  onOpenRoom: (roomId: string) => void;
}

const fmtCountdown = (ms: number): string => {
  const h = Math.floor(ms / 3_600_000);
  const m = Math.floor((ms % 3_600_000) / 60_000);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
};

const Avatar = ({ label, online }: { label: string; online: boolean }) => (
  <span className="relative inline-flex" title={label}>
    <span className="w-7 h-7 rounded-full bg-saarthi-600 text-white text-[10px] font-bold
                     inline-flex items-center justify-center uppercase">
      {label.replace(/\(demo\)/g, "").trim().slice(0, 2)}
    </span>
    <span className={`absolute bottom-0 right-0 w-2 h-2 rounded-full border
      border-white ${online ? "bg-emerald-500" : "bg-slate-300"}`} />
  </span>
);

export function RoomsScreen({ profile, onOpenRoom }: Props) {
  const [rooms, setRooms] = useState<RoomDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [joinCode, setJoinCode] = useState("");
  const [joinBusy, setJoinBusy] = useState(false);
  const [joinError, setJoinError] = useState("");
  const [createDraft, setCreateDraft] = useState<RoomDrafts>({
    title: "",
    topic: "",
    chapter: "ch01",
    language: "or",
    cap: 6,
  });

  const load = async () => {
    setLoading(true); setError("");
    try {
      const r = await api.listRooms();
      setRooms(r.rooms);
    } catch (e) {
      setError(e instanceof SaarthiApiError
        ? `${t("rooms_load_failed")} (${e.error_code ?? e.message})`
        : `${t("rooms_load_failed")} — ସଂଯୋଗ ଯାଞ୍ଚ କରନ୍ତୁ।`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  const join = async () => {
    if (!joinCode.trim()) return;
    setJoinBusy(true); setJoinError("");
    try {
      const detail = await api.joinRoom(joinCode.trim().toUpperCase());
      onOpenRoom(detail.room.room_id);
    } catch (e) {
      if (e instanceof SaarthiApiError) {
        const msgs: Record<string, string> = {
          room_not_found: "ସେହି କୋଡ୍‌ର କୌଣସି କକ୍ଷ ନାହିଁ।",
          room_full: "ସେହି କକ୍ଷ ପୂର୍ଣ୍ଣ ହୋଇଛି।",
          room_expired: "ସେହି କକ୍ଷ ସମାପ୍ତ ହୋଇଛି।",
        };
        setJoinError(msgs[e.error_code ?? ""] ?? `${t("rooms_join_failed")} (${e.error_code ?? e.message}).`);
      } else setJoinError(`${t("rooms_join_failed")} — ସଂଯୋଗ ଯାଞ୍ଚ କରନ୍ତୁ।`);
    } finally {
      setJoinBusy(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="card">
        <h2 className="font-bold text-lg mb-1 odia">{t("rooms_title")}</h2>
        <p className="text-sm text-slate-600 mb-3 odia">
          {t("rooms_subtitle")}
        </p>
        <div className="flex gap-2">
          <button className="btn-primary flex-1 odia" onClick={() => setShowCreate(v => !v)}>
            {showCreate ? t("rooms_close") : t("rooms_create")}
          </button>
          <input
            className="input w-32 text-center tracking-widest uppercase odia"
            placeholder={t("rooms_code")}
            maxLength={8}
            value={joinCode}
            onChange={(e) => setJoinCode(e.target.value)}
            aria-label={t("rooms_room_code")}
          />
          <button className="btn-secondary odia" disabled={joinBusy} onClick={join}>
            {joinBusy ? "…" : t("rooms_join")}
          </button>
        </div>
        {joinError && <p className="text-sm text-rose-700 mt-2 odia">{joinError}</p>}
      </div>

      {showCreate && (
        <CreateRoomCard
          draft={createDraft}
          onDraftChange={(id, value) => {
            setCreateDraft((prev) => ({ ...syncRoomDraftField({ ...prev }, id, value) }));
          }}
          onCreated={(id) => {
            setCreateDraft({ title: "", topic: "", chapter: "ch01", language: "or", cap: 6 });
            setShowCreate(false);
            onOpenRoom(id);
          }}
        />
      )}

      {loading && rooms.length === 0 && (
        <div className="card text-sm text-slate-500 odia">{t("rooms_loading")}</div>
      )}
      {error && !loading && (
        <div className="banner-err border rounded-lg px-4 py-3 text-sm">
          {error}
          <button className="underline ml-2 odia" onClick={load}>{t("rooms_retry")}</button>
        </div>
      )}
      {!loading && !error && rooms.length === 0 && (
        <div className="card text-sm text-slate-500 text-center py-8 odia">
          {t("rooms_no_rooms")}
        </div>
      )}

      {rooms.map(({ room }) => {
        const expiresIn = room.expires_at ? room.expires_at - Date.now() : null;
        return (
          <button
            key={room.room_id}
            className="card w-full text-left hover:bg-saarthi-50/40 transition"
            onClick={() => onOpenRoom(room.room_id)}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <div className="font-semibold truncate odia">{room.title}</div>
                <div className="text-xs text-slate-500 truncate odia">
                  {room.chapter_title || room.subject}
                  {room.learning_topic ? ` · ${room.learning_topic}` : ""}
                </div>
              </div>
              <span className="shrink-0 text-[10px] font-mono bg-slate-100 border
                               border-slate-200 rounded px-1.5 py-0.5 odia" title={t("rooms_room_code")}>
                {room.room_code}
              </span>
            </div>
            <div className="flex items-center gap-1 mt-2">
              {room.members.slice(0, 6).map((m) => (
                <Avatar key={m.learner_id} label={m.display_label} online={m.online} />
              ))}
              <span className="text-xs text-slate-500 ml-1 odia">
                {room.member_count}/{room.capacity} {t("rooms_members")}
              </span>
            </div>
            {room.recent_activity.length > 0 && (
              <p className="text-xs text-slate-500 mt-2 truncate">
                💬 {room.recent_activity[room.recent_activity.length - 1]}
              </p>
            )}
            {expiresIn !== null && (
              <p className="text-xs text-amber-700 mt-1 odia">
                ⏳ {t("rooms_empty_delete").replace("{time}", fmtCountdown(expiresIn))}
              </p>
            )}
          </button>
        );
      })}
    </div>
  );
}

function CreateRoomCard({
  draft,
  onDraftChange,
  onCreated,
}: {
  draft: RoomDrafts;
  onDraftChange: (id: string, value: string) => void;
  onCreated: (roomId: string) => void;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const title = getDraftValue(draft, "rTitle", "");
  const chapter = getDraftValue(draft, "rChapter", "ch01");
  const topic = getDraftValue(draft, "rTopic", "");
  const language = getDraftValue(draft, "rLanguage", "or");
  const capacity = draft.cap ?? 6;

  const chapters = [
    { id: "ch01", title: "Matter in Our Surroundings" },
    { id: "ch02", title: "Motion" },
    { id: "ch03", title: "Tissues" },
  ];

  const create = async () => {
    if (!title.trim()) { setError(t("rooms_need_title")); return; }
    setBusy(true); setError("");
    const ch = chapters.find((c) => c.id === chapter)!;
    try {
      const detail = await api.createRoom({
        title: title.trim(), subject: "science", chapter_id: ch.id,
        chapter_title: ch.title, learning_topic: topic.trim(),
        language, capacity,
      });
      onCreated(detail.room.room_id);
    } catch (e) {
      setError(e instanceof SaarthiApiError
        ? `${t("rooms_create_failed")} (${e.error_code ?? e.message}).`
        : `${t("rooms_create_failed")} — ସଂଯୋଗ ଯାଞ୍ଚ କରନ୍ତୁ।`);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card space-y-3">
      <h3 className="font-semibold odia">{t("rooms_create_title")}</h3>
      <input className="input odia" placeholder={t("rooms_create_placeholder")}
             value={title}
             onChange={(e) => onDraftChange("rTitle", e.target.value)} />
      <div className="grid grid-cols-2 gap-2">
        <select className="input odia" value={chapter}
                onChange={(e) => onDraftChange("rChapter", e.target.value)} aria-label={t("rooms_room_code")}>
          {chapters.map((c) => <option key={c.id} value={c.id}>{c.title}</option>)}
        </select>
        <select className="input odia" value={language}
                onChange={(e) => onDraftChange("rLanguage", e.target.value)} aria-label={t("rooms_room_code")}>
          <option value="or">ଓଡ଼ିଆ (Odia)</option>
          <option value="en">English</option>
          <option value="or-en">Odia + English</option>
        </select>
      </div>
      <input className="input odia" placeholder={t("rooms_topic_placeholder")}
             value={topic}
             onChange={(e) => onDraftChange("rTopic", e.target.value)} />
      <div>
        <label className="text-xs text-slate-500 block mb-1 odia">
          {t("rooms_max_members")}: <b>{capacity}</b>
        </label>
        <div className="flex gap-2">
          {[4, 5, 6].map((n) => (
            <button key={n}
                    className={`px-4 py-2 rounded-lg border font-semibold ${
                      capacity === n
                        ? "bg-saarthi-600 text-white border-saarthi-600"
                        : "bg-white border-slate-300 text-slate-700"}`}
                    onClick={() => onDraftChange("rCap", String(n))}>
              {n}
            </button>
          ))}
        </div>
      </div>
      {error && <p className="text-sm text-rose-700">{error}</p>}
      <button className="btn-primary w-full odia" disabled={busy} onClick={create}>
        {busy ? "…" : t("rooms_create_open")}
      </button>
    </div>
  );
}
