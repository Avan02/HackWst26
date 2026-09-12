-- TutorMatch schema for TigerData (Postgres + TimescaleDB + pgvector).
-- Idempotent: safe to run repeatedly.

CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- gen_random_uuid()

/* ------------------------------------------------------------------ users */

CREATE TABLE IF NOT EXISTS users (
  auth_sub        text PRIMARY KEY,
  role            text NOT NULL DEFAULT 'student',
  name            text,
  email           text,
  avatar_url      text,
  wallet_address  text,
  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS learner_profiles (
  user_id           text PRIMARY KEY REFERENCES users(auth_sub) ON DELETE CASCADE,
  pace              text,
  goals             text,
  subjects          text[],
  -- The quiz answers themselves, keyed by question id. This is what matching
  -- scores against, so keep it readable: {"intake": "visual", "pace": "slow", ...}
  raw_answers       jsonb,
  profile_sentence  text,          -- human-readable summary, for debugging matches
  updated_at        timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tutor_profiles (
  user_id           text PRIMARY KEY REFERENCES users(auth_sub) ON DELETE CASCADE,
  bio               text,
  subjects          text[],
  -- How well this tutor suits each possible quiz answer, 0..1, shaped as
  -- {"intake": {"visual": 1.0, "verbal": 0.3, ...}, "pace": {...}, ...}
  -- Matching sums the tutor's affinity for whichever answers the student gave.
  style_affinity    jsonb,
  hourly_rate_sol   numeric(10,4),
  rating            numeric(3,2) DEFAULT 4.5
);

/* --------------------------------------------------------------- sessions */

CREATE TABLE IF NOT EXISTS sessions (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id     text REFERENCES users(auth_sub),
  tutor_id       text REFERENCES users(auth_sub),
  subject        text,
  mode           text NOT NULL DEFAULT 'video',
  status         text NOT NULL DEFAULT 'pending',
  room_url       text,
  recording_url  text,
  recording_key  text,           -- object key in Vultr Object Storage
  created_at     timestamptz NOT NULL DEFAULT now(),
  started_at     timestamptz,
  ended_at       timestamptz
);

CREATE TABLE IF NOT EXISTS payments (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id      uuid REFERENCES sessions(id) ON DELETE CASCADE,
  tx_signature    text UNIQUE NOT NULL,
  amount_lamports bigint,
  status          text NOT NULL DEFAULT 'pending',
  confirmed_at    timestamptz
);

CREATE TABLE IF NOT EXISTS session_notes (
  session_id    uuid PRIMARY KEY REFERENCES sessions(id) ON DELETE CASCADE,
  summary       text,
  key_moments   jsonb,           -- [{ tMs, title, why }]
  concepts      text[],
  action_items  text[],
  generated_at  timestamptz NOT NULL DEFAULT now()
);

/* ------------------------------------------------------------ hypertables */
-- These two are genuinely time-series, which is what makes TimescaleDB
-- load-bearing here rather than decorative.
--
-- NOTE: a hypertable's PRIMARY KEY / UNIQUE index must include the
-- partitioning column. That is why neither table has a plain `id PRIMARY KEY`.

CREATE TABLE IF NOT EXISTS transcript_segments (
  session_id  uuid NOT NULL,
  ts          timestamptz NOT NULL DEFAULT now(),
  start_ms    integer NOT NULL,
  end_ms      integer NOT NULL,
  speaker     text,
  text        text NOT NULL,
  embedding   vector(768)
);

CREATE TABLE IF NOT EXISTS messages (
  session_id  uuid NOT NULL,
  ts          timestamptz NOT NULL DEFAULT now(),
  sender_id   text,
  body        text NOT NULL
);

SELECT create_hypertable('transcript_segments', 'ts', if_not_exists => TRUE);
SELECT create_hypertable('messages',            'ts', if_not_exists => TRUE);

/* ----------------------------------------------------------------- indexes */

CREATE INDEX IF NOT EXISTS transcript_embedding_hnsw
  ON transcript_segments USING hnsw (embedding vector_cosine_ops);

-- Subject filtering uses the && array-overlap operator.
CREATE INDEX IF NOT EXISTS tutor_subjects_gin
  ON tutor_profiles USING gin (subjects);

CREATE INDEX IF NOT EXISTS transcript_session_ts
  ON transcript_segments (session_id, ts DESC);

CREATE INDEX IF NOT EXISTS messages_session_ts
  ON messages (session_id, ts DESC);

CREATE INDEX IF NOT EXISTS sessions_student
  ON sessions (student_id, created_at DESC);
