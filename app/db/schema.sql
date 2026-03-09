CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  telegram_user_id BIGINT UNIQUE NOT NULL,
  username TEXT,
  role TEXT NOT NULL DEFAULT 'viewer',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE watchlists (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tracked_symbols (
  id BIGSERIAL PRIMARY KEY,
  symbol TEXT UNIQUE NOT NULL,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  market_cap_bucket TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ohlcv_candles (
  id BIGSERIAL PRIMARY KEY,
  symbol TEXT NOT NULL,
  timeframe TEXT NOT NULL,
  open_time TIMESTAMPTZ NOT NULL,
  open NUMERIC(20,10) NOT NULL,
  high NUMERIC(20,10) NOT NULL,
  low NUMERIC(20,10) NOT NULL,
  close NUMERIC(20,10) NOT NULL,
  volume NUMERIC(28,10) NOT NULL,
  source TEXT NOT NULL DEFAULT 'binance',
  UNIQUE(symbol, timeframe, open_time)
);

CREATE TABLE event_sources (
  id BIGSERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  endpoint TEXT,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE events (
  id BIGSERIAL PRIMARY KEY,
  symbol TEXT,
  event_type TEXT NOT NULL,
  title TEXT NOT NULL,
  source_id BIGINT REFERENCES event_sources(id),
  event_time TIMESTAMPTZ NOT NULL,
  urgency_score INT NOT NULL,
  volatility_score INT NOT NULL,
  scenario_tag TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  dedupe_hash TEXT UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE signals (
  id BIGSERIAL PRIMARY KEY,
  symbol TEXT NOT NULL,
  timeframe TEXT NOT NULL,
  direction TEXT NOT NULL,
  entry_zone_low NUMERIC(20,10) NOT NULL,
  entry_zone_high NUMERIC(20,10) NOT NULL,
  entry_midpoint NUMERIC(20,10) NOT NULL,
  stop_loss NUMERIC(20,10) NOT NULL,
  take_profit NUMERIC(20,10) NOT NULL,
  rr_target TEXT NOT NULL DEFAULT '1:5',
  confidence_score INT NOT NULL,
  strategy_mode TEXT NOT NULL,
  reason_summary JSONB NOT NULL,
  event_context_summary TEXT,
  invalidation_condition TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE signal_updates (
  id BIGSERIAL PRIMARY KEY,
  signal_id BIGINT NOT NULL REFERENCES signals(id) ON DELETE CASCADE,
  old_status TEXT,
  new_status TEXT NOT NULL,
  note TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE backtest_runs (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  started_at TIMESTAMPTZ NOT NULL,
  ended_at TIMESTAMPTZ,
  config_snapshot JSONB NOT NULL,
  metrics JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE backtest_trades (
  id BIGSERIAL PRIMARY KEY,
  run_id BIGINT NOT NULL REFERENCES backtest_runs(id) ON DELETE CASCADE,
  signal_id BIGINT,
  symbol TEXT NOT NULL,
  strategy_mode TEXT NOT NULL,
  direction TEXT NOT NULL,
  entry_price NUMERIC(20,10) NOT NULL,
  exit_price NUMERIC(20,10),
  outcome TEXT,
  rr_realized NUMERIC(10,4),
  opened_at TIMESTAMPTZ NOT NULL,
  closed_at TIMESTAMPTZ
);

CREATE TABLE strategy_configs (
  id BIGSERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  config JSONB NOT NULL,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  updated_by BIGINT REFERENCES users(id),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE bot_logs (
  id BIGSERIAL PRIMARY KEY,
  level TEXT NOT NULL,
  message TEXT NOT NULL,
  context JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ai_explanations (
  id BIGSERIAL PRIMARY KEY,
  signal_id BIGINT REFERENCES signals(id) ON DELETE CASCADE,
  model_name TEXT,
  prompt_hash TEXT,
  explanation TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
