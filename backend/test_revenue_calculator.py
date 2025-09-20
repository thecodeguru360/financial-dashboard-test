"""
Unit tests for revenue calculation module.

Tests nightly rate calculations, revenue prorating, and edge cases.
"""

from datetime import date
from app.services.revenue_calculator import (
    calculate_nightly_rate,
    calculate_nights_safe,
    prorate_revenue_across_dates,
    validate_reservation_data,
    calculate_reservation_metrics,
    RevenueCalculationError
)


class MockReservation:
    """Mock reservation object for testing."""
    def __init__(self, reservation_id, revenue, check_in, check_out):
        self.reservation_id = reservation_id
        self.reservation_revenue = revenue
        self.check_in = check_in
        self.check_out = check_out


def test_calculate_nightly_rate_normal():
    """Test normal nightly rate calculation."""
    # 2 nights, $200 total = $100/night
    rate = calculate_nightly_rate(200.0, "2024-01-01", "2024-01-03")
    assert rate == 100.0, f"Expected 100.0, got {rate}"
    
    # 1 night, $150 total = $150/night
    rate = calculate_nightly_rate(150.0, "2024-01-01", "2024-01-02")
    assert rate == 150.0, f"Expected 150.0, got {rate}"
    
    # 7 nights, $700 total = $100/night
    rate = calculate_nightly_rate(700.0, "2024-01-01", "2024-01-08")
    assert rate == 100.0, f"Expected 100.0, got {rate}"


def test_calculate_nightly_rate_same_day():
    """Test same-day booking (0 nights) handling."""
    # Same-day booking should return full revenue as rate
    rate = calculate_nightly_rate(100.0, "2024-01-01", "2024-01-01")
    assert rate == 100.0, f"Expected 100.0 for same-day booking, got {rate}"


def test_calculate_nightly_rate_zero_revenue():
    """Test zero revenue handling."""
    rate = calculate_nightly_rate(0.0, "2024-01-01", "2024-01-03")
    assert rate == 0.0, f"Expected 0.0 for zero revenue, got {rate}"


def test_calculate_nightly_rate_negative_revenue():
    """Test negative revenue error handling."""
    try:
        calculate_nightly_rate(-100.0, "2024-01-01", "2024-01-03")
        assert False, "Should have raised RevenueCalculationError"
    except RevenueCalculationError as e:
        assert "Revenue cannot be negative" in str(e)


def test_calculate_nightly_rate_invalid_dates():
    """Test invalid date handling."""
    # Check-out before check-in
    try:
        calculate_nightly_rate(100.0, "2024-01-03", "2024-01-01")
        assert False, "Should have raised RevenueCalculationError"
    except RevenueCalculationError as e:
        assert "Date validation failed" in str(e)
    
    # Invalid date format
    try:
        calculate_nightly_rate(100.0, "invalid-date", "2024-01-03")
        assert False, "Should have raised RevenueCalculationError"
    except RevenueCalculationError as e:
        assert "Date validation failed" in str(e)


def test_calculate_nights_safe_normal():
    """Test safe nights calculation."""
    nights = calculate_nights_safe("2024-01-01", "2024-01-03")
    assert nights == 2, f"Expected 2 nights, got {nights}"
    
    nights = calculate_nights_safe("2024-01-01", "2024-01-02")
    assert nights == 1, f"Expected 1 night, got {nights}"


def test_calculate_nights_safe_same_day():
    """Test same-day booking returns 1 night."""
    nights = calculate_nights_safe("2024-01-01", "2024-01-01")
    assert nights == 1, f"Expected 1 night for same-day booking, got {nights}"


def test_calculate_nights_safe_invalid_dates():
    """Test invalid date error handling."""
    try:
        calculate_nights_safe("2024-01-03", "2024-01-01")
        assert False, "Should have raised RevenueCalculationError"
    except RevenueCalculationError as e:
        assert "Error calculating nights" in str(e)


def test_prorate_revenue_across_dates_normal():
    """Test normal revenue prorating."""
    # 2 nights, $200 total = $100 per night
    daily_revenue = prorate_revenue_across_dates(200.0, "2024-01-01", "2024-01-03")
    
    expected = {
        "2024-01-01": 100.0,
        "2024-01-02": 100.0
    }
    assert daily_revenue == expected, f"Expected {expected}, got {daily_revenue}"


def test_prorate_revenue_across_dates_single_night():
    """Test single night prorating."""
    daily_revenue = prorate_revenue_across_dates(150.0, "2024-01-01", "2024-01-02")
    
    expected = {"2024-01-01": 150.0}
    assert daily_revenue == expected, f"Expected {expected}, got {daily_revenue}"


