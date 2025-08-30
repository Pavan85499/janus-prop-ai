"""
Lead model for Janus Prop AI Backend

This module defines the Lead database model.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Lead(Base):
    """Lead database model."""
    
    __tablename__ = "leads"
    
    id = Column(String(36), primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    source = Column(String(100), nullable=False)
    status = Column(String(50), default="new")
    priority = Column(String(50), default="medium")
    assigned_agent_id = Column(String(36), nullable=True, index=True)
    notes = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    budget_range = Column(String(100), nullable=True)
    property_preferences = Column(JSON, nullable=True)
    lead_score = Column(String(10), default="0")
    created_at = Column(DateTime, default=func.utcnow)
    updated_at = Column(DateTime, default=func.utcnow, onupdate=func.utcnow)
    
    def __repr__(self):
        return f"<Lead(id='{self.id}', name='{self.first_name} {self.last_name}')>"
