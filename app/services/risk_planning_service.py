import math


class RiskPlanningService:
    @staticmethod
    def required_compound_return(start_usd: float, target_usd: float, trades: int) -> float:
        if start_usd <= 0 or target_usd <= start_usd or trades <= 0:
            raise ValueError("invalid compounding inputs")
        return (target_usd / start_usd) ** (1 / trades) - 1

    @staticmethod
    def leverage_guidance(start_usd: float, target_usd: float, min_trades: int = 20, max_trades: int = 30) -> list[dict]:
        plans = []
        for trades in range(min_trades, max_trades + 1):
            r = RiskPlanningService.required_compound_return(start_usd, target_usd, trades)
            plans.append(
                {
                    "trades": trades,
                    "required_return_per_trade_pct": round(r * 100, 2),
                    "notes": "Use only on A+ setups with strict stop-loss; highly aggressive target.",
                }
            )
        return plans

    @staticmethod
    def liquidation_warning() -> str:
        return (
            "A path from $100 to $1,000,000 in 20-30 compounded trades implies extreme per-trade returns and high ruin risk. "
            "Prefer fixed-risk sizing with low-to-moderate leverage and accept a longer horizon."
        )
