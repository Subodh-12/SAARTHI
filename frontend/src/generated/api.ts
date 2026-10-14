// Auto-generated from backend Pydantic schemas + ruleset (kept in sync by
// `scripts/dev.py check`; do NOT hand-edit divergently — see Design v2
// Section 14 "Contract change process").

export enum NetworkState {
  ONLINE = "online",
  WEAK = "weak",
  OFFLINE = "offline",
  RECONNECTED = "reconnected",
}

export enum Action {
  REMEDIATE = "REMEDIATE",
  RETRY = "RETRY",
  REVISE = "REVISE",
  ADVANCE = "ADVANCE",
}

export enum DeliveryMode {
  RICH = "rich",
  CACHED = "cached",
  PREFETCH_THEN_OFFLINE = "prefetch_then_offline",
}

export enum BackgroundAction {
  SYNC = "SYNC",
  PREFETCH = "PREFETCH",
}

// v2 event types (frozen — Design v2 Section 8)
export enum EventType {
  SESSION_STARTED = "SESSION_STARTED",
  SESSION_ENDED = "SESSION_ENDED",
  CONTENT_VIEWED = "CONTENT_VIEWED",
  ANSWER_SUBMITTED = "ANSWER_SUBMITTED",
  QUESTION_ABANDONED = "QUESTION_ABANDONED",
  DOUBT_ASKED = "DOUBT_ASKED",
  DOUBT_ANSWERED = "DOUBT_ANSWERED",
  PACK_INSTALLED = "PACK_INSTALLED",
  DECISION_MADE_LOCAL = "DECISION_MADE_LOCAL",
  NETWORK_STATE_CHANGED = "NETWORK_STATE_CHANGED",
}

export enum EvidenceType {
  CORRECT = "correct",
  INCORRECT = "incorrect",
  PARTIAL = "partial",
  NONE = "none",
}

export enum BloomLevel {
  REMEMBER = "remember",
  UNDERSTAND = "understand",
  APPLY = "apply",
  ANALYZE = "analyze",
  EVALUATE = "evaluate",
  CREATE = "create",
}

// v2 per-event sync outcomes (frozen)
export enum Outcome {
  ACCEPTED = "ACCEPTED",
  DUPLICATE = "DUPLICATE",
  RETRYABLE = "RETRYABLE",
  REJECTED = "REJECTED",
}

export enum SyncEffect {
  MASTERY_UPDATED = "mastery_updated",
  NONE = "none",
}

export enum SyncReason {
  REPEAT_SUBMISSION = "REPEAT_SUBMISSION",
  LEGACY_QUESTION = "LEGACY_QUESTION",
  INVALID_PAYLOAD = "INVALID_PAYLOAD",
  UNKNOWN_EVENT_TYPE = "UNKNOWN_EVENT_TYPE",
  LEARNER_NOT_LINKED = "LEARNER_NOT_LINKED",
  DEVICE_REVOKED = "DEVICE_REVOKED",
  PAYLOAD_CONFLICT = "PAYLOAD_CONFLICT",
  SERVER_BUSY = "SERVER_BUSY",
  DB_TIMEOUT = "DB_TIMEOUT",
}

export interface Problem {
  type: string;
  title: string;
  status: number;
  detail: string;
  error_code: string;
  request_id: string;
  decision_id?: string | null;
  instance?: string | null;
}

export interface LearnerProfileCreate {
  display_label?: string;
  locale?: "or" | "en";
  grade?: "class9";
  subject?: "science";
  pin_verifier?: string | null;
}

export interface LearnerProfile extends LearnerProfileCreate {
  learner_id: string;
  created_at: number;
}

export interface DeviceRegistration {
  public_key_spki_b64: string;
  hardware_label?: string;
}

export interface DeviceTokenResponse {
  device_id: string;
  access_token: string;
  access_expires_at: number;
  refresh_token: string;
  refresh_expires_at: number;
  token_type: "Bearer";
}

