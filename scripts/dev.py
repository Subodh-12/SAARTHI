#!/usr/bin/env python3
"""SAARTHI master dev script — one entry point for setup/start/test/stop.

Usage:
    python scripts/dev.py setup     # install python+node deps
    python scripts/dev.py start    # start backend + frontend (foreground)
    python scripts/dev.py test     # run pytest + vitest + e2e smoke
    python scripts/dev.py check    # lint + typecheck + build
    python scripts/dev.py stop     # stop running backend + frontend
    python scripts/dev.py doctor   # diagnose environment
    python scripts/dev.py --reset-data   # DESTRUCTIVE: wipe SQLite + IndexedDB (server-side only)

Cross-platform. Uses python venv at ./.venv; uses ./frontend/node_modules.
"""
from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv"
FRONTEND = ROOT / "frontend"
BACKEND = ROOT / "backend"
PID_FILE = ROOT / ".dev_pids"


def _py() -> str:
    if sys.platform == "win32":
        p = VENV / "Scripts" / "python.exe"
        if p.exists():
            return str(p)
    else:
        p = VENV / "bin" / "python"
        if p.exists():
            return str(p)
    # Fall back to the running interpreter (or system python3)
    return sys.executable or "python3"


def _have_venv() -> bool:
    return (VENV / "bin" / "python").exists() or (VENV / "Scripts" / "python.exe").exists()


