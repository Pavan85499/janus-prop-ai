from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

Base = declarative_base()

class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PropertyType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MIXED_USE = "mixed_use"
    LAND = "land"

class PropertyCondition(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    DISTRESSED = "distressed"

class InvestmentPotential(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_HIGH = "very_high"

class PropertyScan(Base):
    __tablename__ = "property_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default=ScanStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Scan Configuration
    search_criteria = Column(JSON)  # Store search filters as JSON
    max_properties = Column(Integer, default=10000)
    scan_radius_miles = Column(Float, default=50.0)
    
    # Results Summary
    total_scanned = Column(Integer, default=0)
    properties_found = Column(Integer, default=0)
    high_potential_count = Column(Integer, default=0)
    distressed_count = Column(Integer, default=0)
    undervalued_count = Column(Integer, default=0)
    
    # User who created the scan
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="property_scans")
    
    # Scanned properties
    scanned_properties = relationship("ScannedProperty", back_populates="scan", cascade="all, delete-orphan")

class ScannedProperty(Base):
    __tablename__ = "scanned_properties"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("property_scans.id"))
    
    # Property Basic Info
    address = Column(String(500), nullable=False)
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    county = Column(String(100))
    
    # Property Details
    property_type = Column(String(50))
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    square_feet = Column(Integer)
    lot_size = Column(Float)
    year_built = Column(Integer)
    condition = Column(String(50))
    
    # Financial Data
    list_price = Column(Float)
    estimated_value = Column(Float)
    price_per_sqft = Column(Float)
    last_sale_price = Column(Float)
    last_sale_date = Column(DateTime)
    tax_assessed_value = Column(Float)
    annual_taxes = Column(Float)
    
    # Investment Analysis
    investment_potential = Column(String(50))
    roi_estimate = Column(Float)
    cap_rate = Column(Float)
    cash_flow_estimate = Column(Float)
    appreciation_potential = Column(Float)
    
    # Market Data
    market_value_estimate = Column(Float)
    days_on_market = Column(Integer)
    price_reductions = Column(Integer)
    market_trend = Column(String(50))  # rising, stable, declining
    
    # Distress Indicators
    is_distressed = Column(Boolean, default=False)
    is_undervalued = Column(Boolean, default=False)
    is_foreclosure = Column(Boolean, default=False)
    is_short_sale = Column(Boolean, default=False)
    is_bank_owned = Column(Boolean, default=False)
    
    # AI Analysis
    ai_confidence_score = Column(Float)  # 0-1 confidence in analysis
    ai_analysis = Column(Text)  # Detailed AI analysis
    risk_factors = Column(JSON)  # List of identified risk factors
    opportunity_factors = Column(JSON)  # List of opportunity factors
    
    # Metadata
    data_source = Column(String(100))  # MLS, Zillow, etc.
    scanned_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scan = relationship("PropertyScan", back_populates="scanned_properties")

# Pydantic Models for API
class PropertyScanCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    search_criteria: Dict[str, Any] = Field(default_factory=dict)
    max_properties: int = Field(default=10000, ge=1, le=1000000)
    scan_radius_miles: float = Field(default=50.0, ge=0.1, le=500.0)

class PropertyScanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ScanStatus] = None

class PropertyScanResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: ScanStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    search_criteria: Dict[str, Any]
    max_properties: int
    scan_radius_miles: float
    total_scanned: int
    properties_found: int
    high_potential_count: int
    distressed_count: int
    undervalued_count: int
    user_id: int

    class Config:
        from_attributes = True

class ScannedPropertyResponse(BaseModel):
    id: int
    address: str
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    property_type: Optional[str]
    bedrooms: Optional[int]
    bathrooms: Optional[float]
    square_feet: Optional[int]
    list_price: Optional[float]
    estimated_value: Optional[float]
    price_per_sqft: Optional[float]
    investment_potential: Optional[str]
    roi_estimate: Optional[float]
    cap_rate: Optional[float]
    is_distressed: bool
    is_undervalued: bool
    is_foreclosure: bool
    ai_confidence_score: Optional[float]
    ai_analysis: Optional[str]
    scanned_at: datetime

    class Config:
        from_attributes = True

class ScanCriteria(BaseModel):
    # Location
    city: Optional[str] = None
    state: Optional[str] = None
    zip_codes: Optional[list[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_miles: Optional[float] = None
    
    # Property Filters
    property_types: Optional[list[PropertyType]] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_sqft: Optional[int] = None
    max_sqft: Optional[int] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_bathrooms: Optional[float] = None
    max_bathrooms: Optional[float] = None
    min_lot_size: Optional[float] = None
    max_lot_size: Optional[float] = None
    year_built_min: Optional[int] = None
    year_built_max: Optional[int] = None
    
    # Investment Criteria
    min_roi: Optional[float] = None
    max_roi: Optional[float] = None
    min_cap_rate: Optional[float] = None
    max_cap_rate: Optional[float] = None
    min_cash_flow: Optional[float] = None
    max_cash_flow: Optional[float] = None
    
    # Distress Indicators
    include_distressed: bool = True
    include_foreclosures: bool = True
    include_short_sales: bool = True
    include_bank_owned: bool = True
    min_days_on_market: Optional[int] = None
    max_days_on_market: Optional[int] = None
    max_price_reductions: Optional[int] = None
    
    # Market Conditions
    market_trends: Optional[list[str]] = None  # rising, stable, declining
    min_appreciation_potential: Optional[float] = None
    max_appreciation_potential: Optional[float] = None
    
    # AI Analysis
    min_ai_confidence: Optional[float] = None
    investment_potential_levels: Optional[list[InvestmentPotential]] = None

class ScanProgress(BaseModel):
    scan_id: int
    status: ScanStatus
    total_properties: int
    scanned_count: int
    found_count: int
    progress_percentage: float
    estimated_completion: Optional[datetime]
    current_location: Optional[str] = None
    errors: Optional[list[str]] = None
