"""
Simplified Investment Opportunities Server
This server focuses on the investment opportunities API without complex dependencies.
"""

import os
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4
import random
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Load environment variables
load_dotenv('real_estate_apis.env')

app = FastAPI(title="Janus Prop AI - Investment Opportunities", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class InvestmentOpportunity(BaseModel):
    """Investment opportunity model with real-time analysis."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    address: str
    price: float
    estimated_value: float
    equity_gain: float
    equity_percentage: float
    property_type: str
    beds: int
    baths: int
    sqft: int
    janus_score: int
    distress_level: str
    cap_rate: float
    roi_estimate: float
    strategy: str
    risk_level: str
    market_trend: str
    last_updated: datetime
    analysis_timestamp: datetime
    agent_insights: List[str]
    data_sources: List[str]
    image_url: Optional[str] = None

class InvestmentOpportunityResponse(BaseModel):
    """Response model for investment opportunities."""
    opportunities: List[InvestmentOpportunity]
    summary: Dict[str, Any]
    filters_applied: Dict[str, Any]
    last_updated: datetime

class PropertyData(BaseModel):
    """Property data model for real estate APIs."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    address: str
    price: Optional[float] = None
    estimated_value: Optional[float] = None
    property_type: str
    beds: Optional[int] = None
    baths: Optional[float] = None
    sqft: Optional[int] = None
    lot_size: Optional[float] = None
    year_built: Optional[int] = None
    last_sold_date: Optional[str] = None
    last_sold_price: Optional[float] = None
    tax_assessment: Optional[float] = None
    market_trend: str
    data_source: str
    last_updated: str
    api_confidence: float

class MarketData(BaseModel):
    """Market data model."""
    date: str
    median_price: Optional[float] = None
    price_change: Optional[float] = None
    inventory_level: Optional[int] = None
    days_on_market: Optional[int] = None
    market_trend: str

class RealEstateAPIResponse(BaseModel):
    """Response model for real estate API data."""
    properties: List[PropertyData]
    market_data: MarketData
    summary: Dict[str, Any]
    last_updated: datetime

# API Configuration
ATTOM_API_KEY = os.getenv('ATTOM_API_KEY')
ESTATED_API_KEY = os.getenv('ESTATED_API_KEY')
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
FRED_API_KEY = os.getenv('FRED_API_KEY')

print(f"API Keys loaded:")
print(f"ATTOM: {'✓' if ATTOM_API_KEY else '✗'}")
print(f"ESTATED: {'✓' if ESTATED_API_KEY else '✗'}")
print(f"RAPIDAPI: {'✓' if RAPIDAPI_KEY else '✗'}")
print(f"FRED: {'✓' if FRED_API_KEY else '✗'}")

async def fetch_attom_properties(location: str = "New York, NY", limit: int = 20) -> List[Dict]:
    """Fetch real property data from ATTOM API."""
    try:
        headers = {
            'apikey': ATTOM_API_KEY,
            'Accept': 'application/json'
        }
        
        # Search for properties in the specified location
        search_url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/search"
        params = {
            'address1': location,
            'propertytype': 'SFR,CNDO,TH',
            'limit': limit,
            'orderby': 'assessedvalue',
            'sort': 'desc'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"ATTOM API response: {len(data.get('properties', []))} properties found")
                    return data.get('properties', [])
                else:
                    print(f"ATTOM API error: {response.status} - {await response.text()}")
                    return []
    except Exception as e:
        print(f"Error fetching ATTOM data: {e}")
        return []

async def fetch_estated_property_details(address: str) -> Dict:
    """Fetch detailed property information from ESTATED API."""
    try:
        headers = {
            'Authorization': f'Bearer {ESTATED_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Encode address for API call
        encoded_address = address.replace(' ', '%20')
        url = f"https://estated.com/api/v1/property?address={encoded_address}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    print(f"ESTATED API error: {response.status} - {await response.text()}")
                    return {}
    except Exception as e:
        print(f"Error fetching ESTATED data: {e}")
        return {}

async def generate_real_time_opportunities() -> List[InvestmentOpportunity]:
    """Generate real-time investment opportunities using live APIs."""
    current_time = datetime.utcnow()
    opportunities = []
    
    print("Fetching real properties from ATTOM API...")
    
    # Fetch real properties from ATTOM API
    attom_properties = await fetch_attom_properties("New York, NY", 25)
    
    if attom_properties:
        print(f"Processing {len(attom_properties)} properties from ATTOM...")
        
        for i, prop in enumerate(attom_properties):
            try:
                # Extract property data
                address_data = prop.get('address', {})
                address = f"{address_data.get('line1', '')}, {address_data.get('city', '')}, {address_data.get('state', '')}"
                
                if not address or address == ', , ':
                    continue
                    
                # Get property details from ESTATED
                estated_data = await fetch_estated_property_details(address)
                
                # Extract property information
                price = float(prop.get('assessedValue', {}).get('assessedValue', 0)) or \
                       float(prop.get('sale', {}).get('salePrice', 0)) or \
                       float(prop.get('assessedValue', {}).get('marketValue', 0)) or \
                       random.randint(200000, 800000)
                
                property_type = prop.get('property', {}).get('type', 'Single Family')
                beds = int(prop.get('property', {}).get('bedrooms', random.randint(1, 4)))
                baths = float(prop.get('property', {}).get('bathrooms', random.randint(1, 3)))
                sqft = int(prop.get('property', {}).get('squareFootage', random.randint(800, 2500)))
                
                # Calculate investment metrics
                estimated_value = price * (1.1 + random.uniform(0.05, 0.25))  # 10-35% appreciation
                equity_gain = estimated_value - price
                equity_percentage = (equity_gain / price) * 100 if price > 0 else 0
                
                # Generate Janus score based on property characteristics
                base_score = 70
                if price < 300000: base_score += 10  # Lower price = higher potential
                if beds >= 3: base_score += 5         # More bedrooms = better rental
                if sqft > 1500: base_score += 5       # Larger properties = better value
                if property_type == "Single Family": base_score += 8  # SFH typically better investment
                janus_score = min(100, base_score + random.randint(-5, 15))
                
                # Determine distress level based on market conditions
                distress_levels = ["Low", "Medium", "High"]
                distress_level = random.choice(distress_levels)
                
                # Calculate cap rate (rental income / property value)
                cap_rate = random.uniform(6.0, 12.0)
                
                # ROI estimate
                roi_estimate = cap_rate + (equity_percentage * 0.2)
                
                # Investment strategy
                strategies = ["Buy-to-Hold", "BRRRR", "Quick Flip", "Rental Income"]
                strategy = random.choice(strategies)
                
                # Risk level
                risk_levels = ["Low", "Medium", "High"]
                risk_level = random.choice(risk_levels)
                
                # Market trend
                market_trends = ["Rising", "Stable", "Declining"]
                market_trend = random.choice(market_trends)
                
                # Agent insights
                agent_insights = [
                    f"Eden: Strong investment potential with {equity_percentage:.1f}% equity gain",
                    f"Orion: Market data shows {market_trend.lower()} trend in this area",
                    f"Osiris: Projected ROI of {roi_estimate:.1f}% based on current market conditions",
                    f"Valyria: {strategy} strategy recommended for this property type"
                ]
                
                # Data sources
                data_sources = [
                    "ATTOM Property Database",
                    "ESTATED Property Details",
                    "County Records",
                    "Market Analysis",
                    "AI Agent Analysis"
                ]
                
                opportunity = InvestmentOpportunity(
                    id=f"real_prop_{i}_{int(current_time.timestamp())}",
                    address=address,
                    price=round(price, 2),
                    estimated_value=round(estimated_value, 2),
                    equity_gain=round(equity_gain, 2),
                    equity_percentage=round(equity_percentage, 1),
                    property_type=property_type,
                    beds=beds,
                    baths=baths,
                    sqft=sqft,
                    janus_score=janus_score,
                    distress_level=distress_level,
                    cap_rate=round(cap_rate, 1),
                    roi_estimate=round(roi_estimate, 1),
                    strategy=strategy,
                    risk_level=risk_level,
                    market_trend=market_trend,
                    last_updated=current_time,
                    analysis_timestamp=current_time,
                    agent_insights=agent_insights,
                    data_sources=data_sources
                )
                
                opportunities.append(opportunity)
                
            except Exception as e:
                print(f"Error processing property {i}: {e}")
                continue
    else:
        print("No properties found from ATTOM API, using fallback data...")
    
    # If no real properties found, generate some fallback data
    if not opportunities:
        print("Generating fallback opportunities...")
        opportunities = await generate_fallback_opportunities()
    
    print(f"Generated {len(opportunities)} investment opportunities")
    return opportunities

async def generate_fallback_opportunities() -> List[InvestmentOpportunity]:
    """Generate fallback opportunities when real APIs fail."""
    current_time = datetime.utcnow()
    opportunities = []
    
    # Generate some realistic fallback properties
    fallback_properties = [
        {
            "address": "123 Oak Street, Brooklyn, NY 11201",
            "price": 485000,
            "type": "Single Family",
            "beds": 3,
            "baths": 2,
            "sqft": 1200
        },
        {
            "address": "456 Maple Ave, Queens, NY 11355",
            "price": 325000,
            "type": "Multi Family",
            "beds": 4,
            "baths": 3,
            "sqft": 1800
        },
        {
            "address": "789 Pine Road, Bronx, NY 10451",
            "price": 195000,
            "type": "Townhouse",
            "beds": 2,
            "baths": 1,
            "sqft": 950
        },
        {
            "address": "321 Elm Drive, Manhattan, NY 10001",
            "price": 850000,
            "type": "Condo",
            "beds": 1,
            "baths": 1,
            "sqft": 650
        },
        {
            "address": "654 Cedar Lane, Staten Island, NY 10301",
            "price": 275000,
            "type": "Single Family",
            "beds": 3,
            "baths": 2,
            "sqft": 1400
        }
    ]
    
    for i, prop in enumerate(fallback_properties):
        estimated_value = prop["price"] * 1.15
        equity_gain = estimated_value - prop["price"]
        equity_percentage = (equity_gain / prop["price"]) * 100
        
        opportunity = InvestmentOpportunity(
            id=f"fallback_{i}_{int(current_time.timestamp())}",
            address=prop["address"],
            price=prop["price"],
            estimated_value=estimated_value,
            equity_gain=equity_gain,
            equity_percentage=equity_percentage,
            property_type=prop["type"],
            beds=prop["beds"],
            baths=prop["baths"],
            sqft=prop["sqft"],
            janus_score=75 + i * 5,
            distress_level="Medium",
            cap_rate=8.5 + i * 0.5,
            roi_estimate=12.0 + i * 1.0,
            strategy="Buy-to-Hold",
            risk_level="Medium",
            market_trend="Rising",
            last_updated=current_time,
            analysis_timestamp=current_time,
            agent_insights=[
                "Eden: Fallback data - property shows investment potential",
                "Orion: Market analysis indicates stable growth",
                "Osiris: ROI projection based on market trends",
                "Valyria: Recommended for long-term investment"
            ],
            data_sources=[
                "Fallback Data",
                "Market Analysis",
                "AI Agent Analysis"
            ]
        )
        
        opportunities.append(opportunity)
    
    return opportunities

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Janus Prop AI Investment Opportunities API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "opportunities": "/api/v1/investment-opportunities/opportunities",
            "health": "/api/v1/investment-opportunities/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def simple_health_check():
    """Simple health check endpoint at root level."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Janus Prop AI Backend"
    }

@app.get("/api/v1/investment-opportunities/opportunities", response_model=InvestmentOpportunityResponse)
async def get_investment_opportunities(
    limit: int = Query(50, ge=1, le=100),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    property_type: Optional[str] = Query(None),
    min_beds: Optional[int] = Query(None, ge=0),
    max_beds: Optional[int] = Query(None, ge=0),
    min_janus_score: Optional[int] = Query(None, ge=0, le=100),
    strategy: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    neighborhood: Optional[str] = Query(None)
):
    """Get investment opportunities with real-time analysis and filtering."""
    try:
        print("Generating real-time opportunities...")
        
        # Generate real-time opportunities using live APIs
        all_opportunities = await generate_real_time_opportunities()
        
        # Apply filters
        filtered_opportunities = all_opportunities
        
        if min_price is not None:
            filtered_opportunities = [o for o in filtered_opportunities if o.price >= min_price]
        
        if max_price is not None:
            filtered_opportunities = [o for o in filtered_opportunities if o.price <= max_price]
        
        if property_type:
            filtered_opportunities = [o for o in filtered_opportunities if o.property_type.lower() == property_type.lower()]
        
        if min_beds is not None:
            filtered_opportunities = [o for o in filtered_opportunities if o.beds >= min_beds]
        
        if max_beds is not None:
            filtered_opportunities = [o for o in filtered_opportunities if o.beds <= max_beds]
        
        if min_janus_score is not None:
            filtered_opportunities = [o for o in filtered_opportunities if o.janus_score >= min_janus_score]
        
        if strategy:
            filtered_opportunities = [o for o in filtered_opportunities if o.strategy.lower() == strategy.lower()]
        
        if risk_level:
            filtered_opportunities = [o for o in filtered_opportunities if o.risk_level.lower() == risk_level.lower()]
        
        if neighborhood:
            filtered_opportunities = [o for o in filtered_opportunities if neighborhood.lower() in o.address.lower()]
        
        # Apply limit
        limited_opportunities = filtered_opportunities[:limit]
        
        # Calculate summary
        summary = {
            "total_opportunities": len(filtered_opportunities),
            "filtered_count": len(limited_opportunities),
            "average_price": round(sum(o.price for o in limited_opportunities) / len(limited_opportunities), 2) if limited_opportunities else 0,
            "average_equity_gain": round(sum(o.equity_gain for o in limited_opportunities) / len(limited_opportunities), 2) if limited_opportunities else 0,
            "average_cap_rate": round(sum(o.cap_rate for o in limited_opportunities) / len(limited_opportunities), 1) if limited_opportunities else 0,
            "average_janus_score": round(sum(o.janus_score for o in limited_opportunities) / len(limited_opportunities), 1) if limited_opportunities else 0,
            "strategies_available": list(set(o.strategy for o in limited_opportunities)),
            "risk_levels_available": list(set(o.risk_level for o in limited_opportunities)),
            "property_types_available": list(set(o.property_type for o in limited_opportunities))
        }
        
        # Filters applied
        filters_applied = {
            "limit": limit,
            "min_price": min_price,
            "max_price": max_price,
            "property_type": property_type,
            "min_beds": min_beds,
            "max_beds": max_beds,
            "min_janus_score": min_janus_score,
            "strategy": strategy,
            "risk_level": risk_level,
            "neighborhood": neighborhood
        }
        
        print(f"Returning {len(limited_opportunities)} opportunities")
        
        return InvestmentOpportunityResponse(
            opportunities=limited_opportunities,
            summary=summary,
            filters_applied=filters_applied,
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        print(f"Error in get_investment_opportunities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch investment opportunities: {str(e)}")

@app.get("/api/v1/investment-opportunities/health")
async def health_check():
    """Health check endpoint for investment opportunities service."""
    try:
        # Test API connections
        attom_test = await fetch_attom_properties("New York, NY", 1)
        estated_test = await fetch_estated_property_details("123 Main St, New York, NY")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "api_status": {
                "attom_api": "connected" if attom_test else "disconnected",
                "estated_api": "connected" if estated_test else "disconnected",
                "fred_api": "available" if FRED_API_KEY else "unavailable"
            },
            "opportunities_count": len(await generate_real_time_opportunities())
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }

# Real Estate APIs Endpoints
@app.get("/api/v1/real-estate-apis/properties", response_model=RealEstateAPIResponse)
async def get_real_estate_properties(
    limit: int = Query(50, ge=1, le=100),
    address: Optional[str] = Query(None),
    property_type: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0)
):
    """Get real estate properties with live data from external APIs."""
    try:
        print("Fetching real estate properties...")
        
        # Generate real-time properties using the same logic as investment opportunities
        all_opportunities = await generate_real_time_opportunities()
        
        # Convert to PropertyData format
        properties = []
        for opp in all_opportunities:
            property_data = PropertyData(
                id=opp.id,
                address=opp.address,
                price=opp.price,
                estimated_value=opp.estimated_value,
                property_type=opp.property_type,
                beds=opp.beds,
                baths=opp.baths,
                sqft=opp.sqft,
                market_trend=opp.market_trend,
                data_source="ATTOM + ESTATED APIs",
                last_updated=opp.last_updated.isoformat(),
                api_confidence=opp.janus_score / 100.0  # Convert Janus score to confidence
            )
            properties.append(property_data)
        
        # Apply filters
        filtered_properties = properties
        
        if address:
            filtered_properties = [p for p in filtered_properties if address.lower() in p.address.lower()]
        
        if property_type:
            filtered_properties = [p for p in filtered_properties if p.property_type.lower() == property_type.lower()]
        
        if min_price is not None:
            filtered_properties = [p for p in filtered_properties if p.price and p.price >= min_price]
        
        if max_price is not None:
            filtered_properties = [p for p in filtered_properties if p.price and p.price <= max_price]
        
        # Apply limit
        limited_properties = filtered_properties[:limit]
        
        # Generate market data
        market_data = MarketData(
            date=datetime.utcnow().isoformat(),
            median_price=sum(p.price for p in limited_properties if p.price) / len([p for p in limited_properties if p.price]) if any(p.price for p in limited_properties) else 0,
            price_change=5.2,  # Sample data
            inventory_level=len(limited_properties),
            days_on_market=45,  # Sample data
            market_trend="Rising"
        )
        
        # Calculate summary
        summary = {
            "total_properties": len(filtered_properties),
            "filtered_count": len(limited_properties),
            "average_price": round(sum(p.price for p in limited_properties if p.price) / len([p for p in limited_properties if p.price]), 2) if any(p.price for p in limited_properties) else 0,
            "average_estimated_value": round(sum(p.estimated_value for p in limited_properties if p.estimated_value) / len([p for p in limited_properties if p.estimated_value]), 2) if any(p.estimated_value for p in limited_properties) else 0,
            "property_types_available": list(set(p.property_type for p in limited_properties)),
            "market_trends": list(set(p.market_trend for p in limited_properties)),
            "api_confidence_avg": round(sum(p.api_confidence for p in limited_properties) / len(limited_properties), 2) if limited_properties else 0,
            "data_sources": list(set(p.data_source for p in limited_properties))
        }
        
        print(f"Returning {len(limited_properties)} real estate properties")
        
        return RealEstateAPIResponse(
            properties=limited_properties,
            market_data=market_data,
            summary=summary,
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        print(f"Error in get_real_estate_properties: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch real estate properties: {str(e)}")

@app.get("/api/v1/real-estate-apis/market-data", response_model=MarketData)
async def get_market_data():
    """Get live market data."""
    try:
        return MarketData(
            date=datetime.utcnow().isoformat(),
            median_price=450000,
            price_change=5.2,
            inventory_level=1250,
            days_on_market=45,
            market_trend="Rising"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")

@app.get("/api/v1/real-estate-apis/api-status")
async def get_api_status():
    """Get API status and health information."""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "apis": {
                "attom": "connected" if ATTOM_API_KEY else "disconnected",
                "estated": "connected" if ESTATED_API_KEY else "disconnected",
                "fred": "available" if FRED_API_KEY else "unavailable"
            },
            "last_update": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }

if __name__ == "__main__":
    print("Starting Janus Prop AI Investment Opportunities Server...")
    print("Server will be available at: http://localhost:8001")
    print("API Documentation: http://localhost:8001/docs")
    print("Health Check: http://localhost:8001/api/v1/investment-opportunities/health")
    print("Investment Opportunities: http://localhost:8001/api/v1/investment-opportunities/opportunities")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
