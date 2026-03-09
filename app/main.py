from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.schemas.domain import MarketContext
from app.services.event_intelligence_service import EventIntelligenceService
from app.services.market_data_service import MarketDataService
from app.services.risk_planning_service import RiskPlanningService
from app.services.signal_decision_engine import SignalDecisionEngine
from app.services.telegram_signal_service import TelegramSignalService
from app.services.technical_analysis_engine import TechnicalAnalysisEngine
from app.services.token_classification_service import TokenClassificationService

app = FastAPI(title="Proweb Signal Engine", version="0.2.0")

classifier = TokenClassificationService()
event_service = EventIntelligenceService()
market_data = MarketDataService()
ta_engine = TechnicalAnalysisEngine()
decision_engine = SignalDecisionEngine()
telegram_service = TelegramSignalService()
risk_planner = RiskPlanningService()


class ScanRequest(BaseModel):
    symbol: str
    timeframe: str = "15m"
    market_cap_usd: float
    avg_daily_volume_usd: float
    orderbook_depth_score: float
    close: float
    detected_patterns: list[str] = []
    spike_candle: bool = False
    abnormal_volume: bool = False
    near_ath: bool = False
    near_atl: bool = False


class CompoundPlanRequest(BaseModel):
    start_usd: float = 100
    target_usd: float = 1_000_000
    min_trades: int = 20
    max_trades: int = 30


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/risk/compound-plan")
def compound_plan(req: CompoundPlanRequest) -> dict:
    return {
        "plans": risk_planner.leverage_guidance(req.start_usd, req.target_usd, req.min_trades, req.max_trades),
        "warning": risk_planner.liquidation_warning(),
    }


@app.post("/signals/scan")
def scan_signal(req: ScanRequest) -> dict:
    classification = classifier.classify(
        symbol=req.symbol,
        market_cap_usd=req.market_cap_usd,
        avg_daily_volume_usd=req.avg_daily_volume_usd,
        orderbook_depth_score=req.orderbook_depth_score,
        spike_context=req.spike_candle,
        near_ath_or_atl=req.near_ath or req.near_atl,
        has_major_event=True,
    )

    market_context = {
        "symbol": req.symbol,
        "timeframe": req.timeframe,
        "close": req.close,
        "avg_volume_20": req.avg_daily_volume_usd,
        "near_ath": req.near_ath,
        "near_atl": req.near_atl,
        "consolidation_breakout": False,
        "retest": False,
        "spike_candle": req.spike_candle,
        "abnormal_volume": req.abnormal_volume,
        "inefficiency_zone_low": req.close * 0.99 if req.spike_candle else None,
        "inefficiency_zone_high": req.close * 1.01 if req.spike_candle else None,
        "detected_patterns": req.detected_patterns,
    }

    event = event_service.normalize_event(
        "rootdata",
        {
            "title": f"Scheduled unlock for {req.symbol}",
            "event_time": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
            "event_type": "unlock",
            "urgency_score": 70,
            "volatility_score": 75,
            "summary": "Token unlock within T-3 window; distribution risk elevated.",
        },
    )

    candidate = decision_engine.build_candidate(classification, MarketContext(**market_context), event)
    if not candidate:
        raise HTTPException(status_code=404, detail="No trade candidate")

    gate = decision_engine.quality_gate(candidate, spread_pct=0.001, duplicate_active=False, stale=False)
    if not gate.accepted:
        raise HTTPException(status_code=422, detail=gate.reason)

    signal = decision_engine.finalize(candidate)
    return {"signal": signal.model_dump(), "telegram_message": telegram_service.format_signal(signal)}


@app.get("/signals/scan-live/{symbol}")
def scan_live(symbol: str, timeframe: str = "15m", market_cap_usd: float = 1_000_000_000) -> dict:
    candles = market_data.fetch_klines(symbol, timeframe, limit=200)
    ticker = market_data.fetch_24h_ticker(symbol)
    orderbook = market_data.fetch_orderbook(symbol, limit=100)
    event_payloads = event_service.fetch_external_events()

    bids = sum(float(price) * float(size) for price, size in orderbook.get("bids", [])[:20])
    asks = sum(float(price) * float(size) for price, size in orderbook.get("asks", [])[:20])
    depth_ratio = bids / (bids + asks) if (bids + asks) else 0.5

    market = ta_engine.detect_market_context(symbol, timeframe, candles)
    classification = classifier.classify(
        symbol=symbol,
        market_cap_usd=market_cap_usd,
        avg_daily_volume_usd=float(ticker.get("quoteVolume", 0.0)),
        orderbook_depth_score=depth_ratio,
        spike_context=market.spike_candle,
        near_ath_or_atl=market.near_ath or market.near_atl,
        has_major_event=any(event_payloads.values()),
    )

    event = event_service.normalize_event(
        "aggregated",
        {
            "title": f"External events fetched: {sum(len(v) for v in event_payloads.values())}",
            "event_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "event_type": "other",
            "urgency_score": 60,
            "volatility_score": 65,
            "summary": "Real-time event adapters polled (RootData/CMC URLs if configured).",
        },
    )

    candidate = decision_engine.build_candidate(classification, market, event)
    if not candidate:
        raise HTTPException(status_code=404, detail="No trade candidate from live scan")

    spread_pct = abs(float(orderbook["asks"][0][0]) - float(orderbook["bids"][0][0])) / market.close
    gate = decision_engine.quality_gate(candidate, spread_pct=spread_pct, duplicate_active=False, stale=False)
    if not gate.accepted:
        raise HTTPException(status_code=422, detail=gate.reason)

    signal = decision_engine.finalize(candidate)
    return {
        "signal": signal.model_dump(),
        "telegram_message": telegram_service.format_signal(signal),
        "external_events_count": {k: len(v) for k, v in event_payloads.items()},
    }
