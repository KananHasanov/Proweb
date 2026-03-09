## Signal JSON Schema Example

```json
{
  "symbol": "SOLUSDT",
  "timeframe": "15m",
  "direction": "SHORT",
  "entry_zone_low": 166.2,
  "entry_zone_high": 167.5,
  "entry_midpoint": 166.85,
  "stop_loss": 169.1,
  "take_profit": 155.6,
  "suggested_leverage": 2.7,
  "rr_target": "1:5",
  "confidence_score": 78,
  "strategy_mode": "event spike retracement mode",
  "reason_summary": [
    "expansion candle created inefficiency zone",
    "abnormal volume confirms participation",
    "event context: T-3 pre-event positioning"
  ],
  "event_context_summary": "Token unlock within T-3 window; distribution risk elevated.",
  "invalidation_condition": "price closes above stop-loss with rising buy volume",
  "timestamp": "2026-01-11T08:10:00Z",
  "status": "new"
}
```

## Telegram Message Example

```text
🚨 SIGNAL ALERT
Pair: SOLUSDT
Timeframe: 15m
Direction: SHORT
Entry Zone: 166.200000 - 167.500000
Entry Midpoint: 166.850000
Stop Loss: 169.100000
Take Profit: 155.600000
Risk:Reward: 1:5
Suggested Leverage: 2.7x
Confidence: 78/100
Strategy Mode: event spike retracement mode
Why this trade:
- expansion candle created inefficiency zone
- abnormal volume confirms participation
- event context: T-3 pre-event positioning
Event Context:
- Token unlock within T-3 window; distribution risk elevated.
Invalidation:
- price closes above stop-loss with rising buy volume
Time: 2026-01-11T08:10:00Z
Status: new
```
