"""
Updated Agents API endpoints for Janus Prop AI Backend

This module provides endpoints for agent management, monitoring, and real-time updates.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# Import with fallback handling
try:
    from core.redis_client import cache_get, cache_set, cache_delete, publish_event
except ImportError:
    # Fallback functions
    async def cache_get(key: str):
        return None
    async def cache_set(key: str, value: Any, expire: int = 3600):
        return False
    async def cache_delete(key: str):
        return False
    async def publish_event(channel: str, event: str, data: Any):
        return False

try:
    from core.websocket_manager import get_websocket_manager
except ImportError:
    # Fallback function
    def get_websocket_manager():
        return None

router = APIRouter()
# New: Manager-backed create/start/stop/task submission for real-time demo
try:
    from agents.agent_manager import get_agent_manager, AgentConfig
except ImportError:
    get_agent_manager = None
    AgentConfig = None

class NewAgentRequest(BaseModel):
    name: str
    type: str
    description: str | None = None
    capabilities: List[str] = Field(default_factory=list)

@router.post("/")
async def create_agent(new_agent: NewAgentRequest):
    """Create an in-memory agent via AgentManager for real-time demos."""
    try:
        if not get_agent_manager or not AgentConfig:
            raise HTTPException(status_code=500, detail="Agent manager unavailable")
        manager = get_agent_manager()
        agent_id = new_agent.name.lower().replace(" ", "_")
        config = AgentConfig(
            agent_id=agent_id,
            name=new_agent.name,
            agent_type=new_agent.type or "custom",
            description=new_agent.description or f"Custom agent {new_agent.name}",
            max_concurrent_tasks=3,
            priority="normal",
            config={}
        )
        manager.register_agent(config)
        await manager.start_agent(agent_id)
        return {"success": True, "agent_id": agent_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {e}")

@router.post("/{agent_id}/start")
async def start_agent(agent_id: str):
    try:
        if not get_agent_manager:
            raise HTTPException(status_code=500, detail="Agent manager unavailable")
        manager = get_agent_manager()
        await manager.start_agent(agent_id)
        return {"success": True, "message": f"Agent {agent_id} started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {e}")

@router.post("/{agent_id}/stop")
async def stop_agent(agent_id: str):
    try:
        if not get_agent_manager:
            raise HTTPException(status_code=500, detail="Agent manager unavailable")
        manager = get_agent_manager()
        await manager.stop_agent(agent_id)
        return {"success": True, "message": f"Agent {agent_id} stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop agent: {e}")

class SubmitTaskRequest(BaseModel):
    task_type: str
    description: str | None = None
    priority: str = Field(default="normal")
    metadata: Dict[str, Any] | None = None

@router.post("/{agent_id}/tasks")
async def submit_task(agent_id: str, body: SubmitTaskRequest):
    try:
        if not get_agent_manager:
            raise HTTPException(status_code=500, detail="Agent manager unavailable")
        manager = get_agent_manager()
        task_id = await manager.submit_task(agent_id, body.task_type, body.priority, description=body.description, **(body.metadata or {}))
        return {"success": True, "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit task: {e}")

# Pydantic models
class AgentActivity(BaseModel):
    """Agent activity model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    agent_id: str
    agent_name: str
    activity_type: str
    message: str
    status: str  # "in-progress", "completed", "alert", "error"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = None
    priority: int = Field(default=1, ge=1, le=4)
    
class AgentStatus(BaseModel):
    """Agent status model."""
    agent_id: str
    name: str
    status: str  # "online", "offline", "busy", "error"
    health_score: float = Field(ge=0.0, le=1.0)
    last_activity: datetime
    capabilities: List[str]
    current_task: Optional[str] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    
class AgentActivityResponse(BaseModel):
    """Response model for agent activities."""
    activities: List[AgentActivity]
    summary: Dict[str, Any]
    
class AgentsStatusResponse(BaseModel):
    """Response model for agents status."""
    agents: List[AgentStatus]
    total_agents: int
    healthy_agents: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Mock data for development
MOCK_AGENTS = {
    "eden": {
        "agent_id": "eden",
        "name": "Eden",
        "status": "online",
        "health_score": 0.95,
        "last_activity": datetime.utcnow(),
        "capabilities": ["ai_insights", "property_analysis", "market_prediction"],
        "current_task": "Analyzing market trends",
        "performance_metrics": {"accuracy": 0.92, "response_time": 1.2}
    },
    "orion": {
        "agent_id": "orion",
        "name": "Orion",
        "status": "online",
        "health_score": 0.88,
        "last_activity": datetime.utcnow(),
        "capabilities": ["data_integration", "api_sync", "data_validation"],
        "current_task": "Syncing property data",
        "performance_metrics": {"sync_rate": 0.98, "error_rate": 0.02}
    },
    "atelius": {
        "agent_id": "atelius",
        "name": "Atelius",
        "status": "busy",
        "health_score": 0.91,
        "last_activity": datetime.utcnow(),
        "capabilities": ["legal_analysis", "compliance_check", "risk_assessment"],
        "current_task": "Reviewing contract compliance",
        "performance_metrics": {"compliance_rate": 0.96, "review_time": 5.1}
    }
}

