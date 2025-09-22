"""
Performance monitoring middleware for the financial dashboard API.

This middleware tracks request performance, cache hit rates, and provides
insights for optimization.
"""

import time
import logging
from typing import Dict, List
from collections import defaultdict, deque
from datetime import datetime, timedelta
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Thread-safe performance monitoring with rolling statistics."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.request_times = deque(maxlen=max_history)
        self.endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'recent_times': deque(maxlen=100)
        })
        self.slow_requests = deque(maxlen=50)  # Track slowest requests
        self.error_count = 0
        self.total_requests = 0
    
    def record_request(self, endpoint: str, duration: float, status_code: int, 
                      cache_hit: bool = False):
        """Record a request's performance metrics."""
        self.total_requests += 1
        self.request_times.append(duration)
        
        # Update endpoint-specific stats
        stats = self.endpoint_stats[endpoint]
        stats['count'] += 1
        stats['total_time'] += duration
        stats['min_time'] = min(stats['min_time'], duration)
        stats['max_time'] = max(stats['max_time'], duration)
        stats['recent_times'].append(duration)
        
        # Track slow requests (>2 seconds)
        if duration > 2.0:
            self.slow_requests.append({
                'endpoint': endpoint,
                'duration': duration,
                'timestamp': datetime.now().isoformat(),
                'status_code': status_code,
                'cache_hit': cache_hit
            })
        
        # Track errors
        if status_code >= 400:
            self.error_count += 1
    
    def get_stats(self) -> Dict:
        """Get comprehensive performance statistics."""
        if not self.request_times:
            return {'message': 'No requests recorded yet'}
        
        # Overall stats
        recent_times = list(self.request_times)
        avg_response_time = sum(recent_times) / len(recent_times)
        
        # Calculate percentiles
        sorted_times = sorted(recent_times)
        p50 = sorted_times[len(sorted_times) // 2]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99)]
        
        # Endpoint-specific stats
        endpoint_summary = {}
        for endpoint, stats in self.endpoint_stats.items():
            if stats['count'] > 0:
                recent_avg = sum(stats['recent_times']) / len(stats['recent_times']) if stats['recent_times'] else 0
                endpoint_summary[endpoint] = {
                    'request_count': stats['count'],
                    'avg_response_time': stats['total_time'] / stats['count'],
                    'recent_avg_response_time': recent_avg,
                    'min_response_time': stats['min_time'],
                    'max_response_time': stats['max_time']
                }
        
        return {
            'overall': {
                'total_requests': self.total_requests,
                'error_count': self.error_count,
                'error_rate': self.error_count / self.total_requests if self.total_requests > 0 else 0,
                'avg_response_time': avg_response_time,
                'p50_response_time': p50,
                'p95_response_time': p95,
                'p99_response_time': p99,
                'min_response_time': min(recent_times),
                'max_response_time': max(recent_times)
            },
            'endpoints': endpoint_summary,
            'slow_requests': list(self.slow_requests),
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        if not self.request_times:
            return recommendations
        
        # Check average response time
        avg_time = sum(self.request_times) / len(self.request_times)
        if avg_time > 1.0:
            recommendations.append("Average response time is high (>1s). Consider optimizing queries or adding more caching.")
        
        # Check for slow endpoints
        slow_endpoints = []
        for endpoint, stats in self.endpoint_stats.items():
            if stats['count'] > 0:
                avg_endpoint_time = stats['total_time'] / stats['count']
                if avg_endpoint_time > 2.0:
                    slow_endpoints.append(endpoint)
        
        if slow_endpoints:
            recommendations.append(f"Slow endpoints detected: {', '.join(slow_endpoints)}. Consider adding caching or optimization.")
        
        # Check error rate
        error_rate = self.error_count / self.total_requests if self.total_requests > 0 else 0
        if error_rate > 0.05:  # 5% error rate
            recommendations.append(f"High error rate detected ({error_rate:.2%}). Check logs for issues.")
        
        # Check for cache opportunities
        if len(self.slow_requests) > 10:
            recommendations.append("Multiple slow requests detected. Consider implementing more aggressive caching.")
        
        if not recommendations:
            recommendations.append("API performance is within acceptable ranges.")
        
        return recommendations


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to track API performance metrics."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip monitoring for health checks and static files
        if request.url.path in ['/health', '/docs', '/openapi.json']:
            return await call_next(request)
        
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Check if response came from cache (simplified check)
        cache_hit = response.headers.get('X-Cache-Status') == 'HIT'
        
        # Record metrics
        endpoint = f"{request.method} {request.url.path}"
        performance_monitor.record_request(
            endpoint=endpoint,
            duration=duration,
            status_code=response.status_code,
            cache_hit=cache_hit
        )
        
        # Add performance headers
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
        response.headers['X-Cache-Status'] = 'HIT' if cache_hit else 'MISS'
        
        # Log slow requests
        if duration > 2.0:
            logger.warning(f"Slow request: {endpoint} took {duration:.3f}s")
        
        return response


def get_performance_stats() -> Dict:
    """Get current performance statistics."""
    return performance_monitor.get_stats()


def reset_performance_stats():
    """Reset performance monitoring statistics."""
    global performance_monitor
    performance_monitor = PerformanceMonitor()
    logger.info("Performance statistics reset")