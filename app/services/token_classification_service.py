from app.core.config import settings
from app.schemas.domain import TokenClassification


class TokenClassificationService:
    def classify(
        self,
        symbol: str,
        market_cap_usd: float,
        avg_daily_volume_usd: float,
        orderbook_depth_score: float,
        spike_context: bool,
        near_ath_or_atl: bool,
        has_major_event: bool,
    ) -> TokenClassification:
        if market_cap_usd >= 10_000_000_000:
            market_cap_bucket = "high-cap"
        elif market_cap_usd >= 1_000_000_000:
            market_cap_bucket = "mid-cap"
        else:
            market_cap_bucket = "low-cap"

        if settings.low_volume_min <= avg_daily_volume_usd <= settings.low_volume_max:
            volume_bucket = "low"
        elif avg_daily_volume_usd <= settings.mid_volume_max:
            volume_bucket = "medium"
        else:
            volume_bucket = "high"

        if orderbook_depth_score < 0.25:
            liquidity_quality = "poor"
        elif orderbook_depth_score < 0.5:
            liquidity_quality = "fair"
        elif orderbook_depth_score < 0.75:
            liquidity_quality = "good"
        else:
            liquidity_quality = "excellent"

        if spike_context:
            dominant_mode = "event spike retracement mode"
        elif near_ath_or_atl:
            dominant_mode = "ATH/ATL reversal mode"
        elif has_major_event:
            dominant_mode = "pre-event positioning mode"
        elif volume_bucket == "low":
            dominant_mode = "low-volume chart pattern mode"
        else:
            dominant_mode = "high-volume structure mode"

        return TokenClassification(
            symbol=symbol,
            market_cap_bucket=market_cap_bucket,
            volume_bucket=volume_bucket,
            liquidity_quality=liquidity_quality,
            dominant_mode=dominant_mode,
        )
