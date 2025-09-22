"""
Revenue calculation and aggregation module for financial dashboard.

This module provides functions for calculating nightly rates, prorating revenue
across stay dates, and aggregating revenue data for analytics.
Enhanced with caching for improved performance.
"""

import logging
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from .date_utils import (
    calculate_nights, 
    parse_date_to_date, 
    generate_date_range,
    DateValidationError
)
from .cache_manager import cached_aggregation, cached_query

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RevenueCalculationError(Exception):
    """Custom exception for revenue calculation errors."""
    pass


def calculate_nightly_rate(revenue: float, check_in: str, check_out: str) -> float:
    """
    Calculate nightly rate from total reservation revenue and stay dates.
    
    Args:
        revenue: Total reservation revenue
        check_in: Check-in date string in YYYY-MM-DD format
        check_out: Check-out date string in YYYY-MM-DD format
        
    Returns:
        Nightly rate (revenue per night)
        
    Raises:
        RevenueCalculationError: If calculation fails due to invalid inputs
    """
    if revenue < 0:
        raise RevenueCalculationError(f"Revenue cannot be negative: {revenue}")
    
    try:
        nights = calculate_nights(check_in, check_out)
        
        # Handle same-day bookings (0 nights)
        if nights == 0:
            logger.warning(f"Same-day booking detected for revenue ${revenue}: {check_in} to {check_out}")
            # For same-day bookings, treat as 1 night for rate calculation
            return revenue
        
        nightly_rate = revenue / nights
        return nightly_rate
        
    except DateValidationError as e:
        raise RevenueCalculationError(f"Date validation failed: {e}")
    except ZeroDivisionError:
        # This shouldn't happen due to nights check above, but safety net
        raise RevenueCalculationError("Cannot calculate nightly rate: zero nights")
    except Exception as e:
        raise RevenueCalculationError(f"Unexpected error calculating nightly rate: {e}")


def calculate_nights_safe(check_in: str, check_out: str) -> int:
    """
    Safely calculate nights with error handling and logging.
    
    Args:
        check_in: Check-in date string in YYYY-MM-DD format
        check_out: Check-out date string in YYYY-MM-DD format
        
    Returns:
        Number of nights, or 1 for same-day bookings
        
    Raises:
        RevenueCalculationError: If date calculation fails
    """
    try:
        nights = calculate_nights(check_in, check_out)
        
        # Handle same-day bookings
        if nights == 0:
            logger.warning(f"Same-day booking: {check_in} to {check_out}, treating as 1 night")
            return 1
        
        return nights
        
    except DateValidationError as e:
        raise RevenueCalculationError(f"Error calculating nights: {e}")


def prorate_revenue_across_dates(revenue: float, check_in: str, check_out: str) -> Dict[str, float]:
    """
    Prorate reservation revenue across all stay dates.
    
    For a reservation from 2024-01-01 to 2024-01-03 (2 nights), the revenue
    is split equally across 2024-01-01 and 2024-01-02.
    
    Args:
        revenue: Total reservation revenue
        check_in: Check-in date string in YYYY-MM-DD format
        check_out: Check-out date string in YYYY-MM-DD format
        
    Returns:
        Dictionary mapping date strings to daily revenue amounts
        
    Raises:
        RevenueCalculationError: If prorating fails
    """
    if revenue < 0:
        raise RevenueCalculationError(f"Revenue cannot be negative: {revenue}")
    
    try:
        # Calculate nightly rate
        nightly_rate = calculate_nightly_rate(revenue, check_in, check_out)
        
        # Generate stay dates (excluding checkout date)
        checkin_date = parse_date_to_date(check_in)
        checkout_date = parse_date_to_date(check_out)
        
        daily_revenue = {}
        current_date = checkin_date
        
        # Distribute revenue across stay dates
        while current_date < checkout_date:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_revenue[date_str] = nightly_rate
            current_date += timedelta(days=1)
        
        # Handle same-day bookings
        if not daily_revenue:
            # Same-day booking: assign all revenue to check-in date
            checkin_str = checkin_date.strftime('%Y-%m-%d')
            daily_revenue[checkin_str] = revenue
            logger.warning(f"Same-day booking revenue ${revenue} assigned to {checkin_str}")
        
        return daily_revenue
        
    except RevenueCalculationError:
        # Re-raise revenue calculation errors
        raise
    except Exception as e:
        raise RevenueCalculationError(f"Error prorating revenue: {e}")


