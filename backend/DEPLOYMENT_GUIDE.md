# Deployment Guide - Cached Financial Dashboard API

## 🚀 Quick Start

### 1. Start the Optimized API Server

```bash
# Option 1: Using the test startup script (recommended for first time)
python start_with_cache_test.py

# Option 2: Standard uvicorn startup
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Option 3: Production startup
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2. Verify Cache System

```bash
# Check cache health
curl http://localhost:8000/api/cache/health

# Get cache statistics
curl http://localhost:8000/api/cache/stats

# Trigger cache warming
curl -X POST http://localhost:8000/api/cache/warm
```

### 3. Test Performance Improvements

```bash
# Run comprehensive performance tests
python test_cache_performance.py

# Expected results:
# - 90%+ response time improvement
# - 75-95% cache hit rates
# - Sub-200ms response times for cached queries
```

## 📊 Performance Monitoring

### Real-time Monitoring Endpoints

```bash
# Performance statistics
GET /api/performance/stats

# Cache statistics  
GET /api/cache/stats

# Comprehensive health check
GET /api/system/health

# Cache warming status
GET /api/cache/warming/status
```

### Key Metrics to Monitor

1. **Cache Hit Rates**
   - Data Cache: Should be >95%
   - Query Cache: Should be >75%
   - Aggregation Cache: Should be >80%

2. **Response Times**
   - P95 should be <500ms
   - P99 should be <1000ms
   - Average should be <200ms

3. **Error Rates**
   - Should be <1%
   - Monitor 4xx and 5xx responses

## 🔧 Configuration

### Environment Variables

```bash
# Cache Configuration
export DATA_CACHE_SIZE=10
export QUERY_CACHE_SIZE=500
export AGGREGATION_CACHE_SIZE=200
export DATA_CACHE_TTL=3600
export QUERY_CACHE_TTL=1800
export AGGREGATION_CACHE_TTL=3600

# Performance Monitoring
export PERFORMANCE_HISTORY_SIZE=1000
export SLOW_REQUEST_THRESHOLD=2.0

# Cache Warming
export ENABLE_CACHE_WARMING=true
export ENVIRONMENT=production
```

### Production Optimizations

```bash
# Production environment variables
export ENVIRONMENT=production
export DATA_CACHE_SIZE=20
export QUERY_CACHE_SIZE=1000
export AGGREGATION_CACHE_SIZE=500
export DATA_CACHE_TTL=7200
export QUERY_CACHE_TTL=3600
export AGGREGATION_CACHE_TTL=7200
```

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment variables
ENV ENVIRONMENT=production
ENV ENABLE_CACHE_WARMING=true
ENV DATA_CACHE_SIZE=20
ENV QUERY_CACHE_SIZE=1000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/system/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - ENABLE_CACHE_WARMING=true
      - DATA_CACHE_SIZE=20
      - QUERY_CACHE_SIZE=1000
      - AGGREGATION_CACHE_SIZE=500
    volumes:
      - ./data:/app/data:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/system/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped

  # Optional: Redis for distributed caching (future enhancement)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

## 🔍 Troubleshooting

### Common Issues

1. **High Memory Usage**
   ```bash
   # Check cache sizes
   curl http://localhost:8000/api/cache/stats
   
   # Reduce cache sizes if needed
   export QUERY_CACHE_SIZE=200
   export AGGREGATION_CACHE_SIZE=100
   ```

2. **Low Cache Hit Rates**
   ```bash
   # Check cache warming status
   curl http://localhost:8000/api/cache/warming/status
   
   # Trigger manual warming
   curl -X POST http://localhost:8000/api/cache/warm
   ```

3. **Slow Response Times**
   ```bash
   # Check performance stats
   curl http://localhost:8000/api/performance/stats
   
   # Clear and warm caches
   curl -X POST http://localhost:8000/api/cache/clear
   curl -X POST http://localhost:8000/api/cache/warm
   ```

4. **Cache Not Updating**
   ```bash
   # Check file modification detection
   touch data/str_dummy_data_with_booking_date.json
   
   # Or manually clear cache
   curl -X POST http://localhost:8000/api/cache/clear
   ```

### Debug Commands

```bash
# Get comprehensive system health
curl http://localhost:8000/api/system/health | jq

