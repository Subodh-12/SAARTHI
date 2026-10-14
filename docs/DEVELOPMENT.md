# SAARTHI Development Guide

## Supported local workflow

This repository is verified in the current workspace using the following commands.

### Backend tests

```bash
cd /home/elemento/SAARTHI
backend/.venv/bin/python -m pytest -q
```

### Frontend build

```bash
cd /home/elemento/SAARTHI/frontend
npm install --silent
npm run build
```

### Pack rebuild and validation

```bash
cd /home/elemento/SAARTHI
backend/.venv/bin/python scripts/build_packs.py
backend/.venv/bin/python -m pytest -q backend/tests/test_pack_build.py
```

### Application startup

```bash
cd /home/elemento/SAARTHI
./run.sh start
```

or on PowerShell:

```powershell
cd /home/elemento/SAARTHI
./run.ps1 start
```

## PostgreSQL 16 workflow

The project includes a PostgreSQL 16 service in `docker-compose.yml`.

```bash
cd /home/elemento/SAARTHI
docker compose up -d postgres
```

Then set a Postgres database URL before starting the app or tests:

```bash
export PERSISTENCE_BACKEND=postgres
export DATABASE_URL=postgresql+asyncpg://saarthi:saarthi@localhost:5432/saarthi
```

This environment was not used to run a live Postgres migration pass during this audit, so that path is documented but not claimed as verified at runtime.

## Safe environment notes

- The default local code path runs against SQLite.
- PostgreSQL is the documented production-parity backend, but it must be explicitly configured.
- Live AI provider paths (HF/OpenAI) require external credentials and are not enabled by default.
- Study-room and demo room seed data is enabled in dev/test startup when the app is run under the local dev/test settings.

## Seed and demo commands

```bash
cd /home/elemento/SAARTHI/backend
../.venv/bin/python -m app.scripts.reseed_rooms
```

The repo also includes:

- `scripts/dev.py` as the master orchestration script
- `scripts/build_packs.py` for curriculum pack generation
- `scripts/smoke_e2e.py` for smoke verification

## Current verified status

As of this audit:

- Backend suite: passing
- Frontend production build: passing
- Pack integrity: passing
- PostgreSQL runtime path: configured but not executed in this environment