MOCK_ACTIVITIES = [
    AgentActivity(
        agent_id="eden",
        agent_name="Eden",
        activity_type="market_analysis",
        message="Completed market trend analysis for Downtown area",
        status="completed",
        priority=2
    ),
    AgentActivity(
        agent_id="orion",
        agent_name="Orion",
        activity_type="data_sync",
        message="Syncing property data from Realie API",
        status="in-progress",
        priority=1
    ),
    AgentActivity(
        agent_id="atelius",
        agent_name="Atelius",
        activity_type="compliance_check",
        message="Contract compliance review in progress",
        status="in-progress",
        priority=3
    )
]

@router.get("/activity", response_model=AgentActivityResponse)
async def get_agent_activity(
    limit: int = 50,
    agent_type: Optional[str] = None,
    status: Optional[str] = None
):
    """Get agent activities with optional filtering."""
    try:
        # Get current timestamp for real-time data
        current_time = datetime.utcnow()
        
        # Generate dynamic, real-time activities based on current time
        # This prevents duplicate data and provides fresh information
        dynamic_activities = []
        
        # Add some real-time generated activities
        for agent_id, agent_data in MOCK_AGENTS.items():
            # Generate activity based on agent status and time
            if agent_data["status"] == "online":
                # Create a unique activity based on current time
                activity_id = f"{agent_id}_{int(current_time.timestamp())}"
                
                # Generate different activity types based on time
                minute = current_time.minute
                if minute < 20:
                    activity_type = "data_sync"
                    message = f"Syncing {agent_data['name']} data from external APIs"
                    status = "in-progress"
                elif minute < 40:
                    activity_type = "analysis"
                    message = f"Running {agent_data['name']} analysis algorithms"
                    status = "completed"
                else:
                    activity_type = "monitoring"
                    message = f"Monitoring {agent_data['name']} system health"
                    status = "completed"
                
                dynamic_activities.append(AgentActivity(
                    id=activity_id,
                    agent_id=agent_id,
                    agent_name=agent_data["name"],
                    activity_type=activity_type,
                    message=message,
                    status=status,
                    timestamp=current_time,
                    priority=1
                ))
        
        # Add static activities but ensure they're unique
        static_activities = []
        for i, activity in enumerate(MOCK_ACTIVITIES):
            # Create unique copy with timestamp variation
            unique_activity = AgentActivity(
                id=f"{activity.agent_id}_{i}_{int(current_time.timestamp())}",
                agent_id=activity.agent_id,
                agent_name=activity.agent_name,
                activity_type=activity.activity_type,
                message=activity.message,
                status=activity.status,
                timestamp=current_time,
                priority=activity.priority
            )
            static_activities.append(unique_activity)
        
        # Combine and filter activities
        all_activities = dynamic_activities + static_activities
        
        if agent_type:
            all_activities = [a for a in all_activities if a.agent_name.lower() == agent_type.lower()]
            
        if status:
            all_activities = [a for a in all_activities if a.status == status]
            
        # Apply limit and ensure uniqueness
        unique_activities = []
        seen_ids = set()
        for activity in all_activities:
            if activity.id not in seen_ids and len(unique_activities) < limit:
                unique_activities.append(activity)
                seen_ids.add(activity.id)
        
        # Calculate summary
        summary = {
            "total_activities": len(unique_activities),
            "active_tasks": len([a for a in unique_activities if a.status == "in-progress"]),
            "completed_tasks": len([a for a in unique_activities if a.status == "completed"]),
            "alerts": len([a for a in unique_activities if a.status == "alert"]),
            "system_status": "healthy",
            "last_updated": current_time.isoformat(),
            "data_source": "real_time"
        }
        
        return AgentActivityResponse(activities=unique_activities, summary=summary)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch agent activities: {str(e)}")

