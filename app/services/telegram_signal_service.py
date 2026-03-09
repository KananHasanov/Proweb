from app.schemas.domain import FinalSignal


class TelegramSignalService:
    @staticmethod
    def format_signal(signal: FinalSignal) -> str:
        reasons = "\n".join([f"- {r}" for r in signal.reason_summary])
        return (
            "🚨 SIGNAL ALERT\n"
            f"Pair: {signal.symbol}\n"
            f"Timeframe: {signal.timeframe}\n"
            f"Direction: {signal.direction.value}\n"
            f"Entry Zone: {signal.entry_zone_low:.6f} - {signal.entry_zone_high:.6f}\n"
            f"Entry Midpoint: {signal.entry_midpoint:.6f}\n"
            f"Stop Loss: {signal.stop_loss:.6f}\n"
            f"Take Profit: {signal.take_profit:.6f}\n"
            f"Risk:Reward: {signal.rr_target}\n"
            f"Suggested Leverage: {signal.suggested_leverage}x\n"
            f"Confidence: {signal.confidence_score}/100\n"
            f"Strategy Mode: {signal.strategy_mode}\n"
            "Why this trade:\n"
            f"{reasons}\n"
            "Event Context:\n"
            f"- {signal.event_context_summary}\n"
            "Invalidation:\n"
            f"- {signal.invalidation_condition}\n"
            f"Time: {signal.timestamp.isoformat()}\n"
            f"Status: {signal.status.value}"
        )
