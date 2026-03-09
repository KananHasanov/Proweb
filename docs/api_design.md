# API Design

## Public/Operator Endpoints
- `GET /health`
- `POST /risk/compound-plan` - computes required compounded return/trade for target account growth and returns leverage-risk warning.
- `POST /signals/scan` - run deterministic scan for provided feature inputs.
- `GET /signals/scan-live/{symbol}` - pulls live Binance candles/ticker/orderbook and polls configured external event sources.

## Planned Endpoints
- `GET /signals/latest`
- `GET /signals/active`
- `GET /events/upcoming`
- `POST /admin/watchlist`
- `PATCH /admin/settings`
- `POST /backtests/run`
- `GET /backtests/{id}`
