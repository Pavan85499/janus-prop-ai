"""
Agent Manager for Janus Prop AI Backend

This module manages all AI agents and coordinates their activities.
"""

import asyncio
import structlog
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from uuid import uuid4
from dataclasses import dataclass, field

from core.redis_client import publish_event, cache_set, cache_get
from core.websocket_manager import get_websocket_manager

logger = structlog.get_logger(__name__)

@dataclass
class AgentConfig:
    """Configuration for an AI agent."""
    agent_id: str
    name: str
    agent_type: str  # "ai_insights", "gemini", "attom", "market_analysis"
    description: str
    is_active: bool = True
    max_concurrent_tasks: int = 5
    priority: str = "normal"  # "low", "normal", "high", "urgent"
    config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentTask:
    """Task for an AI agent."""
    task_id: str
    agent_id: str
    task_type: str
    priority: str
    status: str  # "pending", "running", "completed", "failed", "cancelled"
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentStatus:
    """Status of an AI agent."""
    agent_id: str
    status: str  # "online", "offline", "busy", "error"
    last_heartbeat: datetime
    current_tasks: int = 0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    average_response_time: float = 0.0
    health_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class AgentManager:
    """Manages all AI agents and their activities."""
    
    def __init__(self):
        self.agents: Dict[str, AgentConfig] = {}
        self.agent_statuses: Dict[str, AgentStatus] = {}
        self.tasks: Dict[str, AgentTask] = {}
        self.task_queues: Dict[str, asyncio.Queue] = {}
        self.agent_handlers: Dict[str, Callable] = {}
        self.is_running = False
        self.background_tasks: List[asyncio.Task] = []
        
        # Import agent handlers
        try:
            from agents.gemini_ai_agent import gemini_agent_handler
        except ImportError:
            gemini_agent_handler = None
        
        try:
            from agents.attom_data_agent import attom_agent_handler
        except ImportError:
            attom_agent_handler = None
        
        try:
            from agents.deal_sourcing_agent import deal_sourcing_agent_handler
        except ImportError:
            deal_sourcing_agent_handler = None
        
        try:
            from agents.document_ingestion_agent import document_ingestion_agent_handler
        except ImportError:
            document_ingestion_agent_handler = None
        
        try:
            from agents.automated_underwriting_agent import underwriting_agent_handler
        except ImportError:
            underwriting_agent_handler = None
        
        try:
            from agents.legal_compliance_agent import legal_compliance_agent_handler
        except ImportError:
            legal_compliance_agent_handler = None
        
        try:
            from agents.ai_investment_committee_agent import investment_committee_agent_handler
        except ImportError:
            investment_committee_agent_handler = None

        # New Janus agents
        try:
            from agents.eden_agent import eden_agent_handler
        except ImportError:
            eden_agent_handler = None
        try:
            from agents.orion_agent import orion_agent_handler
        except ImportError:
            orion_agent_handler = None
        try:
            from agents.atelius_agent import atelius_agent_handler
        except ImportError:
            atelius_agent_handler = None
        try:
            from agents.osiris_agent import osiris_agent_handler
        except ImportError:
            osiris_agent_handler = None
        
        # Register agent handlers
        self.agent_handlers = {}
        
        if gemini_agent_handler:
            self.agent_handlers["gemini"] = gemini_agent_handler
        if attom_agent_handler:
            self.agent_handlers["attom"] = attom_agent_handler
        if deal_sourcing_agent_handler:
            self.agent_handlers["deal_sourcing"] = deal_sourcing_agent_handler
        if document_ingestion_agent_handler:
            self.agent_handlers["document_ingestion"] = document_ingestion_agent_handler
        if underwriting_agent_handler:
            self.agent_handlers["automated_underwriting"] = underwriting_agent_handler
        if legal_compliance_agent_handler:
            self.agent_handlers["legal_compliance"] = legal_compliance_agent_handler
        if investment_committee_agent_handler:
            self.agent_handlers["ai_investment_committee"] = investment_committee_agent_handler
        # Register new Janus agents
        if eden_agent_handler:
            self.agent_handlers["eden"] = eden_agent_handler
        if orion_agent_handler:
            self.agent_handlers["orion"] = orion_agent_handler
        if atelius_agent_handler:
            self.agent_handlers["atelius"] = atelius_agent_handler
        if osiris_agent_handler:
            self.agent_handlers["osiris"] = osiris_agent_handler
        
        # Legacy and placeholder handlers
        self.agent_handlers.update({
            "ai_insights": self._handle_ai_insights,
            "market_analysis": self._handle_market_analysis,
            "lead_management": self._handle_lead_management,
            "execution_closing": self._handle_execution_closing,
            "post_acquisition": self._handle_post_acquisition
        })
    
    def _initialize_default_agents(self):
        """Initialize default AI agents."""
        default_agents = [
            # Legacy agents
            AgentConfig(
                agent_id="eden",
                name="Eden",
                agent_type="eden",
                description="Investment Decision Agent - ranks deals and makes final calls",
                max_concurrent_tasks=3,
                priority="high"
            ),
            AgentConfig(
                agent_id="orion",
                name="Orion",
                agent_type="orion",
                description="Monitoring Agent - collects tax liens, auctions, violations, court activity",
                max_concurrent_tasks=4,
                priority="high"
            ),
            AgentConfig(
                agent_id="atelius",
                name="Atelius",
                agent_type="atelius",
                description="Legal Agent - parses filings, redemption rules, legal risks, title chains",
                max_concurrent_tasks=3,
                priority="high"
            ),
            AgentConfig(
                agent_id="osiris",
                name="Osiris",
                agent_type="osiris",
                description="Forecasting Agent - projects returns, redemption windows, yield",
                max_concurrent_tasks=4,
                priority="high"
            ),
            AgentConfig(
                agent_id="nova",
                name="Nova",
                agent_type="market_analysis",
                description="Market Intelligence and Trends Agent",
                max_concurrent_tasks=3,
                priority="normal"
            ),
            AgentConfig(
                agent_id="zenith",
                name="Zenith",
                agent_type="lead_management",
                description="Lead Qualification and Management Agent",
                max_concurrent_tasks=2,
                priority="normal"
            ),
            # New specialized agents for complete real estate lifecycle
            AgentConfig(
                agent_id="prospector",
                name="Prospector",
                agent_type="deal_sourcing",
                description="Deal Sourcing & Discovery Agent - Scans millions of properties for distressed, undervalued, or high-potential assets",
                max_concurrent_tasks=3,
                priority="high",
                config={
                    "scan_radius_default": 25,
                    "min_equity_threshold": 20000,
                    "max_properties_per_scan": 1000
                }
            ),
            AgentConfig(
                agent_id="documentarian",
                name="Documentarian",
                agent_type="document_ingestion",
                description="Document Ingestion & Parsing Agent - Processes deeds, leases, inspections, and financials into structured data",
                max_concurrent_tasks=5,
                priority="high",
                config={
                    "max_file_size": 50 * 1024 * 1024,  # 50MB
                    "supported_formats": ["pdf", "docx", "jpg", "png", "txt"]
                }
            ),
            AgentConfig(
                agent_id="underwriter",
                name="Underwriter",
                agent_type="automated_underwriting",
                description="Automated Underwriting & Analysis Agent - Instant cash-flow models, rent comps, renovation scenarios, and cap rates",
                max_concurrent_tasks=4,
                priority="high",
                config={
                    "default_cap_rate": 0.08,
                    "default_cash_on_cash": 0.10,
                    "analysis_confidence_threshold": 0.7
                }
            ),
            AgentConfig(
                agent_id="compliance_officer",
                name="Compliance Officer",
                agent_type="legal_compliance",
                description="Legal & Compliance Agent - Automated review of ownership, zoning, permits, liens, and tax history",
                max_concurrent_tasks=3,
                priority="high",
                config={
                    "risk_tolerance": "medium",
                    "compliance_depth": "comprehensive"
                }
            ),
            AgentConfig(
                agent_id="investment_committee",
                name="Investment Committee",
                agent_type="ai_investment_committee",
                description="AI Investment Committee - Panel of agents that debates pros and cons, surfacing risks and opportunities",
                max_concurrent_tasks=2,
                priority="high",
                config={
                    "committee_size": 5,
                    "decision_threshold": 0.7,
                    "debate_rounds": 3
                }
            ),
            AgentConfig(
                agent_id="deal_closer",
                name="Deal Closer",
                agent_type="execution_closing",
                description="Execution & Closing Agent - Contacts property owners, generates offers, contracts, and financing packages",
                max_concurrent_tasks=3,
                priority="high",
                config={
                    "auto_contact": False,  # Requires human approval
                    "contract_templates": True,
                    "financing_networks": True
                }
            ),
            AgentConfig(
                agent_id="portfolio_manager",
                name="Portfolio Manager",
                agent_type="post_acquisition",
                description="Post-Acquisition Intelligence Agent - Tracks renovations, tenant demand, and refinancing opportunities",
                max_concurrent_tasks=4,
                priority="normal",
                config={
                    "monitoring_frequency": "weekly",
                    "alert_thresholds": {
                        "vacancy_rate": 0.1,
                        "maintenance_costs": 1000,
                        "cash_flow_drop": 0.2
                    }
                }
            )
        ]
        
        for agent in default_agents:
            self.register_agent(agent)
    
    async def start(self):
        """Start the agent manager."""
        if self.is_running:
            logger.warning("Agent manager is already running")
            return
        
        logger.info("Starting agent manager")
        self.is_running = True
        
        # Start background tasks
        self.background_tasks.extend([
            asyncio.create_task(self._heartbeat_monitor()),
            asyncio.create_task(self._task_processor()),
            asyncio.create_task(self._status_updater())
        ])
        
        # Start all active agents
        for agent_id in self.agents:
            if self.agents[agent_id].is_active:
                await self.start_agent(agent_id)
        
        logger.info("Agent manager started successfully")
    
    async def stop(self):
        """Stop the agent manager."""
        if not self.is_running:
            logger.warning("Agent manager is not running")
            return
        
        logger.info("Stopping agent manager")
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Stop all agents
        for agent_id in self.agents:
            await self.stop_agent(agent_id)
        
        # Wait for tasks to complete
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        self.background_tasks.clear()
        
        logger.info("Agent manager stopped successfully")
    
    def register_agent(self, agent_config: AgentConfig):
        """Register a new AI agent."""
        self.agents[agent_config.agent_id] = agent_config
        self.agent_statuses[agent_config.agent_id] = AgentStatus(
            agent_id=agent_config.agent_id,
            status="offline",
            last_heartbeat=datetime.utcnow()
        )
        self.task_queues[agent_config.agent_id] = asyncio.Queue()
        
        logger.info(f"Registered agent: {agent_config.name} ({agent_config.agent_id})")
    
    async def start_agent(self, agent_id: str):
        """Start a specific agent."""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent_config = self.agents[agent_id]
        if not agent_config.is_active:
            logger.warning(f"Agent {agent_id} is not active")
            return
        
        # Update agent status
        self.agent_statuses[agent_id].status = "online"
        self.agent_statuses[agent_id].last_heartbeat = datetime.utcnow()
        
        # Start agent-specific background task
        task = asyncio.create_task(self._agent_worker(agent_id))
        self.background_tasks.append(task)
        
        logger.info(f"Started agent: {agent_config.name} ({agent_id})")
        
        # Publish real-time update
        try:
            await publish_event(
                "agents",
                "agent_started",
                {"agent_id": agent_id, "status": "online"}
            )
        except Exception:
            # Ignore Redis publish errors
            pass
    
    async def stop_agent(self, agent_id: str):
        """Stop a specific agent."""
        if agent_id not in self.agents:
            return
        
        # Update agent status
        self.agent_statuses[agent_id].status = "offline"
        
        logger.info(f"Stopped agent: {agent_id}")
        
        # Publish real-time update
        try:
            await publish_event(
                "agents",
                "agent_stopped",
                {"agent_id": agent_id, "status": "offline"}
            )
        except Exception:
            # Ignore Redis publish errors
            pass
    
    async def submit_task(self, agent_id: str, task_type: str, priority: str = "normal", **kwargs) -> str:
        """Submit a task to an agent."""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        if not self.agents[agent_id].is_active:
            raise ValueError(f"Agent {agent_id} is not active")
        
        # Create task
        task = AgentTask(
            task_id=str(uuid4()),
            agent_id=agent_id,
            task_type=task_type,
            priority=priority,
            status="pending",
            created_at=datetime.utcnow(),
            metadata=kwargs
        )
        
        # Add to tasks
        self.tasks[task.task_id] = task
        
        # Add to agent's queue
        await self.task_queues[agent_id].put(task)
        
        logger.info(f"Submitted task {task.task_id} to agent {agent_id}")
        
        # Publish real-time update
        try:
            await publish_event(
                f"agent:{agent_id}",
                "task_submitted",
                task.__dict__
            )
        except Exception:
            # Ignore Redis publish errors
            pass
        
        return task.task_id
    
    async def get_task_status(self, task_id: str) -> Optional[AgentTask]:
        """Get the status of a task."""
        return self.tasks.get(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status in ["completed", "failed", "cancelled"]:
            return False
        
        task.status = "cancelled"
        task.completed_at = datetime.utcnow()
        
        logger.info(f"Cancelled task {task_id}")
        
        # Publish real-time update
        await publish_event(
            f"agent:{task.agent_id}",
            "task_cancelled",
            {"task_id": task_id}
        )
        
        return True
    
    async def get_agent_status(self, agent_id: str) -> Optional[AgentStatus]:
        """Get the status of an agent."""
        return self.agent_statuses.get(agent_id)
    
    async def get_all_agent_statuses(self) -> List[AgentStatus]:
        """Get status of all agents."""
        return list(self.agent_statuses.values())
    
    async def get_agent_tasks(self, agent_id: str, status: Optional[str] = None) -> List[AgentTask]:
        """Get tasks for a specific agent."""
        tasks = [task for task in self.tasks.values() if task.agent_id == agent_id]
        if status:
            tasks = [task for task in tasks if task.status == status]
        return tasks
    
    async def _agent_worker(self, agent_id: str):
        """Background worker for an agent."""
        agent_config = self.agents[agent_id]
        queue = self.task_queues[agent_id]
        
        logger.info(f"Started agent worker for {agent_id}")
        
        while self.is_running and agent_config.is_active:
            try:
                # Get task from queue
                task = await asyncio.wait_for(queue.get(), timeout=1.0)
                
                if task.status == "cancelled":
                    continue
                
                # Process task
                await self._process_task(task)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in agent worker {agent_id}: {e}")
                await asyncio.sleep(1)
        
        logger.info(f"Stopped agent worker for {agent_id}")
    
    async def _process_task(self, task: AgentTask):
        """Process a task using the appropriate agent handler."""
        try:
            # Update task status
            task.status = "running"
            task.started_at = datetime.utcnow()
            
            # Publish real-time update
            await publish_event(
                f"agent:{task.agent_id}",
                "task_started",
                {"task_id": task.task_id}
            )
            
            # Get agent handler
            handler = self.agent_handlers.get(task.agent_id)
            if handler:
                # Process task
                result = await handler(task)
                task.result = result
                task.status = "completed"
            else:
                # No handler available, mark as failed
                task.status = "failed"
                task.error = "No handler available for agent"
            
            task.completed_at = datetime.utcnow()
            
            # Update agent status
            if task.status == "completed":
                self.agent_statuses[task.agent_id].total_tasks_completed += 1
            else:
                self.agent_statuses[task.agent_id].total_tasks_failed += 1
            
            logger.info(f"Completed task {task.task_id} with status: {task.status}")
            
            # Publish real-time update
            await publish_event(
                f"agent:{task.agent_id}",
                "task_completed",
                task.__dict__
            )
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            
            self.agent_statuses[task.agent_id].total_tasks_failed += 1
            
            logger.error(f"Failed to process task {task.task_id}: {e}")
            
            # Publish real-time update
            await publish_event(
                f"agent:{task.agent_id}",
                "task_failed",
                {"task_id": task.task_id, "error": str(e)}
            )
    
    async def _heartbeat_monitor(self):
        """Monitor agent heartbeats."""
        while self.is_running:
            try:
                current_time = datetime.utcnow()
                
                for agent_id, status in self.agent_statuses.items():
                    if status.status == "online":
                        # Check if agent is responsive
                        time_since_heartbeat = current_time - status.last_heartbeat
                        if time_since_heartbeat > timedelta(minutes=5):
                            # Agent may be unresponsive
                            status.status = "error"
                            status.health_score = max(0.0, status.health_score - 0.1)
                            
                            logger.warning(f"Agent {agent_id} may be unresponsive")
                            
                            # Publish real-time update (only if Redis is available)
                            try:
                                await publish_event(
                                    "agents",
                                    "agent_health_warning",
                                    {"agent_id": agent_id, "status": "error"}
                                )
                            except Exception:
                                # Ignore Redis publish errors
                                pass
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(30)
    
    async def _task_processor(self):
        """Process task queue and distribute tasks."""
        while self.is_running:
            try:
                # Check for high-priority tasks
                for agent_id, queue in self.task_queues.items():
                    if not queue.empty():
                        # Process tasks based on priority
                        await self._process_agent_queue(agent_id)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in task processor: {e}")
                await asyncio.sleep(1)
    
    async def _process_agent_queue(self, agent_id: str):
        """Process tasks in an agent's queue."""
        agent_config = self.agents[agent_id]
        agent_status = self.agent_statuses[agent_id]
        
        # Check if agent can handle more tasks
        if agent_status.current_tasks >= agent_config.max_concurrent_tasks:
            return
        
        # Get pending tasks
        pending_tasks = [task for task in self.tasks.values() 
                        if task.agent_id == agent_id and task.status == "pending"]
        
        # Sort by priority
        priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
        pending_tasks.sort(key=lambda t: priority_order.get(t.priority, 2))
        
        # Start tasks up to max concurrent limit
        for task in pending_tasks[:agent_config.max_concurrent_tasks - agent_status.current_tasks]:
            agent_status.current_tasks += 1
            # Task will be processed by agent worker
    
    async def _status_updater(self):
        """Update agent statuses and publish updates."""
        while self.is_running:
            try:
                current_time = datetime.utcnow()
                
                for agent_id, status in self.agent_statuses.items():
                    # Update health score based on performance
                    if status.total_tasks_completed > 0:
                        success_rate = status.total_tasks_completed / (status.total_tasks_completed + status.total_tasks_failed)
                        status.health_score = min(1.0, success_rate + 0.1)
                    
                    # Publish status update
                    await publish_event(
                        "agents",
                        "status_update",
                        {
                            "agent_id": agent_id,
                            "status": status.status,
                            "health_score": status.health_score,
                            "current_tasks": status.current_tasks
                        }
                    )
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in status updater: {e}")
                await asyncio.sleep(10)
    
    def register_handler(self, agent_id: str, handler: Callable):
        """Register a handler function for an agent."""
        self.agent_handlers[agent_id] = handler
        logger.info(f"Registered handler for agent {agent_id}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the agent manager."""
        total_agents = len(self.agents)
        online_agents = sum(1 for status in self.agent_statuses.values() if status.status == "online")
        total_tasks = len(self.tasks)
        pending_tasks = sum(1 for task in self.tasks.values() if task.status == "pending")
        running_tasks = sum(1 for task in self.tasks.values() if task.status == "running")
        
        return {
            "status": "healthy" if self.is_running else "stopped",
            "total_agents": total_agents,
            "online_agents": online_agents,
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "running_tasks": running_tasks,
            "is_running": self.is_running
        }

    # Legacy agent handlers (to be replaced with specialized agents)
    async def _handle_ai_insights(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AI insights tasks."""
        # Delegate to gemini agent for now
        if "gemini" in self.agent_handlers:
            return await self.agent_handlers["gemini"](task_type, task_data)
        return {"status": "agent_not_available"}
    
    async def _handle_market_analysis(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle market analysis tasks."""
        # Mock implementation - replace with real market analysis
        return {
            "market_trends": "positive",
            "price_growth": 0.05,
            "inventory_level": "low",
            "recommendation": "favorable_market_conditions"
        }
    
    async def _handle_lead_management(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle lead management tasks."""
        # Mock implementation - replace with real lead management
        return {
            "lead_score": 85,
            "qualification_status": "qualified",
            "next_action": "schedule_viewing",
            "priority": "high"
        }
    
    # Placeholder handlers for new agents (to be implemented)
    async def _handle_investment_committee(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AI investment committee tasks."""
        # Placeholder - will be implemented as separate agent
        return {
            "committee_decision": "recommend_purchase",
            "confidence_score": 0.82,
            "risk_assessment": "medium",
            "unanimous_vote": False,
            "dissenting_opinions": ["Market timing concerns"]
        }
    
    async def _handle_execution_closing(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle execution and closing tasks."""
        # Placeholder - will be implemented as separate agent
        return {
            "offer_generated": True,
            "contact_attempted": True,
            "financing_options": ["conventional", "hard_money", "private"],
            "estimated_closing_date": "2024-03-15"
        }
    
    async def _handle_post_acquisition(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle post-acquisition intelligence tasks."""
        # Placeholder - will be implemented as separate agent
        return {
            "renovation_progress": 0.75,
            "rental_demand": "high",
            "refinancing_opportunity": True,
            "estimated_completion": "2024-04-01",
            "budget_variance": -0.05
        }

# Global agent manager instance
_agent_manager: Optional[AgentManager] = None

def get_agent_manager() -> AgentManager:
    """Get the global agent manager instance."""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager()
    return _agent_manager

async def start_agent_manager():
    """Start the global agent manager."""
    manager = get_agent_manager()
    await manager.start()

async def stop_agent_manager():
    """Stop the global agent manager."""
    global _agent_manager
    if _agent_manager:
        await _agent_manager.stop()
        _agent_manager = None
