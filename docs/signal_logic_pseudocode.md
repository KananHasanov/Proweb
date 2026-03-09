```text
for symbol in tracked_watchlist:
  classification = classify_token(cap, volume, depth, spike_context, ath_atl, event_present)
  market = extract_market_features(ohlcv)
  event = get_deduped_event_context(symbol)

  mode = choose_mode(
    low_volume -> chart_pattern,
    high_volume -> structure_plus_pattern,
    spike -> inefficiency,
    ath_atl -> reversal,
    strong_event -> higher_tf_event_mode
  )

  candidate = build_candidate(mode, market, event)
  if candidate is None: continue

  # deterministic risk engine
  entry_mid = (entry_low + entry_high) / 2
  if direction == LONG:
    risk = entry_mid - stop
    tp = entry_mid + 5*risk
  else:
    risk = stop - entry_mid
    tp = entry_mid - 5*risk

  reject_if(
    risk <= 0,
    entry_zone_too_wide,
    abnormal_stop_distance,
    poor_liquidity,
    high_spread,
    high_event_uncertainty_without_structure,
    duplicate_active,
    stale_setup
  )

  persist_signal_and_send_telegram()
```
