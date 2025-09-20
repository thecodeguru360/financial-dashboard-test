"""
Integration test for revenue calculator with real data.

Tests the revenue calculation and aggregation functions with the actual dataset.
"""

from app.services.data_loader import load_and_validate_data
from app.services.revenue_calculator import (
    aggregate_daily_revenue,
    aggregate_revenue_by_property,
    create_revenue_timeline,
    create_property_revenue_summary,
    calculate_reservation_metrics
)


def test_revenue_calculator_integration():
    """Test revenue calculator with real data."""
    print("🔄 Loading real data...")
    
    # Load the actual data
    data = load_and_validate_data("../data/str_dummy_data_with_booking_date.json")
    reservations = data.reservations
    
    print(f"✓ Loaded {len(reservations)} reservations")
    
    # Test basic metrics calculation
    print("\n📊 Testing basic metrics calculation...")
    metrics = calculate_reservation_metrics(reservations)
    
    print(f"✓ Total revenue: ${metrics['total_revenue']:,.2f}")
    print(f"✓ Total nights: {metrics['total_nights']:,}")
    print(f"✓ Average nightly rate: ${metrics['average_nightly_rate']:.2f}")
    print(f"✓ Valid reservations: {metrics['valid_reservations']}")
    
    # Test daily revenue aggregation
    print("\n📈 Testing daily revenue aggregation...")
    daily_revenue = aggregate_daily_revenue(reservations)
    
    print(f"✓ Generated daily revenue for {len(daily_revenue)} dates")
    
    # Show sample of daily revenue
    sorted_dates = sorted(daily_revenue.keys())
    print(f"✓ Date range: {sorted_dates[0]} to {sorted_dates[-1]}")
    
    # Show top 5 revenue days
    top_days = sorted(daily_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
    print("✓ Top 5 revenue days:")
    for date_str, revenue in top_days:
        print(f"   {date_str}: ${revenue:,.2f}")
    
    # Test property revenue aggregation
    print("\n🏠 Testing property revenue aggregation...")
    property_revenue = aggregate_revenue_by_property(reservations)
    
    print(f"✓ Generated revenue for {len(property_revenue)} properties")
    
    # Show top 5 properties by revenue
    top_properties = sorted(
        property_revenue.items(), 
        key=lambda x: x[1]['total_revenue'], 
        reverse=True
    )[:5]
    
    print("✓ Top 5 properties by revenue:")
    for prop_id, metrics in top_properties:
        print(f"   {metrics['property_name']}: ${metrics['total_revenue']:,.2f} "
              f"({metrics['reservation_count']} reservations, "
              f"${metrics['average_nightly_rate']:.2f}/night)")
    
    # Test timeline creation
    print("\n📅 Testing timeline creation...")
    timeline = create_revenue_timeline(reservations, "2024-01-01", "2024-01-31")
    
    print(f"✓ Generated timeline with {len(timeline)} data points for January 2024")
    
    if timeline:
        total_jan_revenue = sum(point['total_revenue'] for point in timeline)
        print(f"✓ Total January 2024 revenue: ${total_jan_revenue:,.2f}")
    
    # Test property summary creation
    print("\n📋 Testing property summary creation...")
    summary = create_property_revenue_summary(reservations, "2024-01-01", "2024-12-31")
    
    print(f"✓ Generated summary for {len(summary)} properties for 2024")
    
    if summary:
        print("✓ Top 3 properties in 2024:")
        for i, prop in enumerate(summary[:3], 1):
            print(f"   {i}. {prop['property_name']}: ${prop['total_revenue']:,.2f}")
    
    # Test date filtering
    print("\n🔍 Testing date filtering...")
    
    # Test Q1 2024 revenue
    q1_revenue = aggregate_daily_revenue(reservations, "2024-01-01", "2024-03-31")
    q1_total = sum(q1_revenue.values())
    
    # Test Q2 2024 revenue
    q2_revenue = aggregate_daily_revenue(reservations, "2024-04-01", "2024-06-30")
    q2_total = sum(q2_revenue.values())
    
    print(f"✓ Q1 2024 revenue: ${q1_total:,.2f} ({len(q1_revenue)} days)")
    print(f"✓ Q2 2024 revenue: ${q2_total:,.2f} ({len(q2_revenue)} days)")
    
    # Verify totals make sense
    assert metrics['total_revenue'] > 0, "Total revenue should be positive"
    assert metrics['total_nights'] > 0, "Total nights should be positive"
    assert metrics['average_nightly_rate'] > 0, "Average nightly rate should be positive"
    assert len(daily_revenue) > 0, "Should have daily revenue data"
    assert len(property_revenue) > 0, "Should have property revenue data"
    
    print("\n✅ All revenue calculator integration tests passed!")
    return True


if __name__ == "__main__":
    test_revenue_calculator_integration()