def test_prorate_revenue_across_dates_same_day():
    """Test same-day booking prorating."""
    daily_revenue = prorate_revenue_across_dates(100.0, "2024-01-01", "2024-01-01")
    
    expected = {"2024-01-01": 100.0}
    assert daily_revenue == expected, f"Expected {expected}, got {daily_revenue}"


def test_prorate_revenue_across_dates_week():
    """Test week-long stay prorating."""
    daily_revenue = prorate_revenue_across_dates(700.0, "2024-01-01", "2024-01-08")
    
    expected = {
        "2024-01-01": 100.0,
        "2024-01-02": 100.0,
        "2024-01-03": 100.0,
        "2024-01-04": 100.0,
        "2024-01-05": 100.0,
        "2024-01-06": 100.0,
        "2024-01-07": 100.0
    }
    assert daily_revenue == expected, f"Expected {expected}, got {daily_revenue}"
    assert len(daily_revenue) == 7, f"Expected 7 days, got {len(daily_revenue)}"


def test_prorate_revenue_across_dates_zero_revenue():
    """Test zero revenue prorating."""
    daily_revenue = prorate_revenue_across_dates(0.0, "2024-01-01", "2024-01-03")
    
    expected = {
        "2024-01-01": 0.0,
        "2024-01-02": 0.0
    }
    assert daily_revenue == expected, f"Expected {expected}, got {daily_revenue}"


def test_prorate_revenue_across_dates_negative_revenue():
    """Test negative revenue error."""
    try:
        prorate_revenue_across_dates(-100.0, "2024-01-01", "2024-01-03")
        assert False, "Should have raised RevenueCalculationError"
    except RevenueCalculationError as e:
        assert "Revenue cannot be negative" in str(e)


def test_validate_reservation_data_valid():
    """Test valid reservation data validation."""
    assert validate_reservation_data(1, 100.0, "2024-01-01", "2024-01-03") == True
    assert validate_reservation_data(2, 0.0, "2024-01-01", "2024-01-02") == True


def test_validate_reservation_data_invalid():
    """Test invalid reservation data validation."""
    # Negative revenue
    assert validate_reservation_data(1, -100.0, "2024-01-01", "2024-01-03") == False
    
    # Invalid dates
    assert validate_reservation_data(2, 100.0, "invalid", "2024-01-03") == False
    assert validate_reservation_data(3, 100.0, "2024-01-03", "2024-01-01") == False


def test_calculate_reservation_metrics_normal():
    """Test reservation metrics calculation."""
    reservations = [
        MockReservation(1, 200.0, "2024-01-01", "2024-01-03"),  # 2 nights, $100/night
        MockReservation(2, 150.0, "2024-01-05", "2024-01-06"),  # 1 night, $150/night
        MockReservation(3, 300.0, "2024-01-10", "2024-01-13"),  # 3 nights, $100/night
    ]
    
    metrics = calculate_reservation_metrics(reservations)
    
    expected = {
        'total_revenue': 650.0,
        'total_nights': 6,
        'average_nightly_rate': 650.0 / 6,  # ~108.33
        'valid_reservations': 3
    }
    
    assert metrics['total_revenue'] == expected['total_revenue']
    assert metrics['total_nights'] == expected['total_nights']
    assert abs(metrics['average_nightly_rate'] - expected['average_nightly_rate']) < 0.01
    assert metrics['valid_reservations'] == expected['valid_reservations']


def test_calculate_reservation_metrics_with_invalid():
    """Test metrics calculation with some invalid reservations."""
    reservations = [
        MockReservation(1, 200.0, "2024-01-01", "2024-01-03"),  # Valid: 2 nights
        MockReservation(2, -100.0, "2024-01-05", "2024-01-06"), # Invalid: negative revenue
        MockReservation(3, 150.0, "invalid", "2024-01-13"),     # Invalid: bad date
        MockReservation(4, 100.0, "2024-01-10", "2024-01-11"),  # Valid: 1 night
    ]
    
    metrics = calculate_reservation_metrics(reservations)
    
    # Should only count the 2 valid reservations
    assert metrics['total_revenue'] == 300.0
    assert metrics['total_nights'] == 3
    assert metrics['average_nightly_rate'] == 100.0
    assert metrics['valid_reservations'] == 2


def test_calculate_reservation_metrics_empty():
    """Test metrics calculation with empty list."""
    metrics = calculate_reservation_metrics([])
    
    expected = {
        'total_revenue': 0.0,
        'total_nights': 0,
        'average_nightly_rate': 0.0,
        'valid_reservations': 0
    }
    
    assert metrics == expected


