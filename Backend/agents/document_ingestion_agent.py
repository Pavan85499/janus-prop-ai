"""
Document Ingestion & Parsing Agent for Janus Prop AI Backend

This agent specializes in uploading, parsing, and standardizing real estate documents
including deeds, leases, inspections, and financials into structured data.
"""

import asyncio
import structlog
from typing import Dict, Any, List, Optional, Union, BinaryIO, Tuple
from datetime import datetime
import json
import re
import os
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import mimetypes

try:
    import google.generativeai as genai
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.schema import HumanMessage, SystemMessage
    import PyPDF2
    import docx
    from PIL import Image
    import pytesseract
    DOCUMENT_PROCESSING_AVAILABLE = True
except ImportError:
    DOCUMENT_PROCESSING_AVAILABLE = False

from config.settings import get_settings
from core.redis_client import cache_get, cache_set, publish_event
from core.websocket_manager import get_websocket_manager

logger = structlog.get_logger(__name__)

class DocumentType(Enum):
    """Types of real estate documents."""
    DEED = "deed"
    LEASE = "lease"
    INSPECTION = "inspection"
    FINANCIAL = "financial"
    CONTRACT = "contract"
    TITLE = "title"
    SURVEY = "survey"
    APPRAISAL = "appraisal"
    INSURANCE = "insurance"
    TAX_RECORD = "tax_record"
    PERMIT = "permit"
    HOA_DOCUMENT = "hoa_document"
    UNKNOWN = "unknown"

@dataclass
class DocumentInfo:
    """Information about a processed document."""
    document_id: str
    original_filename: str
    document_type: DocumentType
    file_size: int
    mime_type: str
    upload_timestamp: datetime
    processing_status: str  # "uploaded", "processing", "completed", "failed"
    extracted_text: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.0
    processing_duration: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class DeedData:
    """Structured data extracted from deed documents."""
    property_address: str
    grantor: str
    grantee: str
    deed_type: str
    sale_price: Optional[float]
    sale_date: Optional[datetime]
    legal_description: str
    parcel_number: Optional[str]
    recording_info: Dict[str, Any]
    liens_encumbrances: List[str]
    conditions_restrictions: List[str]

@dataclass
class LeaseData:
    """Structured data extracted from lease documents."""
    property_address: str
    landlord: str
    tenant: str
    lease_start_date: datetime
    lease_end_date: datetime
    monthly_rent: float
    security_deposit: float
    lease_terms: List[str]
    utilities_included: List[str]
    pet_policy: str
    maintenance_responsibilities: Dict[str, str]
    renewal_options: str

@dataclass
class InspectionData:
    """Structured data extracted from inspection reports."""
    property_address: str
    inspection_date: datetime
    inspector_name: str
    inspector_license: str
    inspection_type: str  # "general", "specialized", "re-inspection"
    overall_condition: str
    major_issues: List[Dict[str, Any]]
    minor_issues: List[Dict[str, Any]]
    safety_concerns: List[str]
    estimated_repair_costs: Dict[str, float]
    photos_count: int
    recommendations: List[str]

@dataclass
class FinancialData:
    """Structured data extracted from financial documents."""
    property_address: str
    document_type: str  # "operating_statement", "pro_forma", "tax_return", "bank_statement"
    period_covered: str
    gross_income: float
    operating_expenses: Dict[str, float]
    net_operating_income: float
    capital_expenditures: Dict[str, float]
    cash_flow: float
    occupancy_rate: float
    rent_roll: List[Dict[str, Any]]

