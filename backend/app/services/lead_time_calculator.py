"""
Lead time calculation and statistics module for financial dashboard.

This module provides functions for calculating booking lead times, computing
statistical measures (median, p90), and creating histogram distribution data.
"""

import logging
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import statistics

from .date_utils import (
    calculate_days_between,
    parse_date_to_date,
    DateValidationError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LeadTimeCalculationError(Exception):
    """Custom exception for lead time calculation errors."""
    pass


def calculate_lead_time(reservation_date: str, check_in: str) -> int:
    """
    Calculate lead time in days between reservation date and check-in date.
    
    Args:
        reservation_date: Reservation booking date string in YYYY-MM-DD format
        check_in: Check-in date string in YYYY-MM-DD format
        
    Returns:
        Lead time in days (can be negative for same-day or past bookings)
        
    Raises:
        LeadTimeCalculationError: If calculation fails due to invalid inputs
    """
    try:
        # Parse dates manually to handle negative lead times
        reservation_dt = parse_date_to_date(reservation_date)
        checkin_dt = parse_date_to_date(check_in)
        
        # Calculate lead time (can be negative)
        lead_time_days = (checkin_dt - reservation_dt).days
        
        # Log warning for negative lead times (booking after check-in)
        if lead_time_days < 0:
            logger.warning(f"Negative lead time detected: reservation {reservation_date}, check-in {check_in}")
        
        # Log warning for same-day bookings
        if lead_time_days == 0:
            logger.warning(f"Same-day booking detected: reservation {reservation_date}, check-in {check_in}")
        
        return lead_time_days
        
    except DateValidationError as e:
        raise LeadTimeCalculationError(f"Date validation failed: {e}")
    except Exception as e:
        raise LeadTimeCalculationError(f"Unexpected error calculating lead time: {e}")


def validate_reservation_for_lead_time(reservation_id: int, reservation_date: str, check_in: str) -> bool:
    """
    Validate reservation data for lead time calculations.
    
    Args:
        reservation_id: Reservation ID for logging
        reservation_date: Reservation booking date string
        check_in: Check-in date string
        
    Returns:
        True if valid, False if should be skipped
    """
    try:
        # Check if dates are valid
        calculate_lead_time(reservation_date, check_in)
        return True
        
    except LeadTimeCalculationError as e:
        logger.error(f"Reservation {reservation_id}: Invalid data for lead time - {e}")
        return False
    except Exception as e:
        logger.error(f"Reservation {reservation_id}: Validation error - {e}")
        return False


def calculate_lead_time_statistics(reservations: List, start_date: Optional[str] = None,
                                 end_date: Optional[str] = None, 
                                 property_ids: Optional[List[int]] = None) -> Dict[str, float]:
    """
    Calculate lead time statistics (median, p90) for a list of reservations.
    
    Args:
        reservations: List of reservation objects with reservation_date and check_in
        start_date: Optional start date filter for check-in dates (YYYY-MM-DD)
        end_date: Optional end date filter for check-in dates (YYYY-MM-DD)
        property_ids: Optional list of property IDs to filter by
        
    Returns:
        Dictionary with median_days, p90_days, count, min_days, max_days
        
    Raises:
        LeadTimeCalculationError: If calculation fails
    """
    lead_times = []
    processed_reservations = 0
    
    for reservation in reservations:
        try:
            # Apply property filter
            if property_ids and reservation.property_id not in property_ids:
                continue
            
            # Apply date filters to check-in date
            if start_date and reservation.check_in < start_date:
                continue
            if end_date and reservation.check_in > end_date:
                continue
            
            # Validate reservation
            if not validate_reservation_for_lead_time(
                getattr(reservation, 'reservation_id', 'unknown'),
                reservation.reservation_date,
                reservation.check_in
            ):
                continue
            
            # Calculate lead time
            lead_time = calculate_lead_time(reservation.reservation_date, reservation.check_in)
            lead_times.append(lead_time)
            processed_reservations += 1
            
        except Exception as e:
            logger.error(f"Error processing reservation for lead time statistics: {e}")
            continue
    
    if not lead_times:
        logger.warning("No valid reservations found for lead time statistics")
        return {
            'median_days': 0.0,
            'p90_days': 0.0,
            'count': 0,
            'min_days': 0.0,
            'max_days': 0.0
        }
    
    # Calculate statistics
    lead_times.sort()
    
    try:
        median_days = statistics.median(lead_times)
        
        # Calculate 90th percentile
        p90_index = int(0.9 * len(lead_times))
        if p90_index >= len(lead_times):
            p90_index = len(lead_times) - 1
        p90_days = lead_times[p90_index]
        
        min_days = min(lead_times)
        max_days = max(lead_times)
        
        logger.info(f"Calculated lead time statistics for {processed_reservations} reservations")
        
        return {
            'median_days': float(median_days),
            'p90_days': float(p90_days),
            'count': len(lead_times),
            'min_days': float(min_days),
            'max_days': float(max_days)
        }
        
    except Exception as e:
        raise LeadTimeCalculationError(f"Error calculating statistics: {e}")


def create_lead_time_histogram(reservations: List, start_date: Optional[str] = None,
                             end_date: Optional[str] = None,
                             property_ids: Optional[List[int]] = None,
                             bin_size: int = 7) -> List[Dict[str, int]]:
    """
    Create histogram distribution data for lead times.
    
    Args:
        reservations: List of reservation objects
        start_date: Optional start date filter for check-in dates (YYYY-MM-DD)
        end_date: Optional end date filter for check-in dates (YYYY-MM-DD)
        property_ids: Optional list of property IDs to filter by
        bin_size: Size of histogram bins in days (default: 7 for weekly bins)
        
    Returns:
        List of dictionaries with bin_start, bin_end, count
        
    Raises:
        LeadTimeCalculationError: If histogram creation fails
    """
    lead_times = []
    
    for reservation in reservations:
        try:
            # Apply property filter
            if property_ids and reservation.property_id not in property_ids:
                continue
            
            # Apply date filters to check-in date
            if start_date and reservation.check_in < start_date:
                continue
            if end_date and reservation.check_in > end_date:
                continue
            
            # Validate reservation
            if not validate_reservation_for_lead_time(
                getattr(reservation, 'reservation_id', 'unknown'),
                reservation.reservation_date,
                reservation.check_in
            ):
                continue
            
            # Calculate lead time
            lead_time = calculate_lead_time(reservation.reservation_date, reservation.check_in)
            lead_times.append(lead_time)
            
        except Exception as e:
            logger.error(f"Error processing reservation for histogram: {e}")
            continue
    
    if not lead_times:
        logger.warning("No valid reservations found for lead time histogram")
        return []
    
    try:
        # Determine histogram range
        min_lead_time = min(lead_times)
        max_lead_time = max(lead_times)
        
        # Create bins
        bins = defaultdict(int)
        
        for lead_time in lead_times:
            # Calculate which bin this lead time falls into
            bin_start = (lead_time // bin_size) * bin_size
            bins[bin_start] += 1
        
        # Convert to histogram format
        histogram = []
        for bin_start in sorted(bins.keys()):
            bin_end = bin_start + bin_size - 1
            histogram.append({
                'bin_start': bin_start,
                'bin_end': bin_end,
                'count': bins[bin_start],
                'label': f"{bin_start}-{bin_end} days"
            })
        
        logger.info(f"Created histogram with {len(histogram)} bins for {len(lead_times)} lead times")
        return histogram
        
    except Exception as e:
        raise LeadTimeCalculationError(f"Error creating histogram: {e}")


def calculate_lead_time_by_property(reservations: List, start_date: Optional[str] = None,
                                  end_date: Optional[str] = None) -> Dict[int, Dict[str, float]]:
    """
    Calculate lead time statistics grouped by property.
    
    Args:
        reservations: List of reservation objects
        start_date: Optional start date filter for check-in dates (YYYY-MM-DD)
        end_date: Optional end date filter for check-in dates (YYYY-MM-DD)
        
    Returns:
        Dictionary mapping property_id to lead time statistics
    """
    property_lead_times = defaultdict(list)
    property_names = {}
    
    for reservation in reservations:
        try:
            # Apply date filters to check-in date
            if start_date and reservation.check_in < start_date:
                continue
            if end_date and reservation.check_in > end_date:
                continue
            
            # Validate reservation
            if not validate_reservation_for_lead_time(
                getattr(reservation, 'reservation_id', 'unknown'),
                reservation.reservation_date,
                reservation.check_in
            ):
                continue
            
            # Calculate lead time
            lead_time = calculate_lead_time(reservation.reservation_date, reservation.check_in)
            
            property_id = reservation.property_id
            property_lead_times[property_id].append(lead_time)
            property_names[property_id] = reservation.property_name
            
        except Exception as e:
            logger.error(f"Error processing reservation for property lead times: {e}")
            continue
    
    # Calculate statistics for each property
    property_stats = {}
    
    for property_id, lead_times in property_lead_times.items():
        if not lead_times:
            continue
        
        try:
            lead_times.sort()
            
            median_days = statistics.median(lead_times)
            
            # Calculate 90th percentile
            p90_index = int(0.9 * len(lead_times))
            if p90_index >= len(lead_times):
                p90_index = len(lead_times) - 1
            p90_days = lead_times[p90_index]
            
            property_stats[property_id] = {
                'property_name': property_names[property_id],
                'median_days': float(median_days),
                'p90_days': float(p90_days),
                'count': len(lead_times),
                'min_days': float(min(lead_times)),
                'max_days': float(max(lead_times)),
                'average_days': float(sum(lead_times) / len(lead_times))
            }
            
        except Exception as e:
            logger.error(f"Error calculating statistics for property {property_id}: {e}")
            continue
    
    return property_stats


def create_lead_time_summary(reservations: List, start_date: Optional[str] = None,
                           end_date: Optional[str] = None,
                           property_ids: Optional[List[int]] = None) -> Dict[str, any]:
    """
    Create a comprehensive lead time analysis summary suitable for API responses.
    
    Args:
        reservations: List of reservation objects
        start_date: Optional start date filter for check-in dates (YYYY-MM-DD)
        end_date: Optional end date filter for check-in dates (YYYY-MM-DD)
        property_ids: Optional list of property IDs to filter by
        
    Returns:
        Dictionary with statistics, histogram, and property breakdown
    """
    try:
        # Calculate overall statistics
        statistics_data = calculate_lead_time_statistics(
            reservations, start_date, end_date, property_ids
        )
        
        # Create histogram
        histogram_data = create_lead_time_histogram(
            reservations, start_date, end_date, property_ids
        )
        
        # Calculate property breakdown (if not filtering by specific properties)
        property_breakdown = {}
        if not property_ids:
            property_breakdown = calculate_lead_time_by_property(
                reservations, start_date, end_date
            )
        
        return {
            'statistics': statistics_data,
            'histogram': histogram_data,
            'property_breakdown': property_breakdown
        }
        
    except Exception as e:
        raise LeadTimeCalculationError(f"Error creating lead time summary: {e}")