def test_calculate_reservation_metrics_same_day_bookings():
    """Test metrics with same-day bookings."""
    reservations = [
        MockReservation(1, 100.0, "2024-01-01", "2024-01-01"),  # Same-day: treated as 1 night
        MockReservation(2, 200.0, "2024-01-02", "2024-01-04"),  # Normal: 2 nights
    ]
    
    metrics = calculate_reservation_metrics(reservations)
    
    assert metrics['total_revenue'] == 300.0
    assert metrics['total_nights'] == 3  # 1 + 2
    assert metrics['average_nightly_rate'] == 100.0
    assert metrics['valid_reservations'] == 2


def test_aggregate_daily_revenue_normal():
    """Test normal daily revenue aggregation."""
    reservations = [
        MockReservation(1, 200.0, "2024-01-01", "2024-01-03"),  # 2 nights: $100 on 01-01, $100 on 01-02
        MockReservation(2, 150.0, "2024-01-02", "2024-01-03"),  # 1 night: $150 on 01-02
        MockReservation(3, 300.0, "2024-01-03", "2024-01-05"),  # 2 nights: $150 on 01-03, $150 on 01-04
    ]
    
    from app.services.revenue_calculator import aggregate_daily_revenue
    daily_revenue = aggregate_daily_revenue(reservations)
    
    expected = {
        "2024-01-01": 100.0,  # From reservation 1
        "2024-01-02": 250.0,  # From reservation 1 ($100) + reservation 2 ($150)
        "2024-01-03": 150.0,  # From reservation 3
        "2024-01-04": 150.0,  # From reservation 3
    }
    
    assert daily_revenue == expected, f"Expected {expected}, got {daily_revenue}"


def test_aggregate_daily_revenue_with_filters():
    """Test daily revenue aggregation with date filters."""
    reservations = [
        MockReservation(1, 200.0, "2024-01-01", "2024-01-03"),  # 2 nights
        MockReservation(2, 150.0, "2024-01-02", "2024-01-03"),  # 1 night
        MockReservation(3, 300.0, "2024-01-03", "2024-01-05"),  # 2 nights
    ]
    
    from app.services.revenue_calculator import aggregate_daily_revenue
    
    # Filter to only include 2024-01-02
    daily_revenue = aggregate_daily_revenue(reservations, "2024-01-02", "2024-01-02")
    
    expected = {
        "2024-01-02": 250.0,  # From reservation 1 ($100) + reservation 2 ($150)
    }
    
    assert daily_revenue == expected, f"Expected {expected}, got {daily_revenue}"


def test_aggregate_revenue_by_property():
    """Test revenue aggregation by property."""
    reservations = [
        MockReservation(1, 200.0, "2024-01-01", "2024-01-03"),  # Property 1, 2 nights
        MockReservation(2, 150.0, "2024-01-02", "2024-01-03"),  # Property 2, 1 night
        MockReservation(3, 300.0, "2024-01-03", "2024-01-05"),  # Property 1, 2 nights
    ]
    
    # Add property info
    reservations[0].property_id = 1
    reservations[0].property_name = "Property A"
    reservations[1].property_id = 2
    reservations[1].property_name = "Property B"
    reservations[2].property_id = 1
    reservations[2].property_name = "Property A"
    
    from app.services.revenue_calculator import aggregate_revenue_by_property
    property_revenue = aggregate_revenue_by_property(reservations)
    
    # Property 1: $200 + $300 = $500, 2 + 2 = 4 nights, avg = $125/night
    # Property 2: $150, 1 night, avg = $150/night
    
    assert 1 in property_revenue
    assert 2 in property_revenue
    
    prop1 = property_revenue[1]
    assert prop1['total_revenue'] == 500.0
    assert prop1['total_nights'] == 4
    assert prop1['reservation_count'] == 2
    assert prop1['average_nightly_rate'] == 125.0
    assert prop1['property_name'] == "Property A"
    
    prop2 = property_revenue[2]
    assert prop2['total_revenue'] == 150.0
    assert prop2['total_nights'] == 1
    assert prop2['reservation_count'] == 1
    assert prop2['average_nightly_rate'] == 150.0
    assert prop2['property_name'] == "Property B"


