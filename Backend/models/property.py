"""
Property model for Janus Prop AI Backend

This module defines the Property database model and related schemas.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Property(Base):
    """Property database model."""
    
    __tablename__ = "properties"
    
    # Primary key
    id = Column(String(36), primary_key=True, index=True)
    
    # Basic property information
    address = Column(String(255), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(50), nullable=False, index=True)
    zip_code = Column(String(20), nullable=True, index=True)
    county = Column(String(100), nullable=True)
    country = Column(String(50), default="USA")
    
    # Property details
    property_type = Column(String(100), nullable=False, index=True)  # residential, commercial, land, etc.
    property_subtype = Column(String(100), nullable=True)  # single_family, condo, townhouse, etc.
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Float, nullable=True)
    square_feet = Column(Integer, nullable=True)
    lot_size = Column(Integer, nullable=True)  # in square feet
    year_built = Column(Integer, nullable=True)
    
    # Financial information
    list_price = Column(Float, nullable=True)
    estimated_value = Column(Float, nullable=True)
    last_sold_price = Column(Float, nullable=True)
    last_sold_date = Column(DateTime, nullable=True)
    tax_assessment = Column(Float, nullable=True)
    property_tax = Column(Float, nullable=True)
    
    # Property status
    status = Column(String(50), default="active")  # active, sold, pending, off_market
    listing_date = Column(DateTime, nullable=True)
    days_on_market = Column(Integer, default=0)
    
    # Property features
    features = Column(JSON, nullable=True)  # amenities, upgrades, etc.
    description = Column(Text, nullable=True)
    images = Column(JSON, nullable=True)  # array of image URLs
    
    # Location data
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    neighborhood = Column(String(100), nullable=True)
    school_district = Column(String(100), nullable=True)
    
    # Market data
    market_data = Column(JSON, nullable=True)  # market trends, comparables, etc.
    
    # Metadata
    created_at = Column(DateTime, default=func.utcnow)
    updated_at = Column(DateTime, default=func.utcnow, onupdate=func.utcnow)
    is_active = Column(Boolean, default=True)
    
    # External IDs
    mls_id = Column(String(100), nullable=True, index=True)
    zillow_id = Column(String(100), nullable=True)
    redfin_id = Column(String(100), nullable=True)
    attom_id = Column(String(100), nullable=True)
    
    # Agent assignment
    assigned_agent_id = Column(String(36), nullable=True, index=True)
    
    def __repr__(self):
        return f"<Property(id='{self.id}', address='{self.address}', city='{self.city}', state='{self.state}')>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "county": self.county,
            "country": self.country,
            "property_type": self.property_type,
            "property_subtype": self.property_subtype,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "square_feet": self.square_feet,
            "lot_size": self.lot_size,
            "year_built": self.year_built,
            "list_price": self.list_price,
            "estimated_value": self.estimated_value,
            "last_sold_price": self.last_sold_price,
            "last_sold_date": self.last_sold_date.isoformat() if self.last_sold_date else None,
            "tax_assessment": self.tax_assessment,
            "property_tax": self.property_tax,
            "status": self.status,
            "listing_date": self.listing_date.isoformat() if self.listing_date else None,
            "days_on_market": self.days_on_market,
            "features": self.features,
            "description": self.description,
            "images": self.images,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "neighborhood": self.neighborhood,
            "school_district": self.school_district,
            "market_data": self.market_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "mls_id": self.mls_id,
            "zillow_id": self.zillow_id,
            "redfin_id": self.redfin_id,
            "attom_id": self.attom_id,
            "assigned_agent_id": self.assigned_agent_id
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create model instance from dictionary."""
        # Handle date fields
        if "last_sold_date" in data and data["last_sold_date"]:
            try:
                data["last_sold_date"] = datetime.fromisoformat(data["last_sold_date"])
            except (ValueError, TypeError):
                data["last_sold_date"] = None
        
        if "listing_date" in data and data["listing_date"]:
            try:
                data["listing_date"] = datetime.fromisoformat(data["listing_date"])
            except (ValueError, TypeError):
                data["listing_date"] = None
        
        return cls(**data)
