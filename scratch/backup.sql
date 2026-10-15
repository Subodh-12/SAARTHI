--
-- PostgreSQL database dump
--

\restrict 9YtkHPebbrFuRaR6MEatePI5tRtFcnbD55cejMExULc5VGaaFe1cdBhVj1zbVM7

-- Dumped from database version 16.15
-- Dumped by pg_dump version 16.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.sync_cursors DROP CONSTRAINT IF EXISTS sync_cursors_learner_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sync_cursors DROP CONSTRAINT IF EXISTS sync_cursors_device_id_fkey;
ALTER TABLE IF EXISTS ONLY public.refresh_tokens DROP CONSTRAINT IF EXISTS refresh_tokens_device_id_fkey;
ALTER TABLE IF EXISTS ONLY public.questions DROP CONSTRAINT IF EXISTS questions_concept_id_fkey;
ALTER TABLE IF EXISTS ONLY public.learner_profiles DROP CONSTRAINT IF EXISTS learner_profiles_active_device_id_fkey;
ALTER TABLE IF EXISTS ONLY public.learner_events DROP CONSTRAINT IF EXISTS learner_events_learner_id_fkey;
ALTER TABLE IF EXISTS ONLY public.learner_events DROP CONSTRAINT IF EXISTS learner_events_device_id_fkey;
ALTER TABLE IF EXISTS ONLY public.learner_devices DROP CONSTRAINT IF EXISTS learner_devices_learner_id_fkey;
ALTER TABLE IF EXISTS ONLY public.learner_devices DROP CONSTRAINT IF EXISTS learner_devices_device_id_fkey;
ALTER TABLE IF EXISTS ONLY public.generation_records DROP CONSTRAINT IF EXISTS generation_records_decision_id_fkey;
ALTER TABLE IF EXISTS ONLY public.device_tokens DROP CONSTRAINT IF EXISTS device_tokens_device_id_fkey;
ALTER TABLE IF EXISTS ONLY public.concepts DROP CONSTRAINT IF EXISTS concepts_chapter_id_fkey;
ALTER TABLE IF EXISTS ONLY public.chunks DROP CONSTRAINT IF EXISTS chunks_concept_id_fkey;
ALTER TABLE IF EXISTS ONLY public.auth_challenges DROP CONSTRAINT IF EXISTS auth_challenges_device_id_fkey;
DROP INDEX IF EXISTS public.idx_refresh_tokens_hash;
DROP INDEX IF EXISTS public.idx_jobs_status_next_run;
DROP INDEX IF EXISTS public.idx_jobs_lease_expires;
DROP INDEX IF EXISTS public.idx_events_learner_seq;
DROP INDEX IF EXISTS public.idx_device_tokens_hash;
DROP INDEX IF EXISTS public.idx_checkpoints_thread;
ALTER TABLE IF EXISTS ONLY public.sync_cursors DROP CONSTRAINT IF EXISTS sync_cursors_pkey;
ALTER TABLE IF EXISTS ONLY public.refresh_tokens DROP CONSTRAINT IF EXISTS refresh_tokens_pkey;
ALTER TABLE IF EXISTS ONLY public.questions DROP CONSTRAINT IF EXISTS questions_pkey;
ALTER TABLE IF EXISTS ONLY public.packs DROP CONSTRAINT IF EXISTS packs_pkey;
ALTER TABLE IF EXISTS ONLY public.pack_manifests DROP CONSTRAINT IF EXISTS pack_manifests_pkey;
ALTER TABLE IF EXISTS ONLY public.pack_chapters DROP CONSTRAINT IF EXISTS pack_chapters_pkey;
ALTER TABLE IF EXISTS ONLY public.learning_sessions DROP CONSTRAINT IF EXISTS learning_sessions_pkey;
ALTER TABLE IF EXISTS ONLY public.learner_progress DROP CONSTRAINT IF EXISTS learner_progress_pkey;
ALTER TABLE IF EXISTS ONLY public.learner_profiles DROP CONSTRAINT IF EXISTS learner_profiles_pkey;
ALTER TABLE IF EXISTS ONLY public.learner_profiles DROP CONSTRAINT IF EXISTS learner_profiles_active_device_id_key;
ALTER TABLE IF EXISTS ONLY public.learner_events DROP CONSTRAINT IF EXISTS learner_events_pkey;
ALTER TABLE IF EXISTS ONLY public.learner_events DROP CONSTRAINT IF EXISTS learner_events_event_id_key;
ALTER TABLE IF EXISTS ONLY public.learner_devices DROP CONSTRAINT IF EXISTS learner_devices_pkey;
ALTER TABLE IF EXISTS ONLY public.learner_bloom_progress DROP CONSTRAINT IF EXISTS learner_bloom_progress_pkey;
ALTER TABLE IF EXISTS ONLY public.langgraph_writes DROP CONSTRAINT IF EXISTS langgraph_writes_pkey;
ALTER TABLE IF EXISTS ONLY public.langgraph_checkpoints DROP CONSTRAINT IF EXISTS langgraph_checkpoints_pkey;
ALTER TABLE IF EXISTS ONLY public.jobs DROP CONSTRAINT IF EXISTS jobs_pkey;
ALTER TABLE IF EXISTS ONLY public.jobs DROP CONSTRAINT IF EXISTS jobs_dedupe_key_key;
ALTER TABLE IF EXISTS ONLY public.installed_packs DROP CONSTRAINT IF EXISTS installed_packs_pkey;
ALTER TABLE IF EXISTS ONLY public.glossary DROP CONSTRAINT IF EXISTS glossary_term_or_term_en_key;
ALTER TABLE IF EXISTS ONLY public.glossary DROP CONSTRAINT IF EXISTS glossary_pkey;
ALTER TABLE IF EXISTS ONLY public.generation_records DROP CONSTRAINT IF EXISTS generation_records_pkey;
ALTER TABLE IF EXISTS ONLY public.devices DROP CONSTRAINT IF EXISTS devices_pkey;
ALTER TABLE IF EXISTS ONLY public.decisions DROP CONSTRAINT IF EXISTS decisions_pkey;
ALTER TABLE IF EXISTS ONLY public.decision_traces DROP CONSTRAINT IF EXISTS decision_traces_pkey;
ALTER TABLE IF EXISTS ONLY public.dead_letter_events DROP CONSTRAINT IF EXISTS dead_letter_events_pkey;
ALTER TABLE IF EXISTS ONLY public.concepts DROP CONSTRAINT IF EXISTS concepts_pkey;
ALTER TABLE IF EXISTS ONLY public.chunks DROP CONSTRAINT IF EXISTS chunks_pkey;
ALTER TABLE IF EXISTS ONLY public.chapters DROP CONSTRAINT IF EXISTS chapters_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_challenges DROP CONSTRAINT IF EXISTS auth_challenges_pkey;
ALTER TABLE IF EXISTS ONLY public.alembic_version DROP CONSTRAINT IF EXISTS alembic_version_pkc;
ALTER TABLE IF EXISTS public.glossary ALTER COLUMN glossary_id DROP DEFAULT;
DROP TABLE IF EXISTS public.sync_cursors;
DROP TABLE IF EXISTS public.refresh_tokens;
DROP TABLE IF EXISTS public.questions;
DROP TABLE IF EXISTS public.packs;
DROP TABLE IF EXISTS public.pack_manifests;
DROP TABLE IF EXISTS public.pack_chapters;
DROP TABLE IF EXISTS public.learning_sessions;
DROP TABLE IF EXISTS public.learner_progress;
DROP TABLE IF EXISTS public.learner_profiles;
DROP TABLE IF EXISTS public.learner_events;
DROP TABLE IF EXISTS public.learner_devices;
DROP TABLE IF EXISTS public.learner_bloom_progress;
DROP TABLE IF EXISTS public.langgraph_writes;
DROP TABLE IF EXISTS public.langgraph_checkpoints;
DROP TABLE IF EXISTS public.jobs;
DROP TABLE IF EXISTS public.installed_packs;
DROP SEQUENCE IF EXISTS public.glossary_glossary_id_seq;
DROP TABLE IF EXISTS public.glossary;
DROP TABLE IF EXISTS public.generation_records;
DROP TABLE IF EXISTS public.devices;
DROP TABLE IF EXISTS public.device_tokens;
DROP TABLE IF EXISTS public.decisions;
DROP TABLE IF EXISTS public.decision_traces;
DROP TABLE IF EXISTS public.dead_letter_events;
DROP TABLE IF EXISTS public.concepts;
DROP TABLE IF EXISTS public.chunks;
DROP TABLE IF EXISTS public.chapters;
DROP TABLE IF EXISTS public.auth_challenges;
DROP TABLE IF EXISTS public.alembic_version;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: auth_challenges; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_challenges (
    nonce text NOT NULL,
    device_id text NOT NULL,
    created_at bigint NOT NULL,
    expires_at bigint NOT NULL,
    used_at bigint
);


--
-- Name: chapters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chapters (
    chapter_id text NOT NULL,
    subject text NOT NULL,
    grade text NOT NULL,
    title_or text NOT NULL,
    title_en text NOT NULL,
    summary_or text DEFAULT ''::text NOT NULL,
    source_refs_json text DEFAULT '[]'::text NOT NULL
);


--
-- Name: chunks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chunks (
    chunk_id text NOT NULL,
    concept_id text NOT NULL,
    chapter_id text NOT NULL,
    title_or text NOT NULL,
    text_or text NOT NULL,
    glossary_terms_json text DEFAULT '[]'::text NOT NULL,
    source_ref text NOT NULL,
    media_refs_json text DEFAULT '[]'::text NOT NULL,
    token_count integer DEFAULT 0 NOT NULL
);


--
-- Name: concepts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.concepts (
    concept_id text NOT NULL,
    chapter_id text NOT NULL,
    title_or text NOT NULL,
    title_en text NOT NULL,
    summary_or text DEFAULT ''::text NOT NULL,
    prerequisites_json text DEFAULT '[]'::text NOT NULL,
    source_refs_json text DEFAULT '[]'::text NOT NULL
);


--
-- Name: dead_letter_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dead_letter_events (
    event_id text NOT NULL,
    device_id text NOT NULL,
    learner_id text NOT NULL,
    seq integer NOT NULL,
    reason text NOT NULL,
    last_error_code text NOT NULL,
    received_at bigint NOT NULL,
    dead_at bigint NOT NULL
);


--
-- Name: decision_traces; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.decision_traces (
    decision_id text NOT NULL,
    step_ordinal integer NOT NULL,
    step_id text NOT NULL,
    node text NOT NULL,
    tool text,
    provider text,
    ruleset_version text,
    model_id text,
    status text NOT NULL,
    error_code text,
    duration_ms integer NOT NULL,
    retry integer,
    fallback text,
    input_summary_json text DEFAULT '{}'::text NOT NULL,
    output_summary_json text DEFAULT '{}'::text NOT NULL,
    redacted integer DEFAULT 1 NOT NULL
);


--
-- Name: decisions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.decisions (
    decision_id text NOT NULL,
    learner_id text NOT NULL,
    ruleset_version text NOT NULL,
    target_concept_id text NOT NULL,
    action text NOT NULL,
    delivery_mode text NOT NULL,
    background_actions_json text DEFAULT '[]'::text NOT NULL,
    reason_code text NOT NULL,
    reason_or text NOT NULL,
    needs_help integer DEFAULT 0 NOT NULL,
    chapter_id text,
    suggested_question_id text,
    suggested_chunk_id text,
    network text DEFAULT 'offline'::text NOT NULL,
    source text DEFAULT 'server'::text NOT NULL,
    produced_by text DEFAULT 'rule_engine'::text NOT NULL,
    created_at bigint NOT NULL,
    target_bloom_level text,
    trigger_event_id text
);


--
-- Name: device_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.device_tokens (
    device_id text NOT NULL,
    token_hash text NOT NULL,
    issued_at bigint NOT NULL,
    expires_at bigint NOT NULL,
    revoked integer DEFAULT 0 NOT NULL
);


--
-- Name: devices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.devices (
    device_id text NOT NULL,
    hardware_label text DEFAULT 'shared-android-low-end'::text NOT NULL,
    public_key_spki text,
    created_at bigint NOT NULL,
    last_seen_at bigint,
    revoked_at bigint
);


--
-- Name: generation_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.generation_records (
    record_id text NOT NULL,
    decision_id text NOT NULL,
    provider text NOT NULL,
    model_id text,
    prompt_version text NOT NULL,
    prompt_hash text NOT NULL,
    params_json text DEFAULT '{}'::text NOT NULL,
    chunk_ids_json text DEFAULT '[]'::text NOT NULL,
    output_or text DEFAULT ''::text NOT NULL,
    validation_results_json text DEFAULT '{}'::text NOT NULL,
    fallback_used integer DEFAULT 0 NOT NULL,
    created_at bigint NOT NULL
);


--
-- Name: glossary; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.glossary (
    glossary_id integer NOT NULL,
    term_or text NOT NULL,
    term_en text NOT NULL,
    definition_or text NOT NULL,
    definition_en text NOT NULL
);


--
-- Name: glossary_glossary_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.glossary_glossary_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: glossary_glossary_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.glossary_glossary_id_seq OWNED BY public.glossary.glossary_id;


--
-- Name: installed_packs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.installed_packs (
    device_id text NOT NULL,
    pack_id text NOT NULL,
    version text NOT NULL,
    installed_at integer NOT NULL,
    byte_size integer NOT NULL,
    checksum_sha256 text NOT NULL
);


--
-- Name: jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.jobs (
    job_id text NOT NULL,
    type text NOT NULL,
    payload_json text DEFAULT '{}'::text NOT NULL,
    dedupe_key text,
    status text DEFAULT 'queued'::text NOT NULL,
    attempts integer DEFAULT 0 NOT NULL,
    max_attempts integer DEFAULT 6 NOT NULL,
    next_run_at bigint NOT NULL,
    lease_expires_at bigint,
    last_error text,
    created_at bigint NOT NULL,
    updated_at bigint NOT NULL
);


--
-- Name: langgraph_checkpoints; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.langgraph_checkpoints (
    thread_id text NOT NULL,
    checkpoint_ns text DEFAULT ''::text NOT NULL,
    checkpoint_id text NOT NULL,
    parent_checkpoint_id text,
    type text DEFAULT 'dict'::text NOT NULL,
    config_json text NOT NULL,
    metadata_json text DEFAULT '{}'::text NOT NULL,
    blob bytea,
    created_at bigint NOT NULL
);


--
-- Name: langgraph_writes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.langgraph_writes (
    thread_id text NOT NULL,
    checkpoint_ns text DEFAULT ''::text NOT NULL,
    checkpoint_id text NOT NULL,
    task_id text NOT NULL,
    channel text NOT NULL,
    type text NOT NULL,
    blob bytea,
    created_at bigint NOT NULL
);


--
-- Name: learner_bloom_progress; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.learner_bloom_progress (
    learner_id text NOT NULL,
    concept_id text NOT NULL,
    bloom_level text NOT NULL,
    p_bp integer DEFAULT 2000 NOT NULL,
    bkt_version text DEFAULT '1'::text NOT NULL,
    band text DEFAULT 'weak'::text NOT NULL,
    attempts integer DEFAULT 0 NOT NULL,
    correct integer DEFAULT 0 NOT NULL,
    last_event_seq integer
);


--
-- Name: learner_devices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.learner_devices (
    learner_id text NOT NULL,
    device_id text NOT NULL,
    status text DEFAULT 'active'::text NOT NULL,
    first_seen_at bigint NOT NULL,
    last_active_at bigint NOT NULL
);


--
-- Name: learner_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.learner_events (
    device_id text NOT NULL,
    learner_id text NOT NULL,
    seq integer NOT NULL,
    event_id text NOT NULL,
    client_ts bigint NOT NULL,
    event_type text NOT NULL,
    concept_id text,
    chapter_id text,
    question_id text,
    payload_json text DEFAULT '{}'::text NOT NULL,
    status text DEFAULT 'accepted'::text NOT NULL,
    effect text,
    reason text,
    received_at bigint NOT NULL,
    server_seq integer
);


--
-- Name: learner_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.learner_profiles (
    learner_id text NOT NULL,
    display_label text DEFAULT ''::text NOT NULL,
    locale text DEFAULT 'or'::text NOT NULL,
    grade text DEFAULT 'class9'::text NOT NULL,
    subject text DEFAULT 'science'::text NOT NULL,
    pin_hash text,
    created_at bigint NOT NULL,
    active_device_id text
);


--
-- Name: learner_progress; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.learner_progress (
    learner_id text NOT NULL,
    concept_id text NOT NULL,
    p_bp integer DEFAULT 2000 NOT NULL,
    attempts integer DEFAULT 0 NOT NULL,
    correct integer DEFAULT 0 NOT NULL,
    last_seen_at bigint,
    last_event_seq integer,
    bkt_version text DEFAULT '1'::text NOT NULL
);


--
-- Name: learning_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.learning_sessions (
    session_id text NOT NULL,
    learner_id text NOT NULL,
    device_id text NOT NULL,
    started_at integer NOT NULL,
    ended_at integer,
    last_decision_id text
);


--
-- Name: pack_chapters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pack_chapters (
    pack_id text NOT NULL,
    version text NOT NULL,
    chapter_id text NOT NULL
);


--
-- Name: pack_manifests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pack_manifests (
    pack_id text NOT NULL,
    version text NOT NULL,
    title_or text NOT NULL,
    language text DEFAULT 'or'::text NOT NULL,
    byte_size integer NOT NULL,
    checksum_sha256 text NOT NULL,
    min_app_version text NOT NULL,
    licence text NOT NULL,
    source_refs_json text DEFAULT '[]'::text NOT NULL,
    created_at integer NOT NULL,
    chapters_json text DEFAULT '[]'::text NOT NULL
);


--
-- Name: packs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.packs (
    pack_id text NOT NULL,
    version text NOT NULL,
    content_version text NOT NULL,
    language text DEFAULT 'or'::text NOT NULL,
    byte_size integer NOT NULL,
    checksum_sha256 text NOT NULL,
    min_app_version text NOT NULL,
    licence text NOT NULL,
    source_refs_json text DEFAULT '[]'::text NOT NULL,
    created_at integer NOT NULL,
    published integer DEFAULT 1 NOT NULL
);


--
-- Name: questions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.questions (
    question_id text NOT NULL,
    concept_id text NOT NULL,
    chapter_id text NOT NULL,
    text_or text NOT NULL,
    options_json text NOT NULL,
    correct_answer text NOT NULL,
    explanation_or text DEFAULT ''::text NOT NULL,
    difficulty text DEFAULT 'medium'::text NOT NULL,
    bloom_level text DEFAULT 'remember'::text NOT NULL,
    misconception_tag text,
    status text DEFAULT 'active'::text NOT NULL,
    revision integer DEFAULT 1 NOT NULL,
    answer_key_hash text DEFAULT ''::text NOT NULL,
    source_ref text DEFAULT ''::text NOT NULL
);


--
-- Name: refresh_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.refresh_tokens (
    id text NOT NULL,
    device_id text NOT NULL,
    token_hash text NOT NULL,
    issued_at bigint NOT NULL,
    expires_at bigint NOT NULL,
    used_at bigint,
    revoked integer DEFAULT 0 NOT NULL
);


--
-- Name: sync_cursors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sync_cursors (
    device_id text NOT NULL,
    learner_id text NOT NULL,
    last_acked_seq integer DEFAULT 0 NOT NULL,
    last_server_seq integer DEFAULT 0 NOT NULL,
    last_acked_at bigint DEFAULT 0 NOT NULL
);