def test_create_revenue_timeline():
    """Test revenue timeline creation."""
    reservations = [
        MockReservation(1, 200.0, "2024-01-01", "2024-01-03"),  # $100 on 01-01, $100 on 01-02
        MockReservation(2, 150.0, "2024-01-02", "2024-01-03"),  # $150 on 01-02
    ]
    
    from app.services.revenue_calculator import create_revenue_timeline
    timeline = create_revenue_timeline(reservations)
    
    expected = [
        {'date': '2024-01-01', 'total_revenue': 100.0},
        {'date': '2024-01-02', 'total_revenue': 250.0},
    ]
    
    assert timeline == expected, f"Expected {expected}, got {timeline}"


def test_create_property_revenue_summary():
    """Test property revenue summary creation."""
    reservations = [
        MockReservation(1, 300.0, "2024-01-01", "2024-01-03"),  # Property 1, 2 nights
        MockReservation(2, 150.0, "2024-01-02", "2024-01-03"),  # Property 2, 1 night
    ]
    
    # Add property info
    reservations[0].property_id = 1
    reservations[0].property_name = "Property A"
    reservations[1].property_id = 2
    reservations[1].property_name = "Property B"
    
    from app.services.revenue_calculator import create_property_revenue_summary
    summary = create_property_revenue_summary(reservations)
    
    # Should be sorted by total revenue descending
    expected = [
        {
            'property_id': 1,
            'property_name': 'Property A',
            'total_revenue': 300.0,
            'total_nights': 2,
            'reservation_count': 1,
            'average_nightly_rate': 150.0
        },
        {
            'property_id': 2,
            'property_name': 'Property B',
            'total_revenue': 150.0,
            'total_nights': 1,
            'reservation_count': 1,
            'average_nightly_rate': 150.0
        }
    ]
    
    assert summary == expected, f"Expected {expected}, got {summary}"


if __name__ == "__main__":
    print("Running revenue calculator tests...")
    
    # Test nightly rate calculations
    print("\n🧮 Testing nightly rate calculations...")
    test_calculate_nightly_rate_normal()
    test_calculate_nightly_rate_same_day()
    test_calculate_nightly_rate_zero_revenue()
    print("✓ Nightly rate calculations passed")
    
    # Test nights calculation
    print("\n🌙 Testing nights calculations...")
    test_calculate_nights_safe_normal()
    test_calculate_nights_safe_same_day()
    print("✓ Nights calculations passed")
    
    # Test revenue prorating
    print("\n💰 Testing revenue prorating...")
    test_prorate_revenue_across_dates_normal()
    test_prorate_revenue_across_dates_single_night()
    test_prorate_revenue_across_dates_same_day()
    test_prorate_revenue_across_dates_week()
    test_prorate_revenue_across_dates_zero_revenue()
    print("✓ Revenue prorating passed")
    
    # Test validation
    print("\n✅ Testing data validation...")
    test_validate_reservation_data_valid()
    test_validate_reservation_data_invalid()
    print("✓ Data validation passed")
    
    # Test metrics calculation
    print("\n📊 Testing metrics calculation...")
    test_calculate_reservation_metrics_normal()
    test_calculate_reservation_metrics_with_invalid()
    test_calculate_reservation_metrics_empty()
    test_calculate_reservation_metrics_same_day_bookings()
    print("✓ Metrics calculation passed")
    
    # Test daily revenue aggregation
    print("\n📈 Testing daily revenue aggregation...")
    test_aggregate_daily_revenue_normal()
    test_aggregate_daily_revenue_with_filters()
    print("✓ Daily revenue aggregation passed")
    
    # Test property revenue aggregation
    print("\n🏠 Testing property revenue aggregation...")
    test_aggregate_revenue_by_property()
    print("✓ Property revenue aggregation passed")
    
    # Test timeline and summary creation
    print("\n📊 Testing timeline and summary creation...")
    test_create_revenue_timeline()
    test_create_property_revenue_summary()
    print("✓ Timeline and summary creation passed")
    
    # Test error cases
    print("\n❌ Testing error cases...")
    try:
        test_calculate_nightly_rate_negative_revenue()
        assert False, "Should have raised exception"
    except AssertionError:
        pass  # Expected
    
    try:
        test_calculate_nightly_rate_invalid_dates()
        assert False, "Should have raised exception"
    except AssertionError:
        pass  # Expected
    
    try:
        test_calculate_nights_safe_invalid_dates()
        assert False, "Should have raised exception"
    except AssertionError:
        pass  # Expected
    
    try:
        test_prorate_revenue_across_dates_negative_revenue()
        assert False, "Should have raised exception"
    except AssertionError:
        pass  # Expected
    
    print("✓ Error cases handled correctly")
    
    print("\n🎉 All revenue calculator tests passed!")