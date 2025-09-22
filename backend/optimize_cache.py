#!/usr/bin/env python3
"""
Cache optimization utility for the Financial Dashboard API.

This script analyzes cache performance and provides recommendations
for optimal cache configuration based on usage patterns.
"""

import requests
import time
import json
import statistics
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta


class CacheOptimizer:
    """Analyze and optimize cache performance."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.optimization_results = {}
    
    def analyze_cache_performance(self, duration_minutes: int = 10) -> Dict[str, Any]:
        """Analyze cache performance over a period of time."""
        print(f"📊 Analyzing cache performance for {duration_minutes} minutes...")
        
        measurements = []
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            try:
                # Get current stats
                cache_stats = self._get_cache_stats()
                perf_stats = self._get_performance_stats()
                
                measurement = {
                    'timestamp': datetime.now().isoformat(),
                    'cache_stats': cache_stats,
                    'performance_stats': perf_stats
                }
                measurements.append(measurement)
                
                print(f"📈 Measurement {len(measurements)}: "
                      f"Total entries: {cache_stats.get('data', {}).get('total_entries', 0)}")
                
                time.sleep(30)  # Measure every 30 seconds
                
            except KeyboardInterrupt:
                print("\n⏹️  Analysis interrupted by user")
                break
            except Exception as e:
                print(f"⚠️  Error during measurement: {e}")
                time.sleep(30)
        
        return self._analyze_measurements(measurements)
    
    def _get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            response = requests.get(f"{self.base_url}/api/cache/stats")
            response.raise_for_status()
            return response.json()
        except:
            return {}
    
    def _get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        try:
            response = requests.get(f"{self.base_url}/api/performance/stats")
            response.raise_for_status()
            return response.json()
        except:
            return {}
    
    def _analyze_measurements(self, measurements: List[Dict]) -> Dict[str, Any]:
        """Analyze collected measurements."""
        if not measurements:
            return {"error": "No measurements collected"}
        
        print("\n🔍 Analyzing collected data...")
        
        # Extract metrics
        cache_sizes = []
        hit_rates = {'data': [], 'query': [], 'aggregation': []}
        response_times = []
        
        for measurement in measurements:
            cache_data = measurement.get('cache_stats', {}).get('data', {})
            
            # Cache sizes
            total_entries = cache_data.get('total_entries', 0)
            cache_sizes.append(total_entries)
            
            # Hit rates
            for cache_type in ['data_cache', 'query_cache', 'aggregation_cache']:
                cache_info = cache_data.get(cache_type, {})
                hit_ratio = cache_info.get('hit_ratio', 0)
                cache_key = cache_type.replace('_cache', '')
                hit_rates[cache_key].append(hit_ratio)
            
            # Response times
            perf_data = measurement.get('performance_stats', {}).get('data', {})
            overall = perf_data.get('overall', {})
            avg_response = overall.get('avg_response_time', 0)
            if avg_response > 0:
                response_times.append(avg_response)
        
        # Calculate statistics
        analysis = {
            'measurement_count': len(measurements),
            'duration_minutes': len(measurements) * 0.5,  # 30-second intervals
            'cache_utilization': {
                'avg_total_entries': statistics.mean(cache_sizes) if cache_sizes else 0,
                'max_total_entries': max(cache_sizes) if cache_sizes else 0,
                'min_total_entries': min(cache_sizes) if cache_sizes else 0
            },
            'hit_rates': {},
            'performance': {},
            'recommendations': []
        }
        
        # Analyze hit rates
        for cache_type, rates in hit_rates.items():
            if rates:
                analysis['hit_rates'][cache_type] = {
                    'avg': statistics.mean(rates),
                    'min': min(rates),
                    'max': max(rates),
                    'std_dev': statistics.stdev(rates) if len(rates) > 1 else 0
                }
        
        # Analyze performance
        if response_times:
            analysis['performance'] = {
                'avg_response_time': statistics.mean(response_times),
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                'p95_response_time': sorted(response_times)[int(len(response_times) * 0.95)]
            }
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on analysis."""
        recommendations = []
        
        # Check hit rates
        hit_rates = analysis.get('hit_rates', {})
        
        for cache_type, stats in hit_rates.items():
            avg_hit_rate = stats.get('avg', 0)
            
            if avg_hit_rate < 0.5:  # Less than 50% hit rate
                recommendations.append(
                    f"🔴 {cache_type.title()} cache hit rate is low ({avg_hit_rate:.1%}). "
                    f"Consider increasing cache size or TTL."
                )
            elif avg_hit_rate < 0.7:  # Less than 70% hit rate
                recommendations.append(
                    f"🟡 {cache_type.title()} cache hit rate could be improved ({avg_hit_rate:.1%}). "
                    f"Monitor usage patterns."
                )
            else:
                recommendations.append(
                    f"✅ {cache_type.title()} cache performing well ({avg_hit_rate:.1%} hit rate)."
                )
        
        # Check performance
        performance = analysis.get('performance', {})
        avg_response = performance.get('avg_response_time', 0)
        
        if avg_response > 1.0:
            recommendations.append(
                f"🔴 Average response time is high ({avg_response:.3f}s). "
                f"Consider more aggressive caching or optimization."
            )
        elif avg_response > 0.5:
            recommendations.append(
                f"🟡 Response time could be improved ({avg_response:.3f}s). "
                f"Monitor for optimization opportunities."
            )
        else:
            recommendations.append(
                f"✅ Response times are excellent ({avg_response:.3f}s)."
            )
        
        # Check cache utilization
        utilization = analysis.get('cache_utilization', {})
        max_entries = utilization.get('max_total_entries', 0)
        
        if max_entries > 600:  # Close to default total capacity
            recommendations.append(
                f"🟡 Cache utilization is high ({max_entries} entries). "
                f"Consider increasing cache sizes."
            )
        
        return recommendations
    
    def suggest_optimal_config(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest optimal cache configuration based on analysis."""
        hit_rates = analysis.get('hit_rates', {})
        utilization = analysis.get('cache_utilization', {})
        performance = analysis.get('performance', {})
        
        # Current default config
        current_config = {
            'DATA_CACHE_SIZE': 10,
            'QUERY_CACHE_SIZE': 500,
            'AGGREGATION_CACHE_SIZE': 200,
            'DATA_CACHE_TTL': 3600,
            'QUERY_CACHE_TTL': 1800,
            'AGGREGATION_CACHE_TTL': 3600
        }
        
        # Suggested optimizations
        suggested_config = current_config.copy()
        optimizations = []
        
        # Adjust based on hit rates
        query_hit_rate = hit_rates.get('query', {}).get('avg', 0)
        if query_hit_rate < 0.7:
            suggested_config['QUERY_CACHE_SIZE'] = 750
            suggested_config['QUERY_CACHE_TTL'] = 2700  # 45 minutes
            optimizations.append("Increased query cache size and TTL due to low hit rate")
        
        agg_hit_rate = hit_rates.get('aggregation', {}).get('avg', 0)
        if agg_hit_rate < 0.8:
            suggested_config['AGGREGATION_CACHE_SIZE'] = 300
            suggested_config['AGGREGATION_CACHE_TTL'] = 5400  # 90 minutes
            optimizations.append("Increased aggregation cache size and TTL")
        
        # Adjust based on performance
        avg_response = performance.get('avg_response_time', 0)
        if avg_response > 0.5:
            suggested_config['QUERY_CACHE_SIZE'] = min(1000, suggested_config['QUERY_CACHE_SIZE'] * 1.5)
            suggested_config['AGGREGATION_CACHE_SIZE'] = min(500, suggested_config['AGGREGATION_CACHE_SIZE'] * 1.5)
            optimizations.append("Increased cache sizes due to slow response times")
        
        # Adjust based on utilization
        max_entries = utilization.get('max_total_entries', 0)
        if max_entries > 600:
            suggested_config['QUERY_CACHE_SIZE'] = int(suggested_config['QUERY_CACHE_SIZE'] * 1.2)
            suggested_config['AGGREGATION_CACHE_SIZE'] = int(suggested_config['AGGREGATION_CACHE_SIZE'] * 1.2)
            optimizations.append("Increased cache sizes due to high utilization")
        
        return {
            'current_config': current_config,
            'suggested_config': suggested_config,
            'optimizations': optimizations,
            'expected_improvements': self._estimate_improvements(current_config, suggested_config)
        }
    
    def _estimate_improvements(self, current: Dict, suggested: Dict) -> List[str]:
        """Estimate expected improvements from configuration changes."""
        improvements = []
        
        # Cache size improvements
        query_increase = (suggested['QUERY_CACHE_SIZE'] - current['QUERY_CACHE_SIZE']) / current['QUERY_CACHE_SIZE']
        if query_increase > 0.1:  # More than 10% increase
            improvements.append(f"Query cache hit rate may improve by 5-15%")
        
        agg_increase = (suggested['AGGREGATION_CACHE_SIZE'] - current['AGGREGATION_CACHE_SIZE']) / current['AGGREGATION_CACHE_SIZE']
        if agg_increase > 0.1:
            improvements.append(f"Aggregation cache hit rate may improve by 10-20%")
        
        # TTL improvements
        if suggested['QUERY_CACHE_TTL'] > current['QUERY_CACHE_TTL']:
            improvements.append("Longer cache retention may reduce computation load")
        
        if not improvements:
            improvements.append("Current configuration appears optimal")
        
        return improvements
    
    def run_load_test(self, duration_minutes: int = 5) -> Dict[str, Any]:
        """Run a load test to stress-test the cache system."""
        print(f"🚀 Running load test for {duration_minutes} minutes...")
        
        # Test endpoints
        test_endpoints = [
            '/api/properties',
            '/api/revenue/timeline?start_date=2024-01-01&end_date=2024-01-31',
            '/api/revenue/by-property?start_date=2024-01-01&end_date=2024-01-31',
            '/api/kpis?start_date=2024-01-01&end_date=2024-01-31'
        ]
        
        results = []
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        request_count = 0
        
        while time.time() < end_time:
            for endpoint in test_endpoints:
                try:
                    request_start = time.time()
                    response = requests.get(f"{self.base_url}{endpoint}")
                    request_duration = time.time() - request_start
                    
                    results.append({
                        'endpoint': endpoint,
                        'duration': request_duration,
                        'status_code': response.status_code,
                        'cache_status': response.headers.get('X-Cache-Status', 'UNKNOWN'),
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    request_count += 1
                    if request_count % 10 == 0:
                        print(f"📊 Completed {request_count} requests...")
                    
                except Exception as e:
                    print(f"❌ Request failed: {e}")
                
                time.sleep(0.1)  # Small delay between requests
        
        return self._analyze_load_test_results(results)
    
    def _analyze_load_test_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze load test results."""
        if not results:
            return {"error": "No load test results"}
        
        # Group by endpoint
        endpoint_stats = {}
        cache_hits = 0
        cache_misses = 0
        
        for result in results:
            endpoint = result['endpoint']
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    'durations': [],
                    'status_codes': [],
                    'cache_hits': 0,
                    'cache_misses': 0
                }
            
            endpoint_stats[endpoint]['durations'].append(result['duration'])
            endpoint_stats[endpoint]['status_codes'].append(result['status_code'])
            
            cache_status = result.get('cache_status', 'UNKNOWN')
            if cache_status == 'HIT':
                endpoint_stats[endpoint]['cache_hits'] += 1
                cache_hits += 1
            elif cache_status == 'MISS':
                endpoint_stats[endpoint]['cache_misses'] += 1
                cache_misses += 1
        
        # Calculate statistics
        analysis = {
            'total_requests': len(results),
            'overall_cache_hit_rate': cache_hits / (cache_hits + cache_misses) if (cache_hits + cache_misses) > 0 else 0,
            'endpoints': {}
        }
        
        for endpoint, stats in endpoint_stats.items():
            durations = stats['durations']
            total_requests = len(durations)
            
            analysis['endpoints'][endpoint] = {
                'request_count': total_requests,
                'avg_duration': statistics.mean(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'p95_duration': sorted(durations)[int(len(durations) * 0.95)],
                'cache_hit_rate': stats['cache_hits'] / total_requests if total_requests > 0 else 0,
                'success_rate': sum(1 for code in stats['status_codes'] if code < 400) / total_requests
            }
        
        return analysis
    
    def print_analysis_report(self, analysis: Dict[str, Any]):
        """Print formatted analysis report."""
        print("\n" + "="*60)
        print("📊 CACHE PERFORMANCE ANALYSIS REPORT")
        print("="*60)
        
        # Basic info
        print(f"📅 Analysis Duration: {analysis.get('duration_minutes', 0):.1f} minutes")
        print(f"📈 Measurements Taken: {analysis.get('measurement_count', 0)}")
        
        # Cache utilization
        utilization = analysis.get('cache_utilization', {})
        print(f"\n💾 Cache Utilization:")
        print(f"   Average Entries: {utilization.get('avg_total_entries', 0):.0f}")
        print(f"   Peak Entries: {utilization.get('max_total_entries', 0)}")
        
        # Hit rates
        hit_rates = analysis.get('hit_rates', {})
        print(f"\n🎯 Cache Hit Rates:")
        for cache_type, stats in hit_rates.items():
            print(f"   {cache_type.title()}: {stats.get('avg', 0):.1%} (±{stats.get('std_dev', 0):.1%})")
        
        # Performance
        performance = analysis.get('performance', {})
        if performance:
            print(f"\n⚡ Performance Metrics:")
            print(f"   Average Response: {performance.get('avg_response_time', 0):.3f}s")
            print(f"   P95 Response: {performance.get('p95_response_time', 0):.3f}s")
            print(f"   Best Response: {performance.get('min_response_time', 0):.3f}s")
        
        # Recommendations
        recommendations = analysis.get('recommendations', [])
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"   {rec}")
    
    def print_config_suggestions(self, config_analysis: Dict[str, Any]):
        """Print configuration suggestions."""
        print("\n" + "="*60)
        print("⚙️  CONFIGURATION OPTIMIZATION SUGGESTIONS")
        print("="*60)
        
        current = config_analysis.get('current_config', {})
        suggested = config_analysis.get('suggested_config', {})
        optimizations = config_analysis.get('optimizations', [])
        improvements = config_analysis.get('expected_improvements', [])
        
        print("📋 Current vs Suggested Configuration:")
        print("-" * 40)
        
        for key in current.keys():
            current_val = current[key]
            suggested_val = suggested[key]
            change_indicator = "→" if current_val != suggested_val else "✓"
            print(f"   {key}: {current_val} {change_indicator} {suggested_val}")
        
        if optimizations:
            print(f"\n🔧 Optimization Rationale:")
            for opt in optimizations:
                print(f"   • {opt}")
        
        if improvements:
            print(f"\n📈 Expected Improvements:")
            for imp in improvements:
                print(f"   • {imp}")
        
        # Generate environment variable export commands
        print(f"\n💻 Environment Variables to Set:")
        print("-" * 40)
        for key, value in suggested.items():
            print(f"export {key}={value}")


