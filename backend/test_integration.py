#!/usr/bin/env python3
"""
Integration test for data loading and date utilities.
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from services.data_loader import load_and_validate_data
from services.date_utils import (
    calculate_nights,
    calculate_days_between,
    calculate_maintenance_days,
    get_month_year,
    validate_date_range,
    get_date_statistics
)


def test_integration():
    """Test integration between data loading and date utilities."""
    print("🔗 Testing Integration of Data Loading and Date Utilities\n")
    
    try:
        # Load the data
        print("📂 Loading data...")
        data = load_and_validate_data("../data/str_dummy_data_with_booking_date.json")
        print("✓ Data loaded successfully")
        
        # Test reservation date processing
        print("\n🏨 Testing reservation date processing...")
        reservation_nights = []
        invalid_reservations = 0
        
        for reservation in data.reservations[:10]:  # Test first 10 reservations
            try:
                nights = calculate_nights(reservation.check_in, reservation.check_out)
                reservation_nights.append(nights)
                
                # Validate the date range
                validate_date_range(reservation.check_in, reservation.check_out)
                
            except Exception as e:
                print(f"⚠️  Invalid reservation {reservation.reservation_id}: {e}")
                invalid_reservations += 1
        
        print(f"✓ Processed {len(reservation_nights)} reservations")
        print(f"✓ Average nights: {sum(reservation_nights) / len(reservation_nights):.1f}")
        print(f"✓ Invalid reservations: {invalid_reservations}")
        
        # Test maintenance block date processing
        print("\n🔧 Testing maintenance block date processing...")
        maintenance_days = []
        invalid_maintenance = 0
        
        for block in data.maintenance_blocks[:10]:  # Test first 10 blocks
            try:
                days = calculate_maintenance_days(block.start_date, block.end_date)
                maintenance_days.append(days)
                
                # Verify against blocked_days field
                if days != block.blocked_days:
                    print(f"⚠️  Mismatch in maintenance {block.maintenance_id}: calculated {days}, stored {block.blocked_days}")
                
            except Exception as e:
                print(f"⚠️  Invalid maintenance block {block.maintenance_id}: {e}")
                invalid_maintenance += 1
        
        print(f"✓ Processed {len(maintenance_days)} maintenance blocks")
        print(f"✓ Average blocked days: {sum(maintenance_days) / len(maintenance_days):.1f}")
        print(f"✓ Invalid maintenance blocks: {invalid_maintenance}")
        
        # Test review date processing
        print("\n⭐ Testing review date processing...")
        review_months = []
        invalid_reviews = 0
        
        for review in data.reviews[:10]:  # Test first 10 reviews
            try:
                month_year = get_month_year(review.review_date)
                review_months.append(month_year)
                
            except Exception as e:
                print(f"⚠️  Invalid review {review.review_id}: {e}")
                invalid_reviews += 1
        
        print(f"✓ Processed {len(review_months)} reviews")
        print(f"✓ Unique months: {len(set(review_months))}")
        print(f"✓ Invalid reviews: {invalid_reviews}")
        
        # Test date statistics across all data
        print("\n📊 Testing date statistics...")
        
        # Collect all dates
        all_reservation_dates = [r.reservation_date for r in data.reservations]
        all_checkin_dates = [r.check_in for r in data.reservations]
        all_review_dates = [r.review_date for r in data.reviews]
        all_maintenance_dates = [m.start_date for m in data.maintenance_blocks]
        
        # Calculate statistics
        reservation_stats = get_date_statistics(all_reservation_dates)
        checkin_stats = get_date_statistics(all_checkin_dates)
        review_stats = get_date_statistics(all_review_dates)
        maintenance_stats = get_date_statistics(all_maintenance_dates)
        
        print(f"✓ Reservation dates: {reservation_stats['earliest']} to {reservation_stats['latest']} ({reservation_stats['span_days']} days)")
        print(f"✓ Check-in dates: {checkin_stats['earliest']} to {checkin_stats['latest']} ({checkin_stats['span_days']} days)")
        print(f"✓ Review dates: {review_stats['earliest']} to {review_stats['latest']} ({review_stats['span_days']} days)")
        print(f"✓ Maintenance dates: {maintenance_stats['earliest']} to {maintenance_stats['latest']} ({maintenance_stats['span_days']} days)")
        
        # Test revenue calculation with nights
        print("\n💰 Testing revenue calculations...")
        total_revenue = 0
        total_nights = 0
        
        for reservation in data.reservations:
            try:
                nights = calculate_nights(reservation.check_in, reservation.check_out)
                total_revenue += reservation.reservation_revenue
                total_nights += nights
                
            except Exception:
                # Skip invalid reservations
                continue
        
        if total_nights > 0:
            average_nightly_rate = total_revenue / total_nights
            print(f"✓ Total revenue: ${total_revenue:,.2f}")
            print(f"✓ Total nights: {total_nights:,}")
            print(f"✓ Average nightly rate: ${average_nightly_rate:.2f}")
        
        print("\n✅ All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)