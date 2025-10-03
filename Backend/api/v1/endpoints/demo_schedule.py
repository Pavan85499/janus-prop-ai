"""
Demo Schedule API endpoints for Janus Prop AI Backend

This module provides endpoints for scheduling and managing demo requests.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4
from enum import Enum

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from pydantic import BaseModel, Field, EmailStr

from core.database import get_db_session
from core.redis_client import cache_get, cache_set, cache_delete, publish_event
from core.websocket_manager import get_websocket_manager

router = APIRouter()

# Enums
class DemoType(str, Enum):
    """Demo type enumeration."""
    PLATFORM_OVERVIEW = "platform_overview"
    AI_AGENTS = "ai_agents"
    PROPERTY_ANALYSIS = "property_analysis"
    MARKET_INTELLIGENCE = "market_intelligence"
    INVESTMENT_OPPORTUNITIES = "investment_opportunities"
    CUSTOM = "custom"

class DemoStatus(str, Enum):
    """Demo status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"

class TimeSlot(BaseModel):
    """Available time slot model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    start_time: datetime
    end_time: datetime
    is_available: bool = True
    timezone: str = "UTC"

class DemoRequest(BaseModel):
    """Demo request model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    company: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    demo_type: DemoType
    preferred_date: datetime
    preferred_time_slots: List[str] = Field(default_factory=list)  # Time slot IDs
    timezone: str = Field(default="UTC")
    company_size: Optional[str] = None  # "startup", "small", "medium", "enterprise"
    current_solution: Optional[str] = None
    specific_requirements: Optional[str] = Field(None, max_length=1000)
    status: DemoStatus = DemoStatus.PENDING
    assigned_representative: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class DemoRequestCreate(BaseModel):
    """Demo request creation model."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    company: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    demo_type: DemoType
    preferred_date: datetime
    preferred_time_slots: List[str] = Field(default_factory=list)
    timezone: str = Field(default="UTC")
    company_size: Optional[str] = None
    current_solution: Optional[str] = None
    specific_requirements: Optional[str] = Field(None, max_length=1000)

class DemoRequestUpdate(BaseModel):
    """Demo request update model."""
    status: Optional[DemoStatus] = None
    assigned_representative: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[List[str]] = None
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class DemoAvailability(BaseModel):
    """Demo availability model."""
    date: datetime
    available_slots: List[TimeSlot]
    timezone: str = "UTC"

# Mock data storage (in production, this would be in a database)
demo_requests_db: Dict[str, DemoRequest] = {}
time_slots_db: Dict[str, TimeSlot] = {}

# Initialize some mock time slots
def initialize_mock_data():
    """Initialize mock data for development."""
    base_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Create time slots for the next 7 days
    for day_offset in range(7):
        current_date = base_date + timedelta(days=day_offset)
        
        # Skip weekends for demo scheduling
        if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            continue
            
        # Create 4 time slots per day (9 AM, 11 AM, 2 PM, 4 PM UTC)
        for hour in [9, 11, 14, 16]:
            slot_start = current_date.replace(hour=hour, minute=0)
            slot_end = slot_start + timedelta(hours=1)
            
            slot = TimeSlot(
                start_time=slot_start,
                end_time=slot_end,
                is_available=True,
                timezone="UTC"
            )
            time_slots_db[slot.id] = slot

# Initialize mock data
initialize_mock_data()

@router.get("/availability", response_model=List[DemoAvailability])
async def get_demo_availability(
    start_date: Optional[datetime] = Query(None, description="Start date for availability search"),
    end_date: Optional[datetime] = Query(None, description="End date for availability search"),
    timezone: str = Query("UTC", description="Timezone for the request")
):
    """Get available demo time slots."""
    try:
        # Default to next 7 days if no dates provided
        if not start_date:
            start_date = datetime.utcnow()
        if not end_date:
            end_date = start_date + timedelta(days=7)
        
        # Group time slots by date
        availability_by_date: Dict[str, List[TimeSlot]] = {}
        
        for slot in time_slots_db.values():
            if start_date <= slot.start_time <= end_date and slot.is_available:
                date_key = slot.start_time.date().isoformat()
                if date_key not in availability_by_date:
                    availability_by_date[date_key] = []
                availability_by_date[date_key].append(slot)
        
        # Convert to DemoAvailability objects
        availability_list = []
        for date_str, slots in availability_by_date.items():
            date_obj = datetime.fromisoformat(date_str)
            availability_list.append(DemoAvailability(
                date=date_obj,
                available_slots=sorted(slots, key=lambda x: x.start_time),
                timezone=timezone
            ))
        
        return sorted(availability_list, key=lambda x: x.date)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get demo availability: {str(e)}")

@router.post("/request", response_model=DemoRequest)
async def create_demo_request(
    request_data: DemoRequestCreate,
    background_tasks: BackgroundTasks
):
    """Create a new demo request."""
    try:
        # Validate time slots
        for slot_id in request_data.preferred_time_slots:
            if slot_id not in time_slots_db:
                raise HTTPException(status_code=400, detail=f"Invalid time slot ID: {slot_id}")
            if not time_slots_db[slot_id].is_available:
                raise HTTPException(status_code=400, detail=f"Time slot {slot_id} is no longer available")
        
        # Create demo request
        demo_request = DemoRequest(
            **request_data.dict(),
            status=DemoStatus.PENDING
        )
        
        # Store in mock database
        demo_requests_db[demo_request.id] = demo_request
        
        # Mark time slots as unavailable
        for slot_id in request_data.preferred_time_slots:
            time_slots_db[slot_id].is_available = False
        
        # Publish event for real-time updates
        try:
            await publish_event(
                "demo_requests",
                "demo_request_created",
                {
                    "request_id": demo_request.id,
                    "email": demo_request.email,
                    "demo_type": demo_request.demo_type,
                    "preferred_date": demo_request.preferred_date.isoformat()
                }
            )
        except Exception:
            # Ignore Redis publish errors
            pass
        
        # Add background task for sending confirmation email
        background_tasks.add_task(send_demo_confirmation_email, demo_request)
        
        return demo_request
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create demo request: {str(e)}")

@router.get("/requests", response_model=List[DemoRequest])
async def get_demo_requests(
    status: Optional[DemoStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip")
):
    """Get demo requests with optional filtering."""
    try:
        requests = list(demo_requests_db.values())
        
        # Filter by status if provided
        if status:
            requests = [req for req in requests if req.status == status]
        
        # Sort by created_at descending
        requests.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        return requests[offset:offset + limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get demo requests: {str(e)}")

@router.get("/requests/{request_id}", response_model=DemoRequest)
async def get_demo_request(request_id: str):
    """Get a specific demo request by ID."""
    try:
        if request_id not in demo_requests_db:
            raise HTTPException(status_code=404, detail="Demo request not found")
        
        return demo_requests_db[request_id]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get demo request: {str(e)}")

@router.put("/requests/{request_id}", response_model=DemoRequest)
async def update_demo_request(
    request_id: str,
    update_data: DemoRequestUpdate
):
    """Update a demo request."""
    try:
        if request_id not in demo_requests_db:
            raise HTTPException(status_code=404, detail="Demo request not found")
        
        demo_request = demo_requests_db[request_id]
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(demo_request, field, value)
        
        demo_request.updated_at = datetime.utcnow()
        
        # Publish event for real-time updates
        try:
            await publish_event(
                "demo_requests",
                "demo_request_updated",
                {
                    "request_id": request_id,
                    "status": demo_request.status,
                    "updated_at": demo_request.updated_at.isoformat()
                }
            )
        except Exception:
            # Ignore Redis publish errors
            pass
        
        return demo_request
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update demo request: {str(e)}")

@router.delete("/requests/{request_id}")
async def cancel_demo_request(request_id: str):
    """Cancel a demo request."""
    try:
        if request_id not in demo_requests_db:
            raise HTTPException(status_code=404, detail="Demo request not found")
        
        demo_request = demo_requests_db[request_id]
        
        # Update status
        demo_request.status = DemoStatus.CANCELLED
        demo_request.updated_at = datetime.utcnow()
        
        # Make time slots available again
        for slot_id in demo_request.preferred_time_slots:
            if slot_id in time_slots_db:
                time_slots_db[slot_id].is_available = True
        
        # Publish event for real-time updates
        try:
            await publish_event(
                "demo_requests",
                "demo_request_cancelled",
                {
                    "request_id": request_id,
                    "cancelled_at": demo_request.updated_at.isoformat()
                }
            )
        except Exception:
            # Ignore Redis publish errors
            pass
        
        return {"message": "Demo request cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel demo request: {str(e)}")

@router.get("/stats")
async def get_demo_stats():
    """Get demo request statistics."""
    try:
        total_requests = len(demo_requests_db)
        
        # Count by status
        status_counts = {}
        for status in DemoStatus:
            status_counts[status.value] = sum(1 for req in demo_requests_db.values() if req.status == status)
        
        # Count by demo type
        type_counts = {}
        for demo_type in DemoType:
            type_counts[demo_type.value] = sum(1 for req in demo_requests_db.values() if req.demo_type == demo_type)
        
        # Recent requests (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_requests = sum(1 for req in demo_requests_db.values() if req.created_at >= week_ago)
        
        return {
            "total_requests": total_requests,
            "status_breakdown": status_counts,
            "type_breakdown": type_counts,
            "recent_requests": recent_requests,
            "available_slots": sum(1 for slot in time_slots_db.values() if slot.is_available)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get demo stats: {str(e)}")

# Background task functions
async def send_demo_confirmation_email(demo_request: DemoRequest):
    """Send confirmation email for demo request."""
    # In production, this would integrate with an email service
    print(f"Demo confirmation email sent to {demo_request.email} for {demo_request.demo_type} demo")
    
    # Simulate email sending delay
    import asyncio
    await asyncio.sleep(1)
    
    # Update request with confirmation
    demo_request.notes.append(f"Confirmation email sent at {datetime.utcnow().isoformat()}")
