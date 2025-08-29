"""
Inter-Agent Communication System

This module provides the communication infrastructure for agents to interact
with each other, including message passing, event handling, and coordination.
"""

import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union
from uuid import uuid4

import structlog
from pydantic import BaseModel, Field

from core.exceptions import AgentCommunicationError


class MessageType(str, Enum):
    """Types of messages that can be sent between agents."""
    
    # Task-related messages
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    TASK_UPDATE = "task_update"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    
    # Coordination messages
    COORDINATION_REQUEST = "coordination_request"
    COORDINATION_RESPONSE = "coordination_response"
    WORKFLOW_START = "workflow_start"
    WORKFLOW_STEP = "workflow_step"
    WORKFLOW_COMPLETE = "workflow_complete"
    
    # Status and health messages
    STATUS_UPDATE = "status_update"
    HEALTH_CHECK = "health_check"
    CAPABILITY_QUERY = "capability_query"
    CAPABILITY_RESPONSE = "capability_response"
    
    # Data and resource messages
    DATA_REQUEST = "data_request"
    DATA_RESPONSE = "data_response"
    RESOURCE_REQUEST = "resource_request"
    RESOURCE_RESPONSE = "resource_response"
    
    # Error and exception messages
    ERROR_NOTIFICATION = "error_notification"
    EXCEPTION_REPORT = "exception_report"
    
    # System messages
    SYSTEM_SHUTDOWN = "system_shutdown"
    AGENT_REGISTRATION = "agent_registration"
    AGENT_DEREGISTRATION = "agent_deregistration"


