"""
Main Application Entry Point for Janus Prop AI Backend

This module initializes and runs the complete real estate AI agent system,
including real-time APIs, WebSocket support, and all specialized agents.
"""

import asyncio
import signal
import sys
import os
from typing import Dict, Any
from pathlib import Path

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import configuration and core modules
from config.settings import get_settings
from core.database import init_database
from core.redis_client import init_redis
from core.websocket_manager import WebSocketManager
from core.realtime_manager import RealtimeManager
from agents.agent_manager import AgentManager
from api.v1.api import api_router

# Configure structured logging
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
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global managers
websocket_manager: WebSocketManager = None
realtime_manager: RealtimeManager = None
agent_manager: AgentManager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    global websocket_manager, realtime_manager, agent_manager
    
    # Startup
    logger.info("Starting Janus Prop AI Backend...")
    
    try:
        # Initialize database
        await init_database()
        logger.info("Database initialized successfully")
        
        # Initialize Redis
        await init_redis()
        logger.info("Redis initialized successfully")
        
        # Initialize WebSocket manager
        websocket_manager = WebSocketManager()
        await websocket_manager.start()
        logger.info("WebSocket manager started successfully")
        
        # Initialize real-time manager
        realtime_manager = RealtimeManager(websocket_manager)
        await realtime_manager.start()
        logger.info("Real-time manager started successfully")
        
        # Initialize agent manager
        agent_manager = AgentManager()
        await agent_manager.start()
        logger.info("Agent manager started successfully")
        
        logger.info("Janus Prop AI Backend started successfully")
        
    except Exception as e:
        logger.error("Failed to start backend", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Janus Prop AI Backend...")
    
    try:
        if agent_manager:
            await agent_manager.stop()
        if realtime_manager:
            await realtime_manager.stop()
        if websocket_manager:
            await websocket_manager.stop()
        logger.info("Backend shutdown completed")
    except Exception as e:
        logger.error("Error during shutdown", error=str(e))

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Janus Prop AI Backend",
        description="Real Estate AI Agent System with Real-time APIs",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time(),
            "version": "1.0.0"
        }
    
    return app

def main():
    """Main entry point for the application."""
    import uvicorn
    
    settings = get_settings()
    
    # Configure uvicorn
    uvicorn_config = {
        "app": "main:create_app",
        "host": settings.HOST,
        "port": settings.PORT,
        "reload": settings.DEBUG,
        "log_level": settings.LOG_LEVEL.lower(),
        "access_log": True,
        "use_colors": True
    }
    
    logger.info("Starting Janus Prop AI Backend server", config=uvicorn_config)
    
    try:
        uvicorn.run(**uvicorn_config)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
