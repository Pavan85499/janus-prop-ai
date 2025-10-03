"""
Supabase client for Janus Prop AI Backend

This module handles Supabase connections and operations.
"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

import structlog
from config.settings import get_settings

logger = structlog.get_logger()

# Global Supabase client
_supabase_client = None

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase library not available")

async def init_supabase() -> Optional[Any]:
    """Initialize Supabase client."""
    global _supabase_client
    
    if not SUPABASE_AVAILABLE:
        logger.warning("Supabase library not available")
        return None
    
    settings = get_settings()
    
    if not settings.is_supabase_enabled:
        logger.info("Supabase not configured")
        return None
    
    try:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
        
        logger.info("Supabase client initialized", project_id=settings.SUPABASE_PROJECT_ID)
        return _supabase_client
        
    except Exception as e:
        logger.error("Failed to initialize Supabase client", error=str(e))
        return None

def get_supabase_client():
    """Get the Supabase client instance."""
    return _supabase_client

async def test_supabase_connection() -> bool:
    """Test Supabase connection."""
    try:
        if not _supabase_client:
            return False
        
        # Try to perform a simple query to test connection
        # This is a basic test - in production you might want to query a specific table
        result = _supabase_client.table('users').select('id').limit(1).execute()
        return True
        
    except Exception as e:
        logger.warning("Supabase connection test failed", error=str(e))
        return False

async def get_supabase_status() -> Dict[str, Any]:
    """Get Supabase connection status."""
    settings = get_settings()
    
    if not SUPABASE_AVAILABLE:
        return {
            "enabled": False,
            "connected": False,
            "error": "Supabase library not available"
        }
    
    if not settings.is_supabase_enabled:
        return {
            "enabled": False,
            "connected": False,
            "project_id": None,
            "url": None
        }
    
    is_connected = await test_supabase_connection()
    
    return {
        "enabled": True,
        "connected": is_connected,
        "project_id": settings.SUPABASE_PROJECT_ID,
        "url": settings.SUPABASE_URL,
        "last_check": datetime.utcnow().isoformat()
    }

async def get_supabase_config() -> Dict[str, Any]:
    """Get Supabase configuration (safe for client)."""
    settings = get_settings()
    
    return {
        "url": settings.SUPABASE_URL if settings.is_supabase_enabled else None,
        "anon_key": settings.SUPABASE_ANON_KEY if settings.is_supabase_enabled else None,
        "project_id": settings.SUPABASE_PROJECT_ID if settings.is_supabase_enabled else None,
        "enabled": settings.is_supabase_enabled
    }

__all__ = [
    "init_supabase",
    "get_supabase_client", 
    "test_supabase_connection",
    "get_supabase_status",
    "get_supabase_config"
]