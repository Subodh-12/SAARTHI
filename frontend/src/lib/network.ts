// Measured network state with hysteresis — never trusts navigator.onLine
// alone (Design v2 Section 10).
//
//   online   probe succeeds, RTT < 800 ms
//   weak     probe succeeds but 800–3000 ms RTT
//   offline  two consecutive probe failures, or navigator.onLine === false
//
// Probe: a HEAD request to /health every 30 s while the app is visible,
// 3 s timeout (ruleset `network`). Hysteresis: downgrade after ONE bad
// probe, upgrade only after TWO good ones, so the state does not flap.
// Every change is surfaced to the caller so it can be recorded as
// NETWORK_STATE_CHANGED and enter each decision.

import { RULESET } from "../engine/decide";
import { NetworkState } from "../generated/api";

type Listener = (s: NetworkState, info: NetworkInfo) => void;

export interface NetworkInfo {
  state: NetworkState;
  rt_ms: number | null;
  loss: number | null;
}

interface NetworkRuleset {
  online?: { rtt_ms_max?: number };
  weak?: { rtt_ms_max?: number; downlink_kbps_min?: number };
  probe_interval_s?: number;
  probe_timeout_s?: number;
  hysteresis_downgrade_after_bad?: number;
  hysteresis_upgrade_after_good?: number;
}
const n = (RULESET.network || {}) as NetworkRuleset;

const PROBE_INTERVAL_MS = Math.max(5, (n.probe_interval_s ?? 30)) * 1000;
const PROBE_TIMEOUT_MS = Math.max(1, (n.probe_timeout_s ?? 3)) * 1000;
const ONLINE_RTT_MAX = n.online?.rtt_ms_max ?? 800;
const WEAK_RTT_MAX = n.weak?.rtt_ms_max ?? 3000;
const DOWNGRADE_AFTER_BAD = n.hysteresis_downgrade_after_bad ?? 1;
const UPGRADE_AFTER_GOOD = n.hysteresis_upgrade_after_good ?? 2;

class NetworkMonitor {
  private listeners: Listener[] = [];
  private state: NetworkState =
    navigator.onLine ? NetworkState.ONLINE : NetworkState.OFFLINE;
  /** Probe outcomes, oldest → newest (capped). */
  private history: { rt_ms: number; ok: boolean; ts: number }[] = [];
  private timer: number | null = null;
  private visibilityHandler: (() => void) | null = null;

  start() {
    if (this.timer) return;
    window.addEventListener("online", this.onNavigatorOnline);
    window.addEventListener("offline", this.onNavigatorOffline);
    // Probe every 30 s while the app is visible; probe immediately on
    // visibility regain.
    this.timer = window.setInterval(() => {
      if (document.visibilityState === "visible") this.probe();
    }, PROBE_INTERVAL_MS);
    this.visibilityHandler = () => {
      if (document.visibilityState === "visible") this.probe();
    };
    document.addEventListener("visibilitychange", this.visibilityHandler);
    this.probe();
  }

  stop() {
    if (this.timer) { clearInterval(this.timer); this.timer = null; }
    if (this.visibilityHandler) {
      document.removeEventListener("visibilitychange", this.visibilityHandler);
      this.visibilityHandler = null;
    }
    window.removeEventListener("online", this.onNavigatorOnline);
    window.removeEventListener("offline", this.onNavigatorOffline);
  }

  private onNavigatorOnline = () => this.probe();
  private onNavigatorOffline = () => this.setState(NetworkState.OFFLINE, null, 1.0);

