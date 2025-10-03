"""
Eden Agent

Makes final investment decisions using signals from other agents and
optionally augments with Zillow and Gemini insights. Produces ranked
deal lists and a final decision with rationale.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

import structlog

from services.zillow_client import get_zillow_client
from .gemini_ai_agent import get_gemini_agent


logger = structlog.get_logger(__name__)


class EdenAgent:
    def __init__(self) -> None:
        self.zillow = get_zillow_client()
        self.gemini = get_gemini_agent()

    async def rank_deals(self, deals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Rank deals by expected return and fit. Expects list of deals containing either zpid or address and metrics."""
        # Fetch Zillow augmentation in parallel where possible
        async def _augment(deal: Dict[str, Any]) -> Dict[str, Any]:
            zpid = deal.get("zpid")
            address = deal.get("address")
            zillow_detail: Optional[Dict[str, Any]] = None
            if zpid:
                zillow_detail = await self.zillow.get_property_details(zpid)
            elif address:
                search = await self.zillow.search_properties(address, limit=1)
                props = search.get("properties", [])
                if props:
                    zpid2 = props[0].get("zpid")
                    if zpid2:
                        zillow_detail = await self.zillow.get_property_details(zpid2)
                        deal["zpid"] = zpid2
            deal["zillow"] = zillow_detail
            return deal

        augmented = await asyncio.gather(*[_augment(d) for d in deals])

        # Simple scoring heuristic as baseline
        def _score(deal: Dict[str, Any]) -> float:
            metrics = deal.get("metrics", {})
            roi = float(metrics.get("expected_roi", 0))
            cap = float(metrics.get("cap_rate", 0))
            risk = float(metrics.get("risk", 0.5))
            fit = float(metrics.get("strategy_fit", 0.5))
            return (roi * 0.4) + (cap * 0.3) + (fit * 0.3) - (risk * 0.2)

        scored = [{"deal": d, "score": _score(d)} for d in augmented]
        scored.sort(key=lambda x: x["score"], reverse=True)

        # Optionally generate a concise rationale with Gemini
        rationale: Optional[str] = None
        try:
            if hasattr(self.gemini, "is_initialized") and self.gemini.is_initialized:
                prompt = (
                    "Rank the following real estate deals by expected return and fit. "
                    "Explain the top 3 in 3-4 bullet points. Return JSON with keys: ranked_ids, rationale."
                )
                payload = {
                    "deals": [
                        {"id": d["deal"].get("id"), "score": d["score"], "metrics": d["deal"].get("metrics", {})}
                        for d in scored
                    ]
                }
                response = await self.gemini._generate_response(f"{prompt}\n\n{payload}")
                rationale = response
        except Exception:
            rationale = None

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "ranked": [{"id": d["deal"].get("id"), "score": d["score"], "deal": d["deal"]} for d in scored],
            "rationale": rationale,
        }

    async def decide(self, ranked: List[Dict[str, Any]], mandate: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a final investment decision from a ranked list."""
        top = ranked[0] if ranked else None
        decision = {
            "decision": "no_action" if not top else "proceed_to_ic",
            "selected_id": top.get("id") if top else None,
            "confidence": 0.7 if top else 0.0,
            "timestamp": datetime.utcnow().isoformat(),
        }
        # Allow Gemini to refine the decision
        try:
            if hasattr(self.gemini, "is_initialized") and self.gemini.is_initialized and top:
                prompt = (
                    "Given this ranked shortlist and an investment mandate, finalize a decision. "
                    "Return JSON with keys: decision, confidence, reasons, risks, next_steps."
                )
                payload = {"ranked": ranked[:5], "mandate": mandate or {}}
                response = await self.gemini._generate_response(f"{prompt}\n\n{payload}")
                decision["gemini"] = response
        except Exception:
            pass
        return decision


eden_agent: Optional[EdenAgent] = None


def get_eden_agent() -> EdenAgent:
    global eden_agent
    if eden_agent is None:
        eden_agent = EdenAgent()
    return eden_agent


async def eden_agent_handler(task) -> Dict[str, Any]:
    agent = get_eden_agent()
    if task.task_type == "rank_deals":
        return await agent.rank_deals(task.metadata.get("deals", []))
    if task.task_type == "final_decision":
        return await agent.decide(task.metadata.get("ranked", []), task.metadata.get("mandate"))
    raise ValueError(f"Unknown task type for Eden: {task.task_type}")