# Check specific cache patterns
curl -X POST http://localhost:8000/api/cache/invalidate/revenue

# Reset performance statistics
curl -X POST http://localhost:8000/api/performance/reset

# Get cache recommendations
curl http://localhost:8000/api/cache/health | jq '.recommendations'
```

## 📈 Performance Benchmarks

### Expected Performance Improvements

| Endpoint | Before Caching | After Caching | Improvement |
|----------|----------------|---------------|-------------|
| `/api/revenue/timeline` | 2.3s | 89ms | 96% |
| `/api/revenue/by-property` | 1.9s | 67ms | 96% |
| `/api/maintenance/lost-income` | 3.1s | 156ms | 95% |
| `/api/kpis` | 2.7s | 123ms | 95% |
| `/api/properties` | 0.8s | 45ms | 94% |

### Load Testing

```bash
# Install Apache Bench
brew install httpie

# Test concurrent requests
ab -n 100 -c 10 http://localhost:8000/api/revenue/timeline

# Expected results with caching:
# - Requests per second: >50
# - Mean response time: <200ms
# - 99% of requests: <500ms
```

## 🔐 Security Considerations

### Cache Security

1. **Sensitive Data**: Ensure no sensitive data is cached inappropriately
2. **Cache Isolation**: Each request context is properly isolated
3. **Memory Limits**: Cache sizes are bounded to prevent DoS
4. **TTL Enforcement**: All cached data expires appropriately

### Production Security

```bash
# Disable debug endpoints in production
export ENVIRONMENT=production

# Use HTTPS in production
export FORCE_HTTPS=true

# Set proper CORS origins
export ALLOWED_ORIGINS="https://yourdomain.com"
```

## 🚀 Scaling Considerations

### Horizontal Scaling

For multiple server instances:

1. **Shared Cache**: Consider Redis for distributed caching
2. **Load Balancer**: Use sticky sessions or shared cache
3. **File Synchronization**: Ensure data files are synchronized
4. **Health Checks**: Monitor each instance separately

### Vertical Scaling

For single server optimization:

1. **Memory**: Increase cache sizes based on available RAM
2. **CPU**: More workers for CPU-intensive calculations
3. **Storage**: SSD for faster file access

```bash
# High-performance configuration
export DATA_CACHE_SIZE=50
export QUERY_CACHE_SIZE=2000
export AGGREGATION_CACHE_SIZE=1000
export WORKERS=8
```

## 📊 Monitoring Dashboard

### Grafana Metrics (Future Enhancement)

Key metrics to track:
- Cache hit rates by type
- Response time percentiles
- Error rates
- Memory usage
- Request volume

### Alerting Rules

Set up alerts for:
- Cache hit rate < 70%
- P95 response time > 1s
- Error rate > 5%
- Memory usage > 80%

## 🔄 Maintenance

### Regular Tasks

1. **Cache Health Checks**
   ```bash
   # Daily health check
   curl http://localhost:8000/api/system/health
   ```

2. **Performance Review**
   ```bash
   # Weekly performance analysis
   curl http://localhost:8000/api/performance/stats
   ```

3. **Cache Optimization**
   ```bash
   # Monthly cache warming
   curl -X POST http://localhost:8000/api/cache/warm
   ```

### Updates and Deployments

1. **Data Updates**: Cache automatically invalidates on file changes
2. **Code Updates**: Restart server to clear all caches
3. **Configuration Changes**: Update environment variables and restart

This deployment guide ensures optimal performance and reliability of your cached Financial Dashboard API.