  private async probe() {
    if (!navigator.onLine) {
      this.setState(NetworkState.OFFLINE, null, 1.0);
      return;
    }
    const base = (import.meta.env.VITE_API_URL as string | undefined)
      || (import.meta.env.DEV ? "http://127.0.0.1:8000" : "");
    if (!base) { // production build without configured API: stay offline
      this.setState(NetworkState.OFFLINE, null, 1.0);
      return;
    }
    const t0 = performance.now();
    try {
      const ctrl = new AbortController();
      const timer = setTimeout(() => ctrl.abort(), PROBE_TIMEOUT_MS);
      const resp = await fetch(`${base}/api/v1/health`,
                               { signal: ctrl.signal, cache: "no-store" });
      clearTimeout(timer);
      const rt = performance.now() - t0;
      this.history.push({ rt_ms: rt, ok: resp.ok, ts: Date.now() });
    } catch {
      this.history.push({ rt_ms: Number.POSITIVE_INFINITY, ok: false,
                          ts: Date.now() });
    }
    if (this.history.length > 8) this.history.shift();
    this.classify();
  }

  private classify() {
    if (this.history.length < 1) return;
    const last = this.history[this.history.length - 1];

    // Offline rule: two consecutive probe failures (or navigator offline,
    // handled in probe()).
    const failedTwice = this.history.length >= 2
      && !this.history[this.history.length - 1].ok
      && !this.history[this.history.length - 2].ok;

    // Hysteresis helpers: consecutive good / bad probes at the tail.
    let goodStreak = 0;
    for (let i = this.history.length - 1; i >= 0; i--) {
      if (this.history[i].ok) goodStreak++; else break;
    }
    let badStreak = 0;
    for (let i = this.history.length - 1; i >= 0; i--) {
      if (!this.history[i].ok) badStreak++; else break;
    }

    if (failedTwice || badStreak >= DOWNGRADE_AFTER_BAD) {
      this.setState(NetworkState.OFFLINE, null, 1.0);
      return;
    }

    const okSamples = this.history.filter((s) => s.ok);
    const avgRt = okSamples.length
      ? okSamples.reduce((a, b) => a + b.rt_ms, 0) / okSamples.length
      : Number.POSITIVE_INFINITY;
    const loss = 1 - okSamples.length / this.history.length;

    const sampleState = (rt: number): NetworkState =>
      rt <= ONLINE_RTT_MAX ? NetworkState.ONLINE : NetworkState.WEAK;

    // Downgrade online → weak after ONE bad (slow) probe; upgrade only
    // after UPGRADE_AFTER_GOOD consecutive good ones (no flapping).
    if (this.state === NetworkState.ONLINE
        && avgRt > ONLINE_RTT_MAX && avgRt <= WEAK_RTT_MAX) {
      this.setState(NetworkState.WEAK, avgRt, loss);
      return;
    }
    if (this.state === NetworkState.WEAK
        && last.ok && last.rt_ms <= ONLINE_RTT_MAX
        && goodStreak >= UPGRADE_AFTER_GOOD) {
      this.setState(NetworkState.ONLINE, avgRt, loss);
      return;
    }
    if (this.state === NetworkState.OFFLINE
        && goodStreak >= UPGRADE_AFTER_GOOD) {
      // Upgrade from offline goes through the measured sample state.
      this.setState(sampleState(last.rt_ms), avgRt, loss);
      return;
    }
    if (this.state === NetworkState.WEAK
        && badStreak >= DOWNGRADE_AFTER_BAD && failedTwice) {
      this.setState(NetworkState.OFFLINE, null, 1.0);
      return;
    }
    // No transition — report measurement only.
    void sampleState;
  }

  private setState(state: NetworkState, rt_ms: number | null, loss: number) {
    const prev = this.state;
    this.state = state;
    const info: NetworkInfo = { state, rt_ms, loss };
    for (const l of this.listeners) l(state, info);
    // RECONNECTED is a transient: emit when going from OFFLINE to online/weak.
    if (prev === NetworkState.OFFLINE && state !== NetworkState.OFFLINE) {
      for (const l of this.listeners) l(NetworkState.RECONNECTED, info);
    }
  }

  getState(): NetworkState { return this.state; }
  subscribe(l: Listener): () => void {
    this.listeners.push(l);
    return () => { this.listeners = this.listeners.filter((x) => x !== l); };
  }
}

export const networkMonitor = new NetworkMonitor();
