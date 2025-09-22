"""
Advanced caching manager for financial dashboard API.

This module provides multi-level caching including:
- Data-level caching (raw data)
- Query-level caching (computed results)
- Memory-efficient caching with TTL
- Cache invalidation strategies
"""

import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from functools import wraps
from pathlib import Path
import threading
from collections import OrderedDict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTLCache:
    """Thread-safe TTL (Time To Live) cache implementation."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = OrderedDict()
        self.timestamps = {}
        self.lock = threading.RLock()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired."""
        if key not in self.timestamps:
            return True
        
        expiry_time = self.timestamps[key]
        return datetime.now() > expiry_time
    
    def _evict_expired(self):
        """Remove expired entries."""
        current_time = datetime.now()
        expired_keys = [
            key for key, expiry_time in self.timestamps.items()
            if current_time > expiry_time
        ]
        
        for key in expired_keys:
            self.cache.pop(key, None)
            self.timestamps.pop(key, None)
    
    def _evict_lru(self):
        """Remove least recently used entries if cache is full."""
        while len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            self.cache.pop(oldest_key)
            self.timestamps.pop(oldest_key, None)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            if key not in self.cache or self._is_expired(key):
                return None
            
            # Move to end (mark as recently used)
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        with self.lock:
            # Clean up expired entries
            self._evict_expired()
            
            # Evict LRU if needed
            self._evict_lru()
            
            # Set new value
            self.cache[key] = value
            ttl_seconds = ttl or self.default_ttl
            self.timestamps[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def delete(self, key: str) -> bool:
        """Delete specific key from cache."""
        with self.lock:
            if key in self.cache:
                self.cache.pop(key)
                self.timestamps.pop(key, None)
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        with self.lock:
            self._evict_expired()
            return len(self.cache)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            self._evict_expired()
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hit_ratio': getattr(self, '_hits', 0) / max(getattr(self, '_requests', 1), 1)
            }


class CacheManager:
    """Main cache manager with multiple cache levels."""
    
    def __init__(self):
        # Data-level cache (raw data from files)
        self.data_cache = TTLCache(max_size=10, default_ttl=3600)  # 1 hour
        
        # Query-level cache (computed results)
        self.query_cache = TTLCache(max_size=500, default_ttl=1800)  # 30 minutes
        
        # Aggregation cache (expensive computations)
        self.aggregation_cache = TTLCache(max_size=200, default_ttl=3600)  # 1 hour
        
        # File modification times for cache invalidation
        self.file_mtimes = {}
        
        logger.info("CacheManager initialized with multi-level caching")
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a consistent cache key from arguments."""
        # Create a string representation of all arguments
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        
        # Create hash of the key data
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{prefix}:{key_hash}"
    
    def _check_file_modified(self, file_path: str) -> bool:
        """Check if file has been modified since last cache."""
        try:
            current_mtime = Path(file_path).stat().st_mtime
            last_mtime = self.file_mtimes.get(file_path, 0)
            
            if current_mtime > last_mtime:
                self.file_mtimes[file_path] = current_mtime
                return True
            return False
        except Exception as e:
            logger.warning(f"Could not check file modification time for {file_path}: {e}")
            return True  # Assume modified if we can't check
    
    def get_data(self, file_path: str, loader_func) -> Any:
        """Get data with file-based cache invalidation."""
        cache_key = f"data:{file_path}"
        
        # Check if file was modified
        if self._check_file_modified(file_path):
            logger.info(f"File {file_path} was modified, invalidating data cache")
            self.data_cache.delete(cache_key)
            # Also clear related query caches
            self.query_cache.clear()
            self.aggregation_cache.clear()
        
        # Try to get from cache
        cached_data = self.data_cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Data cache hit for {file_path}")
            return cached_data
        
        # Load data and cache it
        logger.info(f"Data cache miss for {file_path}, loading...")
        data = loader_func(file_path)
        self.data_cache.set(cache_key, data, ttl=3600)  # Cache for 1 hour
        
        return data
    
    def get_query_result(self, cache_key: str, compute_func, *args, **kwargs) -> Any:
        """Get query result with caching."""
        full_key = self._generate_cache_key(cache_key, *args, **kwargs)
        
        # Try to get from cache
        cached_result = self.query_cache.get(full_key)
        if cached_result is not None:
            logger.debug(f"Query cache hit for {cache_key}")
            return cached_result
        
        # Compute result and cache it
        logger.debug(f"Query cache miss for {cache_key}, computing...")
        result = compute_func(*args, **kwargs)
        self.query_cache.set(full_key, result, ttl=1800)  # Cache for 30 minutes
        
        return result
    
    def get_aggregation_result(self, cache_key: str, compute_func, *args, **kwargs) -> Any:
        """Get aggregation result with longer caching."""
        full_key = self._generate_cache_key(cache_key, *args, **kwargs)
        
        # Try to get from cache
        cached_result = self.aggregation_cache.get(full_key)
        if cached_result is not None:
            logger.debug(f"Aggregation cache hit for {cache_key}")
            return cached_result
        
        # Compute result and cache it
        logger.debug(f"Aggregation cache miss for {cache_key}, computing...")
        result = compute_func(*args, **kwargs)
        self.aggregation_cache.set(full_key, result, ttl=3600)  # Cache for 1 hour
        
        return result
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern."""
        invalidated = 0
        
        for cache in [self.data_cache, self.query_cache, self.aggregation_cache]:
            with cache.lock:
                keys_to_delete = [key for key in cache.cache.keys() if pattern in key]
                for key in keys_to_delete:
                    cache.delete(key)
                    invalidated += 1
        
        logger.info(f"Invalidated {invalidated} cache entries matching pattern: {pattern}")
        return invalidated
    
    def clear_all(self) -> None:
        """Clear all caches."""
        self.data_cache.clear()
        self.query_cache.clear()
        self.aggregation_cache.clear()
        logger.info("All caches cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        return {
            'data_cache': self.data_cache.stats(),
            'query_cache': self.query_cache.stats(),
            'aggregation_cache': self.aggregation_cache.stats(),
            'total_entries': (
                self.data_cache.size() + 
                self.query_cache.size() + 
                self.aggregation_cache.size()
            )
        }


# Global cache manager instance
cache_manager = CacheManager()


def cached_query(cache_key: str, ttl: Optional[int] = None):
    """Decorator for caching query results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return cache_manager.get_query_result(cache_key, func, *args, **kwargs)
        return wrapper
    return decorator


def cached_aggregation(cache_key: str, ttl: Optional[int] = None):
    """Decorator for caching expensive aggregation results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return cache_manager.get_aggregation_result(cache_key, func, *args, **kwargs)
        return wrapper
    return decorator


def invalidate_cache_on_data_change(file_path: str):
    """Decorator to invalidate caches when data changes."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if data file was modified
            if cache_manager._check_file_modified(file_path):
                cache_manager.clear_all()
            return func(*args, **kwargs)
        return wrapper
    return decorator