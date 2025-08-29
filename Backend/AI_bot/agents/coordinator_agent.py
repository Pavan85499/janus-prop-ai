"""
Coordinator Agent for Real Estate AI System

Purpose:
- Interpret high-level user goals and decompose them into multi-agent workflows
- Delegate tasks to specialized agents via AgentManager (from context)
- Aggregate results and provide a concise, user-facing summary

Usage notes:
- This agent expects `context` to optionally contain `agent_manager` (core.agent_manager.AgentManager)
  when executing workflows. If absent, it will only return the planned workflow.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Union

from agents.base_agent import BaseAgent, AgentConfig


class CoordinatorAgent(BaseAgent):
    """Coordinator that plans and optionally executes multi-agent workflows."""

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
        # Simple intents
        if "plan" in req and ("workflow" in req or "analysis" in req):
            plan = self._plan_workflow({"goal": request})
            return {"analysis_type": "plan_workflow", "result": plan, "confidence_score": 0.75}
        if "execute" in req and ("workflow" in req or "plan" in req):
            plan = self._plan_workflow({"goal": request})
            exec_result = await self._maybe_execute(plan, context)
            return {"analysis_type": "execute_workflow", "result": exec_result, "confidence_score": 0.75}
        # Default: route to a suggested agent
        route = self._route_question(request)
        return {"analysis_type": "route_question", "result": route, "confidence_score": 0.6}

    async def _handle_structured_request(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        rtype = request.get("type", "").lower()
        if rtype == "plan_workflow":
            plan = self._plan_workflow(request.get("data", {}))
            return {"analysis_type": "plan_workflow", "result": plan, "confidence_score": 0.8}
        if rtype == "execute_workflow":
            plan = request.get("workflow_definition") or self._plan_workflow(request.get("data", {}))
            exec_result = await self._maybe_execute(plan, context)
            return {"analysis_type": "execute_workflow", "result": exec_result, "confidence_score": 0.8}
        if rtype == "route_question":
            q = request.get("question") or ""
            route = self._route_question(q)
            return {"analysis_type": "route_question", "result": route, "confidence_score": 0.65}
        # Unknown
        return {"analysis_type": rtype or "coord_unknown", "result": {"message": "Unsupported coordinator request."}, "confidence_score": 0.4}

    # --- Planning logic ---

    def _plan_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        goal = data.get("goal", "Property analysis and recommendation")
        inputs = data.get("inputs", {})
        include_legal = bool(data.get("include_legal", True))
        include_financial = bool(data.get("include_financial", True))
        include_market = bool(data.get("include_market", True))

        steps: List[Dict[str, Any]] = []
        # 0: Market analysis
        if include_market:
            steps.append({
                "agent": "market",
                "task": "market_trends",
                "data": {"neighborhood": inputs.get("neighborhood"), "months": inputs.get("months", 6)},
            })
            steps.append({
                "agent": "market",
                "task": "comparable_sales",
                "data": {"comps": inputs.get("comps", [])},
                "dependencies": [0],
            })
        # 2: Financial analysis (depends on market outputs)
        if include_financial:
            steps.append({
                "agent": "financial",
                "task": "cash_flow_analysis",
                "data": {
                    "monthly_rent": inputs.get("monthly_rent"),
                    "other_income": inputs.get("other_income", 0),
                    "vacancy_rate": inputs.get("vacancy_rate", 0.05),
                    "operating_expenses": inputs.get("operating_expenses", 0),
                },
                "dependencies": [len(steps) - 1] if steps else [],
            })
            steps.append({
                "agent": "financial",
                "task": "roi_analysis",
                "data": {
                    "purchase_price": inputs.get("purchase_price"),
                    "noi": inputs.get("noi"),
                    "yearly_cash_flow": inputs.get("yearly_cash_flow"),
                    "cash_invested": inputs.get("cash_invested"),
                },
                "dependencies": [len(steps) - 1],
            })
        # 4: Optional legal review
        if include_legal:
            steps.append({
                "agent": "legal",
                "task": "risk_assessment",
                "data": {"content": inputs.get("legal_notes", "")},
                "dependencies": [len(steps) - 1] if steps else [],
            })

        plan = {
            "goal": goal,
            "steps": steps,
            "notes": "Autogenerated by CoordinatorAgent; convert indices to proper dependencies when creating workflow.",
        }
        return plan

    def _route_question(self, question: str) -> Dict[str, Any]:
        q = question.lower()
        if any(k in q for k in ["loan", "mortgage", "roi", "cap rate", "cash flow", "pricing"]):
            return {"target_agent": "financial", "reason": "Financial terms detected"}
        if any(k in q for k in ["comps", "trend", "forecast", "neighborhood", "market"]):
            return {"target_agent": "market", "reason": "Market-related terms detected"}
        if any(k in q for k in ["contract", "compliance", "regulation", "legal"]):
            return {"target_agent": "legal", "reason": "Legal-related terms detected"}
        return {"target_agent": "ai_insights", "reason": "General or ambiguous query"}

    async def _maybe_execute(self, plan: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        manager = (context or {}).get("agent_manager")
        if not manager:
            return {"message": "No agent_manager in context. Returning plan only.", "workflow_definition": plan["steps"]}
        # Convert plan steps into workflow definition (replace indexes with ints for AgentManager mapping)
        definition: List[Dict[str, Any]] = []
        for idx, step in enumerate(plan["steps"]):
            # Dependencies will be mapped by AgentManager when given as index list
            definition.append({
                "agent": step["agent"],
                "task": step["task"],
                "data": step.get("data", {}),
                "dependencies": step.get("dependencies", []),
            })
        workflow = await manager.create_workflow(definition)
        results = await manager.execute_workflow(workflow.workflow_id)
        return {"workflow_id": workflow.workflow_id, "results": results}

    def _get_supported_operations(self) -> List[str]:
        return [
            "plan_workflow",
            "execute_workflow",
            "route_question",
        ]