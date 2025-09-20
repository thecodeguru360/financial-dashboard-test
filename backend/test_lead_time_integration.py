"""
Integration tests for lead time calculator with real data.

Tests the lead time calculator using the actual JSON data file to ensure
it works correctly with real reservation data.
"""

import pytest
from pathlib import Path

from app.services.data_loader import load_and_validate_data
from app.services.lead_time_calculator import (
    calculate_lead_time_statistics,
    create_lead_time_histogram,
    calculate_lead_time_by_property,
    create_lead_time_summary
)


class TestLeadTimeIntegration:
    """Integration tests with real data."""
    
    @pytest.fixture
    def sample_data(self):
        """Load sample data for testing."""
        data_file = Path(__file__).parent / "data" / "str_dummy_data_with_booking_date.json"
        if not data_file.exists():
            pytest.skip(f"Sample data file not found: {data_file}")
        
        return load_and_validate_data(str(data_file))
    
    def test_calculate_statistics_with_real_data(self, sample_data):
        """Test lead time statistics calculation with real data."""
        reservations = sample_data.reservations
        
        # Calculate overall statistics
        stats = calculate_lead_time_statistics(reservations)
        
        # Verify basic structure
        assert 'median_days' in stats
        assert 'p90_days' in stats
        assert 'count' in stats
        assert 'min_days' in stats
        assert 'max_days' in stats
        
        # Verify we have data
        assert stats['count'] > 0
        assert stats['median_days'] >= 0  # Should be non-negative for most bookings
        assert stats['p90_days'] >= stats['median_days']  # P90 should be >= median
        assert stats['max_days'] >= stats['min_days']  # Max should be >= min
        
        print(f"Lead time statistics: {stats}")
    
    def test_calculate_statistics_with_date_filter_real_data(self, sample_data):
        """Test lead time statistics with date filtering on real data."""
        reservations = sample_data.reservations
        
        # Filter to 2024 data only
        stats_2024 = calculate_lead_time_statistics(
            reservations, 
            start_date="2024-01-01", 
            end_date="2024-12-31"
        )
        
        # Filter to 2023 data only
        stats_2023 = calculate_lead_time_statistics(
            reservations, 
            start_date="2023-01-01", 
            end_date="2023-12-31"
        )
        
        # Both should have some data
        assert stats_2024['count'] > 0
        assert stats_2023['count'] > 0
        
        # Combined count should be less than or equal to total
        total_stats = calculate_lead_time_statistics(reservations)
        assert stats_2024['count'] + stats_2023['count'] <= total_stats['count']
        
        print(f"2024 lead times: {stats_2024}")
        print(f"2023 lead times: {stats_2023}")
    
    def test_calculate_statistics_with_property_filter_real_data(self, sample_data):
        """Test lead time statistics with property filtering on real data."""
        reservations = sample_data.reservations
        
        # Get unique property IDs
        property_ids = list(set(r.property_id for r in reservations))
        
        # Test with first few properties
        test_properties = property_ids[:3]
        
        stats_filtered = calculate_lead_time_statistics(
            reservations, 
            property_ids=test_properties
        )
        
        # Should have some data
        assert stats_filtered['count'] > 0
        
        # Should be less than total count
        total_stats = calculate_lead_time_statistics(reservations)
        assert stats_filtered['count'] <= total_stats['count']
        
        print(f"Filtered properties {test_properties}: {stats_filtered}")
    
    def test_create_histogram_with_real_data(self, sample_data):
        """Test histogram creation with real data."""
        reservations = sample_data.reservations
        
        # Create histogram with default 7-day bins
        histogram = create_lead_time_histogram(reservations)
        
        # Should have some bins
        assert len(histogram) > 0
        
        # Each bin should have required fields
        for bin_data in histogram:
            assert 'bin_start' in bin_data
            assert 'bin_end' in bin_data
            assert 'count' in bin_data
            assert 'label' in bin_data
            assert bin_data['count'] > 0
            assert bin_data['bin_end'] == bin_data['bin_start'] + 6  # 7-day bins
        
        # Total count should match statistics
        total_count = sum(bin_data['count'] for bin_data in histogram)
        stats = calculate_lead_time_statistics(reservations)
        assert total_count == stats['count']
        
        print(f"Histogram bins: {len(histogram)}")
        print(f"Sample bins: {histogram[:3]}")
    
    def test_create_histogram_custom_bin_size_real_data(self, sample_data):
        """Test histogram with custom bin size on real data."""
        reservations = sample_data.reservations
        
        # Create histogram with 14-day bins
        histogram = create_lead_time_histogram(reservations, bin_size=14)
        
        # Should have some bins
        assert len(histogram) > 0
        
        # Each bin should be 14 days wide
        for bin_data in histogram:
            assert bin_data['bin_end'] == bin_data['bin_start'] + 13  # 14-day bins
        
        print(f"14-day histogram bins: {len(histogram)}")
    
    def test_calculate_by_property_real_data(self, sample_data):
        """Test property-wise lead time calculation with real data."""
        reservations = sample_data.reservations
        
        property_stats = calculate_lead_time_by_property(reservations)
        
        # Should have stats for multiple properties
        assert len(property_stats) > 0
        
        # Each property should have complete stats
        for property_id, stats in property_stats.items():
            assert 'property_name' in stats
            assert 'median_days' in stats
            assert 'p90_days' in stats
            assert 'count' in stats
            assert 'min_days' in stats
            assert 'max_days' in stats
            assert 'average_days' in stats
            
            # Verify logical relationships
            assert stats['count'] > 0
            assert stats['p90_days'] >= stats['median_days']
            assert stats['max_days'] >= stats['min_days']
            assert stats['average_days'] >= 0
        
        print(f"Properties with lead time data: {len(property_stats)}")
        
        # Show sample property stats
        sample_property = next(iter(property_stats.values()))
        print(f"Sample property stats: {sample_property}")
    
    def test_create_summary_real_data(self, sample_data):
        """Test comprehensive summary creation with real data."""
        reservations = sample_data.reservations
        
        summary = create_lead_time_summary(reservations)
        
        # Should have all sections
        assert 'statistics' in summary
        assert 'histogram' in summary
        assert 'property_breakdown' in summary
        
        # Statistics section
        stats = summary['statistics']
        assert stats['count'] > 0
        assert 'median_days' in stats
        assert 'p90_days' in stats
        
        # Histogram section
        histogram = summary['histogram']
        assert len(histogram) > 0
        
        # Property breakdown section
        property_breakdown = summary['property_breakdown']
        assert len(property_breakdown) > 0
        
        print(f"Summary - Total reservations: {stats['count']}")
        print(f"Summary - Median lead time: {stats['median_days']} days")
        print(f"Summary - P90 lead time: {stats['p90_days']} days")
        print(f"Summary - Histogram bins: {len(histogram)}")
        print(f"Summary - Properties: {len(property_breakdown)}")
    
    def test_lead_time_data_quality_real_data(self, sample_data):
        """Test data quality aspects of lead time calculations."""
        reservations = sample_data.reservations
        
        # Calculate statistics
        stats = calculate_lead_time_statistics(reservations)
        
        # Check for reasonable lead time ranges
        # Most bookings should be within 0-365 days
        assert stats['min_days'] >= -30  # Allow some negative lead times (last-minute changes)
        assert stats['max_days'] <= 730  # Allow up to 2 years advance booking
        
        # Median should be reasonable (typically 7-90 days for STR)
        assert 0 <= stats['median_days'] <= 180
        
        # P90 should be higher than median but reasonable
        assert stats['median_days'] <= stats['p90_days'] <= 365
        
        print(f"Lead time range: {stats['min_days']} to {stats['max_days']} days")
        print(f"Median: {stats['median_days']} days, P90: {stats['p90_days']} days")
    
    def test_lead_time_edge_cases_real_data(self, sample_data):
        """Test edge cases in real data."""
        reservations = sample_data.reservations
        
        # Test with very restrictive date filter (should return empty or minimal results)
        stats_restrictive = calculate_lead_time_statistics(
            reservations,
            start_date="2025-12-01",
            end_date="2025-12-31"
        )
        
        # Test with very restrictive property filter
        stats_single_property = calculate_lead_time_statistics(
            reservations,
            property_ids=[999999]  # Non-existent property
        )
        
        # Should handle empty results gracefully
        assert stats_single_property['count'] == 0
        assert stats_single_property['median_days'] == 0.0
        
        print(f"Restrictive filter results: {stats_restrictive}")
        print(f"Non-existent property results: {stats_single_property}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])