#!/usr/bin/env python3
"""
Test AI Agents System for Janus Prop AI Backend

This script tests the AI agent system functionality.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from core.database import get_db
from services.ai_agent_service import AIAgentService
from services.ai_agent_orchestrator import AIAgentOrchestrator
from models.ai_agent import (
    AIAgentCreate, AgentType, TaskPriority,
    AgentTaskCreate, TaskStatus
)

async def test_ai_agents():
    """Test the AI agent system."""
    print("🧪 Testing AI Agents System...")
    
    # Get database session
    db = next(get_db())
    service = AIAgentService(db)
    orchestrator = AIAgentOrchestrator(db)
    
    try:
        # Start orchestrator
        await orchestrator.start()
        print("✅ Orchestrator started")
        
        # Test 1: Create a test agent
        print("\n📝 Test 1: Creating test agent...")
        test_agent = AIAgentCreate(
            name="TestAgent",
            agent_type=AgentType.AI_INSIGHTS,
            description="Test agent for validation",
            capabilities=["test_analysis"],
            max_concurrent_tasks=2,
            priority=TaskPriority.NORMAL
        )
        
        agent = await service.create_agent(test_agent)
        print(f"✅ Created test agent: {agent.name} ({agent.id})")
        
        # Test 2: Create a task for the agent
        print("\n📝 Test 2: Creating test task...")
        task_data = AgentTaskCreate(
            agent_id=agent.id,
            task_type="test_analysis",
            title="Test Analysis Task",
            description="Test task for validation",
            input_data={"test_input": "Hello World"},
            priority=TaskPriority.NORMAL
        )
        
        task = await service.create_task(task_data)
        print(f"✅ Created test task: {task.id}")
        
        # Test 3: Update task status
        print("\n📝 Test 3: Updating task status...")
        updated_task = await service.update_task(task.id, {
            "status": TaskStatus.RUNNING,
            "progress": 0.5
        })
        print(f"✅ Updated task status: {updated_task.status}")
        
        # Test 4: Create activity log
        print("\n📝 Test 4: Creating activity log...")
        activity = await service.create_activity({
            "agent_id": agent.id,
            "activity_type": "test_activity",
            "message": "Test activity for validation",
            "level": "info",
            "status": "completed",
            "task_id": task.id
        })
        print(f"✅ Created activity: {activity.id}")
        
        # Test 5: Get agent health
        print("\n📝 Test 5: Getting agent health...")
        health = await service.get_agent_health(agent.id)
        if health:
            print(f"✅ Agent health: {health['health_score']}")
        else:
            print("❌ Failed to get agent health")
        
        # Test 6: Get system health
        print("\n📝 Test 6: Getting system health...")
        system_health = await service.get_system_health()
        print(f"✅ System health: {system_health['system_health']}")
        print(f"   Total agents: {system_health['total_agents']}")
        print(f"   Online agents: {system_health['online_agents']}")
        
        # Test 7: Create workflow
        print("\n📝 Test 7: Creating test workflow...")
        workflow_id = await orchestrator.create_workflow(
            workflow_name="Test Workflow",
            workflow_type="property_analysis",
            input_data={
                "property_id": "test_property_123",
                "address": "123 Test Street, Test City, TC 12345"
            }
        )
        print(f"✅ Created workflow: {workflow_id}")
        
        # Test 8: Get workflow status
        print("\n📝 Test 8: Getting workflow status...")
        workflow_status = await orchestrator.get_workflow_status(workflow_id)
        if workflow_status:
            print(f"✅ Workflow status: {workflow_status['status']}")
            print(f"   Steps: {workflow_status['current_step']}/{workflow_status['total_steps']}")
        else:
            print("❌ Failed to get workflow status")
        
        # Test 9: Get orchestrator status
        print("\n📝 Test 9: Getting orchestrator status...")
        orchestrator_status = await orchestrator.get_orchestrator_status()
        print(f"✅ Orchestrator running: {orchestrator_status['is_running']}")
        print(f"   Active workflows: {orchestrator_status['workflows']['active']}")
        
        # Test 10: Clean up
        print("\n📝 Test 10: Cleaning up...")
        
        # Cancel workflow
        await orchestrator.cancel_workflow(workflow_id)
        print("✅ Cancelled workflow")
        
        # Update task to completed
        await service.update_task(task.id, {
            "status": TaskStatus.COMPLETED,
            "progress": 1.0,
            "output_data": {"test_result": "Success"}
        })
        print("✅ Completed task")
        
        # Delete test agent
        success = await service.delete_agent(agent.id)
        if success:
            print("✅ Deleted test agent")
        else:
            print("❌ Failed to delete test agent")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        raise
    finally:
        # Stop orchestrator
        await orchestrator.stop()
        db.close()

async def main():
    """Main function."""
    try:
        await test_ai_agents()
        print("\n✨ AI Agents system test completed successfully!")
        
    except Exception as e:
        print(f"\n💥 AI Agents system test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
