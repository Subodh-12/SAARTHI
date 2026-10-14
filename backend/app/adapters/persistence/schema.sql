-- SAARTHI schema v2 — works on SQLite (default MVP) and PostgreSQL.
-- Aligned with Design Document v2 Section 7 (devices/learner profiles,
-- integer basis-point mastery, event status/effect/reason, generation
-- records, refresh tokens and auth challenges).
-- Idempotent: each CREATE uses IF NOT EXISTS. Column additions for prior
-- schemas are handled by the guarded migrations in migrations.sql /
-- persistence._migrate_prior_schema().

-- ---------------------------------------------------------------- --
-- Devices & learners
-- ---------------------------------------------------------------- --
CREATE TABLE IF NOT EXISTS devices (
  device_id          TEXT PRIMARY KEY,
  hardware_label      TEXT NOT NULL DEFAULT 'shared-android-low-end',
  public_key_spki    TEXT,
  created_at          INTEGER NOT NULL,
  last_seen_at        INTEGER,
  revoked_at          INTEGER
);

CREATE TABLE IF NOT EXISTS learner_profiles (
  learner_id          TEXT PRIMARY KEY,
  display_label       TEXT NOT NULL DEFAULT '',
  locale              TEXT NOT NULL DEFAULT 'or',
  grade               TEXT NOT NULL DEFAULT 'class9',
  subject             TEXT NOT NULL DEFAULT 'science',
  pin_hash            TEXT,
  created_at          INTEGER NOT NULL,
  -- Soft column for the currently active profile on a given device.
  active_device_id    TEXT REFERENCES devices(device_id) ON DELETE SET NULL,
  UNIQUE (active_device_id)  -- v2: one ACTIVE device per learner (MVP)
);

CREATE TABLE IF NOT EXISTS learner_devices (
  learner_id          TEXT NOT NULL REFERENCES learner_profiles(learner_id) ON DELETE CASCADE,
  device_id           TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
  status              TEXT NOT NULL DEFAULT 'active',
  first_seen_at       INTEGER NOT NULL,
  last_active_at      INTEGER NOT NULL,
  PRIMARY KEY (learner_id, device_id)
);

