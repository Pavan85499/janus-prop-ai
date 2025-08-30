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
    real_estate_apis
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
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }
