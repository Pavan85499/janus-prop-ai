"""
Market Data API endpoints for Janus Prop AI Backend

This module provides endpoints for market intelligence and real-time market data.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from pydantic import BaseModel, Field

from core.database import get_db_session
from core.redis_client import cache_get, cache_set, publish_event
from core.websocket_manager import get_websocket_manager

router = APIRouter()

# Pydantic models
class MarketData(BaseModel):
    """Market data model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    location: str  # City, ZIP code, or neighborhood
    data_type: str  # "sales", "inventory", "pricing", "trends"
    period: str  # "daily", "weekly", "monthly", "quarterly"
    date: datetime
    metrics: Dict[str, Any]
    source: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class MarketTrend(BaseModel):
    """Market trend model."""
    location: str
    trend_type: str  # "price", "inventory", "days_on_market", "sales_volume"
    direction: str  # "up", "down", "stable"
    magnitude: float  # Percentage change
    period: str  # Time period for the trend
    confidence: float  # Confidence level (0-1)
    factors: List[str]  # Contributing factors
    prediction: Optional[str] = None

class MarketAnalysis(BaseModel):
    """Market analysis model."""
    location: str
    analysis_date: datetime
    summary: str
    key_insights: List[str]
    trends: List[MarketTrend]
    recommendations: List[str]
    risk_factors: List[str]
    opportunities: List[str]
    data_sources: List[str]

# Mock data for development
MOCK_MARKET_DATA = [
    MarketData(
        location="Downtown, CA",
        data_type="sales",
        period="monthly",
        date=datetime.utcnow() - timedelta(days=30),
        metrics={
            "total_sales": 45,
            "average_price": 725000,
            "median_price": 680000,
            "price_per_sqft": 425,
            "days_on_market": 28,
            "inventory": 67
        },
        source="MLS"
    ),
    MarketData(
        location="Uptown, CA",
        data_type="pricing",
        period="weekly",
        date=datetime.utcnow() - timedelta(days=7),
        metrics={
            "average_price": 485000,
            "median_price": 460000,
            "price_change_week": 2.1,
            "price_change_month": 5.3,
            "active_listings": 89
        },
        source="Realie API"
    )
]

MOCK_TRENDS = [
    MarketTrend(
        location="Downtown, CA",
        trend_type="price",
        direction="up",
        magnitude=5.2,
        period="monthly",
        confidence=0.85,
        factors=["low inventory", "high demand", "economic growth"],
        prediction="Continued price growth expected in next quarter"
    ),
    MarketTrend(
        location="Uptown, CA",
        trend_type="inventory",
        direction="down",
        magnitude=-12.3,
        period="monthly",
        confidence=0.78,
        factors=["seasonal factors", "seller reluctance", "market absorption"],
        prediction="Inventory may stabilize in coming months"
    )
]

