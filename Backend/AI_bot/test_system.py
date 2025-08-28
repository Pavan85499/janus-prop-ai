#!/usr/bin/env python3
"""
Test Script for Real Estate AI Agent System

This script demonstrates the basic functionality of the agent system
including agent queries and workflow execution.
"""

import asyncio
import json
from datetime import datetime

from agents.base_agent import AgentConfig
from agents.legal_agent import LegalAgent
from core.agent_manager import AgentManager


async def test_legal_agent():
    """Test the legal agent functionality."""
    print("🔍 Testing Legal Agent...")
    
    # Create agent configuration
    config = AgentConfig(
        name="Test Legal Agent",
        description="Test instance of legal analysis agent",
        model="gpt-4",
        temperature=0.1,
        max_tokens=4000,
        timeout=60
    )
    
    # Create legal agent
    legal_agent = LegalAgent(config)
    
    # Test contract review
    print("\n📋 Testing Contract Review...")
    contract_text = """
    PURCHASE AGREEMENT
    
    This agreement is made between John Doe (Buyer) and Jane Smith (Seller)
    for the purchase of property at 123 Main Street, Anytown, USA.
    
    Purchase Price: $500,000
    Closing Date: December 31, 2024
    Earnest Money: $10,000
    """
    
    response = await legal_agent.process_request(
        "Review this purchase agreement for compliance issues",
        {"document": contract_text}
    )
    
    if response.success:
        print("✅ Contract review completed successfully")
        print(f"📊 Analysis Type: {response.data['analysis_type']}")
        print(f"🎯 Confidence Score: {response.data['confidence_score']}")
        print(f"⏱️  Processing Time: {response.agent_response.processing_time:.2f}s")
    else:
        print(f"❌ Contract review failed: {response.error}")
    
    # Test compliance check
    print("\n⚖️ Testing Compliance Check...")
    compliance_response = await legal_agent.process_request(
        "Check this transaction for compliance with fair housing laws",
        {"transaction_type": "residential_purchase"}
    )
    
    if compliance_response.success:
        print("✅ Compliance check completed successfully")
        print(f"📊 Analysis Type: {compliance_response.data['analysis_type']}")
        print(f"🎯 Confidence Score: {compliance_response.data['confidence_score']}")
    else:
        print(f"❌ Compliance check failed: {compliance_response.error}")
    
    return legal_agent


async def test_agent_manager():
    """Test the agent manager functionality."""
    print("\n🏗️ Testing Agent Manager...")
    
    # Create agent manager
    manager = AgentManager()
    
    try:
        # Start the manager
        await manager.start()
        print("✅ Agent Manager started successfully")
        
        # Create and register a legal agent
        config = AgentConfig(
            name="Manager Legal Agent",
            description="Legal agent managed by agent manager",
            model="gpt-4",
            temperature=0.1,
            max_tokens=4000,
            timeout=60
        )
        
        legal_agent = LegalAgent(config)
        agent_id = await manager.register_agent(legal_agent, "legal")
        print(f"✅ Legal Agent registered with ID: {agent_id}")
        
        # Test agent query through manager
        print("\n🔍 Testing Agent Query Through Manager...")
        query_response = await manager.query_agent(
            "legal",
            "What are the key elements of a real estate purchase agreement?",
            {"context": "residential_purchase"}
        )
        
        if query_response.success:
            print("✅ Agent query completed successfully")
            print(f"📊 Analysis Type: {query_response.data['analysis_type']}")
            print(f"🎯 Confidence Score: {query_response.data['confidence_score']}")
        else:
            print(f"❌ Agent query failed: {query_response.error}")
        
        # Test workflow creation
        print("\n🔄 Testing Workflow Creation...")
        workflow_definition = [
            {
                "agent": "legal",
                "task": "contract_review",
                "data": {"contract_type": "purchase_agreement"}
            },
            {
                "agent": "legal",
                "task": "compliance_check",
                "data": {"check_type": "fair_housing"},
                "dependencies": [0]  # Depends on first step
            }
        ]
        
        workflow = await manager.create_workflow(workflow_definition)
        print(f"✅ Workflow created with ID: {workflow.workflow_id}")
        print(f"📋 Workflow has {len(workflow.steps)} steps")
        
        # Get system status
        status = await manager.get_system_status()
        print(f"\n📊 System Status:")
        print(f"   Total Agents: {status['total_agents']}")
        print(f"   Agent Types: {status['agent_types']}")
        print(f"   Active Workflows: {status['active_workflows']}")
        
    finally:
        # Stop the manager
        await manager.stop()
        print("✅ Agent Manager stopped")


async def test_workflow_execution():
    """Test workflow execution functionality."""
    print("\n🚀 Testing Workflow Execution...")
    
    # Create agent manager
    manager = AgentManager()
    
    try:
        # Start the manager
        await manager.start()
        
        # Register a legal agent
        config = AgentConfig(
            name="Workflow Legal Agent",
            description="Legal agent for workflow testing",
            model="gpt-4",
            temperature=0.1,
            max_tokens=4000,
            timeout=60
        )
        
        legal_agent = LegalAgent(config)
        await manager.register_agent(legal_agent, "legal")
        
        # Create a simple workflow
        workflow_definition = [
            {
                "agent": "legal",
                "task": "contract_review",
                "data": {"contract_type": "purchase_agreement"}
            }
        ]
        
        workflow = await manager.create_workflow(workflow_definition)
        print(f"✅ Workflow created: {workflow.workflow_id}")
        
        # Execute the workflow
        print("🔄 Executing workflow...")
        start_time = datetime.utcnow()
        
        results = await manager.execute_workflow(workflow.workflow_id)
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        print(f"✅ Workflow executed in {execution_time:.2f} seconds")
        print(f"📊 Results: {len(results)} step(s) completed")
        
        # Print step results
        for step_id, result in results.items():
            print(f"   Step {step_id}: {result['analysis_type']}")
        
    finally:
        await manager.stop()


async def main():
    """Main test function."""
    print("🏠 Real Estate AI Agent System - Test Suite")
    print("=" * 50)
    
    try:
        # Test individual agent
        await test_legal_agent()
        
        # Test agent manager
        await test_agent_manager()
        
        # Test workflow execution
        await test_workflow_execution()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
