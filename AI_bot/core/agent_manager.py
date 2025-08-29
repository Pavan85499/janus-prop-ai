"""
Agent Manager for Real Estate AI Agent System

This module provides the central orchestration for all agents in the system,
including agent lifecycle management, workflow coordination, and request routing.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union
from uuid import uuid4

import structlog
from pydantic import BaseModel, Field, ConfigDict

from agents.base_agent import BaseAgent, AgentConfig, AgentResponse
from core.communication import CommunicationManager, Message, MessageType
from core.exceptions import AgentError, AgentTimeoutError, ResourceNotFoundError


class AgentRegistration(BaseModel):
    """Registration information for an agent."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    agent_id: str
    agent_type: str
    agent_instance: BaseAgent
    config: AgentConfig
    capabilities: List[str]
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"  # active, inactive, error


class WorkflowStep(BaseModel):
    """A single step in a workflow."""
    
    step_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_type: str
    task: str
    data: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)  # step_ids this depends on
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class Workflow(BaseModel):
    """A complete workflow definition."""
    
    workflow_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    steps: List[WorkflowStep]
    status: str = "pending"  # pending, running, completed, failed, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentManager:
    """
    Central manager for all agents in the system.
    
    This class provides:
    - Agent registration and lifecycle management
    - Request routing to appropriate agents
    - Workflow creation and execution
    - System monitoring and health checks
    - Load balancing and failover
    """
    
    def __init__(self):
        self.logger = structlog.get_logger(self.__class__.__name__)
        self.agents: Dict[str, AgentRegistration] = {}
        self.agent_types: Dict[str, Set[str]] = {}  # agent_type -> set of agent_ids
        self.workflows: Dict[str, Workflow] = {}
        self.communication_manager = CommunicationManager()
        self.running = False
        self._health_check_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the agent manager."""
        self.logger.info("Starting agent manager")
        self.running = True
        
        # Start communication manager
        await self.communication_manager.start()
        
        # Start health check task
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        self.logger.info("Agent manager started")
    
    async def stop(self):
        """Stop the agent manager."""
        self.logger.info("Stopping agent manager")
        self.running = False
        
        # Stop health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Stop all agents
        for agent_id in list(self.agents.keys()):
            await self.unregister_agent(agent_id)
        
        # Stop communication manager
        await self.communication_manager.stop()
        
        self.logger.info("Agent manager stopped")
    
    async def register_agent(self, agent: BaseAgent, agent_type: str) -> str:
        """
        Register an agent with the manager.
        
        Args:
            agent: The agent instance to register
            agent_type: Type/category of the agent
            
        Returns:
            The agent ID assigned to the agent
        """
        agent_id = agent.config.agent_id
        
        if agent_id in self.agents:
            raise AgentError(f"Agent {agent_id} is already registered")
        
        # Get agent capabilities
        capabilities = await agent.get_capabilities()
        
        # Create registration
        registration = AgentRegistration(
            agent_id=agent_id,
            agent_type=agent_type,
            agent_instance=agent,
            config=agent.config,
            capabilities=capabilities.get("supported_operations", [])
        )
        
        # Register agent
        self.agents[agent_id] = registration
        
        # Add to agent types mapping
        if agent_type not in self.agent_types:
            self.agent_types[agent_type] = set()
        self.agent_types[agent_type].add(agent_id)
        
        # Register with communication manager
        await self.communication_manager.register_agent(agent_id, agent)
        
        self.logger.info(
            "Agent registered",
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=capabilities.get("supported_operations", [])
        )
        
        return agent_id
    
    async def unregister_agent(self, agent_id: str):
        """
        Unregister an agent from the manager.
        
        Args:
            agent_id: ID of the agent to unregister
        """
        if agent_id not in self.agents:
            return
        
        registration = self.agents[agent_id]
        
        # Remove from agent types mapping
        if registration.agent_type in self.agent_types:
            self.agent_types[registration.agent_type].discard(agent_id)
            if not self.agent_types[registration.agent_type]:
                del self.agent_types[registration.agent_type]
        
        # Unregister from communication manager
        await self.communication_manager.unregister_agent(agent_id)
        
        # Shutdown agent
        await registration.agent_instance.shutdown()
        
        # Remove registration
        del self.agents[agent_id]
        
        self.logger.info("Agent unregistered", agent_id=agent_id)
    
    async def query_agent(
        self, 
        agent_type: str, 
        query: Union[str, Dict[str, Any]], 
        context: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> AgentResponse:
        """
        Query a specific type of agent.
        
        Args:
            agent_type: Type of agent to query
            query: The query to send to the agent
            context: Additional context for the query
            timeout: Timeout in seconds (overrides agent default)
            
        Returns:
            Response from the agent
            
        Raises:
            ResourceNotFoundError: If no agents of the specified type are available
            AgentTimeoutError: If the query times out
        """
        if agent_type not in self.agent_types or not self.agent_types[agent_type]:
            raise ResourceNotFoundError(
                f"No agents of type '{agent_type}' available",
                "agent_type",
                agent_type
            )
        
        # Select the best available agent (simple round-robin for now)
        agent_ids = list(self.agent_types[agent_type])
        selected_agent_id = agent_ids[0]  # TODO: Implement load balancing
        
        registration = self.agents[selected_agent_id]
        agent = registration.agent_instance
        
        # Use agent timeout if none specified
        if timeout is None:
            timeout = agent.config.timeout
        
        try:
            # Process request with timeout
            response = await asyncio.wait_for(
                agent.process_request(query, context),
                timeout=timeout
            )
            
            # Update last heartbeat
            registration.last_heartbeat = datetime.utcnow()
            
            return response
            
        except asyncio.TimeoutError:
            raise AgentTimeoutError(
                f"Agent query timed out after {timeout} seconds",
                timeout,
                {"agent_id": selected_agent_id, "agent_type": agent_type}
            )
    
    async def create_workflow(self, workflow_definition: List[Dict[str, Any]]) -> Workflow:
        """
        Create a new workflow from a definition.
        
        Args:
            workflow_definition: List of workflow step definitions
            
        Returns:
            The created workflow
            
        Raises:
            ValidationError: If the workflow definition is invalid
        """
        # Validate workflow definition
        steps = []
        step_ids = []  # Store step IDs to resolve dependencies
        
        for i, step_def in enumerate(workflow_definition):
            step_id = str(uuid4())
            step_ids.append(step_id)
            
            # Convert integer dependencies to step IDs
            dependencies = []
            if "dependencies" in step_def:
                for dep_idx in step_def["dependencies"]:
                    if isinstance(dep_idx, int) and 0 <= dep_idx < i:
                        dependencies.append(step_ids[dep_idx])
                    else:
                        self.logger.warning(
                            "Invalid dependency index",
                            step_index=i,
                            dependency_index=dep_idx,
                            total_steps=len(workflow_definition)
                        )
            
            step = WorkflowStep(
                step_id=step_id,
                agent_type=step_def["agent"],
                task=step_def["task"],
                data=step_def.get("data", {}),
                dependencies=dependencies
            )
            steps.append(step)
        
        # Create workflow
        workflow = Workflow(
            workflow_id=str(uuid4()),
            name=f"Workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            description="Generated workflow",
            steps=steps
        )
        
        # Store workflow
        self.workflows[workflow.workflow_id] = workflow
        
        self.logger.info(
            "Workflow created",
            workflow_id=workflow.workflow_id,
            step_count=len(steps)
        )
        
        return workflow
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            workflow_id: ID of the workflow to execute
            
        Returns:
            Results of the workflow execution
            
        Raises:
            ResourceNotFoundError: If the workflow is not found
            WorkflowError: If workflow execution fails
        """
        if workflow_id not in self.workflows:
            raise ResourceNotFoundError(
                f"Workflow {workflow_id} not found",
                "workflow",
                workflow_id
            )
        
        workflow = self.workflows[workflow_id]
        workflow.status = "running"
        workflow.started_at = datetime.utcnow()
        
        self.logger.info(
            "Starting workflow execution",
            workflow_id=workflow_id,
            step_count=len(workflow.steps)
        )
        
        try:
            # Execute steps in dependency order
            results = {}
            completed_steps = set()
            
            while len(completed_steps) < len(workflow.steps):
                # Find steps that can be executed (all dependencies satisfied)
                for step in workflow.steps:
                    if (step.step_id not in completed_steps and 
                        step.status == "pending" and
                        all(dep in completed_steps for dep in step.dependencies)):
                        
                        # Execute step
                        step.status = "running"
                        step.started_at = datetime.utcnow()
                        
                        try:
                            # Query appropriate agent
                            response = await self.query_agent(
                                step.agent_type,
                                step.task,
                                step.data
                            )
                            
                            if response.success:
                                step.status = "completed"
                                step.result = response.data
                                results[step.step_id] = response.data
                            else:
                                step.status = "failed"
                                step.error = response.error
                                raise Exception(f"Step failed: {response.error}")
                            
                        except Exception as e:
                            step.status = "failed"
                            step.error = str(e)
                            step.completed_at = datetime.utcnow()
                            raise
                        
                        step.completed_at = datetime.utcnow()
                        completed_steps.add(step.step_id)
                        
                        self.logger.info(
                            "Workflow step completed",
                            workflow_id=workflow_id,
                            step_id=step.step_id,
                            status=step.status
                        )
                
                # Check for deadlock
                if len(completed_steps) == 0:
                    raise Exception("Workflow deadlock detected - no progress possible")
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
            
            # Mark workflow as completed
            workflow.status = "completed"
            workflow.completed_at = datetime.utcnow()
            
            self.logger.info(
                "Workflow completed successfully",
                workflow_id=workflow_id
            )
            
            return results
            
        except Exception as e:
            workflow.status = "failed"
            workflow.completed_at = datetime.utcnow()
            
            self.logger.error(
                "Workflow execution failed",
                workflow_id=workflow_id,
                error=str(e)
            )
            
            raise
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific agent."""
        if agent_id not in self.agents:
            return None
        
        registration = self.agents[agent_id]
        return {
            "agent_id": agent_id,
            "agent_type": registration.agent_type,
            "status": registration.status,
            "capabilities": registration.capabilities,
            "registered_at": registration.registered_at.isoformat(),
            "last_heartbeat": registration.last_heartbeat.isoformat(),
            "config": registration.config.dict()
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get the overall system status."""
        return {
            "running": self.running,
            "total_agents": len(self.agents),
            "agent_types": {
                agent_type: len(agent_ids)
                for agent_type, agent_ids in self.agent_types.items()
            },
            "active_workflows": len([
                w for w in self.workflows.values() 
                if w.status in ["pending", "running"]
            ]),
            "communication_status": self.communication_manager.get_system_status()
        }
    
    async def _health_check_loop(self):
        """Periodic health check loop for all agents."""
        while self.running:
            try:
                for agent_id, registration in self.agents.items():
                    try:
                        # Check agent health
                        health_status = await registration.agent_instance.health_check()
                        
                        # Update registration status
                        if health_status["status"] == "healthy":
                            registration.status = "active"
                            registration.last_heartbeat = datetime.utcnow()
                        else:
                            registration.status = "error"
                            self.logger.warning(
                                "Agent health check failed",
                                agent_id=agent_id,
                                status=health_status["status"]
                            )
                    
                    except Exception as e:
                        registration.status = "error"
                        self.logger.error(
                            "Agent health check error",
                            agent_id=agent_id,
                            error=str(e)
                        )
                
                # Wait before next health check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Health check loop error", error=str(e))
                await asyncio.sleep(5)  # Wait before retrying
