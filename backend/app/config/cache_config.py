"""
Cache configuration settings for the financial dashboard API.

This module contains all cache-related configuration parameters
that can be adjusted based on environment and performance requirements.
"""

import os
from typing import Dict, Any


class CacheConfig:
    """Cache configuration class with environment-based settings."""
    
    # Data cache settings (for raw data files)
    DATA_CACHE_SIZE = int(os.getenv('DATA_CACHE_SIZE', '10'))
    DATA_CACHE_TTL = int(os.getenv('DATA_CACHE_TTL', '3600'))  # 1 hour
    
    # Query cache settings (for API query results)
    QUERY_CACHE_SIZE = int(os.getenv('QUERY_CACHE_SIZE', '500'))
    QUERY_CACHE_TTL = int(os.getenv('QUERY_CACHE_TTL', '1800'))  # 30 minutes
    
    # Aggregation cache settings (for expensive computations)
    AGGREGATION_CACHE_SIZE = int(os.getenv('AGGREGATION_CACHE_SIZE', '200'))
    AGGREGATION_CACHE_TTL = int(os.getenv('AGGREGATION_CACHE_TTL', '3600'))  # 1 hour
    
    # Performance monitoring settings
    PERFORMANCE_HISTORY_SIZE = int(os.getenv('PERFORMANCE_HISTORY_SIZE', '1000'))
    SLOW_REQUEST_THRESHOLD = float(os.getenv('SLOW_REQUEST_THRESHOLD', '2.0'))  # seconds
    
    # Cache warming settings
    ENABLE_CACHE_WARMING = os.getenv('ENABLE_CACHE_WARMING', 'true').lower() == 'true'
    CACHE_WARMING_ENDPOINTS = [
        '/api/properties',
        '/api/revenue/timeline',
        '/api/revenue/by-property',
        '/api/kpis'
    ]
    
    # Environment-specific optimizations
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """Get complete cache configuration as dictionary."""
        return {
            'data_cache': {
                'max_size': cls.DATA_CACHE_SIZE,
                'default_ttl': cls.DATA_CACHE_TTL
            },
            'query_cache': {
                'max_size': cls.QUERY_CACHE_SIZE,
                'default_ttl': cls.QUERY_CACHE_TTL
            },
            'aggregation_cache': {
                'max_size': cls.AGGREGATION_CACHE_SIZE,
                'default_ttl': cls.AGGREGATION_CACHE_TTL
            },
            'performance': {
                'history_size': cls.PERFORMANCE_HISTORY_SIZE,
                'slow_request_threshold': cls.SLOW_REQUEST_THRESHOLD
            },
            'cache_warming': {
                'enabled': cls.ENABLE_CACHE_WARMING,
                'endpoints': cls.CACHE_WARMING_ENDPOINTS
            },
            'environment': cls.ENVIRONMENT
        }
    
    @classmethod
    def get_production_config(cls) -> Dict[str, Any]:
        """Get optimized configuration for production environment."""
        return {
            'data_cache': {
                'max_size': 20,  # More data cache in production
                'default_ttl': 7200  # 2 hours
            },
            'query_cache': {
                'max_size': 1000,  # Larger query cache
                'default_ttl': 3600  # 1 hour
            },
            'aggregation_cache': {
                'max_size': 500,  # More aggregation cache
                'default_ttl': 7200  # 2 hours
            }
        }
    
    @classmethod
    def get_development_config(cls) -> Dict[str, Any]:
        """Get configuration optimized for development environment."""
        return {
            'data_cache': {
                'max_size': 5,  # Smaller cache for development
                'default_ttl': 1800  # 30 minutes
            },
            'query_cache': {
                'max_size': 100,  # Smaller query cache
                'default_ttl': 900  # 15 minutes
            },
            'aggregation_cache': {
                'max_size': 50,  # Smaller aggregation cache
                'default_ttl': 1800  # 30 minutes
            }
        }


# Environment-specific cache recommendations
CACHE_RECOMMENDATIONS = {
    'production': [
        "Use longer TTL values for stable data",
        "Enable cache warming for critical endpoints",
        "Monitor cache hit rates and adjust sizes accordingly",
        "Consider Redis for distributed caching if scaling horizontally"
    ],
    'development': [
        "Use shorter TTL values for faster development cycles",
        "Clear cache frequently when testing data changes",
        "Monitor performance impact of caching",
        "Test cache invalidation scenarios"
    ],
    'testing': [
        "Use minimal cache sizes to avoid test interference",
        "Clear cache between test runs",
        "Test both cached and uncached scenarios",
        "Verify cache invalidation works correctly"
    ]
}


def get_environment_recommendations() -> list:
    """Get cache recommendations for current environment."""
    env = CacheConfig.ENVIRONMENT.lower()
    return CACHE_RECOMMENDATIONS.get(env, CACHE_RECOMMENDATIONS['development'])