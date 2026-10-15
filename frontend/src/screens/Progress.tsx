import { useEffect, useState } from "react";
import { getMasterySnapshot, listRecentDecisions, LocalMastery, LocalDecision } from "../store/db";
import { t } from "../i18n/or";
import { CHAPTERS, CONCEPTS } from "../curriculum.js";

interface Props {
  learnerId: string;
}

export function ProgressScreen({ learnerId }: Props) {
  const [masteryList, setMasteryList] = useState<LocalMastery[]>([]);
  const [decision, setDecision] = useState<LocalDecision | undefined>(undefined);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const [m, recents] = await Promise.all([
          getMasterySnapshot(),
          listRecentDecisions(1),
        ]);
        if (mounted) {
          setMasteryList(m);
          setDecision(recents[0]);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [learnerId]);

  if (loading) {
    return <div className="card odia">{t("loading")}</div>;
  }

  const masteryMap = new Map<string, LocalMastery>();
  for (const m of masteryList) {
    masteryMap.set(m.concept_id, m);
  }

  const chapters = CHAPTERS || [
    { chapter_id: "ch01", title_or: "ଆମ ଚାରିପାଖର ପଦାର୍ଥ (Matter in Our Surroundings)" },
    { chapter_id: "ch02", title_or: "ଗତି (Motion)" },
    { chapter_id: "ch03", title_or: "କଳା ଏବଂ ଟିସୁ (Tissues)" },
  ];

  const concepts = CONCEPTS || [
    { concept_id: "c0001", chapter_id: "ch01", title_or: "ପଦାର୍ଥର ସ୍ୱରୂପ ଓ କଣିକା ତତ୍ତ୍ୱ", title_en: "Nature of Matter" },
    { concept_id: "c0002", chapter_id: "ch01", title_or: "ପଦାର୍ଥର ଅବସ୍ଥା ଓ ପରିବର୍ତ୍ତନ", title_en: "States of Matter" },
    { concept_id: "c0003", chapter_id: "ch01", title_or: "ବାଷ୍ପୀଭବନ ଓ ତାହାର ପ୍ରଭାବ", title_en: "Evaporation" },
    { concept_id: "c0004", chapter_id: "ch02", title_or: "ଦୂରତା, ବିସ୍ଥାପନ ଓ ବେଗ", title_en: "Distance, Displacement & Velocity" },
    { concept_id: "c0005", chapter_id: "ch02", title_or: "ତ୍ୱରଣ ଓ ସୁଷମ ଗତି", title_en: "Acceleration & Uniform Motion" },
    { concept_id: "c0006", chapter_id: "ch02", title_or: "ଗତିର ସମୀକରଣ ଓ ଗ୍ରାଫିକାଲ୍ ବିଶ୍ଳେଷଣ", title_en: "Equations of Motion" },
    { concept_id: "c0007", chapter_id: "ch03", title_or: "ଉଦ୍ଭିଦ ଟିସୁ: ଭାଜକ ଓ ସ୍ଥାୟୀ ଟିସୁ", title_en: "Plant Tissues" },
    { concept_id: "c0008", chapter_id: "ch03", title_or: "ଜଟିଳ ସ୍ଥାୟୀ ଟିସୁ: ଜାଇଲେମ୍ ଓ ଫ୍ଲୋଏମ୍", title_en: "Complex Tissues" },
    { concept_id: "c0009", chapter_id: "ch03", title_or: "ପ୍ରାଣୀ ଟିସୁ: ଉପକଳା, ସଂଯୋଜକ, ପେଶୀ ଓ ସ୍ନାୟୁ ଟିସୁ", title_en: "Animal Tissues" },
  ];

  return (
    <div className="space-y-4">
      {decision?.needs_help && (
        <div className="banner-warn p-4 rounded-xl border border-amber-300 bg-amber-50">
          <div className="flex items-start gap-3">
            <span className="text-xl">⚠️</span>
            <div>
              <div className="font-bold text-amber-900 odia">ସାହାଯ୍ୟ ଆବଶ୍ୟକ</div>
              <p className="text-sm text-amber-800 mt-1 odia">
                {t("ask_teacher_prompt")}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <h2 className="text-lg font-bold mb-3 odia">{t("nav_progress")} — ଧାରଣା ମାନଚିତ୍ର</h2>
        <div className="flex gap-4 text-xs font-semibold mb-4 pb-2 border-b">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-emerald-500 inline-block"></span>
            <span className="odia">ଶିଖିଲା (Mastered)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-amber-500 inline-block"></span>
            <span className="odia">ଆଂଶିକ (Partial)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-rose-500 inline-block"></span>
            <span className="odia">ଦୁର୍ବଳ (Weak)</span>
          </div>
        </div>

        <div className="space-y-6">
          {chapters.map((ch: any) => {
            const chConcepts = concepts.filter((c: any) => c.chapter_id === ch.chapter_id);
            return (
              <div key={ch.chapter_id} className="space-y-2">
                <h3 className="font-semibold text-sm text-slate-700 odia">{ch.title_or}</h3>
                <div className="grid grid-cols-1 gap-2">
                  {chConcepts.map((c: any) => {
                    const m = masteryMap.get(c.concept_id);
                    const band = m?.band || "weak";
                    const p_bp = m?.p_bp ?? 2000;
                    const percent = Math.round(p_bp / 100);

                    const colorClass =
                      band === "mastered"
                        ? "border-emerald-300 bg-emerald-50 text-emerald-900"
                        : band === "partial"
                        ? "border-amber-300 bg-amber-50 text-amber-900"
                        : "border-rose-200 bg-rose-50 text-rose-900";

                    const badgeColor =
                      band === "mastered"
                        ? "bg-emerald-500 text-white"
                        : band === "partial"
                        ? "bg-amber-500 text-white"
                        : "bg-rose-500 text-white";

                    return (
                      <div
                        key={c.concept_id}
                        className={`p-3 rounded-lg border flex items-center justify-between gap-3 ${colorClass}`}
                      >
                        <div className="min-w-0 flex-1">
                          <div className="font-medium text-sm odia truncate">{c.title_or}</div>
                          <div className="text-xs opacity-75">{c.title_en}</div>
                        </div>
                        <div className="flex items-center gap-2 flex-none">
                          <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${badgeColor}`}>
                            {band === "mastered" ? "ଦକ୍ଷ" : band === "partial" ? "ଅଭ୍ୟାସ" : "ନୂଆ"}
                          </span>
                          <span className="text-xs font-mono font-semibold">{percent}%</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
