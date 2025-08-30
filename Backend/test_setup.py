#!/usr/bin/env python3
"""
Test script for Janus Prop AI Backend

This script tests the basic setup and connectivity of the backend components.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def test_imports():
    """Test that all required modules can be imported."""
    print("Testing module imports...")
    
    try:
        from config.settings import get_settings
        print("✓ Settings module imported successfully")
        
        from core.database import init_database
        print("✓ Database module imported successfully")
        
        from core.redis_client import init_redis
        print("✓ Redis client module imported successfully")
        
        from core.websocket_manager import WebSocketManager
        print("✓ WebSocket manager module imported successfully")
        
        from core.realtime_manager import RealtimeManager
        print("✓ Real-time manager module imported successfully")
        
        from agents.agent_manager import AgentManager
        print("✓ Agent manager module imported successfully")
        
        from agents.gemini_ai_agent import GeminiAIAgent
        print("✓ Gemini AI agent module imported successfully")
        
        from agents.attom_data_agent import ATTOMDataAgent
        print("✓ ATTOM Data agent module imported successfully")
        
        from api.v1.api import api_router
        print("✓ API router imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

async def test_settings():
    """Test configuration settings."""
    print("\nTesting configuration settings...")
    
    try:
        from config.settings import get_settings
        settings = get_settings()
        
        print(f"✓ Server host: {settings.HOST}")
        print(f"✓ Server port: {settings.PORT}")
        print(f"✓ Debug mode: {settings.DEBUG}")
        print(f"✓ Database URL configured: {'Yes' if settings.DATABASE_URL else 'No'}")
        print(f"✓ Redis URL configured: {'Yes' if settings.REDIS_URL else 'No'}")
        print(f"✓ Gemini API key configured: {'Yes' if settings.GEMINI_API_KEY else 'No'}")
        print(f"✓ ATTOM API key configured: {'Yes' if settings.ATTOM_API_KEY else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"✗ Settings error: {e}")
        return False

async def test_agent_creation():
    """Test agent creation."""
    print("\nTesting agent creation...")
    
    try:
        from agents.agent_manager import AgentManager
        from agents.gemini_ai_agent import GeminiAIAgent
        from agents.attom_data_agent import ATTOMDataAgent
        
        # Test agent manager
        agent_manager = AgentManager()
        print(f"✓ Agent manager created with {len(agent_manager.agents)} agents")
        
        # Test Gemini agent
        gemini_agent = GeminiAIAgent()
        print(f"✓ Gemini agent created, initialized: {gemini_agent.is_initialized}")
        
        # Test ATTOM agent
        attom_agent = ATTOMDataAgent()
        print(f"✓ ATTOM agent created, initialized: {attom_agent.is_initialized}")
        
        return True
        
    except Exception as e:
        print(f"✗ Agent creation error: {e}")
        return False

async def test_api_structure():
    """Test API structure."""
    print("\nTesting API structure...")
    
    try:
        from api.v1.api import api_router
        
        # Check if router has routes
        routes = [route for route in api_router.routes]
        print(f"✓ API router has {len(routes)} routes")
        
        # List available routes
        for route in routes:
            if hasattr(route, 'path'):
                if hasattr(route, 'methods') and route.methods:
                    print(f"  - {route.path} [{', '.join(route.methods)}]")
                else:
                    print(f"  - {route.path} [WebSocket]")
        
        return True
        
    except Exception as e:
        print(f"✗ API structure error: {e}")
        return False

async def main():
    """Main test function."""
    print("Janus Prop AI Backend - Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports(),
        test_settings(),
        test_agent_creation(),
        test_api_structure()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    print("\n" + "=" * 50)
    print("Test Results:")
    
    passed = 0
    total = len(results)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Test {i+1}: ✗ Failed with error: {result}")
        elif result:
            print(f"Test {i+1}: ✓ Passed")
            passed += 1
        else:
            print(f"Test {i+1}: ✗ Failed")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend setup is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)
