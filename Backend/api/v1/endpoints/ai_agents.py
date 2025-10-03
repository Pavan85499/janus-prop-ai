"""
AI Agents API endpoints for Janus Prop AI Backend

This module provides comprehensive REST API endpoints for AI agent management.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4
import asyncio

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query, Path
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from core.database import get_db
from services.ai_agent_service import AIAgentService
from models.ai_agent import (
    AIAgentCreate, AIAgentUpdate, AIAgentResponse,
    AgentTaskCreate, AgentTaskUpdate, AgentTaskResponse,
    AgentActivityCreate, AgentActivityResponse,
    AgentCapabilityCreate, AgentCapabilityResponse,
    AgentStatus, TaskStatus, TaskPriority, AgentType
)
from core.redis_client import publish_event
from core.websocket_manager import get_websocket_manager

router = APIRouter()
# Lightweight task submission endpoints for Janus agents
@router.post("/eden/rank")
async def eden_rank(deals: List[Dict[str, Any]]):
    try:
        from agents.agent_manager import get_agent_manager
        manager = get_agent_manager()
        task_id = await manager.submit_task("eden", "rank_deals", deals=deals)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/eden/decide")
async def eden_decide(payload: Dict[str, Any]):
    try:
        from agents.agent_manager import get_agent_manager
        manager = get_agent_manager()
        task_id = await manager.submit_task("eden", "final_decision", **payload)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orion/monitor")
async def orion_monitor(geo: Dict[str, Any]):
    try:
        from agents.agent_manager import get_agent_manager
        manager = get_agent_manager()
        task_id = await manager.submit_task("orion", "monitor_events", geo=geo)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/atelius/parse-filing")
async def atelius_parse_filing(filing: Dict[str, Any]):
    try:
        from agents.agent_manager import get_agent_manager
        manager = get_agent_manager()
        task_id = await manager.submit_task("atelius", "parse_court_filing", filing=filing)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/atelius/title-chain")
async def atelius_title_chain(records: List[Dict[str, Any]]):
    try:
        from agents.agent_manager import get_agent_manager
        manager = get_agent_manager()
        task_id = await manager.submit_task("atelius", "analyze_title_chain", records=records)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/osiris/forecast")
async def osiris_forecast(deal: Dict[str, Any]):
    try:
        from agents.agent_manager import get_agent_manager
        manager = get_agent_manager()
        task_id = await manager.submit_task("osiris", "forecast", deal=deal)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/osiris/batch-forecast")
async def osiris_batch_forecast(deals: List[Dict[str, Any]]):
    try:
        from agents.agent_manager import get_agent_manager
        manager = get_agent_manager()
        task_id = await manager.submit_task("osiris", "batch_forecast", deals=deals)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Response models
class AgentHealthResponse(BaseModel):
    """Agent health response model."""
    agent_id: str
    name: str
    status: str
    health_score: float
    last_heartbeat: datetime
    success_rate: float
    average_response_time: float
    current_tasks: int
    total_tasks_24h: int
    completed_tasks_24h: int
    failed_tasks_24h: int
    last_error: Optional[str]
    last_error_time: Optional[datetime]

class SystemHealthResponse(BaseModel):
    """System health response model."""
    total_agents: int
    online_agents: int
    error_agents: int
    system_health: str
    recent_activities: int
    pending_tasks: int
    running_tasks: int
    timestamp: datetime

class PaginatedResponse(BaseModel):
    """Paginated response model."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

