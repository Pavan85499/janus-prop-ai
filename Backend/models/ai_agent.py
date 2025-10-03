"""
AI Agent models for Janus Prop AI Backend

This module defines comprehensive AI agent database models.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

Base = declarative_base()

class AgentStatus(str, Enum):
    """Agent status enumeration."""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class AgentType(str, Enum):
    """Agent type enumeration."""
    AI_INSIGHTS = "ai_insights"
    GEMINI = "gemini"
    ATTOM = "attom"
    MARKET_ANALYSIS = "market_analysis"
    LEAD_MANAGEMENT = "lead_management"
    PROPERTY_ANALYSIS = "property_analysis"
    DOCUMENT_PROCESSING = "document_processing"
    INVESTMENT_COMMITTEE = "investment_committee"

class AIAgent(Base):
    """AI Agent database model."""
    
    __tablename__ = "ai_agents"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    agent_type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    version = Column(String(20), default="1.0.0")
    
    # Configuration
    is_active = Column(Boolean, default=True)
    config = Column(JSON, nullable=True)
    capabilities = Column(JSON, nullable=True)  # List of capabilities
    limitations = Column(JSON, nullable=True)   # List of limitations
    
    # Performance metrics
    max_concurrent_tasks = Column(Integer, default=5)
    priority = Column(String(20), default="normal")
    health_score = Column(Float, default=1.0)
    average_response_time = Column(Float, default=0.0)
    
    # Statistics
    total_tasks_completed = Column(Integer, default=0)
    total_tasks_failed = Column(Integer, default=0)
    total_runtime_hours = Column(Float, default=0.0)
    
    # Status tracking
    current_status = Column(String(20), default=AgentStatus.OFFLINE)
    last_heartbeat = Column(DateTime, default=func.utcnow)
    last_error = Column(Text, nullable=True)
    last_error_time = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.utcnow)
    updated_at = Column(DateTime, default=func.utcnow, onupdate=func.utcnow)
    created_by = Column(String(36), nullable=True)
    
    # Relationships
    tasks = relationship("AgentTask", back_populates="agent", cascade="all, delete-orphan")
    activities = relationship("AgentActivity", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AIAgent(id='{self.id}', name='{self.name}', type='{self.agent_type}')>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "agent_type": self.agent_type,
            "description": self.description,
            "version": self.version,
            "is_active": self.is_active,
            "config": self.config,
            "capabilities": self.capabilities,
            "limitations": self.limitations,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "priority": self.priority,
            "health_score": self.health_score,
            "average_response_time": self.average_response_time,
            "total_tasks_completed": self.total_tasks_completed,
            "total_tasks_failed": self.total_tasks_failed,
            "total_runtime_hours": self.total_runtime_hours,
            "current_status": self.current_status,
            "last_heartbeat": self.last_heartbeat,
            "last_error": self.last_error,
            "last_error_time": self.last_error_time,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by
        }

class AgentTask(Base):
    """Agent Task database model."""
    
    __tablename__ = "agent_tasks"
    
    id = Column(String(36), primary_key=True, index=True)
    agent_id = Column(String(36), ForeignKey("ai_agents.id"), nullable=False, index=True)
    
    # Task details
    task_type = Column(String(100), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    priority = Column(String(20), default=TaskPriority.NORMAL)
    status = Column(String(20), default=TaskStatus.PENDING, index=True)
    
    # Task data
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Timing
    created_at = Column(DateTime, default=func.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # seconds
    actual_duration = Column(Integer, nullable=True)     # seconds
    
    # Metadata
    task_metadata = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)  # List of tags
    created_by = Column(String(36), nullable=True)
    
    # Relationships
    agent = relationship("AIAgent", back_populates="tasks")
    
    def __repr__(self):
        return f"<AgentTask(id='{self.id}', agent_id='{self.agent_id}', type='{self.task_type}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "task_type": self.task_type,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "progress": self.progress,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "estimated_duration": self.estimated_duration,
            "actual_duration": self.actual_duration,
            "task_metadata": self.task_metadata,
            "tags": self.tags,
            "created_by": self.created_by
        }

class AgentActivity(Base):
    """Agent Activity database model."""
    
    __tablename__ = "agent_activities"
    
    id = Column(String(36), primary_key=True, index=True)
    agent_id = Column(String(36), ForeignKey("ai_agents.id"), nullable=False, index=True)
    
    # Activity details
    activity_type = Column(String(100), nullable=False, index=True)
    message = Column(Text, nullable=False)
    level = Column(String(20), default="info")  # info, warning, error, critical
    status = Column(String(20), default="in_progress")  # in_progress, completed, failed
    
    # Context
    task_id = Column(String(36), nullable=True, index=True)
    property_id = Column(String(36), nullable=True, index=True)
    user_id = Column(String(36), nullable=True, index=True)
    
    # Data
    data = Column(JSON, nullable=True)
    activity_metadata = Column(JSON, nullable=True)
    
    # Timing
    timestamp = Column(DateTime, default=func.utcnow, index=True)
    duration = Column(Integer, nullable=True)  # seconds
    
    # Relationships
    agent = relationship("AIAgent", back_populates="activities")
    
    def __repr__(self):
        return f"<AgentActivity(id='{self.id}', agent_id='{self.agent_id}', type='{self.activity_type}')>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "activity_type": self.activity_type,
            "message": self.message,
            "level": self.level,
            "status": self.status,
            "task_id": self.task_id,
            "property_id": self.property_id,
            "user_id": self.user_id,
            "data": self.data,
            "activity_metadata": self.activity_metadata,
            "timestamp": self.timestamp,
            "duration": self.duration
        }

class AgentCapability(Base):
    """Agent Capability database model."""
    
    __tablename__ = "agent_capabilities"
    
    id = Column(String(36), primary_key=True, index=True)
    agent_id = Column(String(36), ForeignKey("ai_agents.id"), nullable=False, index=True)
    
    # Capability details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(20), default="1.0.0")
    is_enabled = Column(Boolean, default=True)
    
    # Configuration
    config = Column(JSON, nullable=True)
    parameters = Column(JSON, nullable=True)
    
    # Performance
    success_rate = Column(Float, default=0.0)
    average_duration = Column(Float, default=0.0)
    total_executions = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=func.utcnow)
    updated_at = Column(DateTime, default=func.utcnow, onupdate=func.utcnow)
    
    def __repr__(self):
        return f"<AgentCapability(id='{self.id}', agent_id='{self.agent_id}', name='{self.name}')>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "is_enabled": self.is_enabled,
            "config": self.config,
            "parameters": self.parameters,
            "success_rate": self.success_rate,
            "average_duration": self.average_duration,
            "total_executions": self.total_executions,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

# Pydantic models for API
class AIAgentCreate(BaseModel):
    """Model for creating an AI agent."""
    name: str = Field(..., min_length=1, max_length=100)
    agent_type: AgentType
    description: Optional[str] = None
    version: str = Field(default="1.0.0", max_length=20)
    config: Optional[Dict[str, Any]] = None
    capabilities: Optional[List[str]] = None
    limitations: Optional[List[str]] = None
    max_concurrent_tasks: int = Field(default=5, ge=1, le=50)
    priority: TaskPriority = TaskPriority.NORMAL

class AIAgentUpdate(BaseModel):
    """Model for updating an AI agent."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    version: Optional[str] = Field(None, max_length=20)
    config: Optional[Dict[str, Any]] = None
    capabilities: Optional[List[str]] = None
    limitations: Optional[List[str]] = None
    max_concurrent_tasks: Optional[int] = Field(None, ge=1, le=50)
    priority: Optional[TaskPriority] = None
    is_active: Optional[bool] = None