--
-- Name: glossary glossary_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.glossary ALTER COLUMN glossary_id SET DEFAULT nextval('public.glossary_glossary_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
003_langgraph_writes
\.


--
-- Data for Name: auth_challenges; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_challenges (nonce, device_id, created_at, expires_at, used_at) FROM stdin;
\.


--
-- Data for Name: chapters; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.chapters (chapter_id, subject, grade, title_or, title_en, summary_or, source_refs_json) FROM stdin;
\.


--
-- Data for Name: chunks; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.chunks (chunk_id, concept_id, chapter_id, title_or, text_or, glossary_terms_json, source_ref, media_refs_json, token_count) FROM stdin;
\.


--
-- Data for Name: concepts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.concepts (concept_id, chapter_id, title_or, title_en, summary_or, prerequisites_json, source_refs_json) FROM stdin;
\.


--
-- Data for Name: dead_letter_events; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dead_letter_events (event_id, device_id, learner_id, seq, reason, last_error_code, received_at, dead_at) FROM stdin;
\.


--
-- Data for Name: decision_traces; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.decision_traces (decision_id, step_ordinal, step_id, node, tool, provider, ruleset_version, model_id, status, error_code, duration_ms, retry, fallback, input_summary_json, output_summary_json, redacted) FROM stdin;
\.


--
-- Data for Name: decisions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.decisions (decision_id, learner_id, ruleset_version, target_concept_id, action, delivery_mode, background_actions_json, reason_code, reason_or, needs_help, chapter_id, suggested_question_id, suggested_chunk_id, network, source, produced_by, created_at, target_bloom_level, trigger_event_id) FROM stdin;
\.


--
-- Data for Name: device_tokens; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.device_tokens (device_id, token_hash, issued_at, expires_at, revoked) FROM stdin;
\.


--
-- Data for Name: devices; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.devices (device_id, hardware_label, public_key_spki, created_at, last_seen_at, revoked_at) FROM stdin;
\.


--
-- Data for Name: generation_records; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.generation_records (record_id, decision_id, provider, model_id, prompt_version, prompt_hash, params_json, chunk_ids_json, output_or, validation_results_json, fallback_used, created_at) FROM stdin;
\.


--
-- Data for Name: glossary; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.glossary (glossary_id, term_or, term_en, definition_or, definition_en) FROM stdin;
\.


--
-- Data for Name: installed_packs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.installed_packs (device_id, pack_id, version, installed_at, byte_size, checksum_sha256) FROM stdin;
\.


--
-- Data for Name: jobs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.jobs (job_id, type, payload_json, dedupe_key, status, attempts, max_attempts, next_run_at, lease_expires_at, last_error, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: langgraph_checkpoints; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.langgraph_checkpoints (thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, type, config_json, metadata_json, blob, created_at) FROM stdin;
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	\N	msgpack	{"tags": [], "metadata": "ChainMap({'thread_id': 'doubt_thread_test_002'})", "callbacks": null, "recursion_limit": 10007, "configurable": {"checkpoint_ns": "", "thread_id": "doubt_thread_test_002", "__pregel_runtime": "Runtime(context=None, store=None, stream_writer=<function Pregel.astream.<locals>.stream_writer at 0x7fdfbba475e0>, heartbeat=<function _no_op_heartbeat at 0x7fdfbd582a30>, previous=None, execution_info=None, server_info=None, control=<langgraph.runtime.RunControl object at 0x7fdfbc5febc0>)"}}	{"source": "input", "step": -1, "parents": {}}	\\x87a17604a27473d920323032362d31302d31345432323a34393a30372e3934373433352b30303a3030a26964d92431663163383231372d366536342d363530372d626666662d646430383664613432343333ae6368616e6e656c5f76616c75657381a95f5f73746172745f5fc8013f0293b76170702e6f726368657374726174696f6e2e6772617068b24f726368657374726174696f6e53746174658fa57175657279b7576861742069732070686f746f73796e7468657369733fad6c6561726e65725f696e707574b7576861742069732070686f746f73796e7468657369733fb07472616e736c617465645f7175657279c0b5757365645f7472616e736c6174696f6e5f746f6f6cc2a972657472696576616cc0a6616e73776572c0a5747261636590aa746f6f6c5f63616c6c7300aa737461727465645f6d73cf000001a13c9aea5eab6465636973696f6e5f6964b5646f7562745f7468726561645f746573745f303032a56572726f72c0ab72657472795f636f756e7400b276616c69646174696f6e5f726573756c747380ad66616c6c6261636b5f75736564c2b067656e65726174696f6e5f6572726f72c0b06368616e6e656c5f76657273696f6e7381a95f5f73746172745f5f01ad76657273696f6e735f7365656e81a95f5f696e7075745f5f80b0757064617465645f6368616e6e656c7391a95f5f73746172745f5f	1792018147947
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	1f1c8217-6e64-6507-bfff-dd086da42433	msgpack	{"tags": [], "metadata": "ChainMap({'thread_id': 'doubt_thread_test_002'})", "callbacks": null, "recursion_limit": 10007, "configurable": {"checkpoint_ns": "", "thread_id": "doubt_thread_test_002", "__pregel_runtime": "Runtime(context=None, store=None, stream_writer=<function Pregel.astream.<locals>.stream_writer at 0x7fdfbba475e0>, heartbeat=<function _no_op_heartbeat at 0x7fdfbd582a30>, previous=None, execution_info=None, server_info=None, control=<langgraph.runtime.RunControl object at 0x7fdfbc5febc0>)", "checkpoint_id": "1f1c8217-6e64-6507-bfff-dd086da42433"}}	{"source": "loop", "step": 0, "parents": {}}	\\x87a17604a27473d920323032362d31302d31345432323a34393a30372e3934393539362b30303a3030a26964d92431663163383231372d366536392d363963332d383030302d386165636535653531383161ae6368616e6e656c5f76616c756573de0010a57175657279b7576861742069732070686f746f73796e7468657369733fad6c6561726e65725f696e707574b7576861742069732070686f746f73796e7468657369733fb07472616e736c617465645f7175657279c0b5757365645f7472616e736c6174696f6e5f746f6f6cc2a972657472696576616cc0a6616e73776572c0a5747261636594c801d70594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b063376462336262343063343034623731a46e6f6465af646f7562742e7472616e736c617465a57374616765af646f7562742e7472616e736c617465a4746f6f6cae7472616e736c6174655f74657874a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a866616c6c6261636baa6572726f725f636f6465ab554e415641494c41424c45ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727981a6726561736f6ed9a75452414e534c4154494f4e5f50524f56494445523d6d6f636b20e2809420736574205452414e534c4154494f4e5f50524f56494445523d68665f6c6f63616c2028616e642048465f544f4b454e20666f722074686520676174656420496e6469635472616e7332207265706f73292e20546865206f66666c696e65206c6561726e696e67207061746820646f6573206e6f742072657175697265207472616e736c6174696f6e2ea87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8013d0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b033363431333233373264663534306135a46e6f6465ae646f7562742e7265747269657665a57374616765ae646f7562742e7265747269657665a4746f6f6caf72657472696576655f6368756e6b73a870726f7669646572ac6c6f63616c5f687962726964af72756c657365745f76657273696f6ec0a86d6f64656c5f6964a46d6f636ba6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7346a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727982a66368756e6b7304aa636f6e666964656e6365cb3ff0000000000000a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8012a0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b064616638346166666363363834616665a46e6f6465ae646f7562742e67656e6572617465a57374616765ae646f7562742e67656e6572617465a4746f6f6caf67656e65726174655f616e73776572a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a66368756e6b7304ae6f75747075745f73756d6d61727982a36c656ecd0257a96369746174696f6e7301a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec801280594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b030356239616662616166366134613330a46e6f6465ae646f7562742e76616c6964617465a57374616765ae646f7562742e76616c6964617465a4746f6f6caf76616c69646174655f616e73776572a870726f7669646572c0af72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981aa616e737765725f6c656ecd0257ae6f75747075745f73756d6d61727981ac67617465735f70617373656405a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6eaa746f6f6c5f63616c6c7300aa737461727465645f6d73cf000001a13c9aea5eab6465636973696f6e5f6964b5646f7562745f7468726561645f746573745f303032a56572726f72c0ab72657472795f636f756e7400b276616c69646174696f6e5f726573756c747380ad66616c6c6261636b5f75736564c2b067656e65726174696f6e5f6572726f72c0b36272616e63683a746f3a7472616e736c617465c0b06368616e6e656c5f76657273696f6e73de0011a95f5f73746172745f5f02a5717565727902ad6c6561726e65725f696e70757402b07472616e736c617465645f717565727902b5757365645f7472616e736c6174696f6e5f746f6f6c02a972657472696576616c02a6616e7377657202a5747261636502aa746f6f6c5f63616c6c7302aa737461727465645f6d7302ab6465636973696f6e5f696402a56572726f7202ab72657472795f636f756e7402b276616c69646174696f6e5f726573756c747302ad66616c6c6261636b5f7573656402b067656e65726174696f6e5f6572726f7202b36272616e63683a746f3a7472616e736c61746502ad76657273696f6e735f7365656e82a95f5f696e7075745f5f80a95f5f73746172745f5f81a95f5f73746172745f5f01b0757064617465645f6368616e6e656c73dc0010a6616e73776572b36272616e63683a746f3a7472616e736c617465ab6465636973696f6e5f6964a56572726f72ad66616c6c6261636b5f75736564b067656e65726174696f6e5f6572726f72ad6c6561726e65725f696e707574a57175657279a972657472696576616cab72657472795f636f756e74aa737461727465645f6d73aa746f6f6c5f63616c6c73a57472616365b07472616e736c617465645f7175657279b5757365645f7472616e736c6174696f6e5f746f6f6cb276616c69646174696f6e5f726573756c7473	1792018148034
doubt_thread_test_002		1f1c8217-6f31-673c-8003-5d4532aaf205	1f1c8217-6f25-6eb3-8002-597934130cd1	msgpack	{"tags": [], "metadata": "ChainMap({'thread_id': 'doubt_thread_test_002'})", "callbacks": null, "recursion_limit": 10007, "configurable": {"checkpoint_ns": "", "thread_id": "doubt_thread_test_002", "__pregel_runtime": "Runtime(context=None, store=None, stream_writer=<function Pregel.astream.<locals>.stream_writer at 0x7fdfbba475e0>, heartbeat=<function _no_op_heartbeat at 0x7fdfbd582a30>, previous=None, execution_info=None, server_info=None, control=<langgraph.runtime.RunControl object at 0x7fdfbc5febc0>)", "checkpoint_id": "1f1c8217-6f25-6eb3-8002-597934130cd1"}}	{"source": "loop", "step": 3, "parents": {}}	\\x87a17604a27473d920323032362d31302d31345432323a34393a30382e3033313434342b30303a3030a26964d92431663163383231372d366633312d363733632d383030332d356434353332616166323035ae6368616e6e656c5f76616c756573de0010a57175657279b7576861742069732070686f746f73796e7468657369733fad6c6561726e65725f696e707574b7576861742069732070686f746f73796e7468657369733fb07472616e736c617465645f7175657279c0b5757365645f7472616e736c6174696f6e5f746f6f6cc3a972657472696576616cc81e0e0594b26170702e646f6d61696e2e736368656d6173af526574726965766564526573756c7484a66368756e6b739487a86368756e6b5f6964b36368756e6b5f636830315f63303030325f3031aa636f6e636570745f6964a56330303032aa636861707465725f6964a56368303031a7746578745f6f72da06c2e0ac98e0aca8e0aca4e0ad8de0adb1202864656e736974792920e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0ad8ce0aca3e0acb8e0acbf20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac8fe0ac95e0ac9520e0ac86e0ad9fe0aca4e0aca8e0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1e0acb020e0acaae0acb0e0acbfe0acaee0acbee0aca3e0a5a420e0ac8fe0acb9e0acbee0ac95e0ad8120e0ac97e0acbee0aca3e0acbfe0aca4e0acbfe0ac9520e0acade0acbee0acace0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1203d20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1202f20e0ac86e0ad9fe0aca4e0aca8202844656e73697479203d204d617373202f20566f6c756d652920e0acace0ad8be0acb2e0acbf20e0acaae0ad8de0acb0e0ac95e0acbee0acb620e0ac95e0acb0e0acbee0acafe0acbee0ac8f2c20e0acafe0acbee0acb9e0acbee0acb020e0acb8e0ac99e0ad8de0ac95e0ad87e0aca420e0acb9e0ad87e0ac89e0ac9be0acbf20cf812028e0acb0e0ad8b2920e0ac95e0acbfe0acaee0ad8de0acace0acbe2064203d204d202f2056e0a5a420e0ac86e0aca8e0ad8de0aca4e0acb0e0ad8de0ac9ce0acbee0aca4e0ad80e0ad9f20e0acaee0acbee0aca8e0ac95202853492920e0acaae0aca6e0ad8de0aca7e0aca4e0acbfe0acb0e0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1e0acb020e0ac8fe0ac95e0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0acbfe0acb2e0ad8be0ac97e0ad8de0acb0e0acbee0acae20e0acaae0ad8de0acb0e0aca4e0acbf20e0ac98e0aca820e0acaee0acbfe0ac9fe0acb020286b672f6dc2b329e0a5a420e0acb8e0acbee0aca7e0acbee0acb0e0aca3e0aca4e0ac8320e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac85e0aca7e0acbfe0ac9520e0aca5e0acbee0ac8f2c20e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaee0aca7e0ad8de0ad9fe0acae20e0ac8fe0acace0ac8220e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac95e0acaee0ad8d20e0aca5e0acbee0ac8fe0a5a420e0ac89e0aca6e0acbee0acb9e0acb0e0aca320e0acb8e0ad8de0adb1e0acb0e0ad82e0acaa2c20e0acb2e0ad81e0acb9e0acbee0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0ac95e0acbee0aca020e0aca4e0ad81e0acb3e0aca8e0acbee0acb0e0ad8720e0acace0acb9e0ad81e0aca420e0ac85e0aca7e0acbfe0ac952c20e0ac95e0acbee0acb0e0aca320e0acb2e0ad81e0acb9e0acbee0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acaae0acb0e0acaee0acbee0aca3e0ad81e0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0ac85e0aca4e0acbf20e0aca8e0acbfe0acace0acbfe0aca1e0acbc20e0acade0acbee0acace0ad8720e0acb8e0ac9ce0ad8de0ac9ce0acbfe0aca420e0acb9e0ad8be0ac8720e0acb0e0acb9e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbfe0a5a420e0adaa20e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0acace0acbfe0acb6e0ad81e0aca6e0ad8de0aca720e0ac9ce0acb3e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaae0ad8de0acb0e0acbee0ad9f20e0ada7e0ada6e0ada6e0ada6206b672f6dc2b32028e0acace0acbe20e0ada720672f636dc2b32920e0acb9e0ad8be0ac87e0aca5e0acbee0ac8fe0a5a420e0ac95e0ad8ce0aca3e0acb8e0acbf20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0aca4e0acbee0acb020e0ac85e0aca3e0ad81e0ac97e0ad81e0aca1e0acbce0acbfe0ac95e0acb020e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb120e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0ad8020e0aca6e0ad82e0acb0e0aca4e0acbe20e0ac89e0acaae0acb0e0ad8720e0aca8e0acbfe0acb0e0ad8de0acade0acb020e0ac95e0acb0e0acbfe0aca5e0acbee0ac8fe0a5a4aa736f757263655f726566aa6368303120c2a7312e33a573636f7265cb3ff0000000000000ad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030315f3032aa636f6e636570745f6964a56330303031aa636861707465725f6964a56368303031a7746578745f6f72da06f3e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0aca4e0acbfe0aca8e0ad8be0ac9fe0acbf20e0ac85e0acace0acb8e0ad8de0aca5e0acbee0acb020e0acade0acbfe0aca8e0ad8de0aca820e0acade0acbfe0aca8e0ad8de0aca820e0acade0ad8ce0aca4e0acbfe0ac9520e0aca7e0acb0e0ad8de0acae20e0acb0e0acb9e0acbfe0ac9be0acbfe0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020286669786564207368617065292c20e0acb8e0ad8de0acaae0acb7e0ad8de0ac9f20e0acb8e0ad80e0acaee0acbee0acb0e0ad87e0ac96e0acbe20e0ac8fe0acace0ac8220e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ad9fe0aca4e0aca82028666978656420766f6c756d652920e0aca5e0acbee0ac8fe0a5a420e0ac8fe0acb9e0acbe20e0acb8e0acb9e0ac9ce0acb0e0ad8720e0acb8e0ac99e0ad8de0ac95e0ad81e0ac9ae0acbfe0aca42028636f6d707265737369626c652920e0acb9e0ad8be0ac87e0acaae0acbee0acb0e0ad8720e0aca8e0acbee0acb9e0acbfe0ac81e0a5a420e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac95e0ad8ce0aca3e0acb8e0acbf20e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020e0aca8e0aca5e0acbee0ac8f2c20e0ac95e0acbfe0aca8e0ad8de0aca4e0ad8120e0ac8fe0acb9e0acbee0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ad9fe0aca4e0aca820e0aca5e0acbee0ac8fe0a5a420e0aca4e0acb0e0acb3e0ac95e0ad8120e0acafe0ad87e0ac89e0ac8120e0acaae0acbee0aca4e0ad8de0acb0e0acb0e0ad8720e0acb0e0ac96e0acbee0acafe0acbee0ac8f2c20e0aca4e0acbee0acb9e0acbe20e0acb8e0ad87e0acb9e0acbf20e0acaae0acbee0aca4e0ad8de0acb0e0acb020e0ac86e0ac95e0acbee0acb020e0aca7e0acbee0acb0e0aca320e0ac95e0acb0e0ad87e0a5a420e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac95e0ad8ce0aca3e0acb8e0acbf20e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac86e0ad9fe0aca4e0aca820e0aca8e0aca5e0acbee0ac8f3b20e0ac8fe0acb9e0acbe20e0ac89e0acaae0acb2e0acace0ad8de0aca720e0acb8e0acaee0acb8e0ad8de0aca420e0acb8e0ad8de0aca5e0acbee0aca8e0ac95e0ad8120e0acaae0ad82e0acb0e0ad8de0aca3e0ad8de0aca320e0ac95e0acb0e0acbfe0aca6e0acbfe0ac8fe0a5a420e0ac97e0ad8de0ad9fe0acbee0acb8e0acb020e0acb8e0ac99e0ad8de0ac95e0ad8be0ac9ae0aca8e0acb6e0ad80e0acb3e0aca4e0acbe2028636f6d70726573736962696c6974792920e0acb8e0acb0e0ad8de0acace0acbee0aca7e0acbfe0ac9520e0acb9e0ad8be0ac87e0aca5e0acbfe0acace0acbee0acb0e0ad8120e0ac8fe0acb9e0acbee0ac95e0ad8120e0ac89e0ac9ae0ad8de0ac9a20e0ac9ae0acbee0acaae0acb0e0ad8720e0acb8e0acbfe0acb2e0acbfe0aca3e0ad8de0aca1e0acb020e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0acade0acb0e0ad8de0aca4e0ad8de0aca4e0acbf20e0ac95e0acb0e0acbee0acafe0acbee0ac87e0acaae0acbee0acb0e0ad872c20e0acafe0ad87e0acaae0acb0e0acbfe0ac95e0acbf20e0ac86e0acae20e0ac98e0acb0e0ad8720e0acace0ad8de0ad9fe0acace0acb9e0ad83e0aca420e0acb9e0ad87e0ac89e0aca5e0acbfe0acace0acbe20e0ac8fe0acb2e0acaae0acbfe0ac9ce0acbf20284c50472920e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac85e0ac95e0ad8de0acb8e0acbfe0ac9ce0ad87e0aca820e0acb8e0acbfe0acb2e0acbfe0aca3e0ad8de0aca1e0acb0e0a5a420e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0ac97e0aca4e0acbfe0ac9c20e0acb6e0ac95e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0ac86e0aca8e0ad8de0aca4e0ac83e0ac95e0aca3e0acbfe0ac95e0acbe20e0acb8e0ad8de0aca5e0acbee0aca820e0acb9e0acbfe0ac8120e0ac8fe0acb9e0acbf20e0acb8e0acaee0acb8e0ad8de0aca420e0acaae0acbee0acb0e0ad8de0aca5e0ac95e0ad8de0ad9fe0acb020e0acaee0ad82e0acb320e0ac95e0acbee0acb0e0aca320e0ac85e0ac9fe0ad87e0a5a4aa736f757263655f726566aa6368303120c2a7312e32a573636f7265cb3fdd17fa84aa97caad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030335f3031aa636f6e636570745f6964a56330303033aa636861707465725f6964a56368303031a7746578745f6f72da06e2e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbe20e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac9ae0acbee0acaae0acb020e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0ac98e0ac9fe0acbee0ac8720e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac85e0acace0acb8e0ad8de0aca5e0acbe20e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0ac95e0acb0e0acbee0acafe0acbee0ac87e0acaae0acbee0acb0e0ad87e0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0ac95e0ad8120e0ac97e0acb0e0acae20e0ac95e0acb2e0ad8720e0aca4e0acbee0acb020e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0ac97e0aca4e0acbfe0ac9c20e0acb6e0ac95e0ad8de0aca4e0acbf20e0acace0aca2e0acbce0acbfe0acafe0acbee0ac8f20e0ac8fe0acace0ac8220e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0ac8fe0acb9e0acbe20e0aca4e0acb0e0acb3e0acbfe0acace0acbee0ac95e0ad8120e0acb2e0acbee0ac97e0ad87e0a5a420e0acafe0ad87e0ac89e0ac8120e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0acace0acbee0ad9fe0ad81e0acaee0aca3e0ad8de0aca1e0acb3e0ad80e0ad9f20e0ac9ae0acbee0acaae0acb0e0ad8720e0ac8fe0ac9520e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0aca4e0acb0e0acb3e0acb0e0ad8720e0acaae0acb0e0acbfe0aca3e0aca420e0acb9e0ad81e0ac8f2c20e0aca4e0acbee0acb9e0acbee0ac95e0ad8120e0aca4e0acbee0acb020e0ac97e0acb3e0aca8e0acbee0ac99e0ad8de0ac9520286d656c74696e6720706f696e742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a420e0acace0acb0e0acabe0acb020e0ac97e0acb3e0aca8e0acbee0ac99e0ad8de0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ada620e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0acace0acbe20e0ada8e0adade0ada920e0ac95e0ad87e0acb2e0acade0acbfe0aca8e0a5a420e0acb8e0ad87e0acb9e0acbfe0acaae0acb0e0acbf20e0acafe0ad87e0ac89e0ac8120e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acabe0ad81e0ac9fe0acbf20e0acace0acbee0acb7e0ad8de0acaae0acb0e0ad8720e0acaae0acb0e0acbfe0aca3e0aca420e0acb9e0ad81e0ac8f2c20e0aca4e0acbee0acb9e0acbee0ac95e0ad8120e0acb8e0ad8de0acabe0ad81e0ac9fe0aca8e0acbee0ac99e0ad8de0ac952028626f696c696e6720706f696e742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a420e0ac9ce0acb3e0acb020e0acb8e0ad8de0acabe0ad81e0ac9fe0aca8e0acbee0ac99e0ad8de0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ada7e0ada6e0ada620e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0acace0acbe20e0ada9e0adade0ada920e0ac95e0ad87e0acb2e0acade0acbfe0aca8e0a5a420e0ac85e0acace0acb8e0ad8de0aca5e0acbe20e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0acb8e0acaee0ad9fe0acb0e0ad8720e0acafe0ad8be0ac9720e0ac95e0acb0e0acbee0acafe0acbee0ac89e0aca5e0acbfe0acace0acbe20e0aca4e0acbee0acaa20e0acb6e0ac95e0ad8de0aca4e0acbf20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbe20e0aca820e0acace0aca2e0acbce0acbee0ac8720e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb3e0ac95e0ad8120e0acade0acbee0ac99e0ad8de0ac97e0acbfe0acace0acbee0acb0e0ad8720e0acace0ad8de0ad9fe0acace0acb9e0ad83e0aca420e0acb9e0ad81e0ac8f2c20e0acafe0acbee0acb9e0acbee0ac95e0ad8120e0ac97e0ad81e0acaae0ad8de0aca4e0aca4e0acbee0acaa20286c6174656e7420686561742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a4aa736f757263655f726566aa6368303120c2a7312e34a573636f7265cb3fdd17fa84aa97caad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030315f3031aa636f6e636570745f6964a56330303031aa636861707465725f6964a56368303031a7746578745f6f72da0702e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac86e0acae20e0acaae0acb0e0acbfe0acace0ad87e0acb6e0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acaae0ad8de0acb0e0aca4e0ad8de0ad9fe0ad87e0ac9520e0acace0acb8e0ad8de0aca4e0ad8120e0acafe0acbee0acb9e0acbee0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb120286d6173732920e0aca5e0acbee0ac8f20e0ac8fe0acace0ac8220e0acafe0acbee0acb9e0acbe20e0ac95e0acbfe0ac9be0acbf20e0acb8e0ad8de0aca5e0acbee0aca820e0acace0acbe20e0ac86e0ad9fe0aca4e0aca82028766f6c756d652920e0ac85e0aca7e0acbfe0ac95e0acbee0acb020e0ac95e0acb0e0ad87e0a5a420e0acaae0ad8de0acb0e0ac95e0ad83e0aca4e0acbfe0acb0e0ad8720e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acaee0ad81e0ac96e0ad8de0ad9fe0aca4e0ac8320e0aca4e0acbfe0aca8e0ad8be0ac9fe0acbf20e0acade0ad8ce0aca4e0acbfe0ac9520e0acb8e0ad8de0aca5e0acbfe0aca4e0acbfe0acb0e0ad8720e0aca6e0ad87e0ac96e0acbee0acafe0acbee0ac8f3a20e0ac95e0aca0e0acbfe0aca82028736f6c6964292c20e0aca4e0acb0e0acb320286c69717569642920e0ac8fe0acace0ac8220e0ac97e0ad8de0ad9fe0acbee0acb8202867617329e0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0ac85e0aca4e0ad8de0ad9fe0aca8e0ad8de0aca420e0aca8e0acbfe0acace0acbfe0aca1e0acbc20e0acade0acbee0acace0acb0e0ad8720e0acb8e0ac9ce0ad8de0ac9ce0acbfe0aca420e0acb9e0ad8be0ac8720e0acb0e0acb9e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0ac86e0aca8e0ad8de0aca4e0ac83e0ac95e0aca3e0acbfe0ac95e0acbe20e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb32028696e7465726d6f6c6563756c617220666f7263652920e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac85e0aca7e0acbfe0ac9520e0acaae0ad8de0acb0e0acace0acb320e0aca5e0acbee0ac8fe0a5a420e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0ac95e0acbfe0ac9be0acbf20e0acabe0acbee0ac99e0ad8de0ac95e0acbe20e0acb8e0ad8de0aca5e0acbee0aca820e0aca5e0acbee0ac8f20e0ac8fe0acace0ac8220e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb320e0ac95e0aca0e0acbfe0aca820e0aca4e0ad81e0acb3e0aca8e0acbee0acb0e0ad8720e0ac95e0acaee0ad8d20e0aca5e0acbee0ac8f2c20e0acafe0acbee0acb9e0acbe20e0acabe0acb3e0acb0e0ad8720e0acb8e0ad87e0acaee0acbee0aca8e0ad8720e0acaae0ad8de0acb0e0acace0acbee0acb9e0acbfe0aca420e0acb9e0ad8be0ac87e0acaae0acbee0acb0e0aca8e0ad8de0aca4e0acbfe0a5a420e0ac85e0aca8e0ad8de0ad9fe0acaae0ac95e0ad8de0acb7e0acb0e0ad872c20e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0acaae0acb0e0acb8e0ad8de0acaae0acb0e0aca0e0acbee0acb0e0ad8120e0acace0acb9e0ad81e0aca420e0aca6e0ad82e0acb0e0acb0e0ad8720e0aca5e0acbee0ac86e0aca8e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb320e0aca8e0ac97e0aca3e0ad8de0ad9f20e0aca5e0acbee0ac8fe0a5a420e0aca4e0ad87e0aca3e0ad8120e0ac97e0ad8de0ad9fe0acbee0acb8e0acb020e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0acb8e0acaee0acb8e0ad8de0aca420e0aca6e0acbfe0ac97e0acb0e0ad8720e0aca6e0ad8de0acb0e0ad81e0aca420e0ac9320e0acaee0ad81e0ac95e0ad8de0aca420e0acade0acbee0acace0acb0e0ad8720e0ac97e0aca4e0acbf20e0ac95e0acb0e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbfe0a5a4aa736f757263655f726566aa6368303120c2a7312e32a573636f7265cb0000000000000000ad6d6174636865645f7465726d7390a870726f7669646572ac6c6f63616c5f687962726964a86d6f64656c5f6964a46d6f636baa636f6e666964656e6365cb3ff0000000000000b36d6f64656c5f76616c69646174655f6a736f6ea6616e73776572c806750594b26170702e646f6d61696e2e736368656d6173af47656e657261746564416e7377657286a7746578745f6f72da05bfe0ac98e0aca8e0aca4e0ad8de0adb1202864656e736974792920e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0ad8ce0aca3e0acb8e0acbf20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac8fe0ac95e0ac9520e0ac86e0ad9fe0aca4e0aca8e0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1e0acb020e0acaae0acb0e0acbfe0acaee0acbee0aca3e0a5a420e0ac8fe0acb9e0acbee0ac95e0ad8120e0ac97e0acbee0aca3e0acbfe0aca4e0acbfe0ac9520e0acade0acbee0acace0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1203d20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1202f20e0ac86e0ad9fe0aca4e0aca8202844656e73697479203d204d617373202f20566f6c756d652920e0acace0ad8be0acb2e0acbf20e0acaae0ad8de0acb0e0ac95e0acbee0acb620e0ac95e0acb0e0acbee0acafe0acbee0ac8f2c20e0acafe0acbee0acb9e0acbee0acb020e0acb8e0ac99e0ad8de0ac95e0ad87e0aca420e0acb9e0ad87e0ac89e0ac9be0acbf20cf812028e0acb0e0ad8b2920e0ac95e0acbfe0acaee0ad8de0acace0acbe2064203d204d202f2056e0a5a420e0ac86e0aca8e0ad8de0aca4e0acb0e0ad8de0ac9ce0acbee0aca4e0ad80e0ad9f20e0acaee0acbee0aca8e0ac95202853492920e0acaae0aca6e0ad8de0aca7e0aca4e0acbfe0acb0e0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1e0acb020e0ac8fe0ac95e0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0acbfe0acb2e0ad8be0ac97e0ad8de0acb0e0acbee0acae20e0acaae0ad8de0acb0e0aca4e0acbf20e0ac98e0aca820e0acaee0acbfe0ac9fe0acb020286b672f6dc2b329e0a5a420e0acb8e0acbee0aca7e0acbee0acb0e0aca3e0aca4e0ac8320e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac85e0aca7e0acbfe0ac9520e0aca5e0acbee0ac8f2c20e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaee0aca7e0ad8de0ad9fe0acae20e0ac8fe0acace0ac8220e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac95e0acaee0ad8d20e0aca5e0acbee0ac8fe0a5a420e0ac89e0aca6e0acbee0acb9e0acb0e0aca320e0acb8e0ad8de0adb1e0acb0e0ad82e0acaa2c20e0acb2e0ad81e0acb9e0acbee0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0ac95e0acbee0aca020e0aca4e0ad81e0acb3e0aca8e0acbee0acb0e0ad8720e0acace0acb9e0ad81e0aca420e0ac85e0aca7e0acbfe0ac952c20e0ac95e0acbee0acb0e0aca320e0acb2e0ad81e0acb9e0acbee0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acaae0acb0e0acaee0acbee0aca3e0ad81e0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0ac85e0aca4e0acbf20e0aca8e0acbfe0acace0acbfe0aca1e0acbc20e0acade0acbee0acace0ad8720e0acb8e0ac9ce0ad8de0ac9ce0acbfe0aca420e0acb9e0ad8be0ac8720e0acb0e0acb9e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbfe0a5a420e0adaa20e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0acace0acbfe0acb6e0ad81e0aca6e0ad8de0aca720e0ac9ce0acb3e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaae0ad8de0acb0e0acbee0ad9f20e0ada7e0ada6e0ada6e0ada6206b672f6dc2b32028e0acace0acbe20e0ada720672f636dc2b32920e0acb9e0ad8be0ac87e0aca5e0acbee0ac8fe0a5a4a96369746174696f6e7391b36368756e6b5f636830315f63303030325f3031ac636861707465725f7265667391a56368303031aa636f6e666964656e6365cb3fe6666666666666aa70726f76656e616e6365aa65787472616374697665b362617369635f616e737765725f737461747573c0b36d6f64656c5f76616c69646174655f6a736f6ea5747261636594c801d70594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b063376462336262343063343034623731a46e6f6465af646f7562742e7472616e736c617465a57374616765af646f7562742e7472616e736c617465a4746f6f6cae7472616e736c6174655f74657874a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a866616c6c6261636baa6572726f725f636f6465ab554e415641494c41424c45ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727981a6726561736f6ed9a75452414e534c4154494f4e5f50524f56494445523d6d6f636b20e2809420736574205452414e534c4154494f4e5f50524f56494445523d68665f6c6f63616c2028616e642048465f544f4b454e20666f722074686520676174656420496e6469635472616e7332207265706f73292e20546865206f66666c696e65206c6561726e696e67207061746820646f6573206e6f742072657175697265207472616e736c6174696f6e2ea87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8013d0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b033363431333233373264663534306135a46e6f6465ae646f7562742e7265747269657665a57374616765ae646f7562742e7265747269657665a4746f6f6caf72657472696576655f6368756e6b73a870726f7669646572ac6c6f63616c5f687962726964af72756c657365745f76657273696f6ec0a86d6f64656c5f6964a46d6f636ba6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7346a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727982a66368756e6b7304aa636f6e666964656e6365cb3ff0000000000000a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8012a0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b064616638346166666363363834616665a46e6f6465ae646f7562742e67656e6572617465a57374616765ae646f7562742e67656e6572617465a4746f6f6caf67656e65726174655f616e73776572a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a66368756e6b7304ae6f75747075745f73756d6d61727982a36c656ecd0257a96369746174696f6e7301a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec801280594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b030356239616662616166366134613330a46e6f6465ae646f7562742e76616c6964617465a57374616765ae646f7562742e76616c6964617465a4746f6f6caf76616c69646174655f616e73776572a870726f7669646572c0af72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981aa616e737765725f6c656ecd0257ae6f75747075745f73756d6d61727981ac67617465735f70617373656405a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6eaa746f6f6c5f63616c6c7303aa737461727465645f6d73cf000001a13c9aea5eab6465636973696f6e5f6964b5646f7562745f7468726561645f746573745f303032a56572726f72c0ab72657472795f636f756e7400b276616c69646174696f6e5f726573756c747380ad66616c6c6261636b5f75736564c2b067656e65726174696f6e5f6572726f72c0b26272616e63683a746f3a76616c6964617465c0b06368616e6e656c5f76657273696f6e73de0014a95f5f73746172745f5f02a5717565727905ad6c6561726e65725f696e70757405b07472616e736c617465645f717565727905b5757365645f7472616e736c6174696f6e5f746f6f6c05a972657472696576616c05a6616e7377657205a5747261636505aa746f6f6c5f63616c6c7305aa737461727465645f6d7305ab6465636973696f6e5f696405a56572726f7205ab72657472795f636f756e7405b276616c69646174696f6e5f726573756c747305ad66616c6c6261636b5f7573656405b067656e65726174696f6e5f6572726f7205b36272616e63683a746f3a7472616e736c61746503b26272616e63683a746f3a726574726965766504b26272616e63683a746f3a67656e657261746505b26272616e63683a746f3a76616c696461746505ad76657273696f6e735f7365656e85a95f5f696e7075745f5f80a95f5f73746172745f5f81a95f5f73746172745f5f01a97472616e736c61746581b36272616e63683a746f3a7472616e736c61746502a8726574726965766581b26272616e63683a746f3a726574726965766503a867656e657261746581b26272616e63683a746f3a67656e657261746504b0757064617465645f6368616e6e656c73dc0010a6616e73776572b26272616e63683a746f3a76616c6964617465ab6465636973696f6e5f6964a56572726f72ad66616c6c6261636b5f75736564b067656e65726174696f6e5f6572726f72ad6c6561726e65725f696e707574a57175657279a972657472696576616cab72657472795f636f756e74aa737461727465645f6d73aa746f6f6c5f63616c6c73a57472616365b07472616e736c617465645f7175657279b5757365645f7472616e736c6174696f6e5f746f6f6cb276616c69646174696f6e5f726573756c7473	1792018148071
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	1f1c8217-6e69-69c3-8000-8aece5e5181a	msgpack	{"tags": [], "metadata": "ChainMap({'thread_id': 'doubt_thread_test_002'})", "callbacks": null, "recursion_limit": 10007, "configurable": {"checkpoint_ns": "", "thread_id": "doubt_thread_test_002", "__pregel_runtime": "Runtime(context=None, store=None, stream_writer=<function Pregel.astream.<locals>.stream_writer at 0x7fdfbba475e0>, heartbeat=<function _no_op_heartbeat at 0x7fdfbd582a30>, previous=None, execution_info=None, server_info=None, control=<langgraph.runtime.RunControl object at 0x7fdfbc5febc0>)", "checkpoint_id": "1f1c8217-6e69-69c3-8000-8aece5e5181a"}}	{"source": "loop", "step": 1, "parents": {}}	\\x87a17604a27473d920323032362d31302d31345432323a34393a30372e3935323236322b30303a3030a26964d92431663163383231372d366537302d363164642d383030312d643533623861646637343632ae6368616e6e656c5f76616c756573de0010a57175657279b7576861742069732070686f746f73796e7468657369733fad6c6561726e65725f696e707574b7576861742069732070686f746f73796e7468657369733fb07472616e736c617465645f7175657279c0b5757365645f7472616e736c6174696f6e5f746f6f6cc3a972657472696576616cc0a6616e73776572c0a5747261636594c801d70594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b063376462336262343063343034623731a46e6f6465af646f7562742e7472616e736c617465a57374616765af646f7562742e7472616e736c617465a4746f6f6cae7472616e736c6174655f74657874a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a866616c6c6261636baa6572726f725f636f6465ab554e415641494c41424c45ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727981a6726561736f6ed9a75452414e534c4154494f4e5f50524f56494445523d6d6f636b20e2809420736574205452414e534c4154494f4e5f50524f56494445523d68665f6c6f63616c2028616e642048465f544f4b454e20666f722074686520676174656420496e6469635472616e7332207265706f73292e20546865206f66666c696e65206c6561726e696e67207061746820646f6573206e6f742072657175697265207472616e736c6174696f6e2ea87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8013d0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b033363431333233373264663534306135a46e6f6465ae646f7562742e7265747269657665a57374616765ae646f7562742e7265747269657665a4746f6f6caf72657472696576655f6368756e6b73a870726f7669646572ac6c6f63616c5f687962726964af72756c657365745f76657273696f6ec0a86d6f64656c5f6964a46d6f636ba6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7346a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727982a66368756e6b7304aa636f6e666964656e6365cb3ff0000000000000a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8012a0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b064616638346166666363363834616665a46e6f6465ae646f7562742e67656e6572617465a57374616765ae646f7562742e67656e6572617465a4746f6f6caf67656e65726174655f616e73776572a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a66368756e6b7304ae6f75747075745f73756d6d61727982a36c656ecd0257a96369746174696f6e7301a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec801280594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b030356239616662616166366134613330a46e6f6465ae646f7562742e76616c6964617465a57374616765ae646f7562742e76616c6964617465a4746f6f6caf76616c69646174655f616e73776572a870726f7669646572c0af72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981aa616e737765725f6c656ecd0257ae6f75747075745f73756d6d61727981ac67617465735f70617373656405a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6eaa746f6f6c5f63616c6c7301aa737461727465645f6d73cf000001a13c9aea5eab6465636973696f6e5f6964b5646f7562745f7468726561645f746573745f303032a56572726f72c0ab72657472795f636f756e7400b276616c69646174696f6e5f726573756c747380ad66616c6c6261636b5f75736564c2b067656e65726174696f6e5f6572726f72c0b26272616e63683a746f3a7265747269657665c0b06368616e6e656c5f76657273696f6e73de0012a95f5f73746172745f5f02a5717565727903ad6c6561726e65725f696e70757403b07472616e736c617465645f717565727903b5757365645f7472616e736c6174696f6e5f746f6f6c03a972657472696576616c03a6616e7377657203a5747261636503aa746f6f6c5f63616c6c7303aa737461727465645f6d7303ab6465636973696f6e5f696403a56572726f7203ab72657472795f636f756e7403b276616c69646174696f6e5f726573756c747303ad66616c6c6261636b5f7573656403b067656e65726174696f6e5f6572726f7203b36272616e63683a746f3a7472616e736c61746503b26272616e63683a746f3a726574726965766503ad76657273696f6e735f7365656e83a95f5f696e7075745f5f80a95f5f73746172745f5f81a95f5f73746172745f5f01a97472616e736c61746581b36272616e63683a746f3a7472616e736c61746502b0757064617465645f6368616e6e656c73dc0010a6616e73776572b26272616e63683a746f3a7265747269657665ab6465636973696f6e5f6964a56572726f72ad66616c6c6261636b5f75736564b067656e65726174696f6e5f6572726f72ad6c6561726e65725f696e707574a57175657279a972657472696576616cab72657472795f636f756e74aa737461727465645f6d73aa746f6f6c5f63616c6c73a57472616365b07472616e736c617465645f7175657279b5757365645f7472616e736c6174696f6e5f746f6f6cb276616c69646174696f6e5f726573756c7473	1792018148060
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	1f1c8217-6e70-61dd-8001-d53b8adf7462	msgpack	{"tags": [], "metadata": "ChainMap({'thread_id': 'doubt_thread_test_002'})", "callbacks": null, "recursion_limit": 10007, "configurable": {"checkpoint_ns": "", "thread_id": "doubt_thread_test_002", "__pregel_runtime": "Runtime(context=None, store=None, stream_writer=<function Pregel.astream.<locals>.stream_writer at 0x7fdfbba475e0>, heartbeat=<function _no_op_heartbeat at 0x7fdfbd582a30>, previous=None, execution_info=None, server_info=None, control=<langgraph.runtime.RunControl object at 0x7fdfbc5febc0>)", "checkpoint_id": "1f1c8217-6e70-61dd-8001-d53b8adf7462"}}	{"source": "loop", "step": 2, "parents": {}}	\\x87a17604a27473d920323032362d31302d31345432323a34393a30382e3032363731332b30303a3030a26964d92431663163383231372d366632352d366562332d383030322d353937393334313330636431ae6368616e6e656c5f76616c756573de0010a57175657279b7576861742069732070686f746f73796e7468657369733fad6c6561726e65725f696e707574b7576861742069732070686f746f73796e7468657369733fb07472616e736c617465645f7175657279c0b5757365645f7472616e736c6174696f6e5f746f6f6cc3a972657472696576616cc81e0e0594b26170702e646f6d61696e2e736368656d6173af526574726965766564526573756c7484a66368756e6b739487a86368756e6b5f6964b36368756e6b5f636830315f63303030325f3031aa636f6e636570745f6964a56330303032aa636861707465725f6964a56368303031a7746578745f6f72da06c2e0ac98e0aca8e0aca4e0ad8de0adb1202864656e736974792920e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0ad8ce0aca3e0acb8e0acbf20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac8fe0ac95e0ac9520e0ac86e0ad9fe0aca4e0aca8e0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1e0acb020e0acaae0acb0e0acbfe0acaee0acbee0aca3e0a5a420e0ac8fe0acb9e0acbee0ac95e0ad8120e0ac97e0acbee0aca3e0acbfe0aca4e0acbfe0ac9520e0acade0acbee0acace0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1203d20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1202f20e0ac86e0ad9fe0aca4e0aca8202844656e73697479203d204d617373202f20566f6c756d652920e0acace0ad8be0acb2e0acbf20e0acaae0ad8de0acb0e0ac95e0acbee0acb620e0ac95e0acb0e0acbee0acafe0acbee0ac8f2c20e0acafe0acbee0acb9e0acbee0acb020e0acb8e0ac99e0ad8de0ac95e0ad87e0aca420e0acb9e0ad87e0ac89e0ac9be0acbf20cf812028e0acb0e0ad8b2920e0ac95e0acbfe0acaee0ad8de0acace0acbe2064203d204d202f2056e0a5a420e0ac86e0aca8e0ad8de0aca4e0acb0e0ad8de0ac9ce0acbee0aca4e0ad80e0ad9f20e0acaee0acbee0aca8e0ac95202853492920e0acaae0aca6e0ad8de0aca7e0aca4e0acbfe0acb0e0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1e0acb020e0ac8fe0ac95e0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0acbfe0acb2e0ad8be0ac97e0ad8de0acb0e0acbee0acae20e0acaae0ad8de0acb0e0aca4e0acbf20e0ac98e0aca820e0acaee0acbfe0ac9fe0acb020286b672f6dc2b329e0a5a420e0acb8e0acbee0aca7e0acbee0acb0e0aca3e0aca4e0ac8320e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac85e0aca7e0acbfe0ac9520e0aca5e0acbee0ac8f2c20e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaee0aca7e0ad8de0ad9fe0acae20e0ac8fe0acace0ac8220e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac95e0acaee0ad8d20e0aca5e0acbee0ac8fe0a5a420e0ac89e0aca6e0acbee0acb9e0acb0e0aca320e0acb8e0ad8de0adb1e0acb0e0ad82e0acaa2c20e0acb2e0ad81e0acb9e0acbee0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0ac95e0acbee0aca020e0aca4e0ad81e0acb3e0aca8e0acbee0acb0e0ad8720e0acace0acb9e0ad81e0aca420e0ac85e0aca7e0acbfe0ac952c20e0ac95e0acbee0acb0e0aca320e0acb2e0ad81e0acb9e0acbee0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acaae0acb0e0acaee0acbee0aca3e0ad81e0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0ac85e0aca4e0acbf20e0aca8e0acbfe0acace0acbfe0aca1e0acbc20e0acade0acbee0acace0ad8720e0acb8e0ac9ce0ad8de0ac9ce0acbfe0aca420e0acb9e0ad8be0ac8720e0acb0e0acb9e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbfe0a5a420e0adaa20e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0acace0acbfe0acb6e0ad81e0aca6e0ad8de0aca720e0ac9ce0acb3e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaae0ad8de0acb0e0acbee0ad9f20e0ada7e0ada6e0ada6e0ada6206b672f6dc2b32028e0acace0acbe20e0ada720672f636dc2b32920e0acb9e0ad8be0ac87e0aca5e0acbee0ac8fe0a5a420e0ac95e0ad8ce0aca3e0acb8e0acbf20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0aca4e0acbee0acb020e0ac85e0aca3e0ad81e0ac97e0ad81e0aca1e0acbce0acbfe0ac95e0acb020e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb120e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0ad8020e0aca6e0ad82e0acb0e0aca4e0acbe20e0ac89e0acaae0acb0e0ad8720e0aca8e0acbfe0acb0e0ad8de0acade0acb020e0ac95e0acb0e0acbfe0aca5e0acbee0ac8fe0a5a4aa736f757263655f726566aa6368303120c2a7312e33a573636f7265cb3ff0000000000000ad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030315f3032aa636f6e636570745f6964a56330303031aa636861707465725f6964a56368303031a7746578745f6f72da06f3e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0aca4e0acbfe0aca8e0ad8be0ac9fe0acbf20e0ac85e0acace0acb8e0ad8de0aca5e0acbee0acb020e0acade0acbfe0aca8e0ad8de0aca820e0acade0acbfe0aca8e0ad8de0aca820e0acade0ad8ce0aca4e0acbfe0ac9520e0aca7e0acb0e0ad8de0acae20e0acb0e0acb9e0acbfe0ac9be0acbfe0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020286669786564207368617065292c20e0acb8e0ad8de0acaae0acb7e0ad8de0ac9f20e0acb8e0ad80e0acaee0acbee0acb0e0ad87e0ac96e0acbe20e0ac8fe0acace0ac8220e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ad9fe0aca4e0aca82028666978656420766f6c756d652920e0aca5e0acbee0ac8fe0a5a420e0ac8fe0acb9e0acbe20e0acb8e0acb9e0ac9ce0acb0e0ad8720e0acb8e0ac99e0ad8de0ac95e0ad81e0ac9ae0acbfe0aca42028636f6d707265737369626c652920e0acb9e0ad8be0ac87e0acaae0acbee0acb0e0ad8720e0aca8e0acbee0acb9e0acbfe0ac81e0a5a420e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac95e0ad8ce0aca3e0acb8e0acbf20e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020e0aca8e0aca5e0acbee0ac8f2c20e0ac95e0acbfe0aca8e0ad8de0aca4e0ad8120e0ac8fe0acb9e0acbee0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ad9fe0aca4e0aca820e0aca5e0acbee0ac8fe0a5a420e0aca4e0acb0e0acb3e0ac95e0ad8120e0acafe0ad87e0ac89e0ac8120e0acaae0acbee0aca4e0ad8de0acb0e0acb0e0ad8720e0acb0e0ac96e0acbee0acafe0acbee0ac8f2c20e0aca4e0acbee0acb9e0acbe20e0acb8e0ad87e0acb9e0acbf20e0acaae0acbee0aca4e0ad8de0acb0e0acb020e0ac86e0ac95e0acbee0acb020e0aca7e0acbee0acb0e0aca320e0ac95e0acb0e0ad87e0a5a420e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac95e0ad8ce0aca3e0acb8e0acbf20e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac86e0ad9fe0aca4e0aca820e0aca8e0aca5e0acbee0ac8f3b20e0ac8fe0acb9e0acbe20e0ac89e0acaae0acb2e0acace0ad8de0aca720e0acb8e0acaee0acb8e0ad8de0aca420e0acb8e0ad8de0aca5e0acbee0aca8e0ac95e0ad8120e0acaae0ad82e0acb0e0ad8de0aca3e0ad8de0aca320e0ac95e0acb0e0acbfe0aca6e0acbfe0ac8fe0a5a420e0ac97e0ad8de0ad9fe0acbee0acb8e0acb020e0acb8e0ac99e0ad8de0ac95e0ad8be0ac9ae0aca8e0acb6e0ad80e0acb3e0aca4e0acbe2028636f6d70726573736962696c6974792920e0acb8e0acb0e0ad8de0acace0acbee0aca7e0acbfe0ac9520e0acb9e0ad8be0ac87e0aca5e0acbfe0acace0acbee0acb0e0ad8120e0ac8fe0acb9e0acbee0ac95e0ad8120e0ac89e0ac9ae0ad8de0ac9a20e0ac9ae0acbee0acaae0acb0e0ad8720e0acb8e0acbfe0acb2e0acbfe0aca3e0ad8de0aca1e0acb020e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0acade0acb0e0ad8de0aca4e0ad8de0aca4e0acbf20e0ac95e0acb0e0acbee0acafe0acbee0ac87e0acaae0acbee0acb0e0ad872c20e0acafe0ad87e0acaae0acb0e0acbfe0ac95e0acbf20e0ac86e0acae20e0ac98e0acb0e0ad8720e0acace0ad8de0ad9fe0acace0acb9e0ad83e0aca420e0acb9e0ad87e0ac89e0aca5e0acbfe0acace0acbe20e0ac8fe0acb2e0acaae0acbfe0ac9ce0acbf20284c50472920e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac85e0ac95e0ad8de0acb8e0acbfe0ac9ce0ad87e0aca820e0acb8e0acbfe0acb2e0acbfe0aca3e0ad8de0aca1e0acb0e0a5a420e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0ac97e0aca4e0acbfe0ac9c20e0acb6e0ac95e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0ac86e0aca8e0ad8de0aca4e0ac83e0ac95e0aca3e0acbfe0ac95e0acbe20e0acb8e0ad8de0aca5e0acbee0aca820e0acb9e0acbfe0ac8120e0ac8fe0acb9e0acbf20e0acb8e0acaee0acb8e0ad8de0aca420e0acaae0acbee0acb0e0ad8de0aca5e0ac95e0ad8de0ad9fe0acb020e0acaee0ad82e0acb320e0ac95e0acbee0acb0e0aca320e0ac85e0ac9fe0ad87e0a5a4aa736f757263655f726566aa6368303120c2a7312e32a573636f7265cb3fdd17fa84aa97caad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030335f3031aa636f6e636570745f6964a56330303033aa636861707465725f6964a56368303031a7746578745f6f72da06e2e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbe20e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac9ae0acbee0acaae0acb020e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0ac98e0ac9fe0acbee0ac8720e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac85e0acace0acb8e0ad8de0aca5e0acbe20e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0ac95e0acb0e0acbee0acafe0acbee0ac87e0acaae0acbee0acb0e0ad87e0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0ac95e0ad8120e0ac97e0acb0e0acae20e0ac95e0acb2e0ad8720e0aca4e0acbee0acb020e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0ac97e0aca4e0acbfe0ac9c20e0acb6e0ac95e0ad8de0aca4e0acbf20e0acace0aca2e0acbce0acbfe0acafe0acbee0ac8f20e0ac8fe0acace0ac8220e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0ac8fe0acb9e0acbe20e0aca4e0acb0e0acb3e0acbfe0acace0acbee0ac95e0ad8120e0acb2e0acbee0ac97e0ad87e0a5a420e0acafe0ad87e0ac89e0ac8120e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0acace0acbee0ad9fe0ad81e0acaee0aca3e0ad8de0aca1e0acb3e0ad80e0ad9f20e0ac9ae0acbee0acaae0acb0e0ad8720e0ac8fe0ac9520e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0aca4e0acb0e0acb3e0acb0e0ad8720e0acaae0acb0e0acbfe0aca3e0aca420e0acb9e0ad81e0ac8f2c20e0aca4e0acbee0acb9e0acbee0ac95e0ad8120e0aca4e0acbee0acb020e0ac97e0acb3e0aca8e0acbee0ac99e0ad8de0ac9520286d656c74696e6720706f696e742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a420e0acace0acb0e0acabe0acb020e0ac97e0acb3e0aca8e0acbee0ac99e0ad8de0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ada620e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0acace0acbe20e0ada8e0adade0ada920e0ac95e0ad87e0acb2e0acade0acbfe0aca8e0a5a420e0acb8e0ad87e0acb9e0acbfe0acaae0acb0e0acbf20e0acafe0ad87e0ac89e0ac8120e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acabe0ad81e0ac9fe0acbf20e0acace0acbee0acb7e0ad8de0acaae0acb0e0ad8720e0acaae0acb0e0acbfe0aca3e0aca420e0acb9e0ad81e0ac8f2c20e0aca4e0acbee0acb9e0acbee0ac95e0ad8120e0acb8e0ad8de0acabe0ad81e0ac9fe0aca8e0acbee0ac99e0ad8de0ac952028626f696c696e6720706f696e742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a420e0ac9ce0acb3e0acb020e0acb8e0ad8de0acabe0ad81e0ac9fe0aca8e0acbee0ac99e0ad8de0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ada7e0ada6e0ada620e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0acace0acbe20e0ada9e0adade0ada920e0ac95e0ad87e0acb2e0acade0acbfe0aca8e0a5a420e0ac85e0acace0acb8e0ad8de0aca5e0acbe20e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0acb8e0acaee0ad9fe0acb0e0ad8720e0acafe0ad8be0ac9720e0ac95e0acb0e0acbee0acafe0acbee0ac89e0aca5e0acbfe0acace0acbe20e0aca4e0acbee0acaa20e0acb6e0ac95e0ad8de0aca4e0acbf20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbe20e0aca820e0acace0aca2e0acbce0acbee0ac8720e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb3e0ac95e0ad8120e0acade0acbee0ac99e0ad8de0ac97e0acbfe0acace0acbee0acb0e0ad8720e0acace0ad8de0ad9fe0acace0acb9e0ad83e0aca420e0acb9e0ad81e0ac8f2c20e0acafe0acbee0acb9e0acbee0ac95e0ad8120e0ac97e0ad81e0acaae0ad8de0aca4e0aca4e0acbee0acaa20286c6174656e7420686561742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a4aa736f757263655f726566aa6368303120c2a7312e34a573636f7265cb3fdd17fa84aa97caad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030315f3031aa636f6e636570745f6964a56330303031aa636861707465725f6964a56368303031a7746578745f6f72da0702e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac86e0acae20e0acaae0acb0e0acbfe0acace0ad87e0acb6e0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acaae0ad8de0acb0e0aca4e0ad8de0ad9fe0ad87e0ac9520e0acace0acb8e0ad8de0aca4e0ad8120e0acafe0acbee0acb9e0acbee0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb120286d6173732920e0aca5e0acbee0ac8f20e0ac8fe0acace0ac8220e0acafe0acbee0acb9e0acbe20e0ac95e0acbfe0ac9be0acbf20e0acb8e0ad8de0aca5e0acbee0aca820e0acace0acbe20e0ac86e0ad9fe0aca4e0aca82028766f6c756d652920e0ac85e0aca7e0acbfe0ac95e0acbee0acb020e0ac95e0acb0e0ad87e0a5a420e0acaae0ad8de0acb0e0ac95e0ad83e0aca4e0acbfe0acb0e0ad8720e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acaee0ad81e0ac96e0ad8de0ad9fe0aca4e0ac8320e0aca4e0acbfe0aca8e0ad8be0ac9fe0acbf20e0acade0ad8ce0aca4e0acbfe0ac9520e0acb8e0ad8de0aca5e0acbfe0aca4e0acbfe0acb0e0ad8720e0aca6e0ad87e0ac96e0acbee0acafe0acbee0ac8f3a20e0ac95e0aca0e0acbfe0aca82028736f6c6964292c20e0aca4e0acb0e0acb320286c69717569642920e0ac8fe0acace0ac8220e0ac97e0ad8de0ad9fe0acbee0acb8202867617329e0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0ac85e0aca4e0ad8de0ad9fe0aca8e0ad8de0aca420e0aca8e0acbfe0acace0acbfe0aca1e0acbc20e0acade0acbee0acace0acb0e0ad8720e0acb8e0ac9ce0ad8de0ac9ce0acbfe0aca420e0acb9e0ad8be0ac8720e0acb0e0acb9e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0ac86e0aca8e0ad8de0aca4e0ac83e0ac95e0aca3e0acbfe0ac95e0acbe20e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb32028696e7465726d6f6c6563756c617220666f7263652920e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac85e0aca7e0acbfe0ac9520e0acaae0ad8de0acb0e0acace0acb320e0aca5e0acbee0ac8fe0a5a420e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0ac95e0acbfe0ac9be0acbf20e0acabe0acbee0ac99e0ad8de0ac95e0acbe20e0acb8e0ad8de0aca5e0acbee0aca820e0aca5e0acbee0ac8f20e0ac8fe0acace0ac8220e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb320e0ac95e0aca0e0acbfe0aca820e0aca4e0ad81e0acb3e0aca8e0acbee0acb0e0ad8720e0ac95e0acaee0ad8d20e0aca5e0acbee0ac8f2c20e0acafe0acbee0acb9e0acbe20e0acabe0acb3e0acb0e0ad8720e0acb8e0ad87e0acaee0acbee0aca8e0ad8720e0acaae0ad8de0acb0e0acace0acbee0acb9e0acbfe0aca420e0acb9e0ad8be0ac87e0acaae0acbee0acb0e0aca8e0ad8de0aca4e0acbfe0a5a420e0ac85e0aca8e0ad8de0ad9fe0acaae0ac95e0ad8de0acb7e0acb0e0ad872c20e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0acaae0acb0e0acb8e0ad8de0acaae0acb0e0aca0e0acbee0acb0e0ad8120e0acace0acb9e0ad81e0aca420e0aca6e0ad82e0acb0e0acb0e0ad8720e0aca5e0acbee0ac86e0aca8e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb320e0aca8e0ac97e0aca3e0ad8de0ad9f20e0aca5e0acbee0ac8fe0a5a420e0aca4e0ad87e0aca3e0ad8120e0ac97e0ad8de0ad9fe0acbee0acb8e0acb020e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0acb8e0acaee0acb8e0ad8de0aca420e0aca6e0acbfe0ac97e0acb0e0ad8720e0aca6e0ad8de0acb0e0ad81e0aca420e0ac9320e0acaee0ad81e0ac95e0ad8de0aca420e0acade0acbee0acace0acb0e0ad8720e0ac97e0aca4e0acbf20e0ac95e0acb0e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbfe0a5a4aa736f757263655f726566aa6368303120c2a7312e32a573636f7265cb0000000000000000ad6d6174636865645f7465726d7390a870726f7669646572ac6c6f63616c5f687962726964a86d6f64656c5f6964a46d6f636baa636f6e666964656e6365cb3ff0000000000000b36d6f64656c5f76616c69646174655f6a736f6ea6616e73776572c0a5747261636594c801d70594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b063376462336262343063343034623731a46e6f6465af646f7562742e7472616e736c617465a57374616765af646f7562742e7472616e736c617465a4746f6f6cae7472616e736c6174655f74657874a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a866616c6c6261636baa6572726f725f636f6465ab554e415641494c41424c45ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727981a6726561736f6ed9a75452414e534c4154494f4e5f50524f56494445523d6d6f636b20e2809420736574205452414e534c4154494f4e5f50524f56494445523d68665f6c6f63616c2028616e642048465f544f4b454e20666f722074686520676174656420496e6469635472616e7332207265706f73292e20546865206f66666c696e65206c6561726e696e67207061746820646f6573206e6f742072657175697265207472616e736c6174696f6e2ea87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8013d0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b033363431333233373264663534306135a46e6f6465ae646f7562742e7265747269657665a57374616765ae646f7562742e7265747269657665a4746f6f6caf72657472696576655f6368756e6b73a870726f7669646572ac6c6f63616c5f687962726964af72756c657365745f76657273696f6ec0a86d6f64656c5f6964a46d6f636ba6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7346a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727982a66368756e6b7304aa636f6e666964656e6365cb3ff0000000000000a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8012a0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b064616638346166666363363834616665a46e6f6465ae646f7562742e67656e6572617465a57374616765ae646f7562742e67656e6572617465a4746f6f6caf67656e65726174655f616e73776572a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a66368756e6b7304ae6f75747075745f73756d6d61727982a36c656ecd0257a96369746174696f6e7301a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec801280594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b030356239616662616166366134613330a46e6f6465ae646f7562742e76616c6964617465a57374616765ae646f7562742e76616c6964617465a4746f6f6caf76616c69646174655f616e73776572a870726f7669646572c0af72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981aa616e737765725f6c656ecd0257ae6f75747075745f73756d6d61727981ac67617465735f70617373656405a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6eaa746f6f6c5f63616c6c7302aa737461727465645f6d73cf000001a13c9aea5eab6465636973696f6e5f6964b5646f7562745f7468726561645f746573745f303032a56572726f72c0ab72657472795f636f756e7400b276616c69646174696f6e5f726573756c747380ad66616c6c6261636b5f75736564c2b067656e65726174696f6e5f6572726f72c0b26272616e63683a746f3a67656e6572617465c0b06368616e6e656c5f76657273696f6e73de0013a95f5f73746172745f5f02a5717565727904ad6c6561726e65725f696e70757404b07472616e736c617465645f717565727904b5757365645f7472616e736c6174696f6e5f746f6f6c04a972657472696576616c04a6616e7377657204a5747261636504aa746f6f6c5f63616c6c7304aa737461727465645f6d7304ab6465636973696f6e5f696404a56572726f7204ab72657472795f636f756e7404b276616c69646174696f6e5f726573756c747304ad66616c6c6261636b5f7573656404b067656e65726174696f6e5f6572726f7204b36272616e63683a746f3a7472616e736c61746503b26272616e63683a746f3a726574726965766504b26272616e63683a746f3a67656e657261746504ad76657273696f6e735f7365656e84a95f5f696e7075745f5f80a95f5f73746172745f5f81a95f5f73746172745f5f01a97472616e736c61746581b36272616e63683a746f3a7472616e736c61746502a8726574726965766581b26272616e63683a746f3a726574726965766503b0757064617465645f6368616e6e656c73dc0010a6616e73776572b26272616e63683a746f3a67656e6572617465ab6465636973696f6e5f6964a56572726f72ad66616c6c6261636b5f75736564b067656e65726174696f6e5f6572726f72ad6c6561726e65725f696e707574a57175657279a972657472696576616cab72657472795f636f756e74aa737461727465645f6d73aa746f6f6c5f63616c6c73a57472616365b07472616e736c617465645f7175657279b5757365645f7472616e736c6174696f6e5f746f6f6cb276616c69646174696f6e5f726573756c7473	1792018148066
doubt_thread_test_002		1f1c8217-6f46-6201-8004-cd7c2f9ff82a	1f1c8217-6f31-673c-8003-5d4532aaf205	msgpack	{"tags": [], "metadata": "ChainMap({'thread_id': 'doubt_thread_test_002'})", "callbacks": null, "recursion_limit": 10007, "configurable": {"checkpoint_ns": "", "thread_id": "doubt_thread_test_002", "__pregel_runtime": "Runtime(context=None, store=None, stream_writer=<function Pregel.astream.<locals>.stream_writer at 0x7fdfbba475e0>, heartbeat=<function _no_op_heartbeat at 0x7fdfbd582a30>, previous=None, execution_info=None, server_info=None, control=<langgraph.runtime.RunControl object at 0x7fdfbc5febc0>)", "checkpoint_id": "1f1c8217-6f31-673c-8003-5d4532aaf205"}}	{"source": "loop", "step": 4, "parents": {}}	\\x87a17604a27473d920323032362d31302d31345432323a34393a30382e3033393930332b30303a3030a26964d92431663163383231372d366634362d363230312d383030342d636437633266396666383261ae6368616e6e656c5f76616c7565738fa57175657279b7576861742069732070686f746f73796e7468657369733fad6c6561726e65725f696e707574b7576861742069732070686f746f73796e7468657369733fb07472616e736c617465645f7175657279c0b5757365645f7472616e736c6174696f6e5f746f6f6cc3a972657472696576616cc81e0e0594b26170702e646f6d61696e2e736368656d6173af526574726965766564526573756c7484a66368756e6b739487a86368756e6b5f6964b36368756e6b5f636830315f63303030325f3031aa636f6e636570745f6964a56330303032aa636861707465725f6964a56368303031a7746578745f6f72da06c2e0ac98e0aca8e0aca4e0ad8de0adb1202864656e736974792920e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0ad8ce0aca3e0acb8e0acbf20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac8fe0ac95e0ac9520e0ac86e0ad9fe0aca4e0aca8e0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1e0acb020e0acaae0acb0e0acbfe0acaee0acbee0aca3e0a5a420e0ac8fe0acb9e0acbee0ac95e0ad8120e0ac97e0acbee0aca3e0acbfe0aca4e0acbfe0ac9520e0acade0acbee0acace0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1203d20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1202f20e0ac86e0ad9fe0aca4e0aca8202844656e73697479203d204d617373202f20566f6c756d652920e0acace0ad8be0acb2e0acbf20e0acaae0ad8de0acb0e0ac95e0acbee0acb620e0ac95e0acb0e0acbee0acafe0acbee0ac8f2c20e0acafe0acbee0acb9e0acbee0acb020e0acb8e0ac99e0ad8de0ac95e0ad87e0aca420e0acb9e0ad87e0ac89e0ac9be0acbf20cf812028e0acb0e0ad8b2920e0ac95e0acbfe0acaee0ad8de0acace0acbe2064203d204d202f2056e0a5a420e0ac86e0aca8e0ad8de0aca4e0acb0e0ad8de0ac9ce0acbee0aca4e0ad80e0ad9f20e0acaee0acbee0aca8e0ac95202853492920e0acaae0aca6e0ad8de0aca7e0aca4e0acbfe0acb0e0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1e0acb020e0ac8fe0ac95e0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0acbfe0acb2e0ad8be0ac97e0ad8de0acb0e0acbee0acae20e0acaae0ad8de0acb0e0aca4e0acbf20e0ac98e0aca820e0acaee0acbfe0ac9fe0acb020286b672f6dc2b329e0a5a420e0acb8e0acbee0aca7e0acbee0acb0e0aca3e0aca4e0ac8320e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac85e0aca7e0acbfe0ac9520e0aca5e0acbee0ac8f2c20e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaee0aca7e0ad8de0ad9fe0acae20e0ac8fe0acace0ac8220e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac95e0acaee0ad8d20e0aca5e0acbee0ac8fe0a5a420e0ac89e0aca6e0acbee0acb9e0acb0e0aca320e0acb8e0ad8de0adb1e0acb0e0ad82e0acaa2c20e0acb2e0ad81e0acb9e0acbee0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0ac95e0acbee0aca020e0aca4e0ad81e0acb3e0aca8e0acbee0acb0e0ad8720e0acace0acb9e0ad81e0aca420e0ac85e0aca7e0acbfe0ac952c20e0ac95e0acbee0acb0e0aca320e0acb2e0ad81e0acb9e0acbee0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acaae0acb0e0acaee0acbee0aca3e0ad81e0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0ac85e0aca4e0acbf20e0aca8e0acbfe0acace0acbfe0aca1e0acbc20e0acade0acbee0acace0ad8720e0acb8e0ac9ce0ad8de0ac9ce0acbfe0aca420e0acb9e0ad8be0ac8720e0acb0e0acb9e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbfe0a5a420e0adaa20e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0acace0acbfe0acb6e0ad81e0aca6e0ad8de0aca720e0ac9ce0acb3e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaae0ad8de0acb0e0acbee0ad9f20e0ada7e0ada6e0ada6e0ada6206b672f6dc2b32028e0acace0acbe20e0ada720672f636dc2b32920e0acb9e0ad8be0ac87e0aca5e0acbee0ac8fe0a5a420e0ac95e0ad8ce0aca3e0acb8e0acbf20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0aca4e0acbee0acb020e0ac85e0aca3e0ad81e0ac97e0ad81e0aca1e0acbce0acbfe0ac95e0acb020e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb120e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0ad8020e0aca6e0ad82e0acb0e0aca4e0acbe20e0ac89e0acaae0acb0e0ad8720e0aca8e0acbfe0acb0e0ad8de0acade0acb020e0ac95e0acb0e0acbfe0aca5e0acbee0ac8fe0a5a4aa736f757263655f726566aa6368303120c2a7312e33a573636f7265cb3ff0000000000000ad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030315f3032aa636f6e636570745f6964a56330303031aa636861707465725f6964a56368303031a7746578745f6f72da06f3e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0aca4e0acbfe0aca8e0ad8be0ac9fe0acbf20e0ac85e0acace0acb8e0ad8de0aca5e0acbee0acb020e0acade0acbfe0aca8e0ad8de0aca820e0acade0acbfe0aca8e0ad8de0aca820e0acade0ad8ce0aca4e0acbfe0ac9520e0aca7e0acb0e0ad8de0acae20e0acb0e0acb9e0acbfe0ac9be0acbfe0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020286669786564207368617065292c20e0acb8e0ad8de0acaae0acb7e0ad8de0ac9f20e0acb8e0ad80e0acaee0acbee0acb0e0ad87e0ac96e0acbe20e0ac8fe0acace0ac8220e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ad9fe0aca4e0aca82028666978656420766f6c756d652920e0aca5e0acbee0ac8fe0a5a420e0ac8fe0acb9e0acbe20e0acb8e0acb9e0ac9ce0acb0e0ad8720e0acb8e0ac99e0ad8de0ac95e0ad81e0ac9ae0acbfe0aca42028636f6d707265737369626c652920e0acb9e0ad8be0ac87e0acaae0acbee0acb0e0ad8720e0aca8e0acbee0acb9e0acbfe0ac81e0a5a420e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac95e0ad8ce0aca3e0acb8e0acbf20e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020e0aca8e0aca5e0acbee0ac8f2c20e0ac95e0acbfe0aca8e0ad8de0aca4e0ad8120e0ac8fe0acb9e0acbee0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ad9fe0aca4e0aca820e0aca5e0acbee0ac8fe0a5a420e0aca4e0acb0e0acb3e0ac95e0ad8120e0acafe0ad87e0ac89e0ac8120e0acaae0acbee0aca4e0ad8de0acb0e0acb0e0ad8720e0acb0e0ac96e0acbee0acafe0acbee0ac8f2c20e0aca4e0acbee0acb9e0acbe20e0acb8e0ad87e0acb9e0acbf20e0acaae0acbee0aca4e0ad8de0acb0e0acb020e0ac86e0ac95e0acbee0acb020e0aca7e0acbee0acb0e0aca320e0ac95e0acb0e0ad87e0a5a420e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac95e0ad8ce0aca3e0acb8e0acbf20e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac86e0ad9fe0aca4e0aca820e0aca8e0aca5e0acbee0ac8f3b20e0ac8fe0acb9e0acbe20e0ac89e0acaae0acb2e0acace0ad8de0aca720e0acb8e0acaee0acb8e0ad8de0aca420e0acb8e0ad8de0aca5e0acbee0aca8e0ac95e0ad8120e0acaae0ad82e0acb0e0ad8de0aca3e0ad8de0aca320e0ac95e0acb0e0acbfe0aca6e0acbfe0ac8fe0a5a420e0ac97e0ad8de0ad9fe0acbee0acb8e0acb020e0acb8e0ac99e0ad8de0ac95e0ad8be0ac9ae0aca8e0acb6e0ad80e0acb3e0aca4e0acbe2028636f6d70726573736962696c6974792920e0acb8e0acb0e0ad8de0acace0acbee0aca7e0acbfe0ac9520e0acb9e0ad8be0ac87e0aca5e0acbfe0acace0acbee0acb0e0ad8120e0ac8fe0acb9e0acbee0ac95e0ad8120e0ac89e0ac9ae0ad8de0ac9a20e0ac9ae0acbee0acaae0acb0e0ad8720e0acb8e0acbfe0acb2e0acbfe0aca3e0ad8de0aca1e0acb020e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0acade0acb0e0ad8de0aca4e0ad8de0aca4e0acbf20e0ac95e0acb0e0acbee0acafe0acbee0ac87e0acaae0acbee0acb0e0ad872c20e0acafe0ad87e0acaae0acb0e0acbfe0ac95e0acbf20e0ac86e0acae20e0ac98e0acb0e0ad8720e0acace0ad8de0ad9fe0acace0acb9e0ad83e0aca420e0acb9e0ad87e0ac89e0aca5e0acbfe0acace0acbe20e0ac8fe0acb2e0acaae0acbfe0ac9ce0acbf20284c50472920e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac85e0ac95e0ad8de0acb8e0acbfe0ac9ce0ad87e0aca820e0acb8e0acbfe0acb2e0acbfe0aca3e0ad8de0aca1e0acb0e0a5a420e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0ac97e0aca4e0acbfe0ac9c20e0acb6e0ac95e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0ac86e0aca8e0ad8de0aca4e0ac83e0ac95e0aca3e0acbfe0ac95e0acbe20e0acb8e0ad8de0aca5e0acbee0aca820e0acb9e0acbfe0ac8120e0ac8fe0acb9e0acbf20e0acb8e0acaee0acb8e0ad8de0aca420e0acaae0acbee0acb0e0ad8de0aca5e0ac95e0ad8de0ad9fe0acb020e0acaee0ad82e0acb320e0ac95e0acbee0acb0e0aca320e0ac85e0ac9fe0ad87e0a5a4aa736f757263655f726566aa6368303120c2a7312e32a573636f7265cb3fdd17fa84aa97caad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030335f3031aa636f6e636570745f6964a56330303033aa636861707465725f6964a56368303031a7746578745f6f72da06e2e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbe20e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac9ae0acbee0acaae0acb020e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0ac98e0ac9fe0acbee0ac8720e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac85e0acace0acb8e0ad8de0aca5e0acbe20e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0ac95e0acb0e0acbee0acafe0acbee0ac87e0acaae0acbee0acb0e0ad87e0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0ac95e0ad8120e0ac97e0acb0e0acae20e0ac95e0acb2e0ad8720e0aca4e0acbee0acb020e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0ac97e0aca4e0acbfe0ac9c20e0acb6e0ac95e0ad8de0aca4e0acbf20e0acace0aca2e0acbce0acbfe0acafe0acbee0ac8f20e0ac8fe0acace0ac8220e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0ac8fe0acb9e0acbe20e0aca4e0acb0e0acb3e0acbfe0acace0acbee0ac95e0ad8120e0acb2e0acbee0ac97e0ad87e0a5a420e0acafe0ad87e0ac89e0ac8120e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0acace0acbee0ad9fe0ad81e0acaee0aca3e0ad8de0aca1e0acb3e0ad80e0ad9f20e0ac9ae0acbee0acaae0acb0e0ad8720e0ac8fe0ac9520e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0aca4e0acb0e0acb3e0acb0e0ad8720e0acaae0acb0e0acbfe0aca3e0aca420e0acb9e0ad81e0ac8f2c20e0aca4e0acbee0acb9e0acbee0ac95e0ad8120e0aca4e0acbee0acb020e0ac97e0acb3e0aca8e0acbee0ac99e0ad8de0ac9520286d656c74696e6720706f696e742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a420e0acace0acb0e0acabe0acb020e0ac97e0acb3e0aca8e0acbee0ac99e0ad8de0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ada620e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0acace0acbe20e0ada8e0adade0ada920e0ac95e0ad87e0acb2e0acade0acbfe0aca8e0a5a420e0acb8e0ad87e0acb9e0acbfe0acaae0acb0e0acbf20e0acafe0ad87e0ac89e0ac8120e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acabe0ad81e0ac9fe0acbf20e0acace0acbee0acb7e0ad8de0acaae0acb0e0ad8720e0acaae0acb0e0acbfe0aca3e0aca420e0acb9e0ad81e0ac8f2c20e0aca4e0acbee0acb9e0acbee0ac95e0ad8120e0acb8e0ad8de0acabe0ad81e0ac9fe0aca8e0acbee0ac99e0ad8de0ac952028626f696c696e6720706f696e742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a420e0ac9ce0acb3e0acb020e0acb8e0ad8de0acabe0ad81e0ac9fe0aca8e0acbee0ac99e0ad8de0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ada7e0ada6e0ada620e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0acace0acbe20e0ada9e0adade0ada920e0ac95e0ad87e0acb2e0acade0acbfe0aca8e0a5a420e0ac85e0acace0acb8e0ad8de0aca5e0acbe20e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0acb8e0acaee0ad9fe0acb0e0ad8720e0acafe0ad8be0ac9720e0ac95e0acb0e0acbee0acafe0acbee0ac89e0aca5e0acbfe0acace0acbe20e0aca4e0acbee0acaa20e0acb6e0ac95e0ad8de0aca4e0acbf20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbe20e0aca820e0acace0aca2e0acbce0acbee0ac8720e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb3e0ac95e0ad8120e0acade0acbee0ac99e0ad8de0ac97e0acbfe0acace0acbee0acb0e0ad8720e0acace0ad8de0ad9fe0acace0acb9e0ad83e0aca420e0acb9e0ad81e0ac8f2c20e0acafe0acbee0acb9e0acbee0ac95e0ad8120e0ac97e0ad81e0acaae0ad8de0aca4e0aca4e0acbee0acaa20286c6174656e7420686561742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a4aa736f757263655f726566aa6368303120c2a7312e34a573636f7265cb3fdd17fa84aa97caad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030315f3031aa636f6e636570745f6964a56330303031aa636861707465725f6964a56368303031a7746578745f6f72da0702e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac86e0acae20e0acaae0acb0e0acbfe0acace0ad87e0acb6e0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acaae0ad8de0acb0e0aca4e0ad8de0ad9fe0ad87e0ac9520e0acace0acb8e0ad8de0aca4e0ad8120e0acafe0acbee0acb9e0acbee0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb120286d6173732920e0aca5e0acbee0ac8f20e0ac8fe0acace0ac8220e0acafe0acbee0acb9e0acbe20e0ac95e0acbfe0ac9be0acbf20e0acb8e0ad8de0aca5e0acbee0aca820e0acace0acbe20e0ac86e0ad9fe0aca4e0aca82028766f6c756d652920e0ac85e0aca7e0acbfe0ac95e0acbee0acb020e0ac95e0acb0e0ad87e0a5a420e0acaae0ad8de0acb0e0ac95e0ad83e0aca4e0acbfe0acb0e0ad8720e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acaee0ad81e0ac96e0ad8de0ad9fe0aca4e0ac8320e0aca4e0acbfe0aca8e0ad8be0ac9fe0acbf20e0acade0ad8ce0aca4e0acbfe0ac9520e0acb8e0ad8de0aca5e0acbfe0aca4e0acbfe0acb0e0ad8720e0aca6e0ad87e0ac96e0acbee0acafe0acbee0ac8f3a20e0ac95e0aca0e0acbfe0aca82028736f6c6964292c20e0aca4e0acb0e0acb320286c69717569642920e0ac8fe0acace0ac8220e0ac97e0ad8de0ad9fe0acbee0acb8202867617329e0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0ac85e0aca4e0ad8de0ad9fe0aca8e0ad8de0aca420e0aca8e0acbfe0acace0acbfe0aca1e0acbc20e0acade0acbee0acace0acb0e0ad8720e0acb8e0ac9ce0ad8de0ac9ce0acbfe0aca420e0acb9e0ad8be0ac8720e0acb0e0acb9e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0ac86e0aca8e0ad8de0aca4e0ac83e0ac95e0aca3e0acbfe0ac95e0acbe20e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb32028696e7465726d6f6c6563756c617220666f7263652920e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac85e0aca7e0acbfe0ac9520e0acaae0ad8de0acb0e0acace0acb320e0aca5e0acbee0ac8fe0a5a420e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0ac95e0acbfe0ac9be0acbf20e0acabe0acbee0ac99e0ad8de0ac95e0acbe20e0acb8e0ad8de0aca5e0acbee0aca820e0aca5e0acbee0ac8f20e0ac8fe0acace0ac8220e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb320e0ac95e0aca0e0acbfe0aca820e0aca4e0ad81e0acb3e0aca8e0acbee0acb0e0ad8720e0ac95e0acaee0ad8d20e0aca5e0acbee0ac8f2c20e0acafe0acbee0acb9e0acbe20e0acabe0acb3e0acb0e0ad8720e0acb8e0ad87e0acaee0acbee0aca8e0ad8720e0acaae0ad8de0acb0e0acace0acbee0acb9e0acbfe0aca420e0acb9e0ad8be0ac87e0acaae0acbee0acb0e0aca8e0ad8de0aca4e0acbfe0a5a420e0ac85e0aca8e0ad8de0ad9fe0acaae0ac95e0ad8de0acb7e0acb0e0ad872c20e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0acaae0acb0e0acb8e0ad8de0acaae0acb0e0aca0e0acbee0acb0e0ad8120e0acace0acb9e0ad81e0aca420e0aca6e0ad82e0acb0e0acb0e0ad8720e0aca5e0acbee0ac86e0aca8e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb320e0aca8e0ac97e0aca3e0ad8de0ad9f20e0aca5e0acbee0ac8fe0a5a420e0aca4e0ad87e0aca3e0ad8120e0ac97e0ad8de0ad9fe0acbee0acb8e0acb020e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0acb8e0acaee0acb8e0ad8de0aca420e0aca6e0acbfe0ac97e0acb0e0ad8720e0aca6e0ad8de0acb0e0ad81e0aca420e0ac9320e0acaee0ad81e0ac95e0ad8de0aca420e0acade0acbee0acace0acb0e0ad8720e0ac97e0aca4e0acbf20e0ac95e0acb0e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbfe0a5a4aa736f757263655f726566aa6368303120c2a7312e32a573636f7265cb0000000000000000ad6d6174636865645f7465726d7390a870726f7669646572ac6c6f63616c5f687962726964a86d6f64656c5f6964a46d6f636baa636f6e666964656e6365cb3ff0000000000000b36d6f64656c5f76616c69646174655f6a736f6ea6616e73776572c806750594b26170702e646f6d61696e2e736368656d6173af47656e657261746564416e7377657286a7746578745f6f72da05bfe0ac98e0aca8e0aca4e0ad8de0adb1202864656e736974792920e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0ad8ce0aca3e0acb8e0acbf20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac8fe0ac95e0ac9520e0ac86e0ad9fe0aca4e0aca8e0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1e0acb020e0acaae0acb0e0acbfe0acaee0acbee0aca3e0a5a420e0ac8fe0acb9e0acbee0ac95e0ad8120e0ac97e0acbee0aca3e0acbfe0aca4e0acbfe0ac9520e0acade0acbee0acace0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1203d20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1202f20e0ac86e0ad9fe0aca4e0aca8202844656e73697479203d204d617373202f20566f6c756d652920e0acace0ad8be0acb2e0acbf20e0acaae0ad8de0acb0e0ac95e0acbee0acb620e0ac95e0acb0e0acbee0acafe0acbee0ac8f2c20e0acafe0acbee0acb9e0acbee0acb020e0acb8e0ac99e0ad8de0ac95e0ad87e0aca420e0acb9e0ad87e0ac89e0ac9be0acbf20cf812028e0acb0e0ad8b2920e0ac95e0acbfe0acaee0ad8de0acace0acbe2064203d204d202f2056e0a5a420e0ac86e0aca8e0ad8de0aca4e0acb0e0ad8de0ac9ce0acbee0aca4e0ad80e0ad9f20e0acaee0acbee0aca8e0ac95202853492920e0acaae0aca6e0ad8de0aca7e0aca4e0acbfe0acb0e0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1e0acb020e0ac8fe0ac95e0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0acbfe0acb2e0ad8be0ac97e0ad8de0acb0e0acbee0acae20e0acaae0ad8de0acb0e0aca4e0acbf20e0ac98e0aca820e0acaee0acbfe0ac9fe0acb020286b672f6dc2b329e0a5a420e0acb8e0acbee0aca7e0acbee0acb0e0aca3e0aca4e0ac8320e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac85e0aca7e0acbfe0ac9520e0aca5e0acbee0ac8f2c20e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaee0aca7e0ad8de0ad9fe0acae20e0ac8fe0acace0ac8220e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac95e0acaee0ad8d20e0aca5e0acbee0ac8fe0a5a420e0ac89e0aca6e0acbee0acb9e0acb0e0aca320e0acb8e0ad8de0adb1e0acb0e0ad82e0acaa2c20e0acb2e0ad81e0acb9e0acbee0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0ac95e0acbee0aca020e0aca4e0ad81e0acb3e0aca8e0acbee0acb0e0ad8720e0acace0acb9e0ad81e0aca420e0ac85e0aca7e0acbfe0ac952c20e0ac95e0acbee0acb0e0aca320e0acb2e0ad81e0acb9e0acbee0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acaae0acb0e0acaee0acbee0aca3e0ad81e0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0ac85e0aca4e0acbf20e0aca8e0acbfe0acace0acbfe0aca1e0acbc20e0acade0acbee0acace0ad8720e0acb8e0ac9ce0ad8de0ac9ce0acbfe0aca420e0acb9e0ad8be0ac8720e0acb0e0acb9e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbfe0a5a420e0adaa20e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0acace0acbfe0acb6e0ad81e0aca6e0ad8de0aca720e0ac9ce0acb3e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaae0ad8de0acb0e0acbee0ad9f20e0ada7e0ada6e0ada6e0ada6206b672f6dc2b32028e0acace0acbe20e0ada720672f636dc2b32920e0acb9e0ad8be0ac87e0aca5e0acbee0ac8fe0a5a4a96369746174696f6e7391b36368756e6b5f636830315f63303030325f3031ac636861707465725f7265667391a56368303031aa636f6e666964656e6365cb3fe6666666666666aa70726f76656e616e6365aa65787472616374697665b362617369635f616e737765725f737461747573c0b36d6f64656c5f76616c69646174655f6a736f6ea5747261636594c801d70594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b063376462336262343063343034623731a46e6f6465af646f7562742e7472616e736c617465a57374616765af646f7562742e7472616e736c617465a4746f6f6cae7472616e736c6174655f74657874a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a866616c6c6261636baa6572726f725f636f6465ab554e415641494c41424c45ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727981a6726561736f6ed9a75452414e534c4154494f4e5f50524f56494445523d6d6f636b20e2809420736574205452414e534c4154494f4e5f50524f56494445523d68665f6c6f63616c2028616e642048465f544f4b454e20666f722074686520676174656420496e6469635472616e7332207265706f73292e20546865206f66666c696e65206c6561726e696e67207061746820646f6573206e6f742072657175697265207472616e736c6174696f6e2ea87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8013d0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b033363431333233373264663534306135a46e6f6465ae646f7562742e7265747269657665a57374616765ae646f7562742e7265747269657665a4746f6f6caf72657472696576655f6368756e6b73a870726f7669646572ac6c6f63616c5f687962726964af72756c657365745f76657273696f6ec0a86d6f64656c5f6964a46d6f636ba6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7346a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727982a66368756e6b7304aa636f6e666964656e6365cb3ff0000000000000a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8012a0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b064616638346166666363363834616665a46e6f6465ae646f7562742e67656e6572617465a57374616765ae646f7562742e67656e6572617465a4746f6f6caf67656e65726174655f616e73776572a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a66368756e6b7304ae6f75747075745f73756d6d61727982a36c656ecd0257a96369746174696f6e7301a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec801280594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b030356239616662616166366134613330a46e6f6465ae646f7562742e76616c6964617465a57374616765ae646f7562742e76616c6964617465a4746f6f6caf76616c69646174655f616e73776572a870726f7669646572c0af72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981aa616e737765725f6c656ecd0257ae6f75747075745f73756d6d61727981ac67617465735f70617373656405a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6eaa746f6f6c5f63616c6c7303aa737461727465645f6d73cf000001a13c9aea5eab6465636973696f6e5f6964b5646f7562745f7468726561645f746573745f303032a56572726f72c0ab72657472795f636f756e7400b276616c69646174696f6e5f726573756c747384a26f6bc3ab6661696c65645f67617465c0ac67617465735f70617373656495a6736368656d61b1736f757263655f7265666572656e636573af6c616e67756167655f6c656e677468a6736166657479a967726f756e64696e67ab6f726465725f696e64657804ad66616c6c6261636b5f75736564c2b067656e65726174696f6e5f6572726f72c0b06368616e6e656c5f76657273696f6e73de0014a95f5f73746172745f5f02a5717565727906ad6c6561726e65725f696e70757406b07472616e736c617465645f717565727906b5757365645f7472616e736c6174696f6e5f746f6f6c06a972657472696576616c06a6616e7377657206a5747261636506aa746f6f6c5f63616c6c7306aa737461727465645f6d7306ab6465636973696f6e5f696406a56572726f7206ab72657472795f636f756e7406b276616c69646174696f6e5f726573756c747306ad66616c6c6261636b5f7573656406b067656e65726174696f6e5f6572726f7206b36272616e63683a746f3a7472616e736c61746503b26272616e63683a746f3a726574726965766504b26272616e63683a746f3a67656e657261746505b26272616e63683a746f3a76616c696461746506ad76657273696f6e735f7365656e86a95f5f696e7075745f5f80a95f5f73746172745f5f81a95f5f73746172745f5f01a97472616e736c61746581b36272616e63683a746f3a7472616e736c61746502a8726574726965766581b26272616e63683a746f3a726574726965766503a867656e657261746581b26272616e63683a746f3a67656e657261746504a876616c696461746581b26272616e63683a746f3a76616c696461746505b0757064617465645f6368616e6e656c739fa6616e73776572ab6465636973696f6e5f6964a56572726f72ad66616c6c6261636b5f75736564b067656e65726174696f6e5f6572726f72ad6c6561726e65725f696e707574a57175657279a972657472696576616cab72657472795f636f756e74aa737461727465645f6d73aa746f6f6c5f63616c6c73a57472616365b07472616e736c617465645f7175657279b5757365645f7472616e736c6174696f6e5f746f6f6cb276616c69646174696f6e5f726573756c7473	1792018148078
\.


--
-- Data for Name: langgraph_writes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.langgraph_writes (thread_id, checkpoint_ns, checkpoint_id, task_id, channel, type, blob, created_at) FROM stdin;
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	72572f7d-ed09-826d-4460-6391b5bd5e3e	query	msgpack	\\xb7576861742069732070686f746f73796e7468657369733f	1792018148029
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	72572f7d-ed09-826d-4460-6391b5bd5e3e	learner_input	msgpack	\\xb7576861742069732070686f746f73796e7468657369733f	1792018148029
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	72572f7d-ed09-826d-4460-6391b5bd5e3e	translated_query	null	\\x	1792018148029
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	72572f7d-ed09-826d-4460-6391b5bd5e3e	used_translation_tool	msgpack	\\xc3	1792018148029
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	8d8db099-746d-7a27-33c8-e92c49139573	query	msgpack	\\xb7576861742069732070686f746f73796e7468657369733f	1792018147948
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	8d8db099-746d-7a27-33c8-e92c49139573	learner_input	msgpack	\\xb7576861742069732070686f746f73796e7468657369733f	1792018147948
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	72572f7d-ed09-826d-4460-6391b5bd5e3e	retrieval	msgpack	\\xc81e0e0594b26170702e646f6d61696e2e736368656d6173af526574726965766564526573756c7484a66368756e6b739487a86368756e6b5f6964b36368756e6b5f636830315f63303030325f3031aa636f6e636570745f6964a56330303032aa636861707465725f6964a56368303031a7746578745f6f72da06c2e0ac98e0aca8e0aca4e0ad8de0adb1202864656e736974792920e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0ad8ce0aca3e0acb8e0acbf20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac8fe0ac95e0ac9520e0ac86e0ad9fe0aca4e0aca8e0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1e0acb020e0acaae0acb0e0acbfe0acaee0acbee0aca3e0a5a420e0ac8fe0acb9e0acbee0ac95e0ad8120e0ac97e0acbee0aca3e0acbfe0aca4e0acbfe0ac9520e0acade0acbee0acace0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1203d20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1202f20e0ac86e0ad9fe0aca4e0aca8202844656e73697479203d204d617373202f20566f6c756d652920e0acace0ad8be0acb2e0acbf20e0acaae0ad8de0acb0e0ac95e0acbee0acb620e0ac95e0acb0e0acbee0acafe0acbee0ac8f2c20e0acafe0acbee0acb9e0acbee0acb020e0acb8e0ac99e0ad8de0ac95e0ad87e0aca420e0acb9e0ad87e0ac89e0ac9be0acbf20cf812028e0acb0e0ad8b2920e0ac95e0acbfe0acaee0ad8de0acace0acbe2064203d204d202f2056e0a5a420e0ac86e0aca8e0ad8de0aca4e0acb0e0ad8de0ac9ce0acbee0aca4e0ad80e0ad9f20e0acaee0acbee0aca8e0ac95202853492920e0acaae0aca6e0ad8de0aca7e0aca4e0acbfe0acb0e0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1e0acb020e0ac8fe0ac95e0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0acbfe0acb2e0ad8be0ac97e0ad8de0acb0e0acbee0acae20e0acaae0ad8de0acb0e0aca4e0acbf20e0ac98e0aca820e0acaee0acbfe0ac9fe0acb020286b672f6dc2b329e0a5a420e0acb8e0acbee0aca7e0acbee0acb0e0aca3e0aca4e0ac8320e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac85e0aca7e0acbfe0ac9520e0aca5e0acbee0ac8f2c20e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaee0aca7e0ad8de0ad9fe0acae20e0ac8fe0acace0ac8220e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac95e0acaee0ad8d20e0aca5e0acbee0ac8fe0a5a420e0ac89e0aca6e0acbee0acb9e0acb0e0aca320e0acb8e0ad8de0adb1e0acb0e0ad82e0acaa2c20e0acb2e0ad81e0acb9e0acbee0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0ac95e0acbee0aca020e0aca4e0ad81e0acb3e0aca8e0acbee0acb0e0ad8720e0acace0acb9e0ad81e0aca420e0ac85e0aca7e0acbfe0ac952c20e0ac95e0acbee0acb0e0aca320e0acb2e0ad81e0acb9e0acbee0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acaae0acb0e0acaee0acbee0aca3e0ad81e0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0ac85e0aca4e0acbf20e0aca8e0acbfe0acace0acbfe0aca1e0acbc20e0acade0acbee0acace0ad8720e0acb8e0ac9ce0ad8de0ac9ce0acbfe0aca420e0acb9e0ad8be0ac8720e0acb0e0acb9e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbfe0a5a420e0adaa20e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0acace0acbfe0acb6e0ad81e0aca6e0ad8de0aca720e0ac9ce0acb3e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaae0ad8de0acb0e0acbee0ad9f20e0ada7e0ada6e0ada6e0ada6206b672f6dc2b32028e0acace0acbe20e0ada720672f636dc2b32920e0acb9e0ad8be0ac87e0aca5e0acbee0ac8fe0a5a420e0ac95e0ad8ce0aca3e0acb8e0acbf20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0aca4e0acbee0acb020e0ac85e0aca3e0ad81e0ac97e0ad81e0aca1e0acbce0acbfe0ac95e0acb020e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb120e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0ad8020e0aca6e0ad82e0acb0e0aca4e0acbe20e0ac89e0acaae0acb0e0ad8720e0aca8e0acbfe0acb0e0ad8de0acade0acb020e0ac95e0acb0e0acbfe0aca5e0acbee0ac8fe0a5a4aa736f757263655f726566aa6368303120c2a7312e33a573636f7265cb3ff0000000000000ad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030315f3032aa636f6e636570745f6964a56330303031aa636861707465725f6964a56368303031a7746578745f6f72da06f3e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0aca4e0acbfe0aca8e0ad8be0ac9fe0acbf20e0ac85e0acace0acb8e0ad8de0aca5e0acbee0acb020e0acade0acbfe0aca8e0ad8de0aca820e0acade0acbfe0aca8e0ad8de0aca820e0acade0ad8ce0aca4e0acbfe0ac9520e0aca7e0acb0e0ad8de0acae20e0acb0e0acb9e0acbfe0ac9be0acbfe0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020286669786564207368617065292c20e0acb8e0ad8de0acaae0acb7e0ad8de0ac9f20e0acb8e0ad80e0acaee0acbee0acb0e0ad87e0ac96e0acbe20e0ac8fe0acace0ac8220e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ad9fe0aca4e0aca82028666978656420766f6c756d652920e0aca5e0acbee0ac8fe0a5a420e0ac8fe0acb9e0acbe20e0acb8e0acb9e0ac9ce0acb0e0ad8720e0acb8e0ac99e0ad8de0ac95e0ad81e0ac9ae0acbfe0aca42028636f6d707265737369626c652920e0acb9e0ad8be0ac87e0acaae0acbee0acb0e0ad8720e0aca8e0acbee0acb9e0acbfe0ac81e0a5a420e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac95e0ad8ce0aca3e0acb8e0acbf20e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020e0aca8e0aca5e0acbee0ac8f2c20e0ac95e0acbfe0aca8e0ad8de0aca4e0ad8120e0ac8fe0acb9e0acbee0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ad9fe0aca4e0aca820e0aca5e0acbee0ac8fe0a5a420e0aca4e0acb0e0acb3e0ac95e0ad8120e0acafe0ad87e0ac89e0ac8120e0acaae0acbee0aca4e0ad8de0acb0e0acb0e0ad8720e0acb0e0ac96e0acbee0acafe0acbee0ac8f2c20e0aca4e0acbee0acb9e0acbe20e0acb8e0ad87e0acb9e0acbf20e0acaae0acbee0aca4e0ad8de0acb0e0acb020e0ac86e0ac95e0acbee0acb020e0aca7e0acbee0acb0e0aca320e0ac95e0acb0e0ad87e0a5a420e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac95e0ad8ce0aca3e0acb8e0acbf20e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac86e0ad9fe0aca4e0aca820e0aca8e0aca5e0acbee0ac8f3b20e0ac8fe0acb9e0acbe20e0ac89e0acaae0acb2e0acace0ad8de0aca720e0acb8e0acaee0acb8e0ad8de0aca420e0acb8e0ad8de0aca5e0acbee0aca8e0ac95e0ad8120e0acaae0ad82e0acb0e0ad8de0aca3e0ad8de0aca320e0ac95e0acb0e0acbfe0aca6e0acbfe0ac8fe0a5a420e0ac97e0ad8de0ad9fe0acbee0acb8e0acb020e0acb8e0ac99e0ad8de0ac95e0ad8be0ac9ae0aca8e0acb6e0ad80e0acb3e0aca4e0acbe2028636f6d70726573736962696c6974792920e0acb8e0acb0e0ad8de0acace0acbee0aca7e0acbfe0ac9520e0acb9e0ad8be0ac87e0aca5e0acbfe0acace0acbee0acb0e0ad8120e0ac8fe0acb9e0acbee0ac95e0ad8120e0ac89e0ac9ae0ad8de0ac9a20e0ac9ae0acbee0acaae0acb0e0ad8720e0acb8e0acbfe0acb2e0acbfe0aca3e0ad8de0aca1e0acb020e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0acade0acb0e0ad8de0aca4e0ad8de0aca4e0acbf20e0ac95e0acb0e0acbee0acafe0acbee0ac87e0acaae0acbee0acb0e0ad872c20e0acafe0ad87e0acaae0acb0e0acbfe0ac95e0acbf20e0ac86e0acae20e0ac98e0acb0e0ad8720e0acace0ad8de0ad9fe0acace0acb9e0ad83e0aca420e0acb9e0ad87e0ac89e0aca5e0acbfe0acace0acbe20e0ac8fe0acb2e0acaae0acbfe0ac9ce0acbf20284c50472920e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac85e0ac95e0ad8de0acb8e0acbfe0ac9ce0ad87e0aca820e0acb8e0acbfe0acb2e0acbfe0aca3e0ad8de0aca1e0acb0e0a5a420e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0ac97e0aca4e0acbfe0ac9c20e0acb6e0ac95e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0ac86e0aca8e0ad8de0aca4e0ac83e0ac95e0aca3e0acbfe0ac95e0acbe20e0acb8e0ad8de0aca5e0acbee0aca820e0acb9e0acbfe0ac8120e0ac8fe0acb9e0acbf20e0acb8e0acaee0acb8e0ad8de0aca420e0acaae0acbee0acb0e0ad8de0aca5e0ac95e0ad8de0ad9fe0acb020e0acaee0ad82e0acb320e0ac95e0acbee0acb0e0aca320e0ac85e0ac9fe0ad87e0a5a4aa736f757263655f726566aa6368303120c2a7312e32a573636f7265cb3fdd17fa84aa97caad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030335f3031aa636f6e636570745f6964a56330303033aa636861707465725f6964a56368303031a7746578745f6f72da06e2e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbe20e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac9ae0acbee0acaae0acb020e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0ac98e0ac9fe0acbee0ac8720e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac85e0acace0acb8e0ad8de0aca5e0acbe20e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0ac95e0acb0e0acbee0acafe0acbee0ac87e0acaae0acbee0acb0e0ad87e0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0ac95e0ad8120e0ac97e0acb0e0acae20e0ac95e0acb2e0ad8720e0aca4e0acbee0acb020e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0ac97e0aca4e0acbfe0ac9c20e0acb6e0ac95e0ad8de0aca4e0acbf20e0acace0aca2e0acbce0acbfe0acafe0acbee0ac8f20e0ac8fe0acace0ac8220e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0ac8fe0acb9e0acbe20e0aca4e0acb0e0acb3e0acbfe0acace0acbee0ac95e0ad8120e0acb2e0acbee0ac97e0ad87e0a5a420e0acafe0ad87e0ac89e0ac8120e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0acace0acbee0ad9fe0ad81e0acaee0aca3e0ad8de0aca1e0acb3e0ad80e0ad9f20e0ac9ae0acbee0acaae0acb0e0ad8720e0ac8fe0ac9520e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0aca4e0acb0e0acb3e0acb0e0ad8720e0acaae0acb0e0acbfe0aca3e0aca420e0acb9e0ad81e0ac8f2c20e0aca4e0acbee0acb9e0acbee0ac95e0ad8120e0aca4e0acbee0acb020e0ac97e0acb3e0aca8e0acbee0ac99e0ad8de0ac9520286d656c74696e6720706f696e742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a420e0acace0acb0e0acabe0acb020e0ac97e0acb3e0aca8e0acbee0ac99e0ad8de0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ada620e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0acace0acbe20e0ada8e0adade0ada920e0ac95e0ad87e0acb2e0acade0acbfe0aca8e0a5a420e0acb8e0ad87e0acb9e0acbfe0acaae0acb0e0acbf20e0acafe0ad87e0ac89e0ac8120e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acabe0ad81e0ac9fe0acbf20e0acace0acbee0acb7e0ad8de0acaae0acb0e0ad8720e0acaae0acb0e0acbfe0aca3e0aca420e0acb9e0ad81e0ac8f2c20e0aca4e0acbee0acb9e0acbee0ac95e0ad8120e0acb8e0ad8de0acabe0ad81e0ac9fe0aca8e0acbee0ac99e0ad8de0ac952028626f696c696e6720706f696e742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a420e0ac9ce0acb3e0acb020e0acb8e0ad8de0acabe0ad81e0ac9fe0aca8e0acbee0ac99e0ad8de0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ada7e0ada6e0ada620e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0acace0acbe20e0ada9e0adade0ada920e0ac95e0ad87e0acb2e0acade0acbfe0aca8e0a5a420e0ac85e0acace0acb8e0ad8de0aca5e0acbe20e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0acb8e0acaee0ad9fe0acb0e0ad8720e0acafe0ad8be0ac9720e0ac95e0acb0e0acbee0acafe0acbee0ac89e0aca5e0acbfe0acace0acbe20e0aca4e0acbee0acaa20e0acb6e0ac95e0ad8de0aca4e0acbf20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbe20e0aca820e0acace0aca2e0acbce0acbee0ac8720e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb3e0ac95e0ad8120e0acade0acbee0ac99e0ad8de0ac97e0acbfe0acace0acbee0acb0e0ad8720e0acace0ad8de0ad9fe0acace0acb9e0ad83e0aca420e0acb9e0ad81e0ac8f2c20e0acafe0acbee0acb9e0acbee0ac95e0ad8120e0ac97e0ad81e0acaae0ad8de0aca4e0aca4e0acbee0acaa20286c6174656e7420686561742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a4aa736f757263655f726566aa6368303120c2a7312e34a573636f7265cb3fdd17fa84aa97caad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030315f3031aa636f6e636570745f6964a56330303031aa636861707465725f6964a56368303031a7746578745f6f72da0702e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac86e0acae20e0acaae0acb0e0acbfe0acace0ad87e0acb6e0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acaae0ad8de0acb0e0aca4e0ad8de0ad9fe0ad87e0ac9520e0acace0acb8e0ad8de0aca4e0ad8120e0acafe0acbee0acb9e0acbee0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb120286d6173732920e0aca5e0acbee0ac8f20e0ac8fe0acace0ac8220e0acafe0acbee0acb9e0acbe20e0ac95e0acbfe0ac9be0acbf20e0acb8e0ad8de0aca5e0acbee0aca820e0acace0acbe20e0ac86e0ad9fe0aca4e0aca82028766f6c756d652920e0ac85e0aca7e0acbfe0ac95e0acbee0acb020e0ac95e0acb0e0ad87e0a5a420e0acaae0ad8de0acb0e0ac95e0ad83e0aca4e0acbfe0acb0e0ad8720e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acaee0ad81e0ac96e0ad8de0ad9fe0aca4e0ac8320e0aca4e0acbfe0aca8e0ad8be0ac9fe0acbf20e0acade0ad8ce0aca4e0acbfe0ac9520e0acb8e0ad8de0aca5e0acbfe0aca4e0acbfe0acb0e0ad8720e0aca6e0ad87e0ac96e0acbee0acafe0acbee0ac8f3a20e0ac95e0aca0e0acbfe0aca82028736f6c6964292c20e0aca4e0acb0e0acb320286c69717569642920e0ac8fe0acace0ac8220e0ac97e0ad8de0ad9fe0acbee0acb8202867617329e0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0ac85e0aca4e0ad8de0ad9fe0aca8e0ad8de0aca420e0aca8e0acbfe0acace0acbfe0aca1e0acbc20e0acade0acbee0acace0acb0e0ad8720e0acb8e0ac9ce0ad8de0ac9ce0acbfe0aca420e0acb9e0ad8be0ac8720e0acb0e0acb9e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0ac86e0aca8e0ad8de0aca4e0ac83e0ac95e0aca3e0acbfe0ac95e0acbe20e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb32028696e7465726d6f6c6563756c617220666f7263652920e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac85e0aca7e0acbfe0ac9520e0acaae0ad8de0acb0e0acace0acb320e0aca5e0acbee0ac8fe0a5a420e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0ac95e0acbfe0ac9be0acbf20e0acabe0acbee0ac99e0ad8de0ac95e0acbe20e0acb8e0ad8de0aca5e0acbee0aca820e0aca5e0acbee0ac8f20e0ac8fe0acace0ac8220e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb320e0ac95e0aca0e0acbfe0aca820e0aca4e0ad81e0acb3e0aca8e0acbee0acb0e0ad8720e0ac95e0acaee0ad8d20e0aca5e0acbee0ac8f2c20e0acafe0acbee0acb9e0acbe20e0acabe0acb3e0acb0e0ad8720e0acb8e0ad87e0acaee0acbee0aca8e0ad8720e0acaae0ad8de0acb0e0acace0acbee0acb9e0acbfe0aca420e0acb9e0ad8be0ac87e0acaae0acbee0acb0e0aca8e0ad8de0aca4e0acbfe0a5a420e0ac85e0aca8e0ad8de0ad9fe0acaae0ac95e0ad8de0acb7e0acb0e0ad872c20e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0acaae0acb0e0acb8e0ad8de0acaae0acb0e0aca0e0acbee0acb0e0ad8120e0acace0acb9e0ad81e0aca420e0aca6e0ad82e0acb0e0acb0e0ad8720e0aca5e0acbee0ac86e0aca8e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb320e0aca8e0ac97e0aca3e0ad8de0ad9f20e0aca5e0acbee0ac8fe0a5a420e0aca4e0ad87e0aca3e0ad8120e0ac97e0ad8de0ad9fe0acbee0acb8e0acb020e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0acb8e0acaee0acb8e0ad8de0aca420e0aca6e0acbfe0ac97e0acb0e0ad8720e0aca6e0ad8de0acb0e0ad81e0aca420e0ac9320e0acaee0ad81e0ac95e0ad8de0aca420e0acade0acbee0acace0acb0e0ad8720e0ac97e0aca4e0acbf20e0ac95e0acb0e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbfe0a5a4aa736f757263655f726566aa6368303120c2a7312e32a573636f7265cb0000000000000000ad6d6174636865645f7465726d7390a870726f7669646572ac6c6f63616c5f687962726964a86d6f64656c5f6964a46d6f636baa636f6e666964656e6365cb3ff0000000000000b36d6f64656c5f76616c69646174655f6a736f6e	1792018148029
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	e6400efa-d054-39fb-69f6-92e94ce2cbae	query	msgpack	\\xb7576861742069732070686f746f73796e7468657369733f	1792018147951
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	8d8db099-746d-7a27-33c8-e92c49139573	translated_query	null	\\x	1792018147948
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	72572f7d-ed09-826d-4460-6391b5bd5e3e	answer	msgpack	\\xc806750594b26170702e646f6d61696e2e736368656d6173af47656e657261746564416e7377657286a7746578745f6f72da05bfe0ac98e0aca8e0aca4e0ad8de0adb1202864656e736974792920e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0ad8ce0aca3e0acb8e0acbf20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac8fe0ac95e0ac9520e0ac86e0ad9fe0aca4e0aca8e0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1e0acb020e0acaae0acb0e0acbfe0acaee0acbee0aca3e0a5a420e0ac8fe0acb9e0acbee0ac95e0ad8120e0ac97e0acbee0aca3e0acbfe0aca4e0acbfe0ac9520e0acade0acbee0acace0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1203d20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1202f20e0ac86e0ad9fe0aca4e0aca8202844656e73697479203d204d617373202f20566f6c756d652920e0acace0ad8be0acb2e0acbf20e0acaae0ad8de0acb0e0ac95e0acbee0acb620e0ac95e0acb0e0acbee0acafe0acbee0ac8f2c20e0acafe0acbee0acb9e0acbee0acb020e0acb8e0ac99e0ad8de0ac95e0ad87e0aca420e0acb9e0ad87e0ac89e0ac9be0acbf20cf812028e0acb0e0ad8b2920e0ac95e0acbfe0acaee0ad8de0acace0acbe2064203d204d202f2056e0a5a420e0ac86e0aca8e0ad8de0aca4e0acb0e0ad8de0ac9ce0acbee0aca4e0ad80e0ad9f20e0acaee0acbee0aca8e0ac95202853492920e0acaae0aca6e0ad8de0aca7e0aca4e0acbfe0acb0e0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1e0acb020e0ac8fe0ac95e0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0acbfe0acb2e0ad8be0ac97e0ad8de0acb0e0acbee0acae20e0acaae0ad8de0acb0e0aca4e0acbf20e0ac98e0aca820e0acaee0acbfe0ac9fe0acb020286b672f6dc2b329e0a5a420e0acb8e0acbee0aca7e0acbee0acb0e0aca3e0aca4e0ac8320e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac85e0aca7e0acbfe0ac9520e0aca5e0acbee0ac8f2c20e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaee0aca7e0ad8de0ad9fe0acae20e0ac8fe0acace0ac8220e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac95e0acaee0ad8d20e0aca5e0acbee0ac8fe0a5a420e0ac89e0aca6e0acbee0acb9e0acb0e0aca320e0acb8e0ad8de0adb1e0acb0e0ad82e0acaa2c20e0acb2e0ad81e0acb9e0acbee0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0ac95e0acbee0aca020e0aca4e0ad81e0acb3e0aca8e0acbee0acb0e0ad8720e0acace0acb9e0ad81e0aca420e0ac85e0aca7e0acbfe0ac952c20e0ac95e0acbee0acb0e0aca320e0acb2e0ad81e0acb9e0acbee0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acaae0acb0e0acaee0acbee0aca3e0ad81e0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0ac85e0aca4e0acbf20e0aca8e0acbfe0acace0acbfe0aca1e0acbc20e0acade0acbee0acace0ad8720e0acb8e0ac9ce0ad8de0ac9ce0acbfe0aca420e0acb9e0ad8be0ac8720e0acb0e0acb9e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbfe0a5a420e0adaa20e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0acace0acbfe0acb6e0ad81e0aca6e0ad8de0aca720e0ac9ce0acb3e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaae0ad8de0acb0e0acbee0ad9f20e0ada7e0ada6e0ada6e0ada6206b672f6dc2b32028e0acace0acbe20e0ada720672f636dc2b32920e0acb9e0ad8be0ac87e0aca5e0acbee0ac8fe0a5a4a96369746174696f6e7391b36368756e6b5f636830315f63303030325f3031ac636861707465725f7265667391a56368303031aa636f6e666964656e6365cb3fe6666666666666aa70726f76656e616e6365aa65787472616374697665b362617369635f616e737765725f737461747573c0b36d6f64656c5f76616c69646174655f6a736f6e	1792018148029
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	e6400efa-d054-39fb-69f6-92e94ce2cbae	learner_input	msgpack	\\xb7576861742069732070686f746f73796e7468657369733f	1792018147951
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	8d8db099-746d-7a27-33c8-e92c49139573	used_translation_tool	msgpack	\\xc2	1792018147948
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	72572f7d-ed09-826d-4460-6391b5bd5e3e	trace	msgpack	\\x94c801d70594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b063376462336262343063343034623731a46e6f6465af646f7562742e7472616e736c617465a57374616765af646f7562742e7472616e736c617465a4746f6f6cae7472616e736c6174655f74657874a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a866616c6c6261636baa6572726f725f636f6465ab554e415641494c41424c45ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727981a6726561736f6ed9a75452414e534c4154494f4e5f50524f56494445523d6d6f636b20e2809420736574205452414e534c4154494f4e5f50524f56494445523d68665f6c6f63616c2028616e642048465f544f4b454e20666f722074686520676174656420496e6469635472616e7332207265706f73292e20546865206f66666c696e65206c6561726e696e67207061746820646f6573206e6f742072657175697265207472616e736c6174696f6e2ea87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8013d0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b033363431333233373264663534306135a46e6f6465ae646f7562742e7265747269657665a57374616765ae646f7562742e7265747269657665a4746f6f6caf72657472696576655f6368756e6b73a870726f7669646572ac6c6f63616c5f687962726964af72756c657365745f76657273696f6ec0a86d6f64656c5f6964a46d6f636ba6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7346a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727982a66368756e6b7304aa636f6e666964656e6365cb3ff0000000000000a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8012a0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b064616638346166666363363834616665a46e6f6465ae646f7562742e67656e6572617465a57374616765ae646f7562742e67656e6572617465a4746f6f6caf67656e65726174655f616e73776572a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a66368756e6b7304ae6f75747075745f73756d6d61727982a36c656ecd0257a96369746174696f6e7301a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec801280594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b030356239616662616166366134613330a46e6f6465ae646f7562742e76616c6964617465a57374616765ae646f7562742e76616c6964617465a4746f6f6caf76616c69646174655f616e73776572a870726f7669646572c0af72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981aa616e737765725f6c656ecd0257ae6f75747075745f73756d6d61727981ac67617465735f70617373656405a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6e	1792018148029
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	e6400efa-d054-39fb-69f6-92e94ce2cbae	translated_query	null	\\x	1792018147951
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	8ab41f0e-30e0-d987-4d81-ccebcf6e6b95	query	msgpack	\\xb7576861742069732070686f746f73796e7468657369733f	1792018148025
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	8d8db099-746d-7a27-33c8-e92c49139573	retrieval	null	\\x	1792018147948
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	72572f7d-ed09-826d-4460-6391b5bd5e3e	tool_calls	msgpack	\\x03	1792018148029
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	72572f7d-ed09-826d-4460-6391b5bd5e3e	started_ms	msgpack	\\xcf000001a13c9aea5e	1792018148029
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	72572f7d-ed09-826d-4460-6391b5bd5e3e	decision_id	msgpack	\\xb5646f7562745f7468726561645f746573745f303032	1792018148029
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	72572f7d-ed09-826d-4460-6391b5bd5e3e	error	null	\\x	1792018148029
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	72572f7d-ed09-826d-4460-6391b5bd5e3e	retry_count	msgpack	\\x00	1792018148029
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	72572f7d-ed09-826d-4460-6391b5bd5e3e	validation_results	msgpack	\\x80	1792018148029
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	72572f7d-ed09-826d-4460-6391b5bd5e3e	fallback_used	msgpack	\\xc2	1792018148029
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	72572f7d-ed09-826d-4460-6391b5bd5e3e	generation_error	null	\\x	1792018148029
doubt_thread_test_002		1f1c8217-6f25-6eb3-8002-597934130cd1	72572f7d-ed09-826d-4460-6391b5bd5e3e	branch:to:validate	null	\\x	1792018148029
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	e6400efa-d054-39fb-69f6-92e94ce2cbae	used_translation_tool	msgpack	\\xc3	1792018147951
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	e6400efa-d054-39fb-69f6-92e94ce2cbae	retrieval	null	\\x	1792018147951
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	e6400efa-d054-39fb-69f6-92e94ce2cbae	answer	null	\\x	1792018147951
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	e6400efa-d054-39fb-69f6-92e94ce2cbae	trace	msgpack	\\x94c801d70594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b063376462336262343063343034623731a46e6f6465af646f7562742e7472616e736c617465a57374616765af646f7562742e7472616e736c617465a4746f6f6cae7472616e736c6174655f74657874a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a866616c6c6261636baa6572726f725f636f6465ab554e415641494c41424c45ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727981a6726561736f6ed9a75452414e534c4154494f4e5f50524f56494445523d6d6f636b20e2809420736574205452414e534c4154494f4e5f50524f56494445523d68665f6c6f63616c2028616e642048465f544f4b454e20666f722074686520676174656420496e6469635472616e7332207265706f73292e20546865206f66666c696e65206c6561726e696e67207061746820646f6573206e6f742072657175697265207472616e736c6174696f6e2ea87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8013d0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b033363431333233373264663534306135a46e6f6465ae646f7562742e7265747269657665a57374616765ae646f7562742e7265747269657665a4746f6f6caf72657472696576655f6368756e6b73a870726f7669646572ac6c6f63616c5f687962726964af72756c657365745f76657273696f6ec0a86d6f64656c5f6964a46d6f636ba6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7346a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727982a66368756e6b7304aa636f6e666964656e6365cb3ff0000000000000a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8012a0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b064616638346166666363363834616665a46e6f6465ae646f7562742e67656e6572617465a57374616765ae646f7562742e67656e6572617465a4746f6f6caf67656e65726174655f616e73776572a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a66368756e6b7304ae6f75747075745f73756d6d61727982a36c656ecd0257a96369746174696f6e7301a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec801280594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b030356239616662616166366134613330a46e6f6465ae646f7562742e76616c6964617465a57374616765ae646f7562742e76616c6964617465a4746f6f6caf76616c69646174655f616e73776572a870726f7669646572c0af72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981aa616e737765725f6c656ecd0257ae6f75747075745f73756d6d61727981ac67617465735f70617373656405a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6e	1792018147951
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	e6400efa-d054-39fb-69f6-92e94ce2cbae	tool_calls	msgpack	\\x01	1792018147951
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	e6400efa-d054-39fb-69f6-92e94ce2cbae	started_ms	msgpack	\\xcf000001a13c9aea5e	1792018147951
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	e6400efa-d054-39fb-69f6-92e94ce2cbae	decision_id	msgpack	\\xb5646f7562745f7468726561645f746573745f303032	1792018147951
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	e6400efa-d054-39fb-69f6-92e94ce2cbae	error	null	\\x	1792018147951
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	e6400efa-d054-39fb-69f6-92e94ce2cbae	retry_count	msgpack	\\x00	1792018147951
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	e6400efa-d054-39fb-69f6-92e94ce2cbae	validation_results	msgpack	\\x80	1792018147951
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	e6400efa-d054-39fb-69f6-92e94ce2cbae	fallback_used	msgpack	\\xc2	1792018147951
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	e6400efa-d054-39fb-69f6-92e94ce2cbae	generation_error	null	\\x	1792018147951
doubt_thread_test_002		1f1c8217-6e69-69c3-8000-8aece5e5181a	e6400efa-d054-39fb-69f6-92e94ce2cbae	branch:to:retrieve	null	\\x	1792018147951
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	8ab41f0e-30e0-d987-4d81-ccebcf6e6b95	learner_input	msgpack	\\xb7576861742069732070686f746f73796e7468657369733f	1792018148025
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	8ab41f0e-30e0-d987-4d81-ccebcf6e6b95	translated_query	null	\\x	1792018148025
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	8ab41f0e-30e0-d987-4d81-ccebcf6e6b95	used_translation_tool	msgpack	\\xc3	1792018148025
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	8ab41f0e-30e0-d987-4d81-ccebcf6e6b95	retrieval	msgpack	\\xc81e0e0594b26170702e646f6d61696e2e736368656d6173af526574726965766564526573756c7484a66368756e6b739487a86368756e6b5f6964b36368756e6b5f636830315f63303030325f3031aa636f6e636570745f6964a56330303032aa636861707465725f6964a56368303031a7746578745f6f72da06c2e0ac98e0aca8e0aca4e0ad8de0adb1202864656e736974792920e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0ad8ce0aca3e0acb8e0acbf20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac8fe0ac95e0ac9520e0ac86e0ad9fe0aca4e0aca8e0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1e0acb020e0acaae0acb0e0acbfe0acaee0acbee0aca3e0a5a420e0ac8fe0acb9e0acbee0ac95e0ad8120e0ac97e0acbee0aca3e0acbfe0aca4e0acbfe0ac9520e0acade0acbee0acace0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1203d20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1202f20e0ac86e0ad9fe0aca4e0aca8202844656e73697479203d204d617373202f20566f6c756d652920e0acace0ad8be0acb2e0acbf20e0acaae0ad8de0acb0e0ac95e0acbee0acb620e0ac95e0acb0e0acbee0acafe0acbee0ac8f2c20e0acafe0acbee0acb9e0acbee0acb020e0acb8e0ac99e0ad8de0ac95e0ad87e0aca420e0acb9e0ad87e0ac89e0ac9be0acbf20cf812028e0acb0e0ad8b2920e0ac95e0acbfe0acaee0ad8de0acace0acbe2064203d204d202f2056e0a5a420e0ac86e0aca8e0ad8de0aca4e0acb0e0ad8de0ac9ce0acbee0aca4e0ad80e0ad9f20e0acaee0acbee0aca8e0ac95202853492920e0acaae0aca6e0ad8de0aca7e0aca4e0acbfe0acb0e0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1e0acb020e0ac8fe0ac95e0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0acbfe0acb2e0ad8be0ac97e0ad8de0acb0e0acbee0acae20e0acaae0ad8de0acb0e0aca4e0acbf20e0ac98e0aca820e0acaee0acbfe0ac9fe0acb020286b672f6dc2b329e0a5a420e0acb8e0acbee0aca7e0acbee0acb0e0aca3e0aca4e0ac8320e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac85e0aca7e0acbfe0ac9520e0aca5e0acbee0ac8f2c20e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaee0aca7e0ad8de0ad9fe0acae20e0ac8fe0acace0ac8220e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac95e0acaee0ad8d20e0aca5e0acbee0ac8fe0a5a420e0ac89e0aca6e0acbee0acb9e0acb0e0aca320e0acb8e0ad8de0adb1e0acb0e0ad82e0acaa2c20e0acb2e0ad81e0acb9e0acbee0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0ac95e0acbee0aca020e0aca4e0ad81e0acb3e0aca8e0acbee0acb0e0ad8720e0acace0acb9e0ad81e0aca420e0ac85e0aca7e0acbfe0ac952c20e0ac95e0acbee0acb0e0aca320e0acb2e0ad81e0acb9e0acbee0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acaae0acb0e0acaee0acbee0aca3e0ad81e0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0ac85e0aca4e0acbf20e0aca8e0acbfe0acace0acbfe0aca1e0acbc20e0acade0acbee0acace0ad8720e0acb8e0ac9ce0ad8de0ac9ce0acbfe0aca420e0acb9e0ad8be0ac8720e0acb0e0acb9e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbfe0a5a420e0adaa20e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0acace0acbfe0acb6e0ad81e0aca6e0ad8de0aca720e0ac9ce0acb3e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaae0ad8de0acb0e0acbee0ad9f20e0ada7e0ada6e0ada6e0ada6206b672f6dc2b32028e0acace0acbe20e0ada720672f636dc2b32920e0acb9e0ad8be0ac87e0aca5e0acbee0ac8fe0a5a420e0ac95e0ad8ce0aca3e0acb8e0acbf20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0aca4e0acbee0acb020e0ac85e0aca3e0ad81e0ac97e0ad81e0aca1e0acbce0acbfe0ac95e0acb020e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb120e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0ad8020e0aca6e0ad82e0acb0e0aca4e0acbe20e0ac89e0acaae0acb0e0ad8720e0aca8e0acbfe0acb0e0ad8de0acade0acb020e0ac95e0acb0e0acbfe0aca5e0acbee0ac8fe0a5a4aa736f757263655f726566aa6368303120c2a7312e33a573636f7265cb3ff0000000000000ad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030315f3032aa636f6e636570745f6964a56330303031aa636861707465725f6964a56368303031a7746578745f6f72da06f3e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0aca4e0acbfe0aca8e0ad8be0ac9fe0acbf20e0ac85e0acace0acb8e0ad8de0aca5e0acbee0acb020e0acade0acbfe0aca8e0ad8de0aca820e0acade0acbfe0aca8e0ad8de0aca820e0acade0ad8ce0aca4e0acbfe0ac9520e0aca7e0acb0e0ad8de0acae20e0acb0e0acb9e0acbfe0ac9be0acbfe0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020286669786564207368617065292c20e0acb8e0ad8de0acaae0acb7e0ad8de0ac9f20e0acb8e0ad80e0acaee0acbee0acb0e0ad87e0ac96e0acbe20e0ac8fe0acace0ac8220e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ad9fe0aca4e0aca82028666978656420766f6c756d652920e0aca5e0acbee0ac8fe0a5a420e0ac8fe0acb9e0acbe20e0acb8e0acb9e0ac9ce0acb0e0ad8720e0acb8e0ac99e0ad8de0ac95e0ad81e0ac9ae0acbfe0aca42028636f6d707265737369626c652920e0acb9e0ad8be0ac87e0acaae0acbee0acb0e0ad8720e0aca8e0acbee0acb9e0acbfe0ac81e0a5a420e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac95e0ad8ce0aca3e0acb8e0acbf20e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020e0aca8e0aca5e0acbee0ac8f2c20e0ac95e0acbfe0aca8e0ad8de0aca4e0ad8120e0ac8fe0acb9e0acbee0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ad9fe0aca4e0aca820e0aca5e0acbee0ac8fe0a5a420e0aca4e0acb0e0acb3e0ac95e0ad8120e0acafe0ad87e0ac89e0ac8120e0acaae0acbee0aca4e0ad8de0acb0e0acb0e0ad8720e0acb0e0ac96e0acbee0acafe0acbee0ac8f2c20e0aca4e0acbee0acb9e0acbe20e0acb8e0ad87e0acb9e0acbf20e0acaae0acbee0aca4e0ad8de0acb0e0acb020e0ac86e0ac95e0acbee0acb020e0aca7e0acbee0acb0e0aca320e0ac95e0acb0e0ad87e0a5a420e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac95e0ad8ce0aca3e0acb8e0acbf20e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac86e0ad9fe0aca4e0aca820e0aca8e0aca5e0acbee0ac8f3b20e0ac8fe0acb9e0acbe20e0ac89e0acaae0acb2e0acace0ad8de0aca720e0acb8e0acaee0acb8e0ad8de0aca420e0acb8e0ad8de0aca5e0acbee0aca8e0ac95e0ad8120e0acaae0ad82e0acb0e0ad8de0aca3e0ad8de0aca320e0ac95e0acb0e0acbfe0aca6e0acbfe0ac8fe0a5a420e0ac97e0ad8de0ad9fe0acbee0acb8e0acb020e0acb8e0ac99e0ad8de0ac95e0ad8be0ac9ae0aca8e0acb6e0ad80e0acb3e0aca4e0acbe2028636f6d70726573736962696c6974792920e0acb8e0acb0e0ad8de0acace0acbee0aca7e0acbfe0ac9520e0acb9e0ad8be0ac87e0aca5e0acbfe0acace0acbee0acb0e0ad8120e0ac8fe0acb9e0acbee0ac95e0ad8120e0ac89e0ac9ae0ad8de0ac9a20e0ac9ae0acbee0acaae0acb0e0ad8720e0acb8e0acbfe0acb2e0acbfe0aca3e0ad8de0aca1e0acb020e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0acade0acb0e0ad8de0aca4e0ad8de0aca4e0acbf20e0ac95e0acb0e0acbee0acafe0acbee0ac87e0acaae0acbee0acb0e0ad872c20e0acafe0ad87e0acaae0acb0e0acbfe0ac95e0acbf20e0ac86e0acae20e0ac98e0acb0e0ad8720e0acace0ad8de0ad9fe0acace0acb9e0ad83e0aca420e0acb9e0ad87e0ac89e0aca5e0acbfe0acace0acbe20e0ac8fe0acb2e0acaae0acbfe0ac9ce0acbf20284c50472920e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac85e0ac95e0ad8de0acb8e0acbfe0ac9ce0ad87e0aca820e0acb8e0acbfe0acb2e0acbfe0aca3e0ad8de0aca1e0acb0e0a5a420e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0ac97e0aca4e0acbfe0ac9c20e0acb6e0ac95e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0ac86e0aca8e0ad8de0aca4e0ac83e0ac95e0aca3e0acbfe0ac95e0acbe20e0acb8e0ad8de0aca5e0acbee0aca820e0acb9e0acbfe0ac8120e0ac8fe0acb9e0acbf20e0acb8e0acaee0acb8e0ad8de0aca420e0acaae0acbee0acb0e0ad8de0aca5e0ac95e0ad8de0ad9fe0acb020e0acaee0ad82e0acb320e0ac95e0acbee0acb0e0aca320e0ac85e0ac9fe0ad87e0a5a4aa736f757263655f726566aa6368303120c2a7312e32a573636f7265cb3fdd17fa84aa97caad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030335f3031aa636f6e636570745f6964a56330303033aa636861707465725f6964a56368303031a7746578745f6f72da06e2e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbe20e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac9ae0acbee0acaae0acb020e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0ac98e0ac9fe0acbee0ac8720e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac85e0acace0acb8e0ad8de0aca5e0acbe20e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0ac95e0acb0e0acbee0acafe0acbee0ac87e0acaae0acbee0acb0e0ad87e0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0ac95e0ad8120e0ac97e0acb0e0acae20e0ac95e0acb2e0ad8720e0aca4e0acbee0acb020e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0ac97e0aca4e0acbfe0ac9c20e0acb6e0ac95e0ad8de0aca4e0acbf20e0acace0aca2e0acbce0acbfe0acafe0acbee0ac8f20e0ac8fe0acace0ac8220e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0ac8fe0acb9e0acbe20e0aca4e0acb0e0acb3e0acbfe0acace0acbee0ac95e0ad8120e0acb2e0acbee0ac97e0ad87e0a5a420e0acafe0ad87e0ac89e0ac8120e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0acace0acbee0ad9fe0ad81e0acaee0aca3e0ad8de0aca1e0acb3e0ad80e0ad9f20e0ac9ae0acbee0acaae0acb0e0ad8720e0ac8fe0ac9520e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0aca4e0acb0e0acb3e0acb0e0ad8720e0acaae0acb0e0acbfe0aca3e0aca420e0acb9e0ad81e0ac8f2c20e0aca4e0acbee0acb9e0acbee0ac95e0ad8120e0aca4e0acbee0acb020e0ac97e0acb3e0aca8e0acbee0ac99e0ad8de0ac9520286d656c74696e6720706f696e742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a420e0acace0acb0e0acabe0acb020e0ac97e0acb3e0aca8e0acbee0ac99e0ad8de0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ada620e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0acace0acbe20e0ada8e0adade0ada920e0ac95e0ad87e0acb2e0acade0acbfe0aca8e0a5a420e0acb8e0ad87e0acb9e0acbfe0acaae0acb0e0acbf20e0acafe0ad87e0ac89e0ac8120e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acabe0ad81e0ac9fe0acbf20e0acace0acbee0acb7e0ad8de0acaae0acb0e0ad8720e0acaae0acb0e0acbfe0aca3e0aca420e0acb9e0ad81e0ac8f2c20e0aca4e0acbee0acb9e0acbee0ac95e0ad8120e0acb8e0ad8de0acabe0ad81e0ac9fe0aca8e0acbee0ac99e0ad8de0ac952028626f696c696e6720706f696e742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a420e0ac9ce0acb3e0acb020e0acb8e0ad8de0acabe0ad81e0ac9fe0aca8e0acbee0ac99e0ad8de0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ada7e0ada6e0ada620e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0acace0acbe20e0ada9e0adade0ada920e0ac95e0ad87e0acb2e0acade0acbfe0aca8e0a5a420e0ac85e0acace0acb8e0ad8de0aca5e0acbe20e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0acb8e0acaee0ad9fe0acb0e0ad8720e0acafe0ad8be0ac9720e0ac95e0acb0e0acbee0acafe0acbee0ac89e0aca5e0acbfe0acace0acbe20e0aca4e0acbee0acaa20e0acb6e0ac95e0ad8de0aca4e0acbf20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbe20e0aca820e0acace0aca2e0acbce0acbee0ac8720e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb3e0ac95e0ad8120e0acade0acbee0ac99e0ad8de0ac97e0acbfe0acace0acbee0acb0e0ad8720e0acace0ad8de0ad9fe0acace0acb9e0ad83e0aca420e0acb9e0ad81e0ac8f2c20e0acafe0acbee0acb9e0acbee0ac95e0ad8120e0ac97e0ad81e0acaae0ad8de0aca4e0aca4e0acbee0acaa20286c6174656e7420686561742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a4aa736f757263655f726566aa6368303120c2a7312e34a573636f7265cb3fdd17fa84aa97caad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030315f3031aa636f6e636570745f6964a56330303031aa636861707465725f6964a56368303031a7746578745f6f72da0702e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac86e0acae20e0acaae0acb0e0acbfe0acace0ad87e0acb6e0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acaae0ad8de0acb0e0aca4e0ad8de0ad9fe0ad87e0ac9520e0acace0acb8e0ad8de0aca4e0ad8120e0acafe0acbee0acb9e0acbee0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb120286d6173732920e0aca5e0acbee0ac8f20e0ac8fe0acace0ac8220e0acafe0acbee0acb9e0acbe20e0ac95e0acbfe0ac9be0acbf20e0acb8e0ad8de0aca5e0acbee0aca820e0acace0acbe20e0ac86e0ad9fe0aca4e0aca82028766f6c756d652920e0ac85e0aca7e0acbfe0ac95e0acbee0acb020e0ac95e0acb0e0ad87e0a5a420e0acaae0ad8de0acb0e0ac95e0ad83e0aca4e0acbfe0acb0e0ad8720e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acaee0ad81e0ac96e0ad8de0ad9fe0aca4e0ac8320e0aca4e0acbfe0aca8e0ad8be0ac9fe0acbf20e0acade0ad8ce0aca4e0acbfe0ac9520e0acb8e0ad8de0aca5e0acbfe0aca4e0acbfe0acb0e0ad8720e0aca6e0ad87e0ac96e0acbee0acafe0acbee0ac8f3a20e0ac95e0aca0e0acbfe0aca82028736f6c6964292c20e0aca4e0acb0e0acb320286c69717569642920e0ac8fe0acace0ac8220e0ac97e0ad8de0ad9fe0acbee0acb8202867617329e0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0ac85e0aca4e0ad8de0ad9fe0aca8e0ad8de0aca420e0aca8e0acbfe0acace0acbfe0aca1e0acbc20e0acade0acbee0acace0acb0e0ad8720e0acb8e0ac9ce0ad8de0ac9ce0acbfe0aca420e0acb9e0ad8be0ac8720e0acb0e0acb9e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0ac86e0aca8e0ad8de0aca4e0ac83e0ac95e0aca3e0acbfe0ac95e0acbe20e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb32028696e7465726d6f6c6563756c617220666f7263652920e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac85e0aca7e0acbfe0ac9520e0acaae0ad8de0acb0e0acace0acb320e0aca5e0acbee0ac8fe0a5a420e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0ac95e0acbfe0ac9be0acbf20e0acabe0acbee0ac99e0ad8de0ac95e0acbe20e0acb8e0ad8de0aca5e0acbee0aca820e0aca5e0acbee0ac8f20e0ac8fe0acace0ac8220e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb320e0ac95e0aca0e0acbfe0aca820e0aca4e0ad81e0acb3e0aca8e0acbee0acb0e0ad8720e0ac95e0acaee0ad8d20e0aca5e0acbee0ac8f2c20e0acafe0acbee0acb9e0acbe20e0acabe0acb3e0acb0e0ad8720e0acb8e0ad87e0acaee0acbee0aca8e0ad8720e0acaae0ad8de0acb0e0acace0acbee0acb9e0acbfe0aca420e0acb9e0ad8be0ac87e0acaae0acbee0acb0e0aca8e0ad8de0aca4e0acbfe0a5a420e0ac85e0aca8e0ad8de0ad9fe0acaae0ac95e0ad8de0acb7e0acb0e0ad872c20e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0acaae0acb0e0acb8e0ad8de0acaae0acb0e0aca0e0acbee0acb0e0ad8120e0acace0acb9e0ad81e0aca420e0aca6e0ad82e0acb0e0acb0e0ad8720e0aca5e0acbee0ac86e0aca8e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb320e0aca8e0ac97e0aca3e0ad8de0ad9f20e0aca5e0acbee0ac8fe0a5a420e0aca4e0ad87e0aca3e0ad8120e0ac97e0ad8de0ad9fe0acbee0acb8e0acb020e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0acb8e0acaee0acb8e0ad8de0aca420e0aca6e0acbfe0ac97e0acb0e0ad8720e0aca6e0ad8de0acb0e0ad81e0aca420e0ac9320e0acaee0ad81e0ac95e0ad8de0aca420e0acade0acbee0acace0acb0e0ad8720e0ac97e0aca4e0acbf20e0ac95e0acb0e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbfe0a5a4aa736f757263655f726566aa6368303120c2a7312e32a573636f7265cb0000000000000000ad6d6174636865645f7465726d7390a870726f7669646572ac6c6f63616c5f687962726964a86d6f64656c5f6964a46d6f636baa636f6e666964656e6365cb3ff0000000000000b36d6f64656c5f76616c69646174655f6a736f6e	1792018148025
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	8ab41f0e-30e0-d987-4d81-ccebcf6e6b95	answer	null	\\x	1792018148025
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	8ab41f0e-30e0-d987-4d81-ccebcf6e6b95	trace	msgpack	\\x94c801d70594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b063376462336262343063343034623731a46e6f6465af646f7562742e7472616e736c617465a57374616765af646f7562742e7472616e736c617465a4746f6f6cae7472616e736c6174655f74657874a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a866616c6c6261636baa6572726f725f636f6465ab554e415641494c41424c45ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727981a6726561736f6ed9a75452414e534c4154494f4e5f50524f56494445523d6d6f636b20e2809420736574205452414e534c4154494f4e5f50524f56494445523d68665f6c6f63616c2028616e642048465f544f4b454e20666f722074686520676174656420496e6469635472616e7332207265706f73292e20546865206f66666c696e65206c6561726e696e67207061746820646f6573206e6f742072657175697265207472616e736c6174696f6e2ea87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8013d0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b033363431333233373264663534306135a46e6f6465ae646f7562742e7265747269657665a57374616765ae646f7562742e7265747269657665a4746f6f6caf72657472696576655f6368756e6b73a870726f7669646572ac6c6f63616c5f687962726964af72756c657365745f76657273696f6ec0a86d6f64656c5f6964a46d6f636ba6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7346a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727982a66368756e6b7304aa636f6e666964656e6365cb3ff0000000000000a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8012a0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b064616638346166666363363834616665a46e6f6465ae646f7562742e67656e6572617465a57374616765ae646f7562742e67656e6572617465a4746f6f6caf67656e65726174655f616e73776572a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a66368756e6b7304ae6f75747075745f73756d6d61727982a36c656ecd0257a96369746174696f6e7301a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec801280594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b030356239616662616166366134613330a46e6f6465ae646f7562742e76616c6964617465a57374616765ae646f7562742e76616c6964617465a4746f6f6caf76616c69646174655f616e73776572a870726f7669646572c0af72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981aa616e737765725f6c656ecd0257ae6f75747075745f73756d6d61727981ac67617465735f70617373656405a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6e	1792018148025
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	8ab41f0e-30e0-d987-4d81-ccebcf6e6b95	tool_calls	msgpack	\\x02	1792018148025
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	8ab41f0e-30e0-d987-4d81-ccebcf6e6b95	started_ms	msgpack	\\xcf000001a13c9aea5e	1792018148025
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	8ab41f0e-30e0-d987-4d81-ccebcf6e6b95	decision_id	msgpack	\\xb5646f7562745f7468726561645f746573745f303032	1792018148025
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	8ab41f0e-30e0-d987-4d81-ccebcf6e6b95	error	null	\\x	1792018148025
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	8ab41f0e-30e0-d987-4d81-ccebcf6e6b95	retry_count	msgpack	\\x00	1792018148025
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	8ab41f0e-30e0-d987-4d81-ccebcf6e6b95	validation_results	msgpack	\\x80	1792018148025
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	8ab41f0e-30e0-d987-4d81-ccebcf6e6b95	fallback_used	msgpack	\\xc2	1792018148025
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	8ab41f0e-30e0-d987-4d81-ccebcf6e6b95	generation_error	null	\\x	1792018148025
doubt_thread_test_002		1f1c8217-6e70-61dd-8001-d53b8adf7462	8ab41f0e-30e0-d987-4d81-ccebcf6e6b95	branch:to:generate	null	\\x	1792018148025
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	8d8db099-746d-7a27-33c8-e92c49139573	answer	null	\\x	1792018147948
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	8d8db099-746d-7a27-33c8-e92c49139573	trace	msgpack	\\x94c801d70594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b063376462336262343063343034623731a46e6f6465af646f7562742e7472616e736c617465a57374616765af646f7562742e7472616e736c617465a4746f6f6cae7472616e736c6174655f74657874a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a866616c6c6261636baa6572726f725f636f6465ab554e415641494c41424c45ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727981a6726561736f6ed9a75452414e534c4154494f4e5f50524f56494445523d6d6f636b20e2809420736574205452414e534c4154494f4e5f50524f56494445523d68665f6c6f63616c2028616e642048465f544f4b454e20666f722074686520676174656420496e6469635472616e7332207265706f73292e20546865206f66666c696e65206c6561726e696e67207061746820646f6573206e6f742072657175697265207472616e736c6174696f6e2ea87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8013d0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b033363431333233373264663534306135a46e6f6465ae646f7562742e7265747269657665a57374616765ae646f7562742e7265747269657665a4746f6f6caf72657472696576655f6368756e6b73a870726f7669646572ac6c6f63616c5f687962726964af72756c657365745f76657273696f6ec0a86d6f64656c5f6964a46d6f636ba6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7346a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727982a66368756e6b7304aa636f6e666964656e6365cb3ff0000000000000a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8012a0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b064616638346166666363363834616665a46e6f6465ae646f7562742e67656e6572617465a57374616765ae646f7562742e67656e6572617465a4746f6f6caf67656e65726174655f616e73776572a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a66368756e6b7304ae6f75747075745f73756d6d61727982a36c656ecd0257a96369746174696f6e7301a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec801280594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b030356239616662616166366134613330a46e6f6465ae646f7562742e76616c6964617465a57374616765ae646f7562742e76616c6964617465a4746f6f6caf76616c69646174655f616e73776572a870726f7669646572c0af72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981aa616e737765725f6c656ecd0257ae6f75747075745f73756d6d61727981ac67617465735f70617373656405a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6e	1792018147948
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	8d8db099-746d-7a27-33c8-e92c49139573	tool_calls	msgpack	\\x00	1792018147948
doubt_thread_test_002		1f1c8217-6f31-673c-8003-5d4532aaf205	b75ff29b-aa91-4c8c-656c-eb95b349c2a5	query	msgpack	\\xb7576861742069732070686f746f73796e7468657369733f	1792018148038
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	8d8db099-746d-7a27-33c8-e92c49139573	started_ms	msgpack	\\xcf000001a13c9aea5e	1792018147948
doubt_thread_test_002		1f1c8217-6f31-673c-8003-5d4532aaf205	b75ff29b-aa91-4c8c-656c-eb95b349c2a5	learner_input	msgpack	\\xb7576861742069732070686f746f73796e7468657369733f	1792018148038
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	8d8db099-746d-7a27-33c8-e92c49139573	decision_id	msgpack	\\xb5646f7562745f7468726561645f746573745f303032	1792018147948
doubt_thread_test_002		1f1c8217-6f31-673c-8003-5d4532aaf205	b75ff29b-aa91-4c8c-656c-eb95b349c2a5	translated_query	null	\\x	1792018148038
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	8d8db099-746d-7a27-33c8-e92c49139573	error	null	\\x	1792018147948
doubt_thread_test_002		1f1c8217-6f31-673c-8003-5d4532aaf205	b75ff29b-aa91-4c8c-656c-eb95b349c2a5	used_translation_tool	msgpack	\\xc3	1792018148038
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	8d8db099-746d-7a27-33c8-e92c49139573	retry_count	msgpack	\\x00	1792018147948
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	8d8db099-746d-7a27-33c8-e92c49139573	validation_results	msgpack	\\x80	1792018147948
doubt_thread_test_002		1f1c8217-6f31-673c-8003-5d4532aaf205	b75ff29b-aa91-4c8c-656c-eb95b349c2a5	retrieval	msgpack	\\xc81e0e0594b26170702e646f6d61696e2e736368656d6173af526574726965766564526573756c7484a66368756e6b739487a86368756e6b5f6964b36368756e6b5f636830315f63303030325f3031aa636f6e636570745f6964a56330303032aa636861707465725f6964a56368303031a7746578745f6f72da06c2e0ac98e0aca8e0aca4e0ad8de0adb1202864656e736974792920e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0ad8ce0aca3e0acb8e0acbf20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac8fe0ac95e0ac9520e0ac86e0ad9fe0aca4e0aca8e0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1e0acb020e0acaae0acb0e0acbfe0acaee0acbee0aca3e0a5a420e0ac8fe0acb9e0acbee0ac95e0ad8120e0ac97e0acbee0aca3e0acbfe0aca4e0acbfe0ac9520e0acade0acbee0acace0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1203d20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1202f20e0ac86e0ad9fe0aca4e0aca8202844656e73697479203d204d617373202f20566f6c756d652920e0acace0ad8be0acb2e0acbf20e0acaae0ad8de0acb0e0ac95e0acbee0acb620e0ac95e0acb0e0acbee0acafe0acbee0ac8f2c20e0acafe0acbee0acb9e0acbee0acb020e0acb8e0ac99e0ad8de0ac95e0ad87e0aca420e0acb9e0ad87e0ac89e0ac9be0acbf20cf812028e0acb0e0ad8b2920e0ac95e0acbfe0acaee0ad8de0acace0acbe2064203d204d202f2056e0a5a420e0ac86e0aca8e0ad8de0aca4e0acb0e0ad8de0ac9ce0acbee0aca4e0ad80e0ad9f20e0acaee0acbee0aca8e0ac95202853492920e0acaae0aca6e0ad8de0aca7e0aca4e0acbfe0acb0e0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1e0acb020e0ac8fe0ac95e0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0acbfe0acb2e0ad8be0ac97e0ad8de0acb0e0acbee0acae20e0acaae0ad8de0acb0e0aca4e0acbf20e0ac98e0aca820e0acaee0acbfe0ac9fe0acb020286b672f6dc2b329e0a5a420e0acb8e0acbee0aca7e0acbee0acb0e0aca3e0aca4e0ac8320e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac85e0aca7e0acbfe0ac9520e0aca5e0acbee0ac8f2c20e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaee0aca7e0ad8de0ad9fe0acae20e0ac8fe0acace0ac8220e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac95e0acaee0ad8d20e0aca5e0acbee0ac8fe0a5a420e0ac89e0aca6e0acbee0acb9e0acb0e0aca320e0acb8e0ad8de0adb1e0acb0e0ad82e0acaa2c20e0acb2e0ad81e0acb9e0acbee0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0ac95e0acbee0aca020e0aca4e0ad81e0acb3e0aca8e0acbee0acb0e0ad8720e0acace0acb9e0ad81e0aca420e0ac85e0aca7e0acbfe0ac952c20e0ac95e0acbee0acb0e0aca320e0acb2e0ad81e0acb9e0acbee0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acaae0acb0e0acaee0acbee0aca3e0ad81e0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0ac85e0aca4e0acbf20e0aca8e0acbfe0acace0acbfe0aca1e0acbc20e0acade0acbee0acace0ad8720e0acb8e0ac9ce0ad8de0ac9ce0acbfe0aca420e0acb9e0ad8be0ac8720e0acb0e0acb9e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbfe0a5a420e0adaa20e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0acace0acbfe0acb6e0ad81e0aca6e0ad8de0aca720e0ac9ce0acb3e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaae0ad8de0acb0e0acbee0ad9f20e0ada7e0ada6e0ada6e0ada6206b672f6dc2b32028e0acace0acbe20e0ada720672f636dc2b32920e0acb9e0ad8be0ac87e0aca5e0acbee0ac8fe0a5a420e0ac95e0ad8ce0aca3e0acb8e0acbf20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0aca4e0acbee0acb020e0ac85e0aca3e0ad81e0ac97e0ad81e0aca1e0acbce0acbfe0ac95e0acb020e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb120e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0ad8020e0aca6e0ad82e0acb0e0aca4e0acbe20e0ac89e0acaae0acb0e0ad8720e0aca8e0acbfe0acb0e0ad8de0acade0acb020e0ac95e0acb0e0acbfe0aca5e0acbee0ac8fe0a5a4aa736f757263655f726566aa6368303120c2a7312e33a573636f7265cb3ff0000000000000ad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030315f3032aa636f6e636570745f6964a56330303031aa636861707465725f6964a56368303031a7746578745f6f72da06f3e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0aca4e0acbfe0aca8e0ad8be0ac9fe0acbf20e0ac85e0acace0acb8e0ad8de0aca5e0acbee0acb020e0acade0acbfe0aca8e0ad8de0aca820e0acade0acbfe0aca8e0ad8de0aca820e0acade0ad8ce0aca4e0acbfe0ac9520e0aca7e0acb0e0ad8de0acae20e0acb0e0acb9e0acbfe0ac9be0acbfe0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020286669786564207368617065292c20e0acb8e0ad8de0acaae0acb7e0ad8de0ac9f20e0acb8e0ad80e0acaee0acbee0acb0e0ad87e0ac96e0acbe20e0ac8fe0acace0ac8220e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ad9fe0aca4e0aca82028666978656420766f6c756d652920e0aca5e0acbee0ac8fe0a5a420e0ac8fe0acb9e0acbe20e0acb8e0acb9e0ac9ce0acb0e0ad8720e0acb8e0ac99e0ad8de0ac95e0ad81e0ac9ae0acbfe0aca42028636f6d707265737369626c652920e0acb9e0ad8be0ac87e0acaae0acbee0acb0e0ad8720e0aca8e0acbee0acb9e0acbfe0ac81e0a5a420e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac95e0ad8ce0aca3e0acb8e0acbf20e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020e0aca8e0aca5e0acbee0ac8f2c20e0ac95e0acbfe0aca8e0ad8de0aca4e0ad8120e0ac8fe0acb9e0acbee0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ad9fe0aca4e0aca820e0aca5e0acbee0ac8fe0a5a420e0aca4e0acb0e0acb3e0ac95e0ad8120e0acafe0ad87e0ac89e0ac8120e0acaae0acbee0aca4e0ad8de0acb0e0acb0e0ad8720e0acb0e0ac96e0acbee0acafe0acbee0ac8f2c20e0aca4e0acbee0acb9e0acbe20e0acb8e0ad87e0acb9e0acbf20e0acaae0acbee0aca4e0ad8de0acb0e0acb020e0ac86e0ac95e0acbee0acb020e0aca7e0acbee0acb0e0aca320e0ac95e0acb0e0ad87e0a5a420e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac95e0ad8ce0aca3e0acb8e0acbf20e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0ac86e0ac95e0acbee0acb020e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac86e0ad9fe0aca4e0aca820e0aca8e0aca5e0acbee0ac8f3b20e0ac8fe0acb9e0acbe20e0ac89e0acaae0acb2e0acace0ad8de0aca720e0acb8e0acaee0acb8e0ad8de0aca420e0acb8e0ad8de0aca5e0acbee0aca8e0ac95e0ad8120e0acaae0ad82e0acb0e0ad8de0aca3e0ad8de0aca320e0ac95e0acb0e0acbfe0aca6e0acbfe0ac8fe0a5a420e0ac97e0ad8de0ad9fe0acbee0acb8e0acb020e0acb8e0ac99e0ad8de0ac95e0ad8be0ac9ae0aca8e0acb6e0ad80e0acb3e0aca4e0acbe2028636f6d70726573736962696c6974792920e0acb8e0acb0e0ad8de0acace0acbee0aca7e0acbfe0ac9520e0acb9e0ad8be0ac87e0aca5e0acbfe0acace0acbee0acb0e0ad8120e0ac8fe0acb9e0acbee0ac95e0ad8120e0ac89e0ac9ae0ad8de0ac9a20e0ac9ae0acbee0acaae0acb0e0ad8720e0acb8e0acbfe0acb2e0acbfe0aca3e0ad8de0aca1e0acb020e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0acade0acb0e0ad8de0aca4e0ad8de0aca4e0acbf20e0ac95e0acb0e0acbee0acafe0acbee0ac87e0acaae0acbee0acb0e0ad872c20e0acafe0ad87e0acaae0acb0e0acbfe0ac95e0acbf20e0ac86e0acae20e0ac98e0acb0e0ad8720e0acace0ad8de0ad9fe0acace0acb9e0ad83e0aca420e0acb9e0ad87e0ac89e0aca5e0acbfe0acace0acbe20e0ac8fe0acb2e0acaae0acbfe0ac9ce0acbf20284c50472920e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac85e0ac95e0ad8de0acb8e0acbfe0ac9ce0ad87e0aca820e0acb8e0acbfe0acb2e0acbfe0aca3e0ad8de0aca1e0acb0e0a5a420e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0ac97e0aca4e0acbfe0ac9c20e0acb6e0ac95e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0ac86e0aca8e0ad8de0aca4e0ac83e0ac95e0aca3e0acbfe0ac95e0acbe20e0acb8e0ad8de0aca5e0acbee0aca820e0acb9e0acbfe0ac8120e0ac8fe0acb9e0acbf20e0acb8e0acaee0acb8e0ad8de0aca420e0acaae0acbee0acb0e0ad8de0aca5e0ac95e0ad8de0ad9fe0acb020e0acaee0ad82e0acb320e0ac95e0acbee0acb0e0aca320e0ac85e0ac9fe0ad87e0a5a4aa736f757263655f726566aa6368303120c2a7312e32a573636f7265cb3fdd17fa84aa97caad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030335f3031aa636f6e636570745f6964a56330303033aa636861707465725f6964a56368303031a7746578745f6f72da06e2e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbe20e0ac95e0acbfe0acaee0ad8de0acace0acbe20e0ac9ae0acbee0acaae0acb020e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0ac98e0ac9fe0acbee0ac8720e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac85e0acace0acb8e0ad8de0aca5e0acbe20e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0ac95e0acb0e0acbee0acafe0acbee0ac87e0acaae0acbee0acb0e0ad87e0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0ac95e0ad8120e0ac97e0acb0e0acae20e0ac95e0acb2e0ad8720e0aca4e0acbee0acb020e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0ac97e0aca4e0acbfe0ac9c20e0acb6e0ac95e0ad8de0aca4e0acbf20e0acace0aca2e0acbce0acbfe0acafe0acbee0ac8f20e0ac8fe0acace0ac8220e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0ac8fe0acb9e0acbe20e0aca4e0acb0e0acb3e0acbfe0acace0acbee0ac95e0ad8120e0acb2e0acbee0ac97e0ad87e0a5a420e0acafe0ad87e0ac89e0ac8120e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0acace0acbee0ad9fe0ad81e0acaee0aca3e0ad8de0aca1e0acb3e0ad80e0ad9f20e0ac9ae0acbee0acaae0acb0e0ad8720e0ac8fe0ac9520e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0aca4e0acb0e0acb3e0acb0e0ad8720e0acaae0acb0e0acbfe0aca3e0aca420e0acb9e0ad81e0ac8f2c20e0aca4e0acbee0acb9e0acbee0ac95e0ad8120e0aca4e0acbee0acb020e0ac97e0acb3e0aca8e0acbee0ac99e0ad8de0ac9520286d656c74696e6720706f696e742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a420e0acace0acb0e0acabe0acb020e0ac97e0acb3e0aca8e0acbee0ac99e0ad8de0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ada620e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0acace0acbe20e0ada8e0adade0ada920e0ac95e0ad87e0acb2e0acade0acbfe0aca8e0a5a420e0acb8e0ad87e0acb9e0acbfe0acaae0acb0e0acbf20e0acafe0ad87e0ac89e0ac8120e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acabe0ad81e0ac9fe0acbf20e0acace0acbee0acb7e0ad8de0acaae0acb0e0ad8720e0acaae0acb0e0acbfe0aca3e0aca420e0acb9e0ad81e0ac8f2c20e0aca4e0acbee0acb9e0acbee0ac95e0ad8120e0acb8e0ad8de0acabe0ad81e0ac9fe0aca8e0acbee0ac99e0ad8de0ac952028626f696c696e6720706f696e742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a420e0ac9ce0acb3e0acb020e0acb8e0ad8de0acabe0ad81e0ac9fe0aca8e0acbee0ac99e0ad8de0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ada7e0ada6e0ada620e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0acace0acbe20e0ada9e0adade0ada920e0ac95e0ad87e0acb2e0acade0acbfe0aca8e0a5a420e0ac85e0acace0acb8e0ad8de0aca5e0acbe20e0acaae0acb0e0acbfe0acace0acb0e0ad8de0aca4e0ad8de0aca4e0aca820e0acb8e0acaee0ad9fe0acb0e0ad8720e0acafe0ad8be0ac9720e0ac95e0acb0e0acbee0acafe0acbee0ac89e0aca5e0acbfe0acace0acbe20e0aca4e0acbee0acaa20e0acb6e0ac95e0ad8de0aca4e0acbf20e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbe20e0aca820e0acace0aca2e0acbce0acbee0ac8720e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb3e0ac95e0ad8120e0acade0acbee0ac99e0ad8de0ac97e0acbfe0acace0acbee0acb0e0ad8720e0acace0ad8de0ad9fe0acace0acb9e0ad83e0aca420e0acb9e0ad81e0ac8f2c20e0acafe0acbee0acb9e0acbee0ac95e0ad8120e0ac97e0ad81e0acaae0ad8de0aca4e0aca4e0acbee0acaa20286c6174656e7420686561742920e0ac95e0ad81e0acb9e0acbee0acafe0acbee0ac8fe0a5a4aa736f757263655f726566aa6368303120c2a7312e34a573636f7265cb3fdd17fa84aa97caad6d6174636865645f7465726d739087a86368756e6b5f6964b36368756e6b5f636830315f63303030315f3031aa636f6e636570745f6964a56330303031aa636861707465725f6964a56368303031a7746578745f6f72da0702e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac86e0acae20e0acaae0acb0e0acbfe0acace0ad87e0acb6e0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acaae0ad8de0acb0e0aca4e0ad8de0ad9fe0ad87e0ac9520e0acace0acb8e0ad8de0aca4e0ad8120e0acafe0acbee0acb9e0acbee0acb020e0ac8fe0ac9520e0aca8e0acbfe0acb0e0ad8de0aca6e0ad8de0aca6e0acbfe0acb7e0ad8de0ac9f20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb120286d6173732920e0aca5e0acbee0ac8f20e0ac8fe0acace0ac8220e0acafe0acbee0acb9e0acbe20e0ac95e0acbfe0ac9be0acbf20e0acb8e0ad8de0aca5e0acbee0aca820e0acace0acbe20e0ac86e0ad9fe0aca4e0aca82028766f6c756d652920e0ac85e0aca7e0acbfe0ac95e0acbee0acb020e0ac95e0acb0e0ad87e0a5a420e0acaae0ad8de0acb0e0ac95e0ad83e0aca4e0acbfe0acb0e0ad8720e0acaae0aca6e0acbee0acb0e0ad8de0aca520e0acaee0ad81e0ac96e0ad8de0ad9fe0aca4e0ac8320e0aca4e0acbfe0aca8e0ad8be0ac9fe0acbf20e0acade0ad8ce0aca4e0acbfe0ac9520e0acb8e0ad8de0aca5e0acbfe0aca4e0acbfe0acb0e0ad8720e0aca6e0ad87e0ac96e0acbee0acafe0acbee0ac8f3a20e0ac95e0aca0e0acbfe0aca82028736f6c6964292c20e0aca4e0acb0e0acb320286c69717569642920e0ac8fe0acace0ac8220e0ac97e0ad8de0ad9fe0acbee0acb8202867617329e0a5a420e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0ac85e0aca4e0ad8de0ad9fe0aca8e0ad8de0aca420e0aca8e0acbfe0acace0acbfe0aca1e0acbc20e0acade0acbee0acace0acb0e0ad8720e0acb8e0ac9ce0ad8de0ac9ce0acbfe0aca420e0acb9e0ad8be0ac8720e0acb0e0acb9e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0ac86e0aca8e0ad8de0aca4e0ac83e0ac95e0aca3e0acbfe0ac95e0acbe20e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb32028696e7465726d6f6c6563756c617220666f7263652920e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac85e0aca7e0acbfe0ac9520e0acaae0ad8de0acb0e0acace0acb320e0aca5e0acbee0ac8fe0a5a420e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0ac95e0acbfe0ac9be0acbf20e0acabe0acbee0ac99e0ad8de0ac95e0acbe20e0acb8e0ad8de0aca5e0acbee0aca820e0aca5e0acbee0ac8f20e0ac8fe0acace0ac8220e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb320e0ac95e0aca0e0acbfe0aca820e0aca4e0ad81e0acb3e0aca8e0acbee0acb0e0ad8720e0ac95e0acaee0ad8d20e0aca5e0acbee0ac8f2c20e0acafe0acbee0acb9e0acbe20e0acabe0acb3e0acb0e0ad8720e0acb8e0ad87e0acaee0acbee0aca8e0ad8720e0acaae0ad8de0acb0e0acace0acbee0acb9e0acbfe0aca420e0acb9e0ad8be0ac87e0acaae0acbee0acb0e0aca8e0ad8de0aca4e0acbfe0a5a420e0ac85e0aca8e0ad8de0ad9fe0acaae0ac95e0ad8de0acb7e0acb0e0ad872c20e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb0e0ad8720e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0acaae0acb0e0acb8e0ad8de0acaae0acb0e0aca0e0acbee0acb0e0ad8120e0acace0acb9e0ad81e0aca420e0aca6e0ad82e0acb0e0acb0e0ad8720e0aca5e0acbee0ac86e0aca8e0ad8de0aca4e0acbf20e0ac8fe0acace0ac8220e0acb8e0ad87e0acaee0acbee0aca8e0ac99e0ad8de0ac9520e0acaee0aca7e0ad8de0ad9fe0acb0e0ad8720e0ac86e0ac95e0acb0e0ad8de0acb7e0aca320e0acace0acb320e0aca8e0ac97e0aca3e0ad8de0ad9f20e0aca5e0acbee0ac8fe0a5a420e0aca4e0ad87e0aca3e0ad8120e0ac97e0ad8de0ad9fe0acbee0acb8e0acb020e0ac95e0aca3e0acbfe0ac95e0acbee0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0acb8e0acaee0acb8e0ad8de0aca420e0aca6e0acbfe0ac97e0acb0e0ad8720e0aca6e0ad8de0acb0e0ad81e0aca420e0ac9320e0acaee0ad81e0ac95e0ad8de0aca420e0acade0acbee0acace0acb0e0ad8720e0ac97e0aca4e0acbf20e0ac95e0acb0e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbfe0a5a4aa736f757263655f726566aa6368303120c2a7312e32a573636f7265cb0000000000000000ad6d6174636865645f7465726d7390a870726f7669646572ac6c6f63616c5f687962726964a86d6f64656c5f6964a46d6f636baa636f6e666964656e6365cb3ff0000000000000b36d6f64656c5f76616c69646174655f6a736f6e	1792018148038
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	8d8db099-746d-7a27-33c8-e92c49139573	fallback_used	msgpack	\\xc2	1792018147948
doubt_thread_test_002		1f1c8217-6f31-673c-8003-5d4532aaf205	b75ff29b-aa91-4c8c-656c-eb95b349c2a5	answer	msgpack	\\xc806750594b26170702e646f6d61696e2e736368656d6173af47656e657261746564416e7377657286a7746578745f6f72da05bfe0ac98e0aca8e0aca4e0ad8de0adb1202864656e736974792920e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0ad8ce0aca3e0acb8e0acbf20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac8fe0ac95e0ac9520e0ac86e0ad9fe0aca4e0aca8e0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1e0acb020e0acaae0acb0e0acbfe0acaee0acbee0aca3e0a5a420e0ac8fe0acb9e0acbee0ac95e0ad8120e0ac97e0acbee0aca3e0acbfe0aca4e0acbfe0ac9520e0acade0acbee0acace0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1203d20e0acace0acb8e0ad8de0aca4e0ad81e0aca4e0ad8de0adb1202f20e0ac86e0ad9fe0aca4e0aca8202844656e73697479203d204d617373202f20566f6c756d652920e0acace0ad8be0acb2e0acbf20e0acaae0ad8de0acb0e0ac95e0acbee0acb620e0ac95e0acb0e0acbee0acafe0acbee0ac8f2c20e0acafe0acbee0acb9e0acbee0acb020e0acb8e0ac99e0ad8de0ac95e0ad87e0aca420e0acb9e0ad87e0ac89e0ac9be0acbf20cf812028e0acb0e0ad8b2920e0ac95e0acbfe0acaee0ad8de0acace0acbe2064203d204d202f2056e0a5a420e0ac86e0aca8e0ad8de0aca4e0acb0e0ad8de0ac9ce0acbee0aca4e0ad80e0ad9f20e0acaee0acbee0aca8e0ac95202853492920e0acaae0aca6e0ad8de0aca7e0aca4e0acbfe0acb0e0ad8720e0ac98e0aca8e0aca4e0ad8de0adb1e0acb020e0ac8fe0ac95e0ac9520e0acb9e0ad87e0ac89e0ac9be0acbf20e0ac95e0acbfe0acb2e0ad8be0ac97e0ad8de0acb0e0acbee0acae20e0acaae0ad8de0acb0e0aca4e0acbf20e0ac98e0aca820e0acaee0acbfe0ac9fe0acb020286b672f6dc2b329e0a5a420e0acb8e0acbee0aca7e0acbee0acb0e0aca3e0aca4e0ac8320e0ac95e0aca0e0acbfe0aca820e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac85e0aca7e0acbfe0ac9520e0aca5e0acbee0ac8f2c20e0aca4e0acb0e0acb320e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaee0aca7e0ad8de0ad9fe0acae20e0ac8fe0acace0ac8220e0ac97e0ad8de0ad9fe0acbee0acb8e0ad80e0ad9f20e0acaae0aca6e0acbee0acb0e0ad8de0aca5e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acb8e0acace0ad81e0aca0e0acbee0acb0e0ad8120e0ac95e0acaee0ad8d20e0aca5e0acbee0ac8fe0a5a420e0ac89e0aca6e0acbee0acb9e0acb0e0aca320e0acb8e0ad8de0adb1e0acb0e0ad82e0acaa2c20e0acb2e0ad81e0acb9e0acbee0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0ac95e0acbee0aca020e0aca4e0ad81e0acb3e0aca8e0acbee0acb0e0ad8720e0acace0acb9e0ad81e0aca420e0ac85e0aca7e0acbfe0ac952c20e0ac95e0acbee0acb0e0aca320e0acb2e0ad81e0acb9e0acbee0acb0e0ad8720e0aca5e0acbfe0acace0acbe20e0acaae0acb0e0acaee0acbee0aca3e0ad81e0ac97e0ad81e0aca1e0acbce0acbfe0ac9520e0ac85e0aca4e0acbf20e0aca8e0acbfe0acace0acbfe0aca1e0acbc20e0acade0acbee0acace0ad8720e0acb8e0ac9ce0ad8de0ac9ce0acbfe0aca420e0acb9e0ad8be0ac8720e0acb0e0acb9e0acbfe0aca5e0acbee0aca8e0ad8de0aca4e0acbfe0a5a420e0adaa20e0aca1e0acbfe0ac97e0ad8de0acb0e0ad8020e0acb8e0ad87e0acb2e0acb8e0acbfe0ad9fe0acb820e0aca4e0acbee0acaae0acaee0acbee0aca4e0ad8de0acb0e0acbee0acb0e0ad8720e0acace0acbfe0acb6e0ad81e0aca6e0ad8de0aca720e0ac9ce0acb3e0acb020e0ac98e0aca8e0aca4e0ad8de0adb120e0acaae0ad8de0acb0e0acbee0ad9f20e0ada7e0ada6e0ada6e0ada6206b672f6dc2b32028e0acace0acbe20e0ada720672f636dc2b32920e0acb9e0ad8be0ac87e0aca5e0acbee0ac8fe0a5a4a96369746174696f6e7391b36368756e6b5f636830315f63303030325f3031ac636861707465725f7265667391a56368303031aa636f6e666964656e6365cb3fe6666666666666aa70726f76656e616e6365aa65787472616374697665b362617369635f616e737765725f737461747573c0b36d6f64656c5f76616c69646174655f6a736f6e	1792018148038
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	8d8db099-746d-7a27-33c8-e92c49139573	generation_error	null	\\x	1792018147948
doubt_thread_test_002		1f1c8217-6f31-673c-8003-5d4532aaf205	b75ff29b-aa91-4c8c-656c-eb95b349c2a5	trace	msgpack	\\x94c801d70594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b063376462336262343063343034623731a46e6f6465af646f7562742e7472616e736c617465a57374616765af646f7562742e7472616e736c617465a4746f6f6cae7472616e736c6174655f74657874a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a866616c6c6261636baa6572726f725f636f6465ab554e415641494c41424c45ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727981a6726561736f6ed9a75452414e534c4154494f4e5f50524f56494445523d6d6f636b20e2809420736574205452414e534c4154494f4e5f50524f56494445523d68665f6c6f63616c2028616e642048465f544f4b454e20666f722074686520676174656420496e6469635472616e7332207265706f73292e20546865206f66666c696e65206c6561726e696e67207061746820646f6573206e6f742072657175697265207472616e736c6174696f6e2ea87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8013d0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b033363431333233373264663534306135a46e6f6465ae646f7562742e7265747269657665a57374616765ae646f7562742e7265747269657665a4746f6f6caf72657472696576655f6368756e6b73a870726f7669646572ac6c6f63616c5f687962726964af72756c657365745f76657273696f6ec0a86d6f64656c5f6964a46d6f636ba6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7346a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a36c656e17ae6f75747075745f73756d6d61727982a66368756e6b7304aa636f6e666964656e6365cb3ff0000000000000a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec8012a0594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b064616638346166666363363834616665a46e6f6465ae646f7562742e67656e6572617465a57374616765ae646f7562742e67656e6572617465a4746f6f6caf67656e65726174655f616e73776572a870726f7669646572a46d6f636baf72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981a66368756e6b7304ae6f75747075745f73756d6d61727982a36c656ecd0257a96369746174696f6e7301a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6ec801280594b26170702e646f6d61696e2e736368656d6173a95472616365537465708fa7737465705f6964b030356239616662616166366134613330a46e6f6465ae646f7562742e76616c6964617465a57374616765ae646f7562742e76616c6964617465a4746f6f6caf76616c69646174655f616e73776572a870726f7669646572c0af72756c657365745f76657273696f6ec0a86d6f64656c5f6964c0a6737461747573a26f6baa6572726f725f636f6465c0ab6475726174696f6e5f6d7300a57265747279c0a866616c6c6261636bc0ad696e7075745f73756d6d61727981aa616e737765725f6c656ecd0257ae6f75747075745f73756d6d61727981ac67617465735f70617373656405a87265646163746564c3b36d6f64656c5f76616c69646174655f6a736f6e	1792018148038
doubt_thread_test_002		1f1c8217-6e64-6507-bfff-dd086da42433	8d8db099-746d-7a27-33c8-e92c49139573	branch:to:translate	null	\\x	1792018147948
doubt_thread_test_002		1f1c8217-6f31-673c-8003-5d4532aaf205	b75ff29b-aa91-4c8c-656c-eb95b349c2a5	tool_calls	msgpack	\\x03	1792018148038
doubt_thread_test_002		1f1c8217-6f31-673c-8003-5d4532aaf205	b75ff29b-aa91-4c8c-656c-eb95b349c2a5	started_ms	msgpack	\\xcf000001a13c9aea5e	1792018148038
doubt_thread_test_002		1f1c8217-6f31-673c-8003-5d4532aaf205	b75ff29b-aa91-4c8c-656c-eb95b349c2a5	decision_id	msgpack	\\xb5646f7562745f7468726561645f746573745f303032	1792018148038
doubt_thread_test_002		1f1c8217-6f31-673c-8003-5d4532aaf205	b75ff29b-aa91-4c8c-656c-eb95b349c2a5	error	null	\\x	1792018148038
doubt_thread_test_002		1f1c8217-6f31-673c-8003-5d4532aaf205	b75ff29b-aa91-4c8c-656c-eb95b349c2a5	retry_count	msgpack	\\x00	1792018148038
doubt_thread_test_002		1f1c8217-6f31-673c-8003-5d4532aaf205	b75ff29b-aa91-4c8c-656c-eb95b349c2a5	validation_results	msgpack	\\x84a26f6bc3ab6661696c65645f67617465c0ac67617465735f70617373656495a6736368656d61b1736f757263655f7265666572656e636573af6c616e67756167655f6c656e677468a6736166657479a967726f756e64696e67ab6f726465725f696e64657804	1792018148038
doubt_thread_test_002		1f1c8217-6f31-673c-8003-5d4532aaf205	b75ff29b-aa91-4c8c-656c-eb95b349c2a5	fallback_used	msgpack	\\xc2	1792018148038
doubt_thread_test_002		1f1c8217-6f31-673c-8003-5d4532aaf205	b75ff29b-aa91-4c8c-656c-eb95b349c2a5	generation_error	null	\\x	1792018148038
\.


--
-- Data for Name: learner_bloom_progress; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.learner_bloom_progress (learner_id, concept_id, bloom_level, p_bp, bkt_version, band, attempts, correct, last_event_seq) FROM stdin;
\.


--
-- Data for Name: learner_devices; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.learner_devices (learner_id, device_id, status, first_seen_at, last_active_at) FROM stdin;
\.


--
-- Data for Name: learner_events; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.learner_events (device_id, learner_id, seq, event_id, client_ts, event_type, concept_id, chapter_id, question_id, payload_json, status, effect, reason, received_at, server_seq) FROM stdin;
\.


--
-- Data for Name: learner_profiles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.learner_profiles (learner_id, display_label, locale, grade, subject, pin_hash, created_at, active_device_id) FROM stdin;
\.


--
-- Data for Name: learner_progress; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.learner_progress (learner_id, concept_id, p_bp, attempts, correct, last_seen_at, last_event_seq, bkt_version) FROM stdin;
\.


--
-- Data for Name: learning_sessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.learning_sessions (session_id, learner_id, device_id, started_at, ended_at, last_decision_id) FROM stdin;
\.


--
-- Data for Name: pack_chapters; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pack_chapters (pack_id, version, chapter_id) FROM stdin;
\.


--
-- Data for Name: pack_manifests; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pack_manifests (pack_id, version, title_or, language, byte_size, checksum_sha256, min_app_version, licence, source_refs_json, created_at, chapters_json) FROM stdin;
\.


--
-- Data for Name: packs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.packs (pack_id, version, content_version, language, byte_size, checksum_sha256, min_app_version, licence, source_refs_json, created_at, published) FROM stdin;
\.


--
-- Data for Name: questions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.questions (question_id, concept_id, chapter_id, text_or, options_json, correct_answer, explanation_or, difficulty, bloom_level, misconception_tag, status, revision, answer_key_hash, source_ref) FROM stdin;
\.


--
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.refresh_tokens (id, device_id, token_hash, issued_at, expires_at, used_at, revoked) FROM stdin;
\.


--
-- Data for Name: sync_cursors; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sync_cursors (device_id, learner_id, last_acked_seq, last_server_seq, last_acked_at) FROM stdin;
\.


--
-- Name: glossary_glossary_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.glossary_glossary_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: auth_challenges auth_challenges_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_challenges
    ADD CONSTRAINT auth_challenges_pkey PRIMARY KEY (nonce);


--
-- Name: chapters chapters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chapters
    ADD CONSTRAINT chapters_pkey PRIMARY KEY (chapter_id);


--
-- Name: chunks chunks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chunks
    ADD CONSTRAINT chunks_pkey PRIMARY KEY (chunk_id);


--
-- Name: concepts concepts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.concepts
    ADD CONSTRAINT concepts_pkey PRIMARY KEY (concept_id);


--
-- Name: dead_letter_events dead_letter_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dead_letter_events
    ADD CONSTRAINT dead_letter_events_pkey PRIMARY KEY (event_id);


--
-- Name: decision_traces decision_traces_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.decision_traces
    ADD CONSTRAINT decision_traces_pkey PRIMARY KEY (decision_id, step_ordinal);


--
-- Name: decisions decisions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.decisions
    ADD CONSTRAINT decisions_pkey PRIMARY KEY (decision_id);


--
-- Name: devices devices_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_pkey PRIMARY KEY (device_id);


--
-- Name: generation_records generation_records_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.generation_records
    ADD CONSTRAINT generation_records_pkey PRIMARY KEY (record_id);


--
-- Name: glossary glossary_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.glossary
    ADD CONSTRAINT glossary_pkey PRIMARY KEY (glossary_id);


--
-- Name: glossary glossary_term_or_term_en_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.glossary
    ADD CONSTRAINT glossary_term_or_term_en_key UNIQUE (term_or, term_en);


--
-- Name: installed_packs installed_packs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.installed_packs
    ADD CONSTRAINT installed_packs_pkey PRIMARY KEY (device_id, pack_id);


--
-- Name: jobs jobs_dedupe_key_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_dedupe_key_key UNIQUE (dedupe_key);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (job_id);


--
-- Name: langgraph_checkpoints langgraph_checkpoints_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.langgraph_checkpoints
    ADD CONSTRAINT langgraph_checkpoints_pkey PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id);


--
-- Name: langgraph_writes langgraph_writes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.langgraph_writes
    ADD CONSTRAINT langgraph_writes_pkey PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, channel);


