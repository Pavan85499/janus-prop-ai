"""
ATTOM Data Integration Agent for Real Estate AI System

This agent integrates with ATTOM Data Solutions to provide comprehensive
real estate data including property details, market trends, and analytics.
"""

import asyncio
import httpx
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4
import structlog
from pydantic import BaseModel, Field

from agents.base_agent import BaseAgent, AgentConfig, AgentResponse


class ATTOMPropertyData(BaseModel):
    """Property data structure from ATTOM API."""
    
    property_id: str
    address: str
    city: str
    state: str
    zip_code: str
    county: str
    property_type: str
    square_footage: Optional[int]
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    year_built: Optional[int]
    lot_size: Optional[float]
    last_sold_date: Optional[str]
    last_sold_price: Optional[float]
    estimated_value: Optional[float]
    tax_assessment: Optional[float]
    market_data: Dict[str, Any] = Field(default_factory=dict)


class ATTOMMarketData(BaseModel):
    """Market data structure from ATTOM API."""
    
    location: str
    market_trends: Dict[str, Any]
    price_movements: List[Dict[str, Any]]
    inventory_levels: Dict[str, Any]
    days_on_market: Dict[str, Any]
    foreclosure_data: Optional[Dict[str, Any]]
    rental_data: Optional[Dict[str, Any]]
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class ATTOMDataAgent(BaseAgent):
    """
    Agent that integrates with ATTOM Data Solutions for real estate data.
    
    This agent provides:
    1. Property data retrieval
    2. Market trend analysis
    3. Comparative market data
    4. Investment analytics
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.logger = structlog.get_logger(self.__class__.__name__)
        
        # Initialize ATTOM API configuration
        self.attom_api_key = config.metadata.get("attom_api_key")
        self.attom_base_url = config.metadata.get("attom_base_url", "https://api.attomdata.com/v3.0")
        self.rate_limit = config.metadata.get("rate_limit", 100)  # requests per minute
        self.timeout = config.metadata.get("timeout", 30)
        
        if not self.attom_api_key:
            self.logger.warning("No ATTOM API key provided, agent will not function properly")
    
    def _get_supported_operations(self) -> List[str]:
        """Return list of operations this agent supports."""
        return [
            "get_property_data",
            "search_properties",
            "get_market_data",
            "get_comparable_sales",
            "get_foreclosure_data",
            "get_rental_data",
            "get_tax_data",
            "get_neighborhood_data"
        ]

    async def _process_request_impl(
        self,
        request: Union[str, Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a request for ATTOM data."""
        if not self.attom_api_key:
            raise Exception("ATTOM API not configured")
            
        if isinstance(request, str):
            response = await self._handle_text_request(request, context)
        else:
            response = await self._handle_structured_request(request, context)
        
        if response.success:
            return response.data
        else:
            raise Exception(response.error)
    
    async def _handle_text_request(self, request: str, context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Handle natural language requests for ATTOM data."""
        try:
            # Parse natural language request
            if "property" in request.lower() and "address" in request.lower():
                return await self._extract_and_search_property(request)
            elif "market" in request.lower() and "trend" in request.lower():
                return await self._extract_and_get_market_data(request)
            elif "comparable" in request.lower() or "comp" in request.lower():
                return await self._extract_and_get_comparables(request)
            else:
                return AgentResponse(
                    success=False,
                    error="Please specify what type of data you need (property, market, comparables, etc.)",
                    agent_id=self.config.agent_id
                )
                
        except Exception as e:
            self.logger.error("Error processing text request for ATTOM data", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Failed to process request: {str(e)}",
                agent_id=self.config.agent_id
            )
    
    async def _handle_structured_request(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Handle structured requests for ATTOM data."""
        request_type = request.get("type")
        
        if request_type == "get_property_data":
            return await self._get_property_data(request, context)
        elif request_type == "search_properties":
            return await self._search_properties(request, context)
        elif request_type == "get_market_data":
            return await self._get_market_data(request, context)
        elif request_type == "get_comparable_sales":
            return await self._get_comparable_sales(request, context)
        elif request_type == "get_foreclosure_data":
            return await self._get_foreclosure_data(request, context)
        else:
            return AgentResponse(
                success=False,
                error=f"Unsupported request type: {request_type}",
                agent_id=self.config.agent_id
            )
    
    async def _get_property_data(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Get detailed property data from ATTOM."""
        try:
            address = request.get("address")
            if not address:
                return AgentResponse(
                    success=False,
                    error="Address is required for property data lookup",
                    agent_id=self.config.agent_id
                )
            
            # ATTOM API endpoint for property details
            endpoint = f"{self.attom_base_url}/property/detail"
            params = {
                "apikey": self.attom_api_key,
                "address": address
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Parse ATTOM response into our structure
                property_data = self._parse_attom_property_response(data)
                
                return AgentResponse(
                    success=True,
                    data={
                        "property": property_data,
                        "source": "ATTOM Data",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    agent_id=self.config.agent_id
                )
                
        except Exception as e:
            self.logger.error("Error getting property data from ATTOM", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Property data retrieval failed: {str(e)}",
                agent_id=self.config.agent_id
            )
    
    async def _search_properties(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Search for properties using ATTOM API."""
        try:
            search_criteria = request.get("criteria", {})
            
            # ATTOM API endpoint for property search
            endpoint = f"{self.attom_base_url}/property/search"
            params = {
                "apikey": self.attom_api_key,
                **search_criteria
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Parse search results
                properties = self._parse_attom_search_response(data)
                
                return AgentResponse(
                    success=True,
                    data={
                        "properties": properties,
                        "total_count": len(properties),
                        "source": "ATTOM Data",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    agent_id=self.config.agent_id
                )
                
        except Exception as e:
            self.logger.error("Error searching properties with ATTOM", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Property search failed: {str(e)}",
                agent_id=self.config.agent_id
            )
    
    async def _get_market_data(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Get market data for a specific location."""
        try:
            location = request.get("location")
            if not location:
                return AgentResponse(
                    success=False,
                    error="Location is required for market data",
                    agent_id=self.config.agent_id
                )
            
            # ATTOM API endpoint for market trends
            endpoint = f"{self.attom_base_url}/market/trends"
            params = {
                "apikey": self.attom_api_key,
                "location": location
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Parse market data
                market_data = self._parse_attom_market_response(data)
                
                return AgentResponse(
                    success=True,
                    data={
                        "market_data": market_data,
                        "source": "ATTOM Data",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    agent_id=self.config.agent_id
                )
                
        except Exception as e:
            self.logger.error("Error getting market data from ATTOM", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Market data retrieval failed: {str(e)}",
                agent_id=self.config.agent_id
            )
    
    async def _get_comparable_sales(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Get comparable sales data from ATTOM."""
        try:
            property_data = request.get("property_data", {})
            radius = request.get("radius", 0.5)  # miles
            limit = request.get("limit", 10)
            
            if not property_data.get("address"):
                return AgentResponse(
                    success=False,
                    error="Property address is required for comparable sales",
                    agent_id=self.config.agent_id
                )
            
            # ATTOM API endpoint for comparable sales
            endpoint = f"{self.attom_base_url}/property/comparables"
            params = {
                "apikey": self.attom_api_key,
                "address": property_data["address"],
                "radius": radius,
                "limit": limit
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Parse comparable sales
                comparables = self._parse_attom_comparables_response(data)
                
                return AgentResponse(
                    success=True,
                    data={
                        "comparable_sales": comparables,
                        "search_criteria": {
                            "radius_miles": radius,
                            "limit": limit
                        },
                        "source": "ATTOM Data",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    agent_id=self.config.agent_id
                )
                
        except Exception as e:
            self.logger.error("Error getting comparable sales from ATTOM", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Comparable sales retrieval failed: {str(e)}",
                agent_id=self.config.agent_id
            )
    
    async def _get_foreclosure_data(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Get foreclosure data from ATTOM."""
        try:
            location = request.get("location")
            if not location:
                return AgentResponse(
                    success=False,
                    error="Location is required for foreclosure data",
                    agent_id=self.config.agent_id
                )
            
            # ATTOM API endpoint for foreclosure data
            endpoint = f"{self.attom_base_url}/foreclosure/search"
            params = {
                "apikey": self.attom_api_key,
                "location": location
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Parse foreclosure data
                foreclosure_data = self._parse_attom_foreclosure_response(data)
                
                return AgentResponse(
                    success=True,
                    data={
                        "foreclosure_data": foreclosure_data,
                        "source": "ATTOM Data",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    agent_id=self.config.agent_id
                )
                
        except Exception as e:
            self.logger.error("Error getting foreclosure data from ATTOM", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Foreclosure data retrieval failed: {str(e)}",
                agent_id=self.config.agent_id
            )
    
    def _parse_attom_property_response(self, data: Dict[str, Any]) -> ATTOMPropertyData:
        """Parse ATTOM API property response into our structure."""
        try:
            property_info = data.get("property", {})
            
            return ATTOMPropertyData(
                property_id=property_info.get("identifier", {}).get("obPropId", ""),
                address=property_info.get("address", {}).get("line1", ""),
                city=property_info.get("address", {}).get("city", ""),
                state=property_info.get("address", {}).get("state", ""),
                zip_code=property_info.get("address", {}).get("zip", ""),
                county=property_info.get("address", {}).get("county", ""),
                property_type=property_info.get("building", {}).get("style", ""),
                square_footage=property_info.get("building", {}).get("size", {}).get("grossSize", 0),
                bedrooms=property_info.get("building", {}).get("rooms", {}).get("beds", 0),
                bathrooms=property_info.get("building", {}).get("rooms", {}).get("baths", 0),
                year_built=property_info.get("building", {}).get("yearBuilt", 0),
                lot_size=property_info.get("lot", {}).get("size", 0),
                last_sold_date=property_info.get("sale", {}).get("lastSoldDate", ""),
                last_sold_price=property_info.get("sale", {}).get("lastSoldAmount", 0),
                estimated_value=property_info.get("valuation", {}).get("avm", {}).get("amount", 0),
                tax_assessment=property_info.get("assessment", {}).get("tax", {}).get("assessed", 0),
                market_data=property_info
            )
        except Exception as e:
            self.logger.error("Error parsing ATTOM property response", error=str(e))
            # Return minimal data structure
            return ATTOMPropertyData(
                property_id="",
                address="",
                city="",
                state="",
                zip_code="",
                county="",
                property_type="",
                market_data=data
            )
    
    def _parse_attom_search_response(self, data: Dict[str, Any]) -> List[ATTOMPropertyData]:
        """Parse ATTOM API search response."""
        properties = []
        try:
            for prop in data.get("properties", []):
                property_data = self._parse_attom_property_response({"property": prop})
                properties.append(property_data)
        except Exception as e:
            self.logger.error("Error parsing ATTOM search response", error=str(e))
        
        return properties
    
    def _parse_attom_market_response(self, data: Dict[str, Any]) -> ATTOMMarketData:
        """Parse ATTOM API market response."""
        try:
            return ATTOMMarketData(
                location=data.get("location", ""),
                market_trends=data.get("trends", {}),
                price_movements=data.get("priceMovements", []),
                inventory_levels=data.get("inventory", {}),
                days_on_market=data.get("daysOnMarket", {}),
                foreclosure_data=data.get("foreclosure", {}),
                rental_data=data.get("rental", {})
            )
        except Exception as e:
            self.logger.error("Error parsing ATTOM market response", error=str(e))
            return ATTOMMarketData(
                location="",
                market_trends={},
                price_movements=[],
                inventory_levels={},
                days_on_market={}
            )
    
    def _parse_attom_comparables_response(self, data: Dict[str, Any]) -> List[ATTOMPropertyData]:
        """Parse ATTOM API comparables response."""
        return self._parse_attom_search_response(data)
    
    def _parse_attom_foreclosure_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse ATTOM API foreclosure response."""
        return data.get("foreclosures", {})
    
    async def _extract_and_search_property(self, request: str) -> AgentResponse:
        """Extract address from text and search for property."""
        # Simple address extraction - in production, use NLP
        words = request.split()
        address_parts = []
        for word in words:
            if any(char.isdigit() for char in word) or word.lower() in ["street", "st", "avenue", "ave", "road", "rd"]:
                address_parts.append(word)
        
        if address_parts:
            address = " ".join(address_parts)
            return await self._get_property_data({"address": address}, None)
        else:
            return AgentResponse(
                success=False,
                error="Could not extract address from request",
                agent_id=self.config.agent_id
            )
    
    async def _extract_and_get_market_data(self, request: str) -> AgentResponse:
        """Extract location from text and get market data."""
        # Simple location extraction
        words = request.split()
        location_parts = []
        for word in words:
            if word.lower() in ["brooklyn", "manhattan", "queens", "bronx", "staten", "nyc", "new york"]:
                location_parts.append(word)
        
        if location_parts:
            location = " ".join(location_parts)
            return await self._get_market_data({"location": location}, None)
        else:
            return AgentResponse(
                success=False,
                error="Could not extract location from request",
                agent_id=self.config.agent_id
            )
    
    async def _extract_and_get_comparables(self, request: str) -> AgentResponse:
        """Extract property info from text and get comparables."""
        # This would need more sophisticated NLP in production
        return AgentResponse(
            success=False,
            error="Please provide property address for comparable sales analysis",
            agent_id=self.config.agent_id
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the ATTOM data agent."""
        try:
            if not self.attom_api_key:
                return {
                    "status": "unhealthy",
                    "error": "ATTOM API not configured",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Test ATTOM API connection with a simple request
            endpoint = f"{self.attom_base_url}/property/detail"
            params = {
                "apikey": self.attom_api_key,
                "address": "1600 Pennsylvania Avenue NW, Washington, DC"
            }
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(endpoint, params=params)
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "api_working": True,
                        "timestamp": datetime.utcnow().isoformat(),
                        "response_time": "fast"
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": f"API returned status {response.status_code}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
        except Exception as e:
            self.logger.error("Health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
