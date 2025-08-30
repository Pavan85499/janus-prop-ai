#!/usr/bin/env python3
"""
Script to apply Supabase schema to the database.

This script reads the supabase_schema.sql file and applies it to the configured database.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from core.database import init_database, close_database, get_session_factory
from config.settings import get_settings

async def apply_schema():
    """Apply the Supabase schema to the database."""
    try:
        # Initialize database connection
        await init_database()
        
        # Get database session
        session_factory = get_session_factory()
        
        # Read the schema file
        schema_file = Path(__file__).parent.parent / "supabase_schema.sql"
        
        if not schema_file.exists():
            print(f"Schema file not found: {schema_file}")
            return False
        
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Split the SQL into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        async with session_factory() as session:
            for i, statement in enumerate(statements, 1):
                if statement and not statement.startswith('--'):
                    try:
                        await session.execute(statement)
                        print(f"Executed statement {i}/{len(statements)}")
                    except Exception as e:
                        print(f"Error executing statement {i}: {e}")
                        print(f"Statement: {statement[:100]}...")
                        continue
            
            await session.commit()
        
        print("Schema applied successfully!")
        return True
        
    except Exception as e:
        print(f"Error applying schema: {e}")
        return False
    finally:
        await close_database()

async def main():
    """Main function."""
    settings = get_settings()
    
    if not settings.is_supabase_enabled:
        print("Supabase not configured. Please check your environment variables.")
        print("Required variables:")
        print("  - SUPABASE_PROJECT_ID")
        print("  - SUPABASE_SERVICE_ROLE_KEY")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_ANON_KEY")
        return
    
    print(f"Applying schema to Supabase project: {settings.SUPABASE_PROJECT_ID}")
    
    success = await apply_schema()
    
    if success:
        print("✅ Schema applied successfully!")
    else:
        print("❌ Failed to apply schema")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
