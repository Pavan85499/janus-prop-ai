"""
Database initialization and connection management for Janus Prop AI Backend

This module handles database connections, migrations, and session management.
"""

import asyncio
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

import structlog
from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    create_async_engine, 
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from config.settings import get_settings

logger = structlog.get_logger()

# Database configuration
Base = declarative_base()

# Global database engine and session factory
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None

async def init_database() -> None:
    """Initialize the database connection and create tables."""
    global _engine, _session_factory
    
    settings = get_settings()
    
    try:
        # Determine database URL based on configuration
        if settings.is_supabase_enabled:
            try:
                database_url = settings.supabase_database_url
                logger.info("Using Supabase database", project_id=settings.SUPABASE_PROJECT_ID)
            except ValueError as e:
                logger.warning("Supabase configuration incomplete, falling back to local database", error=str(e))
                database_url = settings.DATABASE_URL
                logger.info("Using local database")
        else:
            database_url = settings.DATABASE_URL
            logger.info("Using local database")
        
        # Check if we have a valid database URL
        if not database_url or database_url == "postgresql://user:password@localhost:5432/janus_prop_ai":
            logger.warning("No valid database configured. Skipping database initialization.")
            logger.info("Please set up Supabase or local database configuration.")
            return
        
        # Create async engine with proper driver
        # For Supabase, we need to ensure we're using asyncpg
        if settings.is_supabase_enabled:
            # Ensure the URL uses asyncpg driver for Supabase
            if not database_url.startswith("postgresql+asyncpg://"):
                database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        
        try:
            _engine = create_async_engine(
                database_url,
                echo=settings.DEBUG,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                pool_timeout=settings.DATABASE_POOL_TIMEOUT,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
        except Exception as e:
            logger.error("Failed to create async engine", error=str(e))
            if "asyncpg" in str(e):
                logger.error("asyncpg driver not available. Please install: pip install asyncpg")
            raise
        
        # Create session factory
        _session_factory = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        # Test connection
        async with _engine.begin() as conn:
            await conn.run_sync(lambda _: None)
        
        logger.info("Database initialized successfully", url=database_url)
        
        # Only create tables for local database, Supabase uses the schema.sql
        if not settings.is_supabase_enabled:
            await create_tables()
        else:
            logger.info("Supabase database detected - tables should be created via schema.sql")
        
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        logger.warning("Database initialization failed. Backend will run without database functionality.")
        # Don't raise the error, just log it and continue
        return

async def create_tables() -> None:
    """Create database tables if they don't exist."""
    try:
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error("Failed to create database tables", error=str(e))
        raise

async def close_database() -> None:
    """Close database connections."""
    global _engine, _session_factory
    
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database connections closed")

def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get the database session factory."""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _session_factory

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session with automatic cleanup."""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    session = _session_factory()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

async def health_check() -> bool:
    """Check database health."""
    try:
        if _engine is None:
            # No database configured
            return False
        
        async with _engine.begin() as conn:
            await conn.run_sync(lambda _: None)
        return True
    except Exception as e:
        logger.warning("Database health check failed", error=str(e))
        return False

# Database models - imported separately to avoid circular imports
# from models.property import Property
# from models.agent import Agent
# from models.user import User
# from models.lead import Lead
# from models.market_data import MarketData
# from models.ai_insight import AIInsight

__all__ = [
    "Base",
    "init_database",
    "close_database",
    "get_db_session",
    "health_check"
]
