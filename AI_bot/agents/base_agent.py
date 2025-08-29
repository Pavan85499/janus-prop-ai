"""
Base Agent Class for Real Estate AI Agents

This module provides the foundational class that all specialized agents inherit from.
It defines the common interface, error handling, logging, and basic functionality.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import structlog
from pydantic import BaseModel, Field

from core.communication import Message, MessageType
from core.exceptions import AgentError, AgentTimeoutError, ValidationError


class AgentConfig(BaseModel):
    """Configuration for an agent instance."""
    
    agent_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    model: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 4000
    timeout: int = 60
    max_retries: int = 3
    enabled: bool = True
    version: str = "1.0.0"
    
    class Config:
        extra = "allow"


class AgentResponse(BaseModel):
    """Standard response format for all agents."""
    
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str
    processing_time: Optional[float] = None


class BaseAgent(ABC):
    """
    Base class for all real estate AI agents.
    
    This class provides:
    - Common interface for all agents
    - Error handling and logging
    - Configuration management
    - Performance monitoring
    - Communication protocols
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = structlog.get_logger(self.__class__.__name__)
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "last_request_time": None
        }
        self._is_healthy = True

    async def start(self):
        """Start the agent."""
        self.logger.info("Starting agent", agent_name=self.config.name)
        self._is_healthy = True
        
    async def process_request(
        self, 
        request: Union[str, Dict[str, Any]], 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Main entry point for processing requests.
        
        Args:
            request: The request to process (string or structured data)
            context: Additional context for the request
            
        Returns:
            AgentResponse: Standardized response format
            
        Raises:
            AgentError: For agent-specific errors
            AgentTimeoutError: If processing exceeds timeout
            ValidationError: If request validation fails
        """
        start_time = datetime.utcnow()
        request_id = str(uuid4())
        
        try:
            # Validate request
            validated_request = self._validate_request(request, context)
            
            # Log request
            self.logger.info(
                "Processing request",
                request_id=request_id,
                agent_name=self.config.name,
                request_type=type(request).__name__
            )
            
            # Process request
            result = await self._process_request_impl(validated_request, context)
            
            # Update stats
            self._update_stats(True, start_time)
            
            # Return success response
            return AgentResponse(
                success=True,
                data=result,
                metadata={
                    "request_id": request_id,
                    "agent_version": self.config.version,
                    "model_used": self.config.model
                },
                agent_id=self.config.agent_id,
                processing_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
        except Exception as e:
            # Update stats
            self._update_stats(False, start_time)
            
            # Log error
            self.logger.error(
                "Request processing failed",
                request_id=request_id,
                error=str(e),
                error_type=type(e).__name__
            )
            
            # Return error response
            return AgentResponse(
                success=False,
                error=str(e),
                metadata={
                    "request_id": request_id,
                    "error_type": type(e).__name__,
                    "agent_version": self.config.version
                },
                agent_id=self.config.agent_id,
                processing_time=(datetime.utcnow() - start_time).total_seconds()
            )
    
    @abstractmethod
    async def _process_request_impl(
        self, 
        request: Any, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Abstract method that each agent must implement.
        
        Args:
            request: Validated request data
            context: Additional context
            
        Returns:
            Dict containing the processing results
        """
        pass
    
    def _validate_request(
        self, 
        request: Union[str, Dict[str, Any]], 
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Validate the incoming request.
        
        Args:
            request: The request to validate
            context: Additional context
            
        Returns:
            Validated request data
            
        Raises:
            ValidationError: If validation fails
        """
        if not request:
            raise ValidationError("Request cannot be empty")
        
        # Basic validation - subclasses can override for specific validation
        return request
    
    def _update_stats(self, success: bool, start_time: datetime):
        """Update agent statistics."""
        self.stats["total_requests"] += 1
        
        if success:
            self.stats["successful_requests"] += 1
        else:
            self.stats["failed_requests"] += 1
        
        self.stats["last_request_time"] = datetime.utcnow()
        
        # Update average response time
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        current_avg = self.stats["average_response_time"]
        total_requests = self.stats["total_requests"]
        
        self.stats["average_response_time"] = (
            (current_avg * (total_requests - 1) + processing_time) / total_requests
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check agent health status."""
        return {
            "agent_id": self.config.agent_id,
            "name": self.config.name,
            "status": "healthy" if self._is_healthy else "unhealthy",
            "enabled": self.config.enabled,
            "version": self.config.version,
            "stats": self.stats.copy(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities and supported operations."""
        return {
            "agent_id": self.config.agent_id,
            "name": self.config.name,
            "description": self.config.description,
            "supported_operations": self._get_supported_operations(),
            "version": self.config.version
        }
    
    @abstractmethod
    def _get_supported_operations(self) -> List[str]:
        """Return list of operations this agent supports."""
        pass
    
    async def shutdown(self):
        """Gracefully shutdown the agent."""
        self.logger.info("Shutting down agent", agent_name=self.config.name)
        self._is_healthy = False
        
        # Perform any cleanup
        await self._cleanup()
    
    async def _cleanup(self):
        """Override in subclasses for cleanup operations."""
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.config.name})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(config={self.config})"
