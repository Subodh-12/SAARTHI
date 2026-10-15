#!/usr/bin/env python3
"""SAARTHI master dev script — one entry point for setup/start/test/health/stop.

Usage:
    python scripts/dev.py setup      # create venv + install deps + build pack
    python scripts/dev.py doctor     # diagnose environment and configuration
    python scripts/dev.py start      # start backend + frontend (foreground)
    python scripts/dev.py stop       # stop only the processes this script started
    python scripts/dev.py test       # backend tests + decision parity + frontend tests + e2e smoke
    python scripts/dev.py check      # typecheck + lint + production build + backend import
    python scripts/dev.py health     # API health/readiness check (with retries)
    python scripts/dev.py migrate    # apply schema to a fresh DB and verify it
    python scripts/dev.py parity     # regenerate shared vectors; run both engines on them
    python scripts/dev.py smoke      # optional real-provider smoke when credentials exist
    python scripts/dev.py --reset-data  # DESTRUCTIVE: wipe the local SQLite DB

Cross-platform (Linux/macOS/Windows). Uses the project venv at ./.venv for
every Python invocation — NEVER the system interpreter — and
./frontend/node_modules for the web app.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv"
FRONTEND = ROOT / "frontend"
BACKEND = ROOT / "backend"
PID_FILE = ROOT / ".dev_pids"


# --------------------------------------------------------------------------- #
# Tool discovery with actionable diagnostics (never silently degrade)
# --------------------------------------------------------------------------- #
def _have(binname: str) -> bool:
    return shutil.which(binname) is not None


def _bootstrap_python() -> str | None:
    """A Python interpreter able to CREATE the project venv.

    Order: the running interpreter, python3 on PATH, py launcher (Windows),
    python on PATH. Returns None when none exists — callers must fail with
    an actionable message instead of improvising.
    """
    candidates: list[str] = []
    if sys.executable:
        candidates.append(sys.executable)
    for name in ("python3", "python"):
        which = shutil.which(name)
        if which:
            candidates.append(which)
    if sys.platform == "win32":
        py_launcher = shutil.which("py")
        if py_launcher:
            candidates.append(py_launcher)
    for cand in candidates:
        try:
            subprocess.check_call(
                [cand, "-c", "import venv, ensurepip"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return cand
        except (OSError, subprocess.CalledProcessError):
            continue
    return None


def _venv_python() -> Path:
    if sys.platform == "win32":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def _have_venv() -> bool:
    return _venv_python().exists()


def _ensure_venv() -> str:
    """Create and validate the project venv; never install into system Python."""
    if not _have_venv():
        bootstrap = _bootstrap_python()
        if not bootstrap:
            raise RuntimeError(
                "Python 3 with the 'venv' module is required to create the "
                "project environment, and no usable interpreter was found.\n"
                "  - Install Python 3.11+ (https://www.python.org/downloads/)\n"
                "  - On Debian/Ubuntu: sudo apt install python3 python3-venv\n"
                "  - On Arch: ensure the 'python' package is installed\n"
                "  - On Windows: install from python.org, or 'py' must exist\n"
                "then rerun: python scripts/dev.py setup")
        print(f"[setup] creating virtual environment at {VENV}…")
        try:
            subprocess.check_call([bootstrap, "-m", "venv", str(VENV)])
        except (OSError, subprocess.CalledProcessError) as exc:
            raise RuntimeError(
                f"Could not create the project virtual environment at {VENV}. "
                f"Bootstrap interpreter: {bootstrap}. On externally-managed "
                "distros ensure python3-venv is installed, then rerun "
                "./run.sh setup.") from exc

    if not _have_venv():
        raise RuntimeError(f"Virtual environment was not created at {VENV}.")

    python = str(_venv_python())
    try:
        # A path existing is not enough: reject broken/stale venvs.
        subprocess.check_call(
            [python, "-c", "import sys; assert sys.prefix != sys.base_prefix"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(
            f"The project virtual environment at {VENV} is not usable. "
            "Remove the broken .venv directory and rerun ./run.sh setup."
        ) from exc

    try:
        subprocess.check_call([python, "-m", "pip", "--version"],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError):
        # Some Python builds omit pip from newly-created environments.
        subprocess.check_call([python, "-m", "ensurepip", "--upgrade"])

    return python


def _require_venv_python() -> str:
    """The venv python for running the app — with an actionable error when
    setup has not happened. NEVER falls back to the system interpreter."""
    if not _have_venv():
        print("[error] the project virtual environment is missing.\n"
              "Run: python scripts/dev.py setup", file=sys.stderr)
        raise SystemExit(1)
    return str(_venv_python())


def _npm() -> str:
    # Windows npm is npm.cmd, which CreateProcess won't resolve from a bare
    # "npm" — resolve the full path so subprocess can launch it.
    return shutil.which("npm") or "npm"


def _require_node() -> None:
    missing = [t for t in ("node", "npm") if not _have(t)]
    if missing:
        print(f"[error] Node.js tooling missing: {', '.join(missing)}.\n"
              "Install Node.js 18+ (https://nodejs.org), then rerun.",
              file=sys.stderr)
        raise SystemExit(1)


def _require_frontend_deps() -> None:
    if not (FRONTEND / "node_modules").exists():
        print("[error] frontend dependencies are missing.\n"
              "Run: python scripts/dev.py setup", file=sys.stderr)
        raise SystemExit(1)


def _run(cmd: list[str], **kw) -> int:
    print(f"[run] {' '.join(str(c) for c in cmd)}")
    return subprocess.call([str(c) for c in cmd], **kw)


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #
def cmd_setup() -> int:
    _require_node()
    try:
        python = _ensure_venv()
    except RuntimeError as exc:
        print(f"[setup] ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"[setup] using project Python: {python}")
    print("[setup] upgrading pip inside the virtual environment…")
    subprocess.check_call([python, "-m", "pip", "install", "--upgrade", "pip"])
    print("[setup] installing Python deps inside the virtual environment…")
    subprocess.check_call([python, "-m", "pip", "install",
                           "-r", str(ROOT / "backend" / "requirements.txt")])
    print("[setup] installing Node deps…")
    subprocess.check_call([_npm(), "install"], cwd=FRONTEND)
    print("[setup] building curriculum pack…")
    subprocess.check_call([python, "scripts/build_packs.py", "--non-strict"],
                          cwd=ROOT)
    print("[setup] generating shared rule vectors…")
    subprocess.check_call([python, "scripts/gen_rule_vectors.py"], cwd=ROOT)
    print("[setup] applying database schema to a fresh DB…")
    if cmd_migrate_quiet() != 0:
        print("[setup] ERROR: schema migration failed", file=sys.stderr)
        return 1
    print("[setup] ✓")
    return 0


def _config_summary() -> list[str]:
    """Configuration consistency check — reports problems WITHOUT secrets."""
    lines = [
        "  PERSISTENCE_BACKEND: "
        f"{os.getenv('PERSISTENCE_BACKEND', 'sqlite (default)')}",
        "  TRANSLATION_PROVIDER: "
        f"{os.getenv('TRANSLATION_PROVIDER', 'mock (default)')}",
        "  LLM_PROVIDER: "
        f"{os.getenv('LLM_PROVIDER', 'mock (default)')}",
        f"  HF_TOKEN set: {bool(os.getenv('HF_TOKEN'))}",
        f"  LLM_API_KEY set: {bool(os.getenv('LLM_API_KEY'))}",
    ]
    if os.getenv("TRANSLATION_PROVIDER") == "hf_local" and not os.getenv("HF_TOKEN"):
        lines.append("  ⚠ hf_local set without HF_TOKEN — translation returns a "
                     "typed UNAVAILABLE error; the offline path is unaffected.")
    if os.getenv("LLM_PROVIDER", "mock") not in ("mock", "") and not os.getenv("LLM_API_KEY"):
        lines.append("  ⚠ LLM provider set without LLM_API_KEY — generation uses "
                     "the extractive fallback; the offline path is unaffected.")
    return lines


def cmd_doctor() -> int:
    print("=== SAARTHI doctor ===")
    venv_ok = _have_venv()
    print(f"  Venv:         {VENV}  exists={venv_ok}")
    if venv_ok:
        try:
            v = subprocess.check_output(
                [str(_venv_python()), "-c",
                 "import sys; print(sys.version.split()[0])"], text=True).strip()
            print(f"  Venv Python:  {v}")
        except (OSError, subprocess.CalledProcessError):
            print("  Venv Python:  unusable (rerun setup)")
    else:
        print("  Venv Python:  — (run `python scripts/dev.py setup`)")
    for tool in ("python3", "node", "npm", "docker"):
        path = shutil.which(tool)
        version = ""
        if path and tool in ("node", "npm"):
            try:
                version = subprocess.check_output(
                    [tool, "--version"]).decode().strip()
                version = f" (version={version})"
            except (OSError, subprocess.CalledProcessError):
                version = " (unusable)"
        marker = "" if path else "  ← MISSING (only needed for postgres/devops)"
        print(f"  {tool:12s} {path or 'not found'}{version}{marker}")
    print(f"  Frontend deps: {(FRONTEND / 'node_modules').exists()}")
    print(f"  Pack file:     {(ROOT / 'packs' / 'pack_class9_science_or_v1-1.0.0.json').exists()}")
    print(f"  Rule vectors:  {(ROOT / 'tests' / 'fixtures' / 'rule_vectors.json').exists()}")
    print(f"  .env file:     {(ROOT / '.env').exists()}")
    for line in _config_summary():
        print(line)
    print("=== end doctor ===")
    if not venv_ok or not (FRONTEND / "node_modules").exists():
        print("\nRun `python scripts/dev.py setup` first.")
    return 0


def cmd_start() -> int:
    python = _require_venv_python()
    _require_node()
    _require_frontend_deps()
    env = os.environ.copy()
    # Clear stale DATABASE_URL so the Settings default takes effect unless
    # the operator set it deliberately.
    if not env.get("DATABASE_URL") or env.get("DATABASE_URL").strip() == "":
        env.pop("DATABASE_URL", None)
    env.setdefault("PERSISTENCE_BACKEND", "sqlite")
    env.setdefault("TRANSLATION_PROVIDER", "mock")
    env.setdefault("LLM_PROVIDER", "mock")
    be_cmd = [python, "-m", "uvicorn", "app.main:app", "--app-dir", str(BACKEND),
              "--host", os.environ.get("BACKEND_HOST", "127.0.0.1"),
              "--port", str(os.environ.get("BACKEND_PORT", "8000")), "--reload"]
    fe_cmd = [_npm(), "run", "dev"]
    print(f"[start] backend: {' '.join(be_cmd)}")
    print(f"[start] frontend: {' '.join(fe_cmd)}  cwd={FRONTEND}")
    be = subprocess.Popen(be_cmd, cwd=ROOT, env=env)
    fe = subprocess.Popen(fe_cmd, cwd=FRONTEND, env=env)
    PID_FILE.write_text(f"{be.pid}\n{fe.pid}\n")
    print(f"[start] pids: backend={be.pid} frontend={fe.pid}")
    print("[start] Ctrl+C to stop both (or `python scripts/dev.py stop` from "
          "another terminal).")
    try:
        while be.poll() is None and fe.poll() is None:
            time.sleep(1)
        print("[start] one of the processes exited; stopping the other…")
    except KeyboardInterrupt:
        print("\n[start] Ctrl+C received, stopping…")
    finally:
        for p in (be, fe):
            if p.poll() is None:
                _terminate(p.pid)
        if PID_FILE.exists():
            PID_FILE.unlink()
    return 0


def _terminate(pid: int) -> None:
    """Terminate ONLY a process we own (started by this script and recorded
    in the PID file). Never broad-kills by name."""
    try:
        if sys.platform == "win32":
            subprocess.call(["taskkill", "/PID", str(pid), "/T", "/F"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        os.kill(pid, signal.SIGTERM)
        for _ in range(50):
            time.sleep(0.1)
            try:
                os.kill(pid, 0)
            except OSError:
                return
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except Exception as e:  # noqa: BLE001
        print(f"[stop] pid {pid}: {e}")


def _pid_is_ours(pid: int) -> bool:
    """Verify the PID still refers to a SAARTHI process before killing it —
    protects against PID reuse between runs."""
    if sys.platform == "win32":
        try:
            out = subprocess.check_output(
                ["wmic", "process", "where", f"ProcessId={pid}", "get",
                 "CommandLine"], text=True, stderr=subprocess.DEVNULL)
        except (OSError, subprocess.CalledProcessError):
            return False
        cmdline = out.lower()
        return "uvicorn" in cmdline or "vite" in cmdline or "dev.py" in cmdline
    proc = Path(f"/proc/{pid}/cmdline")
    if not proc.exists():
        return False
    try:
        cmdline = proc.read_bytes().decode("utf-8", "replace")
    except OSError:
        return False
    return ("uvicorn" in cmdline or "vite" in cmdline
            or "dev.py" in cmdline or "node" in cmdline)


def cmd_stop() -> int:
    if not PID_FILE.exists():
        print("[stop] no PID file; nothing to stop.")
        return 0
    pids = [int(x) for x in PID_FILE.read_text().split()]
    for pid in pids:
        if _pid_is_ours(pid):
            _terminate(pid)
            print(f"[stop] stopped {pid}")
        else:
            print(f"[stop] pid {pid} is not a SAARTHI process (stale PID file "
                  "entry); skipping")
    PID_FILE.unlink()
    return 0


def _wait_for_health(timeout_s: int = 60, port: int | None = None) -> bool:
    port = port or int(os.environ.get("BACKEND_PORT", "8000"))
    url = f"http://127.0.0.1:{port}/api/v1/health"
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(1)
    return False


def cmd_test() -> int:
    python = _require_venv_python()
    _require_node()
    _require_frontend_deps()
    rc = 0
    print("[test] backend unit + integration tests…")
    rc |= subprocess.call([python, "-m", "pytest", "backend/tests/", "-q"],
                          cwd=ROOT)
    print("[test] decision-rule parity (regenerate vectors, run both engines)…")
    rc |= subprocess.call([python, "scripts/gen_rule_vectors.py"], cwd=ROOT)
    rc |= subprocess.call([python, "-m", "pytest",
                           "backend/tests/test_decide_vectors.py", "-q"],
                          cwd=ROOT)
    print("[test] frontend tests (same vectors through the TS engine)…")
    rc |= subprocess.call([_npm(), "exec", "vitest", "run"], cwd=FRONTEND)
    print("[test] e2e smoke…")
    rc |= subprocess.call([python, "scripts/smoke_e2e.py"], cwd=ROOT)
    return rc


def cmd_check() -> int:
    python = _require_venv_python()
    _require_node()
    _require_frontend_deps()
    rc = 0
    print("[check] frontend type-check…")
    rc |= subprocess.call([_npm(), "run", "typecheck"], cwd=FRONTEND)
    print("[check] frontend lint…")
    lint = subprocess.call([_npm(), "run", "lint"], cwd=FRONTEND)
    if lint != 0:
        print("[check] WARNING: eslint reported errors (see above)")
        rc |= lint
    print("[check] frontend production build…")
    rc |= subprocess.call([_npm(), "run", "build"], cwd=FRONTEND)
    print("[check] backend import + configuration validation…")
    rc |= subprocess.call(
        [python, "-c",
         "import sys; sys.path.insert(0, 'backend'); "
         "from app.main import app; "
         "from app.core.settings import get_settings; "
         "problems = get_settings().validate_startup(); "
         "print('backend import OK'); "
         "[print('config:', p) for p in problems]"], cwd=ROOT)
    print("[check] hardcoded-URL scan on production assets…")
    dist = FRONTEND / "dist" / "assets"
    if dist.exists():
        hits = [str(p) for p in dist.rglob("*")
                if p.is_file()
                and b"127.0.0.1:8000" in p.read_bytes()]
        if hits:
            print("[check] ERROR: localhost URL baked into production assets:",
                  hits, file=sys.stderr)
            rc = 1
        else:
            print("[check] production assets clean (no hardcoded URLs)")
    return rc


def cmd_health() -> int:
    port = int(os.environ.get("BACKEND_PORT", "8000"))
    base = f"http://127.0.0.1:{port}"
    ok = _wait_for_health(timeout_s=30, port=port)
    if not ok:
        print(f"[health] FAIL: {base}/api/v1/health did not return 200 within 30s",
              file=sys.stderr)
        return 1
    with urllib.request.urlopen(f"{base}/api/v1/health", timeout=5) as resp:
        body = json.loads(resp.read().decode())
    print(f"[health] liveness OK (env={body.get('env')}, "
          f"persistence={body.get('persistence')}, "
          f"ruleset={body.get('ruleset_version')})")
    try:
        with urllib.request.urlopen(f"{base}/api/v1/readiness", timeout=5) as resp:
            ready = json.loads(resp.read().decode())
        print(f"[health] readiness: {ready.get('status')} "
              f"(core_decision_engine={ready.get('core_decision_engine')})")
    except (urllib.error.URLError, OSError) as e:
        print(f"[health] readiness probe failed (non-fatal): {e}")
    return 0


def cmd_migrate_quiet() -> int:
    """Apply schema.sql to a throwaway DB: proves fresh-DB creation AND
    that the guarded prior-schema migrations are idempotent."""
    code = (
        "import asyncio, os, sys, tempfile\n"
        "sys.path.insert(0, 'backend')\n"
        "tmp = tempfile.mktemp(suffix='.db')\n"
        "os.environ['DATABASE_URL'] = f'sqlite+aiosqlite:///{tmp}'\n"
        "os.environ['PERSISTENCE_BACKEND'] = 'sqlite'\n"
        "os.environ['TRANSLATION_PROVIDER'] = 'mock'\n"
        "os.environ['LLM_PROVIDER'] = 'mock'\n"
        "from app.adapters.persistence import Persistence, SCHEMA_PATH\n"
        "from sqlalchemy import text\n"
        "async def main():\n"
        "    # 1. Fresh database\n"
        "    p = Persistence.from_settings()\n"
        "    await p.apply_schema()\n"
        "    async with p.session() as s:\n"
        "        tables = {r[0] for r in (await s.execute(text(\n"
        "            \"SELECT name FROM sqlite_master WHERE type='table'\"))).fetchall()}\n"
        "    need = {'devices', 'learner_profiles', 'learner_events', 'learner_progress',\n"
        "            'refresh_tokens', 'auth_challenges', 'decisions', 'generation_records'}\n"
        "    missing = need - tables\n"
        "    assert not missing, f'fresh schema missing tables: {missing}'\n"
        "    # 2. Prior-schema migration: create the OLD learner_progress shape,\n"
        "    #    then re-apply and verify the guarded backfill.\n"
        "    await p.dispose()\n"
        "    import sqlite3\n"
        "    conn = sqlite3.connect(tmp)\n"
        "    conn.execute('DROP TABLE learner_progress')\n"
        "    conn.execute('CREATE TABLE learner_progress (learner_id TEXT, '\n"
        "                 'concept_id TEXT, p_known REAL DEFAULT 0.4, '\n"
        "                 'band TEXT, attempts INTEGER, correct INTEGER, '\n"
        "                 'last_updated_event_seq INTEGER, PRIMARY KEY(learner_id, concept_id))')\n"
        "    conn.execute(\"INSERT INTO learner_progress VALUES ('lrn_x', 'c0001', 0.5, 'partial', 2, 1, 3)\")\n"
        "    conn.commit(); conn.close()\n"
        "    p2 = Persistence.from_settings()\n"
        "    await p2.apply_schema()\n"
        "    async with p2.session() as s:\n"
        "        row = (await s.execute(text(\n"
        "            'SELECT p_bp FROM learner_progress WHERE learner_id=\\\"lrn_x\\\"'))).fetchone()\n"
        "    assert row and row[0] == 5000, f'backfill wrong: {row}'\n"
        "    # 3. Idempotent re-apply\n"
        "    await p2.apply_schema()\n"
        "    await p2.dispose()\n"
        "    os.unlink(tmp)\n"
        "    print('migrations OK: fresh schema + prior-schema backfill (p_bp=5000) + idempotent')\n"
        "asyncio.run(main())\n"
    )
    python = _require_venv_python()
    return subprocess.call([python, "-c", code], cwd=ROOT)


def cmd_migrate() -> int:
    print("[migrate] verifying schema on a fresh DB and a prior-schema DB…")
    return cmd_migrate_quiet()


def cmd_parity() -> int:
    """Cross-language decision parity: regenerate shared vectors, then run
    BOTH engines against them (Python pytest + TypeScript vitest)."""
    python = _require_venv_python()
    _require_node()
    _require_frontend_deps()
    rc = 0
    print("[parity] regenerating shared vectors…")
    rc |= subprocess.call([python, "scripts/gen_rule_vectors.py"], cwd=ROOT)
    print("[parity] Python engine…")
    rc |= subprocess.call([python, "-m", "pytest",
                           "backend/tests/test_decide_vectors.py", "-q"],
                          cwd=ROOT)
    print("[parity] TypeScript engine…")
    rc |= subprocess.call([_npm(), "exec", "vitest", "run",
                           "tests/decide.test.ts"], cwd=FRONTEND)
    if rc == 0:
        print("[parity] ✓ identical results on the shared vector set")
    return rc


def cmd_smoke() -> int:
    """Optional real-provider smoke: only when credentials exist. Reports
    honestly when real inference is NOT verified."""
    python = _require_venv_python()
    print("[smoke] core e2e smoke (no credentials needed)…")
    rc = subprocess.call([python, "scripts/smoke_e2e.py"], cwd=ROOT)
    if os.getenv("HF_TOKEN"):
        print("[smoke] HF_TOKEN present — running translation provider probe…")
        code = (
            "import asyncio, os, sys\n"
            "sys.path.insert(0, 'backend')\n"
            "os.environ.setdefault('TRANSLATION_PROVIDER', 'hf_local')\n"
            "from app.adapters.ai.translation import HuggingFaceTranslationProvider\n"
            "async def main():\n"
            "    p = HuggingFaceTranslationProvider()\n"
            "    result = await p.translate('matter', 'en', 'or')\n"
            "    health = await p.health()\n"
            "    print('provider health:', health)\n"
            "    if hasattr(result, 'error_code'):\n"
            "        print(f'typed error: {result.error_code} — {result.detail_dev[:200]}')\n"
            "        print('real inference NOT verified')\n"
            "        return 2\n"
            "    print(f'real inference verified: {result.text[:80]!r}')\n"
            "    return 0\n"
            "raise SystemExit(asyncio.run(main()))\n"
        )
        rc |= subprocess.call([python, "-c", code], cwd=ROOT)
    else:
        print("[smoke] HF_TOKEN not set — real IndicTrans2 inference remains "
              "UNVERIFIED (the provider contract is covered by tests; the "
              "offline path never needs credentials).")
    return rc


def cmd_reset_data() -> int:
    if not sys.stdin.isatty():
        print("[reset-data] Destructive operation requires interactive confirm.")
        return 1
    confirm = input("This will delete the local SQLite DB and all local pack "
                    "installs. Type 'DELETE' to confirm: ")
    if confirm != "DELETE":
        print("[reset-data] aborted.")
        return 1
    db_url = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./saarthi.db")
    if "sqlite" in db_url:
        path = db_url.split("///")[-1]
        if os.path.exists(path):
            os.remove(path)
            print(f"[reset-data] removed {path}")
    else:
        print("[reset-data] non-sqlite backend; not auto-resetting.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="dev.py", description="SAARTHI master development script")
    ap.add_argument("cmd", nargs="?", choices=[
        "setup", "doctor", "start", "stop", "test", "check", "health",
        "migrate", "parity", "smoke", "reset-data"])
    ap.add_argument("--reset-data", action="store_true")
    args = ap.parse_args()
    if args.reset_data:
        return cmd_reset_data()
    if args.cmd is None:
        ap.error("a command is required (or use --reset-data)")
    return {
        "setup": cmd_setup, "doctor": cmd_doctor, "start": cmd_start,
        "stop": cmd_stop, "test": cmd_test, "check": cmd_check,
        "health": cmd_health, "migrate": cmd_migrate, "parity": cmd_parity,
        "smoke": cmd_smoke, "reset-data": cmd_reset_data,
    }[args.cmd]()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # Piping output into `head` etc. is not an error.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
