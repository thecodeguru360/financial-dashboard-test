#!/usr/bin/env python3
"""
Test script for date parsing and validation utilities.
"""

import sys
from pathlib import Path
from datetime import date

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from services.date_utils import (
    parse_date_string,
    parse_date_to_date,
    validate_date_range,
    calculate_nights,
    calculate_days_between,
    calculate_maintenance_days,
    generate_date_range,
    is_valid_date_format,
    format_date,
    get_month_year,
    filter_dates_in_range,
    get_date_statistics,
    DateParsingError,
    DateValidationError
)


def test_date_parsing():
    """Test date parsing functions."""
    print("🔍 Testing date parsing...")
    
    # Test valid date parsing
    date_str = "2024-03-15"
    parsed = parse_date_to_date(date_str)
    assert parsed == date(2024, 3, 15), f"Expected date(2024, 3, 15), got {parsed}"
    print("✓ Valid date parsing works")
    
    # Test invalid date format
    try:
        parse_date_to_date("2024/03/15")
        assert False, "Should have raised DateParsingError"
    except DateParsingError:
        print("✓ Invalid date format properly rejected")
    
    # Test empty date
    try:
        parse_date_to_date("")
        assert False, "Should have raised DateParsingError"
    except DateParsingError:
        print("✓ Empty date properly rejected")
    
    # Test date format validation
    assert is_valid_date_format("2024-03-15") == True
    assert is_valid_date_format("2024/03/15") == False
    assert is_valid_date_format("invalid") == False
    print("✓ Date format validation works")


def test_date_range_validation():
    """Test date range validation."""
    print("\n🔍 Testing date range validation...")
    
    # Test valid range
    start, end = validate_date_range("2024-03-01", "2024-03-15")
    assert start == date(2024, 3, 1)
    assert end == date(2024, 3, 15)
    print("✓ Valid date range validation works")
    
    # Test same date range
    start, end = validate_date_range("2024-03-15", "2024-03-15")
    assert start == end
    print("✓ Same date range validation works")
    
    # Test invalid range
    try:
        validate_date_range("2024-03-15", "2024-03-01")
        assert False, "Should have raised DateValidationError"
    except DateValidationError:
        print("✓ Invalid date range properly rejected")


def test_nights_calculation():
    """Test nights calculation."""
    print("\n🔍 Testing nights calculation...")
    
    # Test normal stay
    nights = calculate_nights("2024-03-01", "2024-03-05")
    assert nights == 4, f"Expected 4 nights, got {nights}"
    print("✓ Normal nights calculation works")
    
    # Test same-day booking
    nights = calculate_nights("2024-03-01", "2024-03-01")
    assert nights == 0, f"Expected 0 nights, got {nights}"
    print("✓ Same-day booking calculation works")
    
    # Test single night
    nights = calculate_nights("2024-03-01", "2024-03-02")
    assert nights == 1, f"Expected 1 night, got {nights}"
    print("✓ Single night calculation works")
    
    # Test invalid order
    try:
        calculate_nights("2024-03-05", "2024-03-01")
        assert False, "Should have raised DateValidationError"
    except DateValidationError:
        print("✓ Invalid nights order properly rejected")


def test_days_between_calculation():
    """Test days between calculation (inclusive and exclusive)."""
    print("\n🔍 Testing days between calculation...")
    
    # Test normal range (inclusive)
    days = calculate_days_between("2024-03-01", "2024-03-05", inclusive=True)
    assert days == 5, f"Expected 5 days (inclusive), got {days}"
    print("✓ Inclusive days calculation works")
    
    # Test normal range (exclusive)
    days = calculate_days_between("2024-03-01", "2024-03-05", inclusive=False)
    assert days == 4, f"Expected 4 days (exclusive), got {days}"
    print("✓ Exclusive days calculation works")
    
    # Test same day (inclusive)
    days = calculate_days_between("2024-03-01", "2024-03-01", inclusive=True)
    assert days == 1, f"Expected 1 day (inclusive), got {days}"
    print("✓ Same day inclusive calculation works")
    
    # Test same day (exclusive)
    days = calculate_days_between("2024-03-01", "2024-03-01", inclusive=False)
    assert days == 0, f"Expected 0 days (exclusive), got {days}"
    print("✓ Same day exclusive calculation works")
    
    # Test maintenance days calculation
    days = calculate_maintenance_days("2024-04-20", "2024-04-23")
    assert days == 3, f"Expected 3 maintenance days, got {days}"
    print("✓ Maintenance days calculation works")
    
    # Test invalid order
    try:
        calculate_days_between("2024-03-05", "2024-03-01")
        assert False, "Should have raised DateValidationError"
    except DateValidationError:
        print("✓ Invalid days order properly rejected")


def test_date_range_generation():
    """Test date range generation."""
    print("\n🔍 Testing date range generation...")
    
    # Test normal range
    dates = generate_date_range("2024-03-01", "2024-03-03")
    expected = [date(2024, 3, 1), date(2024, 3, 2), date(2024, 3, 3)]
    assert dates == expected, f"Expected {expected}, got {dates}"
    print("✓ Date range generation works")
    
    # Test single date
    dates = generate_date_range("2024-03-01", "2024-03-01")
    expected = [date(2024, 3, 1)]
    assert dates == expected, f"Expected {expected}, got {dates}"
    print("✓ Single date range generation works")


def test_month_year_extraction():
    """Test month-year extraction."""
    print("\n🔍 Testing month-year extraction...")
    
    month_year = get_month_year("2024-03-15")
    assert month_year == "2024-03", f"Expected '2024-03', got '{month_year}'"
    print("✓ Month-year extraction works")


def test_date_filtering():
    """Test date filtering."""
    print("\n🔍 Testing date filtering...")
    
    dates = ["2024-03-01", "2024-03-15", "2024-04-01", "2024-04-15"]
    
    # Test start date filter
    filtered = filter_dates_in_range(dates, start_date="2024-03-15")
    expected = ["2024-03-15", "2024-04-01", "2024-04-15"]
    assert filtered == expected, f"Expected {expected}, got {filtered}"
    print("✓ Start date filtering works")
    
    # Test end date filter
    filtered = filter_dates_in_range(dates, end_date="2024-03-15")
    expected = ["2024-03-01", "2024-03-15"]
    assert filtered == expected, f"Expected {expected}, got {filtered}"
    print("✓ End date filtering works")
    
    # Test range filter
    filtered = filter_dates_in_range(dates, start_date="2024-03-15", end_date="2024-04-01")
    expected = ["2024-03-15", "2024-04-01"]
    assert filtered == expected, f"Expected {expected}, got {filtered}"
    print("✓ Range filtering works")
    
    # Test no filter
    filtered = filter_dates_in_range(dates)
    assert filtered == dates, f"Expected {dates}, got {filtered}"
    print("✓ No filter works")


def test_date_statistics():
    """Test date statistics calculation."""
    print("\n🔍 Testing date statistics...")
    
    dates = ["2024-03-01", "2024-03-15", "2024-04-01"]
    stats = get_date_statistics(dates)
    
    expected = {
        'count': 3,
        'earliest': '2024-03-01',
        'latest': '2024-04-01',
        'span_days': 31
    }
    
    assert stats == expected, f"Expected {expected}, got {stats}"
    print("✓ Date statistics calculation works")
    
    # Test empty list
    stats = get_date_statistics([])
    expected = {
        'count': 0,
        'earliest': None,
        'latest': None,
        'span_days': 0
    }
    assert stats == expected, f"Expected {expected}, got {stats}"
    print("✓ Empty date statistics works")


def test_real_world_scenarios():
    """Test with real-world scenarios from the data."""
    print("\n🔍 Testing real-world scenarios...")
    
    # Test typical reservation scenario
    checkin = "2024-06-08"
    checkout = "2024-06-22"
    nights = calculate_nights(checkin, checkout)
    assert nights == 14, f"Expected 14 nights, got {nights}"
    print("✓ Real reservation nights calculation works")
    
    # Test maintenance block scenario
    start = "2024-04-20"
    end = "2024-04-23"
    days = calculate_maintenance_days(start, end)
    assert days == 3, f"Expected 3 maintenance days, got {days}"
    print("✓ Real maintenance days calculation works")
    
    # Test review date processing
    review_date = "2024-04-20"
    month_year = get_month_year(review_date)
    assert month_year == "2024-04", f"Expected '2024-04', got '{month_year}'"
    print("✓ Real review date processing works")


def run_all_tests():
    """Run all date utility tests."""
    print("🧪 Testing Date Utilities\n")
    
    try:
        test_date_parsing()
        test_date_range_validation()
        test_nights_calculation()
        test_days_between_calculation()
        test_date_range_generation()
        test_month_year_extraction()
        test_date_filtering()
        test_date_statistics()
        test_real_world_scenarios()
        
        print("\n✅ All date utility tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)