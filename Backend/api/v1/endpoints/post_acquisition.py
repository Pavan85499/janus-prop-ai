from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
import json

from core.database import get_db
from models.post_acquisition import (
    PostAcquisitionAsset, RenovationProject, TenantDemand, RefinancingOpportunity, AssetMonitoring,
    PostAcquisitionAssetRequest, PostAcquisitionAssetResponse, RenovationProjectRequest,
    RenovationProjectResponse, RefinancingOpportunityResponse, AssetMonitoringResponse,
    AssetStatus, RenovationStatus, RefinancingStatus
)
from models.property import Property
from models.execution_closing import DealExecution
from core.redis_client import publish_event

router = APIRouter()

# Mock AI analysis for post-acquisition intelligence
async def analyze_asset_performance(asset_data: dict) -> dict:
    """AI analysis of asset performance"""
    await asyncio.sleep(1)
    
    # Mock analysis based on asset data
    monthly_rent = asset_data.get("monthly_rent", 0)
    monthly_expenses = asset_data.get("monthly_expenses", 0)
    acquisition_price = asset_data.get("acquisition_price", 0)
    current_value = asset_data.get("current_value", acquisition_price)
    
    # Calculate performance metrics
    monthly_cash_flow = monthly_rent - monthly_expenses
    annual_cash_flow = monthly_cash_flow * 12
    cap_rate = (annual_cash_flow / current_value) * 100 if current_value > 0 else 0
    cash_on_cash_return = (annual_cash_flow / acquisition_price) * 100 if acquisition_price > 0 else 0
    
    # Calculate performance score
    performance_score = 70.0  # Base score
    if cap_rate > 8:
        performance_score += 15
    elif cap_rate > 6:
        performance_score += 10
    elif cap_rate < 4:
        performance_score -= 15
    
    if cash_on_cash_return > 15:
        performance_score += 10
    elif cash_on_cash_return > 10:
        performance_score += 5
    elif cash_on_cash_return < 5:
        performance_score -= 10
    
    # Calculate risk score
    risk_score = 30.0  # Base risk score
    if monthly_cash_flow < 0:
        risk_score += 30
    if cap_rate < 5:
        risk_score += 20
    if monthly_expenses > monthly_rent * 0.8:
        risk_score += 15
    
    # Calculate opportunity score
    opportunity_score = 60.0  # Base opportunity score
    if current_value > acquisition_price * 1.2:
        opportunity_score += 20
    elif current_value > acquisition_price * 1.1:
        opportunity_score += 10
    if monthly_rent < current_value * 0.01:  # Rent is less than 1% of value
        opportunity_score += 15
    
    performance_score = max(0, min(100, performance_score))
    risk_score = max(0, min(100, risk_score))
    opportunity_score = max(0, min(100, opportunity_score))
    
    return {
        "monthly_cash_flow": monthly_cash_flow,
        "annual_cash_flow": annual_cash_flow,
        "cap_rate": cap_rate,
        "cash_on_cash_return": cash_on_cash_return,
        "performance_score": performance_score,
        "risk_score": risk_score,
        "opportunity_score": opportunity_score,
        "ai_analysis": f"Asset shows {performance_score}/100 performance score with {risk_score}/100 risk level. {'Strong performer' if performance_score >= 80 else 'Moderate performer' if performance_score >= 60 else 'Underperforming'}.",
        "ai_recommendations": [
            "Consider rent increase if below market" if monthly_rent < current_value * 0.01 else None,
            "Review expense structure for optimization" if monthly_expenses > monthly_rent * 0.6 else None,
            "Monitor market conditions for refinancing opportunities" if opportunity_score >= 70 else None,
            "Consider renovation to increase value" if opportunity_score >= 80 else None
        ]
    }

