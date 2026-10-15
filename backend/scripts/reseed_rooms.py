#!/usr/bin/env python3
"""Dev command: wipe and reseed demo study rooms.

Usage (from backend/): .venv/bin/python scripts/reseed_rooms.py
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("PERSISTENCE_BACKEND", "sqlite")

from app.adapters.persistence import get_persistence, dispose_persistence
from app.services.rooms_seed import reseed_rooms


async def main() -> None:
    p = await get_persistence()
    n = await reseed_rooms(p)
    print(f"reseeded {n} demo study rooms")
    await dispose_persistence()


if __name__ == "__main__":
    asyncio.run(main())
