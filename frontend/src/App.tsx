import { useEffect, useState, useCallback } from "react";
import { api } from "./api/client";
import {
  getActiveProfile, LocalProfile, listProfiles,
  saveProfile, listPendingOutbox, ensureSession, setActiveProfile,
} from "./store/db";
import {
  closeActiveProfileSession, SharedProfileMeta, StorageFailure, CorruptedState,
} from "./store/profile_session";
import { networkMonitor } from "./lib/network";
import { startSyncLoop } from "./lib/sync";
import { NetworkState } from "./generated/api";
import { t } from "./i18n/or";
import { OnboardingScreen } from "./screens/Onboarding";
import { ProfilePicker } from "./screens/ProfilePicker";
import { HomeScreen } from "./screens/Home";
import { LessonScreen } from "./screens/Lesson";
import { DoubtScreen } from "./screens/Doubt";
import { PacksScreen } from "./screens/Packs";
import { DevTraceScreen } from "./screens/DevTrace";
import { ProgressScreen } from "./screens/Progress";

export type StartupState =
  | "initializing"
  | "profile_required"
  | "profile_active"
  | "storage_unavailable"
  | "recovery_error";

type Tab = "home" | "lesson" | "doubt" | "progress" | "packs" | "dev";
type Profile = { learner_id: string; device_id: string; device_token: string; display_label: string; has_pin?: boolean } | null;

