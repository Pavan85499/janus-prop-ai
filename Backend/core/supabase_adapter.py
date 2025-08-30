"""
Supabase database adapter for Janus Prop AI Backend

This module provides a Supabase-specific database adapter that works with the existing models.
"""

from typing import Optional, List, Dict, Any, TypeVar, Generic
from pydantic import BaseModel
from core.supabase_client import get_supabase_client, get_supabase_service_client
from config.settings import get_settings

T = TypeVar('T', bound=BaseModel)

class SupabaseAdapter:
    """Supabase database adapter for CRUD operations."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.client = get_supabase_client()
        self.service_client = get_supabase_service_client()
    
    async def create(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new record."""
        try:
            response = self.client.table(self.table_name).insert(data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error creating record in {self.table_name}: {e}")
            return None
    
    async def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a record by ID."""
        try:
            response = self.client.table(self.table_name).select('*').eq('id', record_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error getting record from {self.table_name}: {e}")
            return None
    
    async def get_all(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all records with optional filters."""
        try:
            query = self.client.table(self.table_name).select('*').limit(limit)
            
            if filters:
                for key, value in filters.items():
                    if isinstance(value, (list, tuple)):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            response = query.execute()
            return response.data or []
        except Exception as e:
            print(f"Error getting records from {self.table_name}: {e}")
            return []
    
    async def update(self, record_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record."""
        try:
            response = self.client.table(self.table_name).update(data).eq('id', record_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error updating record in {self.table_name}: {e}")
            return None
    
    async def delete(self, record_id: str) -> bool:
        """Delete a record."""
        try:
            response = self.client.table(self.table_name).delete().eq('id', record_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting record from {self.table_name}: {e}")
            return False
    
    async def search(self, search_term: str, search_fields: List[str], limit: int = 100) -> List[Dict[str, Any]]:
        """Search records by text in specified fields."""
        try:
            # For Supabase, we'll use a simple approach with ILIKE
            # In production, you might want to use full-text search
            query = self.client.table(self.table_name).select('*').limit(limit)
            
            # Build OR conditions for search fields
            search_conditions = []
            for field in search_fields:
                search_conditions.append(f"{field}.ilike.%{search_term}%")
            
            if search_conditions:
                query = query.or_(','.join(search_conditions))
            
            response = query.execute()
            return response.data or []
        except Exception as e:
            print(f"Error searching records in {self.table_name}: {e}")
            return []
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Get count of records with optional filters."""
        try:
            query = self.client.table(self.table_name).select('*', count='exact')
            
            if filters:
                for key, value in filters.items():
                    if isinstance(value, (list, tuple)):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            response = query.execute()
            return response.count or 0
        except Exception as e:
            print(f"Error counting records in {self.table_name}: {e}")
            return 0

# Factory function to create adapters for different tables
def get_supabase_adapter(table_name: str) -> SupabaseAdapter:
    """Get a Supabase adapter for a specific table."""
    return SupabaseAdapter(table_name)

# Pre-configured adapters for common tables
users_adapter = get_supabase_adapter('users')
agents_adapter = get_supabase_adapter('agents')
properties_adapter = get_supabase_adapter('properties')
leads_adapter = get_supabase_adapter('leads')
market_data_adapter = get_supabase_adapter('market_data')
ai_insights_adapter = get_supabase_adapter('ai_insights')
user_agent_assignments_adapter = get_supabase_adapter('user_agent_assignments')