def validate_reservation_data(reservation_id: int, revenue: float, check_in: str, check_out: str) -> bool:
    """
    Validate reservation data for revenue calculations.
    
    Args:
        reservation_id: Reservation ID for logging
        revenue: Reservation revenue
        check_in: Check-in date string
        check_out: Check-out date string
        
    Returns:
        True if valid, False if should be skipped
    """
    try:
        # Check revenue
        if revenue < 0:
            logger.error(f"Reservation {reservation_id}: Negative revenue {revenue}")
            return False
        
        # Check dates
        calculate_nights(check_in, check_out)
        return True
        
    except DateValidationError as e:
        logger.error(f"Reservation {reservation_id}: Invalid dates - {e}")
        return False
    except Exception as e:
        logger.error(f"Reservation {reservation_id}: Validation error - {e}")
        return False


def calculate_reservation_metrics(reservations: List) -> Dict[str, float]:
    """
    Calculate aggregate metrics for a list of reservations.
    
    Args:
        reservations: List of reservation objects with revenue, check_in, check_out
        
    Returns:
        Dictionary with total_revenue, total_nights, average_nightly_rate
    """
    total_revenue = 0.0
    total_nights = 0
    valid_reservations = 0
    
    for reservation in reservations:
        try:
            # Validate reservation
            if not validate_reservation_data(
                getattr(reservation, 'reservation_id', 'unknown'),
                reservation.reservation_revenue,
                reservation.check_in,
                reservation.check_out
            ):
                continue
            
            # Calculate nights and add to totals
            nights = calculate_nights_safe(reservation.check_in, reservation.check_out)
            total_revenue += reservation.reservation_revenue
            total_nights += nights
            valid_reservations += 1
            
        except Exception as e:
            logger.error(f"Error processing reservation: {e}")
            continue
    
    # Calculate average nightly rate
    average_nightly_rate = total_revenue / total_nights if total_nights > 0 else 0.0
    
    return {
        'total_revenue': total_revenue,
        'total_nights': total_nights,
        'average_nightly_rate': average_nightly_rate,
        'valid_reservations': valid_reservations
    }


@cached_aggregation("daily_revenue")
def aggregate_daily_revenue(reservations: List, start_date: Optional[str] = None, 
                          end_date: Optional[str] = None) -> Dict[str, float]:
    """
    Aggregate revenue by date across all reservations.
    
    Prorates each reservation's revenue across its stay dates and sums
    by date to create daily revenue totals.
    
    Args:
        reservations: List of reservation objects
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        
    Returns:
        Dictionary mapping date strings to total revenue for that date
        
    Raises:
        RevenueCalculationError: If aggregation fails
    """
    daily_totals = defaultdict(float)
    processed_reservations = 0
    
    for reservation in reservations:
        try:
            # Validate reservation
            if not validate_reservation_data(
                getattr(reservation, 'reservation_id', 'unknown'),
                reservation.reservation_revenue,
                reservation.check_in,
                reservation.check_out
            ):
                continue
            
            # Prorate revenue across stay dates
            daily_revenue = prorate_revenue_across_dates(
                reservation.reservation_revenue,
                reservation.check_in,
                reservation.check_out
            )
            
            # Add to daily totals
            for date_str, revenue in daily_revenue.items():
                # Apply date filters if provided
                if start_date and date_str < start_date:
                    continue
                if end_date and date_str > end_date:
                    continue
                
                daily_totals[date_str] += revenue
            
            processed_reservations += 1
            
        except Exception as e:
            logger.error(f"Error processing reservation for daily aggregation: {e}")
            continue
    
    logger.info(f"Processed {processed_reservations} reservations for daily revenue aggregation")
    return dict(daily_totals)


