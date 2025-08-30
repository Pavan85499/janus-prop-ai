"""
Properties API endpoints for Janus Prop AI Backend

This module provides endpoints for property management and real-time updates.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from pydantic import BaseModel, Field

from core.database import get_db_session
from core.redis_client import cache_get, cache_set, cache_delete, publish_event
from core.websocket_manager import get_websocket_manager

router = APIRouter()

# Pydantic models
class Property(BaseModel):
    """Property model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    address: str
    city: str
    state: str
    zip_code: str
    property_type: str  # "single_family", "condo", "townhouse", "multi_family"
    price: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_feet: Optional[int] = None
    lot_size: Optional[float] = None
    year_built: Optional[int] = None
    status: str = "active"  # "active", "pending", "sold", "off_market"
    listing_date: Optional[datetime] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    features: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    agent_id: Optional[str] = None
    mls_id: Optional[str] = None

class PropertySearch(BaseModel):
    """Property search criteria."""
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    property_type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_bathrooms: Optional[float] = None
    max_bathrooms: Optional[float] = None
    min_square_feet: Optional[int] = None
    max_square_feet: Optional[int] = None
    status: Optional[str] = None

class PropertyResponse(BaseModel):
    """Property response model."""
    properties: List[Property]
    total: int
    page: int
    page_size: int
    filters: Dict[str, Any]

# Mock data for development
MOCK_PROPERTIES = [
    Property(
        address="123 Main St",
        city="Downtown",
        state="CA",
        zip_code="90210",
        property_type="single_family",
        price=750000,
        bedrooms=3,
        bathrooms=2.5,
        square_feet=2200,
        lot_size=0.25,
        year_built=1995,
        features=["garage", "pool", "fireplace"],
        description="Beautiful family home in prime location"
    ),
    Property(
        address="456 Oak Ave",
        city="Uptown",
        state="CA",
        zip_code="90211",
        property_type="condo",
        price=450000,
        bedrooms=2,
        bathrooms=2,
        square_feet=1500,
        year_built=2010,
        features=["balcony", "gym", "parking"],
        description="Modern condo with city views"
    ),
    Property(
        address="789 Pine St",
        city="Midtown",
        state="CA",
        zip_code="90212",
        property_type="townhouse",
        price=650000,
        bedrooms=4,
        bathrooms=3.5,
        square_feet=2800,
        lot_size=0.15,
        year_built=2005,
        features=["patio", "storage", "community_pool"],
        description="Spacious townhouse with modern amenities"
    )
]

