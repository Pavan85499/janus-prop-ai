from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

Base = declarative_base()

class DealStatus(str, Enum):
    DRAFT = "draft"
    OFFER_SUBMITTED = "offer_submitted"
    UNDER_REVIEW = "under_review"
    NEGOTIATING = "negotiating"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    UNDER_CONTRACT = "under_contract"
    INSPECTION = "inspection"
    APPRAISAL = "appraisal"
    FINANCING = "financing"
    CLOSING = "closing"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class OfferType(str, Enum):
    CASH = "cash"
    FINANCED = "financed"
    CONTINGENT = "contingent"
    AS_IS = "as_is"

class ContactMethod(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    TEXT = "text"
    MAIL = "mail"
    IN_PERSON = "in_person"

class DealExecution(Base):
    __tablename__ = "deal_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Property Reference
    property_id = Column(Integer, ForeignKey("properties.id"))
    property = relationship("Property", back_populates="deal_executions")
    
    # Deal Details
    deal_name = Column(String(255), nullable=False)
    status = Column(String(50), default=DealStatus.DRAFT)
    offer_type = Column(String(50), default=OfferType.FINANCED)
    
    # Financial Terms
    offer_price = Column(Float, nullable=False)
    earnest_money = Column(Float, default=0)
    down_payment = Column(Float, default=0)
    loan_amount = Column(Float, default=0)
    interest_rate = Column(Float, default=0)
    loan_term = Column(Integer, default=30)
    
    # Offer Terms
    closing_date = Column(DateTime)
    inspection_period_days = Column(Integer, default=10)
    financing_contingency_days = Column(Integer, default=21)
    appraisal_contingency_days = Column(Integer, default=14)
    
    # Contingencies
    contingencies = Column(JSON)  # List of contingencies
    special_terms = Column(Text)
    seller_concessions = Column(JSON)  # Requested concessions
    
    # Contact Information
    seller_name = Column(String(255))
    seller_email = Column(String(255))
    seller_phone = Column(String(50))
    seller_address = Column(Text)
    agent_name = Column(String(255))
    agent_email = Column(String(255))
    agent_phone = Column(String(50))
    
    # Timeline
    offer_submitted_at = Column(DateTime)
    response_received_at = Column(DateTime)
    contract_signed_at = Column(DateTime)
    inspection_scheduled_at = Column(DateTime)
    inspection_completed_at = Column(DateTime)
    appraisal_ordered_at = Column(DateTime)
    appraisal_completed_at = Column(DateTime)
    financing_approved_at = Column(DateTime)
    closing_scheduled_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Documents
    offer_letter_url = Column(String(500))
    contract_url = Column(String(500))
    inspection_report_url = Column(String(500))
    appraisal_report_url = Column(String(500))
    closing_documents_url = Column(String(500))
    
    # AI Analysis
    ai_analysis = Column(Text)
    ai_recommendations = Column(JSON)
    risk_assessment = Column(JSON)
    success_probability = Column(Float, default=0)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class OwnerContact(Base):
    __tablename__ = "owner_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deal_executions.id"))
    deal = relationship("DealExecution", back_populates="owner_contacts")
    
    # Contact Details
    contact_method = Column(String(50), nullable=False)
    contact_date = Column(DateTime, nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Response
    response_received = Column(Boolean, default=False)
    response_date = Column(DateTime)
    response_content = Column(Text)
    response_sentiment = Column(String(50))  # positive, negative, neutral
    
    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    follow_up_notes = Column(Text)
    
    # AI Analysis
    ai_analysis = Column(Text)
    ai_sentiment_score = Column(Float, default=0)
    ai_recommendations = Column(JSON)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class OfferLetter(Base):
    __tablename__ = "offer_letters"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deal_executions.id"))
    deal = relationship("DealExecution", back_populates="offer_letters")
    
    # Letter Details
    letter_title = Column(String(255), nullable=False)
    letter_content = Column(Text, nullable=False)
    letter_type = Column(String(50), default="initial_offer")  # initial_offer, counter_offer, final_offer
    
    # Terms
    offer_price = Column(Float, nullable=False)
    earnest_money = Column(Float, default=0)
    closing_date = Column(DateTime)
    contingencies = Column(JSON)
    special_terms = Column(Text)
    
    # Status
    status = Column(String(50), default="draft")  # draft, sent, responded, accepted, rejected
    sent_at = Column(DateTime)
    response_received_at = Column(DateTime)
    response_content = Column(Text)
    
    # AI Generation
    ai_generated = Column(Boolean, default=True)
    generation_prompt = Column(Text)
    generation_parameters = Column(JSON)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deal_executions.id"))
    deal = relationship("DealExecution", back_populates="contracts")
    
    # Contract Details
    contract_title = Column(String(255), nullable=False)
    contract_type = Column(String(50), default="purchase_agreement")
    contract_content = Column(Text, nullable=False)
    
    # Parties
    buyer_name = Column(String(255))
    buyer_email = Column(String(255))
    seller_name = Column(String(255))
    seller_email = Column(String(255))
    
    # Terms
    purchase_price = Column(Float, nullable=False)
    earnest_money = Column(Float, default=0)
    closing_date = Column(DateTime)
    contingencies = Column(JSON)
    special_provisions = Column(Text)
    
    # Status
    status = Column(String(50), default="draft")  # draft, sent, signed, executed
    buyer_signed_at = Column(DateTime)
    seller_signed_at = Column(DateTime)
    executed_at = Column(DateTime)
    
    # Legal Review
    legal_reviewed = Column(Boolean, default=False)
    legal_reviewed_by = Column(Integer, ForeignKey("users.id"))
    legal_reviewed_at = Column(DateTime)
    legal_notes = Column(Text)
    
    # AI Generation
    ai_generated = Column(Boolean, default=True)
    generation_prompt = Column(Text)
    generation_parameters = Column(JSON)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Lender(Base):
    __tablename__ = "lenders"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Lender Details
    lender_name = Column(String(255), nullable=False)
    lender_type = Column(String(50))  # bank, credit_union, private, hard_money
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    website = Column(String(500))
    
    # Loan Products
    loan_products = Column(JSON)  # Available loan products
    interest_rates = Column(JSON)  # Current interest rates
    loan_terms = Column(JSON)  # Available loan terms
    minimum_down_payment = Column(Float, default=20)
    maximum_loan_amount = Column(Float, default=1000000)
    
    # Requirements
    credit_score_minimum = Column(Integer, default=620)
    debt_to_income_maximum = Column(Float, default=43)
    documentation_required = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_preferred = Column(Boolean, default=False)
    rating = Column(Float, default=0)  # 0-5 star rating
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class FinancingApplication(Base):
    __tablename__ = "financing_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deal_executions.id"))
    deal = relationship("DealExecution", back_populates="financing_applications")
    lender_id = Column(Integer, ForeignKey("lenders.id"))
    lender = relationship("Lender")
    
    # Application Details
    application_number = Column(String(100), unique=True)
    loan_amount = Column(Float, nullable=False)
    down_payment = Column(Float, nullable=False)
    interest_rate = Column(Float, default=0)
    loan_term = Column(Integer, default=30)
    
    # Borrower Information
    borrower_name = Column(String(255), nullable=False)
    borrower_email = Column(String(255))
    borrower_phone = Column(String(50))
    credit_score = Column(Integer)
    annual_income = Column(Float)
    debt_to_income_ratio = Column(Float)
    
    # Property Information
    property_address = Column(String(500))
    property_value = Column(Float)
    property_type = Column(String(50))
    
    # Application Status
    status = Column(String(50), default="submitted")  # submitted, under_review, approved, rejected, withdrawn
    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)
    approved_at = Column(DateTime)
    rejected_at = Column(DateTime)
    
    # Documents
    required_documents = Column(JSON)
    submitted_documents = Column(JSON)
    missing_documents = Column(JSON)
    
    # AI Analysis
    ai_analysis = Column(Text)
    approval_probability = Column(Float, default=0)
    ai_recommendations = Column(JSON)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models for API