async def analyze_renovation_opportunity(renovation_data: dict) -> dict:
    """AI analysis of renovation opportunity"""
    await asyncio.sleep(1)
    
    estimated_cost = renovation_data.get("estimated_cost", 0)
    expected_rent_increase = renovation_data.get("expected_rent_increase", 0)
    expected_value_increase = renovation_data.get("expected_value_increase", 0)
    
    # Calculate ROI
    total_benefit = expected_rent_increase * 12 + expected_value_increase
    roi = (total_benefit / estimated_cost) * 100 if estimated_cost > 0 else 0
    
    # Calculate payback period
    annual_rent_benefit = expected_rent_increase * 12
    payback_period = estimated_cost / annual_rent_benefit if annual_rent_benefit > 0 else 0
    
    # Risk assessment
    risk_factors = []
    if roi < 50:
        risk_factors.append("Low ROI - consider cost reduction")
    if payback_period > 5:
        risk_factors.append("Long payback period")
    if estimated_cost > renovation_data.get("asset_value", 0) * 0.3:
        risk_factors.append("High renovation cost relative to asset value")
    
    return {
        "expected_roi": roi,
        "payback_period_years": payback_period,
        "risk_factors": risk_factors,
        "ai_analysis": f"Renovation project shows {roi:.1f}% ROI with {payback_period:.1f} year payback period. {'Strong investment' if roi >= 100 else 'Moderate investment' if roi >= 50 else 'High risk investment'}.",
        "ai_recommendations": [
            "Proceed with renovation" if roi >= 100 else "Consider cost reduction" if roi >= 50 else "Reconsider project scope",
            "Negotiate contractor pricing" if estimated_cost > renovation_data.get("asset_value", 0) * 0.2 else None,
            "Phase renovation to reduce risk" if payback_period > 3 else None,
            "Consider alternative improvements" if roi < 30 else None
        ]
    }

async def analyze_refinancing_opportunity(refinancing_data: dict) -> dict:
    """AI analysis of refinancing opportunity"""
    await asyncio.sleep(1)
    
    current_loan_balance = refinancing_data.get("current_loan_balance", 0)
    current_interest_rate = refinancing_data.get("current_interest_rate", 0)
    new_interest_rate = refinancing_data.get("new_interest_rate", 0)
    current_monthly_payment = refinancing_data.get("current_monthly_payment", 0)
    new_monthly_payment = refinancing_data.get("new_monthly_payment", 0)
    closing_costs = refinancing_data.get("closing_costs", 0)
    
    # Calculate savings
    monthly_savings = current_monthly_payment - new_monthly_payment
    annual_savings = monthly_savings * 12
    
    # Calculate break-even
    break_even_months = closing_costs / monthly_savings if monthly_savings > 0 else 0
    
    # Calculate opportunity score
    opportunity_score = 50.0  # Base score
    if monthly_savings > 200:
        opportunity_score += 20
    elif monthly_savings > 100:
        opportunity_score += 10
    if break_even_months < 24:
        opportunity_score += 15
    elif break_even_months < 36:
        opportunity_score += 10
    if current_interest_rate - new_interest_rate > 1:
        opportunity_score += 15
    
    opportunity_score = max(0, min(100, opportunity_score))
    
    return {
        "monthly_savings": monthly_savings,
        "annual_savings": annual_savings,
        "break_even_months": break_even_months,
        "opportunity_score": opportunity_score,
        "ai_analysis": f"Refinancing opportunity shows {opportunity_score}/100 score with {break_even_months:.1f} month break-even. {'Strong opportunity' if opportunity_score >= 80 else 'Moderate opportunity' if opportunity_score >= 60 else 'Weak opportunity'}.",
        "ai_recommendations": [
            "Proceed with refinancing" if opportunity_score >= 80 else "Consider refinancing" if opportunity_score >= 60 else "Wait for better rates",
            "Shop multiple lenders for best terms" if opportunity_score >= 70 else None,
            "Consider cash-out refinancing" if refinancing_data.get("asset_value", 0) > current_loan_balance * 1.5 else None,
            "Monitor rate trends before proceeding" if opportunity_score < 60 else None
        ]
    }

