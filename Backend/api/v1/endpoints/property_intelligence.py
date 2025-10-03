"""
Property Intelligence API endpoints for Janus Prop AI Backend

This module provides comprehensive property intelligence endpoints that integrate
all specialized AI agents for the complete real estate investment lifecycle.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel, Field

# Import agent handlers
try:
    from agents.deal_sourcing_agent import deal_sourcing_agent_handler
    from agents.document_ingestion_agent import document_ingestion_agent_handler
    from agents.automated_underwriting_agent import underwriting_agent_handler
    from agents.legal_compliance_agent import legal_compliance_agent_handler
    from agents.ai_investment_committee_agent import investment_committee_agent_handler
except ImportError:
    # Fallback handlers
    async def deal_sourcing_agent_handler(task_type: str, task_data: Dict[str, Any]):
        return {"status": "agent_not_available"}
    async def document_ingestion_agent_handler(task_type: str, task_data: Dict[str, Any]):
        return {"status": "agent_not_available"}
    async def underwriting_agent_handler(task_type: str, task_data: Dict[str, Any]):
        return {"status": "agent_not_available"}
    async def legal_compliance_agent_handler(task_type: str, task_data: Dict[str, Any]):
        return {"status": "agent_not_available"}
    async def investment_committee_agent_handler(task_type: str, task_data: Dict[str, Any]):
        return {"status": "agent_not_available"}

try:
    from core.redis_client import cache_get, cache_set, publish_event
    from core.websocket_manager import get_websocket_manager
except ImportError:
    # Fallback functions
    async def cache_get(key: str):
        return None
    async def cache_set(key: str, value: Any, expire: int = 3600):
        return False
    async def publish_event(channel: str, event: str, data: Any):
        return False
    def get_websocket_manager():
        return None

router = APIRouter()

# Request/Response Models
class PropertyAnalysisRequest(BaseModel):
    """Request model for comprehensive property analysis."""
    property_data: Dict[str, Any]
    financial_inputs: Dict[str, Any]
    analysis_options: Optional[Dict[str, Any]] = None
    investment_strategy: str = "buy_and_hold"

class MarketScanRequest(BaseModel):
    """Request model for market scanning."""
    location: str
    max_price: Optional[float] = None
    property_types: Optional[List[str]] = None
    min_equity_potential: float = 20000
    scan_radius_miles: float = 25

class DocumentUploadRequest(BaseModel):
    """Request model for document upload."""
    document_type_hint: Optional[str] = None
    property_id: Optional[str] = None

class UnderwritingRequest(BaseModel):
    """Request model for underwriting analysis."""
    property_data: Dict[str, Any]
    financial_inputs: Dict[str, Any]
    investment_strategy: str = "buy_and_hold"

class ComplianceRequest(BaseModel):
    """Request model for legal compliance check."""
    property_data: Dict[str, Any]
    legal_documents: Optional[List[Dict[str, Any]]] = None

class InvestmentCommitteeRequest(BaseModel):
    """Request model for investment committee analysis."""
    property_data: Dict[str, Any]
    financial_analysis: Dict[str, Any]
    market_data: Dict[str, Any]
    legal_analysis: Dict[str, Any]
    additional_context: Optional[Dict[str, Any]] = None

# Comprehensive Property Analysis Endpoints

@router.post("/analyze-property")
async def analyze_property_comprehensive(
    request: PropertyAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Comprehensive property analysis using all specialized agents.
    
    This endpoint orchestrates multiple AI agents to provide a complete
    investment analysis including deal sourcing, underwriting, legal compliance,
    and investment committee recommendation.
    """
    try:
        analysis_id = str(uuid4())
        property_id = request.property_data.get("id", analysis_id)
        
        # Start comprehensive analysis
        background_tasks.add_task(
            _run_comprehensive_analysis,
            analysis_id,
            request.property_data,
            request.financial_inputs,
            request.analysis_options or {},
            request.investment_strategy
        )
        
        return {
            "analysis_id": analysis_id,
            "property_id": property_id,
            "status": "analysis_started",
            "message": "Comprehensive property analysis initiated. You will receive real-time updates.",
            "estimated_completion": "3-5 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis initiation failed: {str(e)}")