export default function App() {
  const [startupState, setStartupState] = useState<StartupState>("initializing");
  const [profile, setProfile] = useState<Profile>(null);
  const [profiles, setProfiles] = useState<SharedProfileMeta[]>([]);
  const [isOnboardingOpen, setIsOnboardingOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [tab, setTab] = useState<Tab>("home");
  const [network, setNetwork] = useState<NetworkState>(
    navigator.onLine ? NetworkState.ONLINE : NetworkState.OFFLINE,
  );
  const [outboxDepth, setOutboxDepth] = useState(0);

  const initApp = useCallback(async () => {
    setStartupState("initializing");
    setErrorMessage("");
    try {
      if (typeof indexedDB === "undefined") {
        setStartupState("storage_unavailable");
        return;
      }

      // Check available profiles
      const existingProfiles = await listProfiles();
      setProfiles(existingProfiles);

      if (existingProfiles.length === 0) {
        setStartupState("profile_required");
        setIsOnboardingOpen(true);
        return;
      }

      // Attempt to recover active profile
      const active = await getActiveProfile();
      if (active) {
        await ensureSession(active);
        api.setAuth(active.device_token, active.device_id, active.refresh_token);
        setProfile({
          learner_id: active.learner_id,
          device_id: active.device_id,
          device_token: active.device_token,
          display_label: active.display_label,
          has_pin: active.has_pin,
        });
        setStartupState("profile_active");
      } else {
        // Multiple profiles exist, prompt learner to select
        setStartupState("profile_required");
        setIsOnboardingOpen(false);
      }
    } catch (err: any) {
      if (err instanceof StorageFailure || err?.name === "SecurityError") {
        setStartupState("storage_unavailable");
      } else if (err instanceof CorruptedState) {
        setStartupState("recovery_error");
        setErrorMessage(err.message);
      } else {
        setStartupState("recovery_error");
        setErrorMessage(err?.message || String(err));
      }
    }
  }, []);

  useEffect(() => {
    initApp();
    networkMonitor.start();
    const unsub = networkMonitor.subscribe((s) => setNetwork(s));
    startSyncLoop();
    return () => {
      unsub();
      networkMonitor.stop();
    };
  }, [initApp]);

  useEffect(() => {
    if (!profile) return;
    const tick = async () => {
      try {
        const pending = (await listPendingOutbox(100000)).length;
        setOutboxDepth(pending);
      } catch {
        // session might be closing or switching
      }
    };
    tick();
    const i = setInterval(tick, 2000);
    return () => clearInterval(i);
  }, [profile]);

  const handleSelectProfile = async (learnerId: string, pin?: string) => {
    await setActiveProfile(learnerId, pin);
    const active = await getActiveProfile();
    if (!active) throw new Error("Could not activate profile");
    await ensureSession(active);
    api.setAuth(active.device_token, active.device_id, active.refresh_token);
    setProfile({
      learner_id: active.learner_id,
      device_id: active.device_id,
      device_token: active.device_token,
      display_label: active.display_label,
      has_pin: active.has_pin,
    });
    setStartupState("profile_active");
  };

  const handleSwitchProfile = async () => {
    await closeActiveProfileSession();
    setProfile(null);
    const all = await listProfiles();
    setProfiles(all);
    setIsOnboardingOpen(false);
    setStartupState("profile_required");
  };

  const handleCreatedProfile = async (p: any, pin?: string) => {
    const display_label = p.display_label || "Student";
    const local: LocalProfile = {
      learner_id: p.learner_id!,
      device_id: p.device_id,
      device_token: p.device_token,
      refresh_token: p.refresh_token ?? undefined,
      token_expires_at: p.token_expires_at,
      display_label,
      created_at: Date.now(),
      active: true,
      has_pin: !!pin,
    };
    await saveProfile(local);
    const session = await ensureSession(local);
    if (pin) {
      await session.setPin(pin);
    }
    api.setAuth(local.device_token, local.device_id, local.refresh_token);
    setProfile({
      learner_id: local.learner_id,
      device_id: local.device_id,
      device_token: local.device_token,
      display_label,
      has_pin: !!pin,
    });
    setStartupState("profile_active");
  };

  // State: Initializing
  if (startupState === "initializing") {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-saarthi-700 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="odia text-slate-600 font-semibold">{t("loading")}</p>
        </div>
      </main>
    );
  }

  // State: Storage Unavailable
  if (startupState === "storage_unavailable") {
    return (
      <main className="min-h-screen flex items-center justify-center p-6 max-w-md mx-auto">
        <div className="card w-full text-center space-y-4">
          <div className="text-3xl">⚠️</div>
          <h2 className="text-xl font-bold odia text-rose-800">{t("storage_unavailable_title")}</h2>
          <p className="text-sm text-slate-600 odia">{t("storage_unavailable_desc")}</p>
          <button onClick={initApp} className="btn-primary w-full py-2 rounded-lg text-sm odia">
            {t("retry")}
          </button>
        </div>
      </main>
    );
  }

  // State: Recovery Error
  if (startupState === "recovery_error") {
    return (
      <main className="min-h-screen flex items-center justify-center p-6 max-w-md mx-auto">
        <div className="card w-full text-center space-y-4">
          <div className="text-3xl">🛑</div>
          <h2 className="text-xl font-bold odia text-rose-800">{t("recovery_error_title")}</h2>
          <p className="text-xs font-mono text-slate-500 bg-slate-100 p-2 rounded break-all">{errorMessage}</p>
          <button onClick={initApp} className="btn-primary w-full py-2 rounded-lg text-sm odia">
            {t("retry")}
          </button>
        </div>
      </main>
    );
  }

  // State: Profile Required
  if (startupState === "profile_required") {
    if (isOnboardingOpen || profiles.length === 0) {
      return (
        <OnboardingScreen
          onCreated={handleCreatedProfile}
          onCancel={profiles.length > 0 ? () => setIsOnboardingOpen(false) : undefined}
        />
      );
    }
    return (
      <ProfilePicker
        profiles={profiles}
        onSelectProfile={handleSelectProfile}
        onCreateNew={() => setIsOnboardingOpen(true)}
      />
    );
  }

  if (!profile) return null;

  const Banner = network === NetworkState.OFFLINE ? (
    <div className="banner-warn text-sm px-4 py-2 border-b">{t("network_offline_banner")}</div>
  ) : null;

  return (
    <main className="min-h-screen max-w-md mx-auto flex flex-col bg-slate-50">
      <header className="bg-saarthi-700 text-white px-4 py-3 flex items-center justify-between">
        <div>
          <div className="font-bold text-lg odia">{t("app_name")}</div>
          <div className="text-xs opacity-80 odia">{t("app_tagline")}</div>
        </div>
        <div className="text-right flex items-center gap-3">
          <div>
            <div className="text-xs font-semibold odia">{profile.display_label}</div>
            <NetworkBadge state={network} />
          </div>
          <button
            onClick={handleSwitchProfile}
            title={t("switch_profile")}
            className="p-1.5 bg-white/10 hover:bg-white/20 rounded-lg text-xs odia transition-colors flex items-center gap-1"
          >
            <span>👥</span>
          </button>
        </div>
      </header>
      {Banner}
      <section className="flex-1 overflow-y-auto p-4">
        {tab === "home" && (
          <HomeScreen profile={profile} network={network} onNavigate={setTab} outboxDepth={outboxDepth} />
        )}
        {tab === "lesson" && (
          <LessonScreen profile={profile} network={network} />
        )}
        {tab === "doubt" && (
          <DoubtScreen profile={profile} network={network} />
        )}
        {tab === "progress" && (
          <ProgressScreen learnerId={profile.learner_id} />
        )}
        {tab === "packs" && (
          <PacksScreen />
        )}
        {tab === "dev" && (
          <DevTraceScreen />
        )}
      </section>
      <nav className="bg-white border-t border-slate-200 grid grid-cols-6 text-xs text-slate-700">
        <TabBtn label={t("nav_home")} active={tab === "home"} onClick={() => setTab("home")} icon="🏠" />
        <TabBtn label={t("nav_lesson")} active={tab === "lesson"} onClick={() => setTab("lesson")} icon="📖" />
        <TabBtn label={t("nav_doubt")} active={tab === "doubt"} onClick={() => setTab("doubt")} icon="?" />
        <TabBtn label={t("nav_progress")} active={tab === "progress"} onClick={() => setTab("progress")} icon="📊" />
        <TabBtn label={t("nav_packs")} active={tab === "packs"} onClick={() => setTab("packs")} icon="📦" />
        <TabBtn label={t("nav_dev")} active={tab === "dev"} onClick={() => setTab("dev")} icon="🔧" />
      </nav>
    </main>
  );
}

function TabBtn({ label, active, onClick, icon }: { label: string; active: boolean; onClick: () => void; icon: string }) {
  return (
    <button
      onClick={onClick}
      className={`flex flex-col items-center justify-center py-2 gap-0.5 ${
        active ? "text-saarthi-700 font-semibold" : "text-slate-500"
      }`}
    >
      <span className="text-base">{icon}</span>
      <span className="odia text-[11px] leading-tight truncate px-0.5">{label}</span>
    </button>
  );
}

function NetworkBadge({ state }: { state: NetworkState }) {
  const text =
    state === NetworkState.ONLINE
      ? t("state_online")
      : state === NetworkState.WEAK
      ? t("state_weak")
      : state === NetworkState.OFFLINE
      ? t("state_offline")
      : t("state_syncing");
  return <div className="text-[11px] opacity-90 odia">{text}</div>;
}