@router.get("/", response_model=PropertyResponse)
async def get_properties(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    city: Optional[str] = None,
    state: Optional[str] = None,
    property_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    status: Optional[str] = None
):
    """Get properties with filtering and pagination."""
    try:
        # Filter properties based on query parameters
        filtered_properties = MOCK_PROPERTIES.copy()
        
        if city:
            filtered_properties = [p for p in filtered_properties if p.city.lower() == city.lower()]
        if state:
            filtered_properties = [p for p in filtered_properties if p.state.lower() == state.lower()]
        if property_type:
            filtered_properties = [p for p in filtered_properties if p.property_type == property_type]
        if min_price is not None:
            filtered_properties = [p for p in filtered_properties if p.price and p.price >= min_price]
        if max_price is not None:
            filtered_properties = [p for p in filtered_properties if p.price and p.price <= max_price]
        if status:
            filtered_properties = [p for p in filtered_properties if p.status == status]
        
        # Calculate pagination
        total = len(filtered_properties)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_properties = filtered_properties[start_idx:end_idx]
        
        # Build filters dict
        filters = {
            "city": city,
            "state": state,
            "property_type": property_type,
            "min_price": min_price,
            "max_price": max_price,
            "status": status
        }
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        return PropertyResponse(
            properties=paginated_properties,
            total=total,
            page=page,
            page_size=page_size,
            filters=filters
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch properties: {str(e)}")

@router.get("/{property_id}", response_model=Property)
async def get_property(property_id: str):
    """Get a specific property by ID."""
    try:
        # Try to get from cache first
        cached_property = await cache_get(f"property:{property_id}")
        if cached_property:
            return Property(**cached_property)
        
        # Find property in mock data
        property_obj = None
        for prop in MOCK_PROPERTIES:
            if prop.id == property_id:
                property_obj = prop
                break
        
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Cache the property
        await cache_set(f"property:{property_id}", property_obj.dict(), expire=1800)
        
        return property_obj
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch property: {str(e)}")

@router.post("/", response_model=Property)
async def create_property(
    property_data: Property,
    background_tasks: BackgroundTasks
):
    """Create a new property."""
    try:
        # Set ID and timestamps
        property_data.id = str(uuid4())
        property_data.last_updated = datetime.utcnow()
        
        # Add to mock properties (in real app, this would go to database)
        MOCK_PROPERTIES.append(property_data)
        
        # Cache the property
        await cache_set(f"property:{property_data.id}", property_data.dict(), expire=1800)
        
        # Publish real-time update
        await publish_event(
            "properties",
            "property_created",
            property_data.dict()
        )
        
        # Send WebSocket update
        websocket_manager = get_websocket_manager()
        await websocket_manager.send_property_update(property_data.id, {
            "type": "property_created",
            "property": property_data.dict()
        })
        
        return property_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create property: {str(e)}")

@router.put("/{property_id}", response_model=Property)
async def update_property(
    property_id: str,
    property_update: Dict[str, Any]
):
    """Update a property."""
    try:
        # Find property in mock data
        property_index = None
        for i, prop in enumerate(MOCK_PROPERTIES):
            if prop.id == property_id:
                property_index = i
                break
        
        if property_index is None:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Update property
        property_obj = MOCK_PROPERTIES[property_index]
        for field, value in property_update.items():
            if hasattr(property_obj, field):
                setattr(property_obj, field, value)
        
        property_obj.last_updated = datetime.utcnow()
        
        # Update cache
        await cache_set(f"property:{property_id}", property_obj.dict(), expire=1800)
        
        # Publish real-time update
        await publish_event(
            f"property:{property_id}",
            "property_updated",
            property_obj.dict()
        )
        
        # Send WebSocket update
        websocket_manager = get_websocket_manager()
        await websocket_manager.send_property_update(property_id, {
            "type": "property_updated",
            "property": property_obj.dict()
        })
        
        return property_obj
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update property: {str(e)}")

@router.delete("/{property_id}")
async def delete_property(property_id: str):
    """Delete a property."""
    try:
        # Find and remove property
        property_index = None
        for i, prop in enumerate(MOCK_PROPERTIES):
            if prop.id == property_id:
                property_index = i
                break
        
        if property_index is None:
            raise HTTPException(status_code=404, detail="Property not found")
        
        removed_property = MOCK_PROPERTIES.pop(property_index)
        
        # Remove from cache
        await cache_delete(f"property:{property_id}")
        
        # Publish real-time update
        await publish_event(
            "properties",
            "property_deleted",
            {"property_id": property_id}
        )
        
        return {"success": True, "message": "Property deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete property: {str(e)}")

@router.post("/search")
async def search_properties(search_criteria: PropertySearch):
    """Search properties with advanced criteria."""
    try:
        # Apply search criteria
        filtered_properties = MOCK_PROPERTIES.copy()
        
        if search_criteria.city:
            filtered_properties = [p for p in filtered_properties if p.city.lower() == search_criteria.city.lower()]
        if search_criteria.state:
            filtered_properties = [p for p in filtered_properties if p.state.lower() == search_criteria.state.lower()]
        if search_criteria.zip_code:
            filtered_properties = [p for p in filtered_properties if p.zip_code == search_criteria.zip_code]
        if search_criteria.property_type:
            filtered_properties = [p for p in filtered_properties if p.property_type == search_criteria.property_type]
        if search_criteria.min_price is not None:
            filtered_properties = [p for p in filtered_properties if p.price and p.price >= search_criteria.min_price]
        if search_criteria.max_price is not None:
            filtered_properties = [p for p in filtered_properties if p.price and p.price <= search_criteria.max_price]
        if search_criteria.min_bedrooms is not None:
            filtered_properties = [p for p in filtered_properties if p.bedrooms and p.bedrooms >= search_criteria.min_bedrooms]
        if search_criteria.max_bedrooms is not None:
            filtered_properties = [p for p in filtered_properties if p.bedrooms and p.bedrooms <= search_criteria.max_bedrooms]
        if search_criteria.min_bathrooms is not None:
            filtered_properties = [p for p in filtered_properties if p.bathrooms and p.bathrooms >= search_criteria.min_bathrooms]
        if search_criteria.max_bathrooms is not None:
            filtered_properties = [p for p in filtered_properties if p.bathrooms and p.bathrooms <= search_criteria.max_bathrooms]
        if search_criteria.min_square_feet is not None:
            filtered_properties = [p for p in filtered_properties if p.square_feet and p.square_feet >= search_criteria.min_square_feet]
        if search_criteria.max_square_feet is not None:
            filtered_properties = [p for p in filtered_properties if p.square_feet and p.square_feet <= search_criteria.max_square_feet]
        if search_criteria.status:
            filtered_properties = [p for p in filtered_properties if p.status == search_criteria.status]
        
        return {
            "properties": filtered_properties,
            "total": len(filtered_properties),
            "search_criteria": search_criteria.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Property search failed: {str(e)}")

@router.get("/{property_id}/similar")
async def get_similar_properties(property_id: str, limit: int = 5):
    """Get similar properties based on characteristics."""
    try:
        # Find the target property
        target_property = None
        for prop in MOCK_PROPERTIES:
            if prop.id == property_id:
                target_property = prop
                break
        
        if not target_property:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Calculate similarity scores (simplified algorithm)
        similar_properties = []
        for prop in MOCK_PROPERTIES:
            if prop.id == property_id:
                continue
            
            # Simple similarity scoring
            score = 0
            if prop.property_type == target_property.property_type:
                score += 3
            if prop.city == target_property.city:
                score += 2
            if prop.state == target_property.state:
                score += 1
            if prop.bedrooms == target_property.bedrooms:
                score += 2
            if prop.bathrooms == target_property.bathrooms:
                score += 1
            
            # Price range similarity
            if target_property.price and prop.price:
                price_diff = abs(prop.price - target_property.price) / target_property.price
                if price_diff <= 0.2:  # Within 20%
                    score += 2
                elif price_diff <= 0.5:  # Within 50%
                    score += 1
            
            if score > 0:
                similar_properties.append((prop, score))
        
        # Sort by similarity score and return top results
        similar_properties.sort(key=lambda x: x[1], reverse=True)
        top_similar = [prop for prop, score in similar_properties[:limit]]
        
        return {
            "target_property": target_property,
            "similar_properties": top_similar,
            "total_found": len(similar_properties)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find similar properties: {str(e)}")