class DealExecutionRequest(BaseModel):
    property_id: int
    deal_name: str
    offer_type: OfferType
    offer_price: float
    earnest_money: float = 0
    down_payment: float = 0
    loan_amount: float = 0
    interest_rate: float = 0
    loan_term: int = 30
    closing_date: Optional[datetime] = None
    inspection_period_days: int = 10
    financing_contingency_days: int = 21
    contingencies: Optional[List[str]] = None
    special_terms: Optional[str] = None

class DealExecutionResponse(BaseModel):
    id: int
    property_id: int
    deal_name: str
    status: str
    offer_type: str
    offer_price: float
    earnest_money: float
    down_payment: float
    loan_amount: float
    closing_date: Optional[datetime]
    success_probability: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OwnerContactRequest(BaseModel):
    deal_id: int
    contact_method: ContactMethod
    subject: str
    message: str
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None

class OfferLetterResponse(BaseModel):
    id: int
    deal_id: int
    letter_title: str
    letter_content: str
    letter_type: str
    offer_price: float
    status: str
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class ContractResponse(BaseModel):
    id: int
    deal_id: int
    contract_title: str
    contract_type: str
    purchase_price: float
    status: str
    buyer_signed_at: Optional[datetime]
    seller_signed_at: Optional[datetime]
    executed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class FinancingApplicationRequest(BaseModel):
    deal_id: int
    lender_id: int
    loan_amount: float
    down_payment: float
    interest_rate: float = 0
    loan_term: int = 30
    borrower_name: str
    borrower_email: str
    borrower_phone: str
    credit_score: int
    annual_income: float

# Add relationships to existing models
DealExecution.owner_contacts = relationship("OwnerContact", back_populates="deal")
DealExecution.offer_letters = relationship("OfferLetter", back_populates="deal")
DealExecution.contracts = relationship("Contract", back_populates="deal")
DealExecution.financing_applications = relationship("FinancingApplication", back_populates="deal")
