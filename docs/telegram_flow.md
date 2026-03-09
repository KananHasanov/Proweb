# Telegram Bot Flow

1. `/start` -> register user, show command menu.
2. `/help` -> strategy + risk disclaimer + commands.
3. `/watchlist` -> list/add/remove tracked symbols.
4. Scheduler posts:
   - daily deep scan summary
   - intraday alerts (5m/15m/1h)
   - unlock/event reminders
5. Signal lifecycle updates:
   - new signal
   - active status
   - invalidated / TP / SL
6. `/latest`, `/active`, `/events`, `/explain <symbol>`, `/settings`, `/backtest` map to API endpoints.
