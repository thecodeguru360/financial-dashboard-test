"""
Data loading and validation module for financial dashboard.

This module handles loading and validating the JSON data file containing
properties, reservations, reviews, and maintenance blocks.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, ValidationError, validator
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PropertyData(BaseModel):
    """Validation model for property data."""
    property_id: int
    property_name: str
    reviews_count: int
    average_review_score: float

    @validator('property_id')
    def validate_property_id(cls, v):
        if v <= 0:
            raise ValueError('property_id must be positive')
        return v

    @validator('reviews_count')
    def validate_reviews_count(cls, v):
        if v < 0:
            raise ValueError('reviews_count must be non-negative')
        return v

    @validator('average_review_score')
    def validate_average_review_score(cls, v):
        if not (0 <= v <= 5):
            raise ValueError('average_review_score must be between 0 and 5')
        return v


class ReservationData(BaseModel):
    """Validation model for reservation data."""
    reservation_id: int
    property_id: int
    property_name: str
    guest_name: str
    reservation_date: str
    check_in: str
    check_out: str
    reservation_revenue: float

    @validator('reservation_id')
    def validate_reservation_id(cls, v):
        if v <= 0:
            raise ValueError('reservation_id must be positive')
        return v

    @validator('property_id')
    def validate_property_id(cls, v):
        if v <= 0:
            raise ValueError('property_id must be positive')
        return v

    @validator('reservation_revenue')
    def validate_reservation_revenue(cls, v):
        if v < 0:
            raise ValueError('reservation_revenue must be non-negative')
        return v

    @validator('reservation_date', 'check_in', 'check_out')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f'Date must be in YYYY-MM-DD format, got: {v}')
        return v


class ReviewData(BaseModel):
    """Validation model for review data."""
    review_id: int
    property_id: int
    property_name: str
    review_date: str
    rating: float

    @validator('review_id')
    def validate_review_id(cls, v):
        if v <= 0:
            raise ValueError('review_id must be positive')
        return v

    @validator('property_id')
    def validate_property_id(cls, v):
        if v <= 0:
            raise ValueError('property_id must be positive')
        return v

    @validator('rating')
    def validate_rating(cls, v):
        if not (0 <= v <= 5):
            raise ValueError('rating must be between 0 and 5')
        return v

    @validator('review_date')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f'Date must be in YYYY-MM-DD format, got: {v}')
        return v


class MaintenanceBlockData(BaseModel):
    """Validation model for maintenance block data."""
    maintenance_id: int
    property_id: int
    property_name: str
    start_date: str
    end_date: str
    blocked_days: int

    @validator('maintenance_id')
    def validate_maintenance_id(cls, v):
        if v <= 0:
            raise ValueError('maintenance_id must be positive')
        return v

    @validator('property_id')
    def validate_property_id(cls, v):
        if v <= 0:
            raise ValueError('property_id must be positive')
        return v

    @validator('blocked_days')
    def validate_blocked_days(cls, v):
        if v <= 0:
            raise ValueError('blocked_days must be positive')
        return v

    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f'Date must be in YYYY-MM-DD format, got: {v}')
        return v


class RawDataStructure(BaseModel):
    """Validation model for the complete raw data structure."""
    properties: List[PropertyData]
    reservations: List[ReservationData]
    reviews: List[ReviewData]
    maintenance_blocks: List[MaintenanceBlockData]


class DataLoadingError(Exception):
    """Custom exception for data loading errors."""
    pass


class DataValidationError(Exception):
    """Custom exception for data validation errors."""
    pass


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load and parse JSON data file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON data as dictionary
        
    Raises:
        DataLoadingError: If file cannot be loaded or parsed
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise DataLoadingError(f"Data file not found: {file_path}")
        
        if not path.is_file():
            raise DataLoadingError(f"Path is not a file: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        logger.info(f"Successfully loaded JSON data from {file_path}")
        return data
        
    except json.JSONDecodeError as e:
        raise DataLoadingError(f"Invalid JSON format in {file_path}: {e}")
    except IOError as e:
        raise DataLoadingError(f"Error reading file {file_path}: {e}")
    except Exception as e:
        raise DataLoadingError(f"Unexpected error loading {file_path}: {e}")


def validate_data_structure(raw_data: Dict[str, Any]) -> RawDataStructure:
    """
    Validate the structure and content of raw data.
    
    Args:
        raw_data: Raw data dictionary from JSON file
        
    Returns:
        Validated data structure
        
    Raises:
        DataValidationError: If data structure is invalid
    """
    try:
        # Check for required top-level keys
        required_keys = {'properties', 'reservations', 'reviews', 'maintenance_blocks'}
        missing_keys = required_keys - set(raw_data.keys())
        if missing_keys:
            raise DataValidationError(f"Missing required keys: {missing_keys}")
        
        # Validate each section
        validated_data = RawDataStructure(**raw_data)
        
        # Log validation results
        logger.info(f"Data validation successful:")
        logger.info(f"  - Properties: {len(validated_data.properties)}")
        logger.info(f"  - Reservations: {len(validated_data.reservations)}")
        logger.info(f"  - Reviews: {len(validated_data.reviews)}")
        logger.info(f"  - Maintenance blocks: {len(validated_data.maintenance_blocks)}")
        
        return validated_data
        
    except ValidationError as e:
        error_details = []
        for error in e.errors():
            location = " -> ".join(str(loc) for loc in error['loc'])
            error_details.append(f"{location}: {error['msg']}")
        
        raise DataValidationError(f"Data validation failed:\n" + "\n".join(error_details))
    except Exception as e:
        raise DataValidationError(f"Unexpected validation error: {e}")


def load_and_validate_data(file_path: str) -> RawDataStructure:
    """
    Load and validate data from JSON file.
    
    This is the main function that combines loading and validation.
    
    Args:
        file_path: Path to the JSON data file
        
    Returns:
        Validated data structure
        
    Raises:
        DataLoadingError: If file cannot be loaded
        DataValidationError: If data validation fails
    """
    logger.info(f"Loading data from {file_path}")
    
    # Load raw data
    raw_data = load_json_file(file_path)
    
    # Validate data structure
    validated_data = validate_data_structure(raw_data)
    
    logger.info("Data loading and validation completed successfully")
    return validated_data


def get_data_summary(data: RawDataStructure) -> Dict[str, Any]:
    """
    Generate a summary of the loaded data.
    
    Args:
        data: Validated data structure
        
    Returns:
        Dictionary containing data summary statistics
    """
    # Get date ranges
    reservation_dates = [r.reservation_date for r in data.reservations]
    checkin_dates = [r.check_in for r in data.reservations]
    review_dates = [r.review_date for r in data.reviews]
    maintenance_dates = [m.start_date for m in data.maintenance_blocks] + [m.end_date for m in data.maintenance_blocks]
    
    all_dates = reservation_dates + checkin_dates + review_dates + maintenance_dates
    
    summary = {
        'properties': {
            'count': len(data.properties),
            'property_ids': sorted([p.property_id for p in data.properties])
        },
        'reservations': {
            'count': len(data.reservations),
            'total_revenue': sum(r.reservation_revenue for r in data.reservations),
            'date_range': {
                'earliest_reservation': min(reservation_dates) if reservation_dates else None,
                'latest_reservation': max(reservation_dates) if reservation_dates else None,
                'earliest_checkin': min(checkin_dates) if checkin_dates else None,
                'latest_checkin': max(checkin_dates) if checkin_dates else None
            }
        },
        'reviews': {
            'count': len(data.reviews),
            'average_rating': sum(r.rating for r in data.reviews) / len(data.reviews) if data.reviews else 0,
            'date_range': {
                'earliest_review': min(review_dates) if review_dates else None,
                'latest_review': max(review_dates) if review_dates else None
            }
        },
        'maintenance_blocks': {
            'count': len(data.maintenance_blocks),
            'total_blocked_days': sum(m.blocked_days for m in data.maintenance_blocks)
        },
        'overall_date_range': {
            'earliest_date': min(all_dates) if all_dates else None,
            'latest_date': max(all_dates) if all_dates else None
        }
    }
    
    return summary