def _ensure_venv() -> str:
    """Create and validate the project venv; never install into system Python."""
    if not _have_venv():
        bootstrap_python = sys.executable or shutil.which("python3") or shutil.which("python")
        if not bootstrap_python:
            raise RuntimeError("Python was not found. Install Python 3, then rerun setup.")
        print(f"[setup] creating virtual environment at {VENV}…")
        try:
            subprocess.check_call([bootstrap_python, "-m", "venv", str(VENV)])
        except (OSError, subprocess.CalledProcessError) as exc:
            raise RuntimeError(
                "Could not create the project virtual environment. On Arch Linux, "
                "ensure the system Python/venv support is installed, then rerun ./run.sh setup."
            ) from exc

    if not _have_venv():
        raise RuntimeError(f"Virtual environment was not created at {VENV}.")

    python = _py()
    try:
        # A path existing is not enough: reject broken/stale venvs before pip is run.
        subprocess.check_call(
            [python, "-c", "import sys; assert sys.prefix != sys.base_prefix"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(
            f"The project virtual environment at {VENV} is not usable. "
            "Remove the broken .venv directory and rerun ./run.sh setup."
        ) from exc

    try:
        subprocess.check_call(
            [python, "-m", "pip", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        # Some Python builds omit pip from newly-created environments.
        subprocess.check_call([python, "-m", "ensurepip", "--upgrade"])

    return python


def _npm() -> str:
    # On Windows npm is npm.cmd, which CreateProcess won't resolve from a bare
    # "npm" — resolve the full path so subprocess can launch it.
    return shutil.which("npm") or "npm"


def _have(binname: str) -> bool:
    return shutil.which(binname) is not None


def cmd_setup() -> int:
    if not _have("node") or not _have("npm"):
        print("[setup] ERROR: Node.js and npm are required. Install Node.js/npm, then rerun ./run.sh setup.", file=sys.stderr)
        return 1
    try:
        python = _ensure_venv()
    except RuntimeError as exc:
        print(f"[setup] ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"[setup] using project Python: {python}")
    print("[setup] upgrading pip inside the virtual environment…")
    subprocess.check_call([python, "-m", "pip", "install", "--upgrade", "pip"])
    print("[setup] installing Python deps inside the virtual environment…")
    subprocess.check_call([python, "-m", "pip", "install", "-r", str(ROOT / "backend" / "requirements.txt")])
    print("[setup] installing Node deps…")
    subprocess.check_call([_npm(), "install"], cwd=FRONTEND)
    print("[setup] building curriculum pack…")
    subprocess.check_call([python, "scripts/build_packs.py", "--non-strict"], cwd=ROOT)
    print("[setup] generating rule vectors…")
    subprocess.check_call([python, "scripts/gen_rule_vectors.py"], cwd=ROOT)
    print("[setup] ✓")
    return 0


def cmd_doctor() -> int:
    print("=== SAARTHI doctor ===")
    python = _py()
    try:
        python_version = subprocess.check_output(
            [python, "-c", "import sys; print(sys.version.split()[0])"], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        python_version = "unavailable"
    print(f"  Python:       {python} (version={python_version})")
    print(f"  Venv:         {VENV}  exists={VENV.exists()}")
    print(f"  Node:         {shutil.which('node')}")
    if shutil.which("node"):
        out = subprocess.check_output(["node", "--version"]).decode().strip()
        print(f"                version={out}")
    print(f"  npm:          {shutil.which('npm')}")
    print(f"  Frontend nm:  {(FRONTEND/'node_modules').exists()}")
    print(f"  Pack file:    {(ROOT/'packs'/'pack_class9_science_or_v1-1.0.0.json').exists()}")
    print(f"  Rule vectors: {(ROOT/'tests'/'fixtures'/'rule_vectors.json').exists()}")
    print(f"  DB file:      {bool(os.getenv('DATABASE_URL'))}")
    print(f"  .env file:    {(ROOT/'.env').exists()}")
    print(f"  PERSISTENCE_BACKEND: {os.getenv('PERSISTENCE_BACKEND', 'sqlite (default)')}")
    print(f"  TRANSLATION_PROVIDER: {os.getenv('TRANSLATION_PROVIDER', 'mock (default)')}")
    print(f"  LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'mock (default)')}")
    print(f"  HF_TOKEN set: {bool(os.getenv('HF_TOKEN'))}")
    print(f"  LLM_API_KEY set: {bool(os.getenv('LLM_API_KEY'))}")
    print("=== end doctor ===")
    if not (FRONTEND / "node_modules").exists():
        print("\nRun `python scripts/dev.py setup` first.")
    return 0


def cmd_start() -> int:
    if not _have_venv() or not (FRONTEND / "node_modules").exists():
        print("Run `./run.sh setup` first.", file=sys.stderr)
        return 1
    # Apply schema + seed pack (silent)
    env = os.environ.copy()
    # Clear stale DATABASE_URL so the Settings default takes effect
    if not env.get("DATABASE_URL") or env.get("DATABASE_URL").strip() == "":
        env.pop("DATABASE_URL", None)
    env.setdefault("PERSISTENCE_BACKEND", "sqlite")
    env.setdefault("TRANSLATION_PROVIDER", "mock")
    env.setdefault("LLM_PROVIDER", "mock")
    be_cmd = [_py(), "-m", "uvicorn", "app.main:app", "--app-dir", str(BACKEND),
              "--host", os.environ.get("BACKEND_HOST", "127.0.0.1"),
              "--port", str(os.environ.get("BACKEND_PORT", "8000")), "--reload"]
    fe_cmd = [_npm(), "run", "dev"]
    print(f"[start] backend: {' '.join(be_cmd)}")
    print(f"[start] frontend: {' '.join(fe_cmd)}  cwd={FRONTEND}")
    be = subprocess.Popen(be_cmd, cwd=ROOT, env=env)
    fe = subprocess.Popen(fe_cmd, cwd=FRONTEND, env=env)
    PID_FILE.write_text(f"{be.pid}\n{fe.pid}\n")
    print(f"[start] pids: backend={be.pid} frontend={fe.pid}")
    print("[start] Ctrl+C to stop both.")
    try:
        # Wait for either to exit
        while be.poll() is None and fe.poll() is None:
            time.sleep(1)
        print("[start] one of the processes exited; stopping the other…")
    except KeyboardInterrupt:
        print("\n[start] Ctrl+C received, stopping…")
    finally:
        for p in (be, fe):
            if p.poll() is None:
                try: p.send_signal(signal.SIGTERM)
                except: pass
                try: p.wait(timeout=5)
                except:
                    try: p.kill()
                    except: pass
        if PID_FILE.exists(): PID_FILE.unlink()
    return 0


def cmd_stop() -> int:
    if not PID_FILE.exists():
        print("[stop] no PID file; nothing to stop."); return 0
    pids = [int(x) for x in PID_FILE.read_text().split()]
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"[stop] sent SIGTERM to {pid}")
        except ProcessLookupError:
            print(f"[stop] pid {pid} not running")
        except Exception as e:
            print(f"[stop] pid {pid}: {e}")
    PID_FILE.unlink()
    return 0


def cmd_test() -> int:
    if not _have_venv() or not (FRONTEND / "node_modules").exists():
        print("Run `./run.sh setup` first.", file=sys.stderr)
        return 1
    rc = 0
    print("[test] pytest backend tests…")
    rc |= subprocess.call([_py(), "-m", "pytest", "backend/tests/", "-q"], cwd=ROOT)
    print("[test] vitest frontend tests…")
    rc |= subprocess.call([_npm(), "exec", "vitest", "run", "--reporter=default"], cwd=FRONTEND)
    print("[test] e2e smoke…")
    rc |= subprocess.call([_py(), "scripts/smoke_e2e.py"], cwd=ROOT)
    return rc


def cmd_check() -> int:
    if not _have_venv() or not (FRONTEND / "node_modules").exists():
        print("Run `./run.sh setup` first.", file=sys.stderr)
        return 1
    rc = 0
    print("[check] frontend build…")
    rc |= subprocess.call([_npm(), "run", "build"], cwd=FRONTEND)
    print("[check] backend import…")
    rc |= subprocess.call([_py(), "-c", "import sys; sys.path.insert(0, 'backend'); from app.main import app; print('OK')"], cwd=ROOT)
    return rc


def cmd_reset_data() -> int:
    if not sys.stdin.isatty():
        print("[reset-data] Destructive operation requires interactive confirm."); return 1
    confirm = input("This will delete the local SQLite DB and all local pack installs. Type 'DELETE' to confirm: ")
    if confirm != "DELETE":
        print("[reset-data] aborted."); return 1
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
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["setup", "start", "test", "check", "stop", "doctor", "reset-data"])
    ap.add_argument("--reset-data", action="store_true")
    args = ap.parse_args()
    if args.reset_data:
        return cmd_reset_data()
    if args.cmd is None:
        ap.error("a command is required (or use --reset-data)")
    return {
        "setup": cmd_setup, "start": cmd_start, "test": cmd_test, "check": cmd_check,
        "stop": cmd_stop, "doctor": cmd_doctor, "reset-data": cmd_reset_data,
    }[args.cmd]()


if __name__ == "__main__":
    sys.exit(main())