--
-- Name: learner_bloom_progress learner_bloom_progress_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learner_bloom_progress
    ADD CONSTRAINT learner_bloom_progress_pkey PRIMARY KEY (learner_id, concept_id, bloom_level);


--
-- Name: learner_devices learner_devices_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learner_devices
    ADD CONSTRAINT learner_devices_pkey PRIMARY KEY (learner_id, device_id);


--
-- Name: learner_events learner_events_event_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learner_events
    ADD CONSTRAINT learner_events_event_id_key UNIQUE (event_id);


--
-- Name: learner_events learner_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learner_events
    ADD CONSTRAINT learner_events_pkey PRIMARY KEY (device_id, seq);


--
-- Name: learner_profiles learner_profiles_active_device_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learner_profiles
    ADD CONSTRAINT learner_profiles_active_device_id_key UNIQUE (active_device_id);


--
-- Name: learner_profiles learner_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learner_profiles
    ADD CONSTRAINT learner_profiles_pkey PRIMARY KEY (learner_id);


--
-- Name: learner_progress learner_progress_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learner_progress
    ADD CONSTRAINT learner_progress_pkey PRIMARY KEY (learner_id, concept_id);


--
-- Name: learning_sessions learning_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learning_sessions
    ADD CONSTRAINT learning_sessions_pkey PRIMARY KEY (session_id);


