PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO "alembic_version" VALUES('002_add_jobs_and_misconceptions');
CREATE TABLE auth_challenges (
  -- Signed-nonce challenge for renewal after prolonged offline periods.
  nonce               TEXT PRIMARY KEY,
  device_id           TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
  created_at          INTEGER NOT NULL,
  expires_at          INTEGER NOT NULL,
  used_at             INTEGER
);
CREATE TABLE chapters (
  chapter_id          TEXT PRIMARY KEY,
  subject             TEXT NOT NULL,
  grade               TEXT NOT NULL,
  title_or            TEXT NOT NULL,
  title_en            TEXT NOT NULL,
  summary_or          TEXT NOT NULL DEFAULT '',
  source_refs_json    TEXT NOT NULL DEFAULT '[]'
);
CREATE TABLE chunks (
  chunk_id            TEXT PRIMARY KEY,
  concept_id          TEXT NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
  chapter_id          TEXT NOT NULL REFERENCES chapters(chapter_id) ON DELETE CASCADE,
  ordinal             INTEGER NOT NULL,
  text_or              TEXT NOT NULL,
  source_ref          TEXT NOT NULL,
  glossary_refs_json  TEXT NOT NULL DEFAULT '[]',
  UNIQUE (concept_id, ordinal)
);
CREATE TABLE concepts (
  concept_id          TEXT PRIMARY KEY,
  chapter_id          TEXT NOT NULL REFERENCES chapters(chapter_id) ON DELETE CASCADE,
  title_or            TEXT NOT NULL,
  title_en            TEXT NOT NULL,
  summary_or          TEXT NOT NULL DEFAULT '',
  prerequisites_json  TEXT NOT NULL DEFAULT '[]',
  source_refs_json    TEXT NOT NULL DEFAULT '[]'
);
CREATE TABLE dead_letter_events (
  event_id            TEXT PRIMARY KEY,
  device_id           TEXT NOT NULL,
  learner_id          TEXT NOT NULL,
  seq                 INTEGER NOT NULL,
  reason              TEXT NOT NULL,
  last_error_code     TEXT NOT NULL,
  received_at         INTEGER NOT NULL,
  dead_at             INTEGER NOT NULL
);
CREATE TABLE decision_traces (
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
CREATE TABLE decisions (
  decision_id         TEXT PRIMARY KEY,
  learner_id          TEXT NOT NULL REFERENCES learner_profiles(learner_id) ON DELETE CASCADE,
  trigger_event_id    TEXT,
  ruleset_version     TEXT NOT NULL,
  target_concept_id   TEXT NOT NULL,
  target_bloom_level  TEXT,
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
CREATE TABLE device_tokens (
  -- Short-lived ACCESS tokens (24h). token_hash = SHA-256 of the token.
  device_id           TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
  token_hash          TEXT NOT NULL,
  issued_at           INTEGER NOT NULL,
  expires_at          INTEGER NOT NULL,
  revoked             INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE devices (
  device_id          TEXT PRIMARY KEY,
  hardware_label      TEXT NOT NULL DEFAULT 'shared-android-low-end',
  public_key_spki    TEXT,
  created_at          INTEGER NOT NULL,
  last_seen_at        INTEGER,
  revoked_at          INTEGER
);
INSERT INTO "devices" VALUES('dev_0123456789abcdef','shared-android-low-end',NULL,1000,NULL,NULL);
CREATE TABLE generation_records (
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
CREATE TABLE glossary (
  glossary_id         INTEGER PRIMARY KEY AUTOINCREMENT,
  term_or             TEXT NOT NULL,
  term_en             TEXT NOT NULL,
  definition_or       TEXT NOT NULL,
  definition_en       TEXT NOT NULL,
  UNIQUE (term_or, term_en)
);
CREATE TABLE installed_packs (
  -- Per-device installed pack version; learners may share a pack on a device.
  device_id           TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
  pack_id             TEXT NOT NULL,
  version             TEXT NOT NULL,
  installed_at        INTEGER NOT NULL,
  byte_size           INTEGER NOT NULL,
  checksum_sha256     TEXT NOT NULL,
  PRIMARY KEY (device_id, pack_id)
);
CREATE TABLE jobs (
  job_id              TEXT PRIMARY KEY,
  type                TEXT NOT NULL,
  payload_json        TEXT NOT NULL DEFAULT '{}',
  dedupe_key          TEXT UNIQUE,
  status              TEXT NOT NULL DEFAULT 'queued',
  attempts            INTEGER NOT NULL DEFAULT 0,
  max_attempts        INTEGER NOT NULL DEFAULT 6,
  next_run_at         INTEGER NOT NULL,
  lease_expires_at    INTEGER,
  last_error          TEXT,
  created_at          INTEGER NOT NULL,
  updated_at          INTEGER NOT NULL
);
CREATE TABLE langgraph_checkpoints (
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
CREATE TABLE langgraph_writes (
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
CREATE TABLE learner_bloom_progress (
  learner_id          TEXT NOT NULL REFERENCES learner_profiles(learner_id) ON DELETE CASCADE,
  concept_id          TEXT NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
  bloom_level         TEXT NOT NULL,
  p_bp                INTEGER NOT NULL DEFAULT 2000,
  bkt_version         TEXT NOT NULL DEFAULT '1',
  band                TEXT NOT NULL DEFAULT 'weak',
  attempts            INTEGER NOT NULL DEFAULT 0,
  correct             INTEGER NOT NULL DEFAULT 0,
  last_event_seq      INTEGER,
  PRIMARY KEY (learner_id, concept_id, bloom_level)
);
CREATE TABLE learner_devices (
  learner_id          TEXT NOT NULL REFERENCES learner_profiles(learner_id) ON DELETE CASCADE,
  device_id           TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
  status              TEXT NOT NULL DEFAULT 'active',
  first_seen_at       INTEGER NOT NULL,
  last_active_at      INTEGER NOT NULL,
  PRIMARY KEY (learner_id, device_id)
);
CREATE TABLE learner_events (
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
INSERT INTO "learner_events" VALUES('dev_0123456789abcdef','lrn_0123456789abcdef',1,'evt_1',1000,'ANSWER_SUBMITTED','c0001',NULL,NULL,'{"attempt_id":"att_1", "question_id":"sci9.ch1.c01.q01", "concept_id":"c0001", "response":"A"}','accepted',NULL,NULL,1000,NULL);
CREATE TABLE learner_profiles (
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
INSERT INTO "learner_profiles" VALUES('lrn_0123456789abcdef','','or','class9','science',NULL,1000,NULL);
CREATE TABLE learner_progress (
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
INSERT INTO "learner_progress" VALUES('lrn_0123456789abcdef','c0001',6000,'1','weak',1,1,NULL);
CREATE TABLE learning_sessions (
  session_id          TEXT PRIMARY KEY,
  learner_id          TEXT NOT NULL REFERENCES learner_profiles(learner_id) ON DELETE CASCADE,
  device_id           TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
  started_at          INTEGER NOT NULL,
  ended_at            INTEGER,
  last_decision_id    TEXT
);
CREATE TABLE pack_chapters (
  pack_id             TEXT NOT NULL,
  version             TEXT NOT NULL,
  chapter_id          TEXT NOT NULL REFERENCES chapters(chapter_id) ON DELETE CASCADE,
  PRIMARY KEY (pack_id, version, chapter_id)
);
INSERT INTO "pack_chapters" VALUES('pack_class9_science_or_v1','1.0.0','ch001');
INSERT INTO "pack_chapters" VALUES('pack_class9_science_or_v1','1.0.0','ch002');
INSERT INTO "pack_chapters" VALUES('pack_class9_science_or_v1','1.0.0','ch003');
CREATE TABLE pack_manifests (
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
CREATE TABLE packs (
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
INSERT INTO "packs" VALUES('pack_class9_science_or_v1','1.0.0','2026.10.001','or',252242,'b6ad5ce6328a4451a58481e85e81c1eff4b206ceb42e4c645bba396f2e2c5c2b','0.1.0','CC-BY 4.0 (original Odia notes aligned to NCERT Class 9 Science syllabus)','["NCERT Class 9 Science syllabus (chapters 1, 8, 6)", "Original Odia notes authored for SAARTHI MVP"]',1792010877977,1);
CREATE TABLE questions (
  question_id         TEXT PRIMARY KEY,
  concept_id          TEXT NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
  chapter_id          TEXT NOT NULL REFERENCES chapters(chapter_id) ON DELETE CASCADE,
  bloom_level         TEXT NOT NULL DEFAULT 'remember',
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
CREATE TABLE refresh_tokens (
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
CREATE TABLE sync_cursors (
  -- Per (device, learner): highest seq the server has acked.
  device_id           TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
  learner_id          TEXT NOT NULL REFERENCES learner_profiles(learner_id) ON DELETE CASCADE,
  last_acked_seq      INTEGER NOT NULL DEFAULT 0,
  last_server_seq     INTEGER NOT NULL DEFAULT 0,
  last_acked_at       INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (device_id, learner_id)
);
CREATE INDEX idx_device_tokens_hash
  ON device_tokens (token_hash, revoked, expires_at);
CREATE INDEX idx_refresh_tokens_hash
  ON refresh_tokens (token_hash, revoked, expires_at);
CREATE INDEX idx_events_learner_seq
  ON learner_events (learner_id, server_seq);
CREATE INDEX idx_checkpoints_thread
  ON langgraph_checkpoints (thread_id, checkpoint_ns, created_at);
CREATE INDEX idx_jobs_status_next_run
  ON jobs (status, next_run_at);
CREATE INDEX idx_jobs_lease_expires
  ON jobs (status, lease_expires_at);
DELETE FROM "sqlite_sequence";
COMMIT;
