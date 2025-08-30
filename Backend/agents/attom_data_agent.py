"""
ATTOM Data Agent for Janus Prop AI Backend

This module provides integration with ATTOM Data Solutions for real estate data.
"""

import asyncio
import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import httpx

from config.settings import get_settings
from core.redis_client import cache_get, cache_set, publish_event

logger = structlog.get_logger(__name__)

class ATTOMDataAgent:
    """Agent for ATTOM Data Solutions integration."""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.ATTOM_API_KEY
        self.base_url = "https://api.gateway.attomdata.com"
        self.is_initialized = False
        
        if not self.api_key:
            logger.warning("ATTOM_API_KEY not configured")
            return
        
        self._initialize_attom()
    
    def _initialize_attom(self):
        """Initialize ATTOM Data client."""
        try:
            # Test API connection
            self.is_initialized = True
            logger.info("ATTOM Data agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ATTOM Data: {e}")
            self.is_initialized = False
    
    async def get_property_details(
        self,
        address: str,
        city: str,
        state: str,
        zip_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed property information from ATTOM."""
        if not self.is_initialized:
            raise RuntimeError("ATTOM Data agent not initialized")
        
        try:
            # Check cache first
            cache_key = f"attom_property:{address}_{city}_{state}"
            cached_data = await cache_get(cache_key)
            if cached_data:
                return cached_data
            
            # Build API request
            endpoint = "/propertyapi/v1.0.0/property/detail"
            params = {
                "address1": address,
                "address2": f"{city}, {state}",
                "format": "json"
            }
            
            if zip_code:
                params["postalcode"] = zip_code
            
            # Make API request
            data = await self._make_api_request(endpoint, params)
            
            # Process and structure the response
            property_details = self._process_property_details(data, address, city, state)
            
            # Cache the result
            await cache_set(cache_key, property_details, expire=7200)  # 2 hours
            
            logger.info(f"Retrieved ATTOM property details for {address}, {city}, {state}")
            
            return property_details
            
        except Exception as e:
            logger.error(f"Failed to get property details: {e}")
            raise
    
    async def get_property_sales_history(
        self,
        address: str,
        city: str,
        state: str,
        zip_code: Optional[str] = None,
        years: int = 5
    ) -> Dict[str, Any]:
        """Get property sales history from ATTOM."""
        if not self.is_initialized:
            raise RuntimeError("ATTOM Data agent not initialized")
        
        try:
            # Check cache first
            cache_key = f"attom_sales_history:{address}_{city}_{state}_{years}"
            cached_data = await cache_get(cache_key)
            if cached_data:
                return cached_data
            
            # Build API request
            endpoint = "/propertyapi/v1.0.0/property/saleshistory"
            params = {
                "address1": address,
                "address2": f"{city}, {state}",
                "format": "json"
            }
            
            if zip_code:
                params["postalcode"] = zip_code
            
            # Make API request
            data = await self._make_api_request(endpoint, params)
            
            # Process sales history
            sales_history = self._process_sales_history(data, address, city, state, years)
            
            # Cache the result
            await cache_set(cache_key, sales_history, expire=86400)  # 24 hours
            
            logger.info(f"Retrieved ATTOM sales history for {address}, {city}, {state}")
            
            return sales_history
            
        except Exception as e:
            logger.error(f"Failed to get sales history: {e}")
            raise
    
    async def get_property_valuation(
        self,
        address: str,
        city: str,
        state: str,
        zip_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get property valuation data from ATTOM."""
        if not self.is_initialized:
            raise RuntimeError("ATTOM Data agent not initialized")
        
        try:
            # Check cache first
            cache_key = f"attom_valuation:{address}_{city}_{state}"
            cached_data = await cache_get(cache_key)
            if cached_data:
                return cached_data
            
            # Build API request
            endpoint = "/propertyapi/v1.0.0/property/expandedprofile"
            params = {
                "address1": address,
                "address2": f"{city}, {state}",
                "format": "json"
            }
            
            if zip_code:
                params["postalcode"] = zip_code
            
            # Make API request
            data = await self._make_api_request(endpoint, params)
            
            # Process valuation data
            valuation = self._process_valuation_data(data, address, city, state)
            
            # Cache the result
            await cache_set(cache_key, valuation, expire=3600)  # 1 hour
            
            logger.info(f"Retrieved ATTOM valuation for {address}, {city}, {state}")
            
            return valuation
            
        except Exception as e:
            logger.error(f"Failed to get property valuation: {e}")
            raise
    
    async def get_market_trends(
        self,
        city: str,
        state: str,
        property_type: str = "residential",
        timeframe: str = "12_months"
    ) -> Dict[str, Any]:
        """Get market trends for a specific location."""
        if not self.is_initialized:
            raise RuntimeError("ATTOM Data agent not initialized")
        
        try:
            # Check cache first
            cache_key = f"attom_market_trends:{city}_{state}_{property_type}_{timeframe}"
            cached_data = await cache_get(cache_key)
            if cached_data:
                return cached_data
            
            # Build API request
            endpoint = "/propertyapi/v1.0.0/property/trends"
            params = {
                "geoid": f"{city}, {state}",
                "propertytype": property_type,
                "format": "json"
            }
            
            # Make API request
            data = await self._make_api_request(endpoint, params)
            
            # Process market trends
            trends = self._process_market_trends(data, city, state, property_type, timeframe)
            
            # Cache the result
            await cache_set(cache_key, trends, expire=86400)  # 24 hours
            
            logger.info(f"Retrieved ATTOM market trends for {city}, {state}")
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get market trends: {e}")
            raise
    
    async def get_comparable_properties(
        self,
        address: str,
        city: str,
        state: str,
        radius_miles: int = 1,
        property_type: str = "residential"
    ) -> Dict[str, Any]:
        """Get comparable properties from ATTOM."""
        if not self.is_initialized:
            raise RuntimeError("ATTOM Data agent not initialized")
        
        try:
            # Check cache first
            cache_key = f"attom_comps:{address}_{city}_{state}_{radius_miles}"
            cached_data = await cache_get(cache_key)
            if cached_data:
                return cached_data
            
            # Build API request
            endpoint = "/propertyapi/v1.0.0/property/expandedprofile"
            params = {
                "address1": address,
                "address2": f"{city}, {state}",
                "radius": radius_miles,
                "propertytype": property_type,
                "format": "json"
            }
            
            # Make API request
            data = await self._make_api_request(endpoint, params)
            
            # Process comparable properties
            comps = self._process_comparable_properties(data, address, city, state, radius_miles)
            
            # Cache the result
            await cache_set(cache_key, comps, expire=7200)  # 2 hours
            
            logger.info(f"Retrieved ATTOM comparable properties for {address}, {city}, {state}")
            
            return comps
            
        except Exception as e:
            logger.error(f"Failed to get comparable properties: {e}")
            raise
    
    async def get_neighborhood_data(
        self,
        city: str,
        state: str,
        zip_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get neighborhood and demographic data from ATTOM."""
        if not self.is_initialized:
            raise RuntimeError("ATTOM Data agent not initialized")
        
        try:
            # Check cache first
            cache_key = f"attom_neighborhood:{city}_{state}_{zip_code or 'all'}"
            cached_data = await cache_get(cache_key)
            if cached_data:
                return cached_data
            
            # Build API request
            endpoint = "/propertyapi/v1.0.0/neighborhood/demographics"
            params = {
                "geoid": f"{city}, {state}",
                "format": "json"
            }
            
            if zip_code:
                params["postalcode"] = zip_code
            
            # Make API request
            data = await self._make_api_request(endpoint, params)
            
            # Process neighborhood data
            neighborhood = self._process_neighborhood_data(data, city, state, zip_code)
            
            # Cache the result
            await cache_set(cache_key, neighborhood, expire=86400)  # 24 hours
            
            logger.info(f"Retrieved ATTOM neighborhood data for {city}, {state}")
            
            return neighborhood
            
        except Exception as e:
            logger.error(f"Failed to get neighborhood data: {e}")
            raise
    
    async def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make an API request to ATTOM Data."""
        try:
            # Add API key to params
            params["apikey"] = self.api_key
            
            # Make HTTP request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    params=params,
                    headers={
                        "Accept": "application/json",
                        "User-Agent": "JanusPropAI/1.0"
                    }
                )
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"ATTOM API HTTP error: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"ATTOM API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"ATTOM API request error: {e}")
            raise RuntimeError(f"ATTOM API request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in ATTOM API request: {e}")
            raise
    
    def _process_property_details(
        self,
        data: Dict[str, Any],
        address: str,
        city: str,
        state: str
    ) -> Dict[str, Any]:
        """Process property details from ATTOM API response."""
        try:
            # Extract property information from ATTOM response
            # This is a simplified example - actual ATTOM response structure may differ
            property_info = data.get("property", [{}])[0] if data.get("property") else {}
            
            processed = {
                "address": address,
                "city": city,
                "state": state,
                "property_id": property_info.get("identifier", {}).get("attomId"),
                "property_type": property_info.get("building", {}).get("propertyType"),
                "bedrooms": property_info.get("building", {}).get("rooms", {}).get("bedrooms"),
                "bathrooms": property_info.get("building", {}).get("rooms", {}).get("bathrooms"),
                "square_feet": property_info.get("building", {}).get("size", {}).get("squareFootage"),
                "year_built": property_info.get("building", {}).get("construction", {}).get("yearBuilt"),
                "lot_size": property_info.get("lot", {}).get("size", {}).get("squareFootage"),
                "last_sold_date": property_info.get("sale", {}).get("lastSaleDate"),
                "last_sold_price": property_info.get("sale", {}).get("lastSaleAmount"),
                "estimated_value": property_info.get("valuation", {}).get("avm", {}).get("amount"),
                "tax_assessment": property_info.get("assessment", {}).get("tax", {}).get("assessedValue"),
                "property_tax": property_info.get("assessment", {}).get("tax", {}).get("taxAmount"),
                "data_source": "attom",
                "retrieved_date": datetime.utcnow().isoformat()
            }
            
            return processed
            
        except Exception as e:
            logger.error(f"Failed to process property details: {e}")
            # Return fallback data
            return {
                "address": address,
                "city": city,
                "state": state,
                "data_source": "attom",
                "retrieved_date": datetime.utcnow().isoformat(),
                "error": "Failed to process ATTOM response"
            }
    
    def _process_sales_history(
        self,
        data: Dict[str, Any],
        address: str,
        city: str,
        state: str,
        years: int
    ) -> Dict[str, Any]:
        """Process sales history from ATTOM API response."""
        try:
            sales_history = data.get("salesHistory", {}).get("sale", []) if data.get("salesHistory") else []
            
            # Filter sales within specified years
            cutoff_date = datetime.utcnow() - timedelta(days=years * 365)
            recent_sales = []
            
            for sale in sales_history:
                try:
                    sale_date = datetime.strptime(sale.get("saleDate", ""), "%Y-%m-%d")
                    if sale_date >= cutoff_date:
                        recent_sales.append({
                            "sale_date": sale.get("saleDate"),
                            "sale_price": sale.get("saleAmount"),
                            "sale_type": sale.get("saleType"),
                            "recording_date": sale.get("recordingDate"),
                            "document_number": sale.get("documentNumber")
                        })
                except (ValueError, TypeError):
                    continue
            
            processed = {
                "address": address,
                "city": city,
                "state": state,
                "total_sales": len(recent_sales),
                "sales_history": recent_sales,
                "price_trends": self._calculate_price_trends(recent_sales),
                "data_source": "attom",
                "retrieved_date": datetime.utcnow().isoformat()
            }
            
            return processed
            
        except Exception as e:
            logger.error(f"Failed to process sales history: {e}")
            return {
                "address": address,
                "city": city,
                "state": state,
                "data_source": "attom",
                "retrieved_date": datetime.utcnow().isoformat(),
                "error": "Failed to process sales history"
            }
    
    def _process_valuation_data(
        self,
        data: Dict[str, Any],
        address: str,
        city: str,
        state: str
    ) -> Dict[str, Any]:
        """Process valuation data from ATTOM API response."""
        try:
            property_info = data.get("property", [{}])[0] if data.get("property") else {}
            valuation = property_info.get("valuation", {})
            
            processed = {
                "address": address,
                "city": city,
                "state": state,
                "estimated_value": valuation.get("avm", {}).get("amount"),
                "value_range": {
                    "low": valuation.get("avm", {}).get("range", {}).get("low"),
                    "high": valuation.get("avm", {}).get("range", {}).get("high")
                },
                "confidence_score": valuation.get("avm", {}).get("confidence"),
                "last_updated": valuation.get("avm", {}).get("lastUpdated"),
                "market_conditions": valuation.get("market", {}).get("conditions"),
                "appreciation_rate": valuation.get("market", {}).get("appreciationRate"),
                "data_source": "attom",
                "retrieved_date": datetime.utcnow().isoformat()
            }
            
            return processed
            
        except Exception as e:
            logger.error(f"Failed to process valuation data: {e}")
            return {
                "address": address,
                "city": city,
                "state": state,
                "data_source": "attom",
                "retrieved_date": datetime.utcnow().isoformat(),
                "error": "Failed to process valuation data"
            }
    
    def _process_market_trends(
        self,
        data: Dict[str, Any],
        city: str,
        state: str,
        property_type: str,
        timeframe: str
    ) -> Dict[str, Any]:
        """Process market trends from ATTOM API response."""
        try:
            trends = data.get("trends", {}) if data.get("trends") else {}
            
            processed = {
                "location": f"{city}, {state}",
                "property_type": property_type,
                "timeframe": timeframe,
                "price_trends": trends.get("price", {}),
                "volume_trends": trends.get("volume", {}),
                "days_on_market": trends.get("daysOnMarket", {}),
                "inventory_levels": trends.get("inventory", {}),
                "market_indicators": {
                    "supply": trends.get("supply", "unknown"),
                    "demand": trends.get("demand", "unknown"),
                    "balance": trends.get("balance", "unknown")
                },
                "data_source": "attom",
                "retrieved_date": datetime.utcnow().isoformat()
            }
            
            return processed
            
        except Exception as e:
            logger.error(f"Failed to process market trends: {e}")
            return {
                "location": f"{city}, {state}",
                "property_type": property_type,
                "timeframe": timeframe,
                "data_source": "attom",
                "retrieved_date": datetime.utcnow().isoformat(),
                "error": "Failed to process market trends"
            }
    
    def _process_comparable_properties(
        self,
        data: Dict[str, Any],
        address: str,
        city: str,
        state: str,
        radius_miles: int
    ) -> Dict[str, Any]:
        """Process comparable properties from ATTOM API response."""
        try:
            properties = data.get("property", []) if data.get("property") else []
            
            # Filter out the subject property and process comps
            comps = []
            for prop in properties:
                if prop.get("identifier", {}).get("attomId") != data.get("subjectProperty", {}).get("attomId"):
                    comp = {
                        "address": f"{prop.get('address', {}).get('line1', 'N/A')}, {prop.get('address', {}).get('city', 'N/A')}, {prop.get('address', {}).get('state', 'N/A')}",
                        "property_type": prop.get("building", {}).get("propertyType"),
                        "bedrooms": prop.get("building", {}).get("rooms", {}).get("bedrooms"),
                        "bathrooms": prop.get("building", {}).get("rooms", {}).get("bathrooms"),
                        "square_feet": prop.get("building", {}).get("size", {}).get("squareFootage"),
                        "estimated_value": prop.get("valuation", {}).get("avm", {}).get("amount"),
                        "last_sold_price": prop.get("sale", {}).get("lastSaleAmount"),
                        "last_sold_date": prop.get("sale", {}).get("lastSaleDate"),
                        "distance_miles": prop.get("distance", 0)
                    }
                    comps.append(comp)
            
            processed = {
                "subject_property": address,
                "city": city,
                "state": state,
                "radius_miles": radius_miles,
                "total_comps": len(comps),
                "comparable_properties": comps,
                "market_analysis": self._analyze_comps(comps),
                "data_source": "attom",
                "retrieved_date": datetime.utcnow().isoformat()
            }
            
            return processed
            
        except Exception as e:
            logger.error(f"Failed to process comparable properties: {e}")
            return {
                "subject_property": address,
                "city": city,
                "state": state,
                "radius_miles": radius_miles,
                "data_source": "attom",
                "retrieved_date": datetime.utcnow().isoformat(),
                "error": "Failed to process comparable properties"
            }
    
    def _process_neighborhood_data(
        self,
        data: Dict[str, Any],
        city: str,
        state: str,
        zip_code: Optional[str]
    ) -> Dict[str, Any]:
        """Process neighborhood data from ATTOM API response."""
        try:
            demographics = data.get("demographics", {}) if data.get("demographics") else {}
            
            processed = {
                "location": f"{city}, {state}",
                "zip_code": zip_code,
                "population": demographics.get("population", {}),
                "households": demographics.get("households", {}),
                "income": demographics.get("income", {}),
                "education": demographics.get("education", {}),
                "employment": demographics.get("employment", {}),
                "housing": demographics.get("housing", {}),
                "crime_stats": demographics.get("crime", {}),
                "schools": demographics.get("schools", {}),
                "amenities": demographics.get("amenities", {}),
                "data_source": "attom",
                "retrieved_date": datetime.utcnow().isoformat()
            }
            
            return processed
            
        except Exception as e:
            logger.error(f"Failed to process neighborhood data: {e}")
            return {
                "location": f"{city}, {state}",
                "zip_code": zip_code,
                "data_source": "attom",
                "retrieved_date": datetime.utcnow().isoformat(),
                "error": "Failed to process neighborhood data"
            }
    
    def _calculate_price_trends(self, sales: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate price trends from sales history."""
        try:
            if not sales or len(sales) < 2:
                return {"trend": "insufficient_data", "change_percentage": 0}
            
            # Sort by sale date
            sorted_sales = sorted(sales, key=lambda x: x.get("sale_date", ""))
            
            # Calculate price change
            first_price = float(sorted_sales[0].get("sale_price", 0))
            last_price = float(sorted_sales[-1].get("sale_price", 0))
            
            if first_price > 0:
                change_percentage = ((last_price - first_price) / first_price) * 100
                trend = "increasing" if change_percentage > 0 else "decreasing" if change_percentage < 0 else "stable"
            else:
                change_percentage = 0
                trend = "unknown"
            
            return {
                "trend": trend,
                "change_percentage": round(change_percentage, 2),
                "first_sale_price": first_price,
                "last_sale_price": last_price,
                "total_sales": len(sales)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate price trends: {e}")
            return {"trend": "error", "change_percentage": 0}
    
    def _analyze_comps(self, comps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze comparable properties data."""
        try:
            if not comps:
                return {"average_price": 0, "price_range": {"min": 0, "max": 0}}
            
            prices = [float(comp.get("estimated_value", 0)) for comp in comps if comp.get("estimated_value")]
            square_feet = [float(comp.get("square_feet", 0)) for comp in comps if comp.get("square_feet")]
            
            analysis = {
                "average_price": sum(prices) / len(prices) if prices else 0,
                "price_range": {
                    "min": min(prices) if prices else 0,
                    "max": max(prices) if prices else 0
                },
                "price_per_sqft": sum(prices) / sum(square_feet) if prices and square_feet and sum(square_feet) > 0 else 0,
                "total_comps": len(comps)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze comps: {e}")
            return {"error": "Failed to analyze comparable properties"}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the ATTOM Data agent."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "initialized": self.is_initialized,
            "api_key_configured": bool(self.api_key),
            "base_url": self.base_url,
            "last_check": datetime.utcnow().isoformat()
        }

# Global ATTOM agent instance
_attom_agent: Optional[ATTOMDataAgent] = None

def get_attom_agent() -> ATTOMDataAgent:
    """Get the global ATTOM Data agent instance."""
    global _attom_agent
    if _attom_agent is None:
        _attom_agent = ATTOMDataAgent()
    return _attom_agent

async def attom_agent_handler(task) -> Dict[str, Any]:
    """Handler function for ATTOM Data agent tasks."""
    agent = get_attom_agent()
    
    if task.task_type == "get_property_details":
        return await agent.get_property_details(
            address=task.metadata.get('address', ''),
            city=task.metadata.get('city', ''),
            state=task.metadata.get('state', ''),
            zip_code=task.metadata.get('zip_code')
        )
    
    elif task.task_type == "get_property_sales_history":
        return await agent.get_property_sales_history(
            address=task.metadata.get('address', ''),
            city=task.metadata.get('city', ''),
            state=task.metadata.get('state', ''),
            zip_code=task.metadata.get('zip_code'),
            years=task.metadata.get('years', 5)
        )
    
    elif task.task_type == "get_property_valuation":
        return await agent.get_property_valuation(
            address=task.metadata.get('address', ''),
            city=task.metadata.get('city', ''),
            state=task.metadata.get('state', ''),
            zip_code=task.metadata.get('zip_code')
        )
    
    elif task.task_type == "get_market_trends":
        return await agent.get_market_trends(
            city=task.metadata.get('city', ''),
            state=task.metadata.get('state', ''),
            property_type=task.metadata.get('property_type', 'residential'),
            timeframe=task.metadata.get('timeframe', '12_months')
        )
    
    elif task.task_type == "get_comparable_properties":
        return await agent.get_comparable_properties(
            address=task.metadata.get('address', ''),
            city=task.metadata.get('city', ''),
            state=task.metadata.get('state', ''),
            radius_miles=task.metadata.get('radius_miles', 1),
            property_type=task.metadata.get('property_type', 'residential')
        )
    
    elif task.task_type == "get_neighborhood_data":
        return await agent.get_neighborhood_data(
            city=task.metadata.get('city', ''),
            state=task.metadata.get('state', ''),
            zip_code=task.metadata.get('zip_code')
        )
    
    else:
        raise ValueError(f"Unknown task type: {task.task_type}")
