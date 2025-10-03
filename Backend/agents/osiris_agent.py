"""
Osiris Agent

Projects returns, redemption windows, and yield forecasts on every deal.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

import structlog


logger = structlog.get_logger(__name__)


class OsirisAgent:
    async def forecast(self, deal: Dict[str, Any]) -> Dict[str, Any]:
        metrics = deal.get("metrics", {})
        price = float(metrics.get("price", deal.get("price", 0) or 0))
        rent = float(metrics.get("rent", 0))
        rehab = float(metrics.get("rehab", 0))
        taxes = float(metrics.get("taxes", 0))
        insurance = float(metrics.get("insurance", 0))
        other = float(metrics.get("other_expenses", 0))
        if price <= 0:
            price = 1
        noi_monthly = max(rent - (taxes + insurance + other) / 12 - rehab / 24, 0)
        cap_rate = (noi_monthly * 12) / price
        coc = ((noi_monthly * 12) / max(price * 0.25, 1))  # assume 25% equity
        return {
            "cap_rate": round(cap_rate, 4),
            "cash_on_cash": round(coc, 4),
            "expected_roi": round(cap_rate + 0.01, 4),
            "redemption_window_days": 180,
            "assumptions": {"equity": 0.25},
            "generated_at": datetime.utcnow().isoformat(),
        }

    async def batch_forecast(self, deals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [await self.forecast(d) for d in deals]


osiris_agent: Optional[OsirisAgent] = None


def get_osiris_agent() -> OsirisAgent:
    global osiris_agent
    if osiris_agent is None:
        osiris_agent = OsirisAgent()
    return osiris_agent


async def osiris_agent_handler(task) -> Dict[str, Any]:
    agent = get_osiris_agent()
    if task.task_type == "forecast":
        return await agent.forecast(task.metadata.get("deal", {}))
    if task.task_type == "batch_forecast":
        return {"results": await agent.batch_forecast(task.metadata.get("deals", []))}
    raise ValueError(f"Unknown task type for Osiris: {task.task_type}")


