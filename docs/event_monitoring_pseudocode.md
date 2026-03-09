```text
every 6h:
  for source in enabled_event_sources:
    raw_events = source.fetch()
    normalized = normalize(raw_events)
    deduped = dedupe_by(hash(symbol,type,time,title))

    for event in deduped:
      event.type in {unlock,burn,listing,partnership,upgrade,macro,governance,vesting,other}
      urgency = score_urgency(event_time, source_reliability, market_attention)
      volatility = score_volatility(event_type, historical_reaction, liquidity)

      if unlock:
        tag lead-up windows T-14/T-7/T-3/T-1/day/T+1..T+3
        tag team vs community unlock when known

      classify scenario:
        pre-event pump | pre-event dump | post-event mean reversion | spike-risk | low-confidence

      store event + tags
      queue pre-event alerts
```
