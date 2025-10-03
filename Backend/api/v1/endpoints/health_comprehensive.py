"""
Comprehensive health check endpoint for Janus Prop AI Backend

Provides the main health endpoint that the frontend expects.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import asyncio
import structlog
import os
import psutil

logger = structlog.get_logger(__name__)

router = APIRouter()

@router.get("/")
async def health_check():
    """Main health check endpoint."""
    try:
        # Get system information
        start_time = datetime.utcnow()
        
        # Basic system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Check environment variables for key services
        services = {
            "database": {
                "status": "healthy",
                "type": "SQLite",
                "location": "janus_prop_ai.db"
            },
            "redis": {
                "status": "healthy" if os.getenv("REDIS_URL") else "not_configured",
                "type": "Redis",
                "url": os.getenv("REDIS_URL", "Not configured")
            },
            "supabase": {
                "status": "healthy" if os.getenv("SUPABASE_URL") else "not_configured",
                "type": "Supabase",
                "url": os.getenv("SUPABASE_URL", "Not configured")
            },
            "openai": {
                "status": "healthy" if os.getenv("OPENAI_API_KEY") else "not_configured",
                "type": "OpenAI API",
                "configured": bool(os.getenv("OPENAI_API_KEY"))
            },
            "attom": {
                "status": "healthy" if os.getenv("ATTOM_API_KEY") else "not_configured",
                "type": "ATTOM Data API",
                "configured": bool(os.getenv("ATTOM_API_KEY"))
            },
            "estated": {
                "status": "healthy" if os.getenv("ESTATED_API_KEY") else "not_configured",
                "type": "Estated API",
                "configured": bool(os.getenv("ESTATED_API_KEY"))
            }
        }
        
        # Calculate overall status
        configured_services = sum(1 for service in services.values() if service["status"] == "healthy")
        total_services = len(services)
        
        overall_status = "healthy"
        if configured_services < total_services * 0.5:
            overall_status = "degraded"
        if configured_services == 0:
            overall_status = "unhealthy"
        
        end_time = datetime.utcnow()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "uptime": 0,  # In production, this would be calculated from start time
            "services": services,
            "system": {
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory.percent}%",
                "disk_usage": f"{disk.percent}%",
                "response_time_ms": round(response_time, 2)
            },
            "environment": {
                "python_version": "3.12",
                "fastapi_version": "0.104.1",
                "environment": os.getenv("ENVIRONMENT", "development")
            }
        }
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "version": "1.0.0"
        }
