"""001_initial_schema — SAARTHI Design Document v2 core tables.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-15
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Devices & learners
    op.execute("""
    CREATE TABLE IF NOT EXISTS devices (
      device_id          TEXT PRIMARY KEY,
      hardware_label     TEXT NOT NULL DEFAULT 'shared-android-low-end',
      public_key_spki    TEXT,
      created_at         BIGINT NOT NULL,
      last_seen_at       BIGINT,
      revoked_at         BIGINT
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS learner_profiles (
      learner_id         TEXT PRIMARY KEY,
      display_label      TEXT NOT NULL DEFAULT '',
      locale             TEXT NOT NULL DEFAULT 'or',
      grade              TEXT NOT NULL DEFAULT 'class9',
      subject            TEXT NOT NULL DEFAULT 'science',
      pin_hash           TEXT,
      created_at         BIGINT NOT NULL,
      active_device_id   TEXT REFERENCES devices(device_id) ON DELETE SET NULL,
      UNIQUE (active_device_id)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS learner_devices (
      learner_id         TEXT NOT NULL REFERENCES learner_profiles(learner_id) ON DELETE CASCADE,
      device_id          TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
      status             TEXT NOT NULL DEFAULT 'active',
      first_seen_at      BIGINT NOT NULL,
      last_active_at     BIGINT NOT NULL,
      PRIMARY KEY (learner_id, device_id)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS device_tokens (
      device_id          TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
      token_hash         TEXT NOT NULL,
      issued_at          BIGINT NOT NULL,
      expires_at         BIGINT NOT NULL,
      revoked            INTEGER NOT NULL DEFAULT 0
    );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_device_tokens_hash ON device_tokens (token_hash, revoked, expires_at);")

    op.execute("""
    CREATE TABLE IF NOT EXISTS refresh_tokens (
      id                 TEXT PRIMARY KEY,
      device_id          TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
      token_hash         TEXT NOT NULL,
      issued_at          BIGINT NOT NULL,
      expires_at         BIGINT NOT NULL,
      used_at            BIGINT,
      revoked            INTEGER NOT NULL DEFAULT 0
    );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_hash ON refresh_tokens (token_hash, revoked, expires_at);")

    op.execute("""
    CREATE TABLE IF NOT EXISTS auth_challenges (
      nonce              TEXT PRIMARY KEY,
      device_id          TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
      created_at         BIGINT NOT NULL,
      expires_at         BIGINT NOT NULL,
      used_at            BIGINT
    );
    """)

    # 2. Content & packs
    op.execute("""
    CREATE TABLE IF NOT EXISTS chapters (
      chapter_id         TEXT PRIMARY KEY,
      subject            TEXT NOT NULL,
      grade              TEXT NOT NULL,
      title_or           TEXT NOT NULL,
      title_en           TEXT NOT NULL,
      summary_or         TEXT NOT NULL DEFAULT '',
      source_refs_json   TEXT NOT NULL DEFAULT '[]'
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS concepts (
      concept_id         TEXT PRIMARY KEY,
      chapter_id         TEXT NOT NULL REFERENCES chapters(chapter_id) ON DELETE CASCADE,
      title_or           TEXT NOT NULL,
      title_en           TEXT NOT NULL,
      summary_or         TEXT NOT NULL DEFAULT '',
      prerequisites_json TEXT NOT NULL DEFAULT '[]',
      source_refs_json   TEXT NOT NULL DEFAULT '[]'
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
      chunk_id           TEXT PRIMARY KEY,
      concept_id         TEXT NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
      chapter_id         TEXT NOT NULL,
      title_or           TEXT NOT NULL,
      text_or            TEXT NOT NULL,
      glossary_terms_json TEXT NOT NULL DEFAULT '[]',
      source_ref         TEXT NOT NULL,
      media_refs_json    TEXT NOT NULL DEFAULT '[]',
      token_count        INTEGER NOT NULL DEFAULT 0
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS questions (
      question_id        TEXT PRIMARY KEY,
      concept_id         TEXT NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
      chapter_id         TEXT NOT NULL,
      text_or            TEXT NOT NULL,
      options_json       TEXT NOT NULL,
      correct_answer     TEXT NOT NULL,
      explanation_or     TEXT NOT NULL DEFAULT '',
      difficulty         TEXT NOT NULL DEFAULT 'medium',
      bloom_level        TEXT NOT NULL DEFAULT 'remember',
      misconception_tag  TEXT,
      status             TEXT NOT NULL DEFAULT 'active',
      revision           INTEGER NOT NULL DEFAULT 1,
      answer_key_hash    TEXT NOT NULL DEFAULT '',
      source_ref         TEXT NOT NULL DEFAULT ''
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS pack_manifests (
      pack_id            TEXT NOT NULL,
      version            TEXT NOT NULL,
      title_or           TEXT NOT NULL,
      language           TEXT NOT NULL DEFAULT 'or',
      byte_size          INTEGER NOT NULL,
      checksum_sha256    TEXT NOT NULL,
      min_app_version    TEXT NOT NULL,
      licence            TEXT NOT NULL,
      source_refs_json   TEXT NOT NULL DEFAULT '[]',
      created_at         INTEGER NOT NULL,
      chapters_json      TEXT NOT NULL DEFAULT '[]',
      PRIMARY KEY (pack_id, version)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS installed_packs (
      device_id          TEXT NOT NULL,
      pack_id            TEXT NOT NULL,
      version            TEXT NOT NULL,
      installed_at       INTEGER NOT NULL,
      byte_size          INTEGER NOT NULL,
      checksum_sha256    TEXT NOT NULL,
      PRIMARY KEY (device_id, pack_id)
    );
    """)

    # 3. Events & Mastery
    op.execute("""
    CREATE TABLE IF NOT EXISTS learner_events (
      device_id           TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
      learner_id          TEXT NOT NULL REFERENCES learner_profiles(learner_id) ON DELETE CASCADE,
      seq                 INTEGER NOT NULL,
      event_id            TEXT NOT NULL,
      client_ts           BIGINT NOT NULL,
      event_type          TEXT NOT NULL,
      concept_id          TEXT,
      chapter_id          TEXT,
      question_id         TEXT,
      payload_json        TEXT NOT NULL DEFAULT '{}',
      status              TEXT NOT NULL DEFAULT 'accepted',
      effect              TEXT,
      reason              TEXT,
      received_at         BIGINT NOT NULL,
      server_seq          INTEGER,
      PRIMARY KEY (device_id, seq),
      UNIQUE (event_id)
    );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_events_learner_seq ON learner_events (learner_id, server_seq);")

    op.execute("""
    CREATE TABLE IF NOT EXISTS sync_cursors (
      device_id           TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
      learner_id          TEXT NOT NULL REFERENCES learner_profiles(learner_id) ON DELETE CASCADE,
      last_acked_seq      INTEGER NOT NULL DEFAULT 0,
      last_server_seq     INTEGER NOT NULL DEFAULT 0,
      last_acked_at       BIGINT NOT NULL DEFAULT 0,
      PRIMARY KEY (device_id, learner_id)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS dead_letter_events (
      event_id            TEXT PRIMARY KEY,
      device_id           TEXT NOT NULL,
      learner_id          TEXT NOT NULL,
      seq                 INTEGER NOT NULL,
      reason              TEXT NOT NULL,
      last_error_code     TEXT NOT NULL,
      received_at         BIGINT NOT NULL,
      dead_at             BIGINT NOT NULL
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS learner_progress (
      learner_id         TEXT NOT NULL,
      concept_id         TEXT NOT NULL,
      p_bp               INTEGER NOT NULL DEFAULT 2000,
      attempts           INTEGER NOT NULL DEFAULT 0,
      correct            INTEGER NOT NULL DEFAULT 0,
      last_seen_at       BIGINT,
      last_event_seq     INTEGER,
      bkt_version        TEXT NOT NULL DEFAULT '1',
      PRIMARY KEY (learner_id, concept_id)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS decisions (
      decision_id        TEXT PRIMARY KEY,
      learner_id         TEXT NOT NULL,
      ruleset_version    TEXT NOT NULL,
      target_concept_id  TEXT NOT NULL,
      action             TEXT NOT NULL,
      delivery_mode      TEXT NOT NULL,
      background_actions_json TEXT NOT NULL DEFAULT '[]',
      reason_code        TEXT NOT NULL,
      reason_or          TEXT NOT NULL,
      needs_help         INTEGER NOT NULL DEFAULT 0,
      chapter_id         TEXT,
      suggested_question_id TEXT,
      suggested_chunk_id TEXT,
      network            TEXT NOT NULL DEFAULT 'offline',
      source             TEXT NOT NULL DEFAULT 'server',
      produced_by        TEXT NOT NULL DEFAULT 'rule_engine',
      created_at         BIGINT NOT NULL,
      target_bloom_level TEXT,
      trigger_event_id   TEXT
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS generation_records (
      record_id          TEXT PRIMARY KEY,
      decision_id        TEXT NOT NULL REFERENCES decisions(decision_id) ON DELETE CASCADE,
      provider           TEXT NOT NULL,
      model_id           TEXT,
      prompt_version     TEXT NOT NULL,
      prompt_hash        TEXT NOT NULL,
      params_json        TEXT NOT NULL DEFAULT '{}',
      chunk_ids_json     TEXT NOT NULL DEFAULT '[]',
      output_or          TEXT NOT NULL DEFAULT '',
      validation_results_json TEXT NOT NULL DEFAULT '{}',
      fallback_used      INTEGER NOT NULL DEFAULT 0,
      created_at         BIGINT NOT NULL
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS langgraph_checkpoints (
      thread_id          TEXT NOT NULL,
      checkpoint_ns      TEXT NOT NULL DEFAULT '',
      checkpoint_id      TEXT NOT NULL,
      parent_checkpoint_id TEXT,
      type               TEXT NOT NULL DEFAULT 'dict',
      config_json        TEXT NOT NULL,
      metadata_json      TEXT NOT NULL DEFAULT '{}',
      blob               BYTEA,
      created_at         BIGINT NOT NULL,
      PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
    );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS langgraph_checkpoints CASCADE;")
    op.execute("DROP TABLE IF EXISTS generation_records CASCADE;")
    op.execute("DROP TABLE IF EXISTS decisions CASCADE;")
    op.execute("DROP TABLE IF EXISTS learner_progress CASCADE;")
    op.execute("DROP TABLE IF EXISTS dead_letter_events CASCADE;")
    op.execute("DROP TABLE IF EXISTS sync_cursors CASCADE;")
    op.execute("DROP TABLE IF EXISTS learner_events CASCADE;")
    op.execute("DROP TABLE IF EXISTS installed_packs CASCADE;")
    op.execute("DROP TABLE IF EXISTS pack_manifests CASCADE;")
    op.execute("DROP TABLE IF EXISTS questions CASCADE;")
    op.execute("DROP TABLE IF EXISTS chunks CASCADE;")
    op.execute("DROP TABLE IF EXISTS concepts CASCADE;")
    op.execute("DROP TABLE IF EXISTS chapters CASCADE;")
    op.execute("DROP TABLE IF EXISTS auth_challenges CASCADE;")
    op.execute("DROP TABLE IF EXISTS refresh_tokens CASCADE;")
    op.execute("DROP TABLE IF EXISTS device_tokens CASCADE;")
    op.execute("DROP TABLE IF EXISTS learner_devices CASCADE;")
    op.execute("DROP TABLE IF EXISTS learner_profiles CASCADE;")
    op.execute("DROP TABLE IF EXISTS devices CASCADE;")
