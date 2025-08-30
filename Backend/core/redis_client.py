"""
Redis client for Janus Prop AI Backend

This module handles Redis connections, caching, and real-time data publishing.
"""

import json
import asyncio
from typing import Any, Optional, Dict
from contextlib import asynccontextmanager

import structlog
from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import RedisError

from config.settings import get_settings

logger = structlog.get_logger()

# Global Redis client
_redis_client: Optional[Redis] = None
_pool: Optional[ConnectionPool] = None

async def init_redis() -> None:
    """Initialize Redis connection."""
    global _redis_client, _pool
    
    settings = get_settings()
    
    try:
        # Check if Redis URL is the default localhost
        if settings.REDIS_URL == "redis://localhost:6379/0":
            logger.warning("Redis not configured. Skipping Redis initialization.")
            logger.info("Backend will run without Redis caching and real-time features.")
            return
        
        # Create connection pool
        _pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={},
            decode_responses=True
        )
        
        # Create Redis client
        _redis_client = Redis(connection_pool=_pool)
        
        # Test connection
        await _redis_client.ping()
        
        logger.info("Redis initialized successfully", url=settings.REDIS_URL)
        
    except Exception as e:
        logger.error("Failed to initialize Redis", error=str(e))
        logger.warning("Redis initialization failed. Backend will run without Redis functionality.")
        # Don't raise the error, just log it and continue
        return

async def close_redis() -> None:
    """Close Redis connections."""
    global _redis_client, _pool
    
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        
    if _pool:
        await _pool.disconnect()
        _pool = None
        
    logger.info("Redis connections closed")

def get_redis_client() -> Optional[Redis]:
    """Get the Redis client instance."""
    return _redis_client

# Caching utilities
async def cache_get(key: str) -> Optional[Any]:
    """Get a value from cache."""
    try:
        client = get_redis_client()
        if client is None:
            return None  # Redis not available
        
        value = await client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.warning("Failed to get from cache", key=key, error=str(e))
        return None

async def cache_set(key: str, value: Any, expire: int = 3600) -> bool:
    """Set a value in cache with expiration."""
    try:
        client = get_redis_client()
        if client is None:
            return False  # Redis not available
        
        serialized = json.dumps(value)
        await client.setex(key, expire, serialized)
        return True
    except Exception as e:
        logger.warning("Failed to set cache", key=key, error=str(e))
        return False

async def cache_delete(key: str) -> bool:
    """Delete a key from cache."""
    try:
        client = get_redis_client()
        if client is None:
            return False  # Redis not available
        
        await client.delete(key)
        return True
    except Exception as e:
        logger.warning("Failed to delete from cache", key=key, error=str(e))
        return False

async def cache_exists(key: str) -> bool:
    """Check if a key exists in cache."""
    try:
        client = get_redis_client()
        return await client.exists(key) > 0
    except Exception as e:
        logger.warning("Failed to check cache existence", key=key, error=str(e))
        return False

# Real-time data utilities
async def publish_event(channel: str, event: str, data: Any) -> bool:
    """Publish an event to a Redis channel."""
    try:
        client = get_redis_client()
        message = {
            "event": event,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await client.publish(channel, json.dumps(message))
        return True
    except Exception as e:
        logger.error("Failed to publish event", channel=channel, error=str(e))
        return False

async def subscribe_to_channel(channel: str) -> Any:
    """Subscribe to a Redis channel for real-time updates."""
    try:
        client = get_redis_client()
        pubsub = client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub
    except Exception as e:
        logger.error("Failed to subscribe to channel", channel=channel, error=str(e))
        raise

# Agent activity caching
async def cache_agent_activity(agent_id: str, activity: Dict[str, Any]) -> bool:
    """Cache agent activity for real-time updates."""
    key = f"agent_activity:{agent_id}"
    return await cache_set(key, activity, expire=300)  # 5 minutes

async def get_agent_activity(agent_id: str) -> Optional[Dict[str, Any]]:
    """Get cached agent activity."""
    key = f"agent_activity:{agent_id}"
    return await cache_get(key)

async def cache_agent_status(agent_id: str, status: Dict[str, Any]) -> bool:
    """Cache agent status."""
    key = f"agent_status:{agent_id}"
    return await cache_set(key, status, expire=60)  # 1 minute

async def get_agent_status(agent_id: str) -> Optional[Dict[str, Any]]:
    """Get cached agent status."""
    key = f"agent_status:{agent_id}"
    return await cache_get(key)

# Property data caching
async def cache_property_data(property_id: str, data: Dict[str, Any]) -> bool:
    """Cache property data."""
    key = f"property:{property_id}"
    return await cache_set(key, data, expire=1800)  # 30 minutes

async def get_property_data(property_id: str) -> Optional[Dict[str, Any]]:
    """Get cached property data."""
    key = f"property:{property_id}"
    return await cache_get(key)

# Market data caching
async def cache_market_data(location: str, data: Dict[str, Any]) -> bool:
    """Cache market data for a location."""
    key = f"market_data:{location}"
    return await cache_set(key, data, expire=3600)  # 1 hour

async def get_market_data(location: str) -> Optional[Dict[str, Any]]:
    """Get cached market data."""
    key = f"market_data:{location}"
    return await cache_get(key)

# Health check
async def health_check() -> bool:
    """Check Redis health."""
    try:
        if _redis_client is None:
            return False  # Redis not configured
        
        await _redis_client.ping()
        return True
    except Exception as e:
        logger.warning("Redis health check failed", error=str(e))
        return False

# Rate limiting
async def check_rate_limit(key: str, limit: int, window: int = 60) -> bool:
    """Check if a rate limit has been exceeded."""
    try:
        client = get_redis_client()
        current = await client.get(key)
        
        if current is None:
            await client.setex(key, window, 1)
            return True
        
        count = int(current)
        if count >= limit:
            return False
        
        await client.incr(key)
        return True
        
    except Exception as e:
        logger.warning("Rate limit check failed", key=key, error=str(e))
        return True  # Allow on error

__all__ = [
    "init_redis",
    "close_redis",
    "get_redis_client",
    "cache_get",
    "cache_set",
    "cache_delete",
    "cache_exists",
    "publish_event",
    "subscribe_to_channel",
    "cache_agent_activity",
    "get_agent_activity",
    "cache_agent_status",
    "get_agent_status",
    "cache_property_data",
    "get_property_data",
    "cache_market_data",
    "get_market_data",
    "health_check",
    "check_rate_limit"
]
