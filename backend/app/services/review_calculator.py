"""
Review trend analysis and aggregation module for financial dashboard.

This module provides functions for aggregating reviews by month and property,
calculating monthly average ratings and review counts, and handling months
with no reviews for analytics.
"""

import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from .date_utils import (
    parse_date_to_date, 
    get_month_year,
    DateValidationError,
    DateParsingError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReviewCalculationError(Exception):
    """Custom exception for review calculation errors."""
    pass


def validate_review_data(review_id: int, rating: float, review_date: str) -> bool:
    """
    Validate review data for aggregation calculations.
    
    Args:
        review_id: Review ID for logging
        rating: Review rating value
        review_date: Review date string
        
    Returns:
        True if valid, False if should be skipped
    """
    try:
        # Check rating range (assuming 1-5 scale based on sample data)
        if not isinstance(rating, (int, float)):
            logger.error(f"Review {review_id}: Rating must be numeric, got {type(rating)}")
            return False
            
        if rating < 1.0 or rating > 5.0:
            logger.error(f"Review {review_id}: Rating {rating} outside valid range (1-5)")
            return False
        
        # Check date format
        parse_date_to_date(review_date)
        return True
        
    except DateParsingError as e:
        logger.error(f"Review {review_id}: Invalid date - {e}")
        return False
    except Exception as e:
        logger.error(f"Review {review_id}: Validation error - {e}")
        return False


def aggregate_reviews_by_month(reviews: List, start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> Dict[str, Dict[str, float]]:
    """
    Aggregate reviews by month, calculating average ratings and review counts.
    
    Args:
        reviews: List of review objects with rating, review_date, property_id
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        
    Returns:
        Dictionary mapping month strings (YYYY-MM) to aggregated metrics:
        {
            'YYYY-MM': {
                'avg_rating': float,
                'review_count': int,
                'total_rating_sum': float  # for debugging
            }
        }
        
    Raises:
        ReviewCalculationError: If aggregation fails
    """
    monthly_data = defaultdict(lambda: {
        'rating_sum': 0.0,
        'review_count': 0
    })
    
    processed_reviews = 0
    
    for review in reviews:
        try:
            # Validate review data
            review_id = getattr(review, 'review_id', 'unknown')
            if not validate_review_data(review_id, review.rating, review.review_date):
                continue
            
            # Apply date filters
            if start_date and review.review_date < start_date:
                continue
            if end_date and review.review_date > end_date:
                continue
            
            # Get month-year string
            month_key = get_month_year(review.review_date)
            
            # Add to monthly aggregation
            monthly_data[month_key]['rating_sum'] += review.rating
            monthly_data[month_key]['review_count'] += 1
            
            processed_reviews += 1
            
        except Exception as e:
            logger.error(f"Error processing review for monthly aggregation: {e}")
            continue
    
    # Calculate average ratings
    result = {}
    for month_key, data in monthly_data.items():
        if data['review_count'] > 0:
            avg_rating = data['rating_sum'] / data['review_count']
            result[month_key] = {
                'avg_rating': round(avg_rating, 2),
                'review_count': data['review_count'],
                'total_rating_sum': data['rating_sum']
            }
    
    logger.info(f"Processed {processed_reviews} reviews for monthly aggregation")
    logger.info(f"Generated data for {len(result)} months")
    
    return result


def aggregate_reviews_by_month_and_property(reviews: List, start_date: Optional[str] = None,
                                          end_date: Optional[str] = None) -> Dict[int, Dict[str, Dict[str, float]]]:
    """
    Aggregate reviews by month and property ID.
    
    Args:
        reviews: List of review objects with rating, review_date, property_id
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        
    Returns:
        Dictionary mapping property_id to monthly data:
        {
            property_id: {
                'YYYY-MM': {
                    'avg_rating': float,
                    'review_count': int
                }
            }
        }
    """
    property_monthly_data = defaultdict(lambda: defaultdict(lambda: {
        'rating_sum': 0.0,
        'review_count': 0
    }))
    
    processed_reviews = 0
    
    for review in reviews:
        try:
            # Validate review data
            review_id = getattr(review, 'review_id', 'unknown')
            if not validate_review_data(review_id, review.rating, review.review_date):
                continue
            
            # Apply date filters
            if start_date and review.review_date < start_date:
                continue
            if end_date and review.review_date > end_date:
                continue
            
            # Get month-year string
            month_key = get_month_year(review.review_date)
            property_id = review.property_id
            
            # Add to property monthly aggregation
            property_monthly_data[property_id][month_key]['rating_sum'] += review.rating
            property_monthly_data[property_id][month_key]['review_count'] += 1
            
            processed_reviews += 1
            
        except Exception as e:
            logger.error(f"Error processing review for property monthly aggregation: {e}")
            continue
    
    # Calculate average ratings for each property and month
    result = {}
    for property_id, monthly_data in property_monthly_data.items():
        result[property_id] = {}
        for month_key, data in monthly_data.items():
            if data['review_count'] > 0:
                avg_rating = data['rating_sum'] / data['review_count']
                result[property_id][month_key] = {
                    'avg_rating': round(avg_rating, 2),
                    'review_count': data['review_count']
                }
    
    logger.info(f"Processed {processed_reviews} reviews for property monthly aggregation")
    logger.info(f"Generated data for {len(result)} properties")
    
    return result


def aggregate_reviews_by_property(reviews: List, start_date: Optional[str] = None,
                                end_date: Optional[str] = None) -> Dict[int, Dict[str, any]]:
    """
    Aggregate reviews by property ID for overall property statistics.
    
    Args:
        reviews: List of review objects with rating, review_date, property_id
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        
    Returns:
        Dictionary mapping property_id to aggregated metrics:
        {
            property_id: {
                'avg_rating': float,
                'review_count': int,
                'property_name': str,
                'earliest_review': str,
                'latest_review': str
            }
        }
    """
    property_data = defaultdict(lambda: {
        'rating_sum': 0.0,
        'review_count': 0,
        'property_name': None,
        'review_dates': []
    })
    
    processed_reviews = 0
    
    for review in reviews:
        try:
            # Validate review data
            review_id = getattr(review, 'review_id', 'unknown')
            if not validate_review_data(review_id, review.rating, review.review_date):
                continue
            
            # Apply date filters
            if start_date and review.review_date < start_date:
                continue
            if end_date and review.review_date > end_date:
                continue
            
            property_id = review.property_id
            
            # Add to property aggregation
            property_data[property_id]['rating_sum'] += review.rating
            property_data[property_id]['review_count'] += 1
            property_data[property_id]['property_name'] = getattr(review, 'property_name', f'Property {property_id}')
            property_data[property_id]['review_dates'].append(review.review_date)
            
            processed_reviews += 1
            
        except Exception as e:
            logger.error(f"Error processing review for property aggregation: {e}")
            continue
    
    # Calculate final metrics
    result = {}
    for property_id, data in property_data.items():
        if data['review_count'] > 0:
            avg_rating = data['rating_sum'] / data['review_count']
            review_dates = sorted(data['review_dates'])
            
            result[property_id] = {
                'avg_rating': round(avg_rating, 2),
                'review_count': data['review_count'],
                'property_name': data['property_name'],
                'earliest_review': review_dates[0] if review_dates else None,
                'latest_review': review_dates[-1] if review_dates else None
            }
    
    logger.info(f"Processed {processed_reviews} reviews for property aggregation")
    logger.info(f"Generated data for {len(result)} properties")
    
    return result


def create_monthly_review_timeline(reviews: List, start_date: Optional[str] = None,
                                 end_date: Optional[str] = None) -> List[Dict[str, any]]:
    """
    Create a timeline of monthly review data suitable for API responses.
    
    Args:
        reviews: List of review objects
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        
    Returns:
        List of dictionaries with month and review information, sorted by month
    """
    # Get monthly aggregated reviews
    monthly_reviews = aggregate_reviews_by_month(reviews, start_date, end_date)
    
    # Convert to timeline format
    timeline = []
    for month_key in sorted(monthly_reviews.keys()):
        data = monthly_reviews[month_key]
        timeline.append({
            'month': month_key,
            'avg_rating': data['avg_rating'],
            'review_count': data['review_count']
        })
    
    return timeline


def create_property_review_summary(reviews: List, start_date: Optional[str] = None,
                                 end_date: Optional[str] = None) -> List[Dict[str, any]]:
    """
    Create a summary of reviews by property suitable for API responses.
    
    Args:
        reviews: List of review objects
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        
    Returns:
        List of dictionaries with property review information
    """
    # Get property aggregated reviews
    property_reviews = aggregate_reviews_by_property(reviews, start_date, end_date)
    
    # Convert to summary format
    summary = []
    for property_id, data in property_reviews.items():
        summary.append({
            'property_id': property_id,
            'property_name': data['property_name'],
            'avg_rating': data['avg_rating'],
            'review_count': data['review_count'],
            'earliest_review': data['earliest_review'],
            'latest_review': data['latest_review']
        })
    
    # Sort by review count descending
    summary.sort(key=lambda x: x['review_count'], reverse=True)
    
    return summary


def fill_missing_months(monthly_data: Dict[str, Dict[str, any]], 
                       start_month: str, end_month: str) -> Dict[str, Dict[str, any]]:
    """
    Fill in missing months with zero values between start and end months.
    
    Args:
        monthly_data: Dictionary of monthly review data
        start_month: Start month in YYYY-MM format
        end_month: End month in YYYY-MM format
        
    Returns:
        Dictionary with all months filled in, missing months have zero values
    """
    try:
        # Parse start and end months
        start_date = datetime.strptime(start_month, '%Y-%m').date()
        end_date = datetime.strptime(end_month, '%Y-%m').date()
        
        filled_data = {}
        current_date = start_date
        
        while current_date <= end_date:
            month_key = current_date.strftime('%Y-%m')
            
            if month_key in monthly_data:
                filled_data[month_key] = monthly_data[month_key]
            else:
                # Fill missing month with zero values
                filled_data[month_key] = {
                    'avg_rating': 0.0,
                    'review_count': 0
                }
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return filled_data
        
    except Exception as e:
        logger.error(f"Error filling missing months: {e}")
        return monthly_data


def get_review_statistics(reviews: List) -> Dict[str, any]:
    """
    Calculate overall statistics for a list of reviews.
    
    Args:
        reviews: List of review objects
        
    Returns:
        Dictionary with review statistics
    """
    if not reviews:
        return {
            'total_reviews': 0,
            'avg_rating': 0.0,
            'min_rating': None,
            'max_rating': None,
            'rating_distribution': {}
        }
    
    valid_reviews = []
    ratings = []
    
    for review in reviews:
        try:
            review_id = getattr(review, 'review_id', 'unknown')
            if validate_review_data(review_id, review.rating, review.review_date):
                valid_reviews.append(review)
                ratings.append(review.rating)
        except Exception as e:
            logger.warning(f"Skipping invalid review in statistics: {e}")
    
    if not ratings:
        return {
            'total_reviews': 0,
            'avg_rating': 0.0,
            'min_rating': None,
            'max_rating': None,
            'rating_distribution': {}
        }
    
    # Calculate rating distribution
    rating_distribution = defaultdict(int)
    for rating in ratings:
        # Round to nearest 0.5 for distribution
        rounded_rating = round(rating * 2) / 2
        rating_distribution[rounded_rating] += 1
    
    return {
        'total_reviews': len(valid_reviews),
        'avg_rating': round(sum(ratings) / len(ratings), 2),
        'min_rating': min(ratings),
        'max_rating': max(ratings),
        'rating_distribution': dict(rating_distribution)
    }