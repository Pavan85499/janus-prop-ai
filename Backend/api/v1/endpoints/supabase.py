"""
Supabase configuration endpoints for Janus Prop AI Backend

This module provides endpoints for Supabase configuration and management.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from core.supabase_client import get_supabase_config, test_supabase_connection
from config.settings import get_settings

router = APIRouter()

class SupabaseConfig(BaseModel):
    """Supabase configuration model."""
    url: str
    anon_key: str
    project_id: str
    enabled: bool

class SupabaseStatus(BaseModel):
    """Supabase status model."""
    enabled: bool
    connected: bool
    project_id: str
    url: str

@router.get("/config", response_model=SupabaseConfig)
async def get_supabase_configuration():
    """Get Supabase configuration for frontend."""
    try:
        settings = get_settings()
        
        if not settings.is_supabase_enabled:
            raise HTTPException(
                status_code=404, 
                detail="Supabase not configured"
            )
        
        config = get_supabase_config()
        
        return SupabaseConfig(
            url=config["url"],
            anon_key=config["anon_key"],
            project_id=config["project_id"],
            enabled=True
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get Supabase configuration: {str(e)}"
        )

@router.get("/status", response_model=SupabaseStatus)
async def get_supabase_status():
    """Get Supabase connection status."""
    try:
        settings = get_settings()
        
        if not settings.is_supabase_enabled:
            return SupabaseStatus(
                enabled=False,
                connected=False,
                project_id="",
                url=""
            )
        
        # Test connection
        connected = await test_supabase_connection()
        
        return SupabaseStatus(
            enabled=True,
            connected=connected,
            project_id=settings.SUPABASE_PROJECT_ID,
            url=settings.SUPABASE_URL
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get Supabase status: {str(e)}"
        )

@router.post("/test-connection")
async def test_supabase_connection_endpoint():
    """Test Supabase connection."""
    try:
        settings = get_settings()
        
        if not settings.is_supabase_enabled:
            raise HTTPException(
                status_code=400, 
                detail="Supabase not configured"
            )
        
        connected = await test_supabase_connection()
        
        if connected:
            return {"status": "success", "message": "Supabase connection successful"}
        else:
            return {"status": "error", "message": "Supabase connection failed"}
            
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Connection test failed: {str(e)}"
        )
