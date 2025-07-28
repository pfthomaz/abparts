# backend/app/cache.py

import json
import hashlib
import logging
from typing import Any, Optional, Dict, Union
from datetime import datetime, timedelta
from functools import wraps

from .database import redis_client

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Redis-based caching manager for warehouse analytics and other data.
    Provides caching with TTL, cache invalidation, and performance monitoring.
    """
    
    def __init__(self):
        self.redis_client = redis_client
        self.default_ttl = 900  # 15 minutes default TTL
        self.analytics_prefix = "analytics:"
        self.trends_prefix = "trends:"
        
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate a consistent cache key from parameters."""
        # Sort kwargs to ensure consistent key generation
        sorted_params = sorted(kwargs.items())
        param_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        # Create hash for long parameter strings
        if len(param_string) > 100:
            param_hash = hashlib.md5(param_string.encode()).hexdigest()
            return f"{prefix}{param_hash}"
        
        return f"{prefix}{param_string}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached data by key."""
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error retrieving cache key {key}: {e}")
            return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """Set cached data with TTL."""
        try:
            ttl = ttl or self.default_ttl
            serialized_data = json.dumps(data, default=str)  # default=str handles datetime objects
            self.redis_client.setex(key, ttl, serialized_data)
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cached data by key."""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error deleting cache pattern {pattern}: {e}")
            return 0
    
    def get_warehouse_analytics_key(self, warehouse_id: str, start_date: str = None, 
                                  end_date: str = None, days: int = 30) -> str:
        """Generate cache key for warehouse analytics."""
        return self._generate_cache_key(
            self.analytics_prefix,
            warehouse_id=warehouse_id,
            start_date=start_date or "none",
            end_date=end_date or "none",
            days=days
        )
    
    def get_warehouse_trends_key(self, warehouse_id: str, period: str = "daily", 
                               days: int = 30) -> str:
        """Generate cache key for warehouse trends."""
        return self._generate_cache_key(
            self.trends_prefix,
            warehouse_id=warehouse_id,
            period=period,
            days=days
        )
    
    def invalidate_warehouse_cache(self, warehouse_id: str) -> int:
        """Invalidate all cached data for a specific warehouse."""
        analytics_pattern = f"{self.analytics_prefix}*warehouse_id={warehouse_id}*"
        trends_pattern = f"{self.trends_prefix}*warehouse_id={warehouse_id}*"
        
        deleted_count = 0
        deleted_count += self.delete_pattern(analytics_pattern)
        deleted_count += self.delete_pattern(trends_pattern)
        
        logger.info(f"Invalidated {deleted_count} cache entries for warehouse {warehouse_id}")
        return deleted_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            info = self.redis_client.info()
            analytics_keys = len(self.redis_client.keys(f"{self.analytics_prefix}*"))
            trends_keys = len(self.redis_client.keys(f"{self.trends_prefix}*"))
            
            return {
                "redis_memory_used": info.get("used_memory_human", "unknown"),
                "redis_connected_clients": info.get("connected_clients", 0),
                "analytics_cache_entries": analytics_keys,
                "trends_cache_entries": trends_keys,
                "total_keys": info.get("db0", {}).get("keys", 0) if "db0" in info else 0
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}


# Global cache manager instance
cache_manager = CacheManager()


def cached_analytics(ttl: int = 900):
    """
    Decorator for caching warehouse analytics functions.
    
    Args:
        ttl: Time to live in seconds (default: 15 minutes)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract warehouse_id and other parameters for cache key
            warehouse_id = None
            if args and hasattr(args[1], '__str__'):  # args[0] is db, args[1] should be warehouse_id
                warehouse_id = str(args[1])
            elif 'warehouse_id' in kwargs:
                warehouse_id = str(kwargs['warehouse_id'])
            
            if not warehouse_id:
                # If we can't determine warehouse_id, don't cache
                return func(*args, **kwargs)
            
            # Generate cache key based on function name and parameters
            if func.__name__ == 'get_warehouse_analytics':
                start_date = kwargs.get('start_date')
                end_date = kwargs.get('end_date')
                days = kwargs.get('days', 30)
                cache_key = cache_manager.get_warehouse_analytics_key(
                    warehouse_id,
                    start_date.isoformat() if start_date else None,
                    end_date.isoformat() if end_date else None,
                    days
                )
            elif func.__name__ == 'get_warehouse_analytics_trends':
                period = kwargs.get('period', 'daily')
                days = kwargs.get('days', 30)
                cache_key = cache_manager.get_warehouse_trends_key(
                    warehouse_id, period, days
                )
            else:
                # Generic cache key for other functions
                cache_key = cache_manager._generate_cache_key(
                    f"{func.__name__}:",
                    warehouse_id=warehouse_id,
                    **{k: str(v) for k, v in kwargs.items() if k != 'db'}
                )
            
            # Try to get from cache first
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__} with key {cache_key}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__} with key {cache_key}")
            result = func(*args, **kwargs)
            
            # Cache the result
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_warehouse_analytics_cache(warehouse_id: str):
    """
    Invalidate all cached analytics data for a warehouse.
    Should be called when inventory data changes.
    """
    return cache_manager.invalidate_warehouse_cache(warehouse_id)


def get_analytics_cache_stats() -> Dict[str, Any]:
    """Get analytics cache statistics."""
    return cache_manager.get_cache_stats()