export interface AuthChallenge {
  nonce: string;
  expires_at: number;
}

export interface AuthChallengeRequest {
  device_id: string;
}

export interface AuthRenewRequest {
  device_id: string;
  nonce: string;
  signature_b64: string;
}

export interface RefreshRequest {
  device_id: string;
  refresh_token: string;
}

export interface AuthResponse {
  learner_id?: string | null;
  device_id: string;
  device_token: string;
  token_expires_at: number;
  refresh_token?: string | null;
  refresh_expires_at?: number | null;
}

export interface GlossaryEntry {
  term_or: string;
  term_en: string;
  definition_or: string;
  definition_en: string;
}

export interface Concept {
  concept_id: string;
  title_or: string;
  title_en: string;
  chapter_id: string;
  prerequisites: string[];
  summary_or: string;
  source_refs: string[];
}

export interface Chunk {
  chunk_id: string;
  concept_id: string;
  chapter_id: string;
  ordinal: number;
  text_or: string;
  source_ref: string;
  glossary_refs: string[];
}

export interface Question {
  question_id: string;
  concept_id: string;
  chapter_id: string;
  bloom_level?: BloomLevel;
  qtype: "mcq" | "short_answer";
  prompt_or: string;
  options: string[];
  correct_option?: number | null;
  rubric_or?: string | null;
  expected_concepts: string[];
  explanation_or: string;
  difficulty: "easy" | "medium" | "hard";
  misconception_tag?: string | null;
  source_ref: string;
  revision: number;
  answer_key_hash: string;
  status: "active" | "legacy";
}

export interface Chapter {
  chapter_id: string;
  subject?: "science";
  grade?: "class9";
  title_or: string;
  title_en: string;
  summary_or?: string;
  source_refs?: string[];
}

export interface EnvironmentSnapshot {
  network: NetworkState;
  measured_rtt_ms?: number | null;
  measured_downlink_kbps?: number | null;
  battery_saver: boolean;
  free_storage_mb?: number | null;
  installed_pack_versions: Record<string, number>;
  ruleset_version: string;
}

// v2: mastery is an INTEGER in basis points (0..10000).
export interface MasteryRecord {
  concept_id: string;
  p_bp: number;
  band: "weak" | "partial" | "mastered";
  attempts: number;
  correct: number;
  last_event_seq: number;
}

export interface BloomMasteryRecord {
  concept_id: string;
  bloom_level: BloomLevel;
  p_bp: number;
  band: "weak" | "partial" | "mastered";
  attempts: number;
  correct: number;
  last_event_seq: number;
}

export interface LearnerEvent {
  event_id: string;
  device_id: string;
  learner_id: string;
  seq: number;
  type: EventType;
  client_ts: number;
  payload: Record<string, any>;
  concept_id?: string | null;
  chapter_id?: string | null;
  question_id?: string | null;
}

export interface PerEventResult {
  event_id: string;
  seq: number;
  outcome: Outcome;
  effect?: SyncEffect | null;
  reason?: SyncReason | null;
  detail: string;
}

export interface SyncRequest {
  device_id: string;
  learner_id: string;
  from_seq: number;
  events: LearnerEvent[];
}

export interface SyncResponse {
  results: PerEventResult[];
  mastery: MasteryRecord[];
  bloom_mastery?: BloomMasteryRecord[];
  decision?: Decision | null;
  decision_status: "computed" | "deferred";
  server_cursor: number;
  ruleset_version: string;
  // Back-compat mirrors
  accepted: PerEventResult[];
  server_learner_seq: number;
  canonical_mastery: MasteryRecord[];
  canonical_bloom_mastery?: BloomMasteryRecord[];
  next_decision?: Decision | null;
}

export interface AssessmentSubmission {
  question_id: string;
  revision?: number;
  attempt_id?: string | null;
  selected_option?: number | null;
  answer_text?: string | null;
  duration_ms: number;
  submitted_at: number;
  correct_claim?: boolean | null;
  seq?: number;
}

