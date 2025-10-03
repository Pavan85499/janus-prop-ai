from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

Base = declarative_base()

class AssetStatus(str, Enum):
    ACTIVE = "active"
    UNDER_RENOVATION = "under_renovation"
    VACANT = "vacant"
    LEASED = "leased"
    FOR_SALE = "for_sale"
    SOLD = "sold"

class RenovationStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

class RefinancingStatus(str, Enum):
    ELIGIBLE = "eligible"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NOT_ELIGIBLE = "not_eligible"

class PostAcquisitionAsset(Base):
    __tablename__ = "post_acquisition_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Property Reference
    property_id = Column(Integer, ForeignKey("properties.id"))
    property = relationship("Property", back_populates="post_acquisition_assets")
    
    # Deal Reference
    deal_id = Column(Integer, ForeignKey("deal_executions.id"))
    deal = relationship("DealExecution", back_populates="post_acquisition_assets")
    
    # Asset Details
    asset_name = Column(String(255), nullable=False)
    status = Column(String(50), default=AssetStatus.ACTIVE)
    acquisition_date = Column(DateTime, nullable=False)
    acquisition_price = Column(Float, nullable=False)
    current_value = Column(Float, default=0)
    total_investment = Column(Float, default=0)
    
    # Financial Performance
    monthly_rent = Column(Float, default=0)
    monthly_expenses = Column(Float, default=0)
    monthly_cash_flow = Column(Float, default=0)
    annual_cash_flow = Column(Float, default=0)
    cap_rate = Column(Float, default=0)
    cash_on_cash_return = Column(Float, default=0)
    total_return = Column(Float, default=0)
    
    # Market Performance
    market_value_appreciation = Column(Float, default=0)
    rent_growth_rate = Column(Float, default=0)
    occupancy_rate = Column(Float, default=0)
    days_vacant = Column(Integer, default=0)
    
    # AI Analysis
    ai_analysis = Column(Text)
    performance_score = Column(Float, default=0)  # 0-100
    risk_score = Column(Float, default=0)  # 0-100
    opportunity_score = Column(Float, default=0)  # 0-100
    ai_recommendations = Column(JSON)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class RenovationProject(Base):
    __tablename__ = "renovation_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("post_acquisition_assets.id"))
    asset = relationship("PostAcquisitionAsset", back_populates="renovation_projects")
    
    # Project Details
    project_name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default=RenovationStatus.PLANNED)
    
    # Budget and Timeline
    estimated_cost = Column(Float, nullable=False)
    actual_cost = Column(Float, default=0)
    budget_variance = Column(Float, default=0)
    estimated_duration_days = Column(Integer, default=0)
    actual_duration_days = Column(Integer, default=0)
    start_date = Column(DateTime)
    completion_date = Column(DateTime)
    
    # Scope of Work
    scope_of_work = Column(JSON)  # Detailed scope
    materials_required = Column(JSON)  # Materials list
    contractors = Column(JSON)  # Contractor information
    
    # Expected Outcomes
    expected_rent_increase = Column(Float, default=0)
    expected_value_increase = Column(Float, default=0)
    expected_roi = Column(Float, default=0)
    
    # Actual Outcomes
    actual_rent_increase = Column(Float, default=0)
    actual_value_increase = Column(Float, default=0)
    actual_roi = Column(Float, default=0)
    
    # AI Analysis
    ai_analysis = Column(Text)
    ai_recommendations = Column(JSON)
    risk_factors = Column(JSON)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class TenantDemand(Base):
    __tablename__ = "tenant_demand"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("post_acquisition_assets.id"))
    asset = relationship("PostAcquisitionAsset", back_populates="tenant_demand")
    
    # Demand Metrics
    inquiry_count = Column(Integer, default=0)
    application_count = Column(Integer, default=0)
    lease_signed_count = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0)
    
    # Market Data
    average_days_on_market = Column(Float, default=0)
    rent_comparison = Column(JSON)  # Rent vs market
    demand_trend = Column(String(50))  # increasing, stable, decreasing
    
    # Tenant Profile
    average_tenant_age = Column(Float, default=0)
    average_tenant_income = Column(Float, default=0)
    tenant_retention_rate = Column(Float, default=0)
    average_lease_length = Column(Float, default=0)
    
    # AI Analysis
    ai_analysis = Column(Text)
    demand_forecast = Column(JSON)
    pricing_recommendations = Column(JSON)
    marketing_recommendations = Column(JSON)
    
    # Metadata
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class RefinancingOpportunity(Base):
    __tablename__ = "refinancing_opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("post_acquisition_assets.id"))
    asset = relationship("PostAcquisitionAsset", back_populates="refinancing_opportunities")
    
    # Opportunity Details
    opportunity_name = Column(String(255), nullable=False)
    status = Column(String(50), default=RefinancingStatus.ELIGIBLE)
    
    # Current Loan
    current_loan_balance = Column(Float, nullable=False)
    current_interest_rate = Column(Float, nullable=False)
    current_monthly_payment = Column(Float, nullable=False)
    current_loan_term_remaining = Column(Integer, default=0)
    
    # Refinancing Terms
    new_loan_amount = Column(Float, default=0)
    new_interest_rate = Column(Float, default=0)
    new_monthly_payment = Column(Float, default=0)
    new_loan_term = Column(Integer, default=30)
    closing_costs = Column(Float, default=0)
    
    # Financial Impact
    monthly_savings = Column(Float, default=0)
    annual_savings = Column(Float, default=0)
    cash_out_amount = Column(Float, default=0)
    break_even_months = Column(Float, default=0)
    net_present_value = Column(Float, default=0)
    
    # Lender Information
    lender_name = Column(String(255))
    lender_contact = Column(String(255))
    application_date = Column(DateTime)
    approval_date = Column(DateTime)
    
    # AI Analysis
    ai_analysis = Column(Text)
    opportunity_score = Column(Float, default=0)  # 0-100
    risk_assessment = Column(JSON)
    ai_recommendations = Column(JSON)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class AssetMonitoring(Base):
    __tablename__ = "asset_monitoring"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("post_acquisition_assets.id"))
    asset = relationship("PostAcquisitionAsset", back_populates="asset_monitoring")
    
    # Monitoring Metrics
    monitoring_date = Column(DateTime, nullable=False)
    property_condition_score = Column(Float, default=0)  # 0-100
    market_performance_score = Column(Float, default=0)  # 0-100
    financial_performance_score = Column(Float, default=0)  # 0-100
    overall_score = Column(Float, default=0)  # 0-100
    
    # Key Performance Indicators
    occupancy_rate = Column(Float, default=0)
    rent_rollover_rate = Column(Float, default=0)
    maintenance_costs = Column(Float, default=0)
    property_taxes = Column(Float, default=0)
    insurance_costs = Column(Float, default=0)
    
    # Market Indicators
    market_rent_trend = Column(String(50))  # rising, stable, falling
    comparable_sales = Column(JSON)
    market_competition = Column(JSON)
    
    # Alerts and Issues
    alerts = Column(JSON)  # List of alerts
    issues_identified = Column(JSON)  # List of issues
    recommendations = Column(JSON)  # List of recommendations
    
    # AI Analysis
    ai_analysis = Column(Text)
    ai_insights = Column(JSON)
    predictive_analytics = Column(JSON)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models for API
class PostAcquisitionAssetRequest(BaseModel):
    property_id: int
    deal_id: int
    asset_name: str
    acquisition_date: datetime
    acquisition_price: float
    monthly_rent: float = 0
    monthly_expenses: float = 0

class PostAcquisitionAssetResponse(BaseModel):
    id: int
    property_id: int
    deal_id: int
    asset_name: str
    status: str
    acquisition_date: datetime
    acquisition_price: float
    current_value: float
    total_investment: float
    monthly_cash_flow: float
    annual_cash_flow: float
    cap_rate: float
    cash_on_cash_return: float
    performance_score: float
    risk_score: float
    opportunity_score: float
    created_at: datetime

    class Config:
        from_attributes = True

class RenovationProjectRequest(BaseModel):
    asset_id: int
    project_name: str
    description: str
    estimated_cost: float
    estimated_duration_days: int
    scope_of_work: List[str]
    expected_rent_increase: float = 0
    expected_value_increase: float = 0

class RenovationProjectResponse(BaseModel):
    id: int
    asset_id: int
    project_name: str
    description: str
    status: str
    estimated_cost: float
    actual_cost: float
    budget_variance: float
    estimated_duration_days: int
    actual_duration_days: int
    start_date: Optional[datetime]
    completion_date: Optional[datetime]
    expected_roi: float
    actual_roi: float
    created_at: datetime

    class Config:
        from_attributes = True

class RefinancingOpportunityResponse(BaseModel):
    id: int
    asset_id: int
    opportunity_name: str
    status: str
    current_loan_balance: float
    current_interest_rate: float
    new_interest_rate: float
    monthly_savings: float
    annual_savings: float
    break_even_months: float
    opportunity_score: float
    created_at: datetime

    class Config:
        from_attributes = True

class AssetMonitoringResponse(BaseModel):
    id: int
    asset_id: int
    monitoring_date: datetime
    property_condition_score: float
    market_performance_score: float
    financial_performance_score: float
    overall_score: float
    occupancy_rate: float
    market_rent_trend: str
    alerts: Optional[List[str]]
    issues_identified: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True

# Add relationships to existing models
PostAcquisitionAsset.renovation_projects = relationship("RenovationProject", back_populates="asset")
PostAcquisitionAsset.tenant_demand = relationship("TenantDemand", back_populates="asset")
PostAcquisitionAsset.refinancing_opportunities = relationship("RefinancingOpportunity", back_populates="asset")
PostAcquisitionAsset.asset_monitoring = relationship("AssetMonitoring", back_populates="asset")