--
-- Name: pack_chapters pack_chapters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pack_chapters
    ADD CONSTRAINT pack_chapters_pkey PRIMARY KEY (pack_id, version, chapter_id);


--
-- Name: pack_manifests pack_manifests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pack_manifests
    ADD CONSTRAINT pack_manifests_pkey PRIMARY KEY (pack_id, version);


--
-- Name: packs packs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.packs
    ADD CONSTRAINT packs_pkey PRIMARY KEY (pack_id, version);


--
-- Name: questions questions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (question_id);


--
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- Name: sync_cursors sync_cursors_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sync_cursors
    ADD CONSTRAINT sync_cursors_pkey PRIMARY KEY (device_id, learner_id);


--
-- Name: idx_checkpoints_thread; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_checkpoints_thread ON public.langgraph_checkpoints USING btree (thread_id, checkpoint_ns, created_at);


--
-- Name: idx_device_tokens_hash; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_device_tokens_hash ON public.device_tokens USING btree (token_hash, revoked, expires_at);


--
-- Name: idx_events_learner_seq; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_events_learner_seq ON public.learner_events USING btree (learner_id, server_seq);


--
-- Name: idx_jobs_lease_expires; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_jobs_lease_expires ON public.jobs USING btree (status, lease_expires_at);


--
-- Name: idx_jobs_status_next_run; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_jobs_status_next_run ON public.jobs USING btree (status, next_run_at);


