"""
Market Intelligence Agent for Real Estate AI System

This agent focuses on market research tasks:
- Comparable sales (comps)
- Neighborhood and trend analysis
- Price forecasting (simple heuristic here)
- Demand/supply signals

Notes:
- Uses BaseAgent contract to integrate with AgentManager.
- Replace placeholders with real data connectors (MLS, Zillow, Redfin, Realtor APIs) later.
"""

from __future__ import annotations

import asyncio
from statistics import mean
from typing import Any, Dict, List, Optional, Union

from agents.base_agent import BaseAgent, AgentConfig


class MarketAgent(BaseAgent):
    """Market research and trend analysis agent."""

    async def _process_request_impl(
        self,
        request: Union[str, Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if isinstance(request, str):
            return await self._handle_text_request(request, context)
        return await self._handle_structured_request(request, context)

    async def _handle_text_request(self, request: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        req = request.lower()
        if "comps" in req or "comparable" in req:
            return await self._comparable_sales(context or {})
        if "trend" in req or "market" in req:
            return await self._market_trends(context or {})
        if "forecast" in req or "price" in req:
            return await self._price_forecast(context or {})
        if "neighborhood" in req or "area" in req:
            return await self._neighborhood_analysis(context or {})
        return {
            "analysis_type": "market_general",
            "result": {"message": "Provide 'type' or keywords (comps, trends, forecast, neighborhood)."},
            "confidence_score": 0.5,
        }

    async def _handle_structured_request(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        rtype = request.get("type", "").lower()
        data = request.get("data", {})
        payload = {**(context or {}), **data}

        if rtype in {"comparable_sales", "comps"}:
            return await self._comparable_sales(payload)
        if rtype in {"market_trends", "trends"}:
            return await self._market_trends(payload)
        if rtype in {"price_forecasting", "forecast"}:
            return await self._price_forecast(payload)
        if rtype in {"neighborhood_analysis", "neighborhood"}:
            return await self._neighborhood_analysis(payload)

        return {
            "analysis_type": rtype or "market_unknown",
            "result": {"message": "Unsupported market analysis type."},
            "confidence_score": 0.4,
        }

    # --- Simplified market logic ---

    async def _comparable_sales(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        comps: List[Dict[str, Any]] = payload.get("comps", [])
        # Each comp: { price: float, sqft: float, beds: int, baths: int, distance_km: float }
        prices = [float(c.get("price", 0)) for c in comps if c.get("price")]
        avg_price = mean(prices) if prices else None
        price_per_sqft = mean([c.get("price", 0) / max(c.get("sqft", 1), 1) for c in comps]) if comps else None
        suggested_value = avg_price
        return {
            "analysis_type": "comparable_sales",
            "result": {
                "average_price": round(avg_price, 2) if avg_price else None,
                "avg_price_per_sqft": round(price_per_sqft, 2) if price_per_sqft else None,
                "sample_size": len(comps),
                "suggested_value": round(suggested_value, 2) if suggested_value else None,
            },
            "confidence_score": 0.72,
        }

    async def _market_trends(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        # Placeholder trend logic
        neighborhood = (payload.get("neighborhood") or payload.get("zip"))
        trailing_months = int(payload.get("months", 6))
        mock_prices = payload.get("historical_prices") or [300000, 305000, 310000, 315000, 320000, 330000][:trailing_months]
        growth_rate = ((mock_prices[-1] - mock_prices[0]) / max(mock_prices[0], 1e-9)) * 100 if len(mock_prices) > 1 else 0.0
        return {
            "analysis_type": "market_trends",
            "result": {
                "area": neighborhood,
                "months": trailing_months,
                "growth_rate_percent": round(growth_rate, 2),
                "series": mock_prices,
            },
            "confidence_score": 0.7,
        }

    async def _price_forecast(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        current_price = float(payload.get("current_price", 0))
        monthly_growth = float(payload.get("monthly_growth", 0.01))  # 1%
        months_out = int(payload.get("months", 6))
        forecast = current_price * ((1 + monthly_growth) ** months_out)
        return {
            "analysis_type": "price_forecasting",
            "result": {
                "current_price": round(current_price, 2),
                "monthly_growth": monthly_growth,
                "months": months_out,
                "forecast_price": round(forecast, 2),
            },
            "confidence_score": 0.68,
        }

    async def _neighborhood_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        # Very simplified scoring based on inputs
        safety = float(payload.get("safety_score", 0.7))
        schools = float(payload.get("school_score", 0.7))
        amenities = float(payload.get("amenity_score", 0.7))
        transit = float(payload.get("transit_score", 0.5))
        score = (0.3 * safety) + (0.3 * schools) + (0.25 * amenities) + (0.15 * transit)
        return {
            "analysis_type": "neighborhood_analysis",
            "result": {
                "composite_score": round(score, 3),
                "inputs": {"safety": safety, "schools": schools, "amenities": amenities, "transit": transit},
            },
            "confidence_score": 0.74,
        }

    def _get_supported_operations(self) -> List[str]:
        return [
            "comparable_sales",
            "market_trends",
            "price_forecasting",
            "neighborhood_analysis",
        ]