class DocumentIngestionAgent:
    """AI Agent specialized in document ingestion and parsing."""
    
    def __init__(self):
        self.agent_id = "document_ingestion_agent"
        self.name = "Document Ingestion Agent"
        self.settings = get_settings()
        self.gemini_api_key = self.settings.GEMINI_API_KEY
        self.upload_dir = Path(self.settings.UPLOAD_DIR)
        self.max_file_size = self.settings.MAX_FILE_SIZE
        self.allowed_types = self.settings.ALLOWED_FILE_TYPES
        self.is_initialized = False
        
        # Ensure upload directory exists
        self.upload_dir.mkdir(exist_ok=True)
        
        # Document type patterns for classification
        self.type_patterns = {
            DocumentType.DEED: [
                r"warranty deed", r"quit.?claim deed", r"special deed", 
                r"grantor", r"grantee", r"legal description"
            ],
            DocumentType.LEASE: [
                r"lease agreement", r"rental agreement", r"lessor", r"lessee",
                r"monthly rent", r"security deposit", r"lease term"
            ],
            DocumentType.INSPECTION: [
                r"inspection report", r"property inspection", r"inspector",
                r"condition", r"defects", r"recommendations"
            ],
            DocumentType.FINANCIAL: [
                r"income statement", r"operating statement", r"cash flow",
                r"pro forma", r"rent roll", r"financial analysis"
            ],
            DocumentType.APPRAISAL: [
                r"appraisal report", r"appraiser", r"market value",
                r"comparable sales", r"valuation"
            ]
        }
        
        if self._has_required_libraries():
            self._initialize_agent()
    
    def _has_required_libraries(self) -> bool:
        """Check if required libraries are available."""
        return DOCUMENT_PROCESSING_AVAILABLE and bool(self.gemini_api_key)
    
    def _initialize_agent(self):
        """Initialize the document ingestion agent."""
        try:
            if self.gemini_api_key:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel("gemini-pro")
                self.vision_model = genai.GenerativeModel("gemini-pro-vision")
                self.chat_model = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=self.gemini_api_key,
                    temperature=0.1,  # Low temperature for precise extraction
                    max_output_tokens=4096
                )
            
            self.is_initialized = True
            logger.info("Document Ingestion Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Document Ingestion Agent: {e}")
            self.is_initialized = False
    
    async def upload_and_process_document(
        self,
        file_content: bytes,
        filename: str,
        document_type_hint: Optional[str] = None
    ) -> DocumentInfo:
        """
        Upload and process a real estate document.
        
        Args:
            file_content: Binary content of the file
            filename: Original filename
            document_type_hint: Optional hint about document type
        """
        start_time = datetime.utcnow()
        document_id = f"doc_{int(start_time.timestamp())}"
        
        try:
            # Validate file
            await self._validate_file(file_content, filename)
            
            # Determine mime type
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                mime_type = "application/octet-stream"
            
            # Save file
            file_path = await self._save_file(file_content, document_id, filename)
            
            # Create initial document info
            doc_info = DocumentInfo(
                document_id=document_id,
                original_filename=filename,
                document_type=DocumentType.UNKNOWN,
                file_size=len(file_content),
                mime_type=mime_type,
                upload_timestamp=start_time,
                processing_status="uploaded",
                metadata={"file_path": str(file_path)}
            )
            
            # Start processing
            doc_info.processing_status = "processing"
            await self._publish_processing_update(doc_info)
            
            # Extract text from document
            extracted_text = await self._extract_text_from_file(file_path, mime_type)
            doc_info.extracted_text = extracted_text
            
            # Classify document type
            doc_info.document_type = await self._classify_document_type(
                extracted_text, document_type_hint
            )
            
            # Extract structured data based on document type
            structured_data, confidence = await self._extract_structured_data(
                extracted_text, doc_info.document_type
            )
            doc_info.structured_data = structured_data
            doc_info.confidence_score = confidence
            
            # Mark as completed
            doc_info.processing_status = "completed"
            doc_info.processing_duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Cache document info
            await cache_set(f"document:{document_id}", doc_info.__dict__, expire=86400)
            
            # Publish completion update
            await self._publish_processing_update(doc_info)
            
            logger.info(f"Document processed successfully: {document_id}")
            return doc_info
            
        except Exception as e:
            # Mark as failed
            doc_info.processing_status = "failed"
            doc_info.error_message = str(e)
            doc_info.processing_duration = (datetime.utcnow() - start_time).total_seconds()
            
            await self._publish_processing_update(doc_info)
            logger.error(f"Document processing failed: {e}")
            raise
    
    async def process_multiple_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[DocumentInfo]:
        """Process multiple documents concurrently."""
        tasks = []
        
        for doc in documents:
            task = self.upload_and_process_document(
                file_content=doc["content"],
                filename=doc["filename"],
                document_type_hint=doc.get("type_hint")
            )
            tasks.append(task)
        
        # Process concurrently with limit
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent processes
        
        async def process_with_semaphore(task):
            async with semaphore:
                return await task
        
        results = await asyncio.gather(
            *[process_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )
        
        # Filter out exceptions and return successful results
        successful_results = [r for r in results if isinstance(r, DocumentInfo)]
        
        return successful_results
    
    async def _validate_file(self, file_content: bytes, filename: str):
        """Validate uploaded file."""
        # Check file size
        if len(file_content) > self.max_file_size:
            raise ValueError(f"File size exceeds maximum allowed size of {self.max_file_size} bytes")
        
        # Check file extension
        file_ext = Path(filename).suffix.lower().lstrip('.')
        if file_ext not in self.allowed_types:
            raise ValueError(f"File type .{file_ext} not allowed. Allowed types: {self.allowed_types}")
        
        # Check if file content is not empty
        if len(file_content) == 0:
            raise ValueError("File is empty")
    
    async def _save_file(self, file_content: bytes, document_id: str, filename: str) -> Path:
        """Save uploaded file to disk."""
        # Create subdirectory for this document
        doc_dir = self.upload_dir / document_id
        doc_dir.mkdir(exist_ok=True)
        
        # Save file
        file_path = doc_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path
    
    async def _extract_text_from_file(self, file_path: Path, mime_type: str) -> str:
        """Extract text from various file formats."""
        try:
            if mime_type == "application/pdf":
                return await self._extract_text_from_pdf(file_path)
            elif mime_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                return await self._extract_text_from_docx(file_path)
            elif mime_type.startswith("image/"):
                return await self._extract_text_from_image(file_path)
            elif mime_type.startswith("text/"):
                return await self._extract_text_from_text_file(file_path)
            else:
                logger.warning(f"Unsupported file type for text extraction: {mime_type}")
                return ""
                
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""
    
    async def _extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        if not DOCUMENT_PROCESSING_AVAILABLE:
            return ""
        
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\\n"
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
        
        return text.strip()
    
    async def _extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        if not DOCUMENT_PROCESSING_AVAILABLE:
            return ""
        
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\\n"
            return text.strip()
        except Exception as e:
            logger.error(f"DOCX text extraction failed: {e}")
            return ""
    
    async def _extract_text_from_image(self, file_path: Path) -> str:
        """Extract text from image using OCR."""
        if not DOCUMENT_PROCESSING_AVAILABLE:
            return ""
        
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR text extraction failed: {e}")
            return ""
    
    async def _extract_text_from_text_file(self, file_path: Path) -> str:
        """Extract text from plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin1') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Text file reading failed: {e}")
                return ""
    
    async def _classify_document_type(self, text: str, type_hint: Optional[str] = None) -> DocumentType:
        """Classify document type based on content."""
        if not text:
            return DocumentType.UNKNOWN
        
        text_lower = text.lower()
        
        # Check type hint first
        if type_hint:
            try:
                return DocumentType(type_hint.lower())
            except ValueError:
                pass
        
        # Use pattern matching
        max_matches = 0
        best_type = DocumentType.UNKNOWN
        
        for doc_type, patterns in self.type_patterns.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, text_lower))
            if matches > max_matches:
                max_matches = matches
                best_type = doc_type
        
        # Use AI classification if pattern matching is inconclusive
        if max_matches == 0 and self.is_initialized:
            try:
                ai_classification = await self._ai_classify_document(text)
                if ai_classification != DocumentType.UNKNOWN:
                    return ai_classification
            except Exception as e:
                logger.warning(f"AI classification failed: {e}")
        
        return best_type
    
    async def _ai_classify_document(self, text: str) -> DocumentType:
        """Use AI to classify document type."""
        if not self.is_initialized:
            return DocumentType.UNKNOWN
        
        try:
            # Truncate text if too long
            max_chars = 2000
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
            
            prompt = f"""
            Classify the following real estate document text into one of these categories:
            - deed: Property deeds, warranty deeds, quitclaim deeds
            - lease: Rental agreements, lease agreements
            - inspection: Property inspection reports
            - financial: Income statements, operating statements, pro formas
            - contract: Purchase contracts, sales agreements
            - title: Title reports, title insurance
            - survey: Land surveys, boundary surveys
            - appraisal: Property appraisals, valuation reports
            - insurance: Property insurance documents
            - tax_record: Tax assessments, tax bills
            - permit: Building permits, construction permits
            - hoa_document: HOA bylaws, covenants, restrictions
            - unknown: If the document doesn't clearly fit any category
            
            Respond with only the category name.
            
            Document text:
            {text}
            """
            
            response = self.gemini_model.generate_content(prompt)
            classification = response.text.strip().lower()
            
            try:
                return DocumentType(classification)
            except ValueError:
                return DocumentType.UNKNOWN
                
        except Exception as e:
            logger.error(f"AI document classification failed: {e}")
            return DocumentType.UNKNOWN
    
    async def _extract_structured_data(self, text: str, doc_type: DocumentType) -> Tuple[Dict[str, Any], float]:
        """Extract structured data based on document type."""
        if not text or not self.is_initialized:
            return {}, 0.0
        
        try:
            if doc_type == DocumentType.DEED:
                return await self._extract_deed_data(text)
            elif doc_type == DocumentType.LEASE:
                return await self._extract_lease_data(text)
            elif doc_type == DocumentType.INSPECTION:
                return await self._extract_inspection_data(text)
            elif doc_type == DocumentType.FINANCIAL:
                return await self._extract_financial_data(text)
            else:
                # Generic extraction for other document types
                return await self._extract_generic_data(text, doc_type)
                
        except Exception as e:
            logger.error(f"Structured data extraction failed: {e}")
            return {}, 0.0
    
    async def _extract_deed_data(self, text: str) -> Tuple[Dict[str, Any], float]:
        """Extract structured data from deed documents."""
        prompt = f"""
        Extract the following information from this deed document:
        - Property address
        - Grantor (seller)
        - Grantee (buyer)
        - Deed type (warranty deed, quitclaim deed, etc.)
        - Sale price (if mentioned)
        - Sale date
        - Legal description
        - Parcel number or APN
        - Recording information (book, page, etc.)
        - Any liens or encumbrances mentioned
        - Conditions or restrictions
        
        Return the information as a JSON object with these keys:
        {{
            "property_address": "string",
            "grantor": "string",
            "grantee": "string",
            "deed_type": "string",
            "sale_price": number or null,
            "sale_date": "YYYY-MM-DD" or null,
            "legal_description": "string",
            "parcel_number": "string" or null,
            "recording_info": {{"book": "string", "page": "string", "date": "string"}},
            "liens_encumbrances": ["list of strings"],
            "conditions_restrictions": ["list of strings"]
        }}
        
        Document text:
        {text[:3000]}
        """
        
        response = self.gemini_model.generate_content(prompt)
        try:
            data = json.loads(response.text.strip())
            confidence = 0.8  # High confidence for structured extraction
            return data, confidence
        except json.JSONDecodeError:
            return {}, 0.0
    
    async def _extract_lease_data(self, text: str) -> Tuple[Dict[str, Any], float]:
        """Extract structured data from lease documents."""
        prompt = f"""
        Extract the following information from this lease agreement:
        - Property address
        - Landlord name
        - Tenant name
        - Lease start date
        - Lease end date
        - Monthly rent amount
        - Security deposit amount
        - Key lease terms
        - Utilities included
        - Pet policy
        - Maintenance responsibilities
        - Renewal options
        
        Return as JSON:
        {{
            "property_address": "string",
            "landlord": "string",
            "tenant": "string",
            "lease_start_date": "YYYY-MM-DD",
            "lease_end_date": "YYYY-MM-DD",
            "monthly_rent": number,
            "security_deposit": number,
            "lease_terms": ["list of key terms"],
            "utilities_included": ["list of utilities"],
            "pet_policy": "string",
            "maintenance_responsibilities": {{"landlord": "string", "tenant": "string"}},
            "renewal_options": "string"
        }}
        
        Document text:
        {text[:3000]}
        """
        
        response = self.gemini_model.generate_content(prompt)
        try:
            data = json.loads(response.text.strip())
            confidence = 0.85
            return data, confidence
        except json.JSONDecodeError:
            return {}, 0.0
    
    async def _extract_inspection_data(self, text: str) -> Tuple[Dict[str, Any], float]:
        """Extract structured data from inspection reports."""
        prompt = f"""
        Extract the following information from this property inspection report:
        - Property address
        - Inspection date
        - Inspector name and license
        - Inspection type
        - Overall property condition
        - Major issues found
        - Minor issues found
        - Safety concerns
        - Estimated repair costs
        - Number of photos taken
        - Recommendations
        
        Return as JSON:
        {{
            "property_address": "string",
            "inspection_date": "YYYY-MM-DD",
            "inspector_name": "string",
            "inspector_license": "string",
            "inspection_type": "string",
            "overall_condition": "string",
            "major_issues": [{{"area": "string", "issue": "string", "severity": "string"}}],
            "minor_issues": [{{"area": "string", "issue": "string"}}],
            "safety_concerns": ["list of concerns"],
            "estimated_repair_costs": {{"major_repairs": number, "minor_repairs": number}},
            "photos_count": number,
            "recommendations": ["list of recommendations"]
        }}
        
        Document text:
        {text[:3000]}
        """
        
        response = self.gemini_model.generate_content(prompt)
        try:
            data = json.loads(response.text.strip())
            confidence = 0.75
            return data, confidence
        except json.JSONDecodeError:
            return {}, 0.0
    
    async def _extract_financial_data(self, text: str) -> Tuple[Dict[str, Any], float]:
        """Extract structured data from financial documents."""
        prompt = f"""
        Extract financial information from this real estate financial document:
        - Property address
        - Document type (operating statement, pro forma, etc.)
        - Period covered
        - Gross income
        - Operating expenses breakdown
        - Net operating income
        - Capital expenditures
        - Cash flow
        - Occupancy rate
        - Rent roll information
        
        Return as JSON:
        {{
            "property_address": "string",
            "document_type": "string",
            "period_covered": "string",
            "gross_income": number,
            "operating_expenses": {{"category": number}},
            "net_operating_income": number,
            "capital_expenditures": {{"category": number}},
            "cash_flow": number,
            "occupancy_rate": number,
            "rent_roll": [{{"unit": "string", "rent": number, "tenant": "string"}}]
        }}
        
        Document text:
        {text[:3000]}
        """
        
        response = self.gemini_model.generate_content(prompt)
        try:
            data = json.loads(response.text.strip())
            confidence = 0.7
            return data, confidence
        except json.JSONDecodeError:
            return {}, 0.0
    
    async def _extract_generic_data(self, text: str, doc_type: DocumentType) -> Tuple[Dict[str, Any], float]:
        """Extract generic data for other document types."""
        prompt = f"""
        Extract key information from this {doc_type.value} document:
        - Property address (if mentioned)
        - Document date
        - Parties involved
        - Key amounts or values
        - Important terms or conditions
        - Expiration dates
        
        Return as JSON:
        {{
            "property_address": "string or null",
            "document_date": "YYYY-MM-DD or null",
            "parties_involved": ["list of parties"],
            "key_amounts": {{"description": number}},
            "important_terms": ["list of terms"],
            "expiration_dates": ["list of dates"]
        }}
        
        Document text:
        {text[:2000]}
        """
        
        response = self.gemini_model.generate_content(prompt)
        try:
            data = json.loads(response.text.strip())
            confidence = 0.6
            return data, confidence
        except json.JSONDecodeError:
            return {}, 0.0
    
    async def _publish_processing_update(self, doc_info: DocumentInfo):
        """Publish real-time update about document processing."""
        try:
            websocket_manager = get_websocket_manager()
            if websocket_manager:
                await websocket_manager.broadcast_to_all({
                    "type": "document_processing_update",
                    "document_id": doc_info.document_id,
                    "filename": doc_info.original_filename,
                    "status": doc_info.processing_status,
                    "document_type": doc_info.document_type.value,
                    "confidence_score": doc_info.confidence_score,
                    "processing_duration": doc_info.processing_duration,
                    "error_message": doc_info.error_message
                })
            
            # Publish to Redis
            await publish_event("agent_activity", "document_processing", {
                "agent_id": self.agent_id,
                "document_info": doc_info.__dict__
            })
            
        except Exception as e:
            logger.warning(f"Failed to publish processing update: {e}")
    
    async def get_document_info(self, document_id: str) -> Optional[DocumentInfo]:
        """Retrieve document information by ID."""
        try:
            cached_data = await cache_get(f"document:{document_id}")
            if cached_data:
                # Convert dict back to DocumentInfo
                data = json.loads(cached_data) if isinstance(cached_data, str) else cached_data
                
                # Convert document_type string back to enum
                if 'document_type' in data:
                    data['document_type'] = DocumentType(data['document_type'])
                
                # Convert timestamp strings back to datetime
                if 'upload_timestamp' in data:
                    data['upload_timestamp'] = datetime.fromisoformat(data['upload_timestamp'])
                
                return DocumentInfo(**data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve document info: {e}")
            return None
    
    async def search_documents(
        self,
        query: str,
        document_type: Optional[DocumentType] = None,
        property_address: Optional[str] = None
    ) -> List[DocumentInfo]:
        """Search processed documents."""
        # This would integrate with a proper search engine in production
        # For now, return mock results
        return []
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and its associated files."""
        try:
            # Remove from cache
            await cache_delete(f"document:{document_id}")
            
            # Remove files from disk
            doc_dir = self.upload_dir / document_id
            if doc_dir.exists():
                import shutil
                shutil.rmtree(doc_dir)
            
            logger.info(f"Document deleted: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False

# Global instance
_document_ingestion_agent = None

def get_document_ingestion_agent() -> DocumentIngestionAgent:
    """Get global document ingestion agent instance."""
    global _document_ingestion_agent
    if _document_ingestion_agent is None:
        _document_ingestion_agent = DocumentIngestionAgent()
    return _document_ingestion_agent

async def document_ingestion_agent_handler(task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler function for document ingestion agent tasks."""
    agent = get_document_ingestion_agent()
    
    if not agent.is_initialized:
        raise RuntimeError("Document Ingestion Agent not properly initialized")
    
    if task_type == "process_document":
        result = await agent.upload_and_process_document(
            file_content=task_data.get("file_content", b""),
            filename=task_data.get("filename", ""),
            document_type_hint=task_data.get("document_type_hint")
        )
        return {"document_info": result.__dict__}
    
    elif task_type == "process_multiple":
        documents = task_data.get("documents", [])
        results = await agent.process_multiple_documents(documents)
        return {"processed_documents": [doc.__dict__ for doc in results]}
    
    elif task_type == "get_document":
        document_id = task_data.get("document_id")
        doc_info = await agent.get_document_info(document_id)
        return {"document_info": doc_info.__dict__ if doc_info else None}
    
    elif task_type == "search_documents":
        results = await agent.search_documents(
            query=task_data.get("query", ""),
            document_type=DocumentType(task_data["document_type"]) if task_data.get("document_type") else None,
            property_address=task_data.get("property_address")
        )
        return {"search_results": [doc.__dict__ for doc in results]}
    
    elif task_type == "delete_document":
        success = await agent.delete_document(task_data.get("document_id", ""))
        return {"success": success}
    
    else:
        raise ValueError(f"Unknown task type: {task_type}")