--
-- Name: idx_refresh_tokens_hash; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_refresh_tokens_hash ON public.refresh_tokens USING btree (token_hash, revoked, expires_at);


--
-- Name: auth_challenges auth_challenges_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_challenges
    ADD CONSTRAINT auth_challenges_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(device_id) ON DELETE CASCADE;


--
-- Name: chunks chunks_concept_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chunks
    ADD CONSTRAINT chunks_concept_id_fkey FOREIGN KEY (concept_id) REFERENCES public.concepts(concept_id) ON DELETE CASCADE;


--
-- Name: concepts concepts_chapter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.concepts
    ADD CONSTRAINT concepts_chapter_id_fkey FOREIGN KEY (chapter_id) REFERENCES public.chapters(chapter_id) ON DELETE CASCADE;


--
-- Name: device_tokens device_tokens_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_tokens
    ADD CONSTRAINT device_tokens_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(device_id) ON DELETE CASCADE;


--
-- Name: generation_records generation_records_decision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.generation_records
    ADD CONSTRAINT generation_records_decision_id_fkey FOREIGN KEY (decision_id) REFERENCES public.decisions(decision_id) ON DELETE CASCADE;


--
-- Name: learner_devices learner_devices_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learner_devices
    ADD CONSTRAINT learner_devices_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(device_id) ON DELETE CASCADE;