@router.get("/", response_model=List[MarketData])
async def get_market_data(
    location: Optional[str] = None,
    data_type: Optional[str] = None,
    period: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100)
):
    """Get market data with optional filtering."""
    try:
        filtered_data = MOCK_MARKET_DATA.copy()
        
        if location:
            filtered_data = [d for d in filtered_data if location.lower() in d.location.lower()]
        if data_type:
            filtered_data = [d for d in filtered_data if d.data_type == data_type]
        if period:
            filtered_data = [d for d in filtered_data if d.period == period]
        
        # Sort by date (newest first) and apply limit
        filtered_data.sort(key=lambda x: x.date, reverse=True)
        return filtered_data[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")

@router.get("/trends", response_model=List[MarketTrend])
async def get_market_trends(
    location: Optional[str] = None,
    trend_type: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50)
):
    """Get market trends with optional filtering."""
    try:
        filtered_trends = MOCK_TRENDS.copy()
        
        if location:
            filtered_trends = [t for t in filtered_trends if location.lower() in t.location.lower()]
        if trend_type:
            filtered_trends = [t for t in filtered_trends if t.trend_type == trend_type]
        
        # Sort by confidence (highest first) and apply limit
        filtered_trends.sort(key=lambda x: x.confidence, reverse=True)
        return filtered_trends[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market trends: {str(e)}")

@router.get("/analysis/{location}", response_model=MarketAnalysis)
async def get_market_analysis(location: str):
    """Get comprehensive market analysis for a specific location."""
    try:
        # Try to get from cache first
        cached_analysis = await cache_get(f"market_analysis:{location}")
        if cached_analysis:
            return MarketAnalysis(**cached_analysis)
        
        # Generate mock analysis (in production, this would use AI/ML models)
        analysis = MarketAnalysis(
            location=location,
            analysis_date=datetime.utcnow(),
            summary=f"Market analysis for {location} shows strong fundamentals with some areas of opportunity.",
            key_insights=[
                "Property values have increased 5.2% over the past month",
                "Inventory levels are 15% below historical averages",
                "Days on market have decreased by 20%",
                "New construction is limited, driving up existing home values"
            ],
            trends=MOCK_TRENDS,
            recommendations=[
                "Consider properties in emerging neighborhoods for better value",
                "Monitor inventory levels for optimal listing timing",
                "Focus on properties with renovation potential",
                "Consider investment properties in high-demand areas"
            ],
            risk_factors=[
                "Potential interest rate increases",
                "Economic uncertainty in certain sectors",
                "Seasonal market fluctuations"
            ],
            opportunities=[
                "Growing demand for single-family homes",
                "Limited new construction supply",
                "Strong rental market supporting investment properties"
            ],
            data_sources=["MLS", "Realie API", "Public Records", "Economic Indicators"]
        )
        
        # Cache the analysis
        await cache_set(f"market_analysis:{location}", analysis.dict(), expire=3600)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate market analysis: {str(e)}")

@router.get("/comparables/{location}")
async def get_market_comparables(
    location: str,
    property_type: Optional[str] = None,
    price_range: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """Get comparable market data for a specific location."""
    try:
        # Filter market data by location and criteria
        comparables = []
        for data in MOCK_MARKET_DATA:
            if location.lower() in data.location.lower():
                if property_type and data.data_type != property_type:
                    continue
                if price_range:
                    # Parse price range (e.g., "500k-750k")
                    # This is simplified - in production would be more sophisticated
                    pass
                comparables.append(data)
        
        # Sort by relevance (could be enhanced with ML scoring)
        comparables.sort(key=lambda x: x.date, reverse=True)
        
        return {
            "location": location,
            "comparables": comparables[:limit],
            "total_found": len(comparables),
            "filters": {
                "property_type": property_type,
                "price_range": price_range
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market comparables: {str(e)}")

@router.get("/forecast/{location}")
async def get_market_forecast(
    location: str,
    timeframe: str = Query("3months", regex="^(1month|3months|6months|1year)$")
):
    """Get market forecast for a specific location and timeframe."""
    try:
        # Mock forecast data (in production, this would use ML models)
        forecast_data = {
            "location": location,
            "timeframe": timeframe,
            "generated_at": datetime.utcnow(),
            "predictions": {
                "price_trend": {
                    "direction": "up",
                    "magnitude": 3.5,
                    "confidence": 0.78,
                    "factors": ["low inventory", "strong demand", "economic stability"]
                },
                "inventory_trend": {
                    "direction": "stable",
                    "magnitude": 0.0,
                    "confidence": 0.65,
                    "factors": ["seasonal patterns", "market equilibrium"]
                },
                "sales_volume": {
                    "direction": "up",
                    "magnitude": 8.2,
                    "confidence": 0.82,
                    "factors": ["increased buyer activity", "favorable financing"]
                }
            },
            "risk_assessment": {
                "overall_risk": "low",
                "key_risks": ["interest rate changes", "economic uncertainty"],
                "mitigation_factors": ["strong local economy", "diverse buyer base"]
            },
            "recommendations": [
                "Monitor interest rate trends",
                "Consider properties with value-add potential",
                "Focus on locations with strong fundamentals"
            ]
        }
        
        return forecast_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate market forecast: {str(e)}")

@router.post("/data", response_model=MarketData)
async def create_market_data(
    market_data: MarketData,
    background_tasks: BackgroundTasks
):
    """Create new market data entry."""
    try:
        # Set ID and timestamps
        market_data.id = str(uuid4())
        market_data.last_updated = datetime.utcnow()
        
        # Add to mock data (in real app, this would go to database)
        MOCK_MARKET_DATA.append(market_data)
        
        # Cache the data
        await cache_set(f"market_data:{market_data.id}", market_data.dict(), expire=3600)
        
        # Publish real-time update
        await publish_event(
            f"market:{market_data.location}",
            "market_data_created",
            market_data.dict()
        )
        
        # Send WebSocket update
        websocket_manager = get_websocket_manager()
        await websocket_manager.send_market_update(market_data.location, {
            "type": "market_data_created",
            "data": market_data.dict()
        })
        
        return market_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create market data: {str(e)}")

@router.get("/locations")
async def get_market_locations():
    """Get list of available market locations."""
    try:
        # Extract unique locations from market data
        locations = list(set([data.location for data in MOCK_MARKET_DATA]))
        
        return {
            "locations": locations,
            "total": len(locations),
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market locations: {str(e)}")

@router.get("/summary/{location}")
async def get_market_summary(location: str):
    """Get market summary for a specific location."""
    try:
        # Filter data for the specific location
        location_data = [d for d in MOCK_MARKET_DATA if location.lower() in d.location.lower()]
        
        if not location_data:
            raise HTTPException(status_code=404, detail="No market data found for location")
        
        # Calculate summary statistics
        total_sales = sum(d.metrics.get("total_sales", 0) for d in location_data if d.data_type == "sales")
        avg_price = sum(d.metrics.get("average_price", 0) for d in location_data if d.data_type == "pricing") / len([d for d in location_data if d.data_type == "pricing"])
        
        summary = {
            "location": location,
            "summary_date": datetime.utcnow(),
            "key_metrics": {
                "total_sales": total_sales,
                "average_price": round(avg_price, 2),
                "data_points": len(location_data)
            },
            "recent_trends": MOCK_TRENDS[:3],  # Top 3 trends
            "data_sources": list(set(d.source for d in location_data)),
            "last_updated": max(d.last_updated for d in location_data)
        }
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate market summary: {str(e)}")
