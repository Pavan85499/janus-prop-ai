"""
Atelius Agent

Parses court filings, redemption rules, legal risks, and title chains.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

import structlog


logger = structlog.get_logger(__name__)


class AteliusAgent:
    async def parse_court_filing(self, filing: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder extraction with minimal structure
        return {
            "filing_id": filing.get("id"),
            "parties": filing.get("parties", []),
            "case_type": filing.get("case_type", "unknown"),
            "risk": "medium",
            "redemption_window_days": 180,
            "title_impacts": ["possible_lien"],
            "parsed_at": datetime.utcnow().isoformat(),
        }

    async def analyze_title_chain(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        gaps = any(r.get("missing") for r in records)
        issues = ["chain_gap"] if gaps else []
        return {
            "issues": issues,
            "ownership_history": records,
            "clean": not gaps,
            "analyzed_at": datetime.utcnow().isoformat(),
        }


atelius_agent: Optional[AteliusAgent] = None


def get_atelius_agent() -> AteliusAgent:
    global atelius_agent
    if atelius_agent is None:
        atelius_agent = AteliusAgent()
    return atelius_agent


async def atelius_agent_handler(task) -> Dict[str, Any]:
    agent = get_atelius_agent()
    if task.task_type == "parse_court_filing":
        return await agent.parse_court_filing(task.metadata.get("filing", {}))
    if task.task_type == "analyze_title_chain":
        return await agent.analyze_title_chain(task.metadata.get("records", []))
    raise ValueError(f"Unknown task type for Atelius: {task.task_type}")