async def _run_comprehensive_analysis(
    analysis_id: str,
    property_data: Dict[str, Any],
    financial_inputs: Dict[str, Any],
    analysis_options: Dict[str, Any],
    investment_strategy: str
):
    """Run comprehensive property analysis using all agents."""
    try:
        # Step 1: Automated Underwriting Analysis
        underwriting_result = await underwriting_agent_handler("generate_report", {
            "property_data": property_data,
            "financial_inputs": financial_inputs,
            "investment_strategy": investment_strategy
        })
        
        # Step 2: Legal Compliance Check
        legal_result = await legal_compliance_agent_handler("generate_compliance_report", {
            "property_data": property_data,
            "legal_documents": analysis_options.get("legal_documents")
        })
        
        # Step 3: Market Analysis (mock data for now)
        market_data = {
            "comparable_sales": [],
            "market_trends": "stable",
            "rental_demand": "high",
            "appreciation_forecast": 0.03
        }
        
        # Step 4: Investment Committee Analysis
        committee_result = await investment_committee_agent_handler("generate_memo", {
            "property_data": property_data,
            "financial_analysis": underwriting_result.get("underwriting_report", {}),
            "market_data": market_data,
            "legal_analysis": legal_result.get("compliance_report", {}),
            "additional_context": analysis_options
        })
        
        # Compile comprehensive results
        comprehensive_result = {
            "analysis_id": analysis_id,
            "property_id": property_data.get("id"),
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "underwriting_analysis": underwriting_result,
            "legal_compliance": legal_result,
            "market_analysis": market_data,
            "investment_committee_memo": committee_result,
            "overall_recommendation": committee_result.get("investment_memo", {}).get("committee_decision"),
            "confidence_score": committee_result.get("investment_memo", {}).get("decision_confidence"),
            "status": "completed"
        }
        
        # Cache results
        await cache_set(f"property_analysis:{analysis_id}", comprehensive_result, expire=86400)
        
        # Publish completion event
        await _publish_analysis_completion(analysis_id, comprehensive_result)
        
    except Exception as e:
        error_result = {
            "analysis_id": analysis_id,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        await cache_set(f"property_analysis:{analysis_id}", error_result, expire=3600)
        await _publish_analysis_completion(analysis_id, error_result)

@router.get("/analysis/{analysis_id}")
async def get_analysis_results(analysis_id: str):
    """Get comprehensive property analysis results."""
    try:
        cached_result = await cache_get(f"property_analysis:{analysis_id}")
        
        if not cached_result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return cached_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analysis: {str(e)}")

# Deal Sourcing Endpoints

@router.post("/scan-market")
async def scan_market_for_deals(request: MarketScanRequest):
    """Scan market for investment opportunities using Deal Sourcing Agent."""
    try:
        result = await deal_sourcing_agent_handler("scan_market", {
            "location": request.location,
            "max_price": request.max_price,
            "property_types": request.property_types,
            "min_equity_potential": request.min_equity_potential,
            "scan_radius_miles": request.scan_radius_miles
        })
        
        return {
            "status": "success",
            "scan_result": result.get("scan_result"),
            "message": "Market scan completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market scan failed: {str(e)}")

@router.post("/analyze-distressed")
async def analyze_distressed_properties(properties: List[Dict[str, Any]]):
    """Analyze properties for distress indicators using Deal Sourcing Agent."""
    try:
        result = await deal_sourcing_agent_handler("analyze_distressed", {
            "properties": properties
        })
        
        return {
            "status": "success",
            "distressed_leads": result.get("distressed_leads"),
            "message": f"Analyzed {len(properties)} properties for distress indicators"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Distressed property analysis failed: {str(e)}")

# Document Processing Endpoints

@router.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    document_type_hint: Optional[str] = Form(None),
    property_id: Optional[str] = Form(None)
):
    """Upload and process real estate document using Document Ingestion Agent."""
    try:
        # Read file content
        file_content = await file.read()
        
        result = await document_ingestion_agent_handler("process_document", {
            "file_content": file_content,
            "filename": file.filename,
            "document_type_hint": document_type_hint
        })
        
        return {
            "status": "success",
            "document_info": result.get("document_info"),
            "message": f"Document {file.filename} processed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@router.post("/upload-multiple-documents")
async def upload_multiple_documents(files: List[UploadFile] = File(...)):
    """Upload and process multiple documents concurrently."""
    try:
        documents = []
        for file in files:
            file_content = await file.read()
            documents.append({
                "content": file_content,
                "filename": file.filename,
                "type_hint": None
            })
        
        result = await document_ingestion_agent_handler("process_multiple", {
            "documents": documents
        })
        
        return {
            "status": "success",
            "processed_documents": result.get("processed_documents"),
            "message": f"Processed {len(files)} documents successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multiple document processing failed: {str(e)}")

@router.get("/document/{document_id}")
async def get_document_info(document_id: str):
    """Get processed document information."""
    try:
        result = await document_ingestion_agent_handler("get_document", {
            "document_id": document_id
        })
        
        document_info = result.get("document_info")
        if not document_info:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "status": "success",
            "document_info": document_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")

# Underwriting Endpoints

@router.post("/underwrite-property")
async def underwrite_property(request: UnderwritingRequest):
    """Generate comprehensive underwriting report using Automated Underwriting Agent."""
    try:
        result = await underwriting_agent_handler("generate_report", {
            "property_data": request.property_data,
            "financial_inputs": request.financial_inputs,
            "investment_strategy": request.investment_strategy
        })
        
        return {
            "status": "success",
            "underwriting_report": result.get("underwriting_report"),
            "message": "Underwriting analysis completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Underwriting analysis failed: {str(e)}")

@router.post("/analyze-brrrr")
async def analyze_brrrr_strategy(request: UnderwritingRequest):
    """Analyze BRRRR (Buy, Rehab, Rent, Refinance, Repeat) strategy."""
    try:
        result = await underwriting_agent_handler("brrrr_analysis", {
            "property_data": request.property_data,
            "financial_inputs": request.financial_inputs
        })
        
        return {
            "status": "success",
            "brrrr_analysis": result.get("brrrr_analysis"),
            "message": "BRRRR analysis completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BRRRR analysis failed: {str(e)}")

@router.post("/analyze-flip")
async def analyze_flip_potential(request: UnderwritingRequest):
    """Analyze fix-and-flip potential using Automated Underwriting Agent."""
    try:
        result = await underwriting_agent_handler("flip_analysis", {
            "property_data": request.property_data,
            "financial_inputs": request.financial_inputs
        })
        
        return {
            "status": "success",
            "flip_analysis": result.get("flip_analysis"),
            "message": "Flip analysis completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flip analysis failed: {str(e)}")

# Legal Compliance Endpoints

@router.post("/check-compliance")
async def check_legal_compliance(request: ComplianceRequest):
    """Generate legal compliance report using Legal Compliance Agent."""
    try:
        result = await legal_compliance_agent_handler("generate_compliance_report", {
            "property_data": request.property_data,
            "legal_documents": request.legal_documents
        })
        
        return {
            "status": "success",
            "compliance_report": result.get("compliance_report"),
            "message": "Legal compliance check completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Legal compliance check failed: {str(e)}")

@router.post("/check-title")
async def check_title_issues(property_data: Dict[str, Any]):
    """Quick title issues check using Legal Compliance Agent."""
    try:
        result = await legal_compliance_agent_handler("check_title", {
            "property_data": property_data
        })
        
        return {
            "status": "success",
            "title_check": result.get("title_check"),
            "message": "Title check completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Title check failed: {str(e)}")

@router.post("/verify-zoning")
async def verify_zoning_compliance(property_data: Dict[str, Any], intended_use: str):
    """Verify zoning compliance for intended use."""
    try:
        result = await legal_compliance_agent_handler("verify_zoning", {
            "property_data": property_data,
            "intended_use": intended_use
        })
        
        return {
            "status": "success",
            "zoning_verification": result.get("zoning_verification"),
            "message": "Zoning verification completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Zoning verification failed: {str(e)}")

# Investment Committee Endpoints

@router.post("/investment-committee-review")
async def investment_committee_review(request: InvestmentCommitteeRequest):
    """Generate investment committee memo using AI Investment Committee Agent."""
    try:
        result = await investment_committee_agent_handler("generate_memo", {
            "property_data": request.property_data,
            "financial_analysis": request.financial_analysis,
            "market_data": request.market_data,
            "legal_analysis": request.legal_analysis,
            "additional_context": request.additional_context
        })
        
        return {
            "status": "success",
            "investment_memo": result.get("investment_memo"),
            "message": "Investment committee review completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Investment committee review failed: {str(e)}")

# Real-time Updates and Status

@router.get("/analysis-status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Get real-time status of ongoing analysis."""
    try:
        cached_result = await cache_get(f"property_analysis:{analysis_id}")
        
        if not cached_result:
            return {
                "analysis_id": analysis_id,
                "status": "not_found",
                "message": "Analysis not found or expired"
            }
        
        return {
            "analysis_id": analysis_id,
            "status": cached_result.get("status", "unknown"),
            "progress": cached_result.get("progress", {}),
            "last_updated": cached_result.get("timestamp"),
            "estimated_completion": cached_result.get("estimated_completion")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analysis status: {str(e)}")

# Helper Functions

async def _publish_analysis_completion(analysis_id: str, result: Dict[str, Any]):
    """Publish analysis completion event."""
    try:
        websocket_manager = get_websocket_manager()
        if websocket_manager:
            await websocket_manager.broadcast_to_all({
                "type": "property_analysis_complete",
                "analysis_id": analysis_id,
                "status": result.get("status"),
                "property_id": result.get("property_id"),
                "overall_recommendation": result.get("overall_recommendation"),
                "confidence_score": result.get("confidence_score")
            })
        
        await publish_event("property_intelligence", "analysis_complete", {
            "analysis_id": analysis_id,
            "result_summary": result
        })
        
    except Exception as e:
        # Don't fail the analysis if publishing fails
        pass

# Bulk Operations

@router.post("/bulk-analyze")
async def bulk_property_analysis(
    properties: List[Dict[str, Any]],
    background_tasks: BackgroundTasks
):
    """Perform bulk property analysis for multiple properties."""
    try:
        batch_id = str(uuid4())
        
        # Start bulk analysis
        background_tasks.add_task(
            _run_bulk_analysis,
            batch_id,
            properties
        )
        
        return {
            "batch_id": batch_id,
            "property_count": len(properties),
            "status": "bulk_analysis_started",
            "message": f"Bulk analysis initiated for {len(properties)} properties",
            "estimated_completion": f"{len(properties) * 2}-{len(properties) * 4} minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk analysis initiation failed: {str(e)}")

async def _run_bulk_analysis(batch_id: str, properties: List[Dict[str, Any]]):
    """Run bulk property analysis."""
    try:
        results = []
        
        for i, property_data in enumerate(properties):
            try:
                # Run basic analysis for each property
                analysis_id = f"{batch_id}_{i}"
                
                # Basic underwriting
                underwriting_result = await underwriting_agent_handler("generate_report", {
                    "property_data": property_data,
                    "financial_inputs": property_data.get("financial_inputs", {}),
                    "investment_strategy": "buy_and_hold"
                })
                
                results.append({
                    "property_id": property_data.get("id", analysis_id),
                    "analysis_id": analysis_id,
                    "status": "completed",
                    "underwriting_result": underwriting_result
                })
                
            except Exception as e:
                results.append({
                    "property_id": property_data.get("id", f"property_{i}"),
                    "analysis_id": f"{batch_id}_{i}",
                    "status": "failed",
                    "error": str(e)
                })
        
        # Cache bulk results
        bulk_result = {
            "batch_id": batch_id,
            "total_properties": len(properties),
            "completed_analyses": len([r for r in results if r["status"] == "completed"]),
            "failed_analyses": len([r for r in results if r["status"] == "failed"]),
            "results": results,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await cache_set(f"bulk_analysis:{batch_id}", bulk_result, expire=86400)
        
        # Publish completion
        await publish_event("property_intelligence", "bulk_analysis_complete", {
            "batch_id": batch_id,
            "summary": bulk_result
        })
        
    except Exception as e:
        error_result = {
            "batch_id": batch_id,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        await cache_set(f"bulk_analysis:{batch_id}", error_result, expire=3600)

@router.get("/bulk-analysis/{batch_id}")
async def get_bulk_analysis_results(batch_id: str):
    """Get bulk property analysis results."""
    try:
        cached_result = await cache_get(f"bulk_analysis:{batch_id}")
        
        if not cached_result:
            raise HTTPException(status_code=404, detail="Bulk analysis not found")
        
        return cached_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve bulk analysis: {str(e)}")