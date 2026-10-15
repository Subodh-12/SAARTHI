"""Pack loader — reads the built curriculum pack into runtime memory.

Loads `packs/pack_class9_science_or_v1-1.0.0.json` once, indexes it by
chunk_id / concept_id / question_id / chapter_id, and exposes lookup helpers.

The pack is content-only; it does not depend on the DB. The DB stores the
manifest and per-device installed-pack state.
"""
from __future__ import annotations

import functools
import json
import os
import time
from pathlib import Path
from typing import Optional

from ..domain.schemas import (
    Chapter, Chunk, Concept, GlossaryEntry, PackManifest, Question,
)


class PackContentIndex:
    """In-memory index of a built curriculum pack."""

    def __init__(self, payload: dict) -> None:
        m = payload["manifest"]
        self.manifest = PackManifest(
            pack_id=m["pack_id"], version=m["version"],
            content_version=m["content_version"], language=m["language"],
            byte_size=m["byte_size"], checksum_sha256=m["checksum_sha256"],
            min_app_version=m["min_app_version"], licence=m["licence"],
            source_refs=m.get("source_refs", []),
            chapters=m["chapters"], created_at=m["created_at"],
        )
        self.chapters: dict[str, Chapter] = {
            c["chapter_id"]: Chapter(
                chapter_id=c["chapter_id"], subject=c.get("subject", "science"),
                grade=c.get("grade", "class9"), title_or=c["title_or"],
                title_en=c["title_en"], summary_or=c.get("summary_or", ""),
                source_refs=c.get("source_refs", []),
            ) for c in payload["chapters"]
        }
        self.concepts: dict[str, Concept] = {
            c["concept_id"]: Concept(
                concept_id=c["concept_id"], title_or=c["title_or"],
                title_en=c["title_en"], chapter_id=c["chapter_id"],
                prerequisites=c.get("prerequisites", []),
                summary_or=c.get("summary_or", ""),
                source_refs=c.get("source_refs", []),
            ) for c in payload["concepts"]
        }
        self.chunks: dict[str, Chunk] = {
            ch["chunk_id"]: Chunk(
                chunk_id=ch["chunk_id"], concept_id=ch["concept_id"],
                chapter_id=ch["chapter_id"], ordinal=ch["ordinal"],
                text_or=ch["text_or"], source_ref=ch["source_ref"],
                glossary_refs=ch.get("glossary_refs", []),
            ) for ch in payload["chunks"]
        }
        self.questions: dict[str, Question] = {
            q["question_id"]: Question(
                question_id=q["question_id"], concept_id=q["concept_id"],
                chapter_id=q.get("chapter_id", ""),
                bloom_level=q.get("bloom_level", "remember"),
                qtype=q["qtype"], prompt_or=q["prompt_or"],
                options=q.get("options", []),
                correct_option=q.get("correct_option"),
                rubric_or=q.get("rubric_or"),
                expected_concepts=q.get("expected_concepts", []),
                explanation_or=q["explanation_or"],
                difficulty=q["difficulty"],
                misconception_tag=q.get("misconception_tag"),
                misconception_options={
                    str(k): v.strip() for k, v in (q.get("misconception_options") or {}).items()
                    if isinstance(v, str) and v.strip()
                },
                review_status=q.get("review_status"),
                source_ref=q.get("source_ref", ""),
                revision=int(q.get("revision", 1)),
                answer_key_hash=q.get("answer_key_hash", ""),
                status=q.get("status", "active"),
            ) for q in payload["questions"]
        }
        self.glossary: list[GlossaryEntry] = [
            GlossaryEntry(
                term_or=g["term_or"], term_en=g["term_en"],
                definition_or=g["definition_or"], definition_en=g["definition_en"],
            ) for g in payload["glossary"]
        ]
        self.glossary_by_en = {g.term_en: g for g in self.glossary}
        self.glossary_by_or = {g.term_or: g for g in self.glossary}
        # Per-chapter concept order (used by deterministic decision engine)
        self.concept_order: list[str] = [c["concept_id"] for c in payload["concepts"]]
        # Chapter-for-concept map (used by decide())
        self.chapter_for_concept: dict[str, str] = {
            c["concept_id"]: c["chapter_id"] for c in payload["concepts"]
        }
        # Prereq map
        self.prereqs: dict[str, list[str]] = {
            c["concept_id"]: c.get("prerequisites", []) for c in payload["concepts"]
        }
        # Concepts grouped by pack — every concept in this pack belongs to the
        # single pack that carries it (v2 packs are chapter-scoped).
        self._pack_id = m["pack_id"]

    def required_pack_for_concept(self) -> dict[str, str]:
        """concept_id -> pack_id that serves its content (v2 offline rule)."""
        return {cid: self._pack_id for cid in self.concept_order}

    def installed_pack_versions(self, device_packs: Optional[dict[str, str]] = None) -> dict[str, int]:
        """Installed pack versions for the decision input.

        The SERVER treats its own served packs as installed for decision
        purposes (delivery feasibility is about the target device — when a
        device pack list is supplied it wins)."""
        try:
            version_int = int(str(self.manifest.version).split(".")[0] or 1)
        except ValueError:
            version_int = 1
        if device_packs is not None:
            return {pid: int(v) for pid, v in device_packs.items()
                    if str(v).split(".")[0].isdigit()}
        return {self._pack_id: version_int}

    def get_chunk(self, chunk_id: str) -> Optional[Chunk]:
        return self.chunks.get(chunk_id)

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        return self.concepts.get(concept_id)

    def get_question(self, question_id: str) -> Optional[Question]:
        return self.questions.get(question_id)

    def get_chapter(self, chapter_id: str) -> Optional[Chapter]:
        return self.chapters.get(chapter_id)

    def list_questions_for_concept(
        self, concept_id: str, difficulty: Optional[str] = None, bloom_level: Optional[str] = None
    ) -> list[Question]:
        out = [q for q in self.questions.values() if q.concept_id == concept_id]
        if difficulty:
            out = [q for q in out if q.difficulty == difficulty]
        if bloom_level:
            bl_str = str(bloom_level.value if hasattr(bloom_level, "value") else bloom_level).lower()
            out = [q for q in out if str(q.bloom_level.value if hasattr(q.bloom_level, "value") else q.bloom_level).lower() == bl_str]
        return out

    def available_bloom_levels_for_concept(self, concept_id: str) -> list[str]:
        levels = set()
        for q in self.questions.values():
            if q.concept_id == concept_id and getattr(q, "status", "active") == "active":
                lvl = q.bloom_level
                lvl_str = lvl.value if hasattr(lvl, "value") else str(lvl)
                levels.add(lvl_str.lower())
        order = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
        return [l for l in order if l in levels]

    def list_chunks_for_concept(self, concept_id: str) -> list[Chunk]:
        return sorted(
            [c for c in self.chunks.values() if c.concept_id == concept_id],
            key=lambda c: c.ordinal,
        )


_PACK_CACHE: dict[str, PackContentIndex] = {}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_pack_index(pack_path: str | None = None) -> PackContentIndex:
    """Load (and cache) a built curriculum pack from disk."""
    configured = pack_path or os.environ.get("SAARTHI_PACK_PATH")
    if configured:
        candidate = Path(configured)
        path = candidate if candidate.is_absolute() else _project_root() / candidate
    else:
        path = _project_root() / "packs" / "pack_class9_science_or_v1-1.0.0.json"
    if str(path) in _PACK_CACHE:
        return _PACK_CACHE[str(path)]
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    idx = PackContentIndex(payload)
    _PACK_CACHE[str(path)] = idx
    return idx


def reset_pack_cache() -> None:
    _PACK_CACHE.clear()


__all__ = ["PackContentIndex", "load_pack_index", "reset_pack_cache"]
