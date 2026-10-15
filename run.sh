#!/usr/bin/env bash
# SAARTHI master script (POSIX shells) — thin wrapper around scripts/dev.py.
#
# Usage:  ./run.sh setup | doctor | start | stop | test | check | health |
#              migrate | parity | smoke
#
# The Python work always happens in the project virtual environment
# (.venv); the wrapper only bootstraps the interpreter that can CREATE it.
# See scripts/dev.py for the full command reference and documentation of
# the required environment variables (.env.example documents them all).
set -euo pipefail
cd "$(dirname "$0")"

if [ -x .venv/bin/python ]; then
  PY=.venv/bin/python
else
  # Bootstrap interpreter: only used to CREATE the venv (never to install
  # into system Python).
  if command -v python3 >/dev/null 2>&1; then
    PY=python3
  elif command -v python >/dev/null 2>&1; then
    PY=python
  else
    echo "run.sh: Python 3 is required. Install Python 3 (with the venv" >&2
    echo "module) and rerun: ./run.sh setup" >&2
    exit 1
  fi
fi

exec "$PY" scripts/dev.py "$@"
