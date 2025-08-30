"""
AI Insights API endpoints for Janus Prop AI Backend

This module provides endpoints for AI-generated property insights and analysis.
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from pydantic import BaseModel, Field

from core.database import get_db_session
from core.redis_client import cache_get, cache_set, cache_delete, publish_event
from core.websocket_manager import get_websocket_manager

router = APIRouter()

# Pydantic models
class PropertyInsight(BaseModel):
    """Property insight model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    property_id: str
    insight_type: str  # "market_analysis", "investment_potential", "risk_assessment", "comparison"
    title: str
    description: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    ai_model: str  # "gemini", "openai", "anthropic"
    generated_date: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True

class PropertyAnalysis(BaseModel):
    """Property analysis model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    property_id: str
    analysis_type: str  # "comprehensive", "quick", "investment", "market"
    summary: str
    key_findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)
    market_trends: List[str] = Field(default_factory=list)
    comparable_properties: List[str] = Field(default_factory=list)
    ai_generated: bool = True
    generated_date: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(ge=0.0, le=1.0)

class AIInsightRequest(BaseModel):
    """AI insight generation request."""
    property_id: str
    insight_type: str
    additional_context: Optional[str] = None
    ai_model: Optional[str] = "gemini"
    priority: str = "normal"  # "low", "normal", "high", "urgent"

class AIInsightResponse(BaseModel):
    """AI insight response model."""
    insights: List[PropertyInsight]
    analyses: List[PropertyAnalysis]
    total: int
    page: int
    page_size: int

# Mock data for development
MOCK_PROPERTY_INSIGHTS = [
    PropertyInsight(
        property_id="prop_001",
        insight_type="market_analysis",
        title="Strong Market Growth in Downtown Area",
        description="Property shows excellent potential for appreciation based on recent market trends and development plans in the downtown area.",
        confidence_score=0.87,
        ai_model="gemini",
        tags=["market_growth", "downtown", "appreciation"],
        metadata={
            "market_growth_rate": "12.5%",
            "development_projects": 3,
            "infrastructure_score": 8.2
        }
    ),
    PropertyInsight(
        property_id="prop_001",
        insight_type="investment_potential",
        title="High ROI Potential for Rental Investment",
        description="Current market conditions suggest strong rental demand with potential 8-12% annual return on investment.",
        confidence_score=0.92,
        ai_model="gemini",
        tags=["rental", "roi", "investment"],
        metadata={
            "estimated_roi": "8-12%",
            "rental_demand": "high",
            "vacancy_rate": "2.1%"
        }
    ),
    PropertyInsight(
        property_id="prop_002",
        insight_type="risk_assessment",
        title="Moderate Flood Risk in Area",
        description="Property is located in a moderate flood risk zone. Consider additional insurance and mitigation measures.",
        confidence_score=0.78,
        ai_model="gemini",
        tags=["flood_risk", "insurance", "mitigation"],
        metadata={
            "flood_risk_level": "moderate",
            "insurance_impact": "+15%",
            "mitigation_cost": "$5,000-8,000"
        }
    )
]

MOCK_PROPERTY_ANALYSES = [
    PropertyAnalysis(
        property_id="prop_001",
        analysis_type="comprehensive",
        summary="Excellent investment opportunity with strong market fundamentals and growth potential.",
        key_findings=[
            "Property value has increased 15% over the last 2 years",
            "Strong rental demand in the area",
            "New infrastructure projects planned nearby"
        ],
        recommendations=[
            "Consider purchasing for long-term investment",
            "Explore rental income opportunities",
            "Monitor local development plans"
        ],
        risk_factors=[
            "Market volatility in luxury segment",
            "Potential interest rate increases"
        ],
        market_trends=[
            "Downtown area experiencing rapid growth",
            "Tech companies expanding in the region",
            "Public transportation improvements planned"
        ],
        comparable_properties=["prop_003", "prop_004"],
        confidence_score=0.89
    ),
    PropertyAnalysis(
        property_id="prop_002",
        analysis_type="investment",
        summary="Moderate investment potential with some risk factors to consider.",
        key_findings=[
            "Stable property values in the area",
            "Good rental yield potential",
            "Some environmental concerns"
        ],
        recommendations=[
            "Conduct thorough environmental assessment",
            "Consider insurance implications",
            "Evaluate long-term holding strategy"
        ],
        risk_factors=[
            "Flood risk in the area",
            "Environmental contamination concerns",
            "Limited appreciation potential"
        ],
        market_trends=[
            "Stable market conditions",
            "Growing demand for affordable housing",
            "Infrastructure improvements planned"
        ],
        comparable_properties=["prop_005", "prop_006"],
        confidence_score=0.76
    )
]

@router.get("/", response_model=AIInsightResponse)
async def get_ai_insights(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    property_id: Optional[str] = None,
    insight_type: Optional[str] = None,
    ai_model: Optional[str] = None,
    analysis_type: Optional[str] = None
):
    """Get AI insights and analyses with filtering and pagination."""
    try:
        # Filter insights
        filtered_insights = MOCK_PROPERTY_INSIGHTS.copy()
        if property_id:
            filtered_insights = [i for i in filtered_insights if i.property_id == property_id]
        if insight_type:
            filtered_insights = [i for i in filtered_insights if i.insight_type == insight_type]
        if ai_model:
            filtered_insights = [i for i in filtered_insights if i.ai_model == ai_model]
        
        # Filter analyses
        filtered_analyses = MOCK_PROPERTY_ANALYSES.copy()
        if property_id:
            filtered_analyses = [a for a in filtered_analyses if a.property_id == property_id]
        if analysis_type:
            filtered_analyses = [a for a in filtered_analyses if a.analysis_type == analysis_type]
        
        # Combine and paginate
        all_items = filtered_insights + filtered_analyses
        total = len(all_items)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = all_items[start_idx:end_idx]
        
        # Separate insights and analyses for response
        page_insights = [item for item in paginated_items if isinstance(item, PropertyInsight)]
        page_analyses = [item for item in paginated_items if isinstance(item, PropertyAnalysis)]
        
        return AIInsightResponse(
            insights=page_insights,
            analyses=page_analyses,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch AI insights: {str(e)}")

@router.get("/insights", response_model=List[PropertyInsight])
async def get_property_insights(
    property_id: Optional[str] = None,
    insight_type: Optional[str] = None,
    ai_model: Optional[str] = None
):
    """Get property insights with optional filtering."""
    try:
        filtered_insights = MOCK_PROPERTY_INSIGHTS.copy()
        
        if property_id:
            filtered_insights = [i for i in filtered_insights if i.property_id == property_id]
        if insight_type:
            filtered_insights = [i for i in filtered_insights if i.insight_type == insight_type]
        if ai_model:
            filtered_insights = [i for i in filtered_insights if i.ai_model == ai_model]
        
        # Sort by confidence score (highest first)
        filtered_insights.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return filtered_insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch property insights: {str(e)}")

@router.get("/analyses", response_model=List[PropertyAnalysis])
async def get_property_analyses(
    property_id: Optional[str] = None,
    analysis_type: Optional[str] = None
):
    """Get property analyses with optional filtering."""
    try:
        filtered_analyses = MOCK_PROPERTY_ANALYSES.copy()
        
        if property_id:
            filtered_analyses = [a for a in filtered_analyses if a.property_id == property_id]
        if analysis_type:
            filtered_analyses = [a for a in filtered_analyses if a.analysis_type == analysis_type]
        
        # Sort by confidence score (highest first)
        filtered_analyses.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return filtered_analyses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch property analyses: {str(e)}")

@router.get("/insights/{insight_id}", response_model=PropertyInsight)
async def get_property_insight(insight_id: str):
    """Get a specific property insight by ID."""
    try:
        # Try to get from cache first
        cached_insight = await cache_get(f"insight:{insight_id}")
        if cached_insight:
            return PropertyInsight(**cached_insight)
        
        # Find insight in mock data
        insight_obj = None
        for insight in MOCK_PROPERTY_INSIGHTS:
            if insight.id == insight_id:
                insight_obj = insight
                break
        
        if not insight_obj:
            raise HTTPException(status_code=404, detail="Property insight not found")
        
        # Cache the insight
        await cache_set(f"insight:{insight_id}", insight_obj.dict(), expire=1800)
        
        return insight_obj
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch property insight: {str(e)}")

@router.get("/analyses/{analysis_id}", response_model=PropertyAnalysis)
async def get_property_analysis(analysis_id: str):
    """Get a specific property analysis by ID."""
    try:
        # Try to get from cache first
        cached_analysis = await cache_get(f"analysis:{analysis_id}")
        if cached_analysis:
            return PropertyAnalysis(**cached_analysis)
        
        # Find analysis in mock data
        analysis_obj = None
        for analysis in MOCK_PROPERTY_ANALYSES:
            if analysis.id == analysis_id:
                analysis_obj = analysis
                break
        
        if not analysis_obj:
            raise HTTPException(status_code=404, detail="Property analysis not found")
        
        # Cache the analysis
        await cache_set(f"analysis:{analysis_id}", analysis_obj.dict(), expire=1800)
        
        return analysis_obj
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch property analysis: {str(e)}")

@router.post("/generate", response_model=Dict[str, Any])
async def generate_ai_insight(
    request: AIInsightRequest,
    background_tasks: BackgroundTasks
):
    """Generate new AI insights for a property."""
    try:
        # This would typically call the AI agent manager to generate insights
        # For now, we'll simulate the process
        
        # Simulate AI processing time
        await asyncio.sleep(1)
        
        # Create mock insight
        new_insight = PropertyInsight(
            property_id=request.property_id,
            insight_type=request.insight_type,
            title=f"AI Generated {request.insight_type.title()}",
            description=f"AI-generated insight for property {request.property_id} using {request.ai_model} model.",
            confidence_score=0.85,
            ai_model=request.ai_model,
            tags=[request.insight_type, request.ai_model],
            metadata={
                "request_context": request.additional_context,
                "priority": request.priority,
                "generation_time": datetime.utcnow().isoformat()
            }
        )
        
        # Add to mock data
        MOCK_PROPERTY_INSIGHTS.append(new_insight)
        
        # Cache the insight
        await cache_set(f"insight:{new_insight.id}", new_insight.dict(), expire=1800)
        
        # Publish real-time update
        await publish_event(
            f"property:{request.property_id}",
            "ai_insight_generated",
            new_insight.dict()
        )
        
        # Send WebSocket update
        websocket_manager = get_websocket_manager()
        await websocket_manager.send_property_update(request.property_id, {
            "type": "ai_insight_generated",
            "insight": new_insight.dict()
        })
        
        return {
            "success": True,
            "message": "AI insight generated successfully",
            "insight_id": new_insight.id,
            "insight": new_insight.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate AI insight: {str(e)}")

@router.post("/insights", response_model=PropertyInsight)
async def create_property_insight(
    insight_data: PropertyInsight,
    background_tasks: BackgroundTasks
):
    """Create a new property insight."""
    try:
        # Set ID and timestamps
        insight_data.id = str(uuid4())
        insight_data.generated_date = datetime.utcnow()
        
        # Add to mock insights
        MOCK_PROPERTY_INSIGHTS.append(insight_data)
        
        # Cache the insight
        await cache_set(f"insight:{insight_data.id}", insight_data.dict(), expire=1800)
        
        # Publish real-time update
        await publish_event(
            f"property:{insight_data.property_id}",
            "insight_created",
            insight_data.dict()
        )
        
        return insight_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create property insight: {str(e)}")

@router.post("/analyses", response_model=PropertyAnalysis)
async def create_property_analysis(
    analysis_data: PropertyAnalysis,
    background_tasks: BackgroundTasks
):
    """Create a new property analysis."""
    try:
        # Set ID and timestamps
        analysis_data.id = str(uuid4())
        analysis_data.generated_date = datetime.utcnow()
        analysis_data.last_updated = datetime.utcnow()
        
        # Add to mock analyses
        MOCK_PROPERTY_ANALYSES.append(analysis_data)
        
        # Cache the analysis
        await cache_set(f"analysis:{analysis_data.id}", analysis_data.dict(), expire=1800)
        
        # Publish real-time update
        await publish_event(
            f"property:{analysis_data.property_id}",
            "analysis_created",
            analysis_data.dict()
        )
        
        return analysis_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create property analysis: {str(e)}")

@router.put("/insights/{insight_id}", response_model=PropertyInsight)
async def update_property_insight(
    insight_id: str,
    insight_update: Dict[str, Any]
):
    """Update a property insight."""
    try:
        # Find insight in mock data
        insight_index = None
        for i, insight in enumerate(MOCK_PROPERTY_INSIGHTS):
            if insight.id == insight_id:
                insight_index = i
                break
        
        if insight_index is None:
            raise HTTPException(status_code=404, detail="Property insight not found")
        
        # Update insight
        insight_obj = MOCK_PROPERTY_INSIGHTS[insight_index]
        for field, value in insight_update.items():
            if hasattr(insight_obj, field):
                setattr(insight_obj, field, value)
        
        # Update cache
        await cache_set(f"insight:{insight_id}", insight_obj.dict(), expire=1800)
        
        # Publish real-time update
        await publish_event(
            f"insight:{insight_id}",
            "insight_updated",
            insight_obj.dict()
        )
        
        return insight_obj
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update property insight: {str(e)}")

@router.delete("/insights/{insight_id}")
async def delete_property_insight(insight_id: str):
    """Delete a property insight."""
    try:
        # Find and remove insight
        insight_index = None
        for i, insight in enumerate(MOCK_PROPERTY_INSIGHTS):
            if insight.id == insight_id:
                insight_index = i
                break
        
        if insight_index is None:
            raise HTTPException(status_code=404, detail="Property insight not found")
        
        removed_insight = MOCK_PROPERTY_INSIGHTS.pop(insight_index)
        
        # Remove from cache
        await cache_delete(f"insight:{insight_id}")
        
        # Publish real-time update
        await publish_event(
            "insights",
            "insight_deleted",
            {"insight_id": insight_id}
        )
        
        return {"success": True, "message": "Property insight deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete property insight: {str(e)}")

@router.get("/summary")
async def get_ai_insights_summary():
    """Get summary of AI insights and analyses."""
    try:
        # Count insights by type
        insight_type_counts = {}
        for insight in MOCK_PROPERTY_INSIGHTS:
            insight_type_counts[insight.insight_type] = insight_type_counts.get(insight.insight_type, 0) + 1
        
        # Count analyses by type
        analysis_type_counts = {}
        for analysis in MOCK_PROPERTY_ANALYSES:
            analysis_type_counts[analysis.analysis_type] = analysis_type_counts.get(analysis.analysis_type, 0) + 1
        
        # Count by AI model
        ai_model_counts = {}
        for insight in MOCK_PROPERTY_INSIGHTS:
            ai_model_counts[insight.ai_model] = ai_model_counts.get(insight.ai_model, 0) + 1
        
        # Calculate average confidence scores
        avg_insight_confidence = sum(i.confidence_score for i in MOCK_PROPERTY_INSIGHTS) / len(MOCK_PROPERTY_INSIGHTS) if MOCK_PROPERTY_INSIGHTS else 0
        avg_analysis_confidence = sum(a.confidence_score for a in MOCK_PROPERTY_ANALYSES) / len(MOCK_PROPERTY_ANALYSES) if MOCK_PROPERTY_ANALYSES else 0
        
        return {
            "total_insights": len(MOCK_PROPERTY_INSIGHTS),
            "total_analyses": len(MOCK_PROPERTY_ANALYSES),
            "insight_type_breakdown": insight_type_counts,
            "analysis_type_breakdown": analysis_type_counts,
            "ai_model_breakdown": ai_model_counts,
            "average_insight_confidence": round(avg_insight_confidence, 3),
            "average_analysis_confidence": round(avg_analysis_confidence, 3),
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate AI insights summary: {str(e)}")

@router.get("/trends")
async def get_ai_insights_trends(
    days: int = Query(30, ge=1, le=365)
):
    """Get trends in AI insights over time."""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Filter insights by date range
        recent_insights = [
            insight for insight in MOCK_PROPERTY_INSIGHTS
            if start_date <= insight.generated_date <= end_date
        ]
        
        # Group by date
        daily_counts = {}
        for insight in recent_insights:
            date_key = insight.generated_date.date().isoformat()
            daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
        
        # Sort by date
        sorted_dates = sorted(daily_counts.keys())
        
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_insights_generated": len(recent_insights),
            "daily_trends": [{"date": date, "count": daily_counts[date]} for date in sorted_dates],
            "average_daily_insights": len(recent_insights) / days if days > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate AI insights trends: {str(e)}")
