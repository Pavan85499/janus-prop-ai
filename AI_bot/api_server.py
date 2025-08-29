"""
FastAPI Server for Real Estate AI System

This server provides REST endpoints for:
- AI Insights generation
- Data integration operations
- Feedback collection
- Learning metrics
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import asyncio
import structlog
from datetime import datetime

from agents.ai_insights_agent import AIInsightsAgent, PropertyAnalysis
from agents.gemini_ai_agent import GeminiAIAgent, GeminiPropertyAnalysis
from agents.attom_data_agent import ATTOMDataAgent, ATTOMPropertyData
from agents.data_integration_agent import DataIntegrationAgent, PropertyData
from agents.feedback_learning_agent import FeedbackLearningAgent, UserFeedback
from agents.base_agent import AgentConfig

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="Janus Prop AI API",
    description="Real Estate AI Agent System API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
ai_insights_agent = None
gemini_ai_agent = None
attom_data_agent = None
data_integration_agent = None
feedback_learning_agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize agents on startup."""
    global ai_insights_agent, gemini_ai_agent, attom_data_agent, data_integration_agent, feedback_learning_agent
    
    logger.info("Initializing AI agents...")
    
    # Initialize AI Insights Agent (OpenAI)
    ai_config = AgentConfig(
        name="AI Insights Agent",
        description="Provides explainable AI insights using OpenAI",
        model="gpt-4",
        temperature=0.1,
        max_tokens=4000,
        timeout=60
    )
    ai_insights_agent = AIInsightsAgent(ai_config)
    await ai_insights_agent.start()
    
    # Initialize Gemini AI Agent
    gemini_config = AgentConfig(
        name="Gemini AI Agent",
        description="Provides AI insights using Google Gemini",
        model="gemini-pro",
        temperature=0.1,
        max_tokens=4000,
        timeout=60,
        metadata={
            "gemini_api_key": "your_gemini_api_key_here"  # Set via environment variable
        }
    )
    gemini_ai_agent = GeminiAIAgent(gemini_config)
    await gemini_ai_agent.start()
    
    # Initialize ATTOM Data Agent
    attom_config = AgentConfig(
        name="ATTOM Data Agent",
        description="Integrates with ATTOM Real Estate Data",
        model="api_integration",
        temperature=0.0,
        max_tokens=1000,
        timeout=45,
        metadata={
            "attom_api_key": "your_attom_api_key_here",  # Set via environment variable
            "attom_base_url": "https://api.attomdata.com/v3.0",
            "rate_limit": 100,
            "timeout": 30
        }
    )
    attom_data_agent = ATTOMDataAgent(attom_config)
    await attom_data_agent.start()
    
    # Initialize Data Integration Agent
    data_config = AgentConfig(
        name="Data Integration Agent",
        description="Handles data integration from multiple sources",
        model="gpt-4",
        temperature=0.1,
        max_tokens=4000,
        timeout=60
    )
    data_integration_agent = DataIntegrationAgent(data_config)
    await data_integration_agent.start()
    
    # Initialize Feedback & Learning Agent
    feedback_config = AgentConfig(
        name="Feedback & Learning Agent",
        description="Implements continuous learning",
        model="gpt-4",
        temperature=0.1,
        max_tokens=4000,
        timeout=60
    )
    feedback_learning_agent = FeedbackLearningAgent(feedback_config)
    await feedback_learning_agent.start()
    
    logger.info("All agents initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown agents on shutdown."""
    global ai_insights_agent, data_integration_agent, feedback_learning_agent
    
    logger.info("Shutting down AI agents...")
    
    if ai_insights_agent:
        await ai_insights_agent.shutdown()
    if data_integration_agent:
        await data_integration_agent.shutdown()
    if feedback_learning_agent:
        await feedback_learning_agent.shutdown()
    
    logger.info("All agents shut down successfully")

# Pydantic models for API requests/responses
class PropertyAnalysisRequest(BaseModel):
    property_data: Dict[str, Any]
    include_insights: List[str] = ["market_opportunity", "risk_assessment", "investment_potential"]

class PropertySearchRequest(BaseModel):
    criteria: Dict[str, Any]
    limit: int = 50

class FeedbackRequest(BaseModel):
    user_id: str
    property_id: str
    insight_id: str
    feedback_type: str
    rating: Optional[int] = None
    comment: Optional[str] = None
    action_taken: Optional[str] = None

class DataSourceRequest(BaseModel):
    source_config: Dict[str, Any]

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": {
            "ai_insights": ai_insights_agent is not None,
            "data_integration": data_integration_agent is not None,
            "feedback_learning": feedback_learning_agent is not None
        }
    }

