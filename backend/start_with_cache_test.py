#!/usr/bin/env python3
"""
Startup script to test the caching system and run the API server.
"""

import uvicorn
import asyncio
import logging
from app.main import app
from app.services.cache_manager import cache_manager
from app.services.cache_warming import cache_warming_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_cache_system():
    """Test the caching system before starting the server."""
    logger.info("🧪 Testing cache system...")
    
    try:
        # Test cache manager initialization
        stats = cache_manager.get_stats()
        logger.info(f"✅ Cache manager initialized: {stats}")
        
        # Test cache warming service
        status = cache_warming_service.get_warming_status()
        logger.info(f"✅ Cache warming service ready: {status['is_warming']}")
        
        logger.info("🎉 Cache system tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Cache system test failed: {e}")
        return False


def main():
    """Main function to start the API with cache testing."""
    print("🚀 Starting Financial Dashboard API with Caching System")
    print("=" * 60)
    
    # Test cache system
    cache_test_passed = asyncio.run(test_cache_system())
    
    if not cache_test_passed:
        print("❌ Cache system tests failed. Starting server anyway...")
    
    print("\n📊 Cache Configuration:")
    print("- Data Cache: 10 entries, 1 hour TTL")
    print("- Query Cache: 500 entries, 30 minutes TTL") 
    print("- Aggregation Cache: 200 entries, 1 hour TTL")
    print("- Performance Monitoring: Enabled")
    print("- Cache Warming: Enabled on startup")
    
    print("\n🔗 Available Cache Endpoints:")
    print("- GET  /api/cache/stats - Cache statistics")
    print("- POST /api/cache/clear - Clear all caches")
    print("- POST /api/cache/warm - Trigger cache warming")
    print("- GET  /api/cache/health - Cache health check")
    print("- GET  /api/performance/stats - Performance metrics")
    print("- GET  /api/system/health - Comprehensive health")
    
    print("\n🧪 To test performance improvements:")
    print("python test_cache_performance.py")
    
    print("\n" + "=" * 60)
    print("Starting server on http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("=" * 60)
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()