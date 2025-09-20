from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import date
from enum import Enum

# Request Models for Filtering and Validation

class FilterRequest(BaseModel):
    """Base filter request model with common filtering parameters"""
    start_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")
    property_ids: Optional[List[int]] = Field(None, description="List of property IDs to filter by")
    
    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        if v is not None:
            try:
                date.fromisoformat(v)
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return v
    
    @validator('property_ids')
    def validate_property_ids(cls, v):
        if v is not None and len(v) == 0:
            return None
        return v

# Response Models

class Property(BaseModel):
    """Property information model"""
    property_id: int
    property_name: str
    reviews_count: int = Field(ge=0, description="Total number of reviews")
    average_review_score: float = Field(ge=0, le=5, description="Average review score (0-5)")

class RevenuePoint(BaseModel):
    """Single data point for revenue timeline"""
    date: str = Field(description="Date in YYYY-MM-DD format")
    revenue: float = Field(ge=0, description="Revenue amount")
    property_id: Optional[int] = Field(None, description="Property ID if property-specific")

class RevenueTimelineResponse(BaseModel):
    """Response model for revenue timeline endpoint"""
    data: List[RevenuePoint]
    total_revenue: float = Field(ge=0, description="Sum of all revenue in the period")
    date_range: Dict[str, str] = Field(description="Actual date range of returned data")

class PropertyRevenue(BaseModel):
    """Revenue data for a single property"""
    property_id: int
    property_name: str
    total_revenue: float = Field(ge=0, description="Total revenue for the property")

class PropertyRevenueResponse(BaseModel):
    """Response model for revenue by property endpoint"""
    data: List[PropertyRevenue]
    total_revenue: float = Field(ge=0, description="Sum of all property revenues")

class LeadTimeStats(BaseModel):
    """Lead time statistics"""
    median_days: float = Field(ge=0, description="Median lead time in days")
    p90_days: float = Field(ge=0, description="90th percentile lead time in days")
    distribution: List[int] = Field(description="Histogram bins for lead time distribution")
    total_bookings: int = Field(ge=0, description="Total number of bookings analyzed")

class LeadTimeResponse(BaseModel):
    """Response model for lead time analysis endpoint"""
    stats: LeadTimeStats
    date_range: Dict[str, str] = Field(description="Date range of analyzed bookings")

class ReviewTrend(BaseModel):
    """Monthly review trend data"""
    month: str = Field(description="Month in YYYY-MM format")
    avg_rating: float = Field(ge=0, le=5, description="Average rating for the month")
    review_count: int = Field(ge=0, description="Number of reviews in the month")

class ReviewTrendsResponse(BaseModel):
    """Response model for review trends endpoint"""
    data: List[ReviewTrend]
    overall_avg_rating: float = Field(ge=0, le=5, description="Overall average rating")
    total_reviews: int = Field(ge=0, description="Total number of reviews")

class LostIncomeData(BaseModel):
    """Lost income data for a single property"""
    property_id: int
    property_name: str
    lost_income: float = Field(ge=0, description="Estimated lost income amount")
    blocked_days: int = Field(ge=0, description="Number of days blocked for maintenance")
    avg_daily_rate: float = Field(ge=0, description="Average daily rate used for calculation")

class LostIncomeResponse(BaseModel):
    """Response model for maintenance lost income endpoint"""
    data: List[LostIncomeData]
    total_lost_income: float = Field(ge=0, description="Total estimated lost income")
    total_blocked_days: int = Field(ge=0, description="Total days blocked across all properties")

class PropertiesResponse(BaseModel):
    """Response model for properties list endpoint"""
    data: List[Property]
    total_count: int = Field(ge=0, description="Total number of properties")

# Error Response Models

class ErrorDetail(BaseModel):
    """Individual error detail"""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(description="Error message")
    code: Optional[str] = Field(None, description="Error code")

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(description="Error type")
    message: str = Field(description="Human-readable error message")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed error information")
    timestamp: str = Field(description="ISO timestamp when error occurred")

class ValidationErrorResponse(BaseModel):
    """Validation error response model"""
    error: str = Field(default="validation_error", description="Error type")
    message: str = Field(description="Validation error message")
    details: List[ErrorDetail] = Field(description="Field-specific validation errors")
    timestamp: str = Field(description="ISO timestamp when error occurred")