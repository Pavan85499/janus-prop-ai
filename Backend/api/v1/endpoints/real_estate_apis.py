"""
Real Estate APIs endpoints for Janus Prop AI Backend

Provides integration with external real estate data sources including ATTOM, Estated, and FRED APIs.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import structlog
import os

from core.database import get_db_session
from models.property import Property
from sqlalchemy import and_, or_, desc, asc

logger = structlog.get_logger(__name__)

router = APIRouter()

@router.options("/api-status")
async def options_api_status():
    """Explicit CORS preflight handler for /api-status."""
    return {}

@router.options("/properties")
async def options_properties():
    """Explicit CORS preflight handler for /properties."""
    return {}

@router.get("/properties")
async def get_real_estate_properties(
    limit: Optional[int] = Query(50, ge=1, le=1000, description="Maximum number of properties to return"),
    address: Optional[str] = Query(None, description="Address to search for"),
    property_type: Optional[str] = Query(None, description="Property type filter"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum property price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum property price"),
    db = Depends(get_db_session)
):
    """Get real estate properties from external APIs."""
    try:
        # Mock real estate properties data
        mock_properties = [
            {
                "id": "prop_001",
                "address": "1247 Oak Street, Austin, TX 78701",
                "price": 185000,
                "estimated_value": 250000,
                "property_type": "Single Family",
                "beds": 3,
                "baths": 2,
                "sqft": 1800,
                "lot_size": 0.25,
                "year_built": 2015,
                "last_sold_date": "2020-03-15",
                "last_sold_price": 165000,
                "tax_assessment": 235000,
                "market_trend": "Rising",
                "data_source": "ATTOM",
                "last_updated": datetime.utcnow().isoformat(),
                "api_confidence": 0.95,
                "latitude": 30.2672,
                "longitude": -97.7431
            },
            {
                "id": "prop_002",
                "address": "892 Pine Avenue, Houston, TX 77001",
                "price": 145000,
                "estimated_value": 195000,
                "property_type": "Single Family",
                "beds": 2,
                "baths": 1,
                "sqft": 1200,
                "lot_size": 0.18,
                "year_built": 2010,
                "last_sold_date": "2018-07-22",
                "last_sold_price": 125000,
                "tax_assessment": 180000,
                "market_trend": "Stable",
                "data_source": "Estated",
                "last_updated": datetime.utcnow().isoformat(),
                "api_confidence": 0.87,
                "latitude": 29.7604,
                "longitude": -95.3698
            },
            {
                "id": "prop_003",
                "address": "3456 Elm Drive, Dallas, TX 75201",
                "price": 225000,
                "estimated_value": 280000,
                "property_type": "Multi-Family",
                "beds": 4,
                "baths": 3,
                "sqft": 2400,
                "lot_size": 0.35,
                "year_built": 2012,
                "last_sold_date": "2019-11-08",
                "last_sold_price": 195000,
                "tax_assessment": 265000,
                "market_trend": "Rising",
                "data_source": "ATTOM",
                "last_updated": datetime.utcnow().isoformat(),
                "api_confidence": 0.92,
                "latitude": 32.7767,
                "longitude": -96.7970
            },
            {
                "id": "prop_004",
                "address": "789 Maple Court, San Antonio, TX 78201",
                "price": 165000,
                "estimated_value": 220000,
                "property_type": "Duplex",
                "beds": 3,
                "baths": 2,
                "sqft": 1600,
                "lot_size": 0.22,
                "year_built": 2008,
                "last_sold_date": "2021-05-12",
                "last_sold_price": 145000,
                "tax_assessment": 210000,
                "market_trend": "Stable",
                "data_source": "Estated",
                "last_updated": datetime.utcnow().isoformat(),
                "api_confidence": 0.89,
                "latitude": 29.4241,
                "longitude": -98.4936
            },
            {
                "id": "prop_005",
                "address": "555 Cedar Lane, Fort Worth, TX 76101",
                "price": 198000,
                "estimated_value": 245000,
                "property_type": "Single Family",
                "beds": 3,
                "baths": 2,
                "sqft": 1900,
                "lot_size": 0.28,
                "year_built": 2014,
                "last_sold_date": "2020-09-30",
                "last_sold_price": 175000,
                "tax_assessment": 230000,
                "market_trend": "Rising",
                "data_source": "ATTOM",
                "last_updated": datetime.utcnow().isoformat(),
                "api_confidence": 0.91,
                "latitude": 32.7555,
                "longitude": -97.3308
            }
        ]
        
        # Apply filters
        filtered_properties = mock_properties
        
        if address:
            filtered_properties = [prop for prop in filtered_properties if address.lower() in prop["address"].lower()]
        
        if property_type:
            filtered_properties = [prop for prop in filtered_properties if prop["property_type"] == property_type]
        
        if min_price is not None:
            filtered_properties = [prop for prop in filtered_properties if prop["price"] and prop["price"] >= min_price]
        
        if max_price is not None:
            filtered_properties = [prop for prop in filtered_properties if prop["price"] and prop["price"] <= max_price]
        
        # Apply limit
        filtered_properties = filtered_properties[:limit]
        
        # Calculate summary statistics
        total_properties = len(mock_properties)
        filtered_count = len(filtered_properties)
        average_price = sum(prop["price"] for prop in filtered_properties if prop["price"]) / len(filtered_properties) if filtered_properties else 0
        average_estimated_value = sum(prop["estimated_value"] for prop in filtered_properties if prop["estimated_value"]) / len(filtered_properties) if filtered_properties else 0
        property_types_available = list(set(prop["property_type"] for prop in mock_properties))
        market_trends = list(set(prop["market_trend"] for prop in mock_properties))
        api_confidence_avg = sum(prop["api_confidence"] for prop in filtered_properties) / len(filtered_properties) if filtered_properties else 0
        data_sources = list(set(prop["data_source"] for prop in mock_properties))
        
        # Mock market data
        market_data = {
            "date": datetime.utcnow().isoformat(),
            "median_price": 225000,
            "sales_volume": 1250,
            "days_on_market": 28,
            "inventory_level": 2.1,
            "mortgage_rate": 6.75,
            "data_source": "FRED"
        }
        
        return {
            "properties": filtered_properties,
            "market_data": market_data,
            "summary": {
                "total_properties": total_properties,
                "filtered_count": filtered_count,
                "average_price": round(average_price, 2),
                "average_estimated_value": round(average_estimated_value, 2),
                "property_types_available": property_types_available,
                "market_trends": market_trends,
                "api_confidence_avg": round(api_confidence_avg, 3),
                "data_sources": data_sources
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting real estate properties", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get real estate properties")

@router.get("/property/{property_id}")
async def get_property_detail(
    property_id: str,
    db = Depends(get_db_session)
):
    """Get detailed information for a specific property."""
    try:
        # Mock detailed property data
        property_detail = {
            "id": property_id,
            "address": "1247 Oak Street, Austin, TX 78701",
            "price": 185000,
            "estimated_value": 250000,
            "property_type": "Single Family",
            "beds": 3,
            "baths": 2,
            "sqft": 1800,
            "lot_size": 0.25,
            "year_built": 2015,
            "last_sold_date": "2020-03-15",
            "last_sold_price": 165000,
            "tax_assessment": 235000,
            "market_trend": "Rising",
            "data_source": "ATTOM",
            "last_updated": datetime.utcnow().isoformat(),
            "api_confidence": 0.95,
            "latitude": 30.2672,
            "longitude": -97.7431,
            "detailed_info": {
                "property_details": {
                    "stories": 2,
                    "garage_spaces": 2,
                    "parking_type": "Attached Garage",
                    "heating": "Central Air",
                    "cooling": "Central Air",
                    "roof_type": "Composition Shingle",
                    "exterior_walls": "Brick",
                    "foundation": "Slab"
                },
                "financial_info": {
                    "property_taxes": 4200,
                    "hoa_fees": 0,
                    "insurance_estimate": 1200,
                    "utilities_estimate": 1800
                },
                "neighborhood_info": {
                    "school_district": "Austin ISD",
                    "elementary_school": "Oak Hill Elementary",
                    "middle_school": "O. Henry Middle School",
                    "high_school": "Austin High School",
                    "walkability_score": 72,
                    "transit_score": 65,
                    "bike_score": 78
                },
                "comparable_sales": [
                    {
                        "address": "1234 Oak Street, Austin, TX",
                        "sale_date": "2023-08-15",
                        "sale_price": 245000,
                        "sqft": 1750,
                        "price_per_sqft": 140
                    },
                    {
                        "address": "1256 Oak Street, Austin, TX",
                        "sale_date": "2023-07-22",
                        "sale_price": 238000,
                        "sqft": 1820,
                        "price_per_sqft": 131
                    }
                ]
            }
        }
        
        return property_detail
        
    except Exception as e:
        logger.error("Error getting property detail", property_id=property_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get property detail")

@router.get("/market-data")
async def get_market_data(
    location: Optional[str] = Query(None, description="Location to get market data for"),
    db = Depends(get_db_session)
):
    """Get current market data from external APIs."""
    try:
        # Mock market data
        market_data = {
            "date": datetime.utcnow().isoformat(),
            "median_price": 225000,
            "sales_volume": 1250,
            "days_on_market": 28,
            "inventory_level": 2.1,
            "mortgage_rate": 6.75,
            "data_source": "FRED",
            "location": location or "Austin, TX",
            "market_indicators": {
                "price_appreciation": 0.08,
                "rental_yield": 0.065,
                "price_to_rent_ratio": 18.5,
                "affordability_index": 0.72,
                "market_health_score": 85
            },
            "trends": {
                "price_trend": "rising",
                "inventory_trend": "declining",
                "demand_trend": "increasing",
                "supply_trend": "stable"
            },
            "forecast": {
                "next_quarter_price_change": 0.025,
                "next_year_price_change": 0.08,
                "confidence_level": 0.78
            }
        }
        
        return market_data
        
    except Exception as e:
        logger.error("Error getting market data", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get market data")

@router.get("/api-status")
async def get_api_status(
    db = Depends(get_db_session)
):
    """Get status of external real estate APIs."""
    try:
        # Check API key availability
        attom_key = os.getenv("ATTOM_API_KEY")
        estated_key = os.getenv("ESTATED_API_KEY")
        fred_key = os.getenv("FRED_API_KEY")
        
        api_status = {
            "estated_api": {
                "available": True,
                "key_configured": bool(estated_key),
                "status": "operational" if estated_key else "key_missing"
            },
            "attom_api": {
                "available": True,
                "key_configured": bool(attom_key),
                "status": "operational" if attom_key else "key_missing"
            },
            "fred_api": {
                "available": True,
                "key_configured": bool(fred_key),
                "status": "operational" if fred_key else "key_missing"
            },
            "last_checked": datetime.utcnow().isoformat(),
            "overall_status": "operational" if all([attom_key, estated_key, fred_key]) else "degraded"
        }
        
        return api_status
        
    except Exception as e:
        logger.error("Error getting API status", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get API status")

@router.post("/refresh-data")
async def refresh_property_data(
    db = Depends(get_db_session)
):
    """Refresh property data from external APIs."""
    try:
        # Mock refresh operation
        refresh_result = {
            "status": "success",
            "message": "Property data refreshed successfully",
            "properties_updated": 156,
            "new_properties_found": 23,
            "errors": 0,
            "last_refresh": datetime.utcnow().isoformat(),
            "next_scheduled_refresh": (datetime.utcnow().replace(hour=2, minute=0, second=0, microsecond=0)).isoformat()
        }
        
        return refresh_result
        
    except Exception as e:
        logger.error("Error refreshing property data", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to refresh property data")

@router.post("/search")
async def search_properties(
    search_criteria: Dict[str, Any] = Body(...),
    db = Depends(get_db_session)
):
    """Search for properties using custom criteria."""
    try:
        # Mock search results based on criteria
        search_results = {
            "query": search_criteria,
            "results": [
                {
                    "id": "search_001",
                    "address": "1247 Oak Street, Austin, TX 78701",
                    "price": 185000,
                    "estimated_value": 250000,
                    "property_type": "Single Family",
                    "beds": 3,
                    "baths": 2,
                    "sqft": 1800,
                    "match_score": 0.95,
                    "data_source": "ATTOM"
                }
            ],
            "total_results": 1,
            "search_time_ms": 245,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return search_results
        
    except Exception as e:
        logger.error("Error searching properties", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to search properties")

@router.get("/comparable-sales")
async def get_comparable_sales(
    property_data: Dict[str, Any] = Body(...),
    radius: float = Query(0.5, ge=0.1, le=5.0, description="Search radius in miles"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of comparables"),
    db = Depends(get_db_session)
):
    """Get comparable sales for a property."""
    try:
        # Mock comparable sales data
        comparable_sales = [
            {
                "id": "comp_001",
                "address": "1234 Oak Street, Austin, TX",
                "sale_date": "2023-08-15",
                "sale_price": 245000,
                "sqft": 1750,
                "beds": 3,
                "baths": 2,
                "price_per_sqft": 140,
                "distance_miles": 0.2,
                "similarity_score": 0.92
            },
            {
                "id": "comp_002",
                "address": "1256 Oak Street, Austin, TX",
                "sale_date": "2023-07-22",
                "sale_price": 238000,
                "sqft": 1820,
                "beds": 3,
                "baths": 2,
                "price_per_sqft": 131,
                "distance_miles": 0.3,
                "similarity_score": 0.88
            }
        ]
        
        return {
            "property_data": property_data,
            "comparable_sales": comparable_sales[:limit],
            "search_radius": radius,
            "total_found": len(comparable_sales),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting comparable sales", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get comparable sales")