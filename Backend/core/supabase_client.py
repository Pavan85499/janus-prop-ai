"""
Supabase client configuration for Janus Prop AI Backend

This module provides Supabase client initialization and configuration.
"""

import os
from typing import Optional
from supabase import create_client, Client
from config.settings import get_settings

# Global Supabase client instance
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get or create the Supabase client instance."""
    global _supabase_client
    
    if _supabase_client is None:
        settings = get_settings()
        
        if not settings.is_supabase_enabled:
            raise ValueError("Supabase not properly configured. Check environment variables.")
        
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
    
    return _supabase_client

def get_supabase_service_client() -> Client:
    """Get Supabase client with service role key for admin operations."""
    settings = get_settings()
    
    if not settings.is_supabase_enabled:
        raise ValueError("Supabase not properly configured. Check environment variables.")
    
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY
    )

async def test_supabase_connection() -> bool:
    """Test Supabase connection."""
    try:
        client = get_supabase_client()
        # Try to query a simple table to test connection
        response = client.table('users').select('id').limit(1).execute()
        return True
    except Exception as e:
        print(f"Supabase connection test failed: {e}")
        return False

def get_supabase_config() -> dict:
    """Get Supabase configuration for frontend."""
    settings = get_settings()
    
    if not settings.is_supabase_enabled:
        return {}
    
    return {
        "url": settings.SUPABASE_URL,
        "anon_key": settings.SUPABASE_ANON_KEY,
        "project_id": settings.SUPABASE_PROJECT_ID
    }
