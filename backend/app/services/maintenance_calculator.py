"""
Maintenance impact calculation module for financial dashboard.

This module provides functions for calculating lost income due to maintenance blocks
by analyzing historical average daily rates per property.
Enhanced with caching for improved performance.
"""

import logging
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from .date_utils import (
    parse_date_to_date, 
    generate_date_range,
    DateValidationError
)
from .revenue_calculator import (
    calculate_nightly_rate,
    validate_reservation_data,
    RevenueCalculationError
)
from .cache_manager import cached_aggregation, cached_query

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MaintenanceCalculationError(Exception):
    """Custom exception for maintenance calculation errors."""
    pass


def calculate_historical_average_daily_rate(reservations: List, property_id: int, 
                                          exclude_start_date: Optional[str] = None,
                                          exclude_end_date: Optional[str] = None) -> float:
    """
    Calculate historical average daily rate for a specific property.
    
    Args:
        reservations: List of reservation objects
        property_id: Property ID to calculate rate for
        exclude_start_date: Optional start date to exclude from calculation (YYYY-MM-DD)
        exclude_end_date: Optional end date to exclude from calculation (YYYY-MM-DD)
        
    Returns:
        Average daily rate for the property, or 0.0 if no valid data
        
    Raises:
        MaintenanceCalculationError: If calculation fails
    """
    try:
        total_revenue = 0.0
        total_nights = 0
        valid_reservations = 0
        
        for reservation in reservations:
            # Skip if not the target property
            if reservation.property_id != property_id:
                continue
            
            # Validate reservation data
            if not validate_reservation_data(
                getattr(reservation, 'reservation_id', 'unknown'),
                reservation.reservation_revenue,
                reservation.check_in,
                reservation.check_out
            ):
                continue
            
            # Skip reservations that overlap with exclusion period
            if exclude_start_date and exclude_end_date:
                checkin_date = parse_date_to_date(reservation.check_in)
                checkout_date = parse_date_to_date(reservation.check_out)
                exclude_start = parse_date_to_date(exclude_start_date)
                exclude_end = parse_date_to_date(exclude_end_date)
                
                # Check if reservation overlaps with exclusion period
                if not (checkout_date <= exclude_start or checkin_date >= exclude_end):
                    logger.debug(f"Excluding reservation {getattr(reservation, 'reservation_id', 'unknown')} "
                               f"from {reservation.check_in} to {reservation.check_out} "
                               f"due to overlap with exclusion period {exclude_start_date} to {exclude_end_date}")
                    continue
            
            # Calculate nights for this reservation
            try:
                checkin_date = parse_date_to_date(reservation.check_in)
                checkout_date = parse_date_to_date(reservation.check_out)
                nights = (checkout_date - checkin_date).days
                
                # Handle same-day bookings
                if nights == 0:
                    nights = 1
                    logger.warning(f"Same-day booking for reservation {getattr(reservation, 'reservation_id', 'unknown')}, "
                                 f"treating as 1 night")
                
                total_revenue += reservation.reservation_revenue
                total_nights += nights
                valid_reservations += 1
                
            except Exception as e:
                logger.error(f"Error calculating nights for reservation {getattr(reservation, 'reservation_id', 'unknown')}: {e}")
                continue
        
        # Calculate average daily rate
        if total_nights > 0:
            average_rate = total_revenue / total_nights
            logger.info(f"Property {property_id}: Calculated average daily rate ${average_rate:.2f} "
                       f"from {valid_reservations} reservations ({total_nights} nights)")
            return average_rate
        else:
            logger.warning(f"Property {property_id}: No valid historical data found for average daily rate calculation")
            return 0.0
            
    except Exception as e:
        raise MaintenanceCalculationError(f"Error calculating historical average daily rate for property {property_id}: {e}")


