-- 0001_init.sql: Initial Economic Indicators Dashboard Schema

CREATE TABLE IF NOT EXISTS users (
  id            BIGSERIAL PRIMARY KEY,
  username      TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role          TEXT NOT NULL DEFAULT 'viewer',
  is_active     BOOLEAN NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
  id          BIGSERIAL PRIMARY KEY,
  user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash  TEXT NOT NULL UNIQUE,
  expires_at  TIMESTAMPTZ NOT NULL,
  revoked_at  TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS sources (
  id        TEXT PRIMARY KEY,
  name      TEXT NOT NULL,
  url       TEXT NOT NULL,
  is_nse    BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS observations (
  id           BIGSERIAL PRIMARY KEY,
  indicator    TEXT NOT NULL,
  series       TEXT NOT NULL,
  period       TEXT NOT NULL,
  period_start DATE,
  value        DOUBLE PRECISION,
  unit         TEXT NOT NULL,
  is_estimate  BOOLEAN NOT NULL DEFAULT FALSE,
  source_id    TEXT NOT NULL REFERENCES sources(id),
  as_of        DATE NOT NULL,
  fetched_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  raw_ref      TEXT,
  UNIQUE (indicator, series, period, as_of)
);

CREATE INDEX IF NOT EXISTS ix_obs_lookup ON observations (indicator, series, period);

CREATE TABLE IF NOT EXISTS snapshots (
  card         TEXT PRIMARY KEY,
  payload      JSONB NOT NULL,
  as_of        DATE,
  fetched_at   TIMESTAMPTZ NOT NULL,
  status       TEXT NOT NULL CHECK (status IN ('fresh','stale','unavailable')),
  last_error   TEXT,
  version      BIGINT NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS collector_runs (
  id           BIGSERIAL PRIMARY KEY,
  job          TEXT NOT NULL,
  started_at   TIMESTAMPTZ NOT NULL,
  finished_at  TIMESTAMPTZ,
  ok           BOOLEAN,
  http_status  INT,
  duration_ms  INT,
  note         TEXT
);

-- Insert primary sources registry
INSERT INTO sources (id, name, url, is_nse) VALUES
  ('nse', 'National Stock Exchange of India', 'https://www.nseindia.com', TRUE),
  ('bse', 'Bombay Stock Exchange (Yahoo Finance)', 'https://query1.finance.yahoo.com', FALSE),
  ('imf', 'International Monetary Fund (WEO DataMapper)', 'https://www.imf.org/external/datamapper/', FALSE),
  ('worldbank', 'World Bank Open Data', 'https://data.worldbank.org/', FALSE),
  ('commerce', 'Ministry of Commerce & Industry', 'https://tradestat.commerce.gov.in/', FALSE),
  ('gst', 'Goods and Services Tax Council / PIB', 'https://pib.gov.in', FALSE),
  ('mospi', 'Ministry of Statistics and Programme Implementation', 'https://www.mospi.gov.in', FALSE),
  ('cga', 'Controller General of Accounts / Union Budget', 'https://www.indiabudget.gov.in/', FALSE)
ON CONFLICT (id) DO NOTHING;
