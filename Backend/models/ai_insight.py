"""
AI Insight model for Janus Prop AI Backend

This module defines the AIInsight database model.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class AIInsight(Base):
    """AI Insight database model."""
    
    __tablename__ = "ai_insights"
    
    id = Column(String(36), primary_key=True, index=True)
    property_id = Column(String(36), nullable=True, index=True)
    insight_type = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    ai_model = Column(String(100), nullable=False)
    tags = Column(JSON, nullable=True)
    insight_metadata = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.utcnow)
    updated_at = Column(DateTime, default=func.utcnow, onupdate=func.utcnow)
    
    def __repr__(self):
        return f"<AIInsight(id='{self.id}', type='{self.insight_type}', title='{self.title}')>"