CREATE TABLE IF NOT EXISTS device_tokens (
  -- Short-lived ACCESS tokens (24h). token_hash = SHA-256 of the token.
  device_id           TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
  token_hash          TEXT NOT NULL,
  issued_at           INTEGER NOT NULL,
  expires_at          INTEGER NOT NULL,
  revoked             INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_device_tokens_hash
  ON device_tokens (token_hash, revoked, expires_at);

CREATE TABLE IF NOT EXISTS refresh_tokens (
  -- Rotating REFRESH tokens (30 days); single use — presented refresh
  -- tokens are marked used and a new one is issued on success.
  id                  TEXT PRIMARY KEY,
  device_id           TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
  token_hash          TEXT NOT NULL,
  issued_at           INTEGER NOT NULL,
  expires_at          INTEGER NOT NULL,
  used_at             INTEGER,
  revoked             INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_hash
  ON refresh_tokens (token_hash, revoked, expires_at);

CREATE TABLE IF NOT EXISTS auth_challenges (
  -- Signed-nonce challenge for renewal after prolonged offline periods.
  nonce               TEXT PRIMARY KEY,
  device_id           TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
  created_at          INTEGER NOT NULL,
  expires_at          INTEGER NOT NULL,
  used_at             INTEGER
);

-- ---------------------------------------------------------------- --
-- Curriculum / content metadata (server-side pack manifests)
-- ---------------------------------------------------------------- --
CREATE TABLE IF NOT EXISTS chapters (
  chapter_id          TEXT PRIMARY KEY,
  subject             TEXT NOT NULL,
  grade               TEXT NOT NULL,
  title_or            TEXT NOT NULL,
  title_en            TEXT NOT NULL,
  summary_or          TEXT NOT NULL DEFAULT '',
  source_refs_json    TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS concepts (
  concept_id          TEXT PRIMARY KEY,
  chapter_id          TEXT NOT NULL REFERENCES chapters(chapter_id) ON DELETE CASCADE,
  title_or            TEXT NOT NULL,
  title_en            TEXT NOT NULL,
  summary_or          TEXT NOT NULL DEFAULT '',
  prerequisites_json  TEXT NOT NULL DEFAULT '[]',
  source_refs_json    TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS chunks (
  chunk_id            TEXT PRIMARY KEY,
  concept_id          TEXT NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
  chapter_id          TEXT NOT NULL REFERENCES chapters(chapter_id) ON DELETE CASCADE,
  ordinal             INTEGER NOT NULL,
  text_or              TEXT NOT NULL,
  source_ref          TEXT NOT NULL,
  glossary_refs_json  TEXT NOT NULL DEFAULT '[]',
  UNIQUE (concept_id, ordinal)
);

CREATE TABLE IF NOT EXISTS questions (
  question_id         TEXT PRIMARY KEY,
  concept_id          TEXT NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
  chapter_id          TEXT NOT NULL REFERENCES chapters(chapter_id) ON DELETE CASCADE,
  qtype               TEXT NOT NULL,
  prompt_or           TEXT NOT NULL,
  options_json        TEXT NOT NULL DEFAULT '[]',
  correct_option      INTEGER,
  rubric_or           TEXT,
  expected_concepts_json TEXT NOT NULL DEFAULT '[]',
  explanation_or      TEXT NOT NULL,
  difficulty          TEXT NOT NULL,
  misconception_tag   TEXT,
  source_ref          TEXT NOT NULL,
  revision            INTEGER NOT NULL DEFAULT 1,
  answer_key_hash     TEXT NOT NULL DEFAULT '',
  status              TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS glossary (
  glossary_id         INTEGER PRIMARY KEY AUTOINCREMENT,
  term_or             TEXT NOT NULL,
  term_en             TEXT NOT NULL,
  definition_or       TEXT NOT NULL,
  definition_en       TEXT NOT NULL,
  UNIQUE (term_or, term_en)
);

-- ---------------------------------------------------------------- --
-- Pack metadata
-- ---------------------------------------------------------------- --
CREATE TABLE IF NOT EXISTS packs (
  pack_id             TEXT NOT NULL,
  version             TEXT NOT NULL,
  content_version     TEXT NOT NULL,
  language            TEXT NOT NULL DEFAULT 'or',
  byte_size           INTEGER NOT NULL,
  checksum_sha256     TEXT NOT NULL,
  min_app_version     TEXT NOT NULL,
  licence             TEXT NOT NULL,
  source_refs_json    TEXT NOT NULL DEFAULT '[]',
  created_at          INTEGER NOT NULL,
  published           INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (pack_id, version)
);

CREATE TABLE IF NOT EXISTS pack_chapters (
  pack_id             TEXT NOT NULL,
  version             TEXT NOT NULL,
  chapter_id          TEXT NOT NULL REFERENCES chapters(chapter_id) ON DELETE CASCADE,
  PRIMARY KEY (pack_id, version, chapter_id)
);

CREATE TABLE IF NOT EXISTS installed_packs (
  -- Per-device installed pack version; learners may share a pack on a device.
  device_id           TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
  pack_id             TEXT NOT NULL,
  version             TEXT NOT NULL,
  installed_at        INTEGER NOT NULL,
  byte_size           INTEGER NOT NULL,
  checksum_sha256     TEXT NOT NULL,
  PRIMARY KEY (device_id, pack_id)
);

-- ---------------------------------------------------------------- --
-- Learner state (mastery projection — rebuilt by replay, never a
-- source of truth. p_bp is the integer basis-point mastery.)
-- ---------------------------------------------------------------- --
CREATE TABLE IF NOT EXISTS learner_progress (
  learner_id          TEXT NOT NULL REFERENCES learner_profiles(learner_id) ON DELETE CASCADE,
  concept_id          TEXT NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
  p_bp                INTEGER NOT NULL DEFAULT 2000,
  bkt_version         TEXT NOT NULL DEFAULT '1',
  band                TEXT NOT NULL DEFAULT 'weak',
  attempts            INTEGER NOT NULL DEFAULT 0,
  correct             INTEGER NOT NULL DEFAULT 0,
  last_event_seq      INTEGER,
  PRIMARY KEY (learner_id, concept_id)
);

CREATE TABLE IF NOT EXISTS learning_sessions (
  session_id          TEXT PRIMARY KEY,
  learner_id          TEXT NOT NULL REFERENCES learner_profiles(learner_id) ON DELETE CASCADE,
  device_id           TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
  started_at          INTEGER NOT NULL,
  ended_at            INTEGER,
  last_decision_id    TEXT
);

-- ---------------------------------------------------------------- --
-- Events / sync (append-only; unique on (device_id, seq))
-- ---------------------------------------------------------------- --
CREATE TABLE IF NOT EXISTS learner_events (
  device_id           TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
  learner_id          TEXT NOT NULL REFERENCES learner_profiles(learner_id) ON DELETE CASCADE,
  seq                 INTEGER NOT NULL,
  event_id            TEXT NOT NULL,
  client_ts           INTEGER NOT NULL,
  event_type          TEXT NOT NULL,
  concept_id          TEXT,
  chapter_id          TEXT,
  question_id         TEXT,
  payload_json        TEXT NOT NULL DEFAULT '{}',
  status              TEXT NOT NULL DEFAULT 'accepted',
  effect              TEXT,
  reason              TEXT,
  received_at         INTEGER NOT NULL,
  server_seq          INTEGER,
  PRIMARY KEY (device_id, seq),
  UNIQUE (event_id)
);

CREATE INDEX IF NOT EXISTS idx_events_learner_seq
  ON learner_events (learner_id, server_seq);

CREATE TABLE IF NOT EXISTS sync_cursors (
  -- Per (device, learner): highest seq the server has acked.
  device_id           TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
  learner_id          TEXT NOT NULL REFERENCES learner_profiles(learner_id) ON DELETE CASCADE,
  last_acked_seq      INTEGER NOT NULL DEFAULT 0,
  last_server_seq     INTEGER NOT NULL DEFAULT 0,
  last_acked_at       INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (device_id, learner_id)
);

CREATE TABLE IF NOT EXISTS dead_letter_events (
  event_id            TEXT PRIMARY KEY,
  device_id           TEXT NOT NULL,
  learner_id          TEXT NOT NULL,
  seq                 INTEGER NOT NULL,
  reason              TEXT NOT NULL,
  last_error_code     TEXT NOT NULL,
  received_at         INTEGER NOT NULL,
  dead_at             INTEGER NOT NULL
);

-- ---------------------------------------------------------------- --
-- Decisions, traces, generation records
-- ---------------------------------------------------------------- --
CREATE TABLE IF NOT EXISTS decisions (
  decision_id         TEXT PRIMARY KEY,
  learner_id          TEXT NOT NULL REFERENCES learner_profiles(learner_id) ON DELETE CASCADE,
  trigger_event_id    TEXT,
  ruleset_version     TEXT NOT NULL,
  target_concept_id   TEXT NOT NULL,
  action              TEXT NOT NULL,
  delivery_mode       TEXT NOT NULL,
  background_actions_json TEXT NOT NULL DEFAULT '[]',
  reason_code         TEXT NOT NULL,
  reason_or           TEXT NOT NULL,
  needs_help          INTEGER NOT NULL DEFAULT 0,
  chapter_id          TEXT NOT NULL DEFAULT '',
  suggested_question_id TEXT,
  suggested_chunk_id  TEXT,
  network             TEXT NOT NULL,
  source              TEXT NOT NULL DEFAULT 'server',
  produced_by         TEXT NOT NULL DEFAULT 'server_engine',
  inputs_json         TEXT NOT NULL DEFAULT '{}',
  trace_json          TEXT,
  created_at          INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS decision_traces (
  decision_id         TEXT NOT NULL REFERENCES decisions(decision_id) ON DELETE CASCADE,
  step_ordinal        INTEGER NOT NULL,
  step_id             TEXT NOT NULL,
  node                TEXT NOT NULL,
  tool                TEXT,
  provider            TEXT,
  ruleset_version     TEXT,
  model_id            TEXT,
  status              TEXT NOT NULL,
  error_code          TEXT,
  duration_ms        INTEGER NOT NULL,
  retry               INTEGER,
  fallback            TEXT,
  input_summary_json  TEXT NOT NULL DEFAULT '{}',
  output_summary_json TEXT NOT NULL DEFAULT '{}',
  redacted            INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (decision_id, step_ordinal)
);

CREATE TABLE IF NOT EXISTS generation_records (
  record_id           TEXT PRIMARY KEY,
  decision_id         TEXT NOT NULL REFERENCES decisions(decision_id) ON DELETE CASCADE,
  provider            TEXT NOT NULL,
  model_id            TEXT,
  prompt_version      TEXT NOT NULL,
  prompt_hash         TEXT NOT NULL,
  params_json         TEXT NOT NULL DEFAULT '{}',
  chunk_ids_json      TEXT NOT NULL DEFAULT '[]',
  output_or           TEXT NOT NULL DEFAULT '',
  validation_results_json TEXT NOT NULL DEFAULT '{}',
  fallback_used       INTEGER NOT NULL DEFAULT 0,
  created_at          INTEGER NOT NULL
);

-- ---------------------------------------------------------------- --
-- LangGraph checkpoints (server-side durable state for interrupted
-- server workflows). The local offline decision engine never depends
-- on these.
-- ---------------------------------------------------------------- --
CREATE TABLE IF NOT EXISTS langgraph_checkpoints (
  thread_id           TEXT NOT NULL,
  checkpoint_ns       TEXT NOT NULL DEFAULT '',
  checkpoint_id       TEXT NOT NULL,
  parent_checkpoint_id TEXT,
  type                 TEXT NOT NULL DEFAULT 'dict',
  config_json          TEXT NOT NULL,
  metadata_json        TEXT NOT NULL DEFAULT '{}',
  blob                 BLOB,
  created_at           INTEGER NOT NULL,
  PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

CREATE INDEX IF NOT EXISTS idx_checkpoints_thread
  ON langgraph_checkpoints (thread_id, checkpoint_ns, created_at);

CREATE TABLE IF NOT EXISTS langgraph_writes (
  thread_id           TEXT NOT NULL,
  checkpoint_ns       TEXT NOT NULL DEFAULT '',
  checkpoint_id       TEXT NOT NULL,
  task_id             INTEGER NOT NULL,
  channel             TEXT NOT NULL,
  type                TEXT NOT NULL,
  blob                 BLOB,
  created_at           INTEGER NOT NULL,
  PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, channel)
);