def main():
    """Main function for cache optimization."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cache optimization utility")
    parser.add_argument("--url", default="http://localhost:8000",
                       help="API base URL")
    parser.add_argument("--analyze", type=int, default=0,
                       help="Analyze cache performance for N minutes")
    parser.add_argument("--load-test", type=int, default=0,
                       help="Run load test for N minutes")
    parser.add_argument("--quick", action="store_true",
                       help="Run quick 2-minute analysis")
    
    args = parser.parse_args()
    
    optimizer = CacheOptimizer(args.url)
    
    # Check API availability
    try:
        response = requests.get(f"{args.url}/health")
        if response.status_code != 200:
            print(f"❌ API not available at {args.url}")
            return
    except:
        print(f"❌ Cannot connect to API at {args.url}")
        return
    
    if args.quick:
        print("🚀 Running quick cache analysis...")
        analysis = optimizer.analyze_cache_performance(2)
        optimizer.print_analysis_report(analysis)
        
        config_suggestions = optimizer.suggest_optimal_config(analysis)
        optimizer.print_config_suggestions(config_suggestions)
        
    elif args.analyze > 0:
        analysis = optimizer.analyze_cache_performance(args.analyze)
        optimizer.print_analysis_report(analysis)
        
        config_suggestions = optimizer.suggest_optimal_config(analysis)
        optimizer.print_config_suggestions(config_suggestions)
        
    elif args.load_test > 0:
        load_results = optimizer.run_load_test(args.load_test)
        print("\n📊 LOAD TEST RESULTS")
        print("="*50)
        print(f"Total Requests: {load_results.get('total_requests', 0)}")
        print(f"Overall Cache Hit Rate: {load_results.get('overall_cache_hit_rate', 0):.1%}")
        
        endpoints = load_results.get('endpoints', {})
        for endpoint, stats in endpoints.items():
            print(f"\n{endpoint}:")
            print(f"  Requests: {stats['request_count']}")
            print(f"  Avg Duration: {stats['avg_duration']:.3f}s")
            print(f"  P95 Duration: {stats['p95_duration']:.3f}s")
            print(f"  Cache Hit Rate: {stats['cache_hit_rate']:.1%}")
            print(f"  Success Rate: {stats['success_rate']:.1%}")
    
    else:
        print("🔧 Cache Optimization Utility")
        print("Use --quick for a 2-minute analysis")
        print("Use --analyze N for N-minute analysis")
        print("Use --load-test N for N-minute load test")


if __name__ == "__main__":
    main()