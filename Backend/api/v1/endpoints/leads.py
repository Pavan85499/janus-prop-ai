"""
Leads API endpoints for Janus Prop AI Backend

This module provides endpoints for lead management and tracking.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from pydantic import BaseModel, Field

from core.database import get_db_session
from core.redis_client import cache_get, cache_set, cache_delete, publish_event
from core.websocket_manager import get_websocket_manager

router = APIRouter()

# Pydantic models
class Lead(BaseModel):
    """Lead model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    source: str  # "website", "referral", "social_media", "cold_call"
    status: str = "new"  # "new", "contacted", "qualified", "proposal", "closed", "lost"
    priority: str = "medium"  # "low", "medium", "high", "urgent"
    assigned_agent: Optional[str] = None
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_contact: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None
    notes: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    budget_range: Optional[str] = None
    property_preferences: Optional[Dict[str, Any]] = None
    lead_score: int = Field(default=0, ge=0, le=100)

class LeadNote(BaseModel):
    """Lead note model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    lead_id: str
    agent_id: str
    content: str
    note_type: str = "general"  # "general", "follow_up", "meeting", "proposal"
    created_date: datetime = Field(default_factory=datetime.utcnow)

class LeadResponse(BaseModel):
    """Lead response model."""
    leads: List[Lead]
    total: int
    page: int
    page_size: int
    filters: Dict[str, Any]

# Mock data for development
MOCK_LEADS = [
    Lead(
        first_name="John",
        last_name="Smith",
        email="john.smith@email.com",
        phone="555-0123",
        source="website",
        status="qualified",
        priority="high",
        assigned_agent="eden",
        last_contact=datetime.utcnow() - timedelta(days=2),
        next_follow_up=datetime.utcnow() + timedelta(days=3),
        notes=["Interested in downtown properties", "Budget: $700k-$900k"],
        tags=["buyer", "downtown", "high_budget"],
        budget_range="700k-900k",
        property_preferences={
            "property_type": "single_family",
            "bedrooms": 3,
            "bathrooms": 2.5,
            "location": "downtown"
        },
        lead_score=85
    ),
    Lead(
        first_name="Sarah",
        last_name="Johnson",
        email="sarah.j@email.com",
        phone="555-0456",
        source="referral",
        status="new",
        priority="medium",
        notes=["Referred by existing client", "Looking for investment property"],
        tags=["buyer", "investment", "referral"],
        budget_range="400k-600k",
        property_preferences={
            "property_type": "condo",
            "bedrooms": 2,
            "bathrooms": 2,
            "location": "uptown"
        },
        lead_score=65
    )
]

MOCK_LEAD_NOTES = [
    LeadNote(
        lead_id=MOCK_LEADS[0].id,
        agent_id="eden",
        content="Initial contact made. Client is very interested in downtown properties.",
        note_type="general"
    ),
    LeadNote(
        lead_id=MOCK_LEADS[0].id,
        agent_id="eden",
        content="Scheduled property viewing for next week.",
        note_type="follow_up"
    )
]

@router.get("/", response_model=LeadResponse)
async def get_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    source: Optional[str] = None,
    assigned_agent: Optional[str] = None
):
    """Get leads with filtering and pagination."""
    try:
        # Filter leads based on query parameters
        filtered_leads = MOCK_LEADS.copy()
        
        if status:
            filtered_leads = [l for l in filtered_leads if l.status == status]
        if priority:
            filtered_leads = [l for l in filtered_leads if l.priority == priority]
        if source:
            filtered_leads = [l for l in filtered_leads if l.source == source]
        if assigned_agent:
            filtered_leads = [l for l in filtered_leads if l.assigned_agent == assigned_agent]
        
        # Calculate pagination
        total = len(filtered_leads)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_leads = filtered_leads[start_idx:end_idx]
        
        # Build filters dict
        filters = {
            "status": status,
            "priority": priority,
            "source": source,
            "assigned_agent": assigned_agent
        }
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        return LeadResponse(
            leads=paginated_leads,
            total=total,
            page=page,
            page_size=page_size,
            filters=filters
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch leads: {str(e)}")

@router.get("/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str):
    """Get a specific lead by ID."""
    try:
        # Try to get from cache first
        cached_lead = await cache_get(f"lead:{lead_id}")
        if cached_lead:
            return Lead(**cached_lead)
        
        # Find lead in mock data
        lead_obj = None
        for lead in MOCK_LEADS:
            if lead.id == lead_id:
                lead_obj = lead
                break
        
        if not lead_obj:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Cache the lead
        await cache_set(f"lead:{lead_id}", lead_obj.dict(), expire=1800)
        
        return lead_obj
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch lead: {str(e)}")

@router.post("/", response_model=Lead)
async def create_lead(
    lead_data: Lead,
    background_tasks: BackgroundTasks
):
    """Create a new lead."""
    try:
        # Set ID and timestamps
        lead_data.id = str(uuid4())
        lead_data.created_date = datetime.utcnow()
        
        # Add to mock leads (in real app, this would go to database)
        MOCK_LEADS.append(lead_data)
        
        # Cache the lead
        await cache_set(f"lead:{lead_data.id}", lead_data.dict(), expire=1800)
        
        # Publish real-time update
        await publish_event(
            "leads",
            "lead_created",
            lead_data.dict()
        )
        
        # Send WebSocket update
        websocket_manager = get_websocket_manager()
        await websocket_manager.send_lead_update(lead_data.id, {
            "type": "lead_created",
            "lead": lead_data.dict()
        })
        
        return lead_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create lead: {str(e)}")

@router.put("/{lead_id}", response_model=Lead)
async def update_lead(
    lead_id: str,
    lead_update: Dict[str, Any]
):
    """Update a lead."""
    try:
        # Find lead in mock data
        lead_index = None
        for i, lead in enumerate(MOCK_LEADS):
            if lead.id == lead_id:
                lead_index = i
                break
        
        if lead_index is None:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Update lead
        lead_obj = MOCK_LEADS[lead_index]
        for field, value in lead_update.items():
            if hasattr(lead_obj, field):
                setattr(lead_obj, field, value)
        
        # Update cache
        await cache_set(f"lead:{lead_id}", lead_obj.dict(), expire=1800)
        
        # Publish real-time update
        await publish_event(
            f"lead:{lead_id}",
            "lead_updated",
            lead_obj.dict()
        )
        
        # Send WebSocket update
        websocket_manager = get_websocket_manager()
        await websocket_manager.send_lead_update(lead_id, {
            "type": "lead_updated",
            "lead": lead_obj.dict()
        })
        
        return lead_obj
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update lead: {str(e)}")

@router.delete("/{lead_id}")
async def delete_lead(lead_id: str):
    """Delete a lead."""
    try:
        # Find and remove lead
        lead_index = None
        for i, lead in enumerate(MOCK_LEADS):
            if lead.id == lead_id:
                lead_index = i
                break
        
        if lead_index is None:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        removed_lead = MOCK_LEADS.pop(lead_index)
        
        # Remove from cache
        await cache_delete(f"lead:{lead_id}")
        
        # Publish real-time update
        await publish_event(
            "leads",
            "lead_deleted",
            {"lead_id": lead_id}
        )
        
        return {"success": True, "message": "Lead deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete lead: {str(e)}")

@router.get("/{lead_id}/notes", response_model=List[LeadNote])
async def get_lead_notes(lead_id: str):
    """Get notes for a specific lead."""
    try:
        # Filter notes by lead ID
        lead_notes = [note for note in MOCK_LEAD_NOTES if note.lead_id == lead_id]
        
        # Sort by creation date (newest first)
        lead_notes.sort(key=lambda x: x.created_date, reverse=True)
        
        return lead_notes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch lead notes: {str(e)}")

@router.post("/{lead_id}/notes", response_model=LeadNote)
async def create_lead_note(
    lead_id: str,
    note_data: LeadNote
):
    """Create a new note for a lead."""
    try:
        # Validate lead exists
        lead_exists = any(lead.id == lead_id for lead in MOCK_LEADS)
        if not lead_exists:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Set note data
        note_data.id = str(uuid4())
        note_data.lead_id = lead_id
        note_data.created_date = datetime.utcnow()
        
        # Add to mock notes
        MOCK_LEAD_NOTES.append(note_data)
        
        # Update lead's last_contact
        for lead in MOCK_LEADS:
            if lead.id == lead_id:
                lead.last_contact = datetime.utcnow()
                break
        
        return note_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create lead note: {str(e)}")

@router.get("/status/summary")
async def get_leads_status_summary():
    """Get summary of leads by status."""
    try:
        status_counts = {}
        priority_counts = {}
        source_counts = {}
        
        for lead in MOCK_LEADS:
            # Count by status
            status_counts[lead.status] = status_counts.get(lead.status, 0) + 1
            
            # Count by priority
            priority_counts[lead.priority] = priority_counts.get(lead.priority, 0) + 1
            
            # Count by source
            source_counts[lead.source] = source_counts.get(lead.source, 0) + 1
        
        return {
            "total_leads": len(MOCK_LEADS),
            "status_breakdown": status_counts,
            "priority_breakdown": priority_counts,
            "source_breakdown": source_counts,
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate leads summary: {str(e)}")

@router.get("/search")
async def search_leads(
    query: str = Query(..., min_length=2),
    status: Optional[str] = None,
    priority: Optional[str] = None
):
    """Search leads by name, email, or other criteria."""
    try:
        query_lower = query.lower()
        search_results = []
        
        for lead in MOCK_LEADS:
            # Search in name, email, and notes
            if (query_lower in lead.first_name.lower() or
                query_lower in lead.last_name.lower() or
                query_lower in lead.email.lower() or
                any(query_lower in note.lower() for note in lead.notes)):
                
                # Apply additional filters
                if status and lead.status != status:
                    continue
                if priority and lead.priority != priority:
                    continue
                
                search_results.append(lead)
        
        return {
            "query": query,
            "results": search_results,
            "total_found": len(search_results),
            "filters": {
                "status": status,
                "priority": priority
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lead search failed: {str(e)}")

@router.post("/{lead_id}/assign")
async def assign_lead(
    lead_id: str,
    agent_id: str
):
    """Assign a lead to an agent."""
    try:
        # Find lead
        lead_obj = None
        for lead in MOCK_LEADS:
            if lead.id == lead_id:
                lead_obj = lead
                break
        
        if not lead_obj:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Update assignment
        lead_obj.assigned_agent = agent_id
        
        # Update cache
        await cache_set(f"lead:{lead_id}", lead_obj.dict(), expire=1800)
        
        # Publish real-time update
        await publish_event(
            f"lead:{lead_id}",
            "lead_assigned",
            {"lead_id": lead_id, "agent_id": agent_id}
        )
        
        return {"success": True, "message": f"Lead assigned to agent {agent_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assign lead: {str(e)}")

@router.post("/{lead_id}/status")
async def update_lead_status(
    lead_id: str,
    status: str,
    notes: Optional[str] = None
):
    """Update lead status."""
    try:
        # Find lead
        lead_obj = None
        for lead in MOCK_LEADS:
            if lead.id == lead_id:
                lead_obj = lead
                break
        
        if not lead_obj:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Update status
        lead_obj.status = status
        
        # Add note if provided
        if notes:
            lead_obj.notes.append(f"Status changed to {status}: {notes}")
        
        # Update cache
        await cache_set(f"lead:{lead_id}", lead_obj.dict(), expire=1800)
        
        # Publish real-time update
        await publish_event(
            f"lead:{lead_id}",
            "lead_status_updated",
            {"lead_id": lead_id, "status": status, "notes": notes}
        )
        
        return {"success": True, "message": f"Lead status updated to {status}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update lead status: {str(e)}")
