from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio
import json

from core.database import get_db
from models.legal_compliance import (
    LegalCompliance, ComplianceRule, LegalDocument,
    ComplianceCheckRequest, ComplianceResponse, LegalDocumentResponse,
    ComplianceReport, ComplianceStatus, ComplianceType
)
from models.property import Property
from core.redis_client import publish_event

router = APIRouter()

# Mock AI legal analysis - in production, this would use real AI services
async def perform_legal_analysis(compliance_id: int, compliance_type: str, property_data: dict) -> dict:
    """AI-powered legal compliance analysis"""
    # Simulate AI processing time
    await asyncio.sleep(2)
    
    # Mock analysis based on compliance type
    if compliance_type == "ownership":
        return {
            "is_compliant": True,
            "compliance_score": 85.0,
            "risk_level": "medium",
            "issues_found": ["Minor title discrepancy in 2019"],
            "violations": [],
            "warnings": ["Verify current owner identity"],
            "recommendations": ["Obtain updated title report", "Verify owner signatures"],
            "legal_description": "Lot 1, Block 2, Subdivision ABC, City of San Francisco",
            "ownership_history": [
                {"owner": "John Doe", "date": "2020-01-15", "type": "purchase"},
                {"owner": "Jane Smith", "date": "2018-06-10", "type": "inheritance"}
            ],
            "title_issues": ["Minor boundary dispute resolved in 2019"],
            "ai_analysis": "Property has clear ownership chain with minor historical issues. No current title problems.",
            "ai_confidence_score": 0.88
        }
    elif compliance_type == "zoning":
        return {
            "is_compliant": True,
            "compliance_score": 92.0,
            "risk_level": "low",
            "issues_found": [],
            "violations": [],
            "warnings": [],
            "recommendations": ["Verify current zoning with city planning"],
            "current_zoning": "R1-Single Family Residential",
            "zoning_compliance": True,
            "zoning_violations": [],
            "variance_required": False,
            "ai_analysis": "Property is in compliance with current zoning regulations. No violations found.",
            "ai_confidence_score": 0.94
        }
    elif compliance_type == "permits":
        return {
            "is_compliant": False,
            "compliance_score": 65.0,
            "risk_level": "high",
            "issues_found": ["Missing building permit for 2020 renovation"],
            "violations": ["Unpermitted electrical work"],
            "warnings": ["Kitchen renovation may require permit"],
            "recommendations": [
                "Obtain retroactive permit for electrical work",
                "Schedule inspection for kitchen renovation",
                "Review all recent modifications"
            ],
            "required_permits": ["Electrical permit", "Building permit"],
            "existing_permits": ["Original construction permit (1995)"],
            "permit_violations": ["Unpermitted electrical work (2020)"],
            "ai_analysis": "Property has significant permit compliance issues. Immediate action required.",
            "ai_confidence_score": 0.91
        }
    elif compliance_type == "liens":
        return {
            "is_compliant": True,
            "compliance_score": 95.0,
            "risk_level": "low",
            "issues_found": [],
            "violations": [],
            "warnings": [],
            "recommendations": ["Continue monitoring for new liens"],
            "encumbrances": [
                {"type": "mortgage", "amount": 200000, "lien_holder": "First National Bank", "date": "2020-01-15"},
                {"type": "property_tax", "amount": 0, "status": "current", "date": "2024-01-01"}
            ],
            "ai_analysis": "Property has clean lien history with only standard mortgage encumbrance.",
            "ai_confidence_score": 0.96
        }
    elif compliance_type == "tax_history":
        return {
            "is_compliant": True,
            "compliance_score": 88.0,
            "risk_level": "low",
            "issues_found": [],
            "violations": [],
            "warnings": ["Late payment in 2022"],
            "recommendations": ["Maintain current payment schedule"],
            "tax_status": "current",
            "tax_delinquency_amount": 0,
            "tax_history": [
                {"year": 2024, "amount": 8500, "status": "paid", "date": "2024-01-15"},
                {"year": 2023, "amount": 8200, "status": "paid", "date": "2023-01-20"},
                {"year": 2022, "amount": 7800, "status": "paid", "date": "2022-02-10"}
            ],
            "tax_exemptions": ["Homestead exemption"],
            "ai_analysis": "Property has good tax payment history with minor late payment in 2022.",
            "ai_confidence_score": 0.89
        }
    elif compliance_type == "environmental":
        return {
            "is_compliant": True,
            "compliance_score": 90.0,
            "risk_level": "low",
            "issues_found": [],
            "violations": [],
            "warnings": ["Property in flood zone X"],
            "recommendations": ["Verify flood insurance coverage"],
            "environmental_issues": [],
            "flood_zone": "X",
            "environmental_restrictions": ["No development in flood zone"],
            "remediation_required": False,
            "ai_analysis": "Property has no environmental issues. Located in low-risk flood zone.",
            "ai_confidence_score": 0.92
        }
    elif compliance_type == "hoa":
        return {
            "is_compliant": True,
            "compliance_score": 78.0,
            "risk_level": "medium",
            "issues_found": ["HOA fee increase pending"],
            "violations": [],
            "warnings": ["Architectural approval required for modifications"],
            "recommendations": ["Review HOA bylaws before purchase"],
            "hoa_exists": True,
            "hoa_name": "Sunset Hills HOA",
            "hoa_fees": 250,
            "hoa_restrictions": [
                "No short-term rentals",
                "Architectural approval required",
                "Pet restrictions apply"
            ],
            "hoa_violations": [],
            "hoa_approval_required": True,
            "ai_analysis": "Property subject to HOA with moderate restrictions. Review bylaws carefully.",
            "ai_confidence_score": 0.85
        }
    
    return {}

async def process_compliance_check_task(compliance_id: int, compliance_type: str, property_data: dict, db: Session):
    """Background task to process compliance check"""
    try:
        # Update compliance status
        compliance = db.query(LegalCompliance).filter(LegalCompliance.id == compliance_id).first()
        if not compliance:
            return
        
        compliance.status = ComplianceStatus.IN_PROGRESS
        db.commit()
        
        # Publish processing started event
        await publish_event("legal_compliance", "check_started", {
            "compliance_id": compliance_id,
            "compliance_type": compliance_type,
            "status": "in_progress"
        })
        
        # Perform AI analysis
        analysis_results = await perform_legal_analysis(compliance_id, compliance_type, property_data)
        
        # Update compliance with results
        compliance.status = ComplianceStatus.PASSED if analysis_results.get("is_compliant", False) else ComplianceStatus.FAILED
        compliance.is_compliant = analysis_results.get("is_compliant", False)
        compliance.compliance_score = analysis_results.get("compliance_score", 0)
        compliance.risk_level = analysis_results.get("risk_level", "unknown")
        compliance.issues_found = analysis_results.get("issues_found", [])
        compliance.violations = analysis_results.get("violations", [])
        compliance.warnings = analysis_results.get("warnings", [])
        compliance.recommendations = analysis_results.get("recommendations", [])
        compliance.ai_analysis = analysis_results.get("ai_analysis", "")
        compliance.ai_confidence_score = analysis_results.get("ai_confidence_score", 0)
        
        # Update type-specific fields
        if compliance_type == "ownership":
            compliance.legal_description = analysis_results.get("legal_description", "")
            compliance.ownership_history = analysis_results.get("ownership_history", [])
            compliance.title_issues = analysis_results.get("title_issues", [])
        elif compliance_type == "zoning":
            compliance.current_zoning = analysis_results.get("current_zoning", "")
            compliance.zoning_compliance = analysis_results.get("zoning_compliance", False)
            compliance.zoning_violations = analysis_results.get("zoning_violations", [])
            compliance.variance_required = analysis_results.get("variance_required", False)
        elif compliance_type == "permits":
            compliance.required_permits = analysis_results.get("required_permits", [])
            compliance.existing_permits = analysis_results.get("existing_permits", [])
            compliance.permit_violations = analysis_results.get("permit_violations", [])
        elif compliance_type == "liens":
            compliance.encumbrances = analysis_results.get("encumbrances", [])
        elif compliance_type == "tax_history":
            compliance.tax_status = analysis_results.get("tax_status", "")
            compliance.tax_delinquency_amount = analysis_results.get("tax_delinquency_amount", 0)
            compliance.tax_history = analysis_results.get("tax_history", [])
            compliance.tax_exemptions = analysis_results.get("tax_exemptions", [])
        elif compliance_type == "environmental":
            compliance.environmental_issues = analysis_results.get("environmental_issues", [])
            compliance.flood_zone = analysis_results.get("flood_zone", "")
            compliance.environmental_restrictions = analysis_results.get("environmental_restrictions", [])
            compliance.remediation_required = analysis_results.get("remediation_required", False)
        elif compliance_type == "hoa":
            compliance.hoa_exists = analysis_results.get("hoa_exists", False)
            compliance.hoa_name = analysis_results.get("hoa_name", "")
            compliance.hoa_fees = analysis_results.get("hoa_fees", 0)
            compliance.hoa_restrictions = analysis_results.get("hoa_restrictions", [])
            compliance.hoa_violations = analysis_results.get("hoa_violations", [])
            compliance.hoa_approval_required = analysis_results.get("hoa_approval_required", False)
        
        # Determine if lawyer review is required
        compliance.requires_lawyer_review = (
            compliance.risk_level in ["high", "critical"] or
            len(compliance.violations) > 0 or
            compliance.compliance_score < 70
        )
        
        db.commit()
        
        # Publish completion event
        await publish_event("legal_compliance", "check_completed", {
            "compliance_id": compliance_id,
            "compliance_type": compliance_type,
            "status": compliance.status,
            "is_compliant": compliance.is_compliant,
            "compliance_score": compliance.compliance_score,
            "requires_lawyer_review": compliance.requires_lawyer_review
        })
        
    except Exception as e:
        # Update compliance status to failed
        compliance = db.query(LegalCompliance).filter(LegalCompliance.id == compliance_id).first()
        if compliance:
            compliance.status = ComplianceStatus.FAILED
            db.commit()
        
        await publish_event("legal_compliance", "check_failed", {
            "compliance_id": compliance_id,
            "compliance_type": compliance_type,
            "status": "failed",
            "error": str(e)
        })

@router.post("/check", response_model=List[ComplianceResponse])
async def run_compliance_check(
    request: ComplianceCheckRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Run comprehensive compliance checks for a property"""
    
    # Verify property exists
    property = db.query(Property).filter(Property.id == request.property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    compliance_results = []
    
    for compliance_type in request.compliance_types:
        # Check if compliance check already exists
        existing_compliance = db.query(LegalCompliance).filter(
            LegalCompliance.property_id == request.property_id,
            LegalCompliance.compliance_type == compliance_type.value
        ).first()
        
        if existing_compliance:
            # Update existing compliance
            existing_compliance.status = ComplianceStatus.PENDING
            existing_compliance.requires_lawyer_review = request.require_lawyer_review
            db.commit()
            compliance_id = existing_compliance.id
        else:
            # Create new compliance check
            compliance = LegalCompliance(
                property_id=request.property_id,
                compliance_type=compliance_type.value,
                requires_lawyer_review=request.require_lawyer_review,
                checked_by=1  # In production, get from authenticated user
            )
            db.add(compliance)
            db.commit()
            db.refresh(compliance)
            compliance_id = compliance.id
        
        # Prepare property data for analysis
        property_data = {
            "property_id": request.property_id,
            "address": property.address,
            "city": property.city,
            "state": property.state,
            "zip_code": property.zip_code
        }
        
        # Start background compliance check
        background_tasks.add_task(
            process_compliance_check_task,
            compliance_id,
            compliance_type.value,
            property_data,
            db
        )
        
        # Get the compliance record for response
        compliance = db.query(LegalCompliance).filter(LegalCompliance.id == compliance_id).first()
        compliance_results.append(compliance)
    
    return compliance_results

@router.get("/", response_model=List[ComplianceResponse])
async def get_compliance_checks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    property_id: Optional[int] = None,
    compliance_type: Optional[ComplianceType] = None,
    status: Optional[ComplianceStatus] = None,
    db: Session = Depends(get_db)
):
    """Get compliance checks with filtering"""
    query = db.query(LegalCompliance)
    
    if property_id:
        query = query.filter(LegalCompliance.property_id == property_id)
    
    if compliance_type:
        query = query.filter(LegalCompliance.compliance_type == compliance_type.value)
    
    if status:
        query = query.filter(LegalCompliance.status == status.value)
    
    checks = query.offset(skip).limit(limit).all()
    return checks

@router.get("/{compliance_id}", response_model=ComplianceResponse)
async def get_compliance_check(compliance_id: int, db: Session = Depends(get_db)):
    """Get a specific compliance check"""
    compliance = db.query(LegalCompliance).filter(LegalCompliance.id == compliance_id).first()
    if not compliance:
        raise HTTPException(status_code=404, detail="Compliance check not found")
    return compliance

@router.get("/property/{property_id}/report", response_model=ComplianceReport)
async def get_compliance_report(property_id: int, db: Session = Depends(get_db)):
    """Get comprehensive compliance report for a property"""
    compliance_checks = db.query(LegalCompliance).filter(
        LegalCompliance.property_id == property_id
    ).all()
    
    if not compliance_checks:
        raise HTTPException(status_code=404, detail="No compliance checks found for this property")
    
    # Calculate overall scores
    total_score = sum(check.compliance_score for check in compliance_checks if check.compliance_score)
    overall_compliance_score = total_score / len(compliance_checks) if compliance_checks else 0
    
    # Determine overall risk level
    risk_levels = [check.risk_level for check in compliance_checks if check.risk_level]
    overall_risk_level = "low"
    if "critical" in risk_levels:
        overall_risk_level = "critical"
    elif "high" in risk_levels:
        overall_risk_level = "high"
    elif "medium" in risk_levels:
        overall_risk_level = "medium"
    
    # Collect all issues and recommendations
    all_issues = []
    all_recommendations = []
    critical_issues = []
    
    for check in compliance_checks:
        if check.issues_found:
            all_issues.extend(check.issues_found)
        if check.violations:
            critical_issues.extend(check.violations)
        if check.recommendations:
            all_recommendations.extend(check.recommendations)
    
    # Check if lawyer review is required
    requires_lawyer_review = any(check.requires_lawyer_review for check in compliance_checks)
    
    # Build compliance summary
    compliance_summary = {}
    for check in compliance_checks:
        compliance_summary[check.compliance_type] = {
            "status": check.status,
            "is_compliant": check.is_compliant,
            "compliance_score": check.compliance_score,
            "risk_level": check.risk_level,
            "issues_count": len(check.issues_found) if check.issues_found else 0,
            "violations_count": len(check.violations) if check.violations else 0
        }
    
    return ComplianceReport(
        property_id=property_id,
        overall_compliance_score=overall_compliance_score,
        overall_risk_level=overall_risk_level,
        compliance_summary=compliance_summary,
        critical_issues=critical_issues,
        recommendations=all_recommendations,
        requires_lawyer_review=requires_lawyer_review,
        generated_at=datetime.utcnow()
    )

@router.post("/{compliance_id}/lawyer-review")
async def submit_lawyer_review(
    compliance_id: int,
    lawyer_notes: str,
    is_approved: bool,
    db: Session = Depends(get_db)
):
    """Submit lawyer review for a compliance check"""
    compliance = db.query(LegalCompliance).filter(LegalCompliance.id == compliance_id).first()
    if not compliance:
        raise HTTPException(status_code=404, detail="Compliance check not found")
    
    if not compliance.requires_lawyer_review:
        raise HTTPException(status_code=400, detail="This compliance check does not require lawyer review")
    
    compliance.lawyer_reviewed = True
    compliance.lawyer_notes = lawyer_notes
    compliance.lawyer_reviewed_by = 1  # In production, get from authenticated user
    compliance.lawyer_reviewed_at = datetime.utcnow()
    
    # Update compliance status based on lawyer review
    if is_approved:
        compliance.status = ComplianceStatus.PASSED
        compliance.is_compliant = True
    else:
        compliance.status = ComplianceStatus.FAILED
        compliance.is_compliant = False
    
    db.commit()
    
    await publish_event("legal_compliance", "lawyer_review_submitted", {
        "compliance_id": compliance_id,
        "is_approved": is_approved,
        "lawyer_notes": lawyer_notes,
        "reviewed_at": compliance.lawyer_reviewed_at.isoformat()
    })
    
    return {"message": "Lawyer review submitted successfully"}

@router.get("/rules/", response_model=List[dict])
async def get_compliance_rules(
    compliance_type: Optional[ComplianceType] = None,
    jurisdiction: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get compliance rules"""
    query = db.query(ComplianceRule).filter(ComplianceRule.is_active == True)
    
    if compliance_type:
        query = query.filter(ComplianceRule.compliance_type == compliance_type.value)
    
    if jurisdiction:
        query = query.filter(ComplianceRule.jurisdiction.contains(jurisdiction))
    
    rules = query.all()
    return [
        {
            "id": rule.id,
            "rule_name": rule.rule_name,
            "description": rule.description,
            "compliance_type": rule.compliance_type,
            "severity": rule.severity,
            "jurisdiction": rule.jurisdiction,
            "effective_date": rule.effective_date,
            "expiration_date": rule.expiration_date
        }
        for rule in rules
    ]

@router.get("/stats/")
async def get_compliance_stats(db: Session = Depends(get_db)):
    """Get compliance statistics"""
    total_checks = db.query(LegalCompliance).count()
    passed_checks = db.query(LegalCompliance).filter(LegalCompliance.is_compliant == True).count()
    failed_checks = db.query(LegalCompliance).filter(LegalCompliance.is_compliant == False).count()
    pending_checks = db.query(LegalCompliance).filter(LegalCompliance.status == ComplianceStatus.PENDING).count()
    in_progress_checks = db.query(LegalCompliance).filter(LegalCompliance.status == ComplianceStatus.IN_PROGRESS).count()
    requires_lawyer_review = db.query(LegalCompliance).filter(LegalCompliance.requires_lawyer_review == True).count()
    
    # Compliance type breakdown
    type_breakdown = {}
    for compliance_type in ComplianceType:
        count = db.query(LegalCompliance).filter(LegalCompliance.compliance_type == compliance_type.value).count()
        type_breakdown[compliance_type.value] = count
    
    return {
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "pending_checks": pending_checks,
        "in_progress_checks": in_progress_checks,
        "requires_lawyer_review": requires_lawyer_review,
        "compliance_rate": (passed_checks / total_checks * 100) if total_checks > 0 else 0,
        "type_breakdown": type_breakdown
    }
