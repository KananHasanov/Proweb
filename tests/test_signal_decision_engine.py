from datetime import datetime, timezone

from app.schemas.domain import EventContext, EventType, MarketContext
from app.services.risk_planning_service import RiskPlanningService
from app.services.signal_decision_engine import SignalDecisionEngine
from app.services.token_classification_service import TokenClassificationService


def test_long_signal_rr_math():
    classifier = TokenClassificationService()
    engine = SignalDecisionEngine()

    classification = classifier.classify("ETHUSDT", 20_000_000_000, 10_000_000, 0.8, False, False, False)
    market = MarketContext(
        symbol="ETHUSDT",
        timeframe="15m",
        close=3000,
        avg_volume_20=10_000_000,
        detected_patterns=["double_bottom"],
    )
    event = EventContext(
        event_type=EventType.PARTNERSHIP,
        source="cmc",
        title="Partnership",
        event_time=datetime.now(timezone.utc),
        urgency_score=50,
        volatility_score=40,
        scenario_tag="pre-event pump",
        summary="Positive catalyst",
    )
    candidate = engine.build_candidate(classification, market, event)
    assert candidate is not None
    final = engine.finalize(candidate)
    risk = final.entry_midpoint - final.stop_loss
    assert abs(final.take_profit - (final.entry_midpoint + 5 * risk)) < 1e-8
    assert final.suggested_leverage >= 1


def test_short_signal_rr_math():
    classifier = TokenClassificationService()
    engine = SignalDecisionEngine()

    classification = classifier.classify("SOLUSDT", 5_000_000_000, 8_000_000, 0.7, True, False, True)
    market = MarketContext(
        symbol="SOLUSDT",
        timeframe="5m",
        close=150,
        avg_volume_20=8_000_000,
        detected_patterns=["double_top"],
        spike_candle=True,
        abnormal_volume=True,
    )
    event = EventContext(
        event_type=EventType.LISTING,
        source="rootdata",
        title="Listing",
        event_time=datetime.now(timezone.utc),
        urgency_score=70,
        volatility_score=80,
        scenario_tag="spike-risk",
        summary="Post-listing spike",
    )
    candidate = engine.build_candidate(classification, market, event)
    assert candidate is not None
    final = engine.finalize(candidate)
    risk = final.stop_loss - final.entry_midpoint
    assert abs(final.take_profit - (final.entry_midpoint - 5 * risk)) < 1e-8


def test_compound_target_from_100_to_1m_in_20_to_30_trades():
    plans = RiskPlanningService.leverage_guidance(100, 1_000_000, 20, 30)
    assert len(plans) == 11
    assert plans[0]["required_return_per_trade_pct"] > plans[-1]["required_return_per_trade_pct"]
