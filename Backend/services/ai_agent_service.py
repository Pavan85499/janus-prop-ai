"""
AI Agent Service for Janus Prop AI Backend

This module provides comprehensive AI agent management and orchestration services.
"""

import asyncio
import structlog
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.exc import SQLAlchemyError

from models.ai_agent import (
    AIAgent, AgentTask, AgentActivity, AgentCapability,
    AgentStatus, TaskStatus, TaskPriority, AgentType,
    AIAgentCreate, AIAgentUpdate, AIAgentResponse,
    AgentTaskCreate, AgentTaskUpdate, AgentTaskResponse,
    AgentActivityCreate, AgentActivityResponse,
    AgentCapabilityCreate, AgentCapabilityResponse
)
from core.redis_client import cache_get, cache_set, cache_delete, publish_event
from core.websocket_manager import get_websocket_manager

logger = structlog.get_logger(__name__)

class AIAgentService:
    """Service for managing AI agents and their operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.websocket_manager = get_websocket_manager()
    
    # Agent Management
    async def create_agent(self, agent_data: AIAgentCreate, created_by: str = None) -> AIAgentResponse:
        """Create a new AI agent."""
        try:
            # Check if agent with same name exists
            existing_agent = self.db.query(AIAgent).filter(
                and_(
                    AIAgent.name == agent_data.name,
                    AIAgent.agent_type == agent_data.agent_type
                )
            ).first()
            
            if existing_agent:
                raise ValueError(f"Agent with name '{agent_data.name}' and type '{agent_data.agent_type}' already exists")
            
            # Create agent
            agent = AIAgent(
                id=str(uuid4()),
                name=agent_data.name,
                agent_type=agent_data.agent_type.value,
                description=agent_data.description,
                version=agent_data.version,
                config=agent_data.config or {},
                capabilities=agent_data.capabilities or [],
                limitations=agent_data.limitations or [],
                max_concurrent_tasks=agent_data.max_concurrent_tasks,
                priority=agent_data.priority.value,
                created_by=created_by
            )
            
            self.db.add(agent)
            self.db.commit()
            self.db.refresh(agent)
            
            logger.info(f"Created AI agent: {agent.name} ({agent.id})")
            
            # Publish real-time update
            await publish_event(
                "agents",
                "agent_created",
                {"agent_id": agent.id, "name": agent.name, "type": agent.agent_type}
            )
            
            return AIAgentResponse(**agent.to_dict())
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating agent: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating agent: {e}")
            raise
    
    async def get_agent(self, agent_id: str) -> Optional[AIAgentResponse]:
        """Get an AI agent by ID."""
        try:
            agent = self.db.query(AIAgent).filter(AIAgent.id == agent_id).first()
            if not agent:
                return None
            
            return AIAgentResponse(**agent.to_dict())
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting agent {agent_id}: {e}")
            raise
    
    async def get_agents(
        self, 
        skip: int = 0, 
        limit: int = 100,
        agent_type: Optional[AgentType] = None,
        is_active: Optional[bool] = None,
        status: Optional[AgentStatus] = None
    ) -> Tuple[List[AIAgentResponse], int]:
        """Get AI agents with filtering and pagination."""
        try:
            query = self.db.query(AIAgent)
            
            # Apply filters
            if agent_type:
                query = query.filter(AIAgent.agent_type == agent_type.value)
            if is_active is not None:
                query = query.filter(AIAgent.is_active == is_active)
            if status:
                query = query.filter(AIAgent.current_status == status.value)
            
            # Get total count
            total = query.count()
            
            # Apply pagination and ordering
            agents = query.order_by(desc(AIAgent.created_at)).offset(skip).limit(limit).all()
            
            return [AIAgentResponse(**agent.to_dict()) for agent in agents], total
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting agents: {e}")
            raise
    
    async def update_agent(self, agent_id: str, agent_data: AIAgentUpdate) -> Optional[AIAgentResponse]:
        """Update an AI agent."""
        try:
            agent = self.db.query(AIAgent).filter(AIAgent.id == agent_id).first()
            if not agent:
                return None
            
            # Update fields
            update_data = agent_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field == "priority" and value:
                    setattr(agent, field, value.value)
                else:
                    setattr(agent, field, value)
            
            agent.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(agent)
            
            logger.info(f"Updated AI agent: {agent.name} ({agent.id})")
            
            # Publish real-time update
            await publish_event(
                "agents",
                "agent_updated",
                {"agent_id": agent.id, "name": agent.name, "changes": list(update_data.keys())}
            )
            
            return AIAgentResponse(**agent.to_dict())
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating agent {agent_id}: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating agent {agent_id}: {e}")
            raise
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an AI agent."""
        try:
            agent = self.db.query(AIAgent).filter(AIAgent.id == agent_id).first()
            if not agent:
                return False
            
            # Cancel all pending/running tasks
            await self.cancel_agent_tasks(agent_id, TaskStatus.PENDING)
            await self.cancel_agent_tasks(agent_id, TaskStatus.RUNNING)
            
            # Delete agent (cascade will handle related records)
            self.db.delete(agent)
            self.db.commit()
            
            logger.info(f"Deleted AI agent: {agent.name} ({agent.id})")
            
            # Publish real-time update
            await publish_event(
                "agents",
                "agent_deleted",
                {"agent_id": agent_id, "name": agent.name}
            )
            
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error deleting agent {agent_id}: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting agent {agent_id}: {e}")
            raise
    
    # Task Management
    async def create_task(self, task_data: AgentTaskCreate, created_by: str = None) -> AgentTaskResponse:
        """Create a new agent task."""
        try:
            # Verify agent exists and is active
            agent = self.db.query(AIAgent).filter(
                and_(
                    AIAgent.id == task_data.agent_id,
                    AIAgent.is_active == True
                )
            ).first()
            
            if not agent:
                raise ValueError(f"Agent {task_data.agent_id} not found or not active")
            
            # Create task
            task = AgentTask(
                id=str(uuid4()),
                agent_id=task_data.agent_id,
                task_type=task_data.task_type,
                title=task_data.title,
                description=task_data.description,
                priority=task_data.priority.value,
                input_data=task_data.input_data or {},
                task_metadata=task_data.task_metadata or {},
                tags=task_data.tags or [],
                estimated_duration=task_data.estimated_duration,
                created_by=created_by
            )
            
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
            
            logger.info(f"Created task {task.id} for agent {task.agent_id}")
            
            # Publish real-time update
            await publish_event(
                f"agent:{task.agent_id}",
                "task_created",
                {"task_id": task.id, "task_type": task.task_type, "priority": task.priority}
            )
            
            return AgentTaskResponse(**task.to_dict())
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating task: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating task: {e}")
            raise
    
    async def get_task(self, task_id: str) -> Optional[AgentTaskResponse]:
        """Get an agent task by ID."""
        try:
            task = self.db.query(AgentTask).filter(AgentTask.id == task_id).first()
            if not task:
                return None
            
            return AgentTaskResponse(**task.to_dict())
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting task {task_id}: {e}")
            raise
    
    async def get_agent_tasks(
        self,
        agent_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TaskStatus] = None,
        task_type: Optional[str] = None
    ) -> Tuple[List[AgentTaskResponse], int]:
        """Get tasks for a specific agent."""
        try:
            query = self.db.query(AgentTask).filter(AgentTask.agent_id == agent_id)
            
            # Apply filters
            if status:
                query = query.filter(AgentTask.status == status.value)
            if task_type:
                query = query.filter(AgentTask.task_type == task_type)
            
            # Get total count
            total = query.count()
            
            # Apply pagination and ordering
            tasks = query.order_by(desc(AgentTask.created_at)).offset(skip).limit(limit).all()
            
            return [AgentTaskResponse(**task.to_dict()) for task in tasks], total
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting agent tasks: {e}")
            raise
    
    async def update_task(self, task_id: str, task_data: AgentTaskUpdate) -> Optional[AgentTaskResponse]:
        """Update an agent task."""
        try:
            task = self.db.query(AgentTask).filter(AgentTask.id == task_id).first()
            if not task:
                return None
            
            # Update fields
            update_data = task_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field in ["priority", "status"] and value:
                    setattr(task, field, value.value)
                else:
                    setattr(task, field, value)
            
            # Update timing fields
            if task_data.status == TaskStatus.RUNNING and not task.started_at:
                task.started_at = datetime.utcnow()
            elif task_data.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and not task.completed_at:
                task.completed_at = datetime.utcnow()
                if task.started_at:
                    task.actual_duration = int((task.completed_at - task.started_at).total_seconds())
            
            self.db.commit()
            self.db.refresh(task)
            
            logger.info(f"Updated task {task_id}: {task.status}")
            
            # Publish real-time update
            await publish_event(
                f"agent:{task.agent_id}",
                "task_updated",
                {"task_id": task_id, "status": task.status, "progress": task.progress}
            )
            
            return AgentTaskResponse(**task.to_dict())
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating task {task_id}: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating task {task_id}: {e}")
            raise
    
    async def cancel_agent_tasks(self, agent_id: str, status: TaskStatus) -> int:
        """Cancel all tasks for an agent with specific status."""
        try:
            tasks = self.db.query(AgentTask).filter(
                and_(
                    AgentTask.agent_id == agent_id,
                    AgentTask.status == status.value
                )
            ).all()
            
            cancelled_count = 0
            for task in tasks:
                task.status = TaskStatus.CANCELLED.value
                task.completed_at = datetime.utcnow()
                cancelled_count += 1
            
            self.db.commit()
            
            logger.info(f"Cancelled {cancelled_count} tasks for agent {agent_id}")
            
            # Publish real-time update
            await publish_event(
                f"agent:{agent_id}",
                "tasks_cancelled",
                {"agent_id": agent_id, "count": cancelled_count, "status": status.value}
            )
            
            return cancelled_count
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error cancelling agent tasks: {e}")
            raise
    
    # Activity Management
    async def create_activity(self, activity_data: AgentActivityCreate) -> AgentActivityResponse:
        """Create an agent activity log entry."""
        try:
            activity = AgentActivity(
                id=str(uuid4()),
                agent_id=activity_data.agent_id,
                activity_type=activity_data.activity_type,
                message=activity_data.message,
                level=activity_data.level,
                status=activity_data.status,
                task_id=activity_data.task_id,
                property_id=activity_data.property_id,
                user_id=activity_data.user_id,
                data=activity_data.data or {},
                activity_metadata=activity_data.activity_metadata or {}
            )
            
            self.db.add(activity)
            self.db.commit()
            self.db.refresh(activity)
            
            logger.info(f"Created activity for agent {activity.agent_id}: {activity.activity_type}")
            
            # Publish real-time update
            await publish_event(
                f"agent:{activity.agent_id}",
                "activity_created",
                {
                    "activity_id": activity.id,
                    "activity_type": activity.activity_type,
                    "level": activity.level,
                    "message": activity.message
                }
            )
            
            return AgentActivityResponse(**activity.to_dict())
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating activity: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating activity: {e}")
            raise
    
    async def get_agent_activities(
        self,
        agent_id: str,
        skip: int = 0,
        limit: int = 100,
        activity_type: Optional[str] = None,
        level: Optional[str] = None,
        hours_back: int = 24
    ) -> Tuple[List[AgentActivityResponse], int]:
        """Get activities for a specific agent."""
        try:
            # Calculate time filter
            time_filter = datetime.utcnow() - timedelta(hours=hours_back)
            
            query = self.db.query(AgentActivity).filter(
                and_(
                    AgentActivity.agent_id == agent_id,
                    AgentActivity.timestamp >= time_filter
                )
            )
            
            # Apply filters
            if activity_type:
                query = query.filter(AgentActivity.activity_type == activity_type)
            if level:
                query = query.filter(AgentActivity.level == level)
            
            # Get total count
            total = query.count()
            
            # Apply pagination and ordering
            activities = query.order_by(desc(AgentActivity.timestamp)).offset(skip).limit(limit).all()
            
            return [AgentActivityResponse(**activity.to_dict()) for activity in activities], total
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting agent activities: {e}")
            raise
    
    # Agent Status Management
    async def update_agent_status(self, agent_id: str, status: AgentStatus, error_message: str = None) -> bool:
        """Update agent status."""
        try:
            agent = self.db.query(AIAgent).filter(AIAgent.id == agent_id).first()
            if not agent:
                return False
            
            agent.current_status = status.value
            agent.last_heartbeat = datetime.utcnow()
            
            if error_message:
                agent.last_error = error_message
                agent.last_error_time = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Updated agent {agent_id} status to {status.value}")
            
            # Publish real-time update
            await publish_event(
                "agents",
                "agent_status_updated",
                {
                    "agent_id": agent_id,
                    "status": status.value,
                    "error_message": error_message
                }
            )
            
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating agent status: {e}")
            raise
    
    async def get_agent_health(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive health information for an agent."""
        try:
            agent = self.db.query(AIAgent).filter(AIAgent.id == agent_id).first()
            if not agent:
                return None
            
            # Get recent tasks
            recent_tasks = self.db.query(AgentTask).filter(
                and_(
                    AgentTask.agent_id == agent_id,
                    AgentTask.created_at >= datetime.utcnow() - timedelta(hours=24)
                )
            ).all()
            
            # Calculate metrics
            total_tasks = len(recent_tasks)
            completed_tasks = len([t for t in recent_tasks if t.status == TaskStatus.COMPLETED.value])
            failed_tasks = len([t for t in recent_tasks if t.status == TaskStatus.FAILED.value])
            
            success_rate = (completed_tasks / total_tasks) if total_tasks > 0 else 0.0
            
            # Calculate average response time
            completed_with_duration = [t for t in recent_tasks if t.actual_duration is not None]
            avg_response_time = (
                sum(t.actual_duration for t in completed_with_duration) / len(completed_with_duration)
                if completed_with_duration else 0.0
            )
            
            # Get current tasks
            current_tasks = len([t for t in recent_tasks if t.status == TaskStatus.RUNNING.value])
            
            return {
                "agent_id": agent_id,
                "name": agent.name,
                "status": agent.current_status,
                "health_score": agent.health_score,
                "last_heartbeat": agent.last_heartbeat,
                "success_rate": success_rate,
                "average_response_time": avg_response_time,
                "current_tasks": current_tasks,
                "total_tasks_24h": total_tasks,
                "completed_tasks_24h": completed_tasks,
                "failed_tasks_24h": failed_tasks,
                "last_error": agent.last_error,
                "last_error_time": agent.last_error_time
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting agent health: {e}")
            raise
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health for all agents."""
        try:
            agents = self.db.query(AIAgent).filter(AIAgent.is_active == True).all()
            
            total_agents = len(agents)
            online_agents = len([a for a in agents if a.current_status == AgentStatus.ONLINE.value])
            error_agents = len([a for a in agents if a.current_status == AgentStatus.ERROR.value])
            
            # Get recent activity
            recent_activities = self.db.query(AgentActivity).filter(
                AgentActivity.timestamp >= datetime.utcnow() - timedelta(hours=1)
            ).count()
            
            # Get recent tasks
            recent_tasks = self.db.query(AgentTask).filter(
                AgentTask.created_at >= datetime.utcnow() - timedelta(hours=1)
            ).all()
            
            pending_tasks = len([t for t in recent_tasks if t.status == TaskStatus.PENDING.value])
            running_tasks = len([t for t in recent_tasks if t.status == TaskStatus.RUNNING.value])
            
            return {
                "total_agents": total_agents,
                "online_agents": online_agents,
                "error_agents": error_agents,
                "system_health": "healthy" if error_agents == 0 else "degraded" if error_agents < total_agents / 2 else "critical",
                "recent_activities": recent_activities,
                "pending_tasks": pending_tasks,
                "running_tasks": running_tasks,
                "timestamp": datetime.utcnow()
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting system health: {e}")
            raise
    
    # Capability Management
    async def create_capability(self, capability_data: AgentCapabilityCreate) -> AgentCapabilityResponse:
        """Create an agent capability."""
        try:
            # Verify agent exists
            agent = self.db.query(AIAgent).filter(AIAgent.id == capability_data.agent_id).first()
            if not agent:
                raise ValueError(f"Agent {capability_data.agent_id} not found")
            
            capability = AgentCapability(
                id=str(uuid4()),
                agent_id=capability_data.agent_id,
                name=capability_data.name,
                description=capability_data.description,
                version=capability_data.version,
                config=capability_data.config or {},
                parameters=capability_data.parameters or {}
            )
            
            self.db.add(capability)
            self.db.commit()
            self.db.refresh(capability)
            
            logger.info(f"Created capability {capability.name} for agent {capability.agent_id}")
            
            return AgentCapabilityResponse(**capability.to_dict())
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating capability: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating capability: {e}")
            raise
    
    async def get_agent_capabilities(self, agent_id: str) -> List[AgentCapabilityResponse]:
        """Get capabilities for a specific agent."""
        try:
            capabilities = self.db.query(AgentCapability).filter(
                AgentCapability.agent_id == agent_id
            ).all()
            
            return [AgentCapabilityResponse(**capability.to_dict()) for capability in capabilities]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting agent capabilities: {e}")
            raise