class AIAgentResponse(BaseModel):
    """Model for AI agent response."""
    id: str
    name: str
    agent_type: str
    description: Optional[str]
    version: str
    is_active: bool
    config: Optional[Dict[str, Any]]
    capabilities: Optional[List[str]]
    limitations: Optional[List[str]]
    max_concurrent_tasks: int
    priority: str
    health_score: float
    average_response_time: float
    total_tasks_completed: int
    total_tasks_failed: int
    total_runtime_hours: float
    current_status: str
    last_heartbeat: datetime
    last_error: Optional[str]
    last_error_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

class AgentTaskCreate(BaseModel):
    """Model for creating an agent task."""
    agent_id: str
    task_type: str = Field(..., min_length=1, max_length=100)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.NORMAL
    input_data: Optional[Dict[str, Any]] = None
    task_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    estimated_duration: Optional[int] = None  # seconds

class AgentTaskUpdate(BaseModel):
    """Model for updating an agent task."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    progress: Optional[float] = Field(None, ge=0.0, le=1.0)
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    task_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class AgentTaskResponse(BaseModel):
    """Model for agent task response."""
    id: str
    agent_id: str
    task_type: str
    title: Optional[str]
    description: Optional[str]
    priority: str
    status: str
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    progress: float
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_duration: Optional[int]
    actual_duration: Optional[int]
    task_metadata: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    created_by: Optional[str]

class AgentActivityCreate(BaseModel):
    """Model for creating agent activity."""
    agent_id: str
    activity_type: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1)
    level: str = Field(default="info", pattern="^(info|warning|error|critical)$")
    status: str = Field(default="in_progress", pattern="^(in_progress|completed|failed)$")
    task_id: Optional[str] = None
    property_id: Optional[str] = None
    user_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    activity_metadata: Optional[Dict[str, Any]] = None

class AgentActivityResponse(BaseModel):
    """Model for agent activity response."""
    id: str
    agent_id: str
    activity_type: str
    message: str
    level: str
    status: str
    task_id: Optional[str]
    property_id: Optional[str]
    user_id: Optional[str]
    data: Optional[Dict[str, Any]]
    activity_metadata: Optional[Dict[str, Any]]
    timestamp: datetime
    duration: Optional[int]

class AgentCapabilityCreate(BaseModel):
    """Model for creating agent capability."""
    agent_id: str
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    version: str = Field(default="1.0.0", max_length=20)
    config: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None

class AgentCapabilityResponse(BaseModel):
    """Model for agent capability response."""
    id: str
    agent_id: str
    name: str
    description: Optional[str]
    version: str
    is_enabled: bool
    config: Optional[Dict[str, Any]]
    parameters: Optional[Dict[str, Any]]
    success_rate: float
    average_duration: float
    total_executions: int
    created_at: datetime
    updated_at: datetime