async def analyze_tenant_demand(demand_data: dict) -> dict:
    """AI analysis of tenant demand"""
    await asyncio.sleep(1)
    
    inquiry_count = demand_data.get("inquiry_count", 0)
    application_count = demand_data.get("application_count", 0)
    lease_signed_count = demand_data.get("lease_signed_count", 0)
    average_days_on_market = demand_data.get("average_days_on_market", 0)
    
    # Calculate conversion rates
    inquiry_to_application_rate = (application_count / inquiry_count) * 100 if inquiry_count > 0 else 0
    application_to_lease_rate = (lease_signed_count / application_count) * 100 if application_count > 0 else 0
    overall_conversion_rate = (lease_signed_count / inquiry_count) * 100 if inquiry_count > 0 else 0
    
    # Analyze demand trend
    demand_trend = "stable"
    if inquiry_count > demand_data.get("previous_period_inquiries", 0) * 1.2:
        demand_trend = "increasing"
    elif inquiry_count < demand_data.get("previous_period_inquiries", 0) * 0.8:
        demand_trend = "decreasing"
    
    return {
        "inquiry_to_application_rate": inquiry_to_application_rate,
        "application_to_lease_rate": application_to_lease_rate,
        "overall_conversion_rate": overall_conversion_rate,
        "demand_trend": demand_trend,
        "ai_analysis": f"Tenant demand shows {demand_trend} trend with {overall_conversion_rate:.1f}% overall conversion rate. {'Strong demand' if overall_conversion_rate >= 20 else 'Moderate demand' if overall_conversion_rate >= 10 else 'Weak demand'}.",
        "ai_recommendations": [
            "Increase marketing efforts" if overall_conversion_rate < 10 else None,
            "Review pricing strategy" if inquiry_count > 0 and application_count < inquiry_count * 0.3 else None,
            "Improve property presentation" if application_count > 0 and lease_signed_count < application_count * 0.5 else None,
            "Consider rent reduction" if average_days_on_market > 30 else None
        ]
    }

