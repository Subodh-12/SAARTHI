"""M3 pack build + validation tests.

The pack artifacts are (re)built by a module fixture so the tests validate
the CURRENT builder code deterministically instead of stale committed
binaries. The archive's inner manifest carries archive_sha256="" and
archive_byte_size=0 (they cover the archive itself); the standalone JSON
manifest carries the real values — tests normalise those two fields when
comparing (documented in PackManifest and build_packs.py).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "backend"))
sys.path.insert(0, str(REPO / "scripts"))

PACK_JSON = REPO / "packs" / "pack_class9_science_or_v1-1.0.0.json"
PACK_GZ = REPO / "packs" / "pack_class9_science_or_v1-1.0.0.srt.tar.gz"


@pytest.fixture(scope="module", autouse=True)
def _built_pack():
    """Rebuild the pack once so tests exercise the current builder."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "build_packs", REPO / "scripts" / "build_packs.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.build_pack(strict=False)
    return None


def _load_json_with_blank_archive_fields() -> bytes:
    """Canonical JSON bytes with the archive integrity fields blanked."""
    data = json.loads(PACK_JSON.read_text(encoding="utf-8"))
    data["manifest"]["archive_sha256"] = ""
    data["manifest"]["archive_byte_size"] = 0
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def test_pack_exists():
    assert PACK_JSON.exists(), "Run scripts/build_packs.py first"
    assert PACK_GZ.exists()


def test_pack_manifest_valid():
    if not PACK_JSON.exists():
        pytest.skip("pack not built")
    data = json.loads(PACK_JSON.read_text(encoding="utf-8"))
    m = data["manifest"]
    assert m["pack_id"] == "pack_class9_science_or_v1"
    assert m["version"] == "1.0.0"
    assert m["language"] == "or"
    assert m["byte_size"] > 0
    assert len(m["checksum_sha256"]) == 64
    assert len(m["chapters"]) == 3


def test_pack_checksum_self_consistent():
    """Verify the stored checksum matches SHA-256 of the blob with the
    checksum field blanked AND the archive fields blanked (canonical
    verification; the archive fields sit at their final key positions)."""
    if not PACK_JSON.exists():
        pytest.skip("pack not built")
    data = json.loads(PACK_JSON.read_text(encoding="utf-8"))
    stored = data["manifest"]["checksum_sha256"]
    # Blank the checksum and archive fields, re-serialize canonically
    data["manifest"]["checksum_sha256"] = ""
    data["manifest"]["archive_sha256"] = ""
    data["manifest"]["archive_byte_size"] = 0
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    actual = hashlib.sha256(blob).hexdigest()
    assert stored == actual, "stored checksum does not match canonical verification"


def test_pack_gzip_payload_matches_json():
    """The archive payload equals the standalone JSON with the archive
    integrity fields blanked (the inner manifest cannot carry the archive's
    own hash — documented in PackManifest.archive_sha256)."""
    if not PACK_GZ.exists() or not PACK_JSON.exists():
        pytest.skip("pack not built")
    with gzip.open(PACK_GZ, "rb") as f:
        gz_data = f.read()
    assert gz_data == _load_json_with_blank_archive_fields()


def test_pack_has_3_chapters_9_concepts():
    if not PACK_JSON.exists():
        pytest.skip("pack not built")
    data = json.loads(PACK_JSON.read_text())
    assert len(data["chapters"]) == 3
    assert len(data["concepts"]) == 9  # 3 concepts × 3 chapters
    assert len(data["chunks"]) >= 9  # ≥1 chunk per concept
    assert len(data["questions"]) >= 9
    assert len(data["glossary"]) >= 20  # ≥20 glossary entries


def test_pack_questions_have_valid_answer_keys():
    """Each MCQ must have a valid correct_option; each short_answer a rubric.
    Every question carries a revision number and an answer-key hash (v2)."""
    if not PACK_JSON.exists():
        pytest.skip("pack not built")
    data = json.loads(PACK_JSON.read_text())
    for q in data["questions"]:
        assert q["qtype"] in ("mcq", "short_answer")
        assert int(q.get("revision", 0)) >= 1, "question missing revision"
        assert len(q.get("answer_key_hash", "")) == 32, "question missing answer_key_hash"
        if q["qtype"] == "mcq":
            assert q.get("correct_option") is not None
            assert 0 <= q["correct_option"] < len(q["options"])
            assert len(q["options"]) >= 2
        else:
            assert q.get("rubric_or")
            assert q.get("expected_concepts")


def test_pack_chapter_ids_consistent():
    if not PACK_JSON.exists():
        pytest.skip("pack not built")
    data = json.loads(PACK_JSON.read_text())
    declared = set(data["manifest"]["chapters"])
    actual = set(c["chapter_id"] for c in data["chapters"])
    assert declared == actual


def test_pack_chunks_have_odia_text():
    if not PACK_JSON.exists():
        pytest.skip("pack not built")
    data = json.loads(PACK_JSON.read_text())
    for ch in data["chunks"]:
        text = ch["text_or"]
        assert text
        # ≥1 Odia unicode char
        assert any("\u0B00" <= c <= "\u0B7F" for c in text), \
            f"chunk {ch['chunk_id']} has no Odia chars"


def test_pack_chunk_word_count_in_range():
    """Each chunk should have 40-280 Odia words."""
    if not PACK_JSON.exists():
        pytest.skip("pack not built")
    data = json.loads(PACK_JSON.read_text())
    for ch in data["chunks"]:
        n = len([w for w in ch["text_or"].split() if any(c.isalpha() for c in w)])
        assert 40 <= n <= 280, f"chunk {ch['chunk_id']}: {n} words out of range"
