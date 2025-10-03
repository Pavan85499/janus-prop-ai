"""
Main API router for Janus Prop AI Backend

This module provides all the REST API endpoints for the real estate AI system.
"""

from fastapi import APIRouter

from .endpoints import (
    agents,
    properties,
    market_data,
    leads,
    ai_insights,
    websocket,
    health,
    supabase,
    investment_opportunities,
    real_estate_apis,
    demo_schedule,
    property_scanner,
    documents,
    underwriting,
    legal_compliance,
    investment_committee,
    execution_closing,
    post_acquisition,
    subscription,
    ai_agents,
    property_intelligence,
    analytics,
    automation,
    ask,
    agent_management
)

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    agents.router,
    prefix="/agents",
    tags=["agents"]
)

api_router.include_router(
    properties.router,
    prefix="/properties",
    tags=["properties"]
)

api_router.include_router(
    market_data.router,
    prefix="/market",
    tags=["market"]
)

api_router.include_router(
    leads.router,
    prefix="/leads",
    tags=["leads"]
)

api_router.include_router(
    ai_insights.router,
    prefix="/ai-insights",
    tags=["ai-insights"]
)

api_router.include_router(
    websocket.router,
    prefix="/ws",
    tags=["websocket"]
)

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    supabase.router,
    prefix="/supabase",
    tags=["supabase"]
)

api_router.include_router(
    investment_opportunities.router,
    prefix="/investment-opportunities",
    tags=["investment-opportunities"]
)

api_router.include_router(
    real_estate_apis.router,
    prefix="/real-estate-apis",
    tags=["real-estate-apis"]
)

api_router.include_router(
    demo_schedule.router,
    prefix="/demo-schedule",
    tags=["demo-schedule"]
)

api_router.include_router(
    property_scanner.router,
    prefix="/property-scanner",
    tags=["property-scanner"]
)

api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)

api_router.include_router(
    underwriting.router,
    prefix="/underwriting",
    tags=["underwriting"]
)

api_router.include_router(
    legal_compliance.router,
    prefix="/legal-compliance",
    tags=["legal-compliance"]
)

api_router.include_router(
    investment_committee.router,
    prefix="/investment-committee",
    tags=["investment-committee"]
)

api_router.include_router(
    execution_closing.router,
    prefix="/execution-closing",
    tags=["execution-closing"]
)

api_router.include_router(
    post_acquisition.router,
    prefix="/post-acquisition",
    tags=["post-acquisition"]
)

api_router.include_router(
    subscription.router,
    prefix="/subscription",
    tags=["subscription"]
)

api_router.include_router(
    ai_agents.router,
    prefix="/ai-agents",
    tags=["ai-agents"]
)

# New comprehensive property intelligence endpoints
api_router.include_router(
    property_intelligence.router,
    prefix="/property-intelligence",
    tags=["property-intelligence"]
)

# Analytics endpoints
api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)

# Automation endpoints
api_router.include_router(
    automation.router,
    prefix="/automation",
    tags=["automation"]
)

# Ask Janus endpoints
api_router.include_router(
    ask.router,
    prefix="/ask",
    tags=["ask"]
)

# Agent Management endpoints
api_router.include_router(
    agent_management.router,
    prefix="/agents",
    tags=["agent-management"]
)

# Root endpoint
@api_router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Janus Prop AI Backend API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "agents": "/api/v1/agents",
            "properties": "/api/v1/properties",
            "market": "/api/v1/market",
            "leads": "/api/v1/leads",
            "ai-insights": "/api/v1/ai-insights",
            "websocket": "/api/v1/ws",
            "health": "/api/v1/health",
            "supabase": "/api/v1/supabase",
            "investment-opportunities": "/api/v1/investment-opportunities",
            "real-estate-apis": "/api/v1/real-estate-apis",
            "demo-schedule": "/api/v1/demo-schedule",
            "property-scanner": "/api/v1/property-scanner",
            "documents": "/api/v1/documents",
            "underwriting": "/api/v1/underwriting",
            "legal-compliance": "/api/v1/legal-compliance",
            "investment-committee": "/api/v1/investment-committee",
            "execution-closing": "/api/v1/execution-closing",
            "post-acquisition": "/api/v1/post-acquisition",
            "subscription": "/api/v1/subscription",
            "property-intelligence": "/api/v1/property-intelligence",
            "analytics": "/api/v1/analytics",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }
