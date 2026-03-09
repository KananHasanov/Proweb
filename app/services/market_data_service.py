from collections import defaultdict, deque
from typing import Any

import httpx

from app.core.config import settings


class MarketDataService:
    """Binance market-data adapter with normalized rolling candle buffers."""

    def __init__(self, max_buffer: int = 500):
        self.base_url = settings.binance_base_url.rstrip("/")
        self.buffers: dict[str, dict[str, deque[dict[str, Any]]]] = defaultdict(lambda: defaultdict(lambda: deque(maxlen=max_buffer)))

    def fetch_klines(self, symbol: str, interval: str, limit: int = 200) -> list[dict[str, Any]]:
        url = f"{self.base_url}/api/v3/klines"
        params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
        with httpx.Client(timeout=20.0) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            rows = resp.json()
        normalized = []
        for r in rows:
            normalized.append(
                {
                    "open_time": r[0],
                    "open": float(r[1]),
                    "high": float(r[2]),
                    "low": float(r[3]),
                    "close": float(r[4]),
                    "volume": float(r[5]),
                    "close_time": r[6],
                }
            )
        return normalized

    def fetch_24h_ticker(self, symbol: str) -> dict[str, Any]:
        url = f"{self.base_url}/api/v3/ticker/24hr"
        with httpx.Client(timeout=20.0) as client:
            resp = client.get(url, params={"symbol": symbol.upper()})
            resp.raise_for_status()
            return resp.json()

    def fetch_orderbook(self, symbol: str, limit: int = 100) -> dict[str, Any]:
        url = f"{self.base_url}/api/v3/depth"
        with httpx.Client(timeout=20.0) as client:
            resp = client.get(url, params={"symbol": symbol.upper(), "limit": limit})
            resp.raise_for_status()
            return resp.json()

    def normalize_kline(self, raw: dict[str, Any]) -> dict[str, Any]:
        return {
            "open_time": raw["t"],
            "open": float(raw["o"]),
            "high": float(raw["h"]),
            "low": float(raw["l"]),
            "close": float(raw["c"]),
            "volume": float(raw["v"]),
            "close_time": raw["T"],
        }

    def push_candle(self, symbol: str, timeframe: str, candle: dict[str, Any]) -> None:
        self.buffers[symbol][timeframe].append(candle)

    def get_buffer(self, symbol: str, timeframe: str) -> list[dict[str, Any]]:
        return list(self.buffers[symbol][timeframe])
