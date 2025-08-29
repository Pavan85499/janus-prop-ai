"""
Main Application Entry Point for Real Estate AI Agent System

This module initializes and runs the complete agent system, including
all specialized agents, the agent manager, and the communication system.
"""

import asyncio
import signal
import sys
from typing import Dict, Any

import structlog
from pydantic import BaseModel

from agents.base_agent import AgentConfig
from agents.legal_agent import LegalAgent
from agents.ai_insights_agent import AIInsightsAgent
from agents.data_integration_agent import DataIntegrationAgent
from agents.feedback_learning_agent import FeedbackLearningAgent
from core.agent_manager import AgentManager


class SystemConfig(BaseModel):
    """Configuration for the entire system."""
    
    # Agent configurations
    legal_agent: AgentConfig = AgentConfig(
        name="Legal Analysis Agent",
        description="Specializes in legal analysis, contract review, and compliance checking",
        model="gpt-4",
        temperature=0.1,
        max_tokens=4000,
        timeout=60
    )
    
    ai_insights_agent: AgentConfig = AgentConfig(
        name="AI Insights Agent",
        description="Provides explainable AI insights and actionable recommendations",
        model="gpt-4",
        temperature=0.1,
        max_tokens=4000,
        timeout=60
    )
    
    data_integration_agent: AgentConfig = AgentConfig(
        name="Data Integration Agent",
        description="Handles data integration from multiple sources including Realie API",
        model="gpt-4",
        temperature=0.1,
        max_tokens=4000,
        timeout=60
    )
    
    feedback_learning_agent: AgentConfig = AgentConfig(
        name="Feedback & Learning Agent",
        description="Implements continuous learning and monitors AI accuracy",
        model="gpt-4",
        temperature=0.1,
        max_tokens=4000,
        timeout=60
    )
    
    # System settings
    log_level: str = "INFO"
    health_check_interval: int = 30  # seconds
    max_concurrent_agents: int = 10
    system_timeout: int = 300  # seconds


class RealEstateAgentSystem:
    """
    Main system class that orchestrates all agents and provides the system interface.
    """
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.agent_manager = AgentManager()
        self.running = False
        self.logger = structlog.get_logger(self.__class__.__name__)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    async def start(self):
        """Start the real estate agent system."""
        try:
            self.logger.info("Starting Real Estate AI Agent System")
            
            # Start the agent manager
            await self.agent_manager.start()
            
            # Initialize and register agents
            await self._initialize_agents()
            
            self.running = True
            self.logger.info("Real Estate AI Agent System started successfully")
            
            # Keep the system running
            await self._run_system()
            
        except Exception as e:
            self.logger.error("Failed to start system", error=str(e))
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the real estate agent system."""
        if not self.running:
            return
        
        self.logger.info("Stopping Real Estate AI Agent System")
        self.running = False
        
        try:
            # Stop the agent manager
            await self.agent_manager.stop()
            self.logger.info("Real Estate AI Agent System stopped successfully")
        except Exception as e:
            self.logger.error("Error during system shutdown", error=str(e))
    
    async def _initialize_agents(self):
        """Initialize and register all agents with the system."""
        self.logger.info("Initializing agents")
        
        try:
            # Initialize Legal Agent
            legal_agent = LegalAgent(self.config.legal_agent)
            await self.agent_manager.register_agent(legal_agent, "legal")
            self.logger.info("Legal Agent initialized and registered")
            
            # Initialize AI Insights Agent
            ai_insights_agent = AIInsightsAgent(self.config.ai_insights_agent)
            await self.agent_manager.register_agent(ai_insights_agent, "ai_insights")
            self.logger.info("AI Insights Agent initialized and registered")
            
            # Initialize Data Integration Agent
            data_integration_agent = DataIntegrationAgent(self.config.data_integration_agent)
            await self.agent_manager.register_agent(data_integration_agent, "data_integration")
            self.logger.info("Data Integration Agent initialized and registered")
            
            # Initialize Feedback & Learning Agent
            feedback_learning_agent = FeedbackLearningAgent(self.config.feedback_learning_agent)
            await self.agent_manager.register_agent(feedback_learning_agent, "feedback_learning")
            self.logger.info("Feedback & Learning Agent initialized and registered")
            
            self.logger.info(f"All agents initialized. Total agents: {len(self.agent_manager.agents)}")
            
        except Exception as e:
            self.logger.error("Failed to initialize agents", error=str(e))
            raise
    
    async def _run_system(self):
        """Main system loop."""
        self.logger.info("System running. Press Ctrl+C to stop.")
        
        try:
            while self.running:
                # Perform periodic system maintenance
                await self._perform_system_maintenance()
                
                # Wait before next maintenance cycle
                await asyncio.sleep(self.config.health_check_interval)
                
        except asyncio.CancelledError:
            self.logger.info("System loop cancelled")
        except Exception as e:
            self.logger.error("Error in system loop", error=str(e))
            raise
    
    async def _perform_system_maintenance(self):
        """Perform periodic system maintenance tasks."""
        try:
            # Get system status
            status = await self.agent_manager.get_system_status()
            
            # Log system status
            self.logger.info(
                "System status",
                total_agents=status["total_agents"],
                agent_types=status["agent_types"],
                active_workflows=status["active_workflows"]
            )
            
            # Check for any system issues
            if status["total_agents"] == 0:
                self.logger.warning("No agents are currently registered")
            
            # TODO: Add more maintenance tasks as needed
            
        except Exception as e:
            self.logger.error("Error during system maintenance", error=str(e))
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.logger.info(f"Received signal {signum}, initiating shutdown")
        asyncio.create_task(self.stop())
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get the current system status."""
        return await self.agent_manager.get_system_status()
    
    async def query_agent(self, agent_type: str, query: str, context: Dict[str, Any] = None):
        """Query a specific agent type."""
        return await self.agent_manager.query_agent(agent_type, query, context)
    
    async def create_workflow(self, workflow_definition: list):
        """Create a new workflow."""
        return await self.agent_manager.create_workflow(workflow_definition)
    
    async def execute_workflow(self, workflow_id: str):
        """Execute a workflow."""
        return await self.agent_manager.execute_workflow(workflow_id)


async def main():
    """Main entry point for the application."""
    # Configure logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    logger = structlog.get_logger()
    logger.info("Initializing Real Estate AI Agent System")
    
    try:
        # Create system configuration
        config = SystemConfig()
        
        # Create and start the system
        system = RealEstateAgentSystem(config)
        
        # Start the system
        await system.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down")
    except Exception as e:
        logger.error("System error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    try:
        # Run the main application
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSystem shutdown complete")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