class MessagePriority(str, Enum):
    """Priority levels for messages."""
    
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class Message(BaseModel):
    """Standard message format for inter-agent communication."""
    
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    sender_id: str
    recipient_id: Optional[str] = None  # None for broadcast messages
    message_type: MessageType
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None  # For tracking related messages
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class MessageHandler:
    """Base class for message handlers."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.logger = structlog.get_logger(f"{self.__class__.__name__}:{agent_id}")
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """
        Handle an incoming message.
        
        Args:
            message: The message to handle
            
        Returns:
            Optional response message
        """
        raise NotImplementedError("Subclasses must implement handle_message")


class CommunicationManager:
    """
    Manages communication between agents in the system.
    
    This class provides:
    - Message routing and delivery
    - Event subscription and publishing
    - Message queuing and prioritization
    - Broadcast and targeted messaging
    """
    
    def __init__(self):
        self.logger = structlog.get_logger(self.__class__.__name__)
        self.agents: Dict[str, MessageHandler] = {}
        self.message_queues: Dict[str, asyncio.Queue] = {}
        self.subscriptions: Dict[str, Set[str]] = {}  # event_type -> set of agent_ids
        self.running = False
        self._message_handlers: Dict[MessageType, List[Callable]] = {}
        
    async def start(self):
        """Start the communication manager."""
        self.logger.info("Starting communication manager")
        self.running = True
        
        # Start message processing tasks for each agent
        for agent_id in self.agents:
            await self._start_agent_message_processor(agent_id)
    
    async def stop(self):
        """Stop the communication manager."""
        self.logger.info("Stopping communication manager")
        self.running = False
        
        # Stop all message processors
        for agent_id in list(self.agents.keys()):
            await self._stop_agent_message_processor(agent_id)
    
    async def register_agent(self, agent_id: str, handler: MessageHandler):
        """
        Register an agent with the communication manager.
        
        Args:
            agent_id: Unique identifier for the agent
            handler: Message handler for the agent
        """
        if agent_id in self.agents:
            raise AgentCommunicationError(f"Agent {agent_id} is already registered")
        
        self.agents[agent_id] = handler
        self.message_queues[agent_id] = asyncio.Queue()
        
        # Start message processor for this agent
        await self._start_agent_message_processor(agent_id)
        
        self.logger.info("Agent registered", agent_id=agent_id)
    
    async def unregister_agent(self, agent_id: str):
        """
        Unregister an agent from the communication manager.
        
        Args:
            agent_id: ID of the agent to unregister
        """
        if agent_id not in self.agents:
            return
        
        # Stop message processor
        await self._stop_agent_message_processor(agent_id)
        
        # Remove agent
        del self.agents[agent_id]
        del self.message_queues[agent_id]
        
        # Remove from subscriptions
        for event_type in list(self.subscriptions.keys()):
            self.subscriptions[event_type].discard(agent_id)
            if not self.subscriptions[event_type]:
                del self.subscriptions[event_type]
        
        self.logger.info("Agent unregistered", agent_id=agent_id)
    
    async def send_message(self, message: Message) -> bool:
        """
        Send a message to a specific agent or broadcast.
        
        Args:
            message: The message to send
            
        Returns:
            True if message was queued successfully
        """
        try:
            if message.recipient_id:
                # Direct message
                if message.recipient_id not in self.agents:
                    self.logger.warning(
                        "Recipient not found",
                        recipient_id=message.recipient_id,
                        message_id=message.message_id
                    )
                    return False
                
                await self.message_queues[message.recipient_id].put(message)
                self.logger.debug(
                    "Message queued for delivery",
                    message_id=message.message_id,
                    recipient_id=message.recipient_id
                )
            else:
                # Broadcast message
                for agent_id in self.agents:
                    broadcast_message = message.copy()
                    broadcast_message.recipient_id = agent_id
                    await self.message_queues[agent_id].put(broadcast_message)
                
                self.logger.debug(
                    "Broadcast message queued",
                    message_id=message.message_id,
                    recipient_count=len(self.agents)
                )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "Failed to send message",
                message_id=message.message_id,
                error=str(e)
            )
            return False
    
    async def publish_event(self, event_type: str, data: Dict[str, Any], sender_id: str):
        """
        Publish an event to all subscribed agents.
        
        Args:
            event_type: Type of event
            data: Event data
            sender_id: ID of the agent publishing the event
        """
        if event_type not in self.subscriptions:
            return
        
        message = Message(
            sender_id=sender_id,
            message_type=MessageType.STATUS_UPDATE,
            payload={"event_type": event_type, "data": data},
            metadata={"is_event": True}
        )
        
        # Send to all subscribed agents
        for agent_id in self.subscriptions[event_type]:
            if agent_id != sender_id:  # Don't send to self
                event_message = message.copy()
                event_message.recipient_id = agent_id
                await self.message_queues[agent_id].put(event_message)
        
        self.logger.debug(
            "Event published",
            event_type=event_type,
            subscriber_count=len(self.subscriptions[event_type])
        )
    
    async def subscribe_to_event(self, agent_id: str, event_type: str):
        """
        Subscribe an agent to a specific event type.
        
        Args:
            agent_id: ID of the agent subscribing
            event_type: Type of event to subscribe to
        """
        if event_type not in self.subscriptions:
            self.subscriptions[event_type] = set()
        
        self.subscriptions[event_type].add(agent_id)
        self.logger.debug(
            "Agent subscribed to event",
            agent_id=agent_id,
            event_type=event_type
        )
    
    async def unsubscribe_from_event(self, agent_id: str, event_type: str):
        """
        Unsubscribe an agent from a specific event type.
        
        Args:
            agent_id: ID of the agent unsubscribing
            event_type: Type of event to unsubscribe from
        """
        if event_type in self.subscriptions:
            self.subscriptions[event_type].discard(agent_id)
            
            # Clean up empty subscriptions
            if not self.subscriptions[event_type]:
                del self.subscriptions[event_type]
            
            self.logger.debug(
                "Agent unsubscribed from event",
                agent_id=agent_id,
                event_type=event_type
            )
    
    async def _start_agent_message_processor(self, agent_id: str):
        """Start the message processing task for a specific agent."""
        if agent_id not in self.agents:
            return
        
        # Create and start the message processor task
        task = asyncio.create_task(self._process_agent_messages(agent_id))
        self.message_queues[agent_id]._processor_task = task
        
        self.logger.debug("Message processor started", agent_id=agent_id)
    
    async def _stop_agent_message_processor(self, agent_id: str):
        """Stop the message processing task for a specific agent."""
        if agent_id not in self.message_queues:
            return
        
        queue = self.message_queues[agent_id]
        if hasattr(queue, '_processor_task'):
            queue._processor_task.cancel()
            try:
                await queue._processor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.debug("Message processor stopped", agent_id=agent_id)
    
    async def _process_agent_messages(self, agent_id: str):
        """Process messages for a specific agent."""
        if agent_id not in self.agents:
            return
        
        handler = self.agents[agent_id]
        queue = self.message_queues[agent_id]
        
        while self.running:
            try:
                # Wait for message with timeout
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Process message
                try:
                    response = await handler.handle_message(message)
                    if response:
                        await self.send_message(response)
                except Exception as e:
                    self.logger.error(
                        "Error processing message",
                        agent_id=agent_id,
                        message_id=message.message_id,
                        error=str(e)
                    )
                
                # Mark task as done
                queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(
                    "Unexpected error in message processor",
                    agent_id=agent_id,
                    error=str(e)
                )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the current status of the communication system."""
        return {
            "running": self.running,
            "registered_agents": list(self.agents.keys()),
            "active_subscriptions": {
                event_type: list(agent_ids)
                for event_type, agent_ids in self.subscriptions.items()
            },
            "queue_sizes": {
                agent_id: queue.qsize()
                for agent_id, queue in self.message_queues.items()
            }
        }
