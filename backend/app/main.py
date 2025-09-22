from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict
from datetime import datetime
import logging

from .models import (
    FilterRequest, PropertyRevenueResponse, 
    PropertiesResponse, ErrorResponse, ValidationErrorResponse,
    PropertyRevenue, Property, LostIncomeResponse,
    LostIncomeData, ReviewTrendsResponse, ReviewTrend, LeadTimeResponse,
    LeadTimeStats, KPIResponse, KPIData, TotalRevenueResponse,
    StaysCountResponse, AverageNightlyRevenueResponse
)
from .services.data_loader import load_and_validate_data, DataLoadingError, DataValidationError
from .services.cache_manager import cache_manager
from .services.cache_warming import cache_warming_service, warm_startup_caches
from .middleware.performance import PerformanceMiddleware, get_performance_stats, reset_performance_stats
from .services.revenue_calculator import (
    create_revenue_timeline, create_property_revenue_summary,
    RevenueCalculationError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Financial Dashboard API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add performance monitoring middleware
app.add_middleware(PerformanceMiddleware)

# Global data storage - in production this would be a database
_data_cache = None

def get_data():
    """Dependency to get loaded data."""
    global _data_cache
    if _data_cache is None:
        try:
            # Try to load from the data directory
            _data_cache = load_and_validate_data("data/str_dummy_data_with_booking_date.json")
            logger.info("Data loaded successfully")
        except (DataLoadingError, DataValidationError) as e:
            logger.error(f"Failed to load data: {e}")
            raise HTTPException(status_code=500, detail=f"Data loading error: {str(e)}")
    return _data_cache

@app.get("/")
async def root():
    return {"message": "Financial Dashboard API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/properties", response_model=PropertiesResponse)
async def get_properties(data=Depends(get_data)):
    """
    Get list of all properties for filter options.
    """
    try:
        properties = [
            Property(
                property_id=prop.property_id,
                property_name=prop.property_name,
                reviews_count=prop.reviews_count,
                average_review_score=prop.average_review_score
            )
            for prop in data.properties
        ]
        
        return PropertiesResponse(
            data=properties,
            total_count=len(properties)
        )
    except Exception as e:
        logger.error(f"Error getting properties: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/revenue/timeline")
async def get_revenue_timeline(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    property_ids: Optional[str] = Query(None, description="Comma-separated property IDs"),
    data=Depends(get_data)
):
    """
    Get revenue timeline with daily granularity.
    """
    try:
        # Parse property IDs if provided
        property_id_list = None
        if property_ids:
            try:
                property_id_list = [int(pid.strip()) for pid in property_ids.split(",")]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid property_ids format")
        
        # Validate dates
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # Filter reservations by property if specified
        reservations = data.reservations
        if property_id_list:
            reservations = [r for r in reservations if r.property_id in property_id_list]
        
        # Create revenue timeline
        timeline_data = create_revenue_timeline(reservations, start_date, end_date)
        
        # Convert to response format - match frontend RevenueTimeline interface
        timeline_points = []
        for item in timeline_data:
            point = {
                'date': item['date'],
                'total_revenue': item['total_revenue']
            }
            # Add property breakdown if property filtering is applied
            if property_id_list and len(property_id_list) == 1:
                point['property_breakdown'] = {property_id_list[0]: item['total_revenue']}
            timeline_points.append(point)
        
        # Calculate totals and date range
        total_revenue = sum(point['total_revenue'] for point in timeline_points)
        actual_start = min(point['date'] for point in timeline_points) if timeline_points else start_date
        actual_end = max(point['date'] for point in timeline_points) if timeline_points else end_date
        
        # Return in the format expected by frontend RevenueTimeline interface
        return {
            "data": timeline_points,
            "total_revenue": total_revenue,
            "date_range": {
                "start_date": actual_start or "N/A",
                "end_date": actual_end or "N/A"
            }
        }
        
    except RevenueCalculationError as e:
        logger.error(f"Revenue calculation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting revenue timeline: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/revenue/by-property", response_model=PropertyRevenueResponse)
async def get_revenue_by_property(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    property_ids: Optional[str] = Query(None, description="Comma-separated property IDs"),
    data=Depends(get_data)
):
    """
    Get total revenue by property.
    """
    try:
        # Parse property IDs if provided
        property_id_list = None
        if property_ids:
            try:
                property_id_list = [int(pid.strip()) for pid in property_ids.split(",")]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid property_ids format")
        
        # Validate dates
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # Filter reservations by property if specified
        reservations = data.reservations
        if property_id_list:
            reservations = [r for r in reservations if r.property_id in property_id_list]
        
        # Create property revenue summary
        property_summary = create_property_revenue_summary(reservations, start_date, end_date)
        
        # Convert to response format
        property_revenues = [
            PropertyRevenue(
                property_id=item['property_id'],
                property_name=item['property_name'],
                total_revenue=item['total_revenue']
            )
            for item in property_summary
        ]
        
        # Calculate total revenue
        total_revenue = sum(prop.total_revenue for prop in property_revenues)
        
        return PropertyRevenueResponse(
            data=property_revenues,
            total_revenue=total_revenue
        )
        
    except RevenueCalculationError as e:
        logger.error(f"Revenue calculation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting revenue by property: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/maintenance/lost-income", response_model=LostIncomeResponse)
async def get_maintenance_lost_income(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    property_ids: Optional[str] = Query(None, description="Comma-separated property IDs"),
    data=Depends(get_data)
):
    """
    Get estimated lost income due to maintenance blocks.
    """
    try:
        from .services.maintenance_calculator import create_lost_income_summary, MaintenanceCalculationError
        
        # Parse property IDs if provided
        property_id_list = None
        if property_ids:
            try:
                property_id_list = [int(pid.strip()) for pid in property_ids.split(",")]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid property_ids format")
        
        # Validate dates
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # Filter maintenance blocks by property if specified
        maintenance_blocks = data.maintenance_blocks
        if property_id_list:
            maintenance_blocks = [m for m in maintenance_blocks if m.property_id in property_id_list]
        
        # Create lost income summary
        lost_income_summary = create_lost_income_summary(
            data.reservations, maintenance_blocks, start_date, end_date
        )
        
        # Convert to response format
        lost_income_data = [
            LostIncomeData(
                property_id=item['property_id'],
                property_name=item['property_name'],
                lost_income=item['lost_income'],
                blocked_days=item['blocked_days'],
                avg_daily_rate=item['average_daily_rate_used']
            )
            for item in lost_income_summary
        ]
        
        # Calculate totals
        total_lost_income = sum(item.lost_income for item in lost_income_data)
        total_blocked_days = sum(item.blocked_days for item in lost_income_data)
        
        return LostIncomeResponse(
            data=lost_income_data,
            total_lost_income=total_lost_income,
            total_blocked_days=total_blocked_days
        )
        
    except MaintenanceCalculationError as e:
        logger.error(f"Maintenance calculation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting maintenance lost income: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/reviews/trends", response_model=ReviewTrendsResponse)
async def get_review_trends(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    property_ids: Optional[str] = Query(None, description="Comma-separated property IDs"),
    data=Depends(get_data)
):
    """
    Get review trends with monthly aggregation.
    """
    try:
        from .services.review_calculator import create_monthly_review_timeline, get_review_statistics, ReviewCalculationError
        
        # Parse property IDs if provided
        property_id_list = None
        if property_ids:
            try:
                property_id_list = [int(pid.strip()) for pid in property_ids.split(",")]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid property_ids format")
        
        # Validate dates
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # Filter reviews by property if specified
        reviews = data.reviews
        if property_id_list:
            reviews = [r for r in reviews if r.property_id in property_id_list]
        
        # Create monthly review timeline
        timeline_data = create_monthly_review_timeline(reviews, start_date, end_date)
        
        # Convert to response format
        review_trends = [
            ReviewTrend(
                month=item['month'],
                avg_rating=item['avg_rating'],
                review_count=item['review_count']
            )
            for item in timeline_data
        ]
        
        # Calculate overall statistics
        overall_stats = get_review_statistics(reviews)
        
        return ReviewTrendsResponse(
            data=review_trends,
            overall_avg_rating=overall_stats['avg_rating'],
            total_reviews=overall_stats['total_reviews']
        )
        
    except ReviewCalculationError as e:
        logger.error(f"Review calculation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting review trends: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/bookings/lead-times", response_model=LeadTimeResponse)
async def get_booking_lead_times(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    property_ids: Optional[str] = Query(None, description="Comma-separated property IDs"),
    data=Depends(get_data)
):
    """
    Get booking lead time analysis with statistics and distribution.
    """
    try:
        from .services.lead_time_calculator import (
            calculate_lead_time_statistics, create_lead_time_histogram, 
            LeadTimeCalculationError
        )
        
        # Parse property IDs if provided
        property_id_list = None
        if property_ids:
            try:
                property_id_list = [int(pid.strip()) for pid in property_ids.split(",")]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid property_ids format")
        
        # Validate dates
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # Calculate lead time statistics
        stats_data = calculate_lead_time_statistics(
            data.reservations, start_date, end_date, property_id_list
        )
        
        # Create histogram distribution
        histogram_data = create_lead_time_histogram(
            data.reservations, start_date, end_date, property_id_list
        )
        
        # Extract histogram counts for the distribution array
        distribution = [item['count'] for item in histogram_data]
        
        # Format histogram data for frontend (convert bin_start to lead_time_days)
        formatted_histogram = []
        for item in histogram_data:
            formatted_histogram.append({
                'lead_time_days': item['bin_start'],
                'count': item['count']
            })
        
        # Create response
        lead_time_stats = LeadTimeStats(
            median_days=stats_data['median_days'],
            p90_days=stats_data['p90_days'],
            distribution=distribution,
            total_bookings=stats_data['count']
        )
        
        # Determine actual date range
        actual_start = start_date or "N/A"
        actual_end = end_date or "N/A"
        
        return LeadTimeResponse(
            stats=lead_time_stats,
            data=formatted_histogram,
            date_range={
                "start_date": actual_start,
                "end_date": actual_end
            }
        )
        
    except LeadTimeCalculationError as e:
        logger.error(f"Lead time calculation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting booking lead times: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/kpis", response_model=KPIResponse)
async def get_kpis(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    property_ids: Optional[str] = Query(None, description="Comma-separated property IDs"),
    data=Depends(get_data)
):
    """
    Get all KPIs in a single response: total revenue, number of stays, 
    average nightly revenue, and lost income due to maintenance.
    """
    try:
        # Parse property IDs if provided
        property_id_list = None
        if property_ids:
            try:
                property_id_list = [int(pid.strip()) for pid in property_ids.split(",")]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid property_ids format")
        
        # Validate dates
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # Filter reservations by property if specified
        reservations = data.reservations
        maintenance_blocks = data.maintenance_blocks
        if property_id_list:
            reservations = [r for r in reservations if r.property_id in property_id_list]
            maintenance_blocks = [m for m in maintenance_blocks if m.property_id in property_id_list]
        
        # Apply date filters to reservations (filter by check-in date)
        filtered_reservations = []
        for r in reservations:
            if start_date and r.check_in < start_date:
                continue
            if end_date and r.check_in > end_date:
                continue
            filtered_reservations.append(r)
        
        # Calculate KPIs
        kpis = []
        
        # 1. Total Revenue
        total_revenue = sum(r.reservation_revenue for r in filtered_reservations)
        kpis.append(KPIData(
            name="total_revenue",
            value=total_revenue,
            unit="USD",
            description="Total revenue from reservations in the selected period"
        ))
        
        # 2. Number of Stays
        total_stays = len(filtered_reservations)
        kpis.append(KPIData(
            name="number_of_stays",
            value=float(total_stays),
            unit="count",
            description="Total number of reservations/stays in the selected period"
        ))
        
        # 3. Average Nightly Revenue (using prorated method)
        from .services.revenue_calculator import calculate_reservation_metrics
        metrics = calculate_reservation_metrics(filtered_reservations)
        avg_nightly_revenue = metrics['average_nightly_rate']
        kpis.append(KPIData(
            name="average_nightly_revenue",
            value=avg_nightly_revenue,
            unit="USD",
            description="Average revenue per night using prorated calculation method"
        ))
        
        # 4. Lost Income Due to Maintenance
        try:
            from .services.maintenance_calculator import create_lost_income_summary
            lost_income_summary = create_lost_income_summary(
                data.reservations, maintenance_blocks, start_date, end_date
            )
            total_lost_income = sum(item['lost_income'] for item in lost_income_summary)
        except Exception as e:
            logger.warning(f"Could not calculate lost income: {e}")
            total_lost_income = 0.0
        
        kpis.append(KPIData(
            name="lost_income_maintenance",
            value=total_lost_income,
            unit="USD",
            description="Estimated lost income due to maintenance blocks in the selected period"
        ))
        
        # Determine actual date range
        actual_start = start_date or "N/A"
        actual_end = end_date or "N/A"
        
        return KPIResponse(
            data=kpis,
            date_range={
                "start_date": actual_start,
                "end_date": actual_end
            },
            property_filter=property_id_list
        )
        
    except Exception as e:
        logger.error(f"Error getting KPIs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/kpis/total-revenue", response_model=TotalRevenueResponse)
async def get_total_revenue_kpi(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    property_ids: Optional[str] = Query(None, description="Comma-separated property IDs"),
    data=Depends(get_data)
):
    """
    Get total revenue KPI for the selected date range and properties.
    """
    try:
        # Parse property IDs if provided
        property_id_list = None
        if property_ids:
            try:
                property_id_list = [int(pid.strip()) for pid in property_ids.split(",")]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid property_ids format")
        
        # Validate dates
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # Filter reservations
        reservations = data.reservations
        if property_id_list:
            reservations = [r for r in reservations if r.property_id in property_id_list]
        
        # Apply date filters (filter by check-in date)
        filtered_reservations = []
        for r in reservations:
            if start_date and r.check_in < start_date:
                continue
            if end_date and r.check_in > end_date:
                continue
            filtered_reservations.append(r)
        
        # Calculate total revenue
        total_revenue = sum(r.reservation_revenue for r in filtered_reservations)
        
        # Count unique properties
        unique_properties = set(r.property_id for r in filtered_reservations)
        property_count = len(unique_properties)
        
        return TotalRevenueResponse(
            total_revenue=total_revenue,
            date_range={
                "start_date": start_date or "N/A",
                "end_date": end_date or "N/A"
            },
            property_count=property_count
        )
        
    except Exception as e:
        logger.error(f"Error getting total revenue KPI: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/kpis/stays-count", response_model=StaysCountResponse)
async def get_stays_count_kpi(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    property_ids: Optional[str] = Query(None, description="Comma-separated property IDs"),
    data=Depends(get_data)
):
    """
    Get number of stays (reservations count) KPI for the selected date range and properties.
    """
    try:
        # Parse property IDs if provided
        property_id_list = None
        if property_ids:
            try:
                property_id_list = [int(pid.strip()) for pid in property_ids.split(",")]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid property_ids format")
        
        # Validate dates
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # Filter reservations
        reservations = data.reservations
        if property_id_list:
            reservations = [r for r in reservations if r.property_id in property_id_list]
        
        # Apply date filters (filter by check-in date)
        filtered_reservations = []
        for r in reservations:
            if start_date and r.check_in < start_date:
                continue
            if end_date and r.check_in > end_date:
                continue
            filtered_reservations.append(r)
        
        # Count stays
        total_stays = len(filtered_reservations)
        
        # Count unique properties
        unique_properties = set(r.property_id for r in filtered_reservations)
        property_count = len(unique_properties)
        
        return StaysCountResponse(
            total_stays=total_stays,
            date_range={
                "start_date": start_date or "N/A",
                "end_date": end_date or "N/A"
            },
            property_count=property_count
        )
        
    except Exception as e:
        logger.error(f"Error getting stays count KPI: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/kpis/average-nightly-revenue", response_model=AverageNightlyRevenueResponse)
async def get_average_nightly_revenue_kpi(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    property_ids: Optional[str] = Query(None, description="Comma-separated property IDs"),
    data=Depends(get_data)
):
    """
    Get average nightly revenue KPI using prorated calculation method.
    """
    try:
        # Parse property IDs if provided
        property_id_list = None
        if property_ids:
            try:
                property_id_list = [int(pid.strip()) for pid in property_ids.split(",")]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid property_ids format")
        
        # Validate dates
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # Filter reservations
        reservations = data.reservations
        if property_id_list:
            reservations = [r for r in reservations if r.property_id in property_id_list]
        
        # Apply date filters (filter by check-in date)
        filtered_reservations = []
        for r in reservations:
            if start_date and r.check_in < start_date:
                continue
            if end_date and r.check_in > end_date:
                continue
            filtered_reservations.append(r)
        
        # Calculate metrics using prorated method
        from .services.revenue_calculator import calculate_reservation_metrics
        metrics = calculate_reservation_metrics(filtered_reservations)
        
        return AverageNightlyRevenueResponse(
            average_nightly_revenue=metrics['average_nightly_rate'],
            total_nights=metrics['total_nights'],
            total_revenue=metrics['total_revenue'],
            date_range={
                "start_date": start_date or "N/A",
                "end_date": end_date or "N/A"
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting average nightly revenue KPI: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Cache Management Endpoints

@app.get("/api/cache/stats")
async def get_cache_stats():
    """
    Get comprehensive cache statistics for monitoring and debugging.
    """
    try:
        stats = cache_manager.get_stats()
        return {
            "status": "success",
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/cache/clear")
async def clear_cache():
    """
    Clear all caches. Use with caution as this will impact performance temporarily.
    """
    try:
        cache_manager.clear_all()
        return {
            "status": "success",
            "message": "All caches cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/cache/invalidate/{pattern}")
async def invalidate_cache_pattern(pattern: str):
    """
    Invalidate cache entries matching a specific pattern.
    
    Args:
        pattern: Pattern to match against cache keys
    """
    try:
        invalidated_count = cache_manager.invalidate_pattern(pattern)
        return {
            "status": "success",
            "message": f"Invalidated {invalidated_count} cache entries matching pattern: {pattern}",
            "invalidated_count": invalidated_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error invalidating cache pattern {pattern}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/cache/health")
async def cache_health_check():
    """
    Health check endpoint specifically for cache system.
    """
    try:
        stats = cache_manager.get_stats()
        
        # Determine health status based on cache performance
        total_entries = stats.get('total_entries', 0)
        data_cache_size = stats.get('data_cache', {}).get('size', 0)
        
        health_status = "healthy"
        if total_entries > 1000:  # High cache usage
            health_status = "warning"
        if data_cache_size == 0:  # No data cached
            health_status = "degraded"
        
        return {
            "status": health_status,
            "cache_stats": stats,
            "recommendations": _get_cache_recommendations(stats),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking cache health: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def _get_cache_recommendations(stats: Dict) -> List[str]:
    """Generate cache optimization recommendations based on stats."""
    recommendations = []
    
    total_entries = stats.get('total_entries', 0)
    if total_entries > 800:
        recommendations.append("Consider increasing cache TTL or clearing old entries")
    
    data_cache_size = stats.get('data_cache', {}).get('size', 0)
    if data_cache_size == 0:
        recommendations.append("Data cache is empty - first request may be slower")
    
    query_cache_size = stats.get('query_cache', {}).get('size', 0)
    if query_cache_size > 400:
        recommendations.append("Query cache is getting full - consider clearing or optimizing queries")
    
    if not recommendations:
        recommendations.append("Cache system is operating optimally")
    
    return recommendations

# Performance Monitoring Endpoints

@app.get("/api/performance/stats")
async def get_performance_statistics():
    """
    Get comprehensive performance statistics including response times,
    error rates, and optimization recommendations.
    """
    try:
        stats = get_performance_stats()
        return {
            "status": "success",
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/performance/reset")
async def reset_performance_statistics():
    """
    Reset performance monitoring statistics. Useful for testing or
    after performance optimizations.
    """
    try:
        reset_performance_stats()
        return {
            "status": "success",
            "message": "Performance statistics reset successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error resetting performance stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/system/health")
async def comprehensive_health_check():
    """
    Comprehensive health check including cache and performance metrics.
    """
    try:
        # Get cache stats
        cache_stats = cache_manager.get_stats()
        
        # Get performance stats
        perf_stats = get_performance_stats()
        
        # Determine overall health
        health_status = "healthy"
        issues = []
        
        # Check cache health
        if cache_stats.get('total_entries', 0) == 0:
            issues.append("No cached data available")
            health_status = "degraded"
        
        # Check performance
        if isinstance(perf_stats, dict) and 'overall' in perf_stats:
            avg_response = perf_stats['overall'].get('avg_response_time', 0)
            error_rate = perf_stats['overall'].get('error_rate', 0)
            
            if avg_response > 2.0:
                issues.append("High average response time")
                health_status = "warning"
            
            if error_rate > 0.05:
                issues.append("High error rate")
                health_status = "warning"
        
        return {
            "status": health_status,
            "issues": issues,
            "cache_stats": cache_stats,
            "performance_stats": perf_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in comprehensive health check: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Cache Warming Endpoints

@app.post("/api/cache/warm")
async def warm_caches():
    """
    Manually trigger cache warming for all common queries and date ranges.
    This can improve performance for subsequent requests.
    """
    try:
        data_file_path = "data/str_dummy_data_with_booking_date.json"
        results = await cache_warming_service.warm_all_caches(data_file_path)
        
        return {
            "status": "success",
            "message": "Cache warming initiated",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error warming caches: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/cache/warming/status")
async def get_cache_warming_status():
    """
    Get the current status of cache warming operations.
    """
    try:
        status = cache_warming_service.get_warming_status()
        return {
            "status": "success",
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting cache warming status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Startup event to warm essential caches
@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    Warms essential caches for better initial performance.
    """
    try:
        data_file_path = "data/str_dummy_data_with_booking_date.json"
        await warm_startup_caches(data_file_path)
        logger.info("Application startup completed with cache warming")
    except Exception as e:
        logger.error(f"Startup cache warming failed: {e}")
        # Don't fail startup if cache warming fails