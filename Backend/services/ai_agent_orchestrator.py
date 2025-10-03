"""
AI Agent Orchestrator for Janus Prop AI Backend

This module provides intelligent orchestration and coordination of AI agents.
"""

import asyncio
import structlog
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from models.ai_agent import (
    AIAgent, AgentTask, AgentActivity, AgentCapability,
    AgentStatus, TaskStatus, TaskPriority, AgentType,
    AIAgentCreate, AgentTaskCreate
)
from services.ai_agent_service import AIAgentService
from core.redis_client import publish_event, cache_get, cache_set
from core.websocket_manager import get_websocket_manager

logger = structlog.get_logger(__name__)

class AIAgentOrchestrator:
    """Orchestrates and coordinates multiple AI agents for complex workflows."""
    
    def __init__(self, db: Session):
        self.db = db
        self.service = AIAgentService(db)
        self.websocket_manager = get_websocket_manager()
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.is_running = False
    
    async def start(self):
        """Start the orchestrator."""
        try:
            self.is_running = True
            
            # Initialize default agents if they don't exist
            await self._initialize_default_agents()
            
            # Start background tasks
            asyncio.create_task(self._workflow_processor())
            asyncio.create_task(self._agent_health_monitor())
            asyncio.create_task(self._task_optimizer())
            
            logger.info("AI Agent Orchestrator started")
            
        except Exception as e:
            logger.error(f"Failed to start AI Agent Orchestrator: {e}")
            raise
    
    async def stop(self):
        """Stop the orchestrator."""
        try:
            self.is_running = False
            
            # Cancel all workflows
            for workflow_id in list(self.workflows.keys()):
                await self.cancel_workflow(workflow_id)
            
            logger.info("AI Agent Orchestrator stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop AI Agent Orchestrator: {e}")
    
    async def _initialize_default_agents(self):
        """Initialize default AI agents if they don't exist."""
        try:
            # Check if agents already exist
            agents, _ = await self.service.get_agents(limit=1)
            if agents:
                return
            
            # Create default agents
            default_agents = [
                AIAgentCreate(
                    name="Eden",
                    agent_type=AgentType.AI_INSIGHTS,
                    description="AI Insights and Property Analysis Agent",
                    capabilities=["property_analysis", "market_insights", "investment_scoring"],
                    max_concurrent_tasks=3,
                    priority=TaskPriority.HIGH
                ),
                AIAgentCreate(
                    name="Orion",
                    agent_type=AgentType.GEMINI,
                    description="Google Gemini AI Integration Agent",
                    capabilities=["natural_language_processing", "content_generation", "data_analysis"],
                    max_concurrent_tasks=5,
                    priority=TaskPriority.HIGH
                ),
                AIAgentCreate(
                    name="Atelius",
                    agent_type=AgentType.ATTOM,
                    description="ATTOM Real Estate Data Agent",
                    capabilities=["property_data", "market_data", "comparable_analysis"],
                    max_concurrent_tasks=4,
                    priority=TaskPriority.HIGH
                ),
                AIAgentCreate(
                    name="Nova",
                    agent_type=AgentType.MARKET_ANALYSIS,
                    description="Market Intelligence and Trends Agent",
                    capabilities=["market_analysis", "trend_prediction", "economic_analysis"],
                    max_concurrent_tasks=3,
                    priority=TaskPriority.NORMAL
                ),
                AIAgentCreate(
                    name="Zenith",
                    agent_type=AgentType.LEAD_MANAGEMENT,
                    description="Lead Qualification and Management Agent",
                    capabilities=["lead_scoring", "qualification", "follow_up"],
                    max_concurrent_tasks=2,
                    priority=TaskPriority.NORMAL
                )
            ]
            
            for agent_data in default_agents:
                try:
                    await self.service.create_agent(agent_data)
                    logger.info(f"Created default agent: {agent_data.name}")
                except Exception as e:
                    logger.warning(f"Failed to create agent {agent_data.name}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to initialize default agents: {e}")
    
    async def create_workflow(
        self,
        workflow_name: str,
        workflow_type: str,
        input_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> str:
        """Create a new workflow."""
        try:
            workflow_id = str(uuid4())
            
            workflow = {
                "id": workflow_id,
                "name": workflow_name,
                "type": workflow_type,
                "status": "pending",
                "input_data": input_data,
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "tasks": [],
                "results": {},
                "current_step": 0,
                "total_steps": 0
            }
            
            # Define workflow steps based on type
            workflow["steps"] = await self._define_workflow_steps(workflow_type, input_data)
            workflow["total_steps"] = len(workflow["steps"])
            
            self.workflows[workflow_id] = workflow
            
            # Log workflow creation
            await self.service.create_activity({
                "agent_id": "orchestrator",
                "activity_type": "workflow_created",
                "message": f"Created workflow: {workflow_name}",
                "level": "info",
                "status": "completed",
                "data": {"workflow_id": workflow_id, "workflow_type": workflow_type}
            })
            
            # Start workflow processing
            asyncio.create_task(self._process_workflow(workflow_id))
            
            logger.info(f"Created workflow {workflow_id}: {workflow_name}")
            
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise
    
    async def _define_workflow_steps(self, workflow_type: str, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define workflow steps based on type."""
        if workflow_type == "property_analysis":
            return [
                {
                    "step": 1,
                    "agent_type": AgentType.ATTOM,
                    "task_type": "property_data_collection",
                    "description": "Collect property data from ATTOM",
                    "input_mapping": {"property_id": "property_id"},
                    "output_key": "property_data"
                },
                {
                    "step": 2,
                    "agent_type": AgentType.MARKET_ANALYSIS,
                    "task_type": "market_analysis",
                    "description": "Analyze market conditions",
                    "input_mapping": {"location": "property_data.location"},
                    "output_key": "market_analysis"
                },
                {
                    "step": 3,
                    "agent_type": AgentType.AI_INSIGHTS,
                    "task_type": "property_valuation",
                    "description": "Perform property valuation",
                    "input_mapping": {
                        "property": "property_data",
                        "market": "market_analysis"
                    },
                    "output_key": "valuation"
                },
                {
                    "step": 4,
                    "agent_type": AgentType.AI_INSIGHTS,
                    "task_type": "investment_scoring",
                    "description": "Calculate investment score",
                    "input_mapping": {
                        "property": "property_data",
                        "market": "market_analysis",
                        "valuation": "valuation"
                    },
                    "output_key": "investment_score"
                },
                {
                    "step": 5,
                    "agent_type": AgentType.GEMINI,
                    "task_type": "generate_report",
                    "description": "Generate comprehensive analysis report",
                    "input_mapping": {
                        "property": "property_data",
                        "market": "market_analysis",
                        "valuation": "valuation",
                        "investment_score": "investment_score"
                    },
                    "output_key": "final_report"
                }
            ]
        
        elif workflow_type == "lead_qualification":
            return [
                {
                    "step": 1,
                    "agent_type": AgentType.LEAD_MANAGEMENT,
                    "task_type": "lead_scoring",
                    "description": "Score lead quality",
                    "input_mapping": {"lead_data": "lead_data"},
                    "output_key": "lead_score"
                },
                {
                    "step": 2,
                    "agent_type": AgentType.ATTOM,
                    "task_type": "property_lookup",
                    "description": "Look up property information",
                    "input_mapping": {"address": "lead_data.address"},
                    "output_key": "property_info"
                },
                {
                    "step": 3,
                    "agent_type": AgentType.AI_INSIGHTS,
                    "task_type": "investment_potential",
                    "description": "Assess investment potential",
                    "input_mapping": {
                        "lead": "lead_data",
                        "property": "property_info"
                    },
                    "output_key": "investment_potential"
                },
                {
                    "step": 4,
                    "agent_type": AgentType.GEMINI,
                    "task_type": "qualification_summary",
                    "description": "Generate qualification summary",
                    "input_mapping": {
                        "lead": "lead_data",
                        "score": "lead_score",
                        "property": "property_info",
                        "potential": "investment_potential"
                    },
                    "output_key": "qualification_summary"
                }
            ]
        
        else:
            # Default workflow
            return [
                {
                    "step": 1,
                    "agent_type": AgentType.AI_INSIGHTS,
                    "task_type": "general_analysis",
                    "description": "Perform general analysis",
                    "input_mapping": {"input": "input_data"},
                    "output_key": "analysis_result"
                }
            ]
    
    async def _process_workflow(self, workflow_id: str):
        """Process a workflow step by step."""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return
            
            workflow["status"] = "running"
            
            # Process each step
            for step in workflow["steps"]:
                if workflow["status"] == "cancelled":
                    break
                
                await self._process_workflow_step(workflow_id, step)
                workflow["current_step"] += 1
                
                # Update workflow progress
                progress = (workflow["current_step"] / workflow["total_steps"]) * 100
                await self._update_workflow_progress(workflow_id, progress)
            
            # Complete workflow
            if workflow["status"] == "running":
                workflow["status"] = "completed"
                workflow["completed_at"] = datetime.utcnow()
                
                # Log workflow completion
                await self.service.create_activity({
                    "agent_id": "orchestrator",
                    "activity_type": "workflow_completed",
                    "message": f"Completed workflow: {workflow['name']}",
                    "level": "info",
                    "status": "completed",
                    "data": {"workflow_id": workflow_id}
                })
            
            logger.info(f"Completed workflow {workflow_id}")
            
        except Exception as e:
            logger.error(f"Failed to process workflow {workflow_id}: {e}")
            workflow["status"] = "failed"
            workflow["error"] = str(e)
    
    async def _process_workflow_step(self, workflow_id: str, step: Dict[str, Any]):
        """Process a single workflow step."""
        try:
            workflow = self.workflows[workflow_id]
            
            # Find available agent for this step
            agent = await self._find_available_agent(step["agent_type"])
            if not agent:
                raise Exception(f"No available agent for type {step['agent_type']}")
            
            # Prepare input data
            input_data = await self._prepare_step_input(workflow, step)
            
            # Create task
            task_data = AgentTaskCreate(
                agent_id=agent.id,
                task_type=step["task_type"],
                title=f"{workflow['name']} - Step {step['step']}",
                description=step["description"],
                input_data=input_data,
                priority=TaskPriority.NORMAL
            )
            
            task = await self.service.create_task(task_data)
            workflow["tasks"].append(task.id)
            
            # Wait for task completion
            await self._wait_for_task_completion(task.id)
            
            # Get task result
            completed_task = await self.service.get_task(task.id)
            if completed_task and completed_task.status == "completed":
                workflow["results"][step["output_key"]] = completed_task.output_data
            else:
                raise Exception(f"Task {task.id} failed: {completed_task.error_message if completed_task else 'Unknown error'}")
            
        except Exception as e:
            logger.error(f"Failed to process workflow step: {e}")
            raise
    
    async def _find_available_agent(self, agent_type: AgentType) -> Optional[AIAgent]:
        """Find an available agent of the specified type."""
        try:
            agents, _ = await self.service.get_agents(
                agent_type=agent_type,
                is_active=True,
                status=AgentStatus.ONLINE
            )
            
            # Find agent with lowest current task count
            best_agent = None
            min_tasks = float('inf')
            
            for agent in agents:
                # Get current task count
                tasks, _ = await self.service.get_agent_tasks(
                    agent_id=agent.id,
                    status=TaskStatus.RUNNING
                )
                
                if len(tasks) < min_tasks and len(tasks) < agent.max_concurrent_tasks:
                    min_tasks = len(tasks)
                    best_agent = agent
            
            return best_agent
            
        except Exception as e:
            logger.error(f"Failed to find available agent: {e}")
            return None
    
    async def _prepare_step_input(self, workflow: Dict[str, Any], step: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input data for a workflow step."""
        input_data = {}
        
        for key, mapping in step["input_mapping"].items():
            if mapping in workflow["results"]:
                input_data[key] = workflow["results"][mapping]
            elif mapping in workflow["input_data"]:
                input_data[key] = workflow["input_data"][mapping]
            else:
                logger.warning(f"Input mapping '{mapping}' not found for step {step['step']}")
        
        return input_data
    
    async def _wait_for_task_completion(self, task_id: str, timeout: int = 300):
        """Wait for a task to complete."""
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).seconds < timeout:
            task = await self.service.get_task(task_id)
            if not task:
                break
            
            if task.status in ["completed", "failed", "cancelled"]:
                return
            
            await asyncio.sleep(1)
        
        raise Exception(f"Task {task_id} timed out")
    
    async def _update_workflow_progress(self, workflow_id: str, progress: float):
        """Update workflow progress."""
        try:
            # Publish real-time update
            await publish_event(
                f"workflow:{workflow_id}",
                "progress_update",
                {
                    "workflow_id": workflow_id,
                    "progress": progress,
                    "timestamp": datetime.utcnow()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to update workflow progress: {e}")
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status."""
        return self.workflows.get(workflow_id)
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow."""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return False
            
            workflow["status"] = "cancelled"
            
            # Cancel all pending/running tasks
            for task_id in workflow["tasks"]:
                await self.service.update_task(task_id, {
                    "status": TaskStatus.CANCELLED
                })
            
            logger.info(f"Cancelled workflow {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel workflow {workflow_id}: {e}")
            return False
    
    async def _workflow_processor(self):
        """Background processor for workflows."""
        while self.is_running:
            try:
                # Process any pending workflows
                for workflow_id, workflow in self.workflows.items():
                    if workflow["status"] == "pending":
                        asyncio.create_task(self._process_workflow(workflow_id))
                
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in workflow processor: {e}")
                await asyncio.sleep(5)
    
    async def _agent_health_monitor(self):
        """Monitor agent health and restart if needed."""
        while self.is_running:
            try:
                agents, _ = await self.service.get_agents(is_active=True)
                
                for agent in agents:
                    if agent.current_status == AgentStatus.ERROR:
                        # Try to restart the agent
                        await self.service.update_agent_status(agent.id, AgentStatus.ONLINE)
                        
                        logger.info(f"Restarted agent {agent.name} due to error status")
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in agent health monitor: {e}")
                await asyncio.sleep(30)
    
    async def _task_optimizer(self):
        """Optimize task distribution across agents."""
        while self.is_running:
            try:
                # Get all agents and their current tasks
                agents, _ = await self.service.get_agents(is_active=True)
                
                for agent in agents:
                    # Check if agent is overloaded
                    tasks, _ = await self.service.get_agent_tasks(
                        agent_id=agent.id,
                        status=TaskStatus.RUNNING
                    )
                    
                    if len(tasks) > agent.max_concurrent_tasks:
                        logger.warning(f"Agent {agent.name} is overloaded with {len(tasks)} tasks")
                
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in task optimizer: {e}")
                await asyncio.sleep(60)
    
    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        try:
            # Get system health
            system_health = await self.service.get_system_health()
            
            # Get workflow statistics
            active_workflows = len([w for w in self.workflows.values() if w["status"] == "running"])
            completed_workflows = len([w for w in self.workflows.values() if w["status"] == "completed"])
            failed_workflows = len([w for w in self.workflows.values() if w["status"] == "failed"])
            
            return {
                "is_running": self.is_running,
                "system_health": system_health,
                "workflows": {
                    "total": len(self.workflows),
                    "active": active_workflows,
                    "completed": completed_workflows,
                    "failed": failed_workflows
                },
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to get orchestrator status: {e}")
            return {
                "is_running": self.is_running,
                "error": str(e),
                "timestamp": datetime.utcnow()
            }
