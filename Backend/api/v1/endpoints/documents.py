from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import uuid
import mimetypes
import asyncio
import json

from core.database import get_db
from models.document import (
    Document, DocumentTemplate, DocumentProcessingJob,
    DocumentUpload, DocumentResponse, DocumentAnalysis,
    DocumentSearchCriteria, DocumentProcessingRequest,
    DocumentType, DocumentStatus, DocumentProcessingStatus
)
from models.user import User
from core.redis_client import publish_event

router = APIRouter()

# Mock AI document processing - in production, this would use real AI services
async def process_document_ai(document_id: int, file_path: str, document_type: str) -> dict:
    """AI-powered document processing and analysis"""
    # Simulate AI processing time
    await asyncio.sleep(2)
    
    # Mock AI analysis based on document type
    analysis_results = {
        "parsed_content": f"Extracted text content from {file_path}",
        "structured_data": {
            "parties": ["John Doe", "Jane Smith"],
            "amounts": [250000, 50000],
            "dates": ["2024-01-15", "2024-02-01"],
            "addresses": ["123 Main St, San Francisco, CA 94102"]
        },
        "key_entities": ["John Doe", "Jane Smith", "123 Main St", "San Francisco"],
        "financial_data": {
            "purchase_price": 250000,
            "down_payment": 50000,
            "loan_amount": 200000,
            "interest_rate": 6.5,
            "monthly_payment": 1264
        },
        "legal_data": {
            "property_type": "Single Family",
            "zoning": "R1",
            "legal_description": "Lot 1, Block 2, Subdivision ABC",
            "restrictions": ["No commercial use", "HOA required"]
        },
        "ai_analysis": f"Document analysis complete. Identified as {document_type} with high confidence.",
        "risk_factors": ["High loan-to-value ratio", "Property in flood zone"],
        "compliance_issues": ["Missing HOA documentation", "Zoning variance required"],
        "recommendations": [
            "Verify property insurance coverage",
            "Review HOA bylaws",
            "Conduct additional inspections"
        ],
        "confidence_score": 0.92
    }
    
    return analysis_results

async def process_document_task(document_id: int, file_path: str, document_type: str, db: Session):
    """Background task to process document with AI"""
    try:
        # Update document status
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return
        
        document.status = DocumentStatus.PROCESSING
        document.processing_status = DocumentProcessingStatus.IN_PROGRESS
        db.commit()
        
        # Publish processing started event
        await publish_event("documents", "processing_started", {
            "document_id": document_id,
            "status": "processing"
        })
        
        # Process document with AI
        analysis_results = await process_document_ai(document_id, file_path, document_type)
        
        # Update document with results
        document.status = DocumentStatus.PARSED
        document.processing_status = DocumentProcessingStatus.COMPLETED
        document.processed_at = datetime.utcnow()
        document.parsed_content = analysis_results["parsed_content"]
        document.structured_data = analysis_results["structured_data"]
        document.key_entities = analysis_results["key_entities"]
        document.financial_data = analysis_results["financial_data"]
        document.legal_data = analysis_results["legal_data"]
        document.ai_analysis = analysis_results["ai_analysis"]
        document.risk_factors = analysis_results["risk_factors"]
        document.compliance_issues = analysis_results["compliance_issues"]
        document.recommendations = analysis_results["recommendations"]
        document.confidence_score = analysis_results["confidence_score"]
        
        db.commit()
        
        # Publish processing completed event
        await publish_event("documents", "processing_completed", {
            "document_id": document_id,
            "status": "parsed",
            "confidence_score": analysis_results["confidence_score"]
        })
        
    except Exception as e:
        # Update document status to failed
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = DocumentStatus.FAILED
            document.processing_status = DocumentProcessingStatus.ERROR
            document.processing_error = str(e)
            db.commit()
        
        await publish_event("documents", "processing_failed", {
            "document_id": document_id,
            "status": "failed",
            "error": str(e)
        })

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: DocumentType = DocumentType.OTHER,
    property_id: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[str] = None,
    is_public: bool = False,
    access_level: str = "private",
    db: Session = Depends(get_db)
):
    """Upload and process a document"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Get file info
    file_size = 0
    file_content = b""
    try:
        file_content = await file.read()
        file_size = len(file_content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    # Validate file size (10MB limit)
    if file_size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create upload directory if it doesn't exist
    upload_dir = "uploads/documents"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Get MIME type
    mime_type, _ = mimetypes.guess_type(file.filename)
    if not mime_type:
        mime_type = "application/octet-stream"
    
    # Parse tags
    tag_list = []
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    
    # Create document record
    document = Document(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=mime_type,
        file_extension=file_extension,
        document_type=document_type.value,
        title=title or file.filename,
        description=description,
        tags=tag_list,
        property_id=property_id,
        user_id=1,  # In production, get from authenticated user
        is_public=is_public,
        access_level=access_level
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Start background processing
    background_tasks.add_task(
        process_document_task,
        document.id,
        file_path,
        document_type.value,
        db
    )
    
    return document

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    document_type: Optional[DocumentType] = None,
    property_id: Optional[int] = None,
    status: Optional[DocumentStatus] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get documents with filtering options"""
    query = db.query(Document)
    
    if document_type:
        query = query.filter(Document.document_type == document_type.value)
    
    if property_id:
        query = query.filter(Document.property_id == property_id)
    
    if status:
        query = query.filter(Document.status == status.value)
    
    if search:
        query = query.filter(
            (Document.title.contains(search)) |
            (Document.description.contains(search)) |
            (Document.parsed_content.contains(search))
        )
    
    documents = query.offset(skip).limit(limit).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a specific document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.get("/{document_id}/analysis", response_model=DocumentAnalysis)
