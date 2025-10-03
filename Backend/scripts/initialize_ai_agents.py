#!/usr/bin/env python3
"""
Initialize AI Agents for Janus Prop AI Backend

This script initializes the AI agent system with default agents and configurations.
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
    AgentCapabilityCreate
)

async def initialize_ai_agents():
    """Initialize AI agents and their capabilities."""
    print("🤖 Initializing AI Agents for Janus Prop AI...")
    
    # Get database session
    db = next(get_db())
    service = AIAgentService(db)
    orchestrator = AIAgentOrchestrator(db)
    
    try:
        # Start orchestrator
        await orchestrator.start()
        print("✅ AI Agent Orchestrator started")
        
        # Check if agents already exist
        existing_agents, _ = await service.get_agents(limit=1)
        if existing_agents:
            print("ℹ️  AI agents already exist, skipping initialization")
            return
        
        # Create default agents
        agents_to_create = [
            {
                "name": "Eden",
                "agent_type": AgentType.AI_INSIGHTS,
                "description": "AI Insights and Property Analysis Agent - Specialized in comprehensive property analysis, investment scoring, and market insights",
                "capabilities": [
                    "property_valuation",
                    "investment_scoring", 
                    "risk_assessment",
                    "market_analysis",
                    "comparable_analysis",
                    "neighborhood_analysis"
                ],
                "max_concurrent_tasks": 3,
                "priority": TaskPriority.HIGH
            },
            {
                "name": "Orion",
                "agent_type": AgentType.GEMINI,
                "description": "Google Gemini AI Integration Agent - Handles natural language processing, content generation, and advanced AI analysis",
                "capabilities": [
                    "natural_language_processing",
                    "content_generation",
                    "data_analysis",
                    "report_generation",
                    "conversational_ai",
                    "text_summarization"
                ],
                "max_concurrent_tasks": 5,
                "priority": TaskPriority.HIGH
            },
            {
                "name": "Atelius",
                "agent_type": AgentType.ATTOM,
                "description": "ATTOM Real Estate Data Agent - Manages property data collection, market data analysis, and comparable property research",
                "capabilities": [
                    "property_data_collection",
                    "market_data_analysis",
                    "comparable_property_research",
                    "property_history_analysis",
                    "market_trends_analysis",
                    "data_validation"
                ],
                "max_concurrent_tasks": 4,
                "priority": TaskPriority.HIGH
            },
            {
                "name": "Nova",
                "agent_type": AgentType.MARKET_ANALYSIS,
                "description": "Market Intelligence and Trends Agent - Analyzes market conditions, economic indicators, and investment trends",
                "capabilities": [
                    "market_condition_analysis",
                    "economic_indicator_analysis",
                    "trend_prediction",
                    "market_forecasting",
                    "investment_trend_analysis",
                    "market_volatility_assessment"
                ],
                "max_concurrent_tasks": 3,
                "priority": TaskPriority.NORMAL
            },
            {
                "name": "Zenith",
                "agent_type": AgentType.LEAD_MANAGEMENT,
                "description": "Lead Qualification and Management Agent - Handles lead scoring, qualification, and automated follow-up processes",
                "capabilities": [
                    "lead_scoring",
                    "lead_qualification",
                    "automated_follow_up",
                    "lead_nurturing",
                    "conversion_tracking",
                    "lead_prioritization"
                ],
                "max_concurrent_tasks": 2,
                "priority": TaskPriority.NORMAL
            },
            {
                "name": "Aurora",
                "agent_type": AgentType.PROPERTY_ANALYSIS,
                "description": "Advanced Property Analysis Agent - Specialized in detailed property inspections, renovation analysis, and investment strategies",
                "capabilities": [
                    "property_inspection_analysis",
                    "renovation_cost_estimation",
                    "flip_analysis",
                    "brrrr_strategy_analysis",
                    "rental_analysis",
                    "property_condition_assessment"
                ],
                "max_concurrent_tasks": 2,
                "priority": TaskPriority.NORMAL
            },
            {
                "name": "Celestia",
                "agent_type": AgentType.DOCUMENT_PROCESSING,
                "description": "Document Processing Agent - Handles document analysis, extraction, and processing for real estate transactions",
                "capabilities": [
                    "document_analysis",
                    "data_extraction",
                    "contract_review",
                    "compliance_checking",
                    "document_classification",
                    "automated_processing"
                ],
                "max_concurrent_tasks": 3,
                "priority": TaskPriority.NORMAL
            },
            {
                "name": "Valyria",
                "agent_type": AgentType.INVESTMENT_COMMITTEE,
                "description": "Investment Committee Agent - Manages investment decisions, committee debates, and investment memo generation",
                "capabilities": [
                    "investment_decision_analysis",
                    "committee_debate_management",
                    "investment_memo_generation",
                    "risk_benefit_analysis",
                    "consensus_building",
                    "decision_documentation"
                ],
                "max_concurrent_tasks": 2,
                "priority": TaskPriority.HIGH
            }
        ]
        
        created_agents = []
        
        for agent_data in agents_to_create:
            try:
                # Create agent
                agent_create = AIAgentCreate(**agent_data)
                agent = await service.create_agent(agent_create)
                created_agents.append(agent)
                
                print(f"✅ Created agent: {agent.name} ({agent.agent_type})")
                
                # Create capabilities for the agent
                await create_agent_capabilities(service, agent.id, agent_data["capabilities"])
                
            except Exception as e:
                print(f"❌ Failed to create agent {agent_data['name']}: {e}")
        
        # Start all agents
        print("\n🚀 Starting AI agents...")
        for agent in created_agents:
            try:
                await service.update_agent_status(agent.id, "online")
                print(f"✅ Started agent: {agent.name}")
            except Exception as e:
                print(f"❌ Failed to start agent {agent.name}: {e}")
        
        # Create sample workflows
        print("\n📋 Creating sample workflows...")
        await create_sample_workflows(orchestrator)
        
        print(f"\n🎉 Successfully initialized {len(created_agents)} AI agents!")
        print("\n📊 Agent Summary:")
        for agent in created_agents:
            print(f"  • {agent.name} ({agent.agent_type}) - {agent.description}")
        
        print("\n🔗 API Endpoints:")
        print("  • GET /api/v1/ai-agents/ - List all agents")
        print("  • GET /api/v1/ai-agents/{agent_id} - Get specific agent")
        print("  • POST /api/v1/ai-agents/{agent_id}/tasks - Create task for agent")
        print("  • GET /api/v1/ai-agents/health/system - System health status")
        print("  • WebSocket: /api/v1/ai-agents/ws/{agent_id} - Real-time updates")
        
    except Exception as e:
        print(f"❌ Failed to initialize AI agents: {e}")
        raise
    finally:
        db.close()

async def create_agent_capabilities(service: AIAgentService, agent_id: str, capabilities: list):
    """Create capabilities for an agent."""
    for capability_name in capabilities:
        try:
            capability_data = AgentCapabilityCreate(
                agent_id=agent_id,
                name=capability_name,
                description=f"Capability for {capability_name}",
                version="1.0.0"
            )
            
            await service.create_capability(capability_data)
            
        except Exception as e:
            print(f"⚠️  Failed to create capability {capability_name} for agent {agent_id}: {e}")

async def create_sample_workflows(orchestrator: AIAgentOrchestrator):
    """Create sample workflows for demonstration."""
    try:
        # Property Analysis Workflow
        workflow_id = await orchestrator.create_workflow(
            workflow_name="Sample Property Analysis",
            workflow_type="property_analysis",
            input_data={
                "property_id": "sample_property_123",
                "address": "123 Main Street, New York, NY 10001",
                "analysis_type": "comprehensive"
            }
        )
        print(f"✅ Created sample workflow: {workflow_id}")
        
        # Lead Qualification Workflow
        workflow_id = await orchestrator.create_workflow(
            workflow_name="Sample Lead Qualification",
            workflow_type="lead_qualification",
            input_data={
                "lead_data": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1-555-0123",
                    "address": "456 Oak Avenue, Brooklyn, NY 11201",
                    "investment_budget": 500000
                }
            }
        )
        print(f"✅ Created sample workflow: {workflow_id}")
        
    except Exception as e:
        print(f"⚠️  Failed to create sample workflows: {e}")

async def main():
    """Main function."""
    try:
        await initialize_ai_agents()
        print("\n✨ AI Agent initialization completed successfully!")
        
    except Exception as e:
        print(f"\n💥 AI Agent initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
