"""
Cache warming service for the financial dashboard API.

This service pre-loads frequently accessed data and computations
into cache to improve initial response times.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from .cache_manager import cache_manager
from .data_loader import load_and_validate_data
from .revenue_calculator import create_revenue_timeline, create_property_revenue_summary
from .maintenance_calculator import create_lost_income_summary
from ..config.cache_config import CacheConfig

logger = logging.getLogger(__name__)


class CacheWarmingService:
    """Service for warming up caches with commonly requested data."""
    
    def __init__(self):
        self.is_warming = False
        self.last_warming_time = None
        self.warming_results = {}
    
    async def warm_data_cache(self, data_file_path: str) -> bool:
        """
        Warm the data cache by loading the main data file.
        
        Args:
            data_file_path: Path to the data file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Warming data cache...")
            data = load_and_validate_data(data_file_path)
            logger.info(f"Data cache warmed with {len(data.reservations)} reservations, "
                       f"{len(data.properties)} properties")
            return True
        except Exception as e:
            logger.error(f"Failed to warm data cache: {e}")
            return False
    
    async def warm_query_caches(self, data) -> Dict[str, bool]:
        """
        Warm query caches with common API requests.
        
        Args:
            data: Loaded and validated data
            
        Returns:
            Dictionary with warming results for each query type
        """
        results = {}
        
        try:
            # Warm revenue timeline cache (last 30 days)
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            logger.info("Warming revenue timeline cache...")
            create_revenue_timeline(data.reservations, start_date, end_date)
            results['revenue_timeline'] = True
            
            # Warm property revenue summary cache
            logger.info("Warming property revenue summary cache...")
            create_property_revenue_summary(data.reservations, start_date, end_date)
            results['property_revenue'] = True
            
            # Warm lost income cache
            logger.info("Warming lost income cache...")
            create_lost_income_summary(data.reservations, data.maintenance_blocks, start_date, end_date)
            results['lost_income'] = True
            
            # Warm full dataset caches (no date filters)
            logger.info("Warming full dataset caches...")
            create_revenue_timeline(data.reservations)
            create_property_revenue_summary(data.reservations)
            results['full_dataset'] = True
            
        except Exception as e:
            logger.error(f"Error warming query caches: {e}")
            results['error'] = str(e)
        
        return results
    
    async def warm_common_date_ranges(self, data) -> Dict[str, bool]:
        """
        Warm caches for commonly requested date ranges.
        
        Args:
            data: Loaded and validated data
            
        Returns:
            Dictionary with warming results for each date range
        """
        results = {}
        current_date = datetime.now()
        
        date_ranges = [
            # Last 7 days
            {
                'name': 'last_7_days',
                'start': (current_date - timedelta(days=7)).strftime('%Y-%m-%d'),
                'end': current_date.strftime('%Y-%m-%d')
            },
            # Last 30 days
            {
                'name': 'last_30_days',
                'start': (current_date - timedelta(days=30)).strftime('%Y-%m-%d'),
                'end': current_date.strftime('%Y-%m-%d')
            },
            # Last 90 days
            {
                'name': 'last_90_days',
                'start': (current_date - timedelta(days=90)).strftime('%Y-%m-%d'),
                'end': current_date.strftime('%Y-%m-%d')
            },
            # Current month
            {
                'name': 'current_month',
                'start': current_date.replace(day=1).strftime('%Y-%m-%d'),
                'end': current_date.strftime('%Y-%m-%d')
            },
            # Previous month
            {
                'name': 'previous_month',
                'start': (current_date.replace(day=1) - timedelta(days=1)).replace(day=1).strftime('%Y-%m-%d'),
                'end': (current_date.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')
            }
        ]
        
        for date_range in date_ranges:
            try:
                logger.info(f"Warming cache for {date_range['name']}...")
                
                # Warm revenue timeline
                create_revenue_timeline(data.reservations, date_range['start'], date_range['end'])
                
                # Warm property revenue
                create_property_revenue_summary(data.reservations, date_range['start'], date_range['end'])
                
                # Warm lost income
                create_lost_income_summary(
                    data.reservations, 
                    data.maintenance_blocks, 
                    date_range['start'], 
                    date_range['end']
                )
                
                results[date_range['name']] = True
                
            except Exception as e:
                logger.error(f"Error warming cache for {date_range['name']}: {e}")
                results[date_range['name']] = False
        
        return results
    
    async def warm_all_caches(self, data_file_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive cache warming.
        
        Args:
            data_file_path: Path to the data file
            
        Returns:
            Dictionary with detailed warming results
        """
        if self.is_warming:
            return {"status": "already_warming", "message": "Cache warming already in progress"}
        
        self.is_warming = True
        start_time = datetime.now()
        
        try:
            logger.info("Starting comprehensive cache warming...")
            
            # Step 1: Warm data cache
            data_cache_result = await self.warm_data_cache(data_file_path)
            
            if not data_cache_result:
                return {
                    "status": "failed",
                    "message": "Failed to warm data cache",
                    "duration": (datetime.now() - start_time).total_seconds()
                }
            
            # Load data for query warming
            data = load_and_validate_data(data_file_path)
            
            # Step 2: Warm query caches
            query_results = await self.warm_query_caches(data)
            
            # Step 3: Warm common date ranges
            date_range_results = await self.warm_common_date_ranges(data)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.last_warming_time = end_time
            self.warming_results = {
                "status": "completed",
                "duration": duration,
                "data_cache": data_cache_result,
                "query_caches": query_results,
                "date_ranges": date_range_results,
                "cache_stats": cache_manager.get_stats()
            }
            
            logger.info(f"Cache warming completed in {duration:.2f} seconds")
            return self.warming_results
            
        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
            return {
                "status": "failed",
                "message": str(e),
                "duration": (datetime.now() - start_time).total_seconds()
            }
        finally:
            self.is_warming = False
    
    def get_warming_status(self) -> Dict[str, Any]:
        """Get current cache warming status."""
        return {
            "is_warming": self.is_warming,
            "last_warming_time": self.last_warming_time.isoformat() if self.last_warming_time else None,
            "last_results": self.warming_results,
            "cache_stats": cache_manager.get_stats()
        }
    
    async def schedule_warming(self, data_file_path: str, interval_hours: int = 6):
        """
        Schedule periodic cache warming.
        
        Args:
            data_file_path: Path to the data file
            interval_hours: Hours between warming cycles
        """
        logger.info(f"Scheduling cache warming every {interval_hours} hours")
        
        while True:
            try:
                await self.warm_all_caches(data_file_path)
                await asyncio.sleep(interval_hours * 3600)  # Convert hours to seconds
            except Exception as e:
                logger.error(f"Scheduled cache warming failed: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying


# Global cache warming service instance
cache_warming_service = CacheWarmingService()


async def warm_startup_caches(data_file_path: str):
    """
    Warm essential caches on application startup.
    
    Args:
        data_file_path: Path to the data file
    """
    if not CacheConfig.ENABLE_CACHE_WARMING:
        logger.info("Cache warming disabled by configuration")
        return
    
    logger.info("Starting startup cache warming...")
    
    try:
        # Warm data cache
        await cache_warming_service.warm_data_cache(data_file_path)
        
        # Warm essential query caches
        data = load_and_validate_data(data_file_path)
        
        # Warm most common queries (last 30 days)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        create_revenue_timeline(data.reservations, start_date, end_date)
        create_property_revenue_summary(data.reservations, start_date, end_date)
        
        logger.info("Startup cache warming completed")
        
    except Exception as e:
        logger.error(f"Startup cache warming failed: {e}")


def get_cache_warming_recommendations() -> List[str]:
    """Get recommendations for cache warming optimization."""
    stats = cache_manager.get_stats()
    recommendations = []
    
    # Check cache utilization
    total_entries = stats.get('total_entries', 0)
    if total_entries < 10:
        recommendations.append("Consider running cache warming to improve initial response times")
    
    # Check if warming is enabled
    if not CacheConfig.ENABLE_CACHE_WARMING:
        recommendations.append("Cache warming is disabled - enable it for better performance")
    
    # Environment-specific recommendations
    if CacheConfig.ENVIRONMENT == 'production':
        recommendations.append("Schedule regular cache warming in production for optimal performance")
    
    if not recommendations:
        recommendations.append("Cache warming is properly configured")
    
    return recommendations