"""
Date parsing and validation utilities for financial dashboard.

This module provides utilities for parsing dates, handling timezones,
validating date ranges, and calculating nights between dates.
"""

import logging
from datetime import datetime, date, timedelta
from typing import Optional, Tuple, List
import pytz
from zoneinfo import ZoneInfo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default timezone for the application
DEFAULT_TIMEZONE = "UTC"


class DateParsingError(Exception):
    """Custom exception for date parsing errors."""
    pass


class DateValidationError(Exception):
    """Custom exception for date validation errors."""
    pass


def parse_date_string(date_str: str, timezone: Optional[str] = None) -> datetime:
    """
    Parse a date string in YYYY-MM-DD format to datetime object.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        timezone: Optional timezone string (e.g., 'UTC', 'America/New_York')
                 If None, uses DEFAULT_TIMEZONE
        
    Returns:
        datetime object with timezone information
        
    Raises:
        DateParsingError: If date string cannot be parsed
    """
    if not date_str:
        raise DateParsingError("Date string cannot be empty")
    
    if not isinstance(date_str, str):
        raise DateParsingError(f"Date must be a string, got {type(date_str)}")
    
    try:
        # Parse the date string
        parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Add timezone information
        tz = timezone or DEFAULT_TIMEZONE
        if tz == "UTC":
            timezone_obj = pytz.UTC
        else:
            try:
                timezone_obj = ZoneInfo(tz)
            except Exception:
                # Fallback to pytz for older timezone names
                timezone_obj = pytz.timezone(tz)
        
        # Localize the datetime
        if hasattr(timezone_obj, 'localize'):
            # pytz timezone
            localized_date = timezone_obj.localize(parsed_date)
        else:
            # zoneinfo timezone
            localized_date = parsed_date.replace(tzinfo=timezone_obj)
        
        return localized_date
        
    except ValueError as e:
        raise DateParsingError(f"Invalid date format '{date_str}'. Expected YYYY-MM-DD: {e}")
    except Exception as e:
        raise DateParsingError(f"Error parsing date '{date_str}': {e}")


def parse_date_to_date(date_str: str) -> date:
    """
    Parse a date string to a date object (without timezone).
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        date object
        
    Raises:
        DateParsingError: If date string cannot be parsed
    """
    if not date_str:
        raise DateParsingError("Date string cannot be empty")
    
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError as e:
        raise DateParsingError(f"Invalid date format '{date_str}'. Expected YYYY-MM-DD: {e}")


def validate_date_range(start_date: str, end_date: str) -> Tuple[date, date]:
    """
    Validate that start_date is before or equal to end_date.
    
    Args:
        start_date: Start date string in YYYY-MM-DD format
        end_date: End date string in YYYY-MM-DD format
        
    Returns:
        Tuple of (start_date, end_date) as date objects
        
    Raises:
        DateValidationError: If date range is invalid
    """
    try:
        start = parse_date_to_date(start_date)
        end = parse_date_to_date(end_date)
        
        if start > end:
            raise DateValidationError(
                f"Start date ({start_date}) must be before or equal to end date ({end_date})"
            )
        
        return start, end
        
    except DateParsingError as e:
        raise DateValidationError(f"Date range validation failed: {e}")


def calculate_nights(check_in: str, check_out: str) -> int:
    """
    Calculate the number of nights between check-in and check-out dates.
    
    Args:
        check_in: Check-in date string in YYYY-MM-DD format
        check_out: Check-out date string in YYYY-MM-DD format
        
    Returns:
        Number of nights (non-negative integer)
        
    Raises:
        DateValidationError: If dates are invalid or check_out is before check_in
    """
    try:
        checkin_date = parse_date_to_date(check_in)
        checkout_date = parse_date_to_date(check_out)
        
        if checkout_date < checkin_date:
            raise DateValidationError(
                f"Check-out date ({check_out}) cannot be before check-in date ({check_in})"
            )
        
        nights = (checkout_date - checkin_date).days
        
        # Log warning for same-day bookings
        if nights == 0:
            logger.warning(f"Same-day booking detected: {check_in} to {check_out}")
        
        return nights
        
    except DateParsingError as e:
        raise DateValidationError(f"Error calculating nights: {e}")


def calculate_days_between(start_date: str, end_date: str, inclusive: bool = True) -> int:
    """
    Calculate the number of days between two dates.
    
    Args:
        start_date: Start date string in YYYY-MM-DD format
        end_date: End date string in YYYY-MM-DD format
        inclusive: If True, includes both start and end dates in count.
                  If False, excludes end date (like hotel nights calculation).
        
    Returns:
        Number of days (positive integer)
        
    Raises:
        DateValidationError: If dates are invalid or end_date is before start_date
    """
    try:
        start = parse_date_to_date(start_date)
        end = parse_date_to_date(end_date)
        
        if end < start:
            raise DateValidationError(
                f"End date ({end_date}) cannot be before start date ({start_date})"
            )
        
        days = (end - start).days
        
        # Add 1 if inclusive calculation is requested
        if inclusive:
            days += 1
        
        return days
        
    except DateParsingError as e:
        raise DateValidationError(f"Error calculating days between dates: {e}")


