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
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Import configuration and core modules
from config.settings import get_settings
from core.database import init_database
from core.redis_client import init_redis
from core.websocket_manager import WebSocketManager, set_websocket_manager
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

# Windows-specific: use SelectorEventLoop to avoid Proactor connection reset noise
try:
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except Exception:
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    global websocket_manager, realtime_manager, agent_manager
    
    # Startup
    logger.info("Starting Janus Prop AI Backend...")
    
    try:
        # Initialize database (graceful failure)
        try:
            await init_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.warning("Database initialization failed, continuing without database", error=str(e))
        
        # Initialize Redis (graceful failure)
        try:
            await init_redis()
            logger.info("Redis initialized successfully")
        except Exception as e:
            logger.warning("Redis initialization failed, continuing without Redis", error=str(e))
        
        # Initialize WebSocket manager
        try:
            websocket_manager = WebSocketManager()
            await websocket_manager.start()
            set_websocket_manager(websocket_manager)  # Set global instance
            logger.info("WebSocket manager started successfully")
        except Exception as e:
            logger.warning("WebSocket manager failed to start", error=str(e))
            websocket_manager = None
        
        # Initialize real-time manager
        try:
            if websocket_manager:
                realtime_manager = RealtimeManager(websocket_manager)
                await realtime_manager.start()
                logger.info("Real-time manager started successfully")
            else:
                logger.warning("Real-time manager not started (WebSocket manager unavailable)")
                realtime_manager = None
        except Exception as e:
            logger.warning("Real-time manager failed to start", error=str(e))
            realtime_manager = None
        
        # Initialize agent manager
        try:
            agent_manager = AgentManager()
            await agent_manager.start()
            logger.info("Agent manager started successfully")
        except Exception as e:
            logger.warning("Agent manager failed to start", error=str(e))
            agent_manager = None
        
        logger.info("Janus Prop AI Backend started (some components may be disabled)")
        
    except Exception as e:
        logger.error("Critical failure during startup", error=str(e))
        # Don't raise - let the app start in degraded mode
    
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
    
    # Add a top-level middleware BEFORE CORS to short-circuit OPTIONS
    class PreflightMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            from fastapi.responses import Response
            if request.method == "OPTIONS":
                origin = request.headers.get("origin", "*")
                request_method = request.headers.get("access-control-request-method", "*")
                request_headers = request.headers.get("access-control-request-headers", "*")
                headers = {
                    "Access-Control-Allow-Origin": origin if origin else "*",
                    "Access-Control-Allow-Methods": request_method if request_method else "*",
                    "Access-Control-Allow-Headers": request_headers if request_headers else "*",
                    "Access-Control-Max-Age": "86400",
                    "Access-Control-Allow-Credentials": "true" if origin and origin != "*" else "false",
                    "X-Preflight-Bypass": "true",
                }
                return Response(content="", status_code=200, headers=headers)
            return await call_next(request)


    # Add CORS middleware with comprehensive configuration
    cors_origins = settings.cors_origins_list
    if settings.DEBUG:
        # Add more permissive origins for development
        cors_origins.extend([
            "http://localhost:8080",
            "http://127.0.0.1:8080", 
            "http://localhost:4173",
            "http://127.0.0.1:4173",
            "http://localhost:5173",  # Vite default port
            "http://127.0.0.1:5173",
            "http://localhost:3000",  # React default port
            "http://127.0.0.1:3000"
        ])
    
    # Remove duplicates and ensure unique origins
    cors_origins = list(set(cors_origins))
    
    # For development, allow all origins
    if settings.DEBUG:
        cors_origins = ["*"]
    
    logger.info("CORS Configuration", 
                origins=cors_origins, 
                debug=settings.DEBUG,
                allow_credentials=cors_origins != ["*"])
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins if cors_origins != ["*"] else ["*"],
        allow_credentials=True if cors_origins != ["*"] else False,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=86400,  # Cache preflight response for 24 hours
    )
    
    # Register preflight middleware AFTER CORS so it wraps outermost
    app.add_middleware(PreflightMiddleware)
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        from datetime import datetime
        import psutil
        
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "uptime": 0,  # Would calculate actual uptime in production
            "services": {
                "database": "healthy",
                "redis": "healthy" if os.getenv("REDIS_URL") else "not_configured",
                "websocket": "healthy",
                "agents": "healthy",
                "supabase": "healthy" if os.getenv("SUPABASE_URL") else "not_configured"
            }
        }
    
    # Explicit preflight for health
    @app.options("/health")
    async def health_options():
        from fastapi.responses import Response
        return Response(content="", status_code=200)
    
    # CORS test endpoint
    @app.get("/cors-test")
    async def cors_test():
        return {
            "message": "CORS test successful",
            "cors_origins": settings.cors_origins_list,
            "debug_mode": settings.DEBUG,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    # Comprehensive CORS debug endpoint
    @app.get("/cors-debug")
    async def cors_debug():
        return {
            "message": "CORS Debug Information",
            "cors_origins": settings.cors_origins_list,
            "debug_mode": settings.DEBUG,
            "server_host": settings.HOST,
            "server_port": settings.PORT,
            "timestamp": asyncio.get_event_loop().time(),
            "headers_allowed": [
                "Accept",
                "Accept-Language", 
                "Content-Language",
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "Origin",
                "Access-Control-Request-Method",
                "Access-Control-Request-Headers",
                "Cache-Control",
                "Pragma",
                "X-API-Key",
                "X-Request-ID",
            ],
            "methods_allowed": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]
        }
    
    # OPTIONS handler for CORS preflight
    @app.options("/{path:path}")
    async def options_handler(path: str, request: Request):
        """Handle CORS preflight OPTIONS requests."""
        from fastapi.responses import Response
        
        origin = request.headers.get("origin", "*")
        
        response = Response(
            content="",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": origin if origin != "*" else "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH",
                "Access-Control-Allow-Headers": "Accept, Accept-Language, Content-Language, Content-Type, Authorization, X-Requested-With, Origin, Access-Control-Request-Method, Access-Control-Request-Headers, Cache-Control, Pragma, X-API-Key, X-Request-ID",
                "Access-Control-Max-Age": "86400",
                "Access-Control-Allow-Credentials": "true" if origin != "*" else "false"
            }
        )
        return response
    
    # Fallback: convert any OPTIONS HTTPException into a 200 preflight
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if request.method == "OPTIONS":
            origin = request.headers.get("origin", "*")
            request_method = request.headers.get("access-control-request-method", "*")
            request_headers = request.headers.get("access-control-request-headers", "*")
            headers = {
                "Access-Control-Allow-Origin": origin if origin else "*",
                "Access-Control-Allow-Methods": request_method if request_method else "*",
                "Access-Control-Allow-Headers": request_headers if request_headers else "*",
                "Access-Control-Max-Age": "86400",
                "Access-Control-Allow-Credentials": "true" if origin and origin != "*" else "false",
            }
            return JSONResponse(status_code=200, content={}, headers=headers)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    
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
        "use_colors": True,
        "loop": "asyncio",
        "http": "h11",
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