def calculate_lost_income_for_maintenance_block(reservations: List, maintenance_block,
                                              fallback_rate: Optional[float] = None) -> float:
    """
    Calculate lost income for a single maintenance block.
    
    Args:
        reservations: List of reservation objects for historical data
        maintenance_block: Maintenance block object with property_id, start_date, end_date, blocked_days
        fallback_rate: Optional fallback rate to use if no historical data exists
        
    Returns:
        Estimated lost income for the maintenance block
        
    Raises:
        MaintenanceCalculationError: If calculation fails
    """
    try:
        property_id = maintenance_block.property_id
        start_date = maintenance_block.start_date
        end_date = maintenance_block.end_date
        blocked_days = maintenance_block.blocked_days
        
        # Calculate historical average daily rate for this property
        # Exclude the maintenance period itself from the calculation
        avg_daily_rate = calculate_historical_average_daily_rate(
            reservations, 
            property_id,
            exclude_start_date=start_date,
            exclude_end_date=end_date
        )
        
        # Use fallback rate if no historical data
        if avg_daily_rate == 0.0 and fallback_rate is not None:
            avg_daily_rate = fallback_rate
            logger.info(f"Property {property_id}: Using fallback rate ${fallback_rate:.2f} "
                       f"for maintenance block {getattr(maintenance_block, 'maintenance_id', 'unknown')}")
        
        # Calculate lost income
        lost_income = avg_daily_rate * blocked_days
        
        logger.info(f"Property {property_id}: Maintenance block from {start_date} to {end_date} "
                   f"({blocked_days} days) - Lost income: ${lost_income:.2f} "
                   f"(${avg_daily_rate:.2f}/day)")
        
        return lost_income
        
    except Exception as e:
        raise MaintenanceCalculationError(f"Error calculating lost income for maintenance block: {e}")


def calculate_portfolio_average_daily_rate(reservations: List) -> float:
    """
    Calculate portfolio-wide average daily rate across all properties.
    
    This can be used as a fallback when individual property data is insufficient.
    
    Args:
        reservations: List of all reservation objects
        
    Returns:
        Portfolio average daily rate
    """
    try:
        total_revenue = 0.0
        total_nights = 0
        
        for reservation in reservations:
            # Validate reservation data
            if not validate_reservation_data(
                getattr(reservation, 'reservation_id', 'unknown'),
                reservation.reservation_revenue,
                reservation.check_in,
                reservation.check_out
            ):
                continue
            
            try:
                checkin_date = parse_date_to_date(reservation.check_in)
                checkout_date = parse_date_to_date(reservation.check_out)
                nights = (checkout_date - checkin_date).days
                
                # Handle same-day bookings
                if nights == 0:
                    nights = 1
                
                total_revenue += reservation.reservation_revenue
                total_nights += nights
                
            except Exception as e:
                logger.error(f"Error processing reservation for portfolio average: {e}")
                continue
        
        if total_nights > 0:
            portfolio_rate = total_revenue / total_nights
            logger.info(f"Portfolio average daily rate: ${portfolio_rate:.2f} from {total_nights} nights")
            return portfolio_rate
        else:
            logger.warning("No valid reservation data found for portfolio average calculation")
            return 0.0
            
    except Exception as e:
        logger.error(f"Error calculating portfolio average daily rate: {e}")
        return 0.0


