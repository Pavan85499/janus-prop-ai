"""
WebSocket manager for real-time communication in Janus Prop AI Backend

This module handles WebSocket connections, real-time updates, and client management.
"""

import asyncio
import json
import uuid
from typing import Dict, Set, Any, Optional, Callable
from datetime import datetime

import structlog
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from config.settings import get_settings

logger = structlog.get_logger()

class ConnectionManager:
    """Manages WebSocket connections and broadcasts messages."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.subscriptions: Dict[str, Set[str]] = {}  # channel -> connection_ids
        
    async def connect(self, websocket: WebSocket, connection_id: str, metadata: Dict[str, Any] = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = metadata or {}
        logger.info("WebSocket connected", connection_id=connection_id, metadata=metadata)
        
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if connection_id in self.connection_metadata:
            del self.connection_metadata[connection_id]
        
        # Remove from all subscriptions
        for channel, connections in self.subscriptions.items():
            if connection_id in connections:
                connections.remove(connection_id)
        
        logger.info("WebSocket disconnected", connection_id=connection_id)
        
    async def send_personal_message(self, message: Dict[str, Any], connection_id: str):
        """Send a message to a specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error("Failed to send personal message", connection_id=connection_id, error=str(e))
                    self.disconnect(connection_id)
                    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all active connections."""
        disconnected = []
        
        for connection_id, websocket in self.active_connections.items():
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error("Failed to broadcast message", connection_id=connection_id, error=str(e))
                    disconnected.append(connection_id)
            else:
                disconnected.append(connection_id)
                
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
            
    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        """Broadcast a message to all connections subscribed to a specific channel."""
        if channel not in self.subscriptions:
            return
            
        disconnected = []
        
        for connection_id in self.subscriptions[channel]:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                if websocket.client_state == WebSocketState.CONNECTED:
                    try:
                        await websocket.send_text(json.dumps(message))
                    except Exception as e:
                        logger.error("Failed to broadcast to channel", channel=channel, connection_id=connection_id, error=str(e))
                        disconnected.append(connection_id)
                else:
                    disconnected.append(connection_id)
                    
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
            
    def subscribe(self, connection_id: str, channel: str):
        """Subscribe a connection to a channel."""
        if channel not in self.subscriptions:
            self.subscriptions[channel] = set()
        self.subscriptions[channel].add(connection_id)
        logger.info("Connection subscribed to channel", connection_id=connection_id, channel=channel)
        
    def unsubscribe(self, connection_id: str, channel: str):
        """Unsubscribe a connection from a channel."""
        if channel in self.subscriptions and connection_id in self.subscriptions[channel]:
            self.subscriptions[channel].remove(connection_id)
            logger.info("Connection unsubscribed from channel", connection_id=connection_id, channel=channel)

class WebSocketManager:
    """Main WebSocket manager for the application."""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.heartbeat_interval = get_settings().WEBSOCKET_HEARTBEAT_INTERVAL
        self.running = False
        self.heartbeat_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the WebSocket manager."""
        self.running = True
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("WebSocket manager started")
        
    async def stop(self):
        """Stop the WebSocket manager."""
        self.running = False
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
                
        # Close all connections
        for connection_id in list(self.connection_manager.active_connections.keys()):
            self.connection_manager.disconnect(connection_id)
            
        logger.info("WebSocket manager stopped")
        
    async def _heartbeat_loop(self):
        """Send heartbeat messages to all connections."""
        while self.running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                await self._send_heartbeat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Heartbeat error", error=str(e))
                
    async def _send_heartbeat(self):
        """Send heartbeat to all connections."""
        heartbeat_message = {
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.connection_manager.broadcast(heartbeat_message)
        
    async def handle_websocket(self, websocket: WebSocket, client_id: str = None):
        """Handle a WebSocket connection."""
        connection_id = client_id or str(uuid.uuid4())
        
        try:
            await self.connection_manager.connect(websocket, connection_id)
            
            # Send welcome message
            welcome_message = {
                "type": "welcome",
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Connected to Janus Prop AI Backend"
            }
            await self.connection_manager.send_personal_message(welcome_message, connection_id)
            
            # Keep connection alive
            while True:
                try:
                    # Wait for messages from client
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # Handle different message types
                    if message.get("type") == "subscribe":
                        channel = message.get("channel")
                        if channel:
                            self.connection_manager.subscribe(connection_id, channel)
                            await self.connection_manager.send_personal_message({
                                "type": "subscribed",
                                "channel": channel
                            }, connection_id)
                            
                    elif message.get("type") == "unsubscribe":
                        channel = message.get("channel")
                        if channel:
                            self.connection_manager.unsubscribe(connection_id, channel)
                            await self.connection_manager.send_personal_message({
                                "type": "unsubscribed",
                                "channel": channel
                            }, connection_id)
                            
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error("WebSocket message handling error", error=str(e))
                    break
                    
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected", connection_id=connection_id)
        except Exception as e:
            logger.error("WebSocket error", connection_id=connection_id, error=str(e))
        finally:
            self.connection_manager.disconnect(connection_id)
            
    async def send_agent_update(self, agent_id: str, update: Dict[str, Any]):
        """Send agent update to subscribed clients."""
        message = {
            "type": "agent_update",
            "agent_id": agent_id,
            "data": update,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.connection_manager.broadcast_to_channel(f"agent:{agent_id}", message)
        
    async def send_property_update(self, property_id: str, update: Dict[str, Any]):
        """Send property update to subscribed clients."""
        message = {
            "type": "property_update",
            "property_id": property_id,
            "data": update,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.connection_manager.broadcast_to_channel(f"property:{property_id}", message)
        
    async def send_lead_update(self, lead_id: str, update: Dict[str, Any]):
        """Send lead update to subscribed clients."""
        message = {
            "type": "lead_update",
            "lead_id": lead_id,
            "data": update,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.connection_manager.broadcast_to_channel(f"lead:{lead_id}", message)
        
    async def send_market_update(self, location: str, update: Dict[str, Any]):
        """Send market update to subscribed clients."""
        message = {
            "type": "market_update",
            "location": location,
            "data": update,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.connection_manager.broadcast_to_channel(f"market:{location}", message)
            
    async def _handle_message(self, connection_id: str, data: str):
        """Handle incoming WebSocket messages."""
        try:
            message = json.loads(data)
            message_type = message.get("type")
            
            if message_type == "subscribe":
                channel = message.get("channel")
                if channel:
                    self.connection_manager.subscribe(connection_id, channel)
                    response = {
                        "type": "subscribed",
                        "channel": channel,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await self.connection_manager.send_personal_message(response, connection_id)
                    
            elif message_type == "unsubscribe":
                channel = message.get("channel")
                if channel:
                    self.connection_manager.unsubscribe(connection_id, channel)
                    response = {
                        "type": "unsubscribed",
                        "channel": channel,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await self.connection_manager.send_personal_message(response, connection_id)
                    
            elif message_type == "ping":
                response = {
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await self.connection_manager.send_personal_message(response, connection_id)
                
            else:
                logger.warning("Unknown message type", connection_id=connection_id, message_type=message_type)
                
        except json.JSONDecodeError:
            logger.warning("Invalid JSON message", connection_id=connection_id, data=data)
            
    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.connection_manager.active_connections)
        
    def get_subscription_count(self, channel: str) -> int:
        """Get the number of connections subscribed to a channel."""
        return len(self.connection_manager.subscriptions.get(channel, set()))

# Global WebSocket manager instance
websocket_manager: Optional[WebSocketManager] = None

def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance."""
    if websocket_manager is None:
        raise RuntimeError("WebSocket manager not initialized")
    return websocket_manager

__all__ = [
    "WebSocketManager",
    "ConnectionManager",
    "get_websocket_manager"
]