def calculate_maintenance_days(start_date: str, end_date: str) -> int:
    """
    Calculate maintenance blocked days using the same logic as the source data.
    
    Based on the data analysis, maintenance blocked_days appears to be calculated
    as the number of days between start and end dates, excluding the end date
    (similar to hotel nights calculation).
    
    Args:
        start_date: Maintenance start date string in YYYY-MM-DD format
        end_date: Maintenance end date string in YYYY-MM-DD format
        
    Returns:
        Number of blocked days (non-negative integer)
        
    Raises:
        DateValidationError: If dates are invalid
    """
    return calculate_days_between(start_date, end_date, inclusive=False)


def generate_date_range(start_date: str, end_date: str) -> List[date]:
    """
    Generate a list of dates between start_date and end_date (inclusive).
    
    Args:
        start_date: Start date string in YYYY-MM-DD format
        end_date: End date string in YYYY-MM-DD format
        
    Returns:
        List of date objects
        
    Raises:
        DateValidationError: If date range is invalid
    """
    start, end = validate_date_range(start_date, end_date)
    
    dates = []
    current_date = start
    
    while current_date <= end:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    return dates


def is_valid_date_format(date_str: str) -> bool:
    """
    Check if a string is in valid YYYY-MM-DD format.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not isinstance(date_str, str):
        return False
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def format_date(date_obj: date) -> str:
    """
    Format a date object to YYYY-MM-DD string.
    
    Args:
        date_obj: Date object to format
        
    Returns:
        Date string in YYYY-MM-DD format
    """
    return date_obj.strftime('%Y-%m-%d')


def get_month_year(date_str: str) -> str:
    """
    Extract month-year string from a date string.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        Month-year string in YYYY-MM format
        
    Raises:
        DateParsingError: If date string is invalid
    """
    date_obj = parse_date_to_date(date_str)
    return date_obj.strftime('%Y-%m')


def filter_dates_in_range(dates: List[str], start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> List[str]:
    """
    Filter a list of date strings to only include those within the specified range.
    
    Args:
        dates: List of date strings in YYYY-MM-DD format
        start_date: Optional start date filter (inclusive)
        end_date: Optional end date filter (inclusive)
        
    Returns:
        Filtered list of date strings
        
    Raises:
        DateValidationError: If filter dates are invalid
    """
    if not dates:
        return []
    
    # Parse filter dates if provided
    start_filter = None
    end_filter = None
    
    if start_date:
        start_filter = parse_date_to_date(start_date)
    
    if end_date:
        end_filter = parse_date_to_date(end_date)
    
    # Validate filter range
    if start_filter and end_filter and start_filter > end_filter:
        raise DateValidationError(
            f"Start filter date ({start_date}) must be before or equal to end filter date ({end_date})"
        )
    
    filtered_dates = []
    
    for date_str in dates:
        try:
            date_obj = parse_date_to_date(date_str)
            
            # Apply start date filter
            if start_filter and date_obj < start_filter:
                continue
            
            # Apply end date filter
            if end_filter and date_obj > end_filter:
                continue
            
            filtered_dates.append(date_str)
            
        except DateParsingError:
            # Skip invalid dates with warning
            logger.warning(f"Skipping invalid date: {date_str}")
            continue
    
    return filtered_dates


def get_date_statistics(dates: List[str]) -> dict:
    """
    Calculate statistics for a list of dates.
    
    Args:
        dates: List of date strings in YYYY-MM-DD format
        
    Returns:
        Dictionary with date statistics
    """
    if not dates:
        return {
            'count': 0,
            'earliest': None,
            'latest': None,
            'span_days': 0
        }
    
    valid_dates = []
    for date_str in dates:
        try:
            valid_dates.append(parse_date_to_date(date_str))
        except DateParsingError:
            logger.warning(f"Skipping invalid date in statistics: {date_str}")
    
    if not valid_dates:
        return {
            'count': 0,
            'earliest': None,
            'latest': None,
            'span_days': 0
        }
    
    earliest = min(valid_dates)
    latest = max(valid_dates)
    span_days = (latest - earliest).days
    
    return {
        'count': len(valid_dates),
        'earliest': format_date(earliest),
        'latest': format_date(latest),
        'span_days': span_days
    }