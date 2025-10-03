#!/usr/bin/env python3
"""
Database Backup Script for Janus Prop AI Backend

This script provides database backup and restore functionality for both
Supabase and local PostgreSQL databases.
"""

import asyncio
import os
import sys
import argparse
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from core.database import init_database, close_database, get_session_factory
from core.supabase_client import get_supabase_client
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

class DatabaseBackup:
    """Database backup and restore management class."""
    
    def __init__(self):
        self.settings = get_settings()
        self.backup_dir = Path(__file__).parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def get_backup_filename(self, prefix: str = "backup") -> str:
        """Generate backup filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.sql"
    
    async def backup_supabase(self, filename: Optional[str] = None) -> str:
        """Backup Supabase database using pg_dump."""
        if not filename:
            filename = self.get_backup_filename("supabase")
        
        backup_path = self.backup_dir / filename
        
        try:
            # Get database connection details
            database_url = self.settings.supabase_database_url
            
            # Extract connection details from URL
            # Format: postgresql://user:password@host:port/database
            url_parts = database_url.replace("postgresql://", "").split("@")
            if len(url_parts) != 2:
                raise ValueError("Invalid database URL format")
            
            user_pass = url_parts[0].split(":")
            if len(user_pass) != 2:
                raise ValueError("Invalid user:password format")
            
            user, password = user_pass
            host_port_db = url_parts[1].split("/")
            if len(host_port_db) != 2:
                raise ValueError("Invalid host:port/database format")
            
            host_port = host_port_db[0].split(":")
            if len(host_port) != 2:
                raise ValueError("Invalid host:port format")
            
            host, port = host_port
            database = host_port_db[1]
            
            # Set password environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = password
            
            # Build pg_dump command
            cmd = [
                "pg_dump",
                f"--host={host}",
                f"--port={port}",
                f"--username={user}",
                f"--dbname={database}",
                "--verbose",
                "--clean",
                "--if-exists",
                "--create",
                "--format=plain",
                f"--file={backup_path}"
            ]
            
            logger.info(f"Running pg_dump for Supabase backup: {filename}")
            
            # Execute pg_dump
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("✅ Supabase backup completed successfully")
            logger.info(f"Backup saved to: {backup_path}")
            
            return str(backup_path)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"pg_dump failed: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"Supabase backup failed: {e}")
            raise
    
    async def backup_postgresql(self, filename: Optional[str] = None) -> str:
        """Backup local PostgreSQL database using pg_dump."""
        if not filename:
            filename = self.get_backup_filename("postgresql")
        
        backup_path = self.backup_dir / filename
        
        try:
            # Get database connection details
            database_url = self.settings.DATABASE_URL
            
            # Convert asyncpg URL to standard PostgreSQL URL
            if "postgresql+asyncpg://" in database_url:
                database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
            
            # Extract connection details from URL
            url_parts = database_url.replace("postgresql://", "").split("@")
            if len(url_parts) != 2:
                raise ValueError("Invalid database URL format")
            
            user_pass = url_parts[0].split(":")
            if len(user_pass) != 2:
                raise ValueError("Invalid user:password format")
            
            user, password = user_pass
            host_port_db = url_parts[1].split("/")
            if len(host_port_db) != 2:
                raise ValueError("Invalid host:port/database format")
            
            host_port = host_port_db[0].split(":")
            if len(host_port) != 2:
                raise ValueError("Invalid host:port format")
            
            host, port = host_port
            database = host_port_db[1]
            
            # Set password environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = password
            
            # Build pg_dump command
            cmd = [
                "pg_dump",
                f"--host={host}",
                f"--port={port}",
                f"--username={user}",
                f"--dbname={database}",
                "--verbose",
                "--clean",
                "--if-exists",
                "--create",
                "--format=plain",
                f"--file={backup_path}"
            ]
            
            logger.info(f"Running pg_dump for PostgreSQL backup: {filename}")
            
            # Execute pg_dump
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("✅ PostgreSQL backup completed successfully")
            logger.info(f"Backup saved to: {backup_path}")
            
            return str(backup_path)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"pg_dump failed: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"PostgreSQL backup failed: {e}")
            raise
    
    async def backup_data_only(self, filename: Optional[str] = None) -> str:
        """Backup only data (no schema) using Supabase client."""
        if not filename:
            filename = self.get_backup_filename("data")
        
        backup_path = self.backup_dir / filename
        
        try:
            # Initialize database
            await init_database()
            
            # Get all tables
            tables = [
                "users", "agents", "properties", "leads", 
                "market_data", "ai_insights", "user_agent_assignments"
            ]
            
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "tables": {}
            }
            
            session_factory = get_session_factory()
            async with session_factory() as session:
                for table in tables:
                    try:
                        # Get table data
                        result = await session.execute(f"SELECT * FROM {table}")
                        rows = result.fetchall()
                        
                        # Convert to list of dicts
                        table_data = []
                        for row in rows:
                            table_data.append(dict(row._mapping))
                        
                        backup_data["tables"][table] = table_data
                        logger.info(f"Backed up {len(table_data)} rows from {table}")
                        
                    except Exception as e:
                        logger.warning(f"Failed to backup table {table}: {e}")
                        backup_data["tables"][table] = []
            
            # Save backup to file
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            logger.info("✅ Data-only backup completed successfully")
            logger.info(f"Backup saved to: {backup_path}")
            
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Data-only backup failed: {e}")
            raise
    
    async def restore_from_backup(self, backup_path: str, drop_existing: bool = False) -> bool:
        """Restore database from backup file."""
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        try:
            if backup_path.suffix == '.json':
                # JSON data backup
                return await self.restore_from_json(backup_path, drop_existing)
            else:
                # SQL backup
                return await self.restore_from_sql(backup_path, drop_existing)
                
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    async def restore_from_sql(self, backup_path: Path, drop_existing: bool = False) -> bool:
        """Restore from SQL backup file."""
        try:
            # Get database connection details
            if self.settings.is_supabase_enabled:
                database_url = self.settings.supabase_database_url
            else:
                database_url = self.settings.DATABASE_URL
            
            # Convert asyncpg URL to standard PostgreSQL URL
            if "postgresql+asyncpg://" in database_url:
                database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
            
            # Extract connection details
            url_parts = database_url.replace("postgresql://", "").split("@")
            user_pass = url_parts[0].split(":")
            user, password = user_pass
            host_port_db = url_parts[1].split("/")
            host_port = host_port_db[0].split(":")
            host, port = host_port
            database = host_port_db[1]
            
            # Set password environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = password
            
            # Build psql command
            cmd = [
                "psql",
                f"--host={host}",
                f"--port={port}",
                f"--username={user}",
                f"--dbname={database}",
                "--file", str(backup_path)
            ]
            
            logger.info(f"Restoring from SQL backup: {backup_path}")
            
            # Execute psql
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("✅ SQL restore completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"psql failed: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            return False
    
    async def restore_from_json(self, backup_path: Path, drop_existing: bool = False) -> bool:
        """Restore from JSON data backup."""
        try:
            # Load backup data
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            # Initialize database
            await init_database()
            
            session_factory = get_session_factory()
            async with session_factory() as session:
                for table_name, table_data in backup_data.get("tables", {}).items():
                    if drop_existing:
                        # Clear existing data
                        await session.execute(f"TRUNCATE TABLE {table_name} CASCADE")
                        logger.info(f"Cleared existing data from {table_name}")
                    
                    # Insert backup data
                    if table_data:
                        for row in table_data:
                            # Build INSERT statement
                            columns = list(row.keys())
                            values = list(row.values())
                            placeholders = ", ".join([f":{col}" for col in columns])
                            
                            insert_sql = f"""
                                INSERT INTO {table_name} ({", ".join(columns)})
                                VALUES ({placeholders})
                                ON CONFLICT (id) DO UPDATE SET
                                {", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col != "id"])}
                            """
                            
                            await session.execute(insert_sql, row)
                        
                        logger.info(f"Restored {len(table_data)} rows to {table_name}")
                
                await session.commit()
            
            logger.info("✅ JSON restore completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"JSON restore failed: {e}")
            return False
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.sql"):
            stat = backup_file.stat()
            backups.append({
                "file": backup_file.name,
                "path": str(backup_file),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "type": "sql"
            })
        
        for backup_file in self.backup_dir.glob("*.json"):
            stat = backup_file.stat()
            backups.append({
                "file": backup_file.name,
                "path": str(backup_file),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "type": "json"
            })
        
        return sorted(backups, key=lambda x: x["created"], reverse=True)
    
    async def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """Clean up old backup files."""
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        deleted_count = 0
        
        for backup_file in self.backup_dir.glob("*"):
            if backup_file.is_file() and backup_file.stat().st_ctime < cutoff_date:
                backup_file.unlink()
                deleted_count += 1
                logger.info(f"Deleted old backup: {backup_file.name}")
        
        logger.info(f"Cleaned up {deleted_count} old backup files")
        return deleted_count

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Janus Prop AI Database Backup")
    parser.add_argument("--backup", choices=["full", "data"], help="Create backup (full or data-only)")
    parser.add_argument("--restore", help="Restore from backup file")
    parser.add_argument("--list", action="store_true", help="List available backups")
    parser.add_argument("--cleanup", type=int, metavar="DAYS", help="Clean up backups older than N days")
    parser.add_argument("--filename", help="Custom backup filename")
    parser.add_argument("--drop-existing", action="store_true", help="Drop existing data before restore")
    
    args = parser.parse_args()
    
    if not any([args.backup, args.restore, args.list, args.cleanup]):
        parser.print_help()
        return
    
    backup = DatabaseBackup()
    
    try:
        if args.list:
            backups = await backup.list_backups()
            logger.info("Available Backups:")
            logger.info("=" * 50)
            for backup_info in backups:
                size_mb = backup_info["size"] / (1024 * 1024)
                logger.info(f"{backup_info['file']} ({backup_info['type']}) - {size_mb:.2f}MB - {backup_info['created']}")
        
        if args.cleanup:
            deleted = await backup.cleanup_old_backups(args.cleanup)
            logger.info(f"Cleaned up {deleted} old backup files")
        
        if args.backup:
            if args.backup == "full":
                if backup.settings.is_supabase_enabled:
                    backup_path = await backup.backup_supabase(args.filename)
                else:
                    backup_path = await backup.backup_postgresql(args.filename)
            else:  # data-only
                backup_path = await backup.backup_data_only(args.filename)
            
            logger.info(f"Backup completed: {backup_path}")
        
        if args.restore:
            success = await backup.restore_from_backup(args.restore, args.drop_existing)
            if success:
                logger.info("✅ Restore completed successfully")
            else:
                logger.error("❌ Restore failed")
                sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Backup operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error("Backup operation failed", error=str(e))
        sys.exit(1)
    finally:
        await close_database()

if __name__ == "__main__":
    asyncio.run(main())
