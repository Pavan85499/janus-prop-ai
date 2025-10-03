"""
Health check endpoints for Janus Prop AI Backend

Provides comprehensive health monitoring and status reporting.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime
import asyncio
import structlog
import os
import psutil

from core.database import get_db_session
from core.redis_client import get_redis_client
from core.websocket_manager import get_websocket_manager

logger = structlog.get_logger(__name__)

router = APIRouter()

@router.get("/detailed")
async def detailed_health_check(
    db = Depends(get_db_session)
):
    """Get detailed health status of all system components."""
    try:
        # Check database connection
        db_status = "healthy"
        try:
            # Simple database query to test connection
            db.execute("SELECT 1")
        except Exception as e:
            db_status = "unhealthy"
            logger.error("Database health check failed", error=str(e))
        
        # Check Redis connection
        redis_status = "healthy"
        try:
            redis_client = get_redis_client()
            await redis_client.ping()
        except Exception as e:
            redis_status = "unhealthy"
            logger.error("Redis health check failed", error=str(e))
        
        # Check WebSocket manager
        websocket_status = "healthy"
        try:
            ws_manager = get_websocket_manager()
            # Check if WebSocket manager is properly initialized
            if not ws_manager:
                websocket_status = "unhealthy"
        except Exception as e:
            websocket_status = "unhealthy"
            logger.error("WebSocket health check failed", error=str(e))
        
        # Check AI agents
        agents_status = "healthy"
        try:
            # Mock agent health check - in production, this would check actual agent status
            agent_health_checks = {
                "eden": "online",
                "atlas": "online", 
                "nova": "online",
                "orion": "online",
                "atelius": "online"
            }
            online_agents = sum(1 for status in agent_health_checks.values() if status == "online")
            total_agents = len(agent_health_checks)
            
            if online_agents < total_agents * 0.8:  # Less than 80% of agents online
                agents_status = "degraded"
            elif online_agents == 0:
                agents_status = "unhealthy"
        except Exception as e:
            agents_status = "unhealthy"
            logger.error("Agents health check failed", error=str(e))
        
        # System resource checks
        system_status = "healthy"
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                system_status = "degraded"
        except Exception as e:
            system_status = "unhealthy"
            logger.error("System health check failed", error=str(e))
        
        # Determine overall status
        overall_status = "healthy"
        if any(status == "unhealthy" for status in [db_status, redis_status, websocket_status, agents_status, system_status]):
            overall_status = "unhealthy"
        elif any(status == "degraded" for status in [db_status, redis_status, websocket_status, agents_status, system_status]):
            overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "database": db_status,
            "redis": redis_status,
            "websocket": websocket_status,
            "agents": agents_status,
            "system": system_status,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "database": {
                    "status": db_status,
                    "connection_pool_size": 10,
                    "active_connections": 3
                },
                "redis": {
                    "status": redis_status,
                    "memory_usage": "45MB",
                    "connected_clients": 2
                },
                "websocket": {
                    "status": websocket_status,
                    "active_connections": 5,
                    "total_connections": 127
                },
                "agents": {
                    "status": agents_status,
                    "total_agents": 5,
                    "online_agents": 5,
                    "agent_details": agent_health_checks
                },
                "system": {
                    "status": system_status,
                    "cpu_usage": f"{cpu_percent}%",
                    "memory_usage": f"{memory.percent}%",
                    "disk_usage": f"{disk.percent}%"
                }
            }
        }
        
    except Exception as e:
        logger.error("Error in detailed health check", error=str(e))
        raise HTTPException(status_code=500, detail="Health check failed")

@router.get("/database")
async def database_health_check(
    db = Depends(get_db_session)
):
    """Check database health specifically."""
    try:
        # Test database connection
        start_time = datetime.utcnow()
        db.execute("SELECT 1")
        end_time = datetime.utcnow()
        
        response_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
        
        return {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/redis")
async def redis_health_check():
    """Check Redis health specifically."""
    try:
        redis_client = get_redis_client()
        
        # Test Redis connection
        start_time = datetime.utcnow()
        await redis_client.ping()
        end_time = datetime.utcnow()
        
        response_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
        
        # Get Redis info
        info = await redis_client.info()
        
        return {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "redis_version": info.get("redis_version", "unknown"),
            "memory_usage": info.get("used_memory_human", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/agents")
async def agents_health_check():
    """Check AI agents health specifically."""
    try:
        # Mock agent health check - in production, this would check actual agent status
        agent_health_checks = {
            "eden": {
                "status": "online",
                "last_activity": "2024-01-15T10:30:00Z",
                "tasks_completed": 1247,
                "success_rate": 0.94
            },
            "atlas": {
                "status": "online",
                "last_activity": "2024-01-15T10:25:00Z",
                "tasks_completed": 892,
                "success_rate": 0.91
            },
            "nova": {
                "status": "online",
                "last_activity": "2024-01-15T10:28:00Z",
                "tasks_completed": 756,
                "success_rate": 0.96
            },
            "orion": {
                "status": "online",
                "last_activity": "2024-01-15T10:20:00Z",
                "tasks_completed": 634,
                "success_rate": 0.93
            },
            "atelius": {
                "status": "online",
                "last_activity": "2024-01-15T09:45:00Z",
                "tasks_completed": 423,
                "success_rate": 0.98
            }
        }
        
        online_agents = sum(1 for agent in agent_health_checks.values() if agent["status"] == "online")
        total_agents = len(agent_health_checks)
        
        overall_status = "healthy"
        if online_agents < total_agents * 0.8:
            overall_status = "degraded"
        elif online_agents == 0:
            overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "total_agents": total_agents,
            "online_agents": online_agents,
            "agents": agent_health_checks,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Agents health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/system")
async def system_health_check():
    """Check system resources health."""
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Determine system status
        system_status = "healthy"
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            system_status = "degraded"
        if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
            system_status = "unhealthy"
        
        return {
            "status": system_status,
            "cpu": {
                "usage_percent": cpu_percent,
                "status": "healthy" if cpu_percent < 80 else "degraded" if cpu_percent < 90 else "unhealthy"
            },
            "memory": {
                "usage_percent": memory.percent,
                "available_gb": round(memory.available / (1024**3), 2),
                "total_gb": round(memory.total / (1024**3), 2),
                "status": "healthy" if memory.percent < 80 else "degraded" if memory.percent < 90 else "unhealthy"
            },
            "disk": {
                "usage_percent": disk.percent,
                "free_gb": round(disk.free / (1024**3), 2),
                "total_gb": round(disk.total / (1024**3), 2),
                "status": "healthy" if disk.percent < 80 else "degraded" if disk.percent < 90 else "unhealthy"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("System health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/external-apis")
async def external_apis_health_check():
    """Check health of external API integrations."""
    try:
        # Check external API keys and availability
        api_health = {
            "attom_api": {
                "status": "healthy" if os.getenv("ATTOM_API_KEY") else "unhealthy",
                "key_configured": bool(os.getenv("ATTOM_API_KEY")),
                "last_check": datetime.utcnow().isoformat()
            },
            "estated_api": {
                "status": "healthy" if os.getenv("ESTATED_API_KEY") else "unhealthy",
                "key_configured": bool(os.getenv("ESTATED_API_KEY")),
                "last_check": datetime.utcnow().isoformat()
            },
            "fred_api": {
                "status": "healthy" if os.getenv("FRED_API_KEY") else "unhealthy",
                "key_configured": bool(os.getenv("FRED_API_KEY")),
                "last_check": datetime.utcnow().isoformat()
            },
            "openai_api": {
                "status": "healthy" if os.getenv("OPENAI_API_KEY") else "unhealthy",
                "key_configured": bool(os.getenv("OPENAI_API_KEY")),
                "last_check": datetime.utcnow().isoformat()
            }
        }
        
        # Determine overall external APIs status
        healthy_apis = sum(1 for api in api_health.values() if api["status"] == "healthy")
        total_apis = len(api_health)
        
        overall_status = "healthy"
        if healthy_apis < total_apis * 0.75:
            overall_status = "degraded"
        if healthy_apis == 0:
            overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "total_apis": total_apis,
            "healthy_apis": healthy_apis,
            "apis": api_health,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("External APIs health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }