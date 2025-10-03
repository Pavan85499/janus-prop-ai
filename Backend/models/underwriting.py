from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

Base = declarative_base()

class UnderwritingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    APPROVED = "approved"
    REJECTED = "rejected"

class AnalysisType(str, Enum):
    CASH_FLOW = "cash_flow"
    RENT_COMP = "rent_comp"
    RENOVATION = "renovation"
    CAP_RATE = "cap_rate"
    SENSITIVITY = "sensitivity"
    STRESS_TEST = "stress_test"
    MARKET_ANALYSIS = "market_analysis"
    RISK_ASSESSMENT = "risk_assessment"

class PropertyUnderwriting(Base):
    __tablename__ = "property_underwriting"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Property Reference
    property_id = Column(Integer, ForeignKey("properties.id"))
    property = relationship("Property", back_populates="underwriting")
    
    # Underwriting Details
    analysis_type = Column(String(50), nullable=False)
    status = Column(String(50), default=UnderwritingStatus.PENDING)
    
    # Financial Assumptions
    purchase_price = Column(Float, nullable=False)
    down_payment = Column(Float, nullable=False)
    loan_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    loan_term_years = Column(Integer, default=30)
    
    # Property Income
    gross_rental_income = Column(Float, default=0)
    other_income = Column(Float, default=0)
    vacancy_rate = Column(Float, default=5.0)  # Percentage
    effective_gross_income = Column(Float, default=0)
    
    # Operating Expenses
    property_taxes = Column(Float, default=0)
    insurance = Column(Float, default=0)
    property_management = Column(Float, default=0)
    maintenance = Column(Float, default=0)
    utilities = Column(Float, default=0)
    hoa_fees = Column(Float, default=0)
    other_expenses = Column(Float, default=0)
    total_operating_expenses = Column(Float, default=0)
    
    # Cash Flow Analysis
    net_operating_income = Column(Float, default=0)
    debt_service = Column(Float, default=0)
    cash_flow_before_taxes = Column(Float, default=0)
    cash_flow_after_taxes = Column(Float, default=0)
    
    # Key Metrics
    cap_rate = Column(Float, default=0)
    cash_on_cash_return = Column(Float, default=0)
    gross_rent_multiplier = Column(Float, default=0)
    debt_coverage_ratio = Column(Float, default=0)
    internal_rate_of_return = Column(Float, default=0)
    
    # Market Analysis
    market_value_estimate = Column(Float, default=0)
    price_per_sqft = Column(Float, default=0)
    rent_per_sqft = Column(Float, default=0)
    market_trend = Column(String(50))  # rising, stable, declining
    days_on_market = Column(Integer, default=0)
    
    # Risk Assessment
    risk_score = Column(Float, default=0)  # 0-100
    risk_factors = Column(JSON)  # List of risk factors
    mitigation_strategies = Column(JSON)  # List of mitigation strategies
    
    # Sensitivity Analysis
    sensitivity_scenarios = Column(JSON)  # Different market scenarios
    break_even_analysis = Column(JSON)  # Break-even points
    stress_test_results = Column(JSON)  # Stress test outcomes
    
    # AI Analysis
    ai_analysis = Column(Text)
    ai_recommendations = Column(JSON)
    ai_confidence_score = Column(Float, default=0)
    
    # Approval Process
    is_approved = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    approval_notes = Column(Text)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

class RentComps(Base):
    __tablename__ = "rent_comps"
    
    id = Column(Integer, primary_key=True, index=True)
    underwriting_id = Column(Integer, ForeignKey("property_underwriting.id"))
    underwriting = relationship("PropertyUnderwriting", back_populates="rent_comps")
    
    # Comp Property Details
    address = Column(String(500), nullable=False)
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    
    # Property Characteristics
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    square_feet = Column(Integer)
    property_type = Column(String(50))
    year_built = Column(Integer)
    
    # Rent Information
    rent_amount = Column(Float, nullable=False)
    rent_per_sqft = Column(Float)
    rent_date = Column(DateTime)
    rent_source = Column(String(100))  # MLS, Zillow, etc.
    
    # Distance and Similarity
    distance_miles = Column(Float)
    similarity_score = Column(Float)  # 0-1, how similar to subject property
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

class RenovationScenario(Base):
    __tablename__ = "renovation_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    underwriting_id = Column(Integer, ForeignKey("property_underwriting.id"))
    underwriting = relationship("PropertyUnderwriting", back_populates="renovation_scenarios")
    
    # Scenario Details
    scenario_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Renovation Costs
    kitchen_renovation = Column(Float, default=0)
    bathroom_renovation = Column(Float, default=0)
    flooring = Column(Float, default=0)
    painting = Column(Float, default=0)
    hvac = Column(Float, default=0)
    electrical = Column(Float, default=0)
    plumbing = Column(Float, default=0)
    roofing = Column(Float, default=0)
    landscaping = Column(Float, default=0)
    other_costs = Column(Float, default=0)
    total_renovation_cost = Column(Float, default=0)
    
    # Expected Outcomes
    expected_rent_increase = Column(Float, default=0)
    expected_value_increase = Column(Float, default=0)
    renovation_timeline_days = Column(Integer, default=0)
    
    # ROI Analysis
    renovation_roi = Column(Float, default=0)
    payback_period_months = Column(Float, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models for API
class UnderwritingRequest(BaseModel):
    property_id: int
    analysis_type: AnalysisType
    purchase_price: float
    down_payment: float
    interest_rate: float
    loan_term_years: int = 30
    gross_rental_income: Optional[float] = None
    vacancy_rate: float = 5.0
    property_taxes: Optional[float] = None
    insurance: Optional[float] = None
    property_management_rate: float = 8.0  # Percentage
    maintenance_rate: float = 10.0  # Percentage
    hoa_fees: Optional[float] = None

class UnderwritingResponse(BaseModel):
    id: int
    property_id: int
    analysis_type: str
    status: str
    purchase_price: float
    down_payment: float
    loan_amount: float
    interest_rate: float
    net_operating_income: float
    cash_flow_before_taxes: float
    cap_rate: float
    cash_on_cash_return: float
    debt_coverage_ratio: float
    risk_score: float
    is_approved: bool
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class CashFlowAnalysis(BaseModel):
    gross_rental_income: float
    vacancy_allowance: float
    effective_gross_income: float
    operating_expenses: Dict[str, float]
    net_operating_income: float
    debt_service: float
    cash_flow_before_taxes: float
    cash_flow_after_taxes: float

class SensitivityAnalysis(BaseModel):
    base_case: Dict[str, float]
    optimistic_case: Dict[str, float]
    pessimistic_case: Dict[str, float]
    break_even_rent: float
    break_even_occupancy: float

class RentCompResponse(BaseModel):
    id: int
    address: str
    city: str
    state: str
    bedrooms: int
    bathrooms: float
    square_feet: int
    rent_amount: float
    rent_per_sqft: float
    distance_miles: float
    similarity_score: float
    rent_date: datetime

    class Config:
        from_attributes = True

class RenovationScenarioResponse(BaseModel):
    id: int
    scenario_name: str
    description: str
    total_renovation_cost: float
    expected_rent_increase: float
    expected_value_increase: float
    renovation_roi: float
    payback_period_months: float
    renovation_timeline_days: int

    class Config:
        from_attributes = True

# Add relationships to existing models
PropertyUnderwriting.rent_comps = relationship("RentComps", back_populates="underwriting")
PropertyUnderwriting.renovation_scenarios = relationship("RenovationScenario", back_populates="underwriting")
