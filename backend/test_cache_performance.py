#!/usr/bin/env python3
"""
Cache performance testing script for the Financial Dashboard API.

This script tests the caching system performance and provides
benchmarks for optimization validation.
"""

import asyncio
import time
import requests
import statistics
from typing import List, Dict, Any
import json


class CachePerformanceTester:
    """Test cache performance and measure improvements."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
    
    def make_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make a request and measure response time."""
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                'success': True,
                'duration': duration,
                'status_code': response.status_code,
                'cache_status': response.headers.get('X-Cache-Status', 'UNKNOWN'),
                'response_time_header': response.headers.get('X-Response-Time', 'N/A')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - start_time
            }
    
    def test_endpoint_performance(self, endpoint: str, params: Dict = None, 
                                 iterations: int = 5) -> Dict[str, Any]:
        """Test an endpoint multiple times to measure cache effectiveness."""
        print(f"\nTesting {endpoint} with {iterations} iterations...")
        
        results = []
        cache_hits = 0
        cache_misses = 0
        
        for i in range(iterations):
            result = self.make_request(endpoint, params)
            results.append(result)
            
            if result['success']:
                cache_status = result.get('cache_status', 'UNKNOWN')
                if cache_status == 'HIT':
                    cache_hits += 1
                elif cache_status == 'MISS':
                    cache_misses += 1
                
                print(f"  Request {i+1}: {result['duration']:.3f}s ({cache_status})")
            else:
                print(f"  Request {i+1}: FAILED - {result['error']}")
        
        # Calculate statistics
        successful_results = [r for r in results if r['success']]
        if successful_results:
            durations = [r['duration'] for r in successful_results]
            
            stats = {
                'endpoint': endpoint,
                'total_requests': iterations,
                'successful_requests': len(successful_results),
                'cache_hits': cache_hits,
                'cache_misses': cache_misses,
                'cache_hit_rate': cache_hits / len(successful_results) if successful_results else 0,
                'avg_duration': statistics.mean(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'median_duration': statistics.median(durations),
                'first_request_duration': durations[0] if durations else 0,
                'subsequent_avg_duration': statistics.mean(durations[1:]) if len(durations) > 1 else 0
            }
            
            return stats
        else:
            return {
                'endpoint': endpoint,
                'total_requests': iterations,
                'successful_requests': 0,
                'error': 'All requests failed'
            }
    
    def test_cache_warming(self) -> Dict[str, Any]:
        """Test cache warming functionality."""
        print("\nTesting cache warming...")
        
        # Clear cache first
        try:
            response = requests.post(f"{self.base_url}/api/cache/clear")
            print(f"Cache cleared: {response.status_code}")
        except Exception as e:
            print(f"Failed to clear cache: {e}")
        
        # Trigger cache warming
        start_time = time.time()
        try:
            response = requests.post(f"{self.base_url}/api/cache/warm")
            warming_duration = time.time() - start_time
            
            if response.status_code == 200:
                warming_result = response.json()
                print(f"Cache warming completed in {warming_duration:.3f}s")
                return {
                    'success': True,
                    'duration': warming_duration,
                    'result': warming_result
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'duration': warming_duration
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - start_time
            }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get current cache statistics."""
        try:
            response = requests.get(f"{self.base_url}/api/cache/stats")
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f"HTTP {response.status_code}"}
        except Exception as e:
            return {'error': str(e)}
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive cache performance tests."""
        print("=" * 60)
        print("CACHE PERFORMANCE TEST SUITE")
        print("=" * 60)
        
        # Test endpoints with different parameters
        test_cases = [
            {
                'endpoint': '/api/properties',
                'params': None,
                'name': 'Properties List'
            },
            {
                'endpoint': '/api/revenue/timeline',
                'params': {'start_date': '2024-01-01', 'end_date': '2024-01-31'},
                'name': 'Revenue Timeline (January 2024)'
            },
            {
                'endpoint': '/api/revenue/by-property',
                'params': {'start_date': '2024-01-01', 'end_date': '2024-01-31'},
                'name': 'Revenue by Property (January 2024)'
            },
            {
                'endpoint': '/api/maintenance/lost-income',
                'params': {'start_date': '2024-01-01', 'end_date': '2024-01-31'},
                'name': 'Lost Income (January 2024)'
            },
            {
                'endpoint': '/api/kpis',
                'params': {'start_date': '2024-01-01', 'end_date': '2024-01-31'},
                'name': 'KPIs (January 2024)'
            }
        ]
        
        # Get initial cache stats
        initial_stats = self.get_cache_stats()
        print(f"\nInitial cache stats: {json.dumps(initial_stats, indent=2)}")
        
        # Test cache warming
        warming_result = self.test_cache_warming()
        
        # Wait a moment for warming to complete
        time.sleep(2)
        
        # Test each endpoint
        test_results = []
        for test_case in test_cases:
            result = self.test_endpoint_performance(
                test_case['endpoint'],
                test_case['params'],
                iterations=3
            )
            result['name'] = test_case['name']
            test_results.append(result)
        
        # Get final cache stats
        final_stats = self.get_cache_stats()
        
        # Compile comprehensive results
        comprehensive_results = {
            'warming_result': warming_result,
            'test_results': test_results,
            'initial_cache_stats': initial_stats,
            'final_cache_stats': final_stats,
            'summary': self._generate_summary(test_results)
        }
        
        self._print_summary(comprehensive_results)
        return comprehensive_results
    
    def _generate_summary(self, test_results: List[Dict]) -> Dict[str, Any]:
        """Generate performance summary."""
        successful_tests = [r for r in test_results if r.get('successful_requests', 0) > 0]
        
        if not successful_tests:
            return {'error': 'No successful tests'}
        
        # Calculate overall statistics
        all_durations = []
        total_cache_hits = 0
        total_requests = 0
        
        for result in successful_tests:
            all_durations.extend([
                result.get('first_request_duration', 0),
                result.get('subsequent_avg_duration', 0)
            ])
            total_cache_hits += result.get('cache_hits', 0)
            total_requests += result.get('successful_requests', 0)
        
        return {
            'total_tests': len(test_results),
            'successful_tests': len(successful_tests),
            'overall_cache_hit_rate': total_cache_hits / total_requests if total_requests > 0 else 0,
            'avg_response_time': statistics.mean(all_durations) if all_durations else 0,
            'fastest_response': min(all_durations) if all_durations else 0,
            'slowest_response': max(all_durations) if all_durations else 0,
            'performance_improvement': self._calculate_improvement(successful_tests)
        }
    
    def _calculate_improvement(self, test_results: List[Dict]) -> Dict[str, float]:
        """Calculate performance improvement from caching."""
        improvements = []
        
        for result in test_results:
            first_duration = result.get('first_request_duration', 0)
            subsequent_avg = result.get('subsequent_avg_duration', 0)
            
            if first_duration > 0 and subsequent_avg > 0:
                improvement = ((first_duration - subsequent_avg) / first_duration) * 100
                improvements.append(improvement)
        
        if improvements:
            return {
                'avg_improvement_percent': statistics.mean(improvements),
                'max_improvement_percent': max(improvements),
                'min_improvement_percent': min(improvements)
            }
        else:
            return {'avg_improvement_percent': 0}
    
    def _print_summary(self, results: Dict[str, Any]):
        """Print formatted test summary."""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        summary = results.get('summary', {})
        
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Successful Tests: {summary.get('successful_tests', 0)}")
        print(f"Overall Cache Hit Rate: {summary.get('overall_cache_hit_rate', 0):.2%}")
        print(f"Average Response Time: {summary.get('avg_response_time', 0):.3f}s")
        print(f"Fastest Response: {summary.get('fastest_response', 0):.3f}s")
        print(f"Slowest Response: {summary.get('slowest_response', 0):.3f}s")
        
        improvement = summary.get('performance_improvement', {})
        avg_improvement = improvement.get('avg_improvement_percent', 0)
        print(f"Average Performance Improvement: {avg_improvement:.1f}%")
        
        print("\nDETAILED RESULTS:")
        for result in results.get('test_results', []):
            if result.get('successful_requests', 0) > 0:
                print(f"\n{result.get('name', result.get('endpoint', 'Unknown'))}:")
                print(f"  Cache Hit Rate: {result.get('cache_hit_rate', 0):.2%}")
                print(f"  First Request: {result.get('first_request_duration', 0):.3f}s")
                print(f"  Subsequent Avg: {result.get('subsequent_avg_duration', 0):.3f}s")
                print(f"  Min Duration: {result.get('min_duration', 0):.3f}s")
                print(f"  Max Duration: {result.get('max_duration', 0):.3f}s")


def main():
    """Main function to run cache performance tests."""
    tester = CachePerformanceTester()
    
    # Check if API is running
    try:
        response = requests.get(f"{tester.base_url}/health")
        if response.status_code != 200:
            print(f"API health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"Cannot connect to API at {tester.base_url}: {e}")
        print("Make sure the API server is running with: uvicorn app.main:app --reload")
        return
    
    # Run comprehensive tests
    results = tester.run_comprehensive_test()
    
    # Save results to file
    with open('cache_performance_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: cache_performance_results.json")


if __name__ == "__main__":
    main()