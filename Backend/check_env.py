#!/usr/bin/env python3
"""
Environment configuration checker for Janus Prop AI Backend

This script checks your environment variables and configuration.
"""

import os
from pathlib import Path

def check_env():
    """Check environment configuration."""
    print("🔍 Environment Configuration Check")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("❌ .env file not found")
        print("   Create a .env file in the Backend directory")
    
    # Check Supabase variables
    print("\n📋 Supabase Configuration:")
    supabase_vars = [
        "SUPABASE_PROJECT_ID",
        "SUPABASE_SERVICE_ROLE_KEY", 
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY"
    ]
    
    supabase_configured = True
    for var in supabase_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "KEY" in var:
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                display_value = value
            print(f"   {var}: ✅ {display_value}")
        else:
            print(f"   {var}: ❌ Not set")
            supabase_configured = False
    
    # Check database variables
    print("\n🗄️  Database Configuration:")
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        print(f"   DATABASE_URL: ✅ Set")
        if "localhost" in database_url:
            print("   📍 Using local database")
        else:
            print("   📍 Using remote database")
    else:
        print("   DATABASE_URL: ❌ Not set")
    
    # Summary
    print("\n📊 Configuration Summary:")
    if supabase_configured:
        print("   🎯 Supabase: Fully configured")
        print("   💡 The Backend will use Supabase as the database")
    elif any(os.getenv(var) for var in supabase_vars):
        print("   ⚠️  Supabase: Partially configured")
        print("   💡 Some Supabase variables are missing")
    else:
        print("   🏠 Supabase: Not configured")
        print("   💡 The Backend will use local database")
    
    if database_url:
        print("   🗄️  Local Database: Configured")
    else:
        print("   🗄️  Local Database: Not configured")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if not supabase_configured and not database_url:
        print("   1. Set up Supabase environment variables, OR")
        print("   2. Set DATABASE_URL for local PostgreSQL")
    elif not supabase_configured and database_url:
        print("   1. Complete Supabase configuration to use cloud database, OR")
        print("   2. Continue using local database")
    elif supabase_configured:
        print("   1. ✅ Ready to use Supabase!")
        print("   2. Apply the schema using: python scripts/apply_supabase_schema.py")
    
    print("\n🚀 Next Steps:")
    if supabase_configured:
        print("   1. Apply the Supabase schema")
        print("   2. Test the connection: python test_supabase.py")
        print("   3. Start the Backend: python start.py")
    else:
        print("   1. Complete your environment configuration")
        print("   2. Check SUPABASE_INTEGRATION.md for setup instructions")
        print("   3. Or use local database if preferred")

if __name__ == "__main__":
    check_env()
