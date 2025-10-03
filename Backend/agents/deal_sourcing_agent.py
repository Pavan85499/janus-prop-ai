"""
Deal Sourcing & Discovery Agent for Janus Prop AI Backend

This agent specializes in scanning millions of properties for distressed, 
undervalued, or high-potential assets and surfacing leads with explainable insights.
"""

import asyncio
import structlog
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import math
from dataclasses import dataclass

try:
    import google.generativeai as genai
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.schema import HumanMessage, SystemMessage
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from config.settings import get_settings
from core.redis_client import cache_get, cache_set, publish_event
from core.websocket_manager import get_websocket_manager

logger = structlog.get_logger(__name__)

@dataclass
class PropertyLead:
    """Represents a property lead discovered by the agent."""
    property_id: str
    address: str
    coordinates: Tuple[float, float]  # (lat, lng)
    price: float
    estimated_value: float
    equity_potential: float
    distress_level: str  # "low", "medium", "high", "critical"
    lead_score: float  # 0-100
    opportunity_type: str  # "distressed", "undervalued", "high_potential", "foreclosure"
    insights: List[str]
    confidence_score: float
    data_sources: List[str]
    discovered_at: datetime
    metadata: Dict[str, Any]

@dataclass
class MarketScanResult:
    """Result of market scanning operation."""
    scan_id: str
    location: str
    scan_parameters: Dict[str, Any]
    total_properties_scanned: int
    leads_discovered: int
    high_priority_leads: int
    scan_duration: float
    leads: List[PropertyLead]
    market_insights: Dict[str, Any]
    scan_timestamp: datetime

