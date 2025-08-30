"""
Agent model for Janus Prop AI Backend

This module defines the Agent database model.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Agent(Base):
    """Agent database model."""
    
    __tablename__ = "agents"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    agent_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.utcnow)
    updated_at = Column(DateTime, default=func.utcnow, onupdate=func.utcnow)
    
    def __repr__(self):
        return f"<Agent(id='{self.id}', name='{self.name}', type='{self.agent_type}')>"