--
-- Name: learner_devices learner_devices_learner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learner_devices
    ADD CONSTRAINT learner_devices_learner_id_fkey FOREIGN KEY (learner_id) REFERENCES public.learner_profiles(learner_id) ON DELETE CASCADE;


--
-- Name: learner_events learner_events_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learner_events
    ADD CONSTRAINT learner_events_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(device_id) ON DELETE CASCADE;


--
-- Name: learner_events learner_events_learner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learner_events
    ADD CONSTRAINT learner_events_learner_id_fkey FOREIGN KEY (learner_id) REFERENCES public.learner_profiles(learner_id) ON DELETE CASCADE;


--
-- Name: learner_profiles learner_profiles_active_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learner_profiles
    ADD CONSTRAINT learner_profiles_active_device_id_fkey FOREIGN KEY (active_device_id) REFERENCES public.devices(device_id) ON DELETE SET NULL;


--
-- Name: questions questions_concept_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_concept_id_fkey FOREIGN KEY (concept_id) REFERENCES public.concepts(concept_id) ON DELETE CASCADE;


--
-- Name: refresh_tokens refresh_tokens_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(device_id) ON DELETE CASCADE;


--
-- Name: sync_cursors sync_cursors_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sync_cursors
    ADD CONSTRAINT sync_cursors_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(device_id) ON DELETE CASCADE;


--
-- Name: sync_cursors sync_cursors_learner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sync_cursors
    ADD CONSTRAINT sync_cursors_learner_id_fkey FOREIGN KEY (learner_id) REFERENCES public.learner_profiles(learner_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 9YtkHPebbrFuRaR6MEatePI5tRtFcnbD55cejMExULc5VGaaFe1cdBhVj1zbVM7