async def get_document_analysis(document_id: int, db: Session = Depends(get_db)):
    """Get AI analysis for a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != DocumentStatus.PARSED:
        raise HTTPException(status_code=400, detail="Document not yet processed")
    
    return DocumentAnalysis(
        document_id=document.id,
        ai_analysis=document.ai_analysis or "",
        key_entities=document.key_entities or [],
        financial_data=document.financial_data or {},
        legal_data=document.legal_data or {},
        risk_factors=document.risk_factors or [],
        compliance_issues=document.compliance_issues or [],
        recommendations=document.recommendations or [],
        confidence_score=document.confidence_score or 0.0
    )

@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Reprocess a document with AI"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Reset processing status
    document.status = DocumentStatus.UPLOADED
    document.processing_status = DocumentProcessingStatus.PENDING
    document.processing_error = None
    db.commit()
    
    # Start reprocessing
    background_tasks.add_task(
        process_document_task,
        document.id,
        document.file_path,
        document.document_type,
        db
    )
    
    return {"message": "Document reprocessing started"}

@router.delete("/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from filesystem
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        # Log error but don't fail the request
        print(f"Error deleting file: {e}")
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}

@router.get("/{document_id}/download")
async def download_document(document_id: int, db: Session = Depends(get_db)):
    """Download a document file"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # Update last accessed time
    document.last_accessed = datetime.utcnow()
    db.commit()
    
    from fastapi.responses import FileResponse
    return FileResponse(
        path=document.file_path,
        filename=document.original_filename,
        media_type=document.mime_type
    )

@router.post("/search")
async def search_documents(
    criteria: DocumentSearchCriteria,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Advanced document search with multiple criteria"""
    query = db.query(Document)
    
    if criteria.document_type:
        query = query.filter(Document.document_type == criteria.document_type.value)
    
    if criteria.property_id:
        query = query.filter(Document.property_id == criteria.property_id)
    
    if criteria.status:
        query = query.filter(Document.status == criteria.status.value)
    
    if criteria.tags:
        for tag in criteria.tags:
            query = query.filter(Document.tags.contains([tag]))
    
    if criteria.date_from:
        query = query.filter(Document.uploaded_at >= criteria.date_from)
    
    if criteria.date_to:
        query = query.filter(Document.uploaded_at <= criteria.date_to)
    
    if criteria.search_text:
        query = query.filter(
            (Document.title.contains(criteria.search_text)) |
            (Document.description.contains(criteria.search_text)) |
            (Document.parsed_content.contains(criteria.search_text))
        )
    
    if criteria.has_financial_data is not None:
        if criteria.has_financial_data:
            query = query.filter(Document.financial_data.isnot(None))
        else:
            query = query.filter(Document.financial_data.is_(None))
    
    if criteria.has_legal_data is not None:
        if criteria.has_legal_data:
            query = query.filter(Document.legal_data.isnot(None))
        else:
            query = query.filter(Document.legal_data.is_(None))
    
    if criteria.confidence_min is not None:
        query = query.filter(Document.confidence_score >= criteria.confidence_min)
    
    if criteria.confidence_max is not None:
        query = query.filter(Document.confidence_score <= criteria.confidence_max)
    
    documents = query.offset(skip).limit(limit).all()
    return documents

@router.get("/templates/", response_model=List[dict])
async def get_document_templates(db: Session = Depends(get_db)):
    """Get available document templates"""
    templates = db.query(DocumentTemplate).filter(DocumentTemplate.is_active == True).all()
    return [
        {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "document_type": template.document_type,
            "required_fields": template.required_fields,
            "optional_fields": template.optional_fields
        }
        for template in templates
    ]

@router.post("/templates/")
async def create_document_template(
    name: str,
    description: str,
    document_type: DocumentType,
    required_fields: List[str],
    optional_fields: List[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new document template"""
    template = DocumentTemplate(
        name=name,
        description=description,
        document_type=document_type.value,
        required_fields=required_fields,
        optional_fields=optional_fields or [],
        created_by=1  # In production, get from authenticated user
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return {"message": "Document template created successfully", "template_id": template.id}

@router.get("/stats/")
async def get_document_stats(db: Session = Depends(get_db)):
    """Get document processing statistics"""
    total_documents = db.query(Document).count()
    processed_documents = db.query(Document).filter(Document.status == DocumentStatus.PARSED).count()
    failed_documents = db.query(Document).filter(Document.status == DocumentStatus.FAILED).count()
    processing_documents = db.query(Document).filter(Document.status == DocumentStatus.PROCESSING).count()
    
    # Document type breakdown
    type_breakdown = {}
    for doc_type in DocumentType:
        count = db.query(Document).filter(Document.document_type == doc_type.value).count()
        type_breakdown[doc_type.value] = count
    
    return {
        "total_documents": total_documents,
        "processed_documents": processed_documents,
        "failed_documents": failed_documents,
        "processing_documents": processing_documents,
        "success_rate": (processed_documents / total_documents * 100) if total_documents > 0 else 0,
        "type_breakdown": type_breakdown
    }
