#!/usr/bin/env python3
"""
Cache monitoring utility for the Financial Dashboard API.

This script provides real-time monitoring of cache performance,
health checks, and optimization recommendations.
"""

import requests
import time
import json
import argparse
from datetime import datetime
from typing import Dict, Any
import sys


class CacheMonitor:
    """Monitor cache performance and health."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.last_stats = None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get current cache statistics."""
        try:
            response = requests.get(f"{self.base_url}/api/cache/stats")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        try:
            response = requests.get(f"{self.base_url}/api/performance/stats")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health."""
        try:
            response = requests.get(f"{self.base_url}/api/system/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def check_api_availability(self) -> bool:
        """Check if API is available."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def print_cache_stats(self, stats: Dict[str, Any]):
        """Print formatted cache statistics."""
        if "error" in stats:
            print(f"❌ Error getting cache stats: {stats['error']}")
            return
        
        data = stats.get("data", {})
        
        print("\n📊 CACHE STATISTICS")
        print("=" * 50)
        
        # Data cache
        data_cache = data.get("data_cache", {})
        print(f"📁 Data Cache:")
        print(f"   Size: {data_cache.get('size', 0)}/{data_cache.get('max_size', 0)}")
        print(f"   Hit Rate: {data_cache.get('hit_ratio', 0):.2%}")
        
        # Query cache
        query_cache = data.get("query_cache", {})
        print(f"🔍 Query Cache:")
        print(f"   Size: {query_cache.get('size', 0)}/{query_cache.get('max_size', 0)}")
        print(f"   Hit Rate: {query_cache.get('hit_ratio', 0):.2%}")
        
        # Aggregation cache
        agg_cache = data.get("aggregation_cache", {})
        print(f"🧮 Aggregation Cache:")
        print(f"   Size: {agg_cache.get('size', 0)}/{agg_cache.get('max_size', 0)}")
        print(f"   Hit Rate: {agg_cache.get('hit_ratio', 0):.2%}")
        
        # Total
        total_entries = data.get("total_entries", 0)
        print(f"\n📈 Total Cached Entries: {total_entries}")
    
    def print_performance_stats(self, stats: Dict[str, Any]):
        """Print formatted performance statistics."""
        if "error" in stats:
            print(f"❌ Error getting performance stats: {stats['error']}")
            return
        
        data = stats.get("data", {})
        overall = data.get("overall", {})
        
        if not overall:
            print("📊 No performance data available yet")
            return
        
        print("\n⚡ PERFORMANCE STATISTICS")
        print("=" * 50)
        
        print(f"📊 Overall Metrics:")
        print(f"   Total Requests: {overall.get('total_requests', 0):,}")
        print(f"   Error Rate: {overall.get('error_rate', 0):.2%}")
        print(f"   Avg Response Time: {overall.get('avg_response_time', 0):.3f}s")
        print(f"   P95 Response Time: {overall.get('p95_response_time', 0):.3f}s")
        print(f"   P99 Response Time: {overall.get('p99_response_time', 0):.3f}s")
        
        # Endpoint breakdown
        endpoints = data.get("endpoints", {})
        if endpoints:
            print(f"\n🎯 Top Endpoints:")
            sorted_endpoints = sorted(
                endpoints.items(), 
                key=lambda x: x[1].get('request_count', 0), 
                reverse=True
            )[:5]
            
            for endpoint, endpoint_stats in sorted_endpoints:
                print(f"   {endpoint}:")
                print(f"     Requests: {endpoint_stats.get('request_count', 0)}")
                print(f"     Avg Time: {endpoint_stats.get('avg_response_time', 0):.3f}s")
                print(f"     Recent Avg: {endpoint_stats.get('recent_avg_response_time', 0):.3f}s")
        
        # Recommendations
        recommendations = data.get("recommendations", [])
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                print(f"   • {rec}")
    
    def print_health_status(self, health: Dict[str, Any]):
        """Print system health status."""
        if "error" in health:
            print(f"❌ Error getting health status: {health['error']}")
            return
        
        status = health.get("status", "unknown")
        issues = health.get("issues", [])
        
        print(f"\n🏥 SYSTEM HEALTH")
        print("=" * 50)
        
        # Status indicator
        status_emoji = {
            "healthy": "✅",
            "warning": "⚠️",
            "degraded": "🔴"
        }.get(status, "❓")
        
        print(f"Status: {status_emoji} {status.upper()}")
        
        if issues:
            print(f"\n⚠️  Issues Detected:")
            for issue in issues:
                print(f"   • {issue}")
        else:
            print("✅ No issues detected")
    
    def monitor_continuous(self, interval: int = 30):
        """Monitor cache performance continuously."""
        print(f"🔄 Starting continuous monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                print(f"\n{'='*60}")
                print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Check API availability
                if not self.check_api_availability():
                    print("❌ API is not available!")
                    time.sleep(interval)
                    continue
                
                # Get and display stats
                cache_stats = self.get_cache_stats()
                self.print_cache_stats(cache_stats)
                
                perf_stats = self.get_performance_stats()
                self.print_performance_stats(perf_stats)
                
                health = self.get_system_health()
                self.print_health_status(health)
                
                # Calculate changes since last check
                if self.last_stats:
                    self.print_changes(cache_stats, self.last_stats)
                
                self.last_stats = cache_stats
                
                print(f"\n⏰ Next check in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
    
    def print_changes(self, current: Dict[str, Any], previous: Dict[str, Any]):
        """Print changes since last check."""
        try:
            current_data = current.get("data", {})
            previous_data = previous.get("data", {})
            
            current_total = current_data.get("total_entries", 0)
            previous_total = previous_data.get("total_entries", 0)
            
            if current_total != previous_total:
                change = current_total - previous_total
                print(f"\n📈 Cache Changes: {change:+d} entries")
        except:
            pass
    
    def run_health_check(self):
        """Run a comprehensive health check."""
        print("🏥 Running comprehensive health check...")
        
        # Check API availability
        if not self.check_api_availability():
            print("❌ API is not available!")
            return False
        
        # Get all stats
        cache_stats = self.get_cache_stats()
        perf_stats = self.get_performance_stats()
        health = self.get_system_health()
        
        # Display results
        self.print_cache_stats(cache_stats)
        self.print_performance_stats(perf_stats)
        self.print_health_status(health)
        
        # Overall assessment
        health_status = health.get("status", "unknown")
        if health_status == "healthy":
            print("\n✅ Overall Status: HEALTHY")
            return True
        elif health_status == "warning":
            print("\n⚠️  Overall Status: WARNING - Monitor closely")
            return True
        else:
            print("\n🔴 Overall Status: DEGRADED - Action required")
            return False
    
    def warm_cache(self):
        """Trigger cache warming."""
        print("🔥 Triggering cache warming...")
        
        try:
            response = requests.post(f"{self.base_url}/api/cache/warm")
            response.raise_for_status()
            result = response.json()
            
            print("✅ Cache warming initiated")
            print(f"Status: {result.get('status', 'unknown')}")
            
            if "results" in result:
                results = result["results"]
                if "duration" in results:
                    print(f"Duration: {results['duration']:.2f}s")
            
            return True
            
        except Exception as e:
            print(f"❌ Cache warming failed: {e}")
            return False
    
    def clear_cache(self):
        """Clear all caches."""
        print("🧹 Clearing all caches...")
        
        try:
            response = requests.post(f"{self.base_url}/api/cache/clear")
            response.raise_for_status()
            result = response.json()
            
            print("✅ All caches cleared")
            print(f"Status: {result.get('status', 'unknown')}")
            return True
            
        except Exception as e:
            print(f"❌ Cache clearing failed: {e}")
            return False


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Cache monitoring utility")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="API base URL (default: http://localhost:8000)")
    parser.add_argument("--monitor", action="store_true", 
                       help="Start continuous monitoring")
    parser.add_argument("--interval", type=int, default=30,
                       help="Monitoring interval in seconds (default: 30)")
    parser.add_argument("--health", action="store_true",
                       help="Run health check")
    parser.add_argument("--warm", action="store_true",
                       help="Trigger cache warming")
    parser.add_argument("--clear", action="store_true",
                       help="Clear all caches")
    
    args = parser.parse_args()
    
    monitor = CacheMonitor(args.url)
    
    # Check API availability first
    if not monitor.check_api_availability():
        print(f"❌ Cannot connect to API at {args.url}")
        print("Make sure the server is running with: python start_with_cache_test.py")
        sys.exit(1)
    
    if args.monitor:
        monitor.monitor_continuous(args.interval)
    elif args.health:
        success = monitor.run_health_check()
        sys.exit(0 if success else 1)
    elif args.warm:
        success = monitor.warm_cache()
        sys.exit(0 if success else 1)
    elif args.clear:
        success = monitor.clear_cache()
        sys.exit(0 if success else 1)
    else:
        # Default: run health check
        monitor.run_health_check()


if __name__ == "__main__":
    main()