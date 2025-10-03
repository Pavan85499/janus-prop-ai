from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio
import json

from core.database import get_db
from models.underwriting import (
    PropertyUnderwriting, RentComps, RenovationScenario,
    UnderwritingRequest, UnderwritingResponse, CashFlowAnalysis,
    SensitivityAnalysis, RentCompResponse, RenovationScenarioResponse,
    UnderwritingStatus, AnalysisType
)
from models.property import Property
from core.redis_client import publish_event

router = APIRouter()

# Mock AI underwriting analysis - in production, this would use real AI services
async def perform_underwriting_analysis(underwriting_id: int, analysis_type: str, property_data: dict) -> dict:
    """AI-powered underwriting analysis"""
    # Simulate AI processing time
    await asyncio.sleep(3)
    
    # Mock analysis based on analysis type
    if analysis_type == "cash_flow":
        return {
            "net_operating_income": property_data["gross_rental_income"] * 0.75,  # 25% expense ratio
            "debt_service": property_data["loan_amount"] * 0.006,  # Approximate monthly payment
            "cash_flow_before_taxes": property_data["gross_rental_income"] * 0.75 - (property_data["loan_amount"] * 0.006 * 12),
            "cap_rate": (property_data["gross_rental_income"] * 0.75) / property_data["purchase_price"] * 100,
            "cash_on_cash_return": ((property_data["gross_rental_income"] * 0.75) - (property_data["loan_amount"] * 0.006 * 12)) / property_data["down_payment"] * 100,
            "debt_coverage_ratio": (property_data["gross_rental_income"] * 0.75) / (property_data["loan_amount"] * 0.006 * 12),
            "risk_score": 75.0,
            "risk_factors": ["High loan-to-value ratio", "Market volatility", "Interest rate risk"],
            "ai_analysis": "Property shows strong cash flow potential with moderate risk factors. Cap rate of 6.2% is competitive for the market.",
            "ai_recommendations": ["Consider interest rate hedging", "Maintain 6-month cash reserve", "Monitor market conditions"],
            "ai_confidence_score": 0.88
        }
    elif analysis_type == "rent_comp":
        return {
            "rent_comps": [
                {
                    "address": "123 Oak St, San Francisco, CA",
                    "rent_amount": 3500,
                    "rent_per_sqft": 2.5,
                    "similarity_score": 0.92,
                    "distance_miles": 0.3
                },
                {
                    "address": "456 Pine Ave, San Francisco, CA",
                    "rent_amount": 3200,
                    "rent_per_sqft": 2.3,
                    "similarity_score": 0.87,
                    "distance_miles": 0.5
                }
            ],
            "market_rent_estimate": 3400,
            "rent_per_sqft_estimate": 2.4,
            "market_trend": "rising",
            "ai_analysis": "Rent comps show strong market demand with 5% year-over-year growth. Subject property is competitively priced.",
            "ai_confidence_score": 0.91
        }
    elif analysis_type == "renovation":
        return {
            "scenarios": [
                {
                    "scenario_name": "Light Renovation",
                    "total_cost": 15000,
                    "expected_rent_increase": 200,
                    "expected_value_increase": 25000,
                    "roi": 133.3,
                    "payback_months": 18
                },
                {
                    "scenario_name": "Full Renovation",
                    "total_cost": 45000,
                    "expected_rent_increase": 500,
                    "expected_value_increase": 75000,
                    "roi": 111.1,
                    "payback_months": 24
                }
            ],
            "ai_analysis": "Renovation scenarios show strong ROI potential. Light renovation offers better risk-adjusted returns.",
            "ai_confidence_score": 0.85
        }
    elif analysis_type == "sensitivity":
        return {
            "base_case": {
                "rent": property_data.get("gross_rental_income", 3000),
                "occupancy": 95,
                "expenses": property_data.get("gross_rental_income", 3000) * 0.25,
                "cash_flow": 1200
            },
            "optimistic_case": {
                "rent": property_data.get("gross_rental_income", 3000) * 1.1,
                "occupancy": 98,
                "expenses": property_data.get("gross_rental_income", 3000) * 0.22,
                "cash_flow": 1800
            },
            "pessimistic_case": {
                "rent": property_data.get("gross_rental_income", 3000) * 0.9,
                "occupancy": 90,
                "expenses": property_data.get("gross_rental_income", 3000) * 0.28,
                "cash_flow": 600
            },
            "break_even_rent": property_data.get("gross_rental_income", 3000) * 0.85,
            "break_even_occupancy": 88,
            "ai_analysis": "Sensitivity analysis shows property remains profitable even in pessimistic scenarios. Strong downside protection.",
            "ai_confidence_score": 0.89
        }
    
    return {}

async def process_underwriting_task(underwriting_id: int, analysis_type: str, property_data: dict, db: Session):
    """Background task to process underwriting analysis"""
    try:
        # Update underwriting status
        underwriting = db.query(PropertyUnderwriting).filter(PropertyUnderwriting.id == underwriting_id).first()
        if not underwriting:
            return
        
        underwriting.status = UnderwritingStatus.IN_PROGRESS
        db.commit()
        
        # Publish processing started event
        await publish_event("underwriting", "analysis_started", {
            "underwriting_id": underwriting_id,
            "status": "in_progress"
        })
        
        # Perform AI analysis
        analysis_results = await perform_underwriting_analysis(underwriting_id, analysis_type, property_data)
        
        # Update underwriting with results
        underwriting.status = UnderwritingStatus.COMPLETED
        underwriting.completed_at = datetime.utcnow()
        
        if analysis_type == "cash_flow":
            underwriting.net_operating_income = analysis_results.get("net_operating_income", 0)
            underwriting.debt_service = analysis_results.get("debt_service", 0)
            underwriting.cash_flow_before_taxes = analysis_results.get("cash_flow_before_taxes", 0)
            underwriting.cap_rate = analysis_results.get("cap_rate", 0)
            underwriting.cash_on_cash_return = analysis_results.get("cash_on_cash_return", 0)
            underwriting.debt_coverage_ratio = analysis_results.get("debt_coverage_ratio", 0)
            underwriting.risk_score = analysis_results.get("risk_score", 0)
            underwriting.risk_factors = analysis_results.get("risk_factors", [])
        
        underwriting.ai_analysis = analysis_results.get("ai_analysis", "")
        underwriting.ai_recommendations = analysis_results.get("ai_recommendations", [])
        underwriting.ai_confidence_score = analysis_results.get("ai_confidence_score", 0)
        
        # Handle rent comps
        if analysis_type == "rent_comp" and "rent_comps" in analysis_results:
            for comp_data in analysis_results["rent_comps"]:
                rent_comp = RentComps(
                    underwriting_id=underwriting_id,
                    address=comp_data["address"],
                    rent_amount=comp_data["rent_amount"],
                    rent_per_sqft=comp_data["rent_per_sqft"],
                    similarity_score=comp_data["similarity_score"],
                    distance_miles=comp_data["distance_miles"],
                    rent_date=datetime.utcnow()
                )
                db.add(rent_comp)
        
        # Handle renovation scenarios
        if analysis_type == "renovation" and "scenarios" in analysis_results:
            for scenario_data in analysis_results["scenarios"]:
                renovation_scenario = RenovationScenario(
                    underwriting_id=underwriting_id,
                    scenario_name=scenario_data["scenario_name"],
                    total_renovation_cost=scenario_data["total_cost"],
                    expected_rent_increase=scenario_data["expected_rent_increase"],
                    expected_value_increase=scenario_data["expected_value_increase"],
                    renovation_roi=scenario_data["roi"],
                    payback_period_months=scenario_data["payback_months"]
                )
                db.add(renovation_scenario)
        
        # Handle sensitivity analysis
        if analysis_type == "sensitivity":
            underwriting.sensitivity_scenarios = analysis_results
        
        db.commit()
        
        # Publish completion event
        await publish_event("underwriting", "analysis_completed", {
            "underwriting_id": underwriting_id,
            "status": "completed",
            "confidence_score": analysis_results.get("ai_confidence_score", 0)
        })
        
    except Exception as e:
        # Update underwriting status to failed
        underwriting = db.query(PropertyUnderwriting).filter(PropertyUnderwriting.id == underwriting_id).first()
        if underwriting:
            underwriting.status = UnderwritingStatus.FAILED
            db.commit()
        
        await publish_event("underwriting", "analysis_failed", {
            "underwriting_id": underwriting_id,
            "status": "failed",
            "error": str(e)
        })