@router.post("/assets", response_model=PostAcquisitionAssetResponse)
async def create_post_acquisition_asset(
    request: PostAcquisitionAssetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new post-acquisition asset"""
    
    # Verify property and deal exist
    property = db.query(Property).filter(Property.id == request.property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    deal = db.query(DealExecution).filter(DealExecution.id == request.deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal execution not found")
    
    # Create asset
    asset = PostAcquisitionAsset(
        property_id=request.property_id,
        deal_id=request.deal_id,
        asset_name=request.asset_name,
        acquisition_date=request.acquisition_date,
        acquisition_price=request.acquisition_price,
        monthly_rent=request.monthly_rent,
        monthly_expenses=request.monthly_expenses,
        current_value=request.acquisition_price,  # Initial value
        total_investment=request.acquisition_price,
        created_by=1  # In production, get from authenticated user
    )
    
    db.add(asset)
    db.commit()
    db.refresh(asset)
    
    # Prepare data for AI analysis
    asset_data = {
        "monthly_rent": request.monthly_rent,
        "monthly_expenses": request.monthly_expenses,
        "acquisition_price": request.acquisition_price,
        "current_value": request.acquisition_price
    }
    
    # Start background AI analysis
    background_tasks.add_task(
        analyze_asset_performance,
        asset_data
    )
    
    return asset

@router.get("/assets", response_model=List[PostAcquisitionAssetResponse])
async def get_post_acquisition_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[AssetStatus] = None,
    db: Session = Depends(get_db)
):
    """Get post-acquisition assets with filtering"""
    query = db.query(PostAcquisitionAsset)
    
    if status:
        query = query.filter(PostAcquisitionAsset.status == status.value)
    
    assets = query.offset(skip).limit(limit).all()
    return assets

@router.get("/assets/{asset_id}", response_model=PostAcquisitionAssetResponse)
async def get_post_acquisition_asset(asset_id: int, db: Session = Depends(get_db)):
    """Get a specific post-acquisition asset"""
    asset = db.query(PostAcquisitionAsset).filter(PostAcquisitionAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Post-acquisition asset not found")
    return asset

@router.post("/assets/{asset_id}/renovation-projects", response_model=RenovationProjectResponse)
async def create_renovation_project(
    asset_id: int,
    request: RenovationProjectRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a renovation project for an asset"""
    
    # Verify asset exists
    asset = db.query(PostAcquisitionAsset).filter(PostAcquisitionAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Post-acquisition asset not found")
    
    # Create renovation project
    project = RenovationProject(
        asset_id=asset_id,
        project_name=request.project_name,
        description=request.description,
        estimated_cost=request.estimated_cost,
        estimated_duration_days=request.estimated_duration_days,
        scope_of_work=request.scope_of_work,
        expected_rent_increase=request.expected_rent_increase,
        expected_value_increase=request.expected_value_increase,
        created_by=1
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Prepare data for AI analysis
    renovation_data = {
        "estimated_cost": request.estimated_cost,
        "expected_rent_increase": request.expected_rent_increase,
        "expected_value_increase": request.expected_value_increase,
        "asset_value": asset.current_value
    }
    
    # Start background AI analysis
    background_tasks.add_task(
        analyze_renovation_opportunity,
        renovation_data
    )
    
    return project

@router.get("/assets/{asset_id}/renovation-projects", response_model=List[RenovationProjectResponse])
async def get_renovation_projects(asset_id: int, db: Session = Depends(get_db)):
    """Get renovation projects for an asset"""
    projects = db.query(RenovationProject).filter(RenovationProject.asset_id == asset_id).all()
    return projects

@router.post("/assets/{asset_id}/refinancing-opportunities", response_model=RefinancingOpportunityResponse)
async def create_refinancing_opportunity(
    asset_id: int,
    current_loan_balance: float,
    current_interest_rate: float,
    new_interest_rate: float,
    current_monthly_payment: float,
    new_monthly_payment: float,
    closing_costs: float,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a refinancing opportunity for an asset"""
    
    # Verify asset exists
    asset = db.query(PostAcquisitionAsset).filter(PostAcquisitionAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Post-acquisition asset not found")
    
    # Create refinancing opportunity
    opportunity = RefinancingOpportunity(
        asset_id=asset_id,
        opportunity_name=f"Refinancing Opportunity - {asset.asset_name}",
        current_loan_balance=current_loan_balance,
        current_interest_rate=current_interest_rate,
        new_interest_rate=new_interest_rate,
        current_monthly_payment=current_monthly_payment,
        new_monthly_payment=new_monthly_payment,
        closing_costs=closing_costs,
        created_by=1
    )
    
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    
    # Prepare data for AI analysis
    refinancing_data = {
        "current_loan_balance": current_loan_balance,
        "current_interest_rate": current_interest_rate,
        "new_interest_rate": new_interest_rate,
        "current_monthly_payment": current_monthly_payment,
        "new_monthly_payment": new_monthly_payment,
        "closing_costs": closing_costs,
        "asset_value": asset.current_value
    }
    
    # Start background AI analysis
    background_tasks.add_task(
        analyze_refinancing_opportunity,
        refinancing_data
    )
    
    return opportunity

@router.get("/assets/{asset_id}/refinancing-opportunities", response_model=List[RefinancingOpportunityResponse])
async def get_refinancing_opportunities(asset_id: int, db: Session = Depends(get_db)):
    """Get refinancing opportunities for an asset"""
    opportunities = db.query(RefinancingOpportunity).filter(RefinancingOpportunity.asset_id == asset_id).all()
    return opportunities

@router.post("/assets/{asset_id}/tenant-demand", response_model=dict)
async def create_tenant_demand_analysis(
    asset_id: int,
    inquiry_count: int,
    application_count: int,
    lease_signed_count: int,
    average_days_on_market: float,
    period_start: datetime,
    period_end: datetime,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create tenant demand analysis for an asset"""
    
    # Verify asset exists
    asset = db.query(PostAcquisitionAsset).filter(PostAcquisitionAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Post-acquisition asset not found")
    
    # Create tenant demand record
    demand = TenantDemand(
        asset_id=asset_id,
        inquiry_count=inquiry_count,
        application_count=application_count,
        lease_signed_count=lease_signed_count,
        average_days_on_market=average_days_on_market,
        period_start=period_start,
        period_end=period_end,
        created_by=1
    )
    
    db.add(demand)
    db.commit()
    db.refresh(demand)
    
    # Prepare data for AI analysis
    demand_data = {
        "inquiry_count": inquiry_count,
        "application_count": application_count,
        "lease_signed_count": lease_signed_count,
        "average_days_on_market": average_days_on_market,
        "previous_period_inquiries": inquiry_count  # Mock previous period data
    }
    
    # Start background AI analysis
    background_tasks.add_task(
        analyze_tenant_demand,
        demand_data
    )
    
    return {"message": "Tenant demand analysis created successfully", "demand_id": demand.id}

@router.get("/assets/{asset_id}/monitoring", response_model=List[AssetMonitoringResponse])
async def get_asset_monitoring(asset_id: int, db: Session = Depends(get_db)):
    """Get asset monitoring data"""
    monitoring = db.query(AssetMonitoring).filter(AssetMonitoring.asset_id == asset_id).all()
    return monitoring

@router.post("/assets/{asset_id}/monitoring", response_model=AssetMonitoringResponse)
async def create_asset_monitoring(
    asset_id: int,
    property_condition_score: float,
    market_performance_score: float,
    financial_performance_score: float,
    occupancy_rate: float,
    market_rent_trend: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create asset monitoring record"""
    
    # Verify asset exists
    asset = db.query(PostAcquisitionAsset).filter(PostAcquisitionAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Post-acquisition asset not found")
    
    # Calculate overall score
    overall_score = (property_condition_score + market_performance_score + financial_performance_score) / 3
    
    # Create monitoring record
    monitoring = AssetMonitoring(
        asset_id=asset_id,
        monitoring_date=datetime.utcnow(),
        property_condition_score=property_condition_score,
        market_performance_score=market_performance_score,
        financial_performance_score=financial_performance_score,
        overall_score=overall_score,
        occupancy_rate=occupancy_rate,
        market_rent_trend=market_rent_trend,
        created_by=1
    )
    
    db.add(monitoring)
    db.commit()
    db.refresh(monitoring)
    
    return monitoring

@router.get("/stats/")
async def get_post_acquisition_stats(db: Session = Depends(get_db)):
    """Get post-acquisition statistics"""
    total_assets = db.query(PostAcquisitionAsset).count()
    active_assets = db.query(PostAcquisitionAsset).filter(PostAcquisitionAsset.status == AssetStatus.ACTIVE).count()
    under_renovation = db.query(PostAcquisitionAsset).filter(PostAcquisitionAsset.status == AssetStatus.UNDER_RENOVATION).count()
    leased_assets = db.query(PostAcquisitionAsset).filter(PostAcquisitionAsset.status == AssetStatus.LEASED).count()
    
    # Calculate average performance
    assets_with_scores = db.query(PostAcquisitionAsset).filter(PostAcquisitionAsset.performance_score.isnot(None)).all()
    avg_performance_score = sum(a.performance_score for a in assets_with_scores) / len(assets_with_scores) if assets_with_scores else 0
    avg_risk_score = sum(a.risk_score for a in assets_with_scores) / len(assets_with_scores) if assets_with_scores else 0
    avg_opportunity_score = sum(a.opportunity_score for a in assets_with_scores) / len(assets_with_scores) if assets_with_scores else 0
    
    # Renovation projects
    total_projects = db.query(RenovationProject).count()
    completed_projects = db.query(RenovationProject).filter(RenovationProject.status == RenovationStatus.COMPLETED).count()
    in_progress_projects = db.query(RenovationProject).filter(RenovationProject.status == RenovationStatus.IN_PROGRESS).count()
    
    # Refinancing opportunities
    total_opportunities = db.query(RefinancingOpportunity).count()
    eligible_opportunities = db.query(RefinancingOpportunity).filter(RefinancingOpportunity.status == RefinancingStatus.ELIGIBLE).count()
    
    return {
        "total_assets": total_assets,
        "active_assets": active_assets,
        "under_renovation": under_renovation,
        "leased_assets": leased_assets,
        "avg_performance_score": round(avg_performance_score, 1),
        "avg_risk_score": round(avg_risk_score, 1),
        "avg_opportunity_score": round(avg_opportunity_score, 1),
        "total_renovation_projects": total_projects,
        "completed_projects": completed_projects,
        "in_progress_projects": in_progress_projects,
        "total_refinancing_opportunities": total_opportunities,
        "eligible_opportunities": eligible_opportunities
    }
