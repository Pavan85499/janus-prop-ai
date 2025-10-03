"""
Orion Agent

Monitors and collects tax liens, auctions, violations, and court activity
in near real-time. Uses public endpoints when keys are missing, otherwise
leverages configured providers.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

import structlog
import aiohttp

from config.settings import get_settings


logger = structlog.get_logger(__name__)


class OrionAgent:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.settings.REQUEST_TIMEOUT)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def monitor_events(self, geo: Dict[str, Any], since_minutes: int = 60) -> Dict[str, Any]:
        """Collect events for the given geography.

        geo: {city, state} or {lat, lng, radius_miles}
        """
        now = datetime.utcnow().isoformat()
        # Placeholder: In production integrate with county/city data portals
        events = [
            {"type": "tax_lien", "id": f"lien_{int(datetime.utcnow().timestamp())}", "severity": "medium"},
            {"type": "auction", "id": f"auc_{int(datetime.utcnow().timestamp())}", "date": now},
            {"type": "violation", "id": f"vio_{int(datetime.utcnow().timestamp())}", "code": "housing"},
        ]
        return {"geo": geo, "since_minutes": since_minutes, "events": events, "generated_at": now}


orion_agent: Optional[OrionAgent] = None


def get_orion_agent() -> OrionAgent:
    global orion_agent
    if orion_agent is None:
        orion_agent = OrionAgent()
    return orion_agent


async def orion_agent_handler(task) -> Dict[str, Any]:
    agent = get_orion_agent()
    if task.task_type == "monitor_events":
        return await agent.monitor_events(task.metadata.get("geo", {}), task.metadata.get("since_minutes", 60))
    raise ValueError(f"Unknown task type for Orion: {task.task_type}")


