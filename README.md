# Proweb Crypto Signal Engine

Deterministic, event-aware crypto signal engine for Telegram delivery.

## Quick Start (Docker)
1. Copy env file:
   ```bash
   cp .env.example .env
   ```
2. (Optional) set `ROOTDATA_EVENTS_URL` and `CMC_UNLOCKS_URL` in `.env` if you have provider endpoints.
3. Start stack:
   ```bash
   docker compose up --build
   ```
4. Open docs at `http://localhost:8000/docs`.

## Quick Start (Local)
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run Checks
```bash
python -m compileall app tests
pytest -q
```

## Main Endpoints
- `GET /health`
- `POST /risk/compound-plan` (compounding plan from `$100 -> $1,000,000` in 20-30 trades)
- `POST /signals/scan` (manual feature-input scan)
- `GET /signals/scan-live/{symbol}?timeframe=15m&market_cap_usd=...` (pulls live Binance + external event adapters)

## Example: compounding & leverage planning
```bash
curl -X POST http://localhost:8000/risk/compound-plan \
  -H "Content-Type: application/json" \
  -d '{"start_usd":100,"target_usd":1000000,"min_trades":20,"max_trades":30}'
```

## Example: live symbol scan
```bash
curl "http://localhost:8000/signals/scan-live/BTCUSDT?timeframe=15m&market_cap_usd=800000000000"
```

## Security Notes
- Use read-only Binance credentials for data-only mode.
- Keep Telegram/API credentials in secret manager.
- AI layer remains explanation-only; signal levels and RR math are deterministic.
