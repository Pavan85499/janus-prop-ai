"""
Health check endpoints for Janus Prop AI Backend

This module provides endpoints for monitoring system health and status.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.database import health_check as db_health_check
from core.redis_client import health_check as redis_health_check
from core.websocket_manager import get_websocket_manager
from core.supabase_client import test_supabase_connection
from config.settings import get_settings

router = APIRouter()

class HealthStatus(BaseModel):
    """Health status model."""
    status: str
    timestamp: datetime
    version: str
    uptime: float
    services: Dict[str, Any]

class SystemStatus(BaseModel):
    """System status model."""
    overall_status: str
    database: str
    redis: str
    websocket: str
    agents: str
    timestamp: datetime

@router.get("/", response_model=HealthStatus)
async def health_check():
    """Basic health check endpoint."""
    try:
        # Check database health
        db_healthy = await db_health_check()
        
        # Check Redis health
        redis_healthy = await redis_health_check()
        
        # Check WebSocket manager
        try:
            websocket_manager = get_websocket_manager()
            websocket_healthy = websocket_manager.get_connection_count() >= 0
        except:
            websocket_healthy = False
        
        # Check Supabase health if configured
        settings = get_settings()
        supabase_healthy = False
        if settings.is_supabase_enabled:
            supabase_healthy = await test_supabase_connection()
        
        # Determine overall status
        core_services_healthy = db_healthy and redis_healthy and websocket_healthy
        if settings.is_supabase_enabled:
            all_healthy = core_services_healthy and supabase_healthy
        else:
            all_healthy = core_services_healthy
        
        if all_healthy:
            status = "healthy"
        elif core_services_healthy:
            status = "degraded"
        else:
            status = "unhealthy"
        
        services = {
            "database": "healthy" if db_healthy else "unhealthy",
            "redis": "healthy" if redis_healthy else "unhealthy",
            "websocket": "healthy" if websocket_healthy else "unhealthy"
        }
        
        if settings.is_supabase_enabled:
            services["supabase"] = "healthy" if supabase_healthy else "unhealthy"
        
        return HealthStatus(
            status=status,
            timestamp=datetime.utcnow(),
            version="1.0.0",
            uptime=0.0,  # Would calculate actual uptime in production
            services=services
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/detailed", response_model=SystemStatus)
async def detailed_health_check():
    """Detailed health check with all system components."""
    try:
        # Check database health
        db_healthy = await db_health_check()
        
        # Check Redis health
        redis_healthy = await redis_health_check()
        
        # Check WebSocket manager
        try:
            websocket_manager = get_websocket_manager()
            websocket_healthy = websocket_manager.get_connection_count() >= 0
            websocket_status = "healthy" if websocket_healthy else "unhealthy"
        except:
            websocket_status = "unhealthy"
        
        # Check agents (mock for now)
        agents_status = "healthy"  # Would check actual agent status in production
        
        # Determine overall status
        all_healthy = all([
            db_healthy,
            redis_healthy,
            websocket_healthy,
            agents_status == "healthy"
        ])
        
        overall_status = "healthy" if all_healthy else "degraded"
        
        return SystemStatus(
            overall_status=overall_status,
            database="healthy" if db_healthy else "unhealthy",
            redis="healthy" if redis_healthy else "unhealthy",
            websocket=websocket_status,
            agents=agents_status,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detailed health check failed: {str(e)}")

@router.get("/database")
async def database_health():
    """Database-specific health check."""
    try:
        is_healthy = await db_health_check()
        return {
            "service": "database",
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.utcnow(),
            "details": {
                "connection": "established" if is_healthy else "failed",
                "response_time": "normal" if is_healthy else "timeout"
            }
        }
    except Exception as e:
        return {
            "service": "database",
            "status": "error",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }

@router.get("/redis")
async def redis_health():
    """Redis-specific health check."""
    try:
        is_healthy = await redis_health_check()
        return {
            "service": "redis",
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.utcnow(),
            "details": {
                "connection": "established" if is_healthy else "failed",
                "ping": "successful" if is_healthy else "failed"
            }
        }
    except Exception as e:
        return {
            "service": "redis",
            "status": "error",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }

@router.get("/websocket")
async def websocket_health():
    """WebSocket-specific health check."""
    try:
        websocket_manager = get_websocket_manager()
        connection_count = websocket_manager.get_connection_count()
        subscription_count = len(websocket_manager.connection_manager.subscriptions)
        
        return {
            "service": "websocket",
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "details": {
                "active_connections": connection_count,
                "active_subscriptions": subscription_count,
                "manager_status": "running"
            }
        }
    except Exception as e:
        return {
            "service": "websocket",
            "status": "error",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }

@router.get("/agents")
async def agents_health():
    """Agents-specific health check."""
    try:
        # Mock agent health check for now
        # In production, this would check actual agent status
        return {
            "service": "agents",
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "details": {
                "total_agents": 3,
                "online_agents": 3,
                "offline_agents": 0,
                "average_health_score": 0.91
            }
        }
    except Exception as e:
        return {
            "service": "agents",
            "status": "error",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }

@router.get("/metrics")
async def system_metrics():
    """Get system performance metrics."""
    try:
        # Mock metrics for now
        # In production, this would collect real metrics
        return {
            "timestamp": datetime.utcnow(),
            "metrics": {
                "cpu_usage": 15.2,
                "memory_usage": 45.8,
                "disk_usage": 23.1,
                "network_io": {
                    "bytes_in": 1024000,
                    "bytes_out": 512000
                },
                "active_connections": 5,
                "requests_per_minute": 12,
                "average_response_time": 0.15
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")
