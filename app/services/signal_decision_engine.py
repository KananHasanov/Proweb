from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.config import settings
from app.schemas.domain import (
    Direction,
    EventContext,
    FinalSignal,
    MarketContext,
    SignalCandidate,
    TokenClassification,
)


@dataclass
class QualityGateResult:
    accepted: bool
    reason: str


class SignalDecisionEngine:
    CORE_PATTERNS = {
        "double_top",
        "double_bottom",
        "triple_top",
        "triple_bottom",
        "head_and_shoulders",
        "inverse_head_and_shoulders",
    }

    def build_candidate(
        self,
        classification: TokenClassification,
        market: MarketContext,
        event: EventContext | None,
    ) -> SignalCandidate | None:
        score = 50
        reasons: list[str] = []

        if market.abnormal_volume:
            score += 10
            reasons.append("abnormal volume confirms participation")
        if market.spike_candle:
            score += 8
            reasons.append("expansion candle created inefficiency zone")
        if self.CORE_PATTERNS.intersection(set(market.detected_patterns)):
            score += 12
            reasons.append("core reversal/continuation chart pattern detected")

        if event:
            score += int(event.urgency_score * 0.1)
            reasons.append(f"event context: {event.scenario_tag}")

        if market.near_ath or market.near_atl:
            score -= 5
            reasons.append("ATH/ATL proximity reduces structure confidence")

        strategy_mode = classification.dominant_mode

        # Deterministic direction selection (no LLM inference)
        if "double_top" in market.detected_patterns or "head_and_shoulders" in market.detected_patterns:
            direction = Direction.SHORT
        elif "double_bottom" in market.detected_patterns or "inverse_head_and_shoulders" in market.detected_patterns:
            direction = Direction.LONG
        elif market.spike_candle and event and event.event_type.value in {"listing", "unlock"}:
            direction = Direction.SHORT
        else:
            return None

        if direction == Direction.LONG:
            entry_zone_low = market.close * 0.995
            entry_zone_high = market.close * 1.001
            stop_loss = entry_zone_low * 0.99
            invalidation = "price closes below stop-loss with rising sell volume"
        else:
            entry_zone_low = market.close * 0.999
            entry_zone_high = market.close * 1.005
            stop_loss = entry_zone_high * 1.01
            invalidation = "price closes above stop-loss with rising buy volume"

        if not reasons:
            reasons.append("no strong confluence")

        return SignalCandidate(
            symbol=market.symbol,
            timeframe=market.timeframe,
            direction=direction,
            entry_zone_low=entry_zone_low,
            entry_zone_high=entry_zone_high,
            stop_loss=stop_loss,
            confidence_score=min(score, 99),
            strategy_mode=strategy_mode,
            reason_summary=reasons,
            event_context_summary=event.summary if event else "no major event catalyst detected",
            invalidation_condition=invalidation,
        )

    def quality_gate(self, candidate: SignalCandidate, spread_pct: float, duplicate_active: bool, stale: bool) -> QualityGateResult:
        if duplicate_active:
            return QualityGateResult(False, "duplicate similar signal already active")
        if stale:
            return QualityGateResult(False, "signal is stale")
        if candidate.confidence_score < settings.min_confidence_score:
            return QualityGateResult(False, "confidence below configured threshold")

        width_pct = (candidate.entry_zone_high - candidate.entry_zone_low) / candidate.entry_zone_low
        if width_pct > settings.max_entry_zone_width_pct:
            return QualityGateResult(False, "entry zone too wide")

        if spread_pct > 0.003:
            return QualityGateResult(False, "spread/slippage risk too high")

        entry_mid = (candidate.entry_zone_low + candidate.entry_zone_high) / 2
        if candidate.direction == Direction.LONG:
            risk = entry_mid - candidate.stop_loss
        else:
            risk = candidate.stop_loss - entry_mid

        if risk <= 0:
            return QualityGateResult(False, "invalid risk (<= 0)")

        if (risk / entry_mid) > settings.abnormal_stop_loss_pct:
            return QualityGateResult(False, "stop loss distance abnormal")

        return QualityGateResult(True, "ok")

    def suggest_leverage(self, candidate: SignalCandidate) -> float:
        entry_mid = (candidate.entry_zone_low + candidate.entry_zone_high) / 2
        if candidate.direction == Direction.LONG:
            risk = entry_mid - candidate.stop_loss
        else:
            risk = candidate.stop_loss - entry_mid

        risk_pct = risk / entry_mid if entry_mid else 0.0
        if risk_pct <= 0:
            return 1.0

        base_leverage = settings.target_risk_per_trade_pct / risk_pct
        confidence_boost = 0.8 + (candidate.confidence_score / 100) * 0.4
        leverage = base_leverage * confidence_boost
        return round(max(1.0, min(leverage, settings.max_leverage)), 2)

    def finalize(self, candidate: SignalCandidate) -> FinalSignal:
        entry_mid = (candidate.entry_zone_low + candidate.entry_zone_high) / 2
        if candidate.direction == Direction.LONG:
            risk = entry_mid - candidate.stop_loss
            take_profit = entry_mid + 5 * risk
        else:
            risk = candidate.stop_loss - entry_mid
            take_profit = entry_mid - 5 * risk

        return FinalSignal(
            **candidate.model_dump(),
            entry_midpoint=entry_mid,
            take_profit=take_profit,
            suggested_leverage=self.suggest_leverage(candidate),
            timestamp=datetime.now(timezone.utc),
        )
