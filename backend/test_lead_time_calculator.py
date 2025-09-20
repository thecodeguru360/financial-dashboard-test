"""
Unit tests for lead time calculation and statistics module.

Tests cover lead time calculations, statistical measures (median, p90),
histogram generation, and error handling scenarios.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock

from app.services.lead_time_calculator import (
    calculate_lead_time,
    validate_reservation_for_lead_time,
    calculate_lead_time_statistics,
    create_lead_time_histogram,
    calculate_lead_time_by_property,
    create_lead_time_summary,
    LeadTimeCalculationError
)


class TestCalculateLeadTime:
    """Test lead time calculation function."""
    
    def test_calculate_lead_time_basic(self):
        """Test basic lead time calculation."""
        # 7 days lead time
        lead_time = calculate_lead_time("2024-01-01", "2024-01-08")
        assert lead_time == 7
        
        # 30 days lead time
        lead_time = calculate_lead_time("2024-01-01", "2024-01-31")
        assert lead_time == 30
        
        # 1 day lead time
        lead_time = calculate_lead_time("2024-01-01", "2024-01-02")
        assert lead_time == 1
    
    def test_calculate_lead_time_same_day(self):
        """Test same-day booking (0 lead time)."""
        lead_time = calculate_lead_time("2024-01-01", "2024-01-01")
        assert lead_time == 0
    
    def test_calculate_lead_time_negative(self):
        """Test negative lead time (booking after check-in)."""
        # Booking made after check-in date
        lead_time = calculate_lead_time("2024-01-08", "2024-01-01")
        assert lead_time == -7
    
    def test_calculate_lead_time_cross_month(self):
        """Test lead time calculation across month boundaries."""
        lead_time = calculate_lead_time("2024-01-25", "2024-02-05")
        assert lead_time == 11  # 6 days in Jan + 5 days in Feb
    
    def test_calculate_lead_time_cross_year(self):
        """Test lead time calculation across year boundaries."""
        lead_time = calculate_lead_time("2023-12-25", "2024-01-05")
        assert lead_time == 11  # 6 days in Dec + 5 days in Jan
    
    def test_calculate_lead_time_leap_year(self):
        """Test lead time calculation in leap year."""
        lead_time = calculate_lead_time("2024-02-25", "2024-03-05")
        assert lead_time == 9  # 4 days in Feb (leap year) + 5 days in Mar
    
    def test_calculate_lead_time_invalid_dates(self):
        """Test error handling for invalid dates."""
        with pytest.raises(LeadTimeCalculationError):
            calculate_lead_time("invalid-date", "2024-01-01")
        
        with pytest.raises(LeadTimeCalculationError):
            calculate_lead_time("2024-01-01", "invalid-date")
        
        with pytest.raises(LeadTimeCalculationError):
            calculate_lead_time("2024-13-01", "2024-01-01")  # Invalid month
    
    def test_calculate_lead_time_empty_dates(self):
        """Test error handling for empty dates."""
        with pytest.raises(LeadTimeCalculationError):
            calculate_lead_time("", "2024-01-01")
        
        with pytest.raises(LeadTimeCalculationError):
            calculate_lead_time("2024-01-01", "")


class TestValidateReservationForLeadTime:
    """Test reservation validation for lead time calculations."""
    
    def test_validate_reservation_valid(self):
        """Test validation of valid reservation data."""
        assert validate_reservation_for_lead_time(1, "2024-01-01", "2024-01-08") is True
        assert validate_reservation_for_lead_time(2, "2024-01-01", "2024-01-01") is True  # Same day
    
    def test_validate_reservation_invalid_dates(self):
        """Test validation with invalid dates."""
        assert validate_reservation_for_lead_time(1, "invalid", "2024-01-01") is False
        assert validate_reservation_for_lead_time(2, "2024-01-01", "invalid") is False
    
    def test_validate_reservation_negative_lead_time(self):
        """Test validation with negative lead time (should still be valid)."""
        assert validate_reservation_for_lead_time(1, "2024-01-08", "2024-01-01") is True


class TestCalculateLeadTimeStatistics:
    """Test lead time statistics calculation."""
    
    def create_mock_reservation(self, reservation_id, property_id, property_name, 
                              reservation_date, check_in):
        """Helper to create mock reservation objects."""
        reservation = Mock()
        reservation.reservation_id = reservation_id
        reservation.property_id = property_id
        reservation.property_name = property_name
        reservation.reservation_date = reservation_date
        reservation.check_in = check_in
        return reservation
    
    def test_calculate_statistics_basic(self):
        """Test basic statistics calculation."""
        reservations = [
            self.create_mock_reservation(1, 1, "Property 1", "2024-01-01", "2024-01-08"),  # 7 days
            self.create_mock_reservation(2, 1, "Property 1", "2024-01-01", "2024-01-15"),  # 14 days
            self.create_mock_reservation(3, 1, "Property 1", "2024-01-01", "2024-01-22"),  # 21 days
        ]
        
        stats = calculate_lead_time_statistics(reservations)
        
        assert stats['count'] == 3
        assert stats['median_days'] == 14.0
        assert stats['min_days'] == 7.0
        assert stats['max_days'] == 21.0
        assert stats['p90_days'] == 21.0  # 90th percentile of [7, 14, 21]
    
    def test_calculate_statistics_even_count(self):
        """Test statistics with even number of reservations."""
        reservations = [
            self.create_mock_reservation(1, 1, "Property 1", "2024-01-01", "2024-01-08"),  # 7 days
            self.create_mock_reservation(2, 1, "Property 1", "2024-01-01", "2024-01-15"),  # 14 days
            self.create_mock_reservation(3, 1, "Property 1", "2024-01-01", "2024-01-22"),  # 21 days
            self.create_mock_reservation(4, 1, "Property 1", "2024-01-01", "2024-01-29"),  # 28 days
        ]
        
        stats = calculate_lead_time_statistics(reservations)
        
        assert stats['count'] == 4
        assert stats['median_days'] == 17.5  # Average of 14 and 21
        assert stats['p90_days'] == 28.0  # 90th percentile
    
    def test_calculate_statistics_single_reservation(self):
        """Test statistics with single reservation."""
        reservations = [
            self.create_mock_reservation(1, 1, "Property 1", "2024-01-01", "2024-01-15"),  # 14 days
        ]
        
        stats = calculate_lead_time_statistics(reservations)
        
        assert stats['count'] == 1
        assert stats['median_days'] == 14.0
        assert stats['p90_days'] == 14.0
        assert stats['min_days'] == 14.0
        assert stats['max_days'] == 14.0
    
    def test_calculate_statistics_with_date_filter(self):
        """Test statistics with date range filtering."""
        reservations = [
            self.create_mock_reservation(1, 1, "Property 1", "2024-01-01", "2024-01-08"),  # Included
            self.create_mock_reservation(2, 1, "Property 1", "2024-01-01", "2024-02-15"),  # Included
            self.create_mock_reservation(3, 1, "Property 1", "2024-01-01", "2024-03-22"),  # Excluded
        ]
        
        stats = calculate_lead_time_statistics(reservations, start_date="2024-01-01", end_date="2024-02-28")
        
        assert stats['count'] == 2
        assert stats['median_days'] == 26.0  # Average of 7 and 45 (Jan 1 to Feb 15)
    
    def test_calculate_statistics_with_property_filter(self):
        """Test statistics with property filtering."""
        reservations = [
            self.create_mock_reservation(1, 1, "Property 1", "2024-01-01", "2024-01-08"),  # Included
            self.create_mock_reservation(2, 2, "Property 2", "2024-01-01", "2024-01-15"),  # Excluded
            self.create_mock_reservation(3, 1, "Property 1", "2024-01-01", "2024-01-22"),  # Included
        ]
        
        stats = calculate_lead_time_statistics(reservations, property_ids=[1])
        
        assert stats['count'] == 2
        assert stats['median_days'] == 14.0  # Median of [7, 21]
    
    def test_calculate_statistics_no_valid_reservations(self):
        """Test statistics with no valid reservations."""
        reservations = []
        
        stats = calculate_lead_time_statistics(reservations)
        
        assert stats['count'] == 0
        assert stats['median_days'] == 0.0
        assert stats['p90_days'] == 0.0
        assert stats['min_days'] == 0.0
        assert stats['max_days'] == 0.0
    
    def test_calculate_statistics_with_invalid_reservations(self):
        """Test statistics filtering out invalid reservations."""
        reservations = [
            self.create_mock_reservation(1, 1, "Property 1", "2024-01-01", "2024-01-08"),  # Valid
            self.create_mock_reservation(2, 1, "Property 1", "invalid", "2024-01-15"),     # Invalid
            self.create_mock_reservation(3, 1, "Property 1", "2024-01-01", "2024-01-22"),  # Valid
        ]
        
        stats = calculate_lead_time_statistics(reservations)
        
        assert stats['count'] == 2  # Only valid reservations counted
        assert stats['median_days'] == 14.0  # Median of [7, 21]


class TestCreateLeadTimeHistogram:
    """Test lead time histogram creation."""
    
    def create_mock_reservation(self, reservation_id, property_id, property_name, 
                              reservation_date, check_in):
        """Helper to create mock reservation objects."""
        reservation = Mock()
        reservation.reservation_id = reservation_id
        reservation.property_id = property_id
        reservation.property_name = property_name
        reservation.reservation_date = reservation_date
        reservation.check_in = check_in
        return reservation
    
    def test_create_histogram_basic(self):
        """Test basic histogram creation."""
        reservations = [
            self.create_mock_reservation(1, 1, "Property 1", "2024-01-01", "2024-01-03"),  # 2 days
            self.create_mock_reservation(2, 1, "Property 1", "2024-01-01", "2024-01-06"),  # 5 days
            self.create_mock_reservation(3, 1, "Property 1", "2024-01-01", "2024-01-10"),  # 9 days
            self.create_mock_reservation(4, 1, "Property 1", "2024-01-01", "2024-01-16"),  # 15 days
        ]
        
        histogram = create_lead_time_histogram(reservations, bin_size=7)
        
        # Should have bins: 0-6 days (2 reservations), 7-13 days (1 reservation), 14-20 days (1 reservation)
        assert len(histogram) == 3
        
        # Check first bin (0-6 days)
        bin_0 = next(bin for bin in histogram if bin['bin_start'] == 0)
        assert bin_0['bin_end'] == 6
        assert bin_0['count'] == 2
        assert bin_0['label'] == "0-6 days"
        
        # Check second bin (7-13 days)
        bin_7 = next(bin for bin in histogram if bin['bin_start'] == 7)
        assert bin_7['bin_end'] == 13
        assert bin_7['count'] == 1
        assert bin_7['label'] == "7-13 days"
        
        # Check third bin (14-20 days)
        bin_14 = next(bin for bin in histogram if bin['bin_start'] == 14)
        assert bin_14['bin_end'] == 20
        assert bin_14['count'] == 1
        assert bin_14['label'] == "14-20 days"
    
    def test_create_histogram_custom_bin_size(self):
        """Test histogram with custom bin size."""
        reservations = [
            self.create_mock_reservation(1, 1, "Property 1", "2024-01-01", "2024-01-04"),  # 3 days
            self.create_mock_reservation(2, 1, "Property 1", "2024-01-01", "2024-01-08"),  # 7 days
        ]
        
        histogram = create_lead_time_histogram(reservations, bin_size=5)
        
        # Should have bins: 0-4 days (1 reservation), 5-9 days (1 reservation)
        assert len(histogram) == 2
        
        bin_0 = next(bin for bin in histogram if bin['bin_start'] == 0)
        assert bin_0['bin_end'] == 4
        assert bin_0['count'] == 1
        
        bin_5 = next(bin for bin in histogram if bin['bin_start'] == 5)
        assert bin_5['bin_end'] == 9
        assert bin_5['count'] == 1
    
    def test_create_histogram_with_filters(self):
        """Test histogram with date and property filters."""
        reservations = [
            self.create_mock_reservation(1, 1, "Property 1", "2024-01-01", "2024-01-08"),  # Included
            self.create_mock_reservation(2, 2, "Property 2", "2024-01-01", "2024-01-15"),  # Excluded by property
            self.create_mock_reservation(3, 1, "Property 1", "2024-01-01", "2024-03-22"),  # Excluded by date
        ]
        
        histogram = create_lead_time_histogram(
            reservations, 
            start_date="2024-01-01", 
            end_date="2024-02-28",
            property_ids=[1]
        )
        
        assert len(histogram) == 1  # Only one reservation matches filters
        assert histogram[0]['count'] == 1
    
    def test_create_histogram_no_reservations(self):
        """Test histogram with no valid reservations."""
        reservations = []
        
        histogram = create_lead_time_histogram(reservations)
        
        assert histogram == []
    
    def test_create_histogram_negative_lead_times(self):
        """Test histogram with negative lead times."""
        reservations = [
            self.create_mock_reservation(1, 1, "Property 1", "2024-01-08", "2024-01-01"),  # -7 days
            self.create_mock_reservation(2, 1, "Property 1", "2024-01-01", "2024-01-08"),  # 7 days
        ]
        
        histogram = create_lead_time_histogram(reservations, bin_size=7)
        
        # Should have bins for both negative and positive lead times
        assert len(histogram) == 2
        
        # Check negative bin
        negative_bin = next(bin for bin in histogram if bin['bin_start'] == -7)
        assert negative_bin['bin_end'] == -1
        assert negative_bin['count'] == 1
        
        # Check positive bin
        positive_bin = next(bin for bin in histogram if bin['bin_start'] == 7)
        assert positive_bin['bin_end'] == 13
        assert positive_bin['count'] == 1


class TestCalculateLeadTimeByProperty:
    """Test lead time calculation by property."""
    
    def create_mock_reservation(self, reservation_id, property_id, property_name, 
                              reservation_date, check_in):
        """Helper to create mock reservation objects."""
        reservation = Mock()
        reservation.reservation_id = reservation_id
        reservation.property_id = property_id
        reservation.property_name = property_name
        reservation.reservation_date = reservation_date
        reservation.check_in = check_in
        return reservation
    
    def test_calculate_by_property_basic(self):
        """Test basic property-wise lead time calculation."""
        reservations = [
            self.create_mock_reservation(1, 1, "Property 1", "2024-01-01", "2024-01-08"),  # 7 days
            self.create_mock_reservation(2, 1, "Property 1", "2024-01-01", "2024-01-15"),  # 14 days
            self.create_mock_reservation(3, 2, "Property 2", "2024-01-01", "2024-01-22"),  # 21 days
        ]
        
        property_stats = calculate_lead_time_by_property(reservations)
        
        assert len(property_stats) == 2
        
        # Check Property 1 stats
        prop1_stats = property_stats[1]
        assert prop1_stats['property_name'] == "Property 1"
        assert prop1_stats['count'] == 2
        assert prop1_stats['median_days'] == 10.5  # Average of 7 and 14
        assert prop1_stats['min_days'] == 7.0
        assert prop1_stats['max_days'] == 14.0
        assert prop1_stats['average_days'] == 10.5
        
        # Check Property 2 stats
        prop2_stats = property_stats[2]
        assert prop2_stats['property_name'] == "Property 2"
        assert prop2_stats['count'] == 1
        assert prop2_stats['median_days'] == 21.0
        assert prop2_stats['p90_days'] == 21.0
    
    def test_calculate_by_property_with_date_filter(self):
        """Test property calculation with date filtering."""
        reservations = [
            self.create_mock_reservation(1, 1, "Property 1", "2024-01-01", "2024-01-08"),  # Included
            self.create_mock_reservation(2, 1, "Property 1", "2024-01-01", "2024-03-15"),  # Excluded
        ]
        
        property_stats = calculate_lead_time_by_property(
            reservations, 
            start_date="2024-01-01", 
            end_date="2024-02-28"
        )
        
        assert len(property_stats) == 1
        assert property_stats[1]['count'] == 1


class TestCreateLeadTimeSummary:
    """Test comprehensive lead time summary creation."""
    
    def create_mock_reservation(self, reservation_id, property_id, property_name, 
                              reservation_date, check_in):
        """Helper to create mock reservation objects."""
        reservation = Mock()
        reservation.reservation_id = reservation_id
        reservation.property_id = property_id
        reservation.property_name = property_name
        reservation.reservation_date = reservation_date
        reservation.check_in = check_in
        return reservation
    
    def test_create_summary_complete(self):
        """Test complete summary creation."""
        reservations = [
            self.create_mock_reservation(1, 1, "Property 1", "2024-01-01", "2024-01-08"),  # 7 days
            self.create_mock_reservation(2, 1, "Property 1", "2024-01-01", "2024-01-15"),  # 14 days
            self.create_mock_reservation(3, 2, "Property 2", "2024-01-01", "2024-01-22"),  # 21 days
        ]
        
        summary = create_lead_time_summary(reservations)
        
        # Check that all sections are present
        assert 'statistics' in summary
        assert 'histogram' in summary
        assert 'property_breakdown' in summary
        
        # Check statistics section
        stats = summary['statistics']
        assert stats['count'] == 3
        assert stats['median_days'] == 14.0
        
        # Check histogram section
        histogram = summary['histogram']
        assert len(histogram) > 0
        
        # Check property breakdown
        property_breakdown = summary['property_breakdown']
        assert len(property_breakdown) == 2
        assert 1 in property_breakdown
        assert 2 in property_breakdown
    
    def test_create_summary_with_property_filter(self):
        """Test summary with property filtering (no property breakdown)."""
        reservations = [
            self.create_mock_reservation(1, 1, "Property 1", "2024-01-01", "2024-01-08"),
            self.create_mock_reservation(2, 2, "Property 2", "2024-01-01", "2024-01-15"),
        ]
        
        summary = create_lead_time_summary(reservations, property_ids=[1])
        
        # Property breakdown should be empty when filtering by specific properties
        assert summary['property_breakdown'] == {}
        
        # Statistics should only include filtered properties
        assert summary['statistics']['count'] == 1


if __name__ == "__main__":
    pytest.main([__file__])