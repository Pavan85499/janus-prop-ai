#!/usr/bin/env python3
"""
Database Validation Script for Janus Prop AI Backend

This script validates database schema, data integrity, and configuration.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from core.database import init_database, close_database, get_session_factory, health_check
from core.supabase_client import get_supabase_status
from core.redis_client import init_redis, get_redis_client
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

class DatabaseValidator:
    """Database validation and health check class."""
    
    def __init__(self):
        self.settings = get_settings()
        self.validation_results = {}
    
    async def validate_configuration(self) -> Dict[str, Any]:
        """Validate database configuration."""
        logger.info("Validating database configuration...")
        
        config_validation = {
            "supabase_configured": False,
            "postgresql_configured": False,
            "redis_configured": False,
            "issues": []
        }
        
        # Check Supabase configuration
        if self.settings.is_supabase_enabled:
            config_validation["supabase_configured"] = True
            logger.info("✓ Supabase configuration detected")
        else:
            config_validation["issues"].append("Supabase not configured")
        
        # Check PostgreSQL configuration
        if self.settings.DATABASE_URL and "postgresql" in self.settings.DATABASE_URL:
            config_validation["postgresql_configured"] = True
            logger.info("✓ PostgreSQL configuration detected")
        else:
            config_validation["issues"].append("PostgreSQL not configured")
        
        # Check Redis configuration
        if self.settings.REDIS_URL:
            config_validation["redis_configured"] = True
            logger.info("✓ Redis configuration detected")
        else:
            config_validation["issues"].append("Redis not configured")
        
        return config_validation
    
    async def validate_connections(self) -> Dict[str, Any]:
        """Validate database connections."""
        logger.info("Validating database connections...")
        
        connection_validation = {
            "database_connected": False,
            "redis_connected": False,
            "supabase_connected": False,
            "issues": []
        }
        
        # Test database connection
        try:
            await init_database()
            is_healthy = await health_check()
            if is_healthy:
                connection_validation["database_connected"] = True
                logger.info("✓ Database connection successful")
            else:
                connection_validation["issues"].append("Database health check failed")
        except Exception as e:
            connection_validation["issues"].append(f"Database connection failed: {e}")
        
        # Test Redis connection
        try:
            await init_redis()
            redis_client = get_redis_client()
            if redis_client:
                await redis_client.ping()
                connection_validation["redis_connected"] = True
                logger.info("✓ Redis connection successful")
            else:
                connection_validation["issues"].append("Redis client not available")
        except Exception as e:
            connection_validation["issues"].append(f"Redis connection failed: {e}")
        
        # Test Supabase connection
        if self.settings.is_supabase_enabled:
            try:
                status = await get_supabase_status()
                if status.get("connected", False):
                    connection_validation["supabase_connected"] = True
                    logger.info("✓ Supabase connection successful")
                else:
                    connection_validation["issues"].append("Supabase connection failed")
            except Exception as e:
                connection_validation["issues"].append(f"Supabase connection failed: {e}")
        
        return connection_validation
    
    async def validate_schema(self) -> Dict[str, Any]:
        """Validate database schema."""
        logger.info("Validating database schema...")
        
        schema_validation = {
            "tables_exist": {},
            "indexes_exist": {},
            "constraints_exist": {},
            "issues": []
        }
        
        expected_tables = [
            "users", "agents", "properties", "leads", 
            "market_data", "ai_insights", "user_agent_assignments"
        ]
        
        expected_indexes = [
            ("users", "idx_users_email"),
            ("users", "idx_users_username"),
            ("agents", "idx_agents_type"),
            ("properties", "idx_properties_address"),
            ("properties", "idx_properties_city"),
            ("properties", "idx_properties_state"),
            ("leads", "idx_leads_email"),
            ("leads", "idx_leads_status"),
            ("market_data", "idx_market_data_location"),
            ("ai_insights", "idx_ai_insights_property")
        ]
        
        try:
            session_factory = get_session_factory()
            async with session_factory() as session:
                # Check tables
                for table in expected_tables:
                    result = await session.execute(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = '{table}'
                        );
                    """)
                    
                    exists = result.scalar()
                    schema_validation["tables_exist"][table] = exists
                    
                    if exists:
                        logger.info(f"✓ Table '{table}' exists")
                    else:
                        logger.warning(f"✗ Table '{table}' missing")
                        schema_validation["issues"].append(f"Table '{table}' missing")
                
                # Check indexes
                for table, index in expected_indexes:
                    result = await session.execute(f"""
                        SELECT EXISTS (
                            SELECT FROM pg_indexes 
                            WHERE tablename = '{table}' AND indexname = '{index}'
                        );
                    """)
                    
                    exists = result.scalar()
                    schema_validation["indexes_exist"][f"{table}.{index}"] = exists
                    
                    if exists:
                        logger.info(f"✓ Index '{index}' on table '{table}' exists")
                    else:
                        logger.warning(f"✗ Index '{index}' on table '{table}' missing")
                        schema_validation["issues"].append(f"Index '{index}' on table '{table}' missing")
                
                # Check constraints
                result = await session.execute("""
                    SELECT 
                        tc.table_name,
                        tc.constraint_name,
                        tc.constraint_type
                    FROM information_schema.table_constraints tc
                    WHERE tc.table_schema = 'public'
                    ORDER BY tc.table_name, tc.constraint_name;
                """)
                
                constraints = result.fetchall()
                schema_validation["constraints_exist"] = {
                    f"{row[0]}.{row[1]}": row[2] for row in constraints
                }
                
                logger.info(f"✓ Found {len(constraints)} constraints")
        
        except Exception as e:
            schema_validation["issues"].append(f"Schema validation failed: {e}")
            logger.error(f"Schema validation error: {e}")
        
        return schema_validation
    
    async def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate data integrity."""
        logger.info("Validating data integrity...")
        
        integrity_validation = {
            "table_counts": {},
            "orphaned_records": {},
            "data_issues": [],
            "issues": []
        }
        
        try:
            session_factory = get_session_factory()
            async with session_factory() as session:
                # Check table record counts
                tables = ["users", "agents", "properties", "leads", "market_data", "ai_insights"]
                
                for table in tables:
                    try:
                        result = await session.execute(f"SELECT COUNT(*) FROM {table}")
                        count = result.scalar()
                        integrity_validation["table_counts"][table] = count
                        logger.info(f"✓ Table '{table}' has {count} records")
                    except Exception as e:
                        integrity_validation["issues"].append(f"Failed to count records in '{table}': {e}")
                
                # Check for orphaned records
                # Properties without valid agents
                result = await session.execute("""
                    SELECT COUNT(*) FROM properties p
                    LEFT JOIN agents a ON p.assigned_agent_id = a.id
                    WHERE p.assigned_agent_id IS NOT NULL AND a.id IS NULL;
                """)
                orphaned_properties = result.scalar()
                integrity_validation["orphaned_records"]["properties_without_agents"] = orphaned_properties
                
                if orphaned_properties > 0:
                    logger.warning(f"✗ Found {orphaned_properties} properties with invalid agent assignments")
                    integrity_validation["issues"].append(f"{orphaned_properties} properties with invalid agent assignments")
                else:
                    logger.info("✓ No orphaned property-agent relationships")
                
                # AI insights without valid properties
                result = await session.execute("""
                    SELECT COUNT(*) FROM ai_insights ai
                    LEFT JOIN properties p ON ai.property_id = p.id
                    WHERE ai.property_id IS NOT NULL AND p.id IS NULL;
                """)
                orphaned_insights = result.scalar()
                integrity_validation["orphaned_records"]["ai_insights_without_properties"] = orphaned_insights
                
                if orphaned_insights > 0:
                    logger.warning(f"✗ Found {orphaned_insights} AI insights with invalid property references")
                    integrity_validation["issues"].append(f"{orphaned_insights} AI insights with invalid property references")
                else:
                    logger.info("✓ No orphaned AI insight-property relationships")
                
                # Check for duplicate records
                # Duplicate users by email
                result = await session.execute("""
                    SELECT email, COUNT(*) FROM users 
                    GROUP BY email HAVING COUNT(*) > 1;
                """)
                duplicate_emails = result.fetchall()
                
                if duplicate_emails:
                    logger.warning(f"✗ Found {len(duplicate_emails)} duplicate email addresses")
                    integrity_validation["issues"].append(f"{len(duplicate_emails)} duplicate email addresses")
                else:
                    logger.info("✓ No duplicate email addresses")
        
        except Exception as e:
            integrity_validation["issues"].append(f"Data integrity validation failed: {e}")
            logger.error(f"Data integrity validation error: {e}")
        
        return integrity_validation
    
    async def validate_performance(self) -> Dict[str, Any]:
        """Validate database performance."""
        logger.info("Validating database performance...")
        
        performance_validation = {
            "query_times": {},
            "slow_queries": [],
            "issues": []
        }
        
        try:
            session_factory = get_session_factory()
            async with session_factory() as session:
                # Test query performance
                test_queries = [
                    ("users_count", "SELECT COUNT(*) FROM users"),
                    ("properties_count", "SELECT COUNT(*) FROM properties"),
                    ("properties_with_agents", """
                        SELECT COUNT(*) FROM properties p
                        INNER JOIN agents a ON p.assigned_agent_id = a.id
                    """),
                    ("recent_insights", """
                        SELECT COUNT(*) FROM ai_insights 
                        WHERE created_at > NOW() - INTERVAL '7 days'
                    """)
                ]
                
                for query_name, query_sql in test_queries:
                    import time
                    start_time = time.time()
                    
                    result = await session.execute(query_sql)
                    result.scalar()  # Execute the query
                    
                    end_time = time.time()
                    query_time = end_time - start_time
                    
                    performance_validation["query_times"][query_name] = query_time
                    
                    if query_time > 1.0:  # Slow query threshold
                        performance_validation["slow_queries"].append({
                            "query": query_name,
                            "time": query_time
                        })
                        logger.warning(f"✗ Slow query '{query_name}': {query_time:.3f}s")
                    else:
                        logger.info(f"✓ Query '{query_name}': {query_time:.3f}s")
        
        except Exception as e:
            performance_validation["issues"].append(f"Performance validation failed: {e}")
            logger.error(f"Performance validation error: {e}")
        
        return performance_validation
    
    async def run_full_validation(self) -> Dict[str, Any]:
        """Run complete database validation."""
        logger.info("Starting full database validation...")
        
        validation_results = {
            "configuration": await self.validate_configuration(),
            "connections": await self.validate_connections(),
            "schema": await self.validate_schema(),
            "data_integrity": await self.validate_data_integrity(),
            "performance": await self.validate_performance(),
            "overall_status": "unknown"
        }
        
        # Determine overall status
        all_issues = []
        for section in validation_results.values():
            if isinstance(section, dict) and "issues" in section:
                all_issues.extend(section["issues"])
        
        if not all_issues:
            validation_results["overall_status"] = "healthy"
            logger.info("✅ Database validation completed - All checks passed")
        else:
            validation_results["overall_status"] = "issues_found"
            logger.warning(f"⚠️ Database validation completed - {len(all_issues)} issues found")
        
        return validation_results
    
    def print_validation_report(self, results: Dict[str, Any]):
        """Print a detailed validation report."""
        logger.info("Database Validation Report")
        logger.info("=" * 50)
        
        # Overall status
        status_icon = "✅" if results["overall_status"] == "healthy" else "⚠️"
        logger.info(f"Overall Status: {status_icon} {results['overall_status']}")
        
        # Configuration
        config = results["configuration"]
        logger.info(f"\nConfiguration:")
        logger.info(f"  Supabase: {'✓' if config['supabase_configured'] else '✗'}")
        logger.info(f"  PostgreSQL: {'✓' if config['postgresql_configured'] else '✗'}")
        logger.info(f"  Redis: {'✓' if config['redis_configured'] else '✗'}")
        
        if config["issues"]:
            logger.info(f"  Issues: {', '.join(config['issues'])}")
        
        # Connections
        connections = results["connections"]
        logger.info(f"\nConnections:")
        logger.info(f"  Database: {'✓' if connections['database_connected'] else '✗'}")
        logger.info(f"  Redis: {'✓' if connections['redis_connected'] else '✗'}")
        logger.info(f"  Supabase: {'✓' if connections['supabase_connected'] else '✗'}")
        
        if connections["issues"]:
            logger.info(f"  Issues: {', '.join(connections['issues'])}")
        
        # Schema
        schema = results["schema"]
        logger.info(f"\nSchema:")
        tables_ok = all(schema["tables_exist"].values())
        indexes_ok = all(schema["indexes_exist"].values())
        logger.info(f"  Tables: {'✓' if tables_ok else '✗'}")
        logger.info(f"  Indexes: {'✓' if indexes_ok else '✗'}")
        
        if schema["issues"]:
            logger.info(f"  Issues: {', '.join(schema['issues'])}")
        
        # Data Integrity
        integrity = results["data_integrity"]
        logger.info(f"\nData Integrity:")
        for table, count in integrity["table_counts"].items():
            logger.info(f"  {table}: {count} records")
        
        if integrity["orphaned_records"]:
            logger.info(f"  Orphaned Records: {integrity['orphaned_records']}")
        
        if integrity["issues"]:
            logger.info(f"  Issues: {', '.join(integrity['issues'])}")
        
        # Performance
        performance = results["performance"]
        logger.info(f"\nPerformance:")
        for query, time in performance["query_times"].items():
            status = "✓" if time < 1.0 else "✗"
            logger.info(f"  {query}: {status} {time:.3f}s")
        
        if performance["slow_queries"]:
            logger.info(f"  Slow Queries: {len(performance['slow_queries'])}")

async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Janus Prop AI Database Validation")
    parser.add_argument("--full", action="store_true", help="Run full validation")
    parser.add_argument("--config", action="store_true", help="Validate configuration only")
    parser.add_argument("--connections", action="store_true", help="Validate connections only")
    parser.add_argument("--schema", action="store_true", help="Validate schema only")
    parser.add_argument("--data", action="store_true", help="Validate data integrity only")
    parser.add_argument("--performance", action="store_true", help="Validate performance only")
    
    args = parser.parse_args()
    
    if not any([args.full, args.config, args.connections, args.schema, args.data, args.performance]):
        parser.print_help()
        return
    
    validator = DatabaseValidator()
    
    try:
        if args.full:
            results = await validator.run_full_validation()
            validator.print_validation_report(results)
        else:
            if args.config:
                results = await validator.validate_configuration()
                logger.info("Configuration validation results:", **results)
            
            if args.connections:
                results = await validator.validate_connections()
                logger.info("Connection validation results:", **results)
            
            if args.schema:
                results = await validator.validate_schema()
                logger.info("Schema validation results:", **results)
            
            if args.data:
                results = await validator.validate_data_integrity()
                logger.info("Data integrity validation results:", **results)
            
            if args.performance:
                results = await validator.validate_performance()
                logger.info("Performance validation results:", **results)
    
    except KeyboardInterrupt:
        logger.info("Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error("Validation failed", error=str(e))
        sys.exit(1)
    finally:
        await close_database()

if __name__ == "__main__":
    asyncio.run(main())
