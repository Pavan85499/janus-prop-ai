"""
Zillow API Client for Janus Prop AI

Provides a thin wrapper around Zillow data via RapidAPI (primary) or
official endpoints when available. All methods are safe to call even when
API keys are not configured; they will return structured fallbacks.
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

import aiohttp

from config.settings import get_settings


class ZillowClient:
    """Client for interacting with Zillow data sources."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.rapidapi_key = self.settings.RAPIDAPI_KEY
        self.zillow_api_key = self.settings.ZILLOW_API_KEY
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.settings.REQUEST_TIMEOUT)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def search_properties(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Search properties by free-text query (address, city, ZIP)."""
        if not self.rapidapi_key and not self.zillow_api_key:
            return {
                "properties": [],
                "source": "none",
                "last_updated": datetime.utcnow().isoformat()
            }

        # Prefer RapidAPI Zillow endpoints as they are broadly available
        if self.rapidapi_key:
            try:
                session = await self._get_session()
                # Endpoint name may vary by provider; using common pattern
                url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"
                params = {"location": query, "status_type": "ForSale", "home_type": "Houses", "sortSelection": "days"}
                headers = {
                    "X-RapidAPI-Key": self.rapidapi_key,
                    "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
                }
                async with session.get(url, params=params, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        items = data.get("props", [])[:limit]
                        return {
                            "properties": items,
                            "source": "rapidapi_zillow",
                            "last_updated": datetime.utcnow().isoformat()
                        }
            except Exception:
                pass

        # Fallback placeholder for official API (if available in future)
        return {
            "properties": [],
            "source": "zillow_official_or_fallback",
            "last_updated": datetime.utcnow().isoformat()
        }

    async def get_property_details(self, zpid: str) -> Dict[str, Any]:
        """Get detailed information for a property by Zillow property id (zpid)."""
        if not self.rapidapi_key and not self.zillow_api_key:
            return {"zpid": zpid, "source": "none"}

        if self.rapidapi_key:
            try:
                session = await self._get_session()
                url = "https://zillow-com1.p.rapidapi.com/property"
                params = {"zpid": zpid}
                headers = {
                    "X-RapidAPI-Key": self.rapidapi_key,
                    "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
                }
                async with session.get(url, params=params, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        data["source"] = "rapidapi_zillow"
                        data["last_updated"] = datetime.utcnow().isoformat()
                        return data
            except Exception:
                pass

        return {"zpid": zpid, "source": "zillow_official_or_fallback", "last_updated": datetime.utcnow().isoformat()}

    async def get_comparables(self, zpid: str, limit: int = 10) -> Dict[str, Any]:
        """Get comparable properties for a given zpid."""
        if not self.rapidapi_key and not self.zillow_api_key:
            return {"zpid": zpid, "comparables": []}

        if self.rapidapi_key:
            try:
                session = await self._get_session()
                url = "https://zillow-com1.p.rapidapi.com/similar"
                params = {"zpid": zpid}
                headers = {
                    "X-RapidAPI-Key": self.rapidapi_key,
                    "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
                }
                async with session.get(url, params=params, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        comps = data.get("similars", [])[:limit]
                        return {
                            "zpid": zpid,
                            "comparables": comps,
                            "source": "rapidapi_zillow",
                            "last_updated": datetime.utcnow().isoformat()
                        }
            except Exception:
                pass

        return {"zpid": zpid, "comparables": [], "source": "zillow_official_or_fallback"}

    async def get_rent_estimate(self, address: str) -> Dict[str, Any]:
        """Get a rent estimate for an address (best-effort)."""
        if not self.rapidapi_key and not self.zillow_api_key:
            return {"address": address, "rent_estimate": None}

        if self.rapidapi_key:
            try:
                # Many providers expose rent estimates via different endpoints; use search + heuristics
                search = await self.search_properties(address, limit=1)
                props = search.get("properties", [])
                if props:
                    prop = props[0]
                    # Some responses include rentZestimate; fallback to zestimate * factor
                    rent = prop.get("rentZestimate") or (
                        (prop.get("zestimate") or 0) * 0.0065
                    )
                    return {
                        "address": address,
                        "rent_estimate": rent,
                        "source": search.get("source"),
                        "zpid": prop.get("zpid")
                    }
            except Exception:
                pass

        return {"address": address, "rent_estimate": None, "source": "zillow_official_or_fallback"}


# Simple module-level accessor
_zillow_client: Optional[ZillowClient] = None


def get_zillow_client() -> ZillowClient:
    global _zillow_client
    if _zillow_client is None:
        _zillow_client = ZillowClient()
    return _zillow_client


