from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import logging

from .models import (
    FilterRequest, RevenueTimelineResponse, PropertyRevenueResponse, 
    PropertiesResponse, ErrorResponse, ValidationErrorResponse,
    RevenuePoint, PropertyRevenue, Property, LostIncomeResponse,
    LostIncomeData, ReviewTrendsResponse, ReviewTrend, LeadTimeResponse,
    LeadTimeStats
)
from .services.data_loader import load_and_validate_data, DataLoadingError, DataValidationError
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

@app.get("/api/revenue/timeline", response_model=RevenueTimelineResponse)
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
        
        # Convert to response format
        revenue_points = [
            RevenuePoint(date=item['date'], revenue=item['total_revenue'])
            for item in timeline_data
        ]
        
        # Calculate totals and date range
        total_revenue = sum(point.revenue for point in revenue_points)
        actual_start = min(point.date for point in revenue_points) if revenue_points else start_date
        actual_end = max(point.date for point in revenue_points) if revenue_points else end_date
        
        return RevenueTimelineResponse(
            data=revenue_points,
            total_revenue=total_revenue,
            date_range={
                "start_date": actual_start or "N/A",
                "end_date": actual_end or "N/A"
            }
        )
        
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