#!/usr/bin/env python3
"""
Environment setup helper for Janus Prop AI Backend

This script helps you set up your environment variables.
"""

import os
from pathlib import Path

def setup_env():
    """Set up environment variables."""
    print("🚀 Janus Prop AI Backend - Environment Setup")
    print("=" * 50)
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        choice = input("Do you want to overwrite it? (y/N): ").lower()
        if choice != 'y':
            print("Keeping existing .env file")
            return
    
    print("\n📋 Choose your database configuration:")
    print("1. Use Supabase (Recommended)")
    print("2. Use Local PostgreSQL")
    print("3. Skip database setup for now")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        setup_supabase(env_file)
    elif choice == "2":
        setup_local_db(env_file)
    elif choice == "3":
        setup_minimal(env_file)
    else:
        print("Invalid choice. Using minimal setup.")
        setup_minimal(env_file)

def setup_supabase(env_file):
    """Set up Supabase configuration."""
    print("\n🎯 Setting up Supabase configuration...")
    
    project_id = input("Enter your Supabase Project ID: ").strip()
    service_role_key = input("Enter your Supabase Service Role Key: ").strip()
    url = input("Enter your Supabase URL (e.g., https://project.supabase.co): ").strip()
    anon_key = input("Enter your Supabase Anon Key: ").strip()
    
    # Validate inputs
    if not all([project_id, service_role_key, url, anon_key]):
        print("❌ All fields are required for Supabase setup")
        return
    
    # Create .env content
    env_content = f"""# Supabase Configuration
SUPABASE_PROJECT_ID={project_id}
SUPABASE_SERVICE_ROLE_KEY={service_role_key}
SUPABASE_URL={url}
SUPABASE_ANON_KEY={anon_key}

# Optional: Local database fallback
# DATABASE_URL=postgresql://user:password@localhost:5432/janus_prop_ai

# Other settings
DEBUG=true
LOG_LEVEL=INFO
"""
    
    # Write to .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Supabase configuration saved to .env file")
    print("💡 Next steps:")
    print("   1. Test configuration: python test_supabase.py")
    print("   2. Apply schema: python scripts/apply_supabase_schema.py")
    print("   3. Start Backend: python start.py")

def setup_local_db(env_file):
    """Set up local database configuration."""
    print("\n🏠 Setting up local PostgreSQL configuration...")
    
    host = input("Enter database host (default: localhost): ").strip() or "localhost"
    port = input("Enter database port (default: 5432): ").strip() or "5432"
    database = input("Enter database name (default: janus_prop_ai): ").strip() or "janus_prop_ai"
    username = input("Enter database username: ").strip()
    password = input("Enter database password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required")
        return
    
    # Create .env content
    env_content = f"""# Local Database Configuration
DATABASE_URL=postgresql://{username}:{password}@{host}:{port}/{database}

# Other settings
DEBUG=true
LOG_LEVEL=INFO
"""
    
    # Write to .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Local database configuration saved to .env file")
    print("💡 Next steps:")
    print("   1. Ensure PostgreSQL is running")
    print("   2. Create database if it doesn't exist")
    print("   3. Start Backend: python start.py")

def setup_minimal(env_file):
    """Set up minimal configuration without database."""
    print("\n⚡ Setting up minimal configuration...")
    
    # Create .env content
    env_content = """# Minimal Configuration (No Database/Redis)
# This allows the Backend to start without external dependencies

# Database - Add when ready
# SUPABASE_PROJECT_ID=your_project_id
# SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
# SUPABASE_URL=https://your_project_id.supabase.co
# SUPABASE_ANON_KEY=your_anon_key

# Or for local database:
# DATABASE_URL=postgresql://username:password@localhost:5432/janus_prop_ai

# Redis - Add when ready
# REDIS_URL=redis://localhost:6379/0

# Basic settings
DEBUG=true
LOG_LEVEL=INFO
"""
    
    # Write to .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Minimal configuration saved to .env file")
    print("💡 Next steps:")
    print("   1. Start Backend: python start.py")
    print("   2. Configure database and Redis later when needed")
    print("   3. The Backend will run with limited functionality")

if __name__ == "__main__":
    setup_env()