def calculate_lost_income_by_property(reservations: List, maintenance_blocks: List,
                                    start_date: Optional[str] = None,
                                    end_date: Optional[str] = None,
                                    use_portfolio_fallback: bool = True) -> Dict[int, Dict[str, any]]:
    """
    Calculate lost income aggregated by property.
    
    Args:
        reservations: List of reservation objects for historical data
        maintenance_blocks: List of maintenance block objects
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        use_portfolio_fallback: Whether to use portfolio average as fallback rate
        
    Returns:
        Dictionary mapping property_id to lost income metrics
        
    Raises:
        MaintenanceCalculationError: If calculation fails
    """
    try:
        # Calculate portfolio average as fallback if requested
        portfolio_fallback = None
        if use_portfolio_fallback:
            portfolio_fallback = calculate_portfolio_average_daily_rate(reservations)
        
        property_lost_income = defaultdict(lambda: {
            'total_lost_income': 0.0,
            'total_blocked_days': 0,
            'maintenance_blocks_count': 0,
            'property_name': None,
            'average_daily_rate_used': 0.0
        })
        
        processed_blocks = 0
        
        for maintenance_block in maintenance_blocks:
            try:
                # Apply date filters to maintenance block
                if start_date and maintenance_block.end_date < start_date:
                    continue
                if end_date and maintenance_block.start_date > end_date:
                    continue
                
                # Calculate lost income for this block
                lost_income = calculate_lost_income_for_maintenance_block(
                    reservations, 
                    maintenance_block,
                    fallback_rate=portfolio_fallback
                )
                
                # Get the rate that was used
                avg_rate = calculate_historical_average_daily_rate(
                    reservations,
                    maintenance_block.property_id,
                    exclude_start_date=maintenance_block.start_date,
                    exclude_end_date=maintenance_block.end_date
                )
                if avg_rate == 0.0 and portfolio_fallback is not None:
                    avg_rate = portfolio_fallback
                
                # Add to property totals
                property_id = maintenance_block.property_id
                property_lost_income[property_id]['total_lost_income'] += lost_income
                property_lost_income[property_id]['total_blocked_days'] += maintenance_block.blocked_days
                property_lost_income[property_id]['maintenance_blocks_count'] += 1
                property_lost_income[property_id]['property_name'] = maintenance_block.property_name
                
                # Update average rate (weighted by blocked days)
                current_total_days = property_lost_income[property_id]['total_blocked_days']
                current_avg = property_lost_income[property_id]['average_daily_rate_used']
                
                # Calculate weighted average
                if current_total_days > 0:
                    property_lost_income[property_id]['average_daily_rate_used'] = (
                        (current_avg * (current_total_days - maintenance_block.blocked_days) + 
                         avg_rate * maintenance_block.blocked_days) / current_total_days
                    )
                else:
                    property_lost_income[property_id]['average_daily_rate_used'] = avg_rate
                
                processed_blocks += 1
                
            except Exception as e:
                logger.error(f"Error processing maintenance block {getattr(maintenance_block, 'maintenance_id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Processed {processed_blocks} maintenance blocks for lost income calculation")
        return dict(property_lost_income)
        
    except Exception as e:
        raise MaintenanceCalculationError(f"Error calculating lost income by property: {e}")


@cached_query("lost_income_summary")
def create_lost_income_summary(reservations: List, maintenance_blocks: List,
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> List[Dict[str, any]]:
    """
    Create a summary of lost income by property suitable for API responses.
    
    Args:
        reservations: List of reservation objects for historical data
        maintenance_blocks: List of maintenance block objects
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        
    Returns:
        List of dictionaries with property lost income information
    """
    try:
        # Calculate lost income by property
        property_lost_income = calculate_lost_income_by_property(
            reservations, 
            maintenance_blocks,
            start_date,
            end_date
        )
        
        # Convert to summary format
        summary = []
        for property_id, metrics in property_lost_income.items():
            summary.append({
                'property_id': property_id,
                'property_name': metrics['property_name'],
                'lost_income': metrics['total_lost_income'],
                'blocked_days': metrics['total_blocked_days'],
                'maintenance_blocks_count': metrics['maintenance_blocks_count'],
                'average_daily_rate_used': metrics['average_daily_rate_used']
            })
        
        # Sort by lost income descending
        summary.sort(key=lambda x: x['lost_income'], reverse=True)
        
        return summary
        
    except Exception as e:
        raise MaintenanceCalculationError(f"Error creating lost income summary: {e}")


def validate_maintenance_block_data(maintenance_block) -> bool:
    """
    Validate maintenance block data for lost income calculations.
    
    Args:
        maintenance_block: Maintenance block object
        
    Returns:
        True if valid, False if should be skipped
    """
    try:
        # Check required fields
        if not hasattr(maintenance_block, 'property_id') or maintenance_block.property_id <= 0:
            logger.error(f"Invalid property_id in maintenance block: {getattr(maintenance_block, 'property_id', 'missing')}")
            return False
        
        if not hasattr(maintenance_block, 'blocked_days') or maintenance_block.blocked_days <= 0:
            logger.error(f"Invalid blocked_days in maintenance block: {getattr(maintenance_block, 'blocked_days', 'missing')}")
            return False
        
        # Validate dates
        if not hasattr(maintenance_block, 'start_date') or not hasattr(maintenance_block, 'end_date'):
            logger.error("Missing start_date or end_date in maintenance block")
            return False
        
        try:
            start_date = parse_date_to_date(maintenance_block.start_date)
            end_date = parse_date_to_date(maintenance_block.end_date)
            
            if start_date >= end_date:
                logger.error(f"Invalid date range in maintenance block: {maintenance_block.start_date} to {maintenance_block.end_date}")
                return False
                
        except DateValidationError as e:
            logger.error(f"Date validation failed for maintenance block: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating maintenance block: {e}")
        return False