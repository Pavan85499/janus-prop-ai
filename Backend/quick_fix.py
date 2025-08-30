#!/usr/bin/env python3
"""
Quick fix script to create a minimal .env file
"""

from pathlib import Path

def create_minimal_env():
    """Create a minimal .env file."""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        choice = input("Do you want to overwrite it? (y/N): ").lower()
        if choice != 'y':
            print("Keeping existing .env file")
            return
    
    # Create minimal .env content
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
    
    print("✅ Minimal .env file created!")
    print("💡 Now you can start the Backend:")
    print("   python start.py")
    print("\n🔧 To add full functionality later:")
    print("   python setup_env.py")

if __name__ == "__main__":
    create_minimal_env()