@cached_aggregation("property_revenue")
def aggregate_revenue_by_property(reservations: List, start_date: Optional[str] = None,
                                end_date: Optional[str] = None) -> Dict[int, Dict[str, float]]:
    """
    Aggregate revenue by property ID.
    
    Args:
        reservations: List of reservation objects
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        
    Returns:
        Dictionary mapping property_id to revenue metrics
        
    Raises:
        RevenueCalculationError: If aggregation fails
    """
    property_totals = defaultdict(lambda: {
        'total_revenue': 0.0,
        'total_nights': 0,
        'reservation_count': 0,
        'property_name': None
    })
    
    for reservation in reservations:
        try:
            # Validate reservation
            if not validate_reservation_data(
                getattr(reservation, 'reservation_id', 'unknown'),
                reservation.reservation_revenue,
                reservation.check_in,
                reservation.check_out
            ):
                continue
            
            # Apply date filters to check-in date
            if start_date and reservation.check_in < start_date:
                continue
            if end_date and reservation.check_in > end_date:
                continue
            
            # Calculate nights
            nights = calculate_nights_safe(reservation.check_in, reservation.check_out)
            
            # Add to property totals
            property_id = reservation.property_id
            property_totals[property_id]['total_revenue'] += reservation.reservation_revenue
            property_totals[property_id]['total_nights'] += nights
            property_totals[property_id]['reservation_count'] += 1
            property_totals[property_id]['property_name'] = reservation.property_name
            
        except Exception as e:
            logger.error(f"Error processing reservation for property aggregation: {e}")
            continue
    
    # Calculate average nightly rates
    for property_id, metrics in property_totals.items():
        if metrics['total_nights'] > 0:
            metrics['average_nightly_rate'] = metrics['total_revenue'] / metrics['total_nights']
        else:
            metrics['average_nightly_rate'] = 0.0
    
    return dict(property_totals)


def aggregate_daily_revenue_by_property(reservations: List, start_date: Optional[str] = None,
                                      end_date: Optional[str] = None) -> Dict[int, Dict[str, float]]:
    """
    Aggregate daily revenue by property ID.
    
    Creates a nested structure: property_id -> date -> revenue
    
    Args:
        reservations: List of reservation objects
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        
    Returns:
        Dictionary mapping property_id to daily revenue dictionaries
    """
    property_daily_revenue = defaultdict(lambda: defaultdict(float))
    
    for reservation in reservations:
        try:
            # Validate reservation
            if not validate_reservation_data(
                getattr(reservation, 'reservation_id', 'unknown'),
                reservation.reservation_revenue,
                reservation.check_in,
                reservation.check_out
            ):
                continue
            
            # Prorate revenue across stay dates
            daily_revenue = prorate_revenue_across_dates(
                reservation.reservation_revenue,
                reservation.check_in,
                reservation.check_out
            )
            
            # Add to property daily totals
            property_id = reservation.property_id
            for date_str, revenue in daily_revenue.items():
                # Apply date filters if provided
                if start_date and date_str < start_date:
                    continue
                if end_date and date_str > end_date:
                    continue
                
                property_daily_revenue[property_id][date_str] += revenue
            
        except Exception as e:
            logger.error(f"Error processing reservation for property daily aggregation: {e}")
            continue
    
    # Convert defaultdicts to regular dicts
    result = {}
    for property_id, daily_data in property_daily_revenue.items():
        result[property_id] = dict(daily_data)
    
    return result


@cached_query("revenue_timeline")
def create_revenue_timeline(reservations: List, start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> List[Dict[str, any]]:
    """
    Create a timeline of daily revenue data suitable for API responses.
    
    Args:
        reservations: List of reservation objects
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        
    Returns:
        List of dictionaries with date and revenue information
    """
    # Get daily aggregated revenue
    daily_revenue = aggregate_daily_revenue(reservations, start_date, end_date)
    
    # Convert to timeline format
    timeline = []
    for date_str in sorted(daily_revenue.keys()):
        timeline.append({
            'date': date_str,
            'total_revenue': daily_revenue[date_str]
        })
    
    return timeline


@cached_query("property_revenue_summary")
def create_property_revenue_summary(reservations: List, start_date: Optional[str] = None,
                                  end_date: Optional[str] = None) -> List[Dict[str, any]]:
    """
    Create a summary of revenue by property suitable for API responses.
    
    Args:
        reservations: List of reservation objects
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        
    Returns:
        List of dictionaries with property revenue information
    """
    # Get property aggregated revenue
    property_revenue = aggregate_revenue_by_property(reservations, start_date, end_date)
    
    # Convert to summary format
    summary = []
    for property_id, metrics in property_revenue.items():
        summary.append({
            'property_id': property_id,
            'property_name': metrics['property_name'],
            'total_revenue': metrics['total_revenue'],
            'total_nights': metrics['total_nights'],
            'reservation_count': metrics['reservation_count'],
            'average_nightly_rate': metrics['average_nightly_rate']
        })
    
    # Sort by total revenue descending
    summary.sort(key=lambda x: x['total_revenue'], reverse=True)
    
    return summary