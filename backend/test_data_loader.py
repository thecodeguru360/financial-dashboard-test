#!/usr/bin/env python3
"""
Test script for data loading and validation module.
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from services.data_loader import (
    load_and_validate_data,
    get_data_summary,
    DataLoadingError,
    DataValidationError
)


def test_data_loading():
    """Test the data loading functionality."""
    try:
        # Load and validate data
        data_file = "../data/str_dummy_data_with_booking_date.json"
        print(f"Loading data from: {data_file}")
        
        validated_data = load_and_validate_data(data_file)
        print("✓ Data loaded and validated successfully")
        
        # Generate summary
        summary = get_data_summary(validated_data)
        print("\n📊 Data Summary:")
        print(f"Properties: {summary['properties']['count']}")
        print(f"Reservations: {summary['reservations']['count']}")
        print(f"Reviews: {summary['reviews']['count']}")
        print(f"Maintenance blocks: {summary['maintenance_blocks']['count']}")
        print(f"Total revenue: ${summary['reservations']['total_revenue']:,.2f}")
        print(f"Average rating: {summary['reviews']['average_rating']:.2f}")
        print(f"Date range: {summary['overall_date_range']['earliest_date']} to {summary['overall_date_range']['latest_date']}")
        
        # Test some specific validations
        print("\n🔍 Validation Tests:")
        
        # Check property IDs are positive
        property_ids = [p.property_id for p in validated_data.properties]
        assert all(pid > 0 for pid in property_ids), "All property IDs should be positive"
        print("✓ Property IDs are valid")
        
        # Check reservation revenue is non-negative
        revenues = [r.reservation_revenue for r in validated_data.reservations]
        assert all(rev >= 0 for rev in revenues), "All revenues should be non-negative"
        print("✓ Reservation revenues are valid")
        
        # Check ratings are in valid range
        ratings = [r.rating for r in validated_data.reviews]
        assert all(0 <= rating <= 5 for rating in ratings), "All ratings should be between 0 and 5"
        print("✓ Review ratings are valid")
        
        # Check blocked days are positive
        blocked_days = [m.blocked_days for m in validated_data.maintenance_blocks]
        assert all(days > 0 for days in blocked_days), "All blocked days should be positive"
        print("✓ Maintenance blocked days are valid")
        
        print("\n✅ All tests passed!")
        return True
        
    except (DataLoadingError, DataValidationError) as e:
        print(f"❌ Data error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_data_loading()
    sys.exit(0 if success else 1)