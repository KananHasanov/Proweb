from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class SignalStatus(str, Enum):
    NEW = "new"
    ACTIVE = "active"
    MISSED = "missed"
    INVALIDATED = "invalidated"
    TP = "tp"
    SL = "sl"


class EventType(str, Enum):
    UNLOCK = "unlock"
    BURN = "burn"
    LISTING = "listing"
    PARTNERSHIP = "partnership"
    UPGRADE = "upgrade"
    MACRO = "macro"
    GOVERNANCE = "governance"
    VESTING = "vesting"
    OTHER = "other"


class MarketContext(BaseModel):
    symbol: str
    timeframe: Literal["1m", "5m", "15m", "1h", "4h", "1d"]
    close: float
    avg_volume_20: float
    near_ath: bool = False
    near_atl: bool = False
    consolidation_breakout: bool = False
    retest: bool = False
    spike_candle: bool = False
    abnormal_volume: bool = False
    inefficiency_zone_low: float | None = None
    inefficiency_zone_high: float | None = None
    detected_patterns: list[str] = Field(default_factory=list)


class EventContext(BaseModel):
    event_type: EventType
    source: str
    title: str
    event_time: datetime
    urgency_score: int = Field(ge=0, le=100)
    volatility_score: int = Field(ge=0, le=100)
    scenario_tag: str
    summary: str


class TokenClassification(BaseModel):
    symbol: str
    market_cap_bucket: Literal["high-cap", "mid-cap", "low-cap"]
    volume_bucket: Literal["low", "medium", "high"]
    liquidity_quality: Literal["poor", "fair", "good", "excellent"]
    dominant_mode: Literal[
        "low-volume chart pattern mode",
        "high-volume structure mode",
        "event spike retracement mode",
        "ATH/ATL reversal mode",
        "pre-event positioning mode",
    ]


class SignalCandidate(BaseModel):
    symbol: str
    timeframe: str
    direction: Direction
    entry_zone_low: float
    entry_zone_high: float
    stop_loss: float
    confidence_score: int
    strategy_mode: str
    reason_summary: list[str]
    event_context_summary: str
    invalidation_condition: str


class FinalSignal(SignalCandidate):
    entry_midpoint: float
    take_profit: float
    suggested_leverage: float
    rr_target: str = "1:5"
    timestamp: datetime
    status: SignalStatus = SignalStatus.NEW
