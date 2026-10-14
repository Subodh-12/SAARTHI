import { useEffect, useState } from "react";
import { api, SaarthiApiError } from "../api/client";
import { recordAssessmentEvent, getMasterySnapshot } from "../store/db";
import {
  Action, AssessmentResult, Chapter, Chunk, Decision,
  EvidenceType, NetworkState, Question,
} from "../generated/api";
import { t } from "../i18n/or";
import { getInstalledPack } from "../lib/sync";
import { RULESET } from "../engine/decide";
import { bloomLabel, bloomDescription, isValidBloomLevel } from "../engine/bloom";

interface Props {
  profile: { learner_id: string; device_id: string; display_label: string };
  network: NetworkState;
}

export function LessonScreen({ profile, network }: Props) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [chunkIdx, setChunkIdx] = useState(0);
  const [question, setQuestion] = useState<Question | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [decision, setDecision] = useState<Decision | null>(null);

  useEffect(() => { void loadNext(); }, []);

  async function loadNext() {
    setLoading(true); setError(""); setSubmitted(false); setSelected(null);
    setResult(null); setDecision(null); setChunkIdx(0);
    try {
      // Server-side decision (or local if offline)
      let d: Decision;
      if (network === NetworkState.OFFLINE) {
        // pick first chapter of installed pack
        const pack = await getInstalledPack();
        if (!pack) throw new Error("No pack installed");
        const manifest = JSON.parse(pack.manifest_json);
        const c = manifest.chapters[0];
        const firstConcept = manifest.concepts.filter((cc: any) => cc.chapter_id === c.chapter_id)[0];
        const ch = manifest.chunks.filter((ck: any) => ck.concept_id === firstConcept.concept_id);
        setChapter(c); setChunks(ch); setQuestion(manifest.questions.find((q: any) => q.concept_id === firstConcept.concept_id));
        d = {
          decision_id: `local_${Date.now()}`, learner_id: profile.learner_id,
          ruleset_version: RULESET.ruleset_version,
          target_concept_id: firstConcept.concept_id,
          action: Action.REVISE, delivery_mode: "cached" as any, background_actions: [],
          reason_code: "CONTENT_NOT_AVAILABLE_OFFLINE",
          reason_or: "ଅଫଲାଇନ — ସ୍ଥାନୀୟ ପାଠ",
          needs_help: false,
          chapter_id: c.chapter_id, network, produced_by: "local_engine",
          source: "local",
          created_at: Date.now(), suggested_chunk_id: ch[0]?.chunk_id ?? null,
          suggested_question_id: null,
        };
      } else {
        d = await api.nextDecision(network);
        const ch = await api.listChunksForConcept(d.target_concept_id) as Chunk[];
        setChunks(ch);
        setChapter(await api.getConcept(d.target_concept_id) as any);
        const q = await api.getNextQuestion(d.target_concept_id) as Question;
        setQuestion(q);
      }
      setDecision(d);
    } catch (e: any) {
      setError(e instanceof SaarthiApiError ? e.message : (e.message || String(e)));
    } finally {
      setLoading(false);
    }
  };

  const submit = async () => {
    if (!question || selected === null || !decision) return;
    const eventId = `evt_${crypto.randomUUID().replace(/-/g, "").slice(0, 24)}`;
    const correct = selected === question.correct_option;
    const evidence = correct ? EvidenceType.CORRECT : EvidenceType.INCORRECT;
    const attemptId = `att_${crypto.randomUUID().replace(/-/g, "").slice(0, 20)}`;
    // Atomic local write: mastery (basis points) + outbox event + seq counter
    // in ONE IndexedDB transaction (ProfileSession).
    const event = await recordAssessmentEvent(
      profile.learner_id, profile.device_id, eventId,
      question.concept_id,
      { question_id: question.question_id, chapter_id: question.chapter_id,
        revision: (question as any).revision ?? 1,
        bloom_level: question.bloom_level },
      correct, attemptId, selected, undefined, 0,
    );
    setSubmitted(true);
    // Local mastery projection for instant feedback (the server regrades
    // and its result wins at sync).
    const snap = await getMasterySnapshot();
    const local = snap.find((m) => m.concept_id === question.concept_id);
    setResult({
      question_id: question.question_id, attempt_id: attemptId, correct,
      evidence,
      explanation_or: question.explanation_or, concept_id: question.concept_id,
      mastery_after: {
        concept_id: question.concept_id,
        p_bp: local?.p_bp ?? 2000, band: local?.band ?? "weak",
        attempts: local?.attempts ?? 1, correct: local?.correct ?? 0,
        last_event_seq: (event as any).seq ?? 0,
      } as any, next_decision_id: "",
    });
    // If online, also try to sync this event
    if (network !== NetworkState.OFFLINE) {
      try {
        await api.submitAssessment({
          question_id: question.question_id,
          revision: (question as any).revision ?? 1,
          attempt_id: attemptId,
          selected_option: selected,
          answer_text: undefined, duration_ms: 0,
          submitted_at: Date.now(),
          correct_claim: correct,
        }, (event as any).seq ?? 1);
        const { trySyncNow } = await import("../lib/sync");
        await trySyncNow();
      } catch { /* offline-sync later */ }
    }
  };

  if (loading) return <div className="card odia">{t("loading")}</div>;
  if (error) return (
    <div className="card">
      <div className="banner-err text-sm px-3 py-2 rounded mb-3">{error}</div>
      <button className="btn-secondary w-full" onClick={loadNext}>{t("retry")}</button>
    </div>
  );
  if (!chunks.length || !question) return <div className="card odia">{t("empty")}</div>;

  const currentChunk = chunks[chunkIdx];

  return (
    <div className="space-y-4">
      <div className="card">
        <div className="text-xs text-slate-500 odia">CLASS 9 · SCIENCE · {chapter?.title_or}</div>
        <h1 className="text-xl font-bold mb-3 odia">{currentChunk?.text_or.slice(0, 60)}…</h1>
        <p className="odia leading-relaxed">{currentChunk?.text_or}</p>
        {chunkIdx < chunks.length - 1 && (
          <button className="btn-secondary mt-3 w-full"
                  onClick={() => setChunkIdx(chunkIdx + 1)}>{t("lesson_read")}</button>
        )}
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <h2 className="font-semibold odia">{"ଆପଣଙ୍କ ପ୍ରଶ୍ନ"}</h2>
          {question.bloom_level && isValidBloomLevel(question.bloom_level) && (
            <span
              className="text-xs px-2 py-0.5 rounded bg-saarthi-100 text-saarthi-800 font-semibold odia"
              title={bloomDescription(question.bloom_level, "or")}
            >
              🎯 {bloomLabel(question.bloom_level, "or")} ({bloomLabel(question.bloom_level, "en")})
            </span>
          )}
        </div>
        {question.bloom_level && isValidBloomLevel(question.bloom_level) && (
          <p className="text-xs text-slate-500 mb-3 odia italic">
            ଦକ୍ଷତା ଲକ୍ଷ୍ୟ: {bloomDescription(question.bloom_level, "or")}
          </p>
        )}
        <p className="odia mb-4">{question.prompt_or}</p>
        <div className="space-y-2">
          {question.options.map((opt, i) => {
            let cls = "option-btn";
            if (submitted) {
              if (i === question.correct_option) cls += " option-correct";
              else if (i === selected) cls += " option-incorrect";
            } else if (i === selected) cls += " option-selected";
            return (
              <button key={i} className={cls}
                      disabled={submitted}
                      onClick={() => setSelected(i)}>
                {i + 1}. {opt}
              </button>
            );
          })}
        </div>
        {!submitted ? (
          <button className="btn-primary mt-4 w-full" disabled={selected === null}
                  onClick={submit}>{t("quiz_submit")}</button>
        ) : (
          <div className="mt-4">
            <h3 className="font-bold mb-2">
              {result?.correct ? `✅ ${t("quiz_correct")}` : `❌ ${t("quiz_incorrect")}`}
            </h3>
            <p className="odia text-sm mb-3"><b>{t("quiz_explanation")}:</b> {question.explanation_or}</p>
            <button className="btn-primary w-full" onClick={loadNext}>{t("back")}</button>
          </div>
        )}
      </div>
    </div>
  );
}
