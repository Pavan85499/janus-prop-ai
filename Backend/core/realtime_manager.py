"""
Real-time manager for handling real-time data updates and synchronization in Janus Prop AI Backend

This module manages real-time data streams, updates, and synchronization across the system.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass

import structlog
from core.websocket_manager import WebSocketManager
from core.redis_client import publish_event, cache_set, cache_get
from config.settings import get_settings

logger = structlog.get_logger()

@dataclass
class DataUpdate:
    """Represents a data update event."""
    update_id: str
    data_type: str
    entity_id: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    priority: int = 1  # 1=low, 2=medium, 3=high, 4=critical

class RealtimeManager:
    """Manages real-time data updates and synchronization."""
    
    def __init__(self, websocket_manager: WebSocketManager):
        self.websocket_manager = websocket_manager
        self.settings = get_settings()
        self.running = False
        self.update_queue: asyncio.Queue[DataUpdate] = asyncio.Queue()
        self.update_handlers: Dict[str, List[Callable]] = {}
        self.sync_tasks: Dict[str, asyncio.Task] = {}
        self.running = False
        
    async def start(self):
        """Start the real-time manager."""
        self.running = True
        
        # Start update processing
        asyncio.create_task(self._process_updates())
        
        # Start data synchronization tasks
        await self._start_sync_tasks()
        
        logger.info("Real-time manager started")
        
    async def stop(self):
        """Stop the real-time manager."""
        self.running = False
        
        # Cancel all sync tasks
        for task in self.sync_tasks.values():
            task.cancel()
            
        # Wait for tasks to complete
        if self.sync_tasks:
            await asyncio.gather(*self.sync_tasks.values(), return_exceptions=True)
            
        logger.info("Real-time manager stopped")
        
    async def _start_sync_tasks(self):
        """Start data synchronization tasks."""
        # Property data sync
        self.sync_tasks["properties"] = asyncio.create_task(
            self._sync_property_data()
        )
        
        # Market data sync
        self.sync_tasks["market"] = asyncio.create_task(
            self._sync_market_data()
        )
        
        # Agent status sync
        self.sync_tasks["agents"] = asyncio.create_task(
            self._sync_agent_status()
        )
        
        # Lead data sync
        self.sync_tasks["leads"] = asyncio.create_task(
            self._sync_lead_data()
        )
        
    async def _process_updates(self):
        """Process queued data updates."""
        while self.running:
            try:
                # Get update from queue with timeout
                try:
                    update = await asyncio.wait_for(
                        self.update_queue.get(), 
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                    
                await self._handle_update(update)
                self.update_queue.task_done()
                
            except Exception as e:
                logger.error("Error processing update", error=str(e))
                
    async def _handle_update(self, update: DataUpdate):
        """Handle a single data update."""
        try:
            # Cache the update
            await cache_set(
                f"update:{update.update_id}",
                update.__dict__,
                expire=3600
            )
            
            # Publish to Redis
            await publish_event(
                f"updates:{update.data_type}",
                "data_update",
                update.__dict__
            )
            
            # Send via WebSocket
            await self._send_websocket_update(update)
            
            # Call registered handlers
            await self._call_update_handlers(update)
            
            logger.debug("Update processed", update_id=update.update_id, data_type=update.data_type)
            
        except Exception as e:
            logger.error("Error handling update", update_id=update.update_id, error=str(e))
            
    async def _send_websocket_update(self, update: DataUpdate):
        """Send update via WebSocket."""
        try:
            message = {
                "type": "data_update",
                "update_id": update.update_id,
                "data_type": update.data_type,
                "entity_id": update.entity_id,
                "data": update.data,
                "timestamp": update.timestamp.isoformat(),
                "source": update.source,
                "priority": update.priority
            }
            
            # Send to specific channel
            channel = f"{update.data_type}:{update.entity_id}"
            await self.websocket_manager.connection_manager.broadcast_to_channel(
                channel, message
            )
            
            # Send to general updates channel
            await self.websocket_manager.connection_manager.broadcast_to_channel(
                "updates", message
            )
            
        except Exception as e:
            logger.error("Error sending WebSocket update", error=str(e))
            
    async def _call_update_handlers(self, update: DataUpdate):
        """Call registered update handlers."""
        handlers = self.update_handlers.get(update.data_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(update)
                else:
                    handler(update)
            except Exception as e:
                logger.error("Error in update handler", handler=str(handler), error=str(e))
                
    def register_update_handler(self, data_type: str, handler: Callable):
        """Register a handler for a specific data type."""
        if data_type not in self.update_handlers:
            self.update_handlers[data_type] = []
        self.update_handlers[data_type].append(handler)
        logger.info("Update handler registered", data_type=data_type)
        
    def unregister_update_handler(self, data_type: str, handler: Callable):
        """Unregister a handler for a specific data type."""
        if data_type in self.update_handlers and handler in self.update_handlers[data_type]:
            self.update_handlers[data_type].remove(handler)
            logger.info("Update handler unregistered", data_type=data_type)
            
    async def queue_update(self, update: DataUpdate):
        """Queue a data update for processing."""
        await self.update_queue.put(update)
        
    async def queue_property_update(self, property_id: str, data: Dict[str, Any], source: str = "system"):
        """Queue a property update."""
        update = DataUpdate(
            update_id=f"prop_{property_id}_{int(datetime.utcnow().timestamp())}",
            data_type="property",
            entity_id=property_id,
            data=data,
            timestamp=datetime.utcnow(),
            source=source
        )
        await self.queue_update(update)
        
    async def queue_market_update(self, location: str, data: Dict[str, Any], source: str = "system"):
        """Queue a market update."""
        update = DataUpdate(
            update_id=f"market_{location}_{int(datetime.utcnow().timestamp())}",
            data_type="market",
            entity_id=location,
            data=data,
            timestamp=datetime.utcnow(),
            source=source
        )
        await self.queue_update(update)
        
    async def queue_agent_update(self, agent_id: str, data: Dict[str, Any], source: str = "system"):
        """Queue an agent update."""
        update = DataUpdate(
            update_id=f"agent_{agent_id}_{int(datetime.utcnow().timestamp())}",
            data_type="agent",
            entity_id=agent_id,
            data=data,
            timestamp=datetime.utcnow(),
            source=source
        )
        await self.queue_update(update)
        
    async def queue_lead_update(self, lead_id: str, data: Dict[str, Any], source: str = "system"):
        """Queue a lead update."""
        update = DataUpdate(
            update_id=f"lead_{lead_id}_{int(datetime.utcnow().timestamp())}",
            data_type="lead",
            entity_id=lead_id,
            data=data,
            timestamp=datetime.utcnow(),
            source=source
        )
        await self.queue_update(update)
        
    # Data synchronization methods
    async def _sync_property_data(self):
        """Synchronize property data from external sources."""
        while self.running:
            try:
                # This would integrate with real estate APIs
                # For now, we'll just wait
                await asyncio.sleep(self.settings.DATA_SYNC_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Property data sync error", error=str(e))
                await asyncio.sleep(60)  # Wait before retry
                
    async def _sync_market_data(self):
        """Synchronize market data from external sources."""
        while self.running:
            try:
                # This would integrate with market data APIs
                # For now, we'll just wait
                await asyncio.sleep(self.settings.DATA_SYNC_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Market data sync error", error=str(e))
                await asyncio.sleep(60)  # Wait before retry
                
    async def _sync_agent_status(self):
        """Synchronize agent status and health."""
        while self.running:
            try:
                # Check agent health and status
                # This would integrate with the agent manager
                await asyncio.sleep(self.settings.AGENT_HEALTH_CHECK_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Agent status sync error", error=str(e))
                await asyncio.sleep(30)  # Wait before retry
                
    async def _sync_lead_data(self):
        """Synchronize lead data from external sources."""
        while self.running:
            try:
                # This would integrate with CRM systems
                # For now, we'll just wait
                await asyncio.sleep(self.settings.DATA_SYNC_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Lead data sync error", error=str(e))
                await asyncio.sleep(60)  # Wait before retry
                
    # Utility methods
    def get_queue_size(self) -> int:
        """Get the current update queue size."""
        return self.update_queue.qsize()
        
    def get_active_sync_tasks(self) -> List[str]:
        """Get list of active synchronization tasks."""
        return [name for name, task in self.sync_tasks.items() if not task.done()]
        
    async def get_recent_updates(self, data_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent updates from cache."""
        # This would implement logic to retrieve recent updates
        # For now, return empty list
        return []

__all__ = ["RealtimeManager", "DataUpdate"]
