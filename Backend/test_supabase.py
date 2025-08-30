#!/usr/bin/env python3
"""
Test script for Supabase integration.

This script tests the Supabase connection and basic functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent))

from config.settings import get_settings
from core.supabase_client import test_supabase_connection, get_supabase_config

async def test_supabase():
    """Test Supabase integration."""
    print("🔍 Testing Supabase Integration...")
    print("=" * 50)
    
    # Check configuration
    settings = get_settings()
    print(f"📋 Configuration Status:")
    print(f"   Supabase Enabled: {settings.is_supabase_enabled}")
    
    if not settings.is_supabase_enabled:
        print("\n❌ Supabase not configured!")
        print("Please set the following environment variables:")
        print("  - SUPABASE_PROJECT_ID")
        print("  - SUPABASE_SERVICE_ROLE_KEY")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_ANON_KEY")
        return False
    
    print(f"   Project ID: {settings.SUPABASE_PROJECT_ID}")
    print(f"   URL: {settings.SUPABASE_URL}")
    print(f"   Service Role Key: {'✅ Set' if settings.SUPABASE_SERVICE_ROLE_KEY else '❌ Missing'}")
    print(f"   Anon Key: {'✅ Set' if settings.SUPABASE_ANON_KEY else '❌ Missing'}")
    
    # Test connection
    print(f"\n🔌 Testing Connection...")
    try:
        connected = await test_supabase_connection()
        if connected:
            print("✅ Supabase connection successful!")
        else:
            print("❌ Supabase connection failed!")
            return False
    except Exception as e:
        print(f"❌ Connection test error: {e}")
        return False
    
    # Test configuration retrieval
    print(f"\n⚙️  Testing Configuration...")
    try:
        config = get_supabase_config()
        print(f"✅ Configuration retrieved successfully")
        print(f"   Config keys: {list(config.keys())}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    print(f"\n🎉 All tests passed! Supabase integration is working correctly.")
    return True

def main():
    """Main function."""
    try:
        success = asyncio.run(test_supabase())
        if success:
            print("\n🚀 Ready to use Supabase!")
            sys.exit(0)
        else:
            print("\n💥 Supabase integration failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