# Agent Management Endpoints
@router.post("/", response_model=AIAgentResponse, status_code=201)
async def create_agent(
    agent_data: AIAgentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new AI agent."""
    try:
        service = AIAgentService(db)
        agent = await service.create_agent(agent_data)
        
        # Start agent in background
        background_tasks.add_task(start_agent_background, agent.id)
        
        return agent
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")

@router.get("/", response_model=PaginatedResponse)
async def get_agents(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    agent_type: Optional[AgentType] = Query(None, description="Filter by agent type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    status: Optional[AgentStatus] = Query(None, description="Filter by current status"),
    db: Session = Depends(get_db)
):
    """Get AI agents with filtering and pagination."""
    try:
        service = AIAgentService(db)
        agents, total = await service.get_agents(
            skip=skip,
            limit=limit,
            agent_type=agent_type,
            is_active=is_active,
            status=status
        )
        
        total_pages = (total + limit - 1) // limit
        page = (skip // limit) + 1
        
        return PaginatedResponse(
            items=agents,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")

@router.get("/{agent_id}", response_model=AIAgentResponse)
async def get_agent(
    agent_id: str = Path(..., description="Agent ID"),
    db: Session = Depends(get_db)
):
    """Get a specific AI agent by ID."""
    try:
        service = AIAgentService(db)
        agent = await service.get_agent(agent_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent: {str(e)}")

@router.put("/{agent_id}", response_model=AIAgentResponse)
async def update_agent(
    agent_id: str = Path(..., description="Agent ID"),
    agent_data: AIAgentUpdate = None,
    db: Session = Depends(get_db)
):
    """Update an AI agent."""
    try:
        service = AIAgentService(db)
        agent = await service.update_agent(agent_id, agent_data)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update agent: {str(e)}")

@router.delete("/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: str = Path(..., description="Agent ID"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Delete an AI agent."""
    try:
        service = AIAgentService(db)
        success = await service.delete_agent(agent_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Stop agent in background
        if background_tasks:
            background_tasks.add_task(stop_agent_background, agent_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete agent: {str(e)}")

# Agent Control Endpoints
@router.post("/{agent_id}/start", status_code=200)
async def start_agent(
    agent_id: str = Path(..., description="Agent ID"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Start an AI agent."""
    try:
        service = AIAgentService(db)
        
        # Check if agent exists
        agent = await service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Update status to online
        await service.update_agent_status(agent_id, AgentStatus.ONLINE)
        
        # Start agent in background
        if background_tasks:
            background_tasks.add_task(start_agent_background, agent_id)
        
        return {"message": f"Agent {agent_id} started successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")

@router.post("/{agent_id}/stop", status_code=200)
async def stop_agent(
    agent_id: str = Path(..., description="Agent ID"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Stop an AI agent."""
    try:
        service = AIAgentService(db)
        
        # Check if agent exists
        agent = await service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Cancel all pending/running tasks
        await service.cancel_agent_tasks(agent_id, TaskStatus.PENDING)
        await service.cancel_agent_tasks(agent_id, TaskStatus.RUNNING)
        
        # Update status to offline
        await service.update_agent_status(agent_id, AgentStatus.OFFLINE)
        
        # Stop agent in background
        if background_tasks:
            background_tasks.add_task(stop_agent_background, agent_id)
        
        return {"message": f"Agent {agent_id} stopped successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop agent: {str(e)}")

@router.post("/{agent_id}/restart", status_code=200)
async def restart_agent(
    agent_id: str = Path(..., description="Agent ID"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Restart an AI agent."""
    try:
        service = AIAgentService(db)
        
        # Check if agent exists
        agent = await service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Stop first
        await service.cancel_agent_tasks(agent_id, TaskStatus.PENDING)
        await service.cancel_agent_tasks(agent_id, TaskStatus.RUNNING)
        await service.update_agent_status(agent_id, AgentStatus.OFFLINE)
        
        # Start again
        await service.update_agent_status(agent_id, AgentStatus.ONLINE)
        
        # Restart agent in background
        if background_tasks:
            background_tasks.add_task(restart_agent_background, agent_id)
        
        return {"message": f"Agent {agent_id} restarted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restart agent: {str(e)}")

# Task Management Endpoints
@router.post("/{agent_id}/tasks", response_model=AgentTaskResponse, status_code=201)
async def create_task(
    agent_id: str = Path(..., description="Agent ID"),
    task_data: AgentTaskCreate = None,
    db: Session = Depends(get_db)
):
    """Create a new task for an AI agent."""
    try:
        service = AIAgentService(db)
        
        # Set agent_id from path
        task_data.agent_id = agent_id
        
        task = await service.create_task(task_data)
        return task
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")

@router.get("/{agent_id}/tasks", response_model=PaginatedResponse)
async def get_agent_tasks(
    agent_id: str = Path(..., description="Agent ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    db: Session = Depends(get_db)
):
    """Get tasks for a specific AI agent."""
    try:
        service = AIAgentService(db)
        tasks, total = await service.get_agent_tasks(
            agent_id=agent_id,
            skip=skip,
            limit=limit,
            status=status,
            task_type=task_type
        )
        
        total_pages = (total + limit - 1) // limit
        page = (skip // limit) + 1
        
        return PaginatedResponse(
            items=tasks,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent tasks: {str(e)}")

@router.get("/tasks/{task_id}", response_model=AgentTaskResponse)
async def get_task(
    task_id: str = Path(..., description="Task ID"),
    db: Session = Depends(get_db)
):
    """Get a specific task by ID."""
    try:
        service = AIAgentService(db)
        task = await service.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task: {str(e)}")

@router.put("/tasks/{task_id}", response_model=AgentTaskResponse)
async def update_task(
    task_id: str = Path(..., description="Task ID"),
    task_data: AgentTaskUpdate = None,
    db: Session = Depends(get_db)
):
    """Update a task."""
    try:
        service = AIAgentService(db)
        task = await service.update_task(task_id, task_data)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")

@router.post("/{agent_id}/tasks/cancel", status_code=200)
async def cancel_agent_tasks(
    agent_id: str = Path(..., description="Agent ID"),
    status: TaskStatus = Query(..., description="Task status to cancel"),
    db: Session = Depends(get_db)
):
    """Cancel all tasks for an agent with specific status."""
    try:
        service = AIAgentService(db)
        cancelled_count = await service.cancel_agent_tasks(agent_id, status)
        
        return {
            "message": f"Cancelled {cancelled_count} tasks for agent {agent_id}",
            "cancelled_count": cancelled_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel tasks: {str(e)}")

# Activity Management Endpoints
@router.post("/{agent_id}/activities", response_model=AgentActivityResponse, status_code=201)
async def create_activity(
    agent_id: str = Path(..., description="Agent ID"),
    activity_data: AgentActivityCreate = None,
    db: Session = Depends(get_db)
):
    """Create an activity log entry for an AI agent."""
    try:
        service = AIAgentService(db)
        
        # Set agent_id from path
        activity_data.agent_id = agent_id
        
        activity = await service.create_activity(activity_data)
        return activity
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create activity: {str(e)}")

@router.get("/{agent_id}/activities", response_model=PaginatedResponse)
async def get_agent_activities(
    agent_id: str = Path(..., description="Agent ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    level: Optional[str] = Query(None, description="Filter by activity level"),
    hours_back: int = Query(24, ge=1, le=168, description="Hours back to look for activities"),
    db: Session = Depends(get_db)
):
    """Get activities for a specific AI agent."""
    try:
        service = AIAgentService(db)
        activities, total = await service.get_agent_activities(
            agent_id=agent_id,
            skip=skip,
            limit=limit,
            activity_type=activity_type,
            level=level,
            hours_back=hours_back
        )
        
        total_pages = (total + limit - 1) // limit
        page = (skip // limit) + 1
        
        return PaginatedResponse(
            items=activities,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent activities: {str(e)}")

# Health and Monitoring Endpoints
@router.get("/{agent_id}/health", response_model=AgentHealthResponse)
async def get_agent_health(
    agent_id: str = Path(..., description="Agent ID"),
    db: Session = Depends(get_db)
):
    """Get comprehensive health information for an AI agent."""
    try:
        service = AIAgentService(db)
        health = await service.get_agent_health(agent_id)
        
        if not health:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return AgentHealthResponse(**health)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent health: {str(e)}")

@router.get("/health/system", response_model=SystemHealthResponse)
async def get_system_health(
    db: Session = Depends(get_db)
):
    """Get overall system health for all AI agents."""
    try:
        service = AIAgentService(db)
        health = await service.get_system_health()
        
        return SystemHealthResponse(**health)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")

# Capability Management Endpoints
@router.post("/{agent_id}/capabilities", response_model=AgentCapabilityResponse, status_code=201)
async def create_capability(
    agent_id: str = Path(..., description="Agent ID"),
    capability_data: AgentCapabilityCreate = None,
    db: Session = Depends(get_db)
):
    """Create a capability for an AI agent."""
    try:
        service = AIAgentService(db)
        
        # Set agent_id from path
        capability_data.agent_id = agent_id
        
        capability = await service.create_capability(capability_data)
        return capability
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create capability: {str(e)}")

@router.get("/{agent_id}/capabilities", response_model=List[AgentCapabilityResponse])
async def get_agent_capabilities(
    agent_id: str = Path(..., description="Agent ID"),
    db: Session = Depends(get_db)
):
    """Get capabilities for a specific AI agent."""
    try:
        service = AIAgentService(db)
        capabilities = await service.get_agent_capabilities(agent_id)
        
        return capabilities
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent capabilities: {str(e)}")

# Background task functions
async def start_agent_background(agent_id: str):
    """Background task to start an agent."""
    try:
        # Import here to avoid circular imports
        from agents.agent_manager import get_agent_manager
        
        manager = get_agent_manager()
        await manager.start_agent(agent_id)
        
        logger.info(f"Started agent {agent_id} in background")
        
    except Exception as e:
        logger.error(f"Failed to start agent {agent_id} in background: {e}")

async def stop_agent_background(agent_id: str):
    """Background task to stop an agent."""
    try:
        # Import here to avoid circular imports
        from agents.agent_manager import get_agent_manager
        
        manager = get_agent_manager()
        await manager.stop_agent(agent_id)
        
        logger.info(f"Stopped agent {agent_id} in background")
        
    except Exception as e:
        logger.error(f"Failed to stop agent {agent_id} in background: {e}")

async def restart_agent_background(agent_id: str):
    """Background task to restart an agent."""
    try:
        # Import here to avoid circular imports
        from agents.agent_manager import get_agent_manager
        
        manager = get_agent_manager()
        await manager.stop_agent(agent_id)
        await asyncio.sleep(1)  # Brief pause
        await manager.start_agent(agent_id)
        
        logger.info(f"Restarted agent {agent_id} in background")
        
    except Exception as e:
        logger.error(f"Failed to restart agent {agent_id} in background: {e}")

# WebSocket endpoint for real-time updates
@router.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket, agent_id: str):
    """WebSocket endpoint for real-time agent updates."""
    try:
        await websocket.accept()
        
        # Subscribe to agent-specific events
        websocket_manager = get_websocket_manager()
        if websocket_manager:
            await websocket_manager.connect(websocket, f"agent:{agent_id}")
        
        # Keep connection alive
        while True:
            try:
                # Send ping to keep connection alive
                await websocket.ping()
                await asyncio.sleep(30)
            except Exception:
                break
                
    except Exception as e:
        logger.error(f"WebSocket error for agent {agent_id}: {e}")
    finally:
        if websocket_manager:
            await websocket_manager.disconnect(websocket)
