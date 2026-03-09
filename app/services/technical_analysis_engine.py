from app.schemas.domain import MarketContext


class TechnicalAnalysisEngine:
    """Deterministic TA feature extraction hooks for pattern/situation scoring."""

    def detect_market_context(self, symbol: str, timeframe: str, candles: list[dict]) -> MarketContext:
        if len(candles) < 20:
            raise ValueError("at least 20 candles required for context detection")
        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        volumes = [c["volume"] for c in candles]

        close = closes[-1]
        ath = max(highs)
        atl = min(lows)
        avg_vol_20 = sum(volumes[-20:]) / max(len(volumes[-20:]), 1)
        near_ath = close >= ath * 0.97
        near_atl = close <= atl * 1.03

        last_range = highs[-1] - lows[-1]
        prior_avg_range = sum((h - l) for h, l in zip(highs[-10:-1], lows[-10:-1])) / max(len(highs[-10:-1]), 1)
        spike_candle = prior_avg_range > 0 and last_range >= 2.2 * prior_avg_range
        abnormal_volume = avg_vol_20 > 0 and volumes[-1] >= 2.0 * avg_vol_20

        patterns: list[str] = []
        if len(closes) >= 5 and closes[-1] < closes[-2] < closes[-3] and highs[-4] <= highs[-5]:
            patterns.append("double_top")
        if len(closes) >= 5 and closes[-1] > closes[-2] > closes[-3] and lows[-4] >= lows[-5]:
            patterns.append("double_bottom")

        return MarketContext(
            symbol=symbol,
            timeframe=timeframe,
            close=close,
            avg_volume_20=avg_vol_20,
            near_ath=near_ath,
            near_atl=near_atl,
            consolidation_breakout=(max(highs[-5:]) - min(lows[-5:])) / close < 0.02,
            retest=abs(close - closes[-2]) / close < 0.002,
            spike_candle=spike_candle,
            abnormal_volume=abnormal_volume,
            inefficiency_zone_low=lows[-1] if spike_candle else None,
            inefficiency_zone_high=highs[-1] if spike_candle else None,
            detected_patterns=patterns,
        )
