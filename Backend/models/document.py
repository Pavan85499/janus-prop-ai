from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

Base = declarative_base()

class DocumentType(str, Enum):
    DEED = "deed"
    LEASE = "lease"
    INSPECTION = "inspection"
    FINANCIAL = "financial"
    TAX_RECORD = "tax_record"
    ZONING = "zoning"
    PERMIT = "permit"
    LIEN = "lien"
    APPRAISAL = "appraisal"
    INSURANCE = "insurance"
    CONTRACT = "contract"
    OFFER_LETTER = "offer_letter"
    OTHER = "other"

class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PARSED = "parsed"
    FAILED = "failed"
    VERIFIED = "verified"

class DocumentProcessingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_extension = Column(String(10), nullable=False)
    
    # Document Classification
    document_type = Column(String(50), nullable=False)
    document_subtype = Column(String(100))
    confidence_score = Column(Float, default=0.0)
    
    # Processing Status
    status = Column(String(50), default=DocumentStatus.UPLOADED)
    processing_status = Column(String(50), default=DocumentProcessingStatus.PENDING)
    processing_error = Column(Text)
    
    # Metadata
    title = Column(String(255))
    description = Column(Text)
    tags = Column(JSON)  # Array of tags
    properties = Column(JSON)  # Extracted properties
    
    # Relationships
    property_id = Column(Integer, ForeignKey("properties.id"))
    property = relationship("Property", back_populates="documents")
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="documents")
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    verified_at = Column(DateTime)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    
    # Parsed Content
    parsed_content = Column(Text)  # Extracted text content
    structured_data = Column(JSON)  # Structured data extracted from document
    key_entities = Column(JSON)  # Named entities extracted
    financial_data = Column(JSON)  # Financial information extracted
    legal_data = Column(JSON)  # Legal information extracted
    
    # AI Analysis
    ai_analysis = Column(Text)  # AI-generated analysis
    risk_factors = Column(JSON)  # Identified risk factors
    compliance_issues = Column(JSON)  # Compliance issues found
    recommendations = Column(JSON)  # AI recommendations
    
    # Version Control
    version = Column(Integer, default=1)
    parent_document_id = Column(Integer, ForeignKey("documents.id"))
    parent_document = relationship("Document", remote_side=[id])
    child_documents = relationship("Document", backref="parent_document")
    
    # Access Control
    is_public = Column(Boolean, default=False)
    access_level = Column(String(50), default="private")  # private, team, public
    encryption_key = Column(String(255))  # For encrypted documents

class DocumentTemplate(Base):
    __tablename__ = "document_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    document_type = Column(String(50), nullable=False)
    
    # Template Configuration
    template_config = Column(JSON)  # Template-specific configuration
    required_fields = Column(JSON)  # Required fields for this template
    optional_fields = Column(JSON)  # Optional fields for this template
    validation_rules = Column(JSON)  # Validation rules
    
    # AI Processing Rules
    extraction_rules = Column(JSON)  # Rules for data extraction
    analysis_rules = Column(JSON)  # Rules for AI analysis
    compliance_rules = Column(JSON)  # Compliance checking rules
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class DocumentProcessingJob(Base):
    __tablename__ = "document_processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    document = relationship("Document")
    
    # Job Configuration
    job_type = Column(String(50), nullable=False)  # parse, analyze, extract, validate
    priority = Column(Integer, default=5)  # 1-10, 1 being highest priority
    
    # Processing Details
    status = Column(String(50), default=DocumentProcessingStatus.PENDING)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    
    # Processing Results
    processing_results = Column(JSON)
    extracted_data = Column(JSON)
    analysis_results = Column(JSON)
    
    # Retry Logic
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime)

# Pydantic Models for API
class DocumentUpload(BaseModel):
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    document_type: DocumentType
    property_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    is_public: bool = False
    access_level: str = "private"

class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    document_type: str
    status: str
    processing_status: str
    title: Optional[str]
    description: Optional[str]
    tags: Optional[list[str]]
    file_size: int
    mime_type: str
    uploaded_at: datetime
    processed_at: Optional[datetime]
    confidence_score: Optional[float]
    property_id: Optional[int]
    user_id: int

    class Config:
        from_attributes = True

class DocumentAnalysis(BaseModel):
    document_id: int
    ai_analysis: str
    key_entities: list[str]
    financial_data: Dict[str, Any]
    legal_data: Dict[str, Any]
    risk_factors: list[str]
    compliance_issues: list[str]
    recommendations: list[str]
    confidence_score: float

class DocumentSearchCriteria(BaseModel):
    document_type: Optional[DocumentType] = None
    property_id: Optional[int] = None
    status: Optional[DocumentStatus] = None
    tags: Optional[list[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search_text: Optional[str] = None
    has_financial_data: Optional[bool] = None
    has_legal_data: Optional[bool] = None
    confidence_min: Optional[float] = None
    confidence_max: Optional[float] = None

class DocumentProcessingRequest(BaseModel):
    document_id: int
    job_type: str
    priority: int = 5
    force_reprocess: bool = False
    processing_options: Optional[Dict[str, Any]] = None
