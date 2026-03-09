from datetime import datetime, timedelta, timezone

import httpx

from app.core.config import settings
from app.schemas.domain import EventContext, EventType


class EventIntelligenceService:
    def classify_unlock_window(self, event_time: datetime) -> str:
        now = datetime.now(timezone.utc)
        delta_days = (event_time - now).days
        if delta_days <= -1:
            return "post-event mean reversion"
        if delta_days <= 0:
            return "event-day volatility"
        if delta_days <= 1:
            return "T-1 high-risk window"
        if delta_days <= 3:
            return "T-3 pre-event positioning"
        if delta_days <= 7:
            return "T-7 lead-up"
        if delta_days <= 14:
            return "T-14 early positioning"
        return "outside lead-up window"

    def normalize_event(self, source: str, payload: dict) -> EventContext:
        event_time = datetime.fromisoformat(payload["event_time"])
        event_type = EventType(payload.get("event_type", "other"))
        scenario = self.classify_unlock_window(event_time)
        return EventContext(
            event_type=event_type,
            source=source,
            title=payload["title"],
            event_time=event_time,
            urgency_score=min(int(payload.get("urgency_score", 50)), 100),
            volatility_score=min(int(payload.get("volatility_score", 50)), 100),
            scenario_tag=scenario,
            summary=payload.get("summary", f"{event_type.value} event classified as {scenario}"),
        )

    def fetch_source_events(self, source_name: str, url: str) -> list[dict]:
        if not url:
            return []
        with httpx.Client(timeout=20.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()

        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("events", "data", "result"):
                if isinstance(data.get(key), list):
                    return data[key]
        return []

    def fetch_external_events(self) -> dict[str, list[dict]]:
        sources = {
            "rootdata": settings.rootdata_events_url,
            "cmc_unlocks": settings.cmc_unlocks_url,
        }
        payload: dict[str, list[dict]] = {}
        for name, url in sources.items():
            try:
                payload[name] = self.fetch_source_events(name, url)
            except Exception:
                payload[name] = []
        return payload

    def upcoming_daily_refresh_times(self) -> list[datetime]:
        now = datetime.now(timezone.utc)
        return [now + timedelta(hours=6), now + timedelta(hours=12), now + timedelta(hours=24)]