# AI Insights endpoints
@app.post("/api/ai-insights/analyze")
async def analyze_property(request: PropertyAnalysisRequest):
    """Analyze a property and generate AI insights."""
    try:
        if not ai_insights_agent:
            raise HTTPException(status_code=503, detail="AI Insights Agent not available")
        
        response = await ai_insights_agent.process_request({
            "type": "property_analysis",
            "property_data": request.property_data
        })
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except Exception as e:
        logger.error("Error analyzing property", error=str(e))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/ai-insights/capabilities")
async def get_ai_insights_capabilities():
    """Get AI Insights Agent capabilities."""
    try:
        if not ai_insights_agent:
            raise HTTPException(status_code=503, detail="AI Insights Agent not available")
        
        capabilities = await ai_insights_agent.get_capabilities()
        return capabilities
        
    except Exception as e:
        logger.error("Error getting capabilities", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")

# Data Integration endpoints
@app.post("/api/data-integration/search")
async def search_properties(request: PropertySearchRequest):
    """Search for properties using data integration."""
    try:
        if not data_integration_agent:
            raise HTTPException(status_code=503, detail="Data Integration Agent not available")
        
        response = await data_integration_agent.process_request({
            "type": "search_properties",
            "criteria": request.criteria,
            "limit": request.limit
        })
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except Exception as e:
        logger.error("Error searching properties", error=str(e))
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/data-integration/sync")
async def sync_data_source(source_id: str):
    """Sync data from a specific source."""
    try:
        if not data_integration_agent:
            raise HTTPException(status_code=503, detail="Data Integration Agent not available")
        
        response = await data_integration_agent.process_request({
            "type": "sync_data_source",
            "source_id": source_id
        })
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except Exception as e:
        logger.error("Error syncing data source", error=str(e))
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@app.post("/api/data-integration/add-source")
async def add_data_source(request: DataSourceRequest):
    """Add a new data source."""
    try:
        if not data_integration_agent:
            raise HTTPException(status_code=503, detail="Data Integration Agent not available")
        
        response = await data_integration_agent.process_request({
            "type": "add_data_source",
            "source_config": request.source_config
        })
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except Exception as e:
        logger.error("Error adding data source", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to add data source: {str(e)}")

@app.get("/api/data-integration/status")
async def get_data_integration_status():
    """Get data integration status and health."""
    try:
        if not data_integration_agent:
            raise HTTPException(status_code=503, detail="Data Integration Agent not available")
        
        status = await data_integration_agent.health_check()
        return status
        
    except Exception as e:
        logger.error("Error getting data integration status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

# Feedback & Learning endpoints
@app.post("/api/feedback/collect")
async def collect_feedback(request: FeedbackRequest):
    """Collect user feedback on AI insights."""
    try:
        if not feedback_learning_agent:
            raise HTTPException(status_code=503, detail="Feedback & Learning Agent not available")
        
        response = await feedback_learning_agent.process_request({
            "type": "collect_feedback",
            "feedback": request.dict()
        })
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except Exception as e:
        logger.error("Error collecting feedback", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to collect feedback: {str(e)}")

@app.post("/api/feedback/track-accuracy")
async def track_prediction_accuracy(accuracy_data: Dict[str, Any]):
    """Track the accuracy of AI predictions."""
    try:
        if not feedback_learning_agent:
            raise HTTPException(status_code=503, detail="Feedback & Learning Agent not available")
        
        response = await feedback_learning_agent.process_request({
            "type": "track_prediction_accuracy",
            "accuracy_data": accuracy_data
        })
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except Exception as e:
        logger.error("Error tracking prediction accuracy", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to track accuracy: {str(e)}")

@app.get("/api/feedback/learning-metrics")
async def get_learning_metrics(agent_id: str = "all", date_range: int = 30):
    """Get learning metrics for continuous improvement."""
    try:
        if not feedback_learning_agent:
            raise HTTPException(status_code=503, detail="Feedback & Learning Agent not available")
        
        response = await feedback_learning_agent.process_request({
            "type": "generate_learning_metrics",
            "agent_id": agent_id,
            "date_range": date_range
        })
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except Exception as e:
        logger.error("Error getting learning metrics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get learning metrics: {str(e)}")

@app.get("/api/feedback/agent-performance")
async def get_agent_performance(agent_id: str):
    """Get performance metrics for a specific agent."""
    try:
        if not feedback_learning_agent:
            raise HTTPException(status_code=503, detail="Feedback & Learning Agent not available")
        
        response = await feedback_learning_agent.process_request({
            "type": "get_agent_performance",
            "agent_id": agent_id
        })
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except Exception as e:
        logger.error("Error getting agent performance", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get agent performance: {str(e)}")

# Gemini AI endpoints
@app.post("/api/gemini/analyze-property")
async def analyze_property_with_gemini(request: Dict[str, Any]):
    """Analyze a property using Gemini AI."""
    try:
        if not gemini_ai_agent:
            raise HTTPException(status_code=503, detail="Gemini AI Agent not available")
        
        response = await gemini_ai_agent.process_request({
            "type": "analyze_property",
            "property_data": request.get("property_data", {})
        })
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except Exception as e:
        logger.error("Error analyzing property with Gemini", error=str(e))
        raise HTTPException(status_code=500, detail=f"Gemini analysis failed: {str(e)}")

@app.post("/api/gemini/generate-insights")
async def generate_insights_with_gemini(request: Dict[str, Any]):
    """Generate insights using Gemini AI."""
    try:
        if not gemini_ai_agent:
            raise HTTPException(status_code=503, detail="Gemini AI Agent not available")
        
        response = await gemini_ai_agent.process_request({
            "type": "generate_insights",
            "insight_type": request.get("insight_type", "general"),
            "property_context": request.get("property_context", {})
        })
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except Exception as e:
        logger.error("Error generating insights with Gemini", error=str(e))
        raise HTTPException(status_code=500, detail=f"Gemini insight generation failed: {str(e)}")

@app.post("/api/gemini/market-analysis")
async def perform_market_analysis_with_gemini(request: Dict[str, Any]):
    """Perform market analysis using Gemini AI."""
    try:
        if not gemini_ai_agent:
            raise HTTPException(status_code=503, detail="Gemini AI Agent not available")
        
        response = await gemini_ai_agent.process_request({
            "type": "market_analysis",
            "location": request.get("location", ""),
            "market_data": request.get("market_data", {})
        })
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except Exception as e:
        logger.error("Error performing market analysis with Gemini", error=str(e))
        raise HTTPException(status_code=500, detail=f"Gemini market analysis failed: {str(e)}")

# ATTOM Data endpoints
@app.get("/api/attom/property/{address}")
async def get_attom_property_data(address: str):
    """Get property data from ATTOM."""
    try:
        if not attom_data_agent:
            raise HTTPException(status_code=503, detail="ATTOM Data Agent not available")
        
        response = await attom_data_agent.process_request({
            "type": "get_property_data",
            "address": address
        })
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except Exception as e:
        logger.error("Error getting ATTOM property data", error=str(e))
        raise HTTPException(status_code=500, detail=f"ATTOM data retrieval failed: {str(e)}")

@app.post("/api/attom/search")
async def search_attom_properties(request: Dict[str, Any]):
    """Search properties using ATTOM API."""
    try:
        if not attom_data_agent:
            raise HTTPException(status_code=503, detail="ATTOM Data Agent not available")
        
        response = await attom_data_agent.process_request({
            "type": "search_properties",
            "criteria": request.get("criteria", {})
        })
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except Exception as e:
        logger.error("Error searching ATTOM properties", error=str(e))
        raise HTTPException(status_code=500, detail=f"ATTOM property search failed: {str(e)}")

@app.get("/api/attom/market/{location}")
async def get_attom_market_data(location: str):
    """Get market data from ATTOM."""
    try:
        if not attom_data_agent:
            raise HTTPException(status_code=503, detail="ATTOM Data Agent not available")
        
        response = await attom_data_agent.process_request({
            "type": "get_market_data",
            "location": location
        })
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except Exception as e:
        logger.error("Error getting ATTOM market data", error=str(e))
        raise HTTPException(status_code=500, detail=f"ATTOM market data retrieval failed: {str(e)}")

@app.post("/api/attom/comparables")
async def get_attom_comparables(request: Dict[str, Any]):
    """Get comparable sales from ATTOM."""
    try:
        if not attom_data_agent:
            raise HTTPException(status_code=503, detail="ATTOM Data Agent not available")
        
        response = await attom_data_agent.process_request({
            "type": "get_comparable_sales",
            "property_data": request.get("property_data", {}),
            "radius": request.get("radius", 0.5),
            "limit": request.get("limit", 10)
        })
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except Exception as e:
        logger.error("Error getting ATTOM comparables", error=str(e))
        raise HTTPException(status_code=500, detail=f"ATTOM comparables retrieval failed: {str(e)}")

@app.get("/api/attom/foreclosure/{location}")
async def get_attom_foreclosure_data(location: str):
    """Get foreclosure data from ATTOM."""
    try:
        if not attom_data_agent:
            raise HTTPException(status_code=503, detail="ATTOM Data Agent not available")
        
        response = await attom_data_agent.process_request({
            "type": "get_foreclosure_data",
            "location": location
        })
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except Exception as e:
        logger.error("Error getting ATTOM foreclosure data", error=str(e))
        raise HTTPException(status_code=500, detail=f"ATTOM foreclosure data retrieval failed: {str(e)}")

# System endpoints
@app.get("/api/system/status")
async def get_system_status():
    """Get overall system status."""
    try:
        status = {
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "agents": {}
        }
        
        if ai_insights_agent:
            status["agents"]["ai_insights"] = await ai_insights_agent.health_check()
        
        if data_integration_agent:
            status["agents"]["data_integration"] = await data_integration_agent.health_check()
        
        if feedback_learning_agent:
            status["agents"]["feedback_learning"] = await feedback_learning_agent.health_check()
        
        return status
        
    except Exception as e:
        logger.error("Error getting system status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

# Agent Activity and Status endpoints
@app.get("/api/agents/activity")
async def get_agent_activity(limit: int = 50, agent_type: str = None):
    """Get recent agent activity and status updates."""
    try:
        activities = []
        
        # Get system status
        system_status = await get_system_status()
        
        # Get individual agent statuses
        if ai_insights_agent:
            ai_status = await ai_insights_agent.health_check()
            activities.append({
                "id": f"ai_insights_{datetime.utcnow().timestamp()}",
                "agent": "Eden",
                "message": "AI Insights analysis active (OpenAI)",
                "status": "in-progress" if ai_status.get("status") == "healthy" else "alert",
                "timestamp": "Just now",
                "details": f"Processing AI insights with {ai_status.get('status', 'unknown')} status using OpenAI",
                "agent_type": "ai_insights"
            })
        
        if gemini_ai_agent:
            gemini_status = await gemini_ai_agent.health_check()
            activities.append({
                "id": f"gemini_ai_{datetime.utcnow().timestamp()}",
                "agent": "Gemini",
                "message": "Gemini AI analysis active",
                "status": "in-progress" if gemini_status.get("status") == "healthy" else "alert",
                "timestamp": "Just now",
                "details": f"Processing AI insights with {gemini_status.get('status', 'unknown')} status using Google Gemini",
                "agent_type": "gemini_ai"
            })
        
        if attom_data_agent:
            attom_status = await attom_data_agent.health_check()
            activities.append({
                "id": f"attom_data_{datetime.utcnow().timestamp()}",
                "agent": "Elysia",
                "message": "ATTOM data integration active",
                "status": "in-progress" if attom_status.get("status") == "healthy" else "alert",
                "timestamp": "Just now",
                "details": f"Managing ATTOM real estate data with {attom_status.get('status', 'unknown')} status",
                "agent_type": "attom_data"
            })
        
        if data_integration_agent:
            data_status = await data_integration_agent.health_check()
            activities.append({
                "id": f"data_integration_{datetime.utcnow().timestamp()}",
                "agent": "Elysia",
                "message": "Data integration active",
                "status": "in-progress" if data_status.get("status") == "healthy" else "alert",
                "timestamp": "Just now",
                "details": f"Managing data sources with {data_status.get('status', 'unknown')} status",
                "agent_type": "data_integration"
            })
        
        if feedback_learning_agent:
            feedback_status = await feedback_learning_agent.health_check()
            activities.append({
                "id": f"feedback_learning_{datetime.utcnow().timestamp()}",
                "agent": "Spring",
                "message": "Learning and feedback active",
                "status": "in-progress" if feedback_status.get("status") == "healthy" else "alert",
                "timestamp": "Just now",
                "details": f"Processing feedback with {feedback_status.get('status', 'unknown')} status",
                "agent_type": "feedback_learning"
            })
        
        # Add some mock activities for demonstration
        mock_activities = [
            {
                "id": "mock_1",
                "agent": "Orion",
                "message": "Analyzing 47 pre-foreclosure homes in Brooklyn...",
                "status": "in-progress",
                "timestamp": "2 min ago",
                "details": "Scanning MLS data, court filings, and auction schedules for distressed properties across 15 zip codes",
                "agent_type": "market_research"
            },
            {
                "id": "mock_2",
                "agent": "Celestia",
                "message": "Generated 3 new investment reports",
                "status": "completed",
                "timestamp": "5 min ago",
                "details": "Created comprehensive analysis reports for properties on Oak Street, Maple Ave, and Pine Road with ROI projections",
                "agent_type": "document_processing"
            },
            {
                "id": "mock_3",
                "agent": "Valyria",
                "message": "Market forecast updated for Queens zip codes",
                "status": "completed",
                "timestamp": "8 min ago",
                "details": "Analyzed migration patterns, rental demand trends, and price movement predictions for 23 neighborhoods",
                "agent_type": "market_research"
            },
            {
                "id": "mock_4",
                "agent": "Atelius",
                "message": "Legal risk assessment complete",
                "status": "completed",
                "timestamp": "12 min ago",
                "details": "Reviewed legal documentation for 15 properties and identified 2 with potential title issues",
                "agent_type": "legal_analysis"
            },
            {
                "id": "mock_5",
                "agent": "Osiris",
                "message": "Financial modeling complete for 8 properties",
                "status": "completed",
                "timestamp": "15 min ago",
                "details": "Projected cash flows, redemption windows, and yield forecasts with 89% accuracy confidence",
                "agent_type": "financial_modeling"
            }
        ]
        
        activities.extend(mock_activities)
        
        # Filter by agent type if specified
        if agent_type:
            activities = [a for a in activities if a.get("agent_type") == agent_type]
        
        # Limit results
        activities = activities[:limit]
        
        return {
            "activities": activities,
            "summary": {
                "total_activities": len(activities),
                "active_tasks": len([a for a in activities if a["status"] == "in-progress"]),
                "completed_tasks": len([a for a in activities if a["status"] == "completed"]),
                "alerts": len([a for a in activities if a["status"] == "alert"]),
                "system_status": system_status
            }
        }
        
    except Exception as e:
        logger.error("Error getting agent activity", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get agent activity: {str(e)}")

@app.get("/api/agents/status")
async def get_agents_status():
    """Get detailed status of all agents."""
    try:
        agent_statuses = {}
        
        if ai_insights_agent:
            agent_statuses["ai_insights"] = {
                "name": "Eden",
                "status": await ai_insights_agent.health_check(),
                "capabilities": ["property_analysis", "insight_generation", "risk_assessment"],
                "last_activity": datetime.utcnow().isoformat()
            }
        
        if gemini_ai_agent:
            agent_statuses["gemini_ai"] = {
                "name": "Gemini",
                "status": await gemini_ai_agent.health_check(),
                "capabilities": ["ai_analysis", "insight_generation", "market_analysis", "investment_recommendation"],
                "last_activity": datetime.utcnow().isoformat()
            }
        
        if attom_data_agent:
            agent_statuses["attom_data"] = {
                "name": "Elysia",
                "status": await attom_data_agent.health_check(),
                "capabilities": ["property_data", "market_trends", "comparable_sales", "foreclosure_data"],
                "last_activity": datetime.utcnow().isoformat()
            }
        
        if data_integration_agent:
            agent_statuses["data_integration"] = {
                "name": "Elysia",
                "status": await data_integration_agent.health_check(),
                "capabilities": ["data_sync", "source_management", "quality_validation"],
                "last_activity": datetime.utcnow().isoformat()
            }
        
        if feedback_learning_agent:
            agent_statuses["feedback_learning"] = {
                "name": "Spring",
                "status": await feedback_learning_agent.health_check(),
                "capabilities": ["feedback_collection", "accuracy_tracking", "model_improvement"],
                "last_activity": datetime.utcnow().isoformat()
            }
        
        return {
            "agents": agent_statuses,
            "total_agents": len(agent_statuses),
            "healthy_agents": len([a for a in agent_statuses.values() if a["status"].get("status") == "healthy"]),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting agents status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get agents status: {str(e)}")

@app.post("/api/agents/activity/dismiss")
async def dismiss_activity(activity_id: str):
    """Dismiss a specific activity notification."""
    try:
        # In a real implementation, this would mark the activity as dismissed in the database
        # For now, we'll just return success
        return {
            "success": True,
            "message": f"Activity {activity_id} dismissed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error dismissing activity", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to dismiss activity: {str(e)}")

@app.get("/api/agents/activity/stream")
async def stream_agent_activity():
    """Stream real-time agent activity updates (WebSocket endpoint)."""
    # This would be implemented with WebSocket support
    # For now, return a message indicating WebSocket support is planned
    return {
        "message": "WebSocket streaming for real-time agent activity is planned for future implementation",
        "current_support": "Polling via /api/agents/activity endpoint"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