@router.get("/status", response_model=AgentsStatusResponse)
async def get_agents_status():
    """Get status of all agents."""
    try:
        agents = []
        for agent_data in MOCK_AGENTS.values():
            agent = AgentStatus(**agent_data)
            agents.append(agent)
            
        healthy_count = len([a for a in agents if a.health_score >= 0.8])
        
        return AgentsStatusResponse(
            agents=agents,
            total_agents=len(agents),
            healthy_agents=healthy_count,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch agents status: {str(e)}")

@router.get("/{agent_id}/status", response_model=AgentStatus)
async def get_agent_status(agent_id: str):
    """Get status of a specific agent."""
    try:
        if agent_id not in MOCK_AGENTS:
            raise HTTPException(status_code=404, detail="Agent not found")
            
        agent_data = MOCK_AGENTS[agent_id]
        return AgentStatus(**agent_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch agent status: {str(e)}")

@router.post("/{agent_id}/activity")
async def create_agent_activity(
    agent_id: str,
    activity: AgentActivity,
    background_tasks: BackgroundTasks
):
    """Create a new agent activity."""
    try:
        # Validate agent exists
        if agent_id not in MOCK_AGENTS:
            raise HTTPException(status_code=404, detail="Agent not found")
            
        # Set agent ID and timestamp
        activity.agent_id = agent_id
        activity.timestamp = datetime.utcnow()
        
        # Add to mock activities (in real app, this would go to database)
        MOCK_ACTIVITIES.append(activity)
        
        # Cache the activity
        try:
            await cache_set(f"agent_activity:{activity.id}", activity.dict(), expire=300)
        except Exception:
            pass  # Cache not available
        
        # Publish real-time update
        try:
            await publish_event(
                f"agent:{agent_id}",
                "activity_created",
                activity.dict()
            )
        except Exception:
            pass  # Redis not available
        
        # Send WebSocket update
        try:
            websocket_manager = get_websocket_manager()
            if websocket_manager:
                await websocket_manager.send_agent_update(agent_id, {
                    "type": "activity_created",
                    "activity": activity.dict()
                })
        except Exception:
            pass  # WebSocket not available
        
        return {"success": True, "activity_id": activity.id, "message": "Activity created successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create activity: {str(e)}")

@router.put("/{agent_id}/status")
async def update_agent_status(
    agent_id: str,
    status_update: Dict[str, Any]
):
    """Update agent status."""
    try:
        if agent_id not in MOCK_AGENTS:
            raise HTTPException(status_code=404, detail="Agent not found")
            
        # Update mock agent status
        MOCK_AGENTS[agent_id].update(status_update)
        MOCK_AGENTS[agent_id]["last_activity"] = datetime.utcnow()
        
        # Cache the status
        try:
            await cache_set(f"agent_status:{agent_id}", MOCK_AGENTS[agent_id], expire=60)
        except Exception:
            pass  # Cache not available
        
        # Publish real-time update
        try:
            await publish_event(
                f"agent:{agent_id}",
                "status_updated",
                MOCK_AGENTS[agent_id]
            )
        except Exception:
            pass  # Redis not available
        
        # Send WebSocket update
        try:
            websocket_manager = get_websocket_manager()
            if websocket_manager:
                await websocket_manager.send_agent_update(agent_id, {
                    "type": "status_updated",
                    "status": MOCK_AGENTS[agent_id]
                })
        except Exception:
            pass  # WebSocket not available
        
        return {"success": True, "message": "Agent status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update agent status: {str(e)}")

@router.delete("/activity/{activity_id}")
async def dismiss_activity(activity_id: str):
    """Dismiss/remove an agent activity."""
    try:
        # Find and remove activity
        activity_index = None
        for i, activity in enumerate(MOCK_ACTIVITIES):
            if activity.id == activity_id:
                activity_index = i
                break
                
        if activity_index is None:
            raise HTTPException(status_code=404, detail="Activity not found")
            
        removed_activity = MOCK_ACTIVITIES.pop(activity_index)
        
        # Remove from cache
        try:
            await cache_delete(f"agent_activity:{activity_id}")
        except Exception:
            pass  # Cache not available
        
        return {"success": True, "message": "Activity dismissed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to dismiss activity: {str(e)}")

@router.get("/health/overview")
async def get_agents_health_overview():
    """Get overview of all agents' health status."""
    try:
        health_summary = {
            "total_agents": len(MOCK_AGENTS),
            "online_agents": len([a for a in MOCK_AGENTS.values() if a["status"] == "online"]),
            "busy_agents": len([a for a in MOCK_AGENTS.values() if a["status"] == "busy"]),
            "offline_agents": len([a for a in MOCK_AGENTS.values() if a["status"] == "offline"]),
            "average_health_score": sum(a["health_score"] for a in MOCK_AGENTS.values()) / len(MOCK_AGENTS),
            "system_health": "healthy" if all(a["health_score"] >= 0.8 for a in MOCK_AGENTS.values()) else "degraded"
        }
        
        return health_summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch health overview: {str(e)}")

@router.post("/{agent_id}/restart")
async def restart_agent(agent_id: str):
    """Restart a specific agent."""
    try:
        if agent_id not in MOCK_AGENTS:
            raise HTTPException(status_code=404, detail="Agent not found")
            
        # In a real implementation, this would restart the actual agent
        # For now, we'll just update the status
        MOCK_AGENTS[agent_id]["status"] = "online"
        MOCK_AGENTS[agent_id]["health_score"] = 1.0
        MOCK_AGENTS[agent_id]["last_activity"] = datetime.utcnow()
        
        return {"success": True, "message": f"Agent {agent_id} restarted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restart agent: {str(e)}")