class DealSourcingAgent:
    """AI Agent specialized in deal sourcing and property discovery."""
    
    def __init__(self):
        self.agent_id = "deal_sourcing_agent"
        self.name = "Deal Sourcing Agent"
        self.settings = get_settings()
        self.gemini_api_key = self.settings.GEMINI_API_KEY
        self.attom_api_key = self.settings.ATTOM_API_KEY
        self.rapidapi_key = self.settings.RAPIDAPI_KEY
        self.is_initialized = False
        
        # Property scoring weights
        self.scoring_weights = {
            "price_to_value_ratio": 0.25,
            "distress_indicators": 0.30,
            "market_growth_potential": 0.20,
            "location_quality": 0.15,
            "property_condition": 0.10
        }
        
        # Distress indicators to look for
        self.distress_indicators = [
            "foreclosure",
            "pre_foreclosure", 
            "auction",
            "tax_lien",
            "bankruptcy",
            "divorce",
            "estate_sale",
            "vacant",
            "distressed_sale",
            "motivated_seller",
            "price_reduction",
            "high_days_on_market"
        ]
        
        if self._has_required_apis():
            self._initialize_agent()
    
    def _has_required_apis(self) -> bool:
        """Check if required API keys are available."""
        return bool(self.gemini_api_key)
    
    def _initialize_agent(self):
        """Initialize the deal sourcing agent."""
        try:
            if GEMINI_AVAILABLE and self.gemini_api_key:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel("gemini-pro")
                self.chat_model = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=self.gemini_api_key,
                    temperature=0.3,
                    max_output_tokens=4096
                )
            
            self.is_initialized = True
            logger.info("Deal Sourcing Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Deal Sourcing Agent: {e}")
            self.is_initialized = False
    
    async def scan_market_for_deals(
        self,
        location: str,
        max_price: Optional[float] = None,
        property_types: Optional[List[str]] = None,
        min_equity_potential: float = 20000,
        scan_radius_miles: float = 25
    ) -> MarketScanResult:
        """
        Scan a market area for potential deals and distressed properties.
        
        Args:
            location: Target location (city, zip, or coordinates)
            max_price: Maximum property price to consider
            property_types: Types of properties to scan (residential, commercial, etc.)
            min_equity_potential: Minimum equity potential in USD
            scan_radius_miles: Radius in miles to scan around location
        """
        start_time = datetime.utcnow()
        scan_id = f"scan_{int(start_time.timestamp())}"
        
        try:
            # Step 1: Get properties from multiple data sources
            properties = await self._fetch_properties_multi_source(
                location, max_price, property_types, scan_radius_miles
            )
            
            # Step 2: Analyze each property for investment potential
            leads = []
            for prop in properties:
                lead = await self._analyze_property_for_deal_potential(prop)
                if lead and lead.equity_potential >= min_equity_potential:
                    leads.append(lead)
            
            # Step 3: Score and rank leads
            scored_leads = await self._score_and_rank_leads(leads, location)
            
            # Step 4: Generate market insights
            market_insights = await self._generate_market_insights(
                location, properties, scored_leads
            )
            
            # Calculate scan metrics
            scan_duration = (datetime.utcnow() - start_time).total_seconds()
            high_priority_count = len([l for l in scored_leads if l.lead_score >= 80])
            
            result = MarketScanResult(
                scan_id=scan_id,
                location=location,
                scan_parameters={
                    "max_price": max_price,
                    "property_types": property_types or ["all"],
                    "min_equity_potential": min_equity_potential,
                    "scan_radius_miles": scan_radius_miles
                },
                total_properties_scanned=len(properties),
                leads_discovered=len(scored_leads),
                high_priority_leads=high_priority_count,
                scan_duration=scan_duration,
                leads=scored_leads[:50],  # Return top 50 leads
                market_insights=market_insights,
                scan_timestamp=start_time
            )
            
            # Cache results
            await cache_set(f"market_scan:{scan_id}", result.__dict__, expire=7200)
            
            # Publish real-time update
            await self._publish_scan_update(result)
            
            logger.info(f"Market scan completed: {len(scored_leads)} leads found")
            return result
            
        except Exception as e:
            logger.error(f"Market scan failed: {e}")
            raise
    
    async def analyze_distressed_properties(
        self,
        properties: List[Dict[str, Any]]
    ) -> List[PropertyLead]:
        """Analyze properties specifically for distress indicators."""
        leads = []
        
        for prop in properties:
            try:
                # Check for distress indicators
                distress_score = await self._calculate_distress_score(prop)
                
                if distress_score > 0.6:  # High distress threshold
                    lead = await self._create_distressed_property_lead(prop, distress_score)
                    if lead:
                        leads.append(lead)
                        
            except Exception as e:
                logger.warning(f"Failed to analyze property {prop.get('id', 'unknown')}: {e}")
        
        return leads
    
    async def _fetch_properties_multi_source(
        self,
        location: str,
        max_price: Optional[float],
        property_types: Optional[List[str]],
        radius_miles: float
    ) -> List[Dict[str, Any]]:
        """Fetch properties from multiple data sources."""
        all_properties = []
        
        # Fetch from different sources (mock data for now - replace with real APIs)
        sources = [
            self._fetch_from_mls(location, max_price, property_types, radius_miles),
            self._fetch_from_public_records(location, max_price, radius_miles),
            self._fetch_from_foreclosure_data(location, max_price, radius_miles),
            self._fetch_from_tax_lien_data(location, radius_miles)
        ]
        
        # Execute all fetches concurrently
        results = await asyncio.gather(*sources, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_properties.extend(result)
        
        # Remove duplicates and normalize data
        return self._deduplicate_properties(all_properties)
    
    async def _fetch_from_mls(
        self, location: str, max_price: Optional[float], 
        property_types: Optional[List[str]], radius_miles: float
    ) -> List[Dict[str, Any]]:
        """Fetch properties from MLS data sources."""
        # Mock MLS data - replace with real MLS API integration
        mock_properties = [
            {
                "id": f"mls_{i}",
                "address": f"{1000 + i} Main Street, {location}",
                "price": 150000 + (i * 25000),
                "property_type": "residential",
                "beds": 3,
                "baths": 2,
                "sqft": 1200 + (i * 100),
                "lot_size": 0.25,
                "year_built": 1980 + (i % 30),
                "days_on_market": 30 + (i * 10),
                "listing_status": "active",
                "price_history": [
                    {"date": "2024-01-01", "price": 175000 + (i * 25000), "event": "listed"},
                    {"date": "2024-02-01", "price": 150000 + (i * 25000), "event": "price_reduction"}
                ],
                "source": "mls",
                "coordinates": [34.0522 + (i * 0.01), -118.2437 + (i * 0.01)]
            }
            for i in range(20)
        ]
        
        # Filter by max_price if specified
        if max_price:
            mock_properties = [p for p in mock_properties if p["price"] <= max_price]
        
        return mock_properties
    
    async def _fetch_from_public_records(
        self, location: str, max_price: Optional[float], radius_miles: float
    ) -> List[Dict[str, Any]]:
        """Fetch properties from public records."""
        # Mock public records data
        return [
            {
                "id": f"public_{i}",
                "address": f"{2000 + i} Oak Avenue, {location}",
                "price": 120000 + (i * 15000),
                "property_type": "residential",
                "assessed_value": 130000 + (i * 15000),
                "tax_amount": 2000 + (i * 100),
                "owner_occupied": i % 3 == 0,
                "last_sale_date": "2020-01-01",
                "deed_type": "warranty",
                "source": "public_records",
                "coordinates": [34.0622 + (i * 0.01), -118.2537 + (i * 0.01)]
            }
            for i in range(15)
        ]
    
    async def _fetch_from_foreclosure_data(
        self, location: str, max_price: Optional[float], radius_miles: float
    ) -> List[Dict[str, Any]]:
        """Fetch foreclosure and pre-foreclosure properties."""
        # Mock foreclosure data
        return [
            {
                "id": f"foreclosure_{i}",
                "address": f"{3000 + i} Pine Street, {location}",
                "price": 100000 + (i * 20000),
                "property_type": "residential",
                "foreclosure_stage": ["pre_foreclosure", "auction", "reo"][i % 3],
                "auction_date": "2024-03-15",
                "loan_amount": 150000 + (i * 20000),
                "estimated_value": 180000 + (i * 25000),
                "source": "foreclosure",
                "coordinates": [34.0722 + (i * 0.01), -118.2637 + (i * 0.01)]
            }
            for i in range(10)
        ]
    
    async def _fetch_from_tax_lien_data(
        self, location: str, radius_miles: float
    ) -> List[Dict[str, Any]]:
        """Fetch properties with tax liens."""
        # Mock tax lien data
        return [
            {
                "id": f"tax_lien_{i}",
                "address": f"{4000 + i} Elm Street, {location}",
                "property_type": "residential",
                "tax_lien_amount": 5000 + (i * 1000),
                "lien_date": "2023-12-01",
                "estimated_value": 200000 + (i * 30000),
                "source": "tax_lien",
                "coordinates": [34.0822 + (i * 0.01), -118.2737 + (i * 0.01)]
            }
            for i in range(8)
        ]

    def _deduplicate_properties(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate properties and normalize data."""
        seen_addresses = set()
        unique_properties = []
        
        for prop in properties:
            address = prop.get('address', '').lower().strip()
            if address and address not in seen_addresses:
                seen_addresses.add(address)
                unique_properties.append(prop)
        
        return unique_properties
    
    async def _analyze_property_for_deal_potential(self, property_data: Dict[str, Any]) -> Optional[PropertyLead]:
        """Analyze a single property for investment deal potential."""
        try:
            # Calculate key metrics
            price = property_data.get('price', 0)
            estimated_value = await self._estimate_property_value(property_data)
            
            if not price or not estimated_value:
                return None
            
            # Calculate equity potential
            equity_potential = estimated_value - price
            
            # Calculate distress score
            distress_score = await self._calculate_distress_score(property_data)
            
            # Calculate lead score
            lead_score = await self._calculate_lead_score(property_data, equity_potential, distress_score)
            
            if lead_score < 50:  # Minimum threshold
                return None
            
            # Generate insights
            insights = await self._generate_property_insights(property_data, equity_potential, distress_score)
            
            # Determine opportunity type
            opportunity_type = self._determine_opportunity_type(property_data, distress_score)
            
            # Create property lead
            lead = PropertyLead(
                property_id=property_data.get('id', ''),
                address=property_data.get('address', ''),
                coordinates=tuple(property_data.get('coordinates', [0, 0])),
                price=price,
                estimated_value=estimated_value,
                equity_potential=equity_potential,
                distress_level=self._get_distress_level(distress_score),
                lead_score=lead_score,
                opportunity_type=opportunity_type,
                insights=insights,
                confidence_score=min(0.9, 0.6 + (lead_score / 200)),
                data_sources=[property_data.get('source', 'unknown')],
                discovered_at=datetime.utcnow(),
                metadata={
                    'property_type': property_data.get('property_type'),
                    'beds': property_data.get('beds'),
                    'baths': property_data.get('baths'),
                    'sqft': property_data.get('sqft'),
                    'year_built': property_data.get('year_built'),
                    'days_on_market': property_data.get('days_on_market')
                }
            )
            
            return lead
            
        except Exception as e:
            logger.warning(f"Failed to analyze property {property_data.get('id', 'unknown')}: {e}")
            return None
    
    async def _estimate_property_value(self, property_data: Dict[str, Any]) -> float:
        """Estimate property value using various methods."""
        # Priority order: assessed_value, estimated_value, price-based estimate
        
        if 'assessed_value' in property_data:
            return property_data['assessed_value']
        
        if 'estimated_value' in property_data:
            return property_data['estimated_value']
        
        # Basic estimation based on square footage and market data
        sqft = property_data.get('sqft', 1200)
        price_per_sqft = self._get_market_price_per_sqft(property_data.get('location', 'default'))
        
        return sqft * price_per_sqft
    
    def _get_market_price_per_sqft(self, location: str) -> float:
        """Get market price per square foot for location."""
        # Mock market data - replace with real market analysis
        market_rates = {
            'default': 150,
            'los_angeles': 400,
            'san_francisco': 800,
            'new_york': 600,
            'chicago': 200,
            'phoenix': 180,
            'philadelphia': 250,
            'san_antonio': 120,
            'san_diego': 450,
            'dallas': 160
        }
        
        location_key = location.lower().replace(' ', '_')
        return market_rates.get(location_key, market_rates['default'])
    
    async def _calculate_distress_score(self, property_data: Dict[str, Any]) -> float:
        """Calculate distress score based on various indicators."""
        score = 0.0
        
        # Check for explicit distress indicators
        if property_data.get('foreclosure_stage'):
            if property_data['foreclosure_stage'] == 'pre_foreclosure':
                score += 0.7
            elif property_data['foreclosure_stage'] == 'auction':
                score += 0.9
            elif property_data['foreclosure_stage'] == 'reo':
                score += 0.8
        
        # Tax lien indicators
        if property_data.get('tax_lien_amount', 0) > 0:
            score += 0.6
        
        # Price reduction history
        price_history = property_data.get('price_history', [])
        if len(price_history) > 1:
            reductions = [h for h in price_history if h.get('event') == 'price_reduction']
            score += min(0.5, len(reductions) * 0.2)
        
        # High days on market
        dom = property_data.get('days_on_market', 0)
        if dom > 90:
            score += min(0.4, (dom - 90) / 200)
        
        # Vacant property indicators
        if property_data.get('vacant', False):
            score += 0.5
        
        # Non-owner occupied (investment property, possibly distressed)
        if not property_data.get('owner_occupied', True):
            score += 0.2
        
        return min(1.0, score)
    
    async def _calculate_lead_score(self, property_data: Dict[str, Any], equity_potential: float, distress_score: float) -> float:
        """Calculate overall lead score (0-100)."""
        # Base score from equity potential
        equity_score = min(40, equity_potential / 1000)  # $1000 equity = 1 point, max 40
        
        # Distress bonus
        distress_bonus = distress_score * 30  # max 30 points
        
        # Location quality (mock - replace with real location analysis)
        location_score = self._get_location_quality_score(property_data)
        
        # Property condition score (mock)
        condition_score = self._get_property_condition_score(property_data)
        
        # Market growth potential (mock)
        growth_score = self._get_market_growth_score(property_data)
        
        total_score = equity_score + distress_bonus + location_score + condition_score + growth_score
        
        return min(100, max(0, total_score))
    
    def _get_location_quality_score(self, property_data: Dict[str, Any]) -> float:
        """Calculate location quality score (0-15 points)."""
        # Mock location scoring - replace with real location analysis
        coordinates = property_data.get('coordinates', [0, 0])
        
        # Basic scoring based on coordinates (mock)
        lat, lng = coordinates
        if 34.0 <= lat <= 34.1 and -118.3 <= lng <= -118.2:  # Good LA area
            return 15
        elif 33.9 <= lat <= 34.2 and -118.4 <= lng <= -118.1:  # Decent LA area
            return 10
        else:
            return 5
    
    def _get_property_condition_score(self, property_data: Dict[str, Any]) -> float:
        """Calculate property condition score (0-10 points)."""
        year_built = property_data.get('year_built', 1980)
        current_year = datetime.now().year
        age = current_year - year_built
        
        if age < 10:
            return 10  # New property
        elif age < 20:
            return 8   # Relatively new
        elif age < 30:
            return 6   # Middle-aged
        elif age < 50:
            return 4   # Older property
        else:
            return 2   # Very old property
    
    def _get_market_growth_score(self, property_data: Dict[str, Any]) -> float:
        """Calculate market growth potential score (0-5 points)."""
        # Mock market growth analysis
        return 3.0  # Average growth potential
    
    def _determine_opportunity_type(self, property_data: Dict[str, Any], distress_score: float) -> str:
        """Determine the type of investment opportunity."""
        if property_data.get('foreclosure_stage'):
            return 'foreclosure'
        elif distress_score > 0.7:
            return 'distressed'
        elif property_data.get('price', 0) < property_data.get('estimated_value', 0) * 0.8:
            return 'undervalued'
        else:
            return 'high_potential'
    
    def _get_distress_level(self, distress_score: float) -> str:
        """Convert distress score to level string."""
        if distress_score >= 0.8:
            return 'critical'
        elif distress_score >= 0.6:
            return 'high'
        elif distress_score >= 0.3:
            return 'medium'
        else:
            return 'low'
    
    async def _generate_property_insights(self, property_data: Dict[str, Any], equity_potential: float, distress_score: float) -> List[str]:
        """Generate AI-powered insights for the property."""
        insights = []
        
        # Equity-based insights
        if equity_potential > 50000:
            insights.append(f"High equity potential: ${equity_potential:,.0f} below estimated value")
        elif equity_potential > 20000:
            insights.append(f"Good equity potential: ${equity_potential:,.0f} below estimated value")
        
        # Distress-based insights
        if distress_score > 0.7:
            insights.append("High distress indicators suggest motivated seller")
        
        # Days on market insights
        dom = property_data.get('days_on_market', 0)
        if dom > 120:
            insights.append(f"Extended market time ({dom} days) indicates negotiation opportunity")
        
        # Price reduction insights
        price_history = property_data.get('price_history', [])
        reductions = [h for h in price_history if h.get('event') == 'price_reduction']
        if len(reductions) >= 2:
            insights.append("Multiple price reductions suggest seller motivation")
        
        # Property type insights
        prop_type = property_data.get('property_type', '')
        if prop_type == 'residential':
            beds = property_data.get('beds', 0)
            baths = property_data.get('baths', 0)
            if beds >= 3 and baths >= 2:
                insights.append("Good rental potential with 3+ beds, 2+ baths")
        
        return insights[:5]  # Limit to top 5 insights
    
    async def _score_and_rank_leads(self, leads: List[PropertyLead], location: str) -> List[PropertyLead]:
        """Score and rank property leads by investment potential."""
        # Sort by lead score descending
        return sorted(leads, key=lambda x: x.lead_score, reverse=True)
    
    async def _generate_market_insights(self, location: str, properties: List[Dict[str, Any]], leads: List[PropertyLead]) -> Dict[str, Any]:
        """Generate market-level insights using AI."""
        total_properties = len(properties)
        total_leads = len(leads)
        high_priority_leads = len([l for l in leads if l.lead_score >= 80])
        
        avg_price = sum(p.get('price', 0) for p in properties) / max(1, total_properties)
        avg_equity_potential = sum(l.equity_potential for l in leads) / max(1, total_leads)
        
        # Calculate market metrics
        distressed_count = len([l for l in leads if l.distress_level in ['high', 'critical']])
        foreclosure_count = len([l for l in leads if l.opportunity_type == 'foreclosure'])
        
        insights = {
            "market_summary": {
                "location": location,
                "total_properties_analyzed": total_properties,
                "investment_opportunities_found": total_leads,
                "high_priority_opportunities": high_priority_leads,
                "opportunity_rate": round((total_leads / max(1, total_properties)) * 100, 1)
            },
            "pricing_analysis": {
                "average_property_price": round(avg_price, 0),
                "average_equity_potential": round(avg_equity_potential, 0),
                "price_range": {
                    "min": min(p.get('price', 0) for p in properties) if properties else 0,
                    "max": max(p.get('price', 0) for p in properties) if properties else 0
                }
            },
            "distress_analysis": {
                "total_distressed_properties": distressed_count,
                "foreclosure_opportunities": foreclosure_count,
                "distress_rate": round((distressed_count / max(1, total_leads)) * 100, 1)
            },
            "investment_recommendations": await self._generate_investment_recommendations(location, leads),
            "market_trends": await self._analyze_market_trends(location, properties)
        }
        
        return insights
    
    async def _generate_investment_recommendations(self, location: str, leads: List[PropertyLead]) -> List[str]:
        """Generate AI-powered investment recommendations."""
        recommendations = []
        
        if not leads:
            return ["No significant investment opportunities identified in current scan"]
        
        high_score_leads = [l for l in leads if l.lead_score >= 80]
        if high_score_leads:
            recommendations.append(f"Focus on {len(high_score_leads)} high-score properties with lead scores above 80")
        
        distressed_leads = [l for l in leads if l.distress_level in ['high', 'critical']]
        if distressed_leads:
            recommendations.append(f"Consider {len(distressed_leads)} distressed properties for potential wholesale opportunities")
        
        undervalued_leads = [l for l in leads if l.opportunity_type == 'undervalued']
        if undervalued_leads:
            recommendations.append(f"Investigate {len(undervalued_leads)} undervalued properties for BRRRR strategy potential")
        
        avg_equity = sum(l.equity_potential for l in leads) / len(leads)
        if avg_equity > 30000:
            recommendations.append(f"Strong market with average equity potential of ${avg_equity:,.0f}")
        
        return recommendations[:5]
    
    async def _analyze_market_trends(self, location: str, properties: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market trends from property data."""
        # Mock trend analysis - replace with real market data
        return {
            "price_trend": "stable",
            "inventory_level": "normal",
            "days_on_market_trend": "increasing",
            "foreclosure_trend": "stable",
            "market_temperature": "buyer_friendly"
        }
    
    async def _create_distressed_property_lead(self, property_data: Dict[str, Any], distress_score: float) -> Optional[PropertyLead]:
        """Create a lead specifically for distressed properties."""
        return await self._analyze_property_for_deal_potential(property_data)
    
    async def _publish_scan_update(self, scan_result: MarketScanResult):
        """Publish real-time update about scan completion."""
        try:
            websocket_manager = get_websocket_manager()
            if websocket_manager:
                await websocket_manager.broadcast_to_all({
                    "type": "deal_scan_complete",
                    "scan_id": scan_result.scan_id,
                    "location": scan_result.location,
                    "leads_found": scan_result.leads_discovered,
                    "high_priority_leads": scan_result.high_priority_leads,
                    "scan_duration": scan_result.scan_duration
                })
            
            # Publish to Redis
            await publish_event("agent_activity", "deal_scan_complete", {
                "agent_id": self.agent_id,
                "scan_result": scan_result.__dict__
            })
            
        except Exception as e:
            logger.warning(f"Failed to publish scan update: {e}")

# Global instance
_deal_sourcing_agent = None

def get_deal_sourcing_agent() -> DealSourcingAgent:
    """Get global deal sourcing agent instance."""
    global _deal_sourcing_agent
    if _deal_sourcing_agent is None:
        _deal_sourcing_agent = DealSourcingAgent()
    return _deal_sourcing_agent

async def deal_sourcing_agent_handler(task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler function for deal sourcing agent tasks."""
    agent = get_deal_sourcing_agent()
    
    if not agent.is_initialized:
        raise RuntimeError("Deal Sourcing Agent not properly initialized")
    
    if task_type == "scan_market":
        result = await agent.scan_market_for_deals(
            location=task_data.get("location", ""),
            max_price=task_data.get("max_price"),
            property_types=task_data.get("property_types"),
            min_equity_potential=task_data.get("min_equity_potential", 20000),
            scan_radius_miles=task_data.get("scan_radius_miles", 25)
        )
        return {"scan_result": result.__dict__}
    
    elif task_type == "analyze_distressed":
        properties = task_data.get("properties", [])
        leads = await agent.analyze_distressed_properties(properties)
        return {"distressed_leads": [lead.__dict__ for lead in leads]}
    
    else:
        raise ValueError(f"Unknown task type: {task_type}")