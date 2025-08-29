"""
Data Integration Agent for Real Estate AI System

This agent handles data integration from multiple sources including:
- Realie API (immediate integration for speed and freshness)
- ATTOM Data (historical data and deeper analytics)
- Architecture designed for easy swapping/adding of new data sources
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import structlog
from pydantic import BaseModel, Field
import json

from agents.base_agent import BaseAgent, AgentConfig, AgentResponse


class DataSource(BaseModel):
    """Configuration for a data source."""
    
    source_id: str
    name: str
    type: str  # "api", "database", "file", "stream"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    rate_limit: Optional[int] = None  # requests per minute
    last_sync: Optional[datetime] = None
    status: str = "active"  # active, inactive, error
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PropertyData(BaseModel):
    """Standardized property data structure."""
    
    property_id: str
    address: str
    city: str
    state: str
    zip_code: str
    property_type: str
    square_feet: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    lot_size: Optional[float] = None
    year_built: Optional[int] = None
    last_sold_date: Optional[datetime] = None
    last_sold_price: Optional[float] = None
    estimated_value: Optional[float] = None
    estimated_monthly_rent: Optional[float] = None
    market_conditions: Dict[str, Any] = Field(default_factory=dict)
    comparable_sales: List[Dict[str, Any]] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DataIntegrationAgent(BaseAgent):
    """
    Agent responsible for integrating data from multiple sources.
    
    Features:
    - Realie API integration for immediate property coverage
    - ATTOM data preparation and integration
    - Modular architecture for easy data source swapping
    - Data standardization and quality control
    - Rate limiting and error handling
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.logger = structlog.get_logger(self.__class__.__name__)
        self.data_sources: Dict[str, DataSource] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiters: Dict[str, Any] = {}
        
        # Initialize default data sources
        self._initialize_default_sources()
    
    def _get_supported_operations(self) -> List[str]:
        """Return list of operations this agent supports."""
        return [
            "fetch_property_data",
            "search_properties",
            "sync_data_source",
            "get_data_quality_metrics",
            "add_data_source",
            "remove_data_source"
        ]

    async def _process_request_impl(
        self,
        request: Union[str, Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a data integration request."""
        if isinstance(request, str):
            response = await self._handle_text_request(request, context)
        else:
            response = await self._handle_structured_request(request, context)

        if response.success:
            return response.data
        else:
            raise Exception(response.error)
    
    async def start(self):
        """Start the data integration agent."""
        await super().start()
        
        # Initialize HTTP session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "Janus-Prop-AI/1.0"}
        )
        
        self.logger.info("Data Integration Agent started")
    
    async def shutdown(self):
        """Shutdown the agent."""
        if self.session:
            await self.session.close()
        self.logger.info("Data Integration Agent shutting down")
        await super().shutdown()
    
    def _initialize_default_sources(self):
        """Initialize default data sources."""
        # Realie API source (immediate integration)
        realie_source = DataSource(
            source_id="realie_api",
            name="Realie API",
            type="api",
            base_url="https://api.realie.com/v1",  # Placeholder URL
            api_key=None,  # Will be loaded from environment
            rate_limit=60,  # 60 requests per minute
            status="active"
        )
        self.data_sources["realie_api"] = realie_source
        
        # ATTOM Data source (preparation for future integration)
        attom_source = DataSource(
            source_id="attom_data",
            name="ATTOM Data",
            type="api",
            base_url="https://api.attomdata.com/v3.0",  # Placeholder URL
            api_key=None,  # Will be loaded from environment
            rate_limit=30,  # 30 requests per minute
            status="inactive"  # Not yet integrated
        )
        self.data_sources["attom_data"] = attom_source
    
    async def _handle_text_request(self, request: str, context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Handle natural language requests."""
        # Simple keyword-based routing for now
        request_lower = request.lower()
        
        if "property" in request_lower and "search" in request_lower:
            return await self._search_properties_from_text(request, context)
        elif "sync" in request_lower or "update" in request_lower:
            return await self._sync_data_sources_from_text(request, context)
        else:
            return AgentResponse(
                success=True,
                data={
                    "message": "Text-based requests supported for property search and data sync",
                    "examples": [
                        "Search for properties in downtown area",
                        "Sync data from Realie API",
                        "Update property data for 123 Main St"
                    ]
                }
            )
    
    async def _handle_structured_request(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Handle structured requests."""
        request_type = request.get("type")
        
        if request_type == "fetch_property_data":
            return await self._fetch_property_data(request, context)
        elif request_type == "search_properties":
            return await self._search_properties(request, context)
        elif request_type == "sync_data_source":
            return await self._sync_data_source(request, context)
        elif request_type == "add_data_source":
            return await self._add_data_source(request, context)
        else:
            return AgentResponse(
                success=False,
                error=f"Unsupported request type: {request_type}",
                data=None
            )
    
    async def _fetch_property_data(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Fetch property data from available sources."""
        try:
            property_id = request.get("property_id")
            address = request.get("address")
            
            if not property_id and not address:
                return AgentResponse(
                    success=False,
                    error="Either property_id or address is required",
                    data=None
                )
            
            # Try to fetch from Realie API first (fastest)
            if "realie_api" in self.data_sources and self.data_sources["realie_api"].status == "active":
                try:
                    property_data = await self._fetch_from_realie(property_id, address)
                    if property_data:
                        return AgentResponse(
                            success=True,
                            data=property_data.dict()
                        )
                except Exception as e:
                    self.logger.warning("Failed to fetch from Realie API", error=str(e))
            
            # Fallback to other sources or return cached data
            return AgentResponse(
                success=True,
                data={
                    "message": "Property data not available from active sources",
                    "property_id": property_id,
                    "address": address,
                    "available_sources": [s.source_id for s in self.data_sources.values() if s.status == "active"]
                }
            )
            
        except Exception as e:
            self.logger.error("Error fetching property data", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Failed to fetch property data: {str(e)}",
                data=None
            )
    
    async def _fetch_from_realie(self, property_id: Optional[str], address: Optional[str]) -> Optional[PropertyData]:
        """Fetch property data from Realie API."""
        if not self.session:
            return None
        
        # This is a placeholder implementation
        # In production, you would:
        # 1. Load API key from environment
        # 2. Make actual API calls to Realie
        # 3. Handle rate limiting
        # 4. Parse and standardize the response
        
        try:
            # Simulate API call
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # Return mock data for demonstration
            if address:
                return PropertyData(
                    property_id=property_id or f"realie_{hash(address)}",
                    address=address,
                    city="Sample City",
                    state="CA",
                    zip_code="90210",
                    property_type="Single Family",
                    square_feet=2000.0,
                    bedrooms=3,
                    bathrooms=2.5,
                    lot_size=5000.0,
                    year_built=1990,
                    estimated_value=750000.0,
                    estimated_monthly_rent=3500.0,
                    market_conditions={
                        "price_trend": "rising",
                        "days_on_market": 15,
                        "market_volatility": "low"
                    },
                    data_sources=["realie_api"]
                )
            
        except Exception as e:
            self.logger.error("Error fetching from Realie API", error=str(e))
            return None
        
        return None
    
    async def _search_properties(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Search for properties based on criteria."""
        try:
            search_criteria = request.get("criteria", {})
            limit = request.get("limit", 50)
            
            # Validate search criteria
            if not search_criteria:
                return AgentResponse(
                    success=False,
                    error="Search criteria are required",
                    data=None
                )
            
            # Search from available sources
            results = []
            
            if "realie_api" in self.data_sources and self.data_sources["realie_api"].status == "active":
                try:
                    realie_results = await self._search_realie_api(search_criteria, limit)
                    results.extend(realie_results)
                except Exception as e:
                    self.logger.warning("Realie API search failed", error=str(e))
            
            return AgentResponse(
                success=True,
                data={
                    "properties": [prop.dict() for prop in results[:limit]],
                    "total_found": len(results),
                    "sources_queried": [s.source_id for s in self.data_sources.values() if s.status == "active"]
                }
            )
            
        except Exception as e:
            self.logger.error("Error searching properties", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Property search failed: {str(e)}",
                data=None
            )
    
    async def _search_realie_api(self, criteria: Dict[str, Any], limit: int) -> List[PropertyData]:
        """Search properties using Realie API."""
        # Placeholder implementation
        # In production, this would make actual API calls
        
        results = []
        
        # Generate mock results based on criteria
        city = criteria.get("city", "Sample City")
        min_price = criteria.get("min_price", 0)
        max_price = criteria.get("max_price", 1000000)
        
        for i in range(min(limit, 10)):  # Generate up to 10 mock results
            property_data = PropertyData(
                property_id=f"realie_search_{i}",
                address=f"{100 + i} Sample St",
                city=city,
                state="CA",
                zip_code="90210",
                property_type="Single Family",
                square_feet=1500.0 + (i * 100),
                bedrooms=2 + (i % 3),
                bathrooms=1.5 + (i % 2),
                estimated_value=min_price + (i * 50000),
                data_sources=["realie_api"]
            )
            results.append(property_data)
        
        return results
    
    async def _search_properties_from_text(self, request: str, context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Search properties from natural language request."""
        # Simple keyword extraction
        # In production, use NLP for better understanding
        
        criteria = {}
        
        if "downtown" in request.lower():
            criteria["city"] = "Downtown"
        if "house" in request.lower():
            criteria["property_type"] = "Single Family"
        if "apartment" in request.lower():
            criteria["property_type"] = "Apartment"
        
        return await self._search_properties({
            "type": "search_properties",
            "criteria": criteria,
            "limit": 20
        }, context)
    
    async def _sync_data_source(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Sync data from a specific source."""
        try:
            source_id = request.get("source_id")
            
            if not source_id:
                return AgentResponse(
                    success=False,
                    error="Source ID is required for sync",
                    data=None
                )
            
            if source_id not in self.data_sources:
                return AgentResponse(
                    success=False,
                    error=f"Data source {source_id} not found",
                    data=None
                )
            
            source = self.data_sources[source_id]
            
            if source.status != "active":
                return AgentResponse(
                    success=False,
                    error=f"Data source {source_id} is not active",
                    data=None
                )
            
            # Perform sync
            sync_result = await self._perform_sync(source)
            
            # Update last sync time
            source.last_sync = datetime.utcnow()
            
            return AgentResponse(
                success=True,
                data={
                    "source_id": source_id,
                    "sync_result": sync_result,
                    "last_sync": source.last_sync.isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error("Error syncing data source", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Data source sync failed: {str(e)}",
                data=None
            )
    
    async def _sync_data_sources_from_text(self, request: str, context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Sync data sources from natural language request."""
        # Determine which source to sync
        if "realie" in request.lower():
            source_id = "realie_api"
        elif "attom" in request.lower():
            source_id = "attom_data"
        else:
            source_id = "realie_api"  # Default to Realie
        
        return await self._sync_data_source({
            "type": "sync_data_source",
            "source_id": source_id
        }, context)
    
    async def _perform_sync(self, source: DataSource) -> Dict[str, Any]:
        """Perform actual data synchronization."""
        # Placeholder implementation
        # In production, this would:
        # 1. Check rate limits
        # 2. Make API calls
        # 3. Process and store data
        # 4. Handle errors and retries
        
        await asyncio.sleep(0.5)  # Simulate sync time
        
        return {
            "status": "completed",
            "records_processed": 100,
            "errors": 0,
            "sync_duration_ms": 500
        }
    
    async def _add_data_source(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Add a new data source."""
        try:
            source_config = request.get("source_config", {})
            
            if not source_config.get("source_id"):
                return AgentResponse(
                    success=False,
                    error="Source ID is required",
                    data=None
                )
            
            source_id = source_config["source_id"]
            
            if source_id in self.data_sources:
                return AgentResponse(
                    success=False,
                    error=f"Data source {source_id} already exists",
                    data=None
                )
            
            # Create new data source
            new_source = DataSource(**source_config)
            self.data_sources[source_id] = new_source
            
            self.logger.info("New data source added", source_id=source_id, name=new_source.name)
            
            return AgentResponse(
                success=True,
                data={
                    "message": f"Data source {source_id} added successfully",
                    "source": new_source.dict()
                }
            )
            
        except Exception as e:
            self.logger.error("Error adding data source", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Failed to add data source: {str(e)}",
                data=None
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of this agent."""
        return {
            "status": "healthy",
            "agent_type": "data_integration",
            "capabilities": await self.get_capabilities(),
            "data_sources": {
                source_id: {
                    "name": source.name,
                    "status": source.status,
                    "last_sync": source.last_sync.isoformat() if source.last_sync else None
                }
                for source_id, source in self.data_sources.items()
            },
            "last_check": datetime.utcnow().isoformat()
        }
