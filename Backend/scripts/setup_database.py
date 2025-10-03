#!/usr/bin/env python3
"""
Database Setup Script for Janus Prop AI Backend

This script provides a comprehensive database setup and management tool.
It supports both Supabase and local PostgreSQL configurations.
"""

import asyncio
import os
import sys
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from core.database import init_database, close_database, get_session_factory, health_check
from core.supabase_client import init_supabase, get_supabase_status
from core.redis_client import init_redis, close_redis
from config.settings import get_settings
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class DatabaseSetup:
    """Database setup and management class."""
    
    def __init__(self):
        self.settings = get_settings()
        self.setup_type = None
    
    async def detect_setup_type(self) -> str:
        """Detect the type of database setup based on configuration."""
        if self.settings.is_supabase_enabled:
            return "supabase"
        elif self.settings.DATABASE_URL and "postgresql" in self.settings.DATABASE_URL:
            return "postgresql"
        else:
            return "none"
    
    async def check_dependencies(self) -> Dict[str, bool]:
        """Check if required dependencies are available."""
        dependencies = {
            "asyncpg": False,
            "supabase": False,
            "redis": False,
            "sqlalchemy": False
        }
        
        try:
            import asyncpg
            dependencies["asyncpg"] = True
        except ImportError:
            logger.warning("asyncpg not available - required for PostgreSQL")
        
        try:
            import supabase
            dependencies["supabase"] = True
        except ImportError:
            logger.warning("supabase not available - required for Supabase")
        
        try:
            import redis
            dependencies["redis"] = True
        except ImportError:
            logger.warning("redis not available - required for caching")
        
        try:
            import sqlalchemy
            dependencies["sqlalchemy"] = True
        except ImportError:
            logger.warning("sqlalchemy not available - required for database ORM")
        
        return dependencies
    
    async def setup_supabase(self) -> bool:
        """Setup Supabase database."""
        logger.info("Setting up Supabase database...")
        
        try:
            # Initialize Supabase client
            supabase_client = await init_supabase()
            if not supabase_client:
                logger.error("Failed to initialize Supabase client")
                return False
            
            # Test connection
            status = await get_supabase_status()
            if not status.get("connected", False):
                logger.error("Failed to connect to Supabase")
                return False
            
            logger.info("Supabase connection successful", 
                       project_id=self.settings.SUPABASE_PROJECT_ID)
            
            # Apply schema
            await self.apply_schema()
            
            return True
            
        except Exception as e:
            logger.error("Supabase setup failed", error=str(e))
            return False
    
    async def setup_postgresql(self) -> bool:
        """Setup local PostgreSQL database."""
        logger.info("Setting up local PostgreSQL database...")
        
        try:
            # Initialize database
            await init_database()
            
            # Test connection
            is_healthy = await health_check()
            if not is_healthy:
                logger.error("Database health check failed")
                return False
            
            logger.info("PostgreSQL connection successful")
            
            # Create tables (handled by init_database for local setup)
            logger.info("Database tables created/verified")
            
            return True
            
        except Exception as e:
            logger.error("PostgreSQL setup failed", error=str(e))
            return False
    
    async def apply_schema(self) -> bool:
        """Apply database schema."""
        logger.info("Applying database schema...")
        
        try:
            schema_file = Path(__file__).parent.parent / "supabase_schema.sql"
            
            if not schema_file.exists():
                logger.error(f"Schema file not found: {schema_file}")
                return False
            
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            # Split the SQL into individual statements
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            session_factory = get_session_factory()
            async with session_factory() as session:
                for i, statement in enumerate(statements, 1):
                    if statement and not statement.startswith('--'):
                        try:
                            await session.execute(statement)
                            logger.info(f"Executed statement {i}/{len(statements)}")
                        except Exception as e:
                            logger.warning(f"Error executing statement {i}: {e}")
                            continue
                
                await session.commit()
            
            logger.info("Schema applied successfully")
            return True
            
        except Exception as e:
            logger.error("Schema application failed", error=str(e))
            return False
    
    async def setup_redis(self) -> bool:
        """Setup Redis connection."""
        logger.info("Setting up Redis...")
        
        try:
            await init_redis()
            logger.info("Redis connection successful")
            return True
            
        except Exception as e:
            logger.warning("Redis setup failed", error=str(e))
            return False
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run comprehensive health checks."""
        logger.info("Running health checks...")
        
        health_status = {
            "database": False,
            "redis": False,
            "supabase": False,
            "overall": False
        }
        
        # Database health check
        try:
            health_status["database"] = await health_check()
        except Exception as e:
            logger.warning("Database health check failed", error=str(e))
        
        # Redis health check
        try:
            from core.redis_client import get_redis_client
            redis_client = get_redis_client()
            if redis_client:
                await redis_client.ping()
                health_status["redis"] = True
        except Exception as e:
            logger.warning("Redis health check failed", error=str(e))
        
        # Supabase health check
        if self.settings.is_supabase_enabled:
            try:
                status = await get_supabase_status()
                health_status["supabase"] = status.get("connected", False)
            except Exception as e:
                logger.warning("Supabase health check failed", error=str(e))
        
        # Overall health
        health_status["overall"] = health_status["database"] and (
            health_status["redis"] or not self.settings.REDIS_URL
        )
        
        return health_status
    
    async def print_status(self):
        """Print current database status."""
        logger.info("Database Status Report")
        logger.info("=" * 50)
        
        # Configuration
        setup_type = await self.detect_setup_type()
        logger.info(f"Setup Type: {setup_type}")
        
        if setup_type == "supabase":
            logger.info(f"Supabase Project ID: {self.settings.SUPABASE_PROJECT_ID}")
            logger.info(f"Supabase URL: {self.settings.SUPABASE_URL}")
        elif setup_type == "postgresql":
            logger.info(f"Database URL: {self.settings.DATABASE_URL}")
        
        logger.info(f"Redis URL: {self.settings.REDIS_URL}")
        
        # Dependencies
        dependencies = await self.check_dependencies()
        logger.info("Dependencies:")
        for dep, available in dependencies.items():
            status = "✓" if available else "✗"
            logger.info(f"  {status} {dep}")
        
        # Health checks
        health_status = await self.run_health_checks()
        logger.info("Health Status:")
        for service, status in health_status.items():
            status_icon = "✓" if status else "✗"
            logger.info(f"  {status_icon} {service}")
    
    async def setup(self, force: bool = False) -> bool:
        """Run complete database setup."""
        logger.info("Starting database setup...")
        
        # Detect setup type
        setup_type = await self.detect_setup_type()
        self.setup_type = setup_type
        
        if setup_type == "none":
            logger.error("No database configuration found")
            logger.info("Please configure either Supabase or local PostgreSQL")
            return False
        
        logger.info(f"Detected setup type: {setup_type}")
        
        # Check dependencies
        dependencies = await self.check_dependencies()
        missing_deps = [dep for dep, available in dependencies.items() if not available]
        
        if missing_deps:
            logger.error(f"Missing dependencies: {missing_deps}")
            logger.info("Please install missing dependencies: pip install " + " ".join(missing_deps))
            return False
        
        # Setup database
        db_success = False
        if setup_type == "supabase":
            db_success = await self.setup_supabase()
        elif setup_type == "postgresql":
            db_success = await self.setup_postgresql()
        
        if not db_success:
            logger.error("Database setup failed")
            return False
        
        # Setup Redis
        redis_success = await self.setup_redis()
        if not redis_success:
            logger.warning("Redis setup failed, continuing without Redis")
        
        # Final health check
        health_status = await self.run_health_checks()
        
        if health_status["overall"]:
            logger.info("✅ Database setup completed successfully!")
            return True
        else:
            logger.error("❌ Database setup completed with issues")
            return False

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Janus Prop AI Database Setup")
    parser.add_argument("--setup", action="store_true", help="Run database setup")
    parser.add_argument("--status", action="store_true", help="Show database status")
    parser.add_argument("--health", action="store_true", help="Run health checks")
    parser.add_argument("--force", action="store_true", help="Force setup even if already configured")
    
    args = parser.parse_args()
    
    if not any([args.setup, args.status, args.health]):
        parser.print_help()
        return
    
    setup = DatabaseSetup()
    
    try:
        if args.status:
            await setup.print_status()
        
        if args.health:
            health_status = await setup.run_health_checks()
            logger.info("Health Check Results:", **health_status)
        
        if args.setup:
            success = await setup.setup(force=args.force)
            if not success:
                sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error("Setup failed", error=str(e))
        sys.exit(1)
    finally:
        await close_database()
        await close_redis()

if __name__ == "__main__":
    asyncio.run(main())
