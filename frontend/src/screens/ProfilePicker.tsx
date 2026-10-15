import { useState } from "react";
import { SharedProfileMeta } from "../store/profile_session";
import { t } from "../i18n/or";

interface Props {
  profiles: SharedProfileMeta[];
  onSelectProfile: (learnerId: string, pin?: string) => Promise<void>;
  onCreateNew: () => void;
}

export function ProfilePicker({ profiles, onSelectProfile, onCreateNew }: Props) {
  const [selectedLearner, setSelectedLearner] = useState<SharedProfileMeta | null>(null);
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleProfileClick = async (profile: SharedProfileMeta) => {
    setError("");
    if (profile.has_pin) {
      setSelectedLearner(profile);
      setPin("");
    } else {
      setLoading(true);
      try {
        await onSelectProfile(profile.learner_id);
      } catch (e: any) {
        setError(e.message || String(e));
      } finally {
        setLoading(false);
      }
    }
  };

  const handlePinSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedLearner) return;
    if (pin.length !== 4) {
      setError(t("pin_invalid"));
      return;
    }
    setLoading(true);
    setError("");
    try {
      await onSelectProfile(selectedLearner.learner_id, pin);
      setSelectedLearner(null);
      setPin("");
    } catch (e: any) {
      setError(t("pin_incorrect"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-6 max-w-md mx-auto">
      <div className="card w-full">
        <h1 className="text-2xl font-bold mb-2 odia">{t("app_name")}</h1>
        <p className="text-sm text-slate-600 mb-6 odia">{t("select_profile")}</p>

        {error && <div className="banner-err text-sm px-3 py-2 rounded mb-4">{error}</div>}

        {selectedLearner ? (
          <form onSubmit={handlePinSubmit} className="space-y-4">
            <div className="p-3 bg-slate-50 border rounded-lg flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-saarthi-700 text-white font-bold flex items-center justify-center text-lg">
                {(selectedLearner.display_label || "S")[0].toUpperCase()}
              </div>
              <div className="flex-1">
                <div className="font-semibold text-slate-800 odia">
                  {selectedLearner.display_label || "Student"}
                </div>
                <div className="text-xs text-slate-500">🔒 PIN Protected</div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 odia">{t("enter_pin")}</label>
              <input
                autoFocus
                value={pin}
                onChange={(e) => setPin(e.target.value.replace(/\D/g, "").slice(0, 4))}
                inputMode="numeric"
                type="password"
                className="w-full border rounded-lg px-3 py-2 text-center text-xl tracking-widest"
                placeholder="••••"
              />
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                className="btn-ghost flex-1 py-2 rounded-lg border text-sm odia"
                onClick={() => { setSelectedLearner(null); setError(""); setPin(""); }}
                disabled={loading}
              >
                {t("cancel")}
              </button>
              <button
                type="submit"
                className="btn-primary flex-1 py-2 rounded-lg text-sm odia"
                disabled={loading || pin.length !== 4}
              >
                {loading ? t("loading") : t("submit")}
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-3">
            <ul className="divide-y divide-slate-100">
              {profiles.map((p) => (
                <li key={p.learner_id}>
                  <button
                    type="button"
                    onClick={() => handleProfileClick(p)}
                    disabled={loading}
                    className="w-full py-3 px-2 flex items-center gap-3 text-left hover:bg-slate-50 rounded-lg transition-colors"
                  >
                    <div className="w-10 h-10 rounded-full bg-saarthi-700 text-white font-bold flex items-center justify-center text-lg flex-none">
                      {(p.display_label || "S")[0].toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-slate-800 truncate odia">
                        {p.display_label || "Student"}
                      </div>
                      <div className="text-xs text-slate-400">
                        {p.has_pin ? "🔒 PIN Protected" : "🔓 Open Profile"}
                      </div>
                    </div>
                    <div className="text-slate-400">›</div>
                  </button>
                </li>
              ))}
            </ul>

            <div className="pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={onCreateNew}
                disabled={loading}
                className="btn-primary w-full py-2 rounded-lg text-sm odia flex items-center justify-center gap-2"
              >
                <span>+</span>
                <span>{t("create_profile")}</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
