from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

Base = declarative_base()

class ComplianceStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"
    EXEMPT = "exempt"

class ComplianceType(str, Enum):
    OWNERSHIP = "ownership"
    ZONING = "zoning"
    PERMITS = "permits"
    LIENS = "liens"
    TAX_HISTORY = "tax_history"
    ENVIRONMENTAL = "environmental"
    TITLE = "title"
    INSURANCE = "insurance"
    HOA = "hoa"
    BUILDING_CODES = "building_codes"

class LegalCompliance(Base):
    __tablename__ = "legal_compliance"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Property Reference
    property_id = Column(Integer, ForeignKey("properties.id"))
    property = relationship("Property", back_populates="legal_compliance")
    
    # Compliance Details
    compliance_type = Column(String(50), nullable=False)
    status = Column(String(50), default=ComplianceStatus.PENDING)
    
    # Check Results
    is_compliant = Column(Boolean, default=False)
    compliance_score = Column(Float, default=0)  # 0-100
    risk_level = Column(String(20))  # low, medium, high, critical
    
    # Issues and Findings
    issues_found = Column(JSON)  # List of compliance issues
    violations = Column(JSON)  # List of violations
    warnings = Column(JSON)  # List of warnings
    recommendations = Column(JSON)  # List of recommendations
    
    # Legal Data
    legal_description = Column(Text)
    ownership_history = Column(JSON)  # Ownership chain
    title_issues = Column(JSON)  # Title problems
    easements = Column(JSON)  # Easements and restrictions
    encumbrances = Column(JSON)  # Liens, mortgages, etc.
    
    # Zoning Information
    current_zoning = Column(String(100))
    zoning_compliance = Column(Boolean)
    zoning_violations = Column(JSON)
    variance_required = Column(Boolean, default=False)
    variance_details = Column(JSON)
    
    # Permit Information
    required_permits = Column(JSON)  # List of required permits
    existing_permits = Column(JSON)  # List of existing permits
    permit_violations = Column(JSON)  # Permit violations
    permit_recommendations = Column(JSON)  # Permit recommendations
    
    # Tax Information
    tax_status = Column(String(50))  # current, delinquent, exempt
    tax_delinquency_amount = Column(Float, default=0)
    tax_history = Column(JSON)  # Tax payment history
    tax_exemptions = Column(JSON)  # Tax exemptions
    
    # Environmental Information
    environmental_issues = Column(JSON)  # Environmental concerns
    flood_zone = Column(String(50))
    environmental_restrictions = Column(JSON)
    remediation_required = Column(Boolean, default=False)
    
    # HOA Information
    hoa_exists = Column(Boolean, default=False)
    hoa_name = Column(String(255))
    hoa_fees = Column(Float, default=0)
    hoa_restrictions = Column(JSON)
    hoa_violations = Column(JSON)
    hoa_approval_required = Column(Boolean, default=False)
    
    # AI Analysis
    ai_analysis = Column(Text)
    ai_confidence_score = Column(Float, default=0)
    ai_recommendations = Column(JSON)
    legal_opinion = Column(Text)  # AI-generated legal opinion
    
    # Review Process
    requires_lawyer_review = Column(Boolean, default=False)
    lawyer_reviewed = Column(Boolean, default=False)
    lawyer_notes = Column(Text)
    lawyer_reviewed_by = Column(Integer, ForeignKey("users.id"))
    lawyer_reviewed_at = Column(DateTime)
    
    # Metadata
    checked_by = Column(Integer, ForeignKey("users.id"))
    checked_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Rule Definition
    rule_name = Column(String(255), nullable=False)
    description = Column(Text)
    compliance_type = Column(String(50), nullable=False)
    
    # Rule Logic
    rule_conditions = Column(JSON)  # Conditions for the rule
    rule_actions = Column(JSON)  # Actions to take when rule is triggered
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Jurisdiction
    jurisdiction = Column(String(100))  # City, county, state
    effective_date = Column(DateTime)
    expiration_date = Column(DateTime)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class LegalDocument(Base):
    __tablename__ = "legal_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Document Information
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False)
    document_url = Column(String(500))
    document_content = Column(Text)
    
    # Legal Classification
    legal_category = Column(String(50))  # deed, title, lien, permit, etc.
    jurisdiction = Column(String(100))
    effective_date = Column(DateTime)
    expiration_date = Column(DateTime)
    
    # Property Reference
    property_id = Column(Integer, ForeignKey("properties.id"))
    property = relationship("Property", back_populates="legal_documents")
    
    # Compliance Reference
    compliance_id = Column(Integer, ForeignKey("legal_compliance.id"))
    compliance = relationship("LegalCompliance", back_populates="legal_documents")
    
    # Metadata
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    verified = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey("users.id"))
    verified_at = Column(DateTime)

# Pydantic Models for API
class ComplianceCheckRequest(BaseModel):
    property_id: int
    compliance_types: List[ComplianceType]
    include_ai_analysis: bool = True
    require_lawyer_review: bool = False

class ComplianceResponse(BaseModel):
    id: int
    property_id: int
    compliance_type: str
    status: str
    is_compliant: bool
    compliance_score: float
    risk_level: Optional[str]
    issues_found: Optional[List[str]]
    violations: Optional[List[str]]
    warnings: Optional[List[str]]
    recommendations: Optional[List[str]]
    ai_analysis: Optional[str]
    ai_confidence_score: float
    requires_lawyer_review: bool
    checked_at: datetime

    class Config:
        from_attributes = True

class LegalDocumentResponse(BaseModel):
    id: int
    document_name: str
    document_type: str
    legal_category: str
    jurisdiction: str
    effective_date: Optional[datetime]
    expiration_date: Optional[datetime]
    verified: bool
    uploaded_at: datetime

    class Config:
        from_attributes = True

class ComplianceReport(BaseModel):
    property_id: int
    overall_compliance_score: float
    overall_risk_level: str
    compliance_summary: Dict[str, Any]
    critical_issues: List[str]
    recommendations: List[str]
    requires_lawyer_review: bool
    generated_at: datetime

# Add relationships to existing models
LegalCompliance.legal_documents = relationship("LegalDocument", back_populates="compliance")
