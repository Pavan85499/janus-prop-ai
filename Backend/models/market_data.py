"""
Market Data model for Janus Prop AI Backend

This module defines the MarketData database model.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class MarketData(Base):
    """Market Data database model."""
    
    __tablename__ = "market_data"
    
    id = Column(String(36), primary_key=True, index=True)
    location = Column(String(255), nullable=False, index=True)
    property_type = Column(String(100), nullable=False, index=True)
    data_type = Column(String(100), nullable=False)
    value = Column(Float, nullable=True)
    trend = Column(String(50), nullable=True)
    period = Column(String(50), nullable=True)
    data_source = Column(String(100), nullable=False)
    data_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.utcnow)
    updated_at = Column(DateTime, default=func.utcnow, onupdate=func.utcnow)
    
    def __repr__(self):
        return f"<MarketData(id='{self.id}', location='{self.location}', type='{self.data_type}')>"
