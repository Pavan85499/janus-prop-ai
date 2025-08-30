"""
User model for Janus Prop AI Backend

This module defines the User database model.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    """User database model."""
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.utcnow)
    updated_at = Column(DateTime, default=func.utcnow, onupdate=func.utcnow)
    
    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}')>"