@router.post("/", response_model=UnderwritingResponse)
async def create_underwriting(
    request: UnderwritingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new underwriting analysis"""
    
    # Verify property exists
    property = db.query(Property).filter(Property.id == request.property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Calculate loan amount
    loan_amount = request.purchase_price - request.down_payment
    
    # Create underwriting record
    underwriting = PropertyUnderwriting(
        property_id=request.property_id,
        analysis_type=request.analysis_type.value,
        purchase_price=request.purchase_price,
        down_payment=request.down_payment,
        loan_amount=loan_amount,
        interest_rate=request.interest_rate,
        loan_term_years=request.loan_term_years,
        gross_rental_income=request.gross_rental_income or 0,
        vacancy_rate=request.vacancy_rate,
        property_taxes=request.property_taxes or 0,
        insurance=request.insurance or 0,
        property_management=request.gross_rental_income * (request.property_management_rate / 100) if request.gross_rental_income else 0,
        maintenance=request.gross_rental_income * (request.maintenance_rate / 100) if request.gross_rental_income else 0,
        hoa_fees=request.hoa_fees or 0,
        created_by=1  # In production, get from authenticated user
    )
    
    db.add(underwriting)
    db.commit()
    db.refresh(underwriting)
    
    # Prepare property data for analysis
    property_data = {
        "purchase_price": request.purchase_price,
        "down_payment": request.down_payment,
        "loan_amount": loan_amount,
        "gross_rental_income": request.gross_rental_income or 0,
        "interest_rate": request.interest_rate
    }
    
    # Start background analysis
    background_tasks.add_task(
        process_underwriting_task,
        underwriting.id,
        request.analysis_type.value,
        property_data,
        db
    )
    
    return underwriting

@router.get("/", response_model=List[UnderwritingResponse])
async def get_underwriting_analyses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    property_id: Optional[int] = None,
    analysis_type: Optional[AnalysisType] = None,
    status: Optional[UnderwritingStatus] = None,
    db: Session = Depends(get_db)
):
    """Get underwriting analyses with filtering"""
    query = db.query(PropertyUnderwriting)
    
    if property_id:
        query = query.filter(PropertyUnderwriting.property_id == property_id)
    
    if analysis_type:
        query = query.filter(PropertyUnderwriting.analysis_type == analysis_type.value)
    
    if status:
        query = query.filter(PropertyUnderwriting.status == status.value)
    
    analyses = query.offset(skip).limit(limit).all()
    return analyses

@router.get("/{underwriting_id}", response_model=UnderwritingResponse)
async def get_underwriting_analysis(underwriting_id: int, db: Session = Depends(get_db)):
    """Get a specific underwriting analysis"""
    underwriting = db.query(PropertyUnderwriting).filter(PropertyUnderwriting.id == underwriting_id).first()
    if not underwriting:
        raise HTTPException(status_code=404, detail="Underwriting analysis not found")
    return underwriting

@router.get("/{underwriting_id}/cash-flow", response_model=CashFlowAnalysis)
async def get_cash_flow_analysis(underwriting_id: int, db: Session = Depends(get_db)):
    """Get detailed cash flow analysis"""
    underwriting = db.query(PropertyUnderwriting).filter(PropertyUnderwriting.id == underwriting_id).first()
    if not underwriting:
        raise HTTPException(status_code=404, detail="Underwriting analysis not found")
    
    if underwriting.analysis_type != "cash_flow":
        raise HTTPException(status_code=400, detail="This analysis is not a cash flow analysis")
    
    return CashFlowAnalysis(
        gross_rental_income=underwriting.gross_rental_income,
        vacancy_allowance=underwriting.gross_rental_income * (underwriting.vacancy_rate / 100),
        effective_gross_income=underwriting.effective_gross_income,
        operating_expenses={
            "property_taxes": underwriting.property_taxes,
            "insurance": underwriting.insurance,
            "property_management": underwriting.property_management,
            "maintenance": underwriting.maintenance,
            "utilities": underwriting.utilities,
            "hoa_fees": underwriting.hoa_fees,
            "other_expenses": underwriting.other_expenses
        },
        net_operating_income=underwriting.net_operating_income,
        debt_service=underwriting.debt_service,
        cash_flow_before_taxes=underwriting.cash_flow_before_taxes,
        cash_flow_after_taxes=underwriting.cash_flow_after_taxes
    )

@router.get("/{underwriting_id}/rent-comps", response_model=List[RentCompResponse])
async def get_rent_comps(underwriting_id: int, db: Session = Depends(get_db)):
    """Get rent comparables for an analysis"""
    rent_comps = db.query(RentComps).filter(RentComps.underwriting_id == underwriting_id).all()
    return rent_comps

@router.get("/{underwriting_id}/renovation-scenarios", response_model=List[RenovationScenarioResponse])
async def get_renovation_scenarios(underwriting_id: int, db: Session = Depends(get_db)):
    """Get renovation scenarios for an analysis"""
    scenarios = db.query(RenovationScenario).filter(RenovationScenario.underwriting_id == underwriting_id).all()
    return scenarios

@router.get("/{underwriting_id}/sensitivity", response_model=SensitivityAnalysis)
async def get_sensitivity_analysis(underwriting_id: int, db: Session = Depends(get_db)):
    """Get sensitivity analysis results"""
    underwriting = db.query(PropertyUnderwriting).filter(PropertyUnderwriting.id == underwriting_id).first()
    if not underwriting:
        raise HTTPException(status_code=404, detail="Underwriting analysis not found")
    
    if not underwriting.sensitivity_scenarios:
        raise HTTPException(status_code=400, detail="No sensitivity analysis available")
    
    scenarios = underwriting.sensitivity_scenarios
    return SensitivityAnalysis(
        base_case=scenarios.get("base_case", {}),
        optimistic_case=scenarios.get("optimistic_case", {}),
        pessimistic_case=scenarios.get("pessimistic_case", {}),
        break_even_rent=scenarios.get("break_even_rent", 0),
        break_even_occupancy=scenarios.get("break_even_occupancy", 0)
    )

@router.post("/{underwriting_id}/approve")
async def approve_underwriting(
    underwriting_id: int,
    approval_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Approve an underwriting analysis"""
    underwriting = db.query(PropertyUnderwriting).filter(PropertyUnderwriting.id == underwriting_id).first()
    if not underwriting:
        raise HTTPException(status_code=404, detail="Underwriting analysis not found")
    
    if underwriting.status != UnderwritingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Analysis must be completed before approval")
    
    underwriting.is_approved = True
    underwriting.approved_by = 1  # In production, get from authenticated user
    underwriting.approved_at = datetime.utcnow()
    underwriting.approval_notes = approval_notes
    
    db.commit()
    
    await publish_event("underwriting", "analysis_approved", {
        "underwriting_id": underwriting_id,
        "approved_by": 1,
        "approved_at": underwriting.approved_at.isoformat()
    })
    
    return {"message": "Underwriting analysis approved successfully"}

@router.post("/{underwriting_id}/reject")
async def reject_underwriting(
    underwriting_id: int,
    rejection_notes: str,
    db: Session = Depends(get_db)
):
    """Reject an underwriting analysis"""
    underwriting = db.query(PropertyUnderwriting).filter(PropertyUnderwriting.id == underwriting_id).first()
    if not underwriting:
        raise HTTPException(status_code=404, detail="Underwriting analysis not found")
    
    underwriting.is_approved = False
    underwriting.approved_by = 1  # In production, get from authenticated user
    underwriting.approved_at = datetime.utcnow()
    underwriting.approval_notes = rejection_notes
    
    db.commit()
    
    await publish_event("underwriting", "analysis_rejected", {
        "underwriting_id": underwriting_id,
        "rejected_by": 1,
        "rejected_at": underwriting.approved_at.isoformat(),
        "rejection_notes": rejection_notes
    })
    
    return {"message": "Underwriting analysis rejected"}

@router.get("/stats/")
async def get_underwriting_stats(db: Session = Depends(get_db)):
    """Get underwriting statistics"""
    total_analyses = db.query(PropertyUnderwriting).count()
    completed_analyses = db.query(PropertyUnderwriting).filter(PropertyUnderwriting.status == UnderwritingStatus.COMPLETED).count()
    approved_analyses = db.query(PropertyUnderwriting).filter(PropertyUnderwriting.is_approved == True).count()
    failed_analyses = db.query(PropertyUnderwriting).filter(PropertyUnderwriting.status == UnderwritingStatus.FAILED).count()
    
    # Analysis type breakdown
    type_breakdown = {}
    for analysis_type in AnalysisType:
        count = db.query(PropertyUnderwriting).filter(PropertyUnderwriting.analysis_type == analysis_type.value).count()
        type_breakdown[analysis_type.value] = count
    
    return {
        "total_analyses": total_analyses,
        "completed_analyses": completed_analyses,
        "approved_analyses": approved_analyses,
        "failed_analyses": failed_analyses,
        "completion_rate": (completed_analyses / total_analyses * 100) if total_analyses > 0 else 0,
        "approval_rate": (approved_analyses / completed_analyses * 100) if completed_analyses > 0 else 0,
        "type_breakdown": type_breakdown
    }