export interface AssessmentResult {
  question_id: string;
  attempt_id?: string | null;
  correct: boolean;
  evidence: EvidenceType;
  explanation_or: string;
  concept_id: string;
  bloom_level?: BloomLevel | null;
  mastery_after: MasteryRecord;
  bloom_mastery_after?: BloomMasteryRecord | null;
  next_decision_id: string;
}

export interface Decision {
  decision_id: string;
  learner_id?: string | null;
  ruleset_version: string;
  target_concept_id: string;
  target_bloom_level?: BloomLevel | null;
  action: Action;
  delivery_mode: DeliveryMode;
  background_actions: BackgroundAction[];
  reason_code: string;
  reason_or: string;
  needs_help: boolean;
  chapter_id: string;
  suggested_question_id?: string | null;
  suggested_chunk_id?: string | null;
  network: NetworkState;
  source: "server" | "local";
  produced_by: "local_engine" | "server_engine";
  created_at: number;
}

export interface TraceStep {
  step_id: string;
  node: string;
  stage?: string | null;
  tool?: string | null;
  provider?: string | null;
  ruleset_version?: string | null;
  model_id?: string | null;
  status: "ok" | "error" | "skipped" | "fallback";
  error_code?: string | null;
  duration_ms: number;
  retry?: number | null;
  fallback?: string | null;
  input_summary: Record<string, any>;
  output_summary: Record<string, any>;
  redacted: boolean;
}

export interface DecisionTrace {
  decision_id: string;
  trace: TraceStep[];
}

export interface DoubtRequest {
  query: string;
  learner_id: string;
  pack_ids: string[];
  concept_hint?: string | null;
}

export interface RetrievedChunk {
  chunk_id: string;
  concept_id: string;
  chapter_id: string;
  text_or: string;
  source_ref: string;
  score: number;
  matched_terms: string[];
}

export interface RetrievedResult {
  chunks: RetrievedChunk[];
  provider: string;
  model_id?: string | null;
  confidence: number;
}

export interface GeneratedAnswer {
  text_or: string;
  citations: string[];
  chapter_refs: string[];
  confidence: number;
  provenance: "extractive" | "llm_grounded" | "basic";
  basic_answer_status?: string | null;
}

export interface GenerationRecord {
  record_id: string;
  decision_id: string;
  provider: string;
  model_id?: string | null;
  prompt_version: string;
  prompt_hash: string;
  params: Record<string, any>;
  chunk_ids: string[];
  output_or: string;
  validation_results: Record<string, any>;
  fallback_used: boolean;
  created_at: number;
}

export interface DoubtResponse {
  answer: GeneratedAnswer;
  retrieved: RetrievedResult;
  decision_id: string;
  translated_query?: string | null;
  used_translation_tool: boolean;
  generation_record?: GenerationRecord | null;
}

export interface PackManifest {
  pack_id: string;
  version: string;
  content_version: string;
  language: "or" | "en";
  byte_size: number;
  checksum_sha256: string;
  archive_sha256: string;
  archive_byte_size: number;
  min_app_version: string;
  chapters: string[];
  licence: string;
  source_refs: string[];
  created_at: number;
}

export interface PackDownloadInfo {
  pack_id: string;
  version: string;
  url: string;
  byte_size: number;
  checksum_sha256: string;
  archive_sha256: string;
  archive_byte_size: number;
}

export interface LearnerState {
  learner_id: string;
  device_id: string;
  mastery: MasteryRecord[];
  bloom_mastery?: BloomMasteryRecord[];
  active_pack_versions: Record<string, number>;
  last_decision_id?: string | null;
  outbox_depth: number;
}

export interface HealthResponse {
  status: string;
  project: string;
  app_version: string;
  env: string;
  persistence: string;
  translation_provider: string;
  llm_provider: string;
  retrieval_provider: string;
  ruleset_version: string;
  bkt_version: string;
  has_hf_token: boolean;
  has_llm_key: boolean;
  request_id: string;
}
