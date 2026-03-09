# Telegram Crypto Signal Platform - System Design

## 1) Product Overview
This platform is a deterministic signal engine with AI-assisted explanation only. The engine separates data ingestion, event intelligence, token classification, technical analysis, signal decisioning, Telegram delivery, and admin controls.

## 2) Architecture Diagram (Text)
```
Binance REST/WS ---> market_data_service ----+
                                             |
Event APIs ---> event_intelligence_service --+--> signal_decision_engine --> signals table --> telegram_signal_service
                                             |
Tokenomics / Liquidity ---> token_classification_service
                                             |
OHLCV Buffers ----------> technical_analysis_engine

Admin UI/API --> admin_config_service --> strategy_configs / tracked_symbols

Historical candles + events --> backtesting_engine --> backtest_runs / backtest_trades
```

## 3) Module-by-Module Design
- `market_data_service`: Binance backfill/live kline normalization, rolling buffers, reconnect/rate-limit handling.
- `event_intelligence_service`: source adapter ingestion, dedupe, event typing, urgency/volatility scoring, unlock lead-up windows.
- `token_classification_service`: cap bucket + volume regime + liquidity quality + dominant strategy mode.
- `technical_analysis_engine`: structure, ATH/ATL proximity, spike/expansion, abnormal volume, core pattern detection, inefficiency zones.
- `signal_decision_engine`: strategy selection hierarchy, deterministic LONG/SHORT/no-trade, confidence scoring, rejection filters, fixed RR math.
- `telegram_signal_service`: signal/update/digest formatting and command handlers.
- `admin_config_service`: thresholds, watchlists, toggles, cooldowns, source config.
- `backtesting_engine`: event-aware replay, metrics by token bucket and strategy mode.

## 4) Database Schema
See `app/db/schema.sql`.

## 5) Signal Logic Pseudocode
See `docs/signal_logic_pseudocode.md`.

## 6) Event Monitoring Pseudocode
See `docs/event_monitoring_pseudocode.md`.

## 7) Telegram Bot Flow
See `docs/telegram_flow.md`.

## 8) Folder Structure
See `docs/folder_structure.md`.

## 9) Implementation Roadmap
- Phase 1: infra + schema + deterministic engine + Telegram alerts.
- Phase 2: event adapters + dedupe + scheduled scans.
- Phase 3: backtesting + admin dashboard + AI explanation service.
- Phase 4: multi-exchange + production hardening + observability.

## 10) Risks & Edge Cases
- Event-source outages, stale events, symbol mapping mismatches.
- Listing spikes with extreme slippage.
- Low-liquidity patterns with false breakouts.
- Overlapping contradictory events.

## 11) Sample JSON Payloads
See `docs/sample_payloads.md`.

## 12) MVP vs Advanced
- MVP: Binance + unlock/listing sources + core patterns + Telegram alerts + basic backtest.
- Advanced: multi-source event graph, Monte Carlo backtests, explainability traces, multi-exchange adapters.

## 13) Technical Recommendations
- Keep all trade levels deterministic and auditable.
- Use AI only for summarization/classification/explanation.
- Record every config change and signal lifecycle transition.
- Add leverage suggestion as deterministic risk-output (bounded by `MAX_LEVERAGE`) and not as AI output.
- Use `/signals/scan-live/{symbol}` for real Binance polling and configured event-source polling.
