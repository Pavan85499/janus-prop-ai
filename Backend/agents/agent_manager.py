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
        
        # Initialize default agents
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """Initialize default AI agents."""
        default_agents = [
            AgentConfig(
                agent_id="eden",
                name="Eden",
                agent_type="ai_insights",
                description="AI Insights and Property Analysis Agent",
                max_concurrent_tasks=3,
                priority="high"
            ),
            AgentConfig(
                agent_id="orion",
                name="Orion",
                agent_type="gemini",
                description="Google Gemini AI Integration Agent",
                max_concurrent_tasks=5,
                priority="high"
            ),
            AgentConfig(
                agent_id="atelius",
                name="Atelius",
                agent_type="attom",
                description="ATTOM Real Estate Data Agent",
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
        await publish_event(
            "agents",
            "agent_started",
            {"agent_id": agent_id, "status": "online"}
        )
    
    async def stop_agent(self, agent_id: str):
        """Stop a specific agent."""
        if agent_id not in self.agents:
            return
        
        # Update agent status
        self.agent_statuses[agent_id].status = "offline"
        
        logger.info(f"Stopped agent: {agent_id}")
        
        # Publish real-time update
        await publish_event(
            "agents",
            "agent_stopped",
            {"agent_id": agent_id, "status": "offline"}
        )
    
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
        await publish_event(
            f"agent:{agent_id}",
            "task_submitted",
            task.__dict__
        )
        
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
                            
                            # Publish real-time update
                            await publish_event(
                                "agents",
                                "agent_health_warning",
                                {"agent_id": agent_id, "status": "error"}
                            )
                
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
