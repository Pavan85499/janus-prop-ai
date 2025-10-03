#!/usr/bin/env python3
"""
Database Migration Script for Janus Prop AI Backend

This script handles database migrations and schema updates.
"""

import asyncio
import os
import sys
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from core.database import init_database, close_database, get_session_factory
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

class DatabaseMigrator:
    """Database migration management class."""
    
    def __init__(self):
        self.settings = get_settings()
        self.migrations_dir = Path(__file__).parent / "migrations"
        self.migrations_dir.mkdir(exist_ok=True)
    
    async def create_migration(self, name: str, description: str = "") -> str:
        """Create a new migration file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.sql"
        filepath = self.migrations_dir / filename
        
        migration_content = f"""-- Migration: {name}
-- Created: {datetime.now().isoformat()}
-- Description: {description}

-- Add your migration SQL here
-- Example:
-- ALTER TABLE users ADD COLUMN new_field VARCHAR(255);
-- CREATE INDEX idx_users_new_field ON users(new_field);

-- Rollback SQL (for down migration)
-- Example:
-- ALTER TABLE users DROP COLUMN new_field;
"""
        
        with open(filepath, 'w') as f:
            f.write(migration_content)
        
        logger.info(f"Created migration file: {filepath}")
        return str(filepath)
    
    async def list_migrations(self) -> List[Dict[str, Any]]:
        """List all available migrations."""
        migrations = []
        
        for filepath in self.migrations_dir.glob("*.sql"):
            if filepath.is_file():
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Extract metadata from comments
                lines = content.split('\n')
                name = filepath.stem
                created = None
                description = ""
                
                for line in lines[:10]:  # Check first 10 lines for metadata
                    if line.startswith('-- Migration:'):
                        name = line.replace('-- Migration:', '').strip()
                    elif line.startswith('-- Created:'):
                        created = line.replace('-- Created:', '').strip()
                    elif line.startswith('-- Description:'):
                        description = line.replace('-- Description:', '').strip()
                
                migrations.append({
                    "file": filepath.name,
                    "name": name,
                    "created": created,
                    "description": description,
                    "path": str(filepath)
                })
        
        return sorted(migrations, key=lambda x: x["file"])
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations from database."""
        try:
            session_factory = get_session_factory()
            async with session_factory() as session:
                # Check if migrations table exists
                result = await session.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'migrations'
                    );
                """)
                
                if not result.scalar():
                    # Create migrations table
                    await session.execute("""
                        CREATE TABLE migrations (
                            id SERIAL PRIMARY KEY,
                            filename VARCHAR(255) UNIQUE NOT NULL,
                            applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            checksum VARCHAR(64)
                        );
                    """)
                    await session.commit()
                    return []
                
                # Get applied migrations
                result = await session.execute("""
                    SELECT filename FROM migrations ORDER BY applied_at;
                """)
                
                return [row[0] for row in result.fetchall()]
                
        except Exception as e:
            logger.error("Failed to get applied migrations", error=str(e))
            return []
    
    async def apply_migration(self, migration_path: str, dry_run: bool = False) -> bool:
        """Apply a single migration."""
        try:
            with open(migration_path, 'r') as f:
                content = f.read()
            
            # Split content into up and down migrations
            parts = content.split('-- Rollback SQL (for down migration)')
            up_sql = parts[0].strip()
            down_sql = parts[1].strip() if len(parts) > 1 else ""
            
            # Remove comments and empty lines
            up_statements = []
            for line in up_sql.split('\n'):
                line = line.strip()
                if line and not line.startswith('--'):
                    up_statements.append(line)
            
            if not up_statements:
                logger.warning(f"No SQL statements found in {migration_path}")
                return True
            
            if dry_run:
                logger.info(f"DRY RUN - Would apply migration: {migration_path}")
                for stmt in up_statements:
                    logger.info(f"  {stmt}")
                return True
            
            session_factory = get_session_factory()
            async with session_factory() as session:
                # Apply each statement
                for stmt in up_statements:
                    if stmt:
                        await session.execute(stmt)
                        logger.info(f"Executed: {stmt[:100]}...")
                
                # Record migration as applied
                filename = Path(migration_path).name
                await session.execute("""
                    INSERT INTO migrations (filename, applied_at) 
                    VALUES (:filename, NOW())
                    ON CONFLICT (filename) DO NOTHING;
                """, {"filename": filename})
                
                await session.commit()
            
            logger.info(f"✅ Applied migration: {migration_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply migration {migration_path}", error=str(e))
            return False
    
    async def rollback_migration(self, migration_path: str, dry_run: bool = False) -> bool:
        """Rollback a single migration."""
        try:
            with open(migration_path, 'r') as f:
                content = f.read()
            
            # Extract rollback SQL
            parts = content.split('-- Rollback SQL (for down migration)')
            if len(parts) < 2:
                logger.warning(f"No rollback SQL found in {migration_path}")
                return True
            
            down_sql = parts[1].strip()
            
            # Remove comments and empty lines
            down_statements = []
            for line in down_sql.split('\n'):
                line = line.strip()
                if line and not line.startswith('--'):
                    down_statements.append(line)
            
            if not down_statements:
                logger.warning(f"No rollback statements found in {migration_path}")
                return True
            
            if dry_run:
                logger.info(f"DRY RUN - Would rollback migration: {migration_path}")
                for stmt in down_statements:
                    logger.info(f"  {stmt}")
                return True
            
            session_factory = get_session_factory()
            async with session_factory() as session:
                # Apply rollback statements
                for stmt in down_statements:
                    if stmt:
                        await session.execute(stmt)
                        logger.info(f"Executed rollback: {stmt[:100]}...")
                
                # Remove migration record
                filename = Path(migration_path).name
                await session.execute("""
                    DELETE FROM migrations WHERE filename = :filename;
                """, {"filename": filename})
                
                await session.commit()
            
            logger.info(f"✅ Rolled back migration: {migration_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback migration {migration_path}", error=str(e))
            return False
    
    async def migrate_up(self, target: Optional[str] = None, dry_run: bool = False) -> bool:
        """Apply pending migrations."""
        logger.info("Running migrations...")
        
        try:
            # Initialize database
            await init_database()
            
            # Get available and applied migrations
            available_migrations = await self.list_migrations()
            applied_migrations = await self.get_applied_migrations()
            
            # Find pending migrations
            pending_migrations = [
                m for m in available_migrations 
                if m["file"] not in applied_migrations
            ]
            
            if target:
                # Apply migrations up to target
                pending_migrations = [
                    m for m in pending_migrations 
                    if m["file"] <= target
                ]
            
            if not pending_migrations:
                logger.info("No pending migrations")
                return True
            
            logger.info(f"Found {len(pending_migrations)} pending migrations")
            
            # Apply each migration
            for migration in pending_migrations:
                success = await self.apply_migration(migration["path"], dry_run)
                if not success:
                    logger.error(f"Migration failed: {migration['file']}")
                    return False
            
            logger.info("✅ All migrations applied successfully")
            return True
            
        except Exception as e:
            logger.error("Migration failed", error=str(e))
            return False
    
    async def migrate_down(self, target: str, dry_run: bool = False) -> bool:
        """Rollback migrations down to target."""
        logger.info(f"Rolling back migrations to: {target}")
        
        try:
            # Initialize database
            await init_database()
            
            # Get applied migrations
            applied_migrations = await self.get_applied_migrations()
            
            # Find migrations to rollback
            migrations_to_rollback = [
                m for m in applied_migrations 
                if m > target
            ]
            
            if not migrations_to_rollback:
                logger.info("No migrations to rollback")
                return True
            
            logger.info(f"Found {len(migrations_to_rollback)} migrations to rollback")
            
            # Rollback in reverse order
            for migration_file in reversed(migrations_to_rollback):
                migration_path = self.migrations_dir / migration_file
                if migration_path.exists():
                    success = await self.rollback_migration(str(migration_path), dry_run)
                    if not success:
                        logger.error(f"Rollback failed: {migration_file}")
                        return False
            
            logger.info("✅ All migrations rolled back successfully")
            return True
            
        except Exception as e:
            logger.error("Rollback failed", error=str(e))
            return False
    
    async def status(self):
        """Show migration status."""
        logger.info("Migration Status")
        logger.info("=" * 50)
        
        try:
            await init_database()
            
            available_migrations = await self.list_migrations()
            applied_migrations = await self.get_applied_migrations()
            
            logger.info(f"Available migrations: {len(available_migrations)}")
            logger.info(f"Applied migrations: {len(applied_migrations)}")
            logger.info(f"Pending migrations: {len(available_migrations) - len(applied_migrations)}")
            
            logger.info("\nMigration Details:")
            for migration in available_migrations:
                status = "✓" if migration["file"] in applied_migrations else "✗"
                logger.info(f"  {status} {migration['file']} - {migration['name']}")
                if migration['description']:
                    logger.info(f"    {migration['description']}")
            
        except Exception as e:
            logger.error("Failed to get migration status", error=str(e))

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Janus Prop AI Database Migrations")
    parser.add_argument("--create", help="Create a new migration with given name")
    parser.add_argument("--description", help="Description for new migration")
    parser.add_argument("--up", action="store_true", help="Apply pending migrations")
    parser.add_argument("--down", help="Rollback migrations to target")
    parser.add_argument("--target", help="Target migration for up/down")
    parser.add_argument("--status", action="store_true", help="Show migration status")
    parser.add_argument("--list", action="store_true", help="List all migrations")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")
    
    args = parser.parse_args()
    
    if not any([args.create, args.up, args.down, args.status, args.list]):
        parser.print_help()
        return
    
    migrator = DatabaseMigrator()
    
    try:
        if args.create:
            await migrator.create_migration(args.create, args.description or "")
        
        if args.list:
            migrations = await migrator.list_migrations()
            logger.info("Available Migrations:")
            for migration in migrations:
                logger.info(f"  {migration['file']} - {migration['name']}")
                if migration['description']:
                    logger.info(f"    {migration['description']}")
        
        if args.status:
            await migrator.status()
        
        if args.up:
            success = await migrator.migrate_up(args.target, args.dry_run)
            if not success:
                sys.exit(1)
        
        if args.down:
            if not args.target:
                logger.error("Target migration required for rollback")
                sys.exit(1)
            success = await migrator.migrate_down(args.target, args.dry_run)
            if not success:
                sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error("Migration failed", error=str(e))
        sys.exit(1)
    finally:
        await close_database()

if __name__ == "__main__":
    asyncio.run(main())
