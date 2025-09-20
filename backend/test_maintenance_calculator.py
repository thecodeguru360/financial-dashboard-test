"""
Unit tests for maintenance impact calculation module.

Tests the calculation of lost income due to maintenance blocks using
historical average daily rates per property.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock

from backend.app.services.maintenance_calculator import (
    calculate_historical_average_daily_rate,
    calculate_lost_income_for_maintenance_block,
    calculate_portfolio_average_daily_rate,
    calculate_lost_income_by_property,
    create_lost_income_summary,
    validate_maintenance_block_data,
    MaintenanceCalculationError
)


class TestCalculateHistoricalAverageDailyRate:
    """Test historical average daily rate calculation."""
    
    def test_calculate_basic_average_rate(self):
        """Test basic average daily rate calculation."""
        # Create mock reservations
        reservations = [
            Mock(
                property_id=1,
                reservation_revenue=300.0,
                check_in='2024-01-01',
                check_out='2024-01-03',  # 2 nights
                reservation_id=1
            ),
            Mock(
                property_id=1,
                reservation_revenue=400.0,
                check_in='2024-01-05',
                check_out='2024-01-09',  # 4 nights
                reservation_id=2
            ),
            Mock(
                property_id=2,  # Different property - should be ignored
                reservation_revenue=500.0,
                check_in='2024-01-01',
                check_out='2024-01-03',
                reservation_id=3
            )
        ]
        
        # Calculate average rate for property 1
        # Total revenue: 300 + 400 = 700
        # Total nights: 2 + 4 = 6
        # Expected rate: 700 / 6 = 116.67
        avg_rate = calculate_historical_average_daily_rate(reservations, 1)
        
        assert abs(avg_rate - 116.67) < 0.01
    
    def test_calculate_with_same_day_booking(self):
        """Test calculation with same-day bookings (treated as 1 night)."""
        reservations = [
            Mock(
                property_id=1,
                reservation_revenue=200.0,
                check_in='2024-01-01',
                check_out='2024-01-01',  # Same day - 1 night
                reservation_id=1
            ),
            Mock(
                property_id=1,
                reservation_revenue=300.0,
                check_in='2024-01-05',
                check_out='2024-01-07',  # 2 nights
                reservation_id=2
            )
        ]
        
        # Total revenue: 200 + 300 = 500
        # Total nights: 1 + 2 = 3
        # Expected rate: 500 / 3 = 166.67
        avg_rate = calculate_historical_average_daily_rate(reservations, 1)
        
        assert abs(avg_rate - 166.67) < 0.01
    
    def test_calculate_with_exclusion_period(self):
        """Test calculation excluding reservations that overlap with maintenance period."""
        reservations = [
            Mock(
                property_id=1,
                reservation_revenue=300.0,
                check_in='2024-01-01',
                check_out='2024-01-03',  # Before exclusion - included
                reservation_id=1
            ),
            Mock(
                property_id=1,
                reservation_revenue=400.0,
                check_in='2024-01-10',
                check_out='2024-01-15',  # Overlaps exclusion - excluded
                reservation_id=2
            ),
            Mock(
                property_id=1,
                reservation_revenue=500.0,
                check_in='2024-01-20',
                check_out='2024-01-22',  # After exclusion - included
                reservation_id=3
            )
        ]
        
        # Exclude period: 2024-01-12 to 2024-01-18
        # Only reservations 1 and 3 should be included
        # Total revenue: 300 + 500 = 800
        # Total nights: 2 + 2 = 4
        # Expected rate: 800 / 4 = 200
        avg_rate = calculate_historical_average_daily_rate(
            reservations, 1, 
            exclude_start_date='2024-01-12',
            exclude_end_date='2024-01-18'
        )
        
        assert avg_rate == 200.0
    
    def test_no_valid_reservations(self):
        """Test when no valid reservations exist for property."""
        reservations = [
            Mock(
                property_id=2,  # Different property
                reservation_revenue=300.0,
                check_in='2024-01-01',
                check_out='2024-01-03',
                reservation_id=1
            )
        ]
        
        avg_rate = calculate_historical_average_daily_rate(reservations, 1)
        assert avg_rate == 0.0
    
    def test_invalid_reservation_data(self):
        """Test handling of invalid reservation data."""
        reservations = [
            Mock(
                property_id=1,
                reservation_revenue=-100.0,  # Invalid negative revenue
                check_in='2024-01-01',
                check_out='2024-01-03',
                reservation_id=1
            ),
            Mock(
                property_id=1,
                reservation_revenue=300.0,
                check_in='2024-01-05',
                check_out='2024-01-07',
                reservation_id=2
            )
        ]
        
        # Only valid reservation should be included
        # Expected rate: 300 / 2 = 150
        avg_rate = calculate_historical_average_daily_rate(reservations, 1)
        assert avg_rate == 150.0


class TestCalculateLostIncomeForMaintenanceBlock:
    """Test lost income calculation for individual maintenance blocks."""
    
    def test_calculate_basic_lost_income(self):
        """Test basic lost income calculation."""
        # Mock reservations for historical data
        reservations = [
            Mock(
                property_id=1,
                reservation_revenue=300.0,
                check_in='2024-01-01',
                check_out='2024-01-03',  # 2 nights, rate = 150/night
                reservation_id=1
            )
        ]
        
        # Mock maintenance block
        maintenance_block = Mock(
            property_id=1,
            start_date='2024-02-01',
            end_date='2024-02-05',
            blocked_days=4,
            maintenance_id=1
        )
        
        # Expected lost income: 150 * 4 = 600
        lost_income = calculate_lost_income_for_maintenance_block(reservations, maintenance_block)
        assert lost_income == 600.0
    
    def test_calculate_with_fallback_rate(self):
        """Test calculation using fallback rate when no historical data."""
        # Empty reservations (no historical data)
        reservations = []
        
        maintenance_block = Mock(
            property_id=1,
            start_date='2024-02-01',
            end_date='2024-02-05',
            blocked_days=4,
            maintenance_id=1
        )
        
        # Expected lost income with fallback: 100 * 4 = 400
        lost_income = calculate_lost_income_for_maintenance_block(
            reservations, 
            maintenance_block,
            fallback_rate=100.0
        )
        assert lost_income == 400.0
    
    def test_calculate_without_fallback_no_data(self):
        """Test calculation without fallback when no historical data."""
        reservations = []
        
        maintenance_block = Mock(
            property_id=1,
            start_date='2024-02-01',
            end_date='2024-02-05',
            blocked_days=4,
            maintenance_id=1
        )
        
        # Expected lost income: 0 * 4 = 0 (no data, no fallback)
        lost_income = calculate_lost_income_for_maintenance_block(reservations, maintenance_block)
        assert lost_income == 0.0


class TestCalculatePortfolioAverageDailyRate:
    """Test portfolio-wide average daily rate calculation."""
    
    def test_calculate_portfolio_average(self):
        """Test basic portfolio average calculation."""
        reservations = [
            Mock(
                property_id=1,
                reservation_revenue=300.0,
                check_in='2024-01-01',
                check_out='2024-01-03',  # 2 nights
                reservation_id=1
            ),
            Mock(
                property_id=2,
                reservation_revenue=400.0,
                check_in='2024-01-05',
                check_out='2024-01-09',  # 4 nights
                reservation_id=2
            )
        ]
        
        # Total revenue: 300 + 400 = 700
        # Total nights: 2 + 4 = 6
        # Expected rate: 700 / 6 = 116.67
        portfolio_rate = calculate_portfolio_average_daily_rate(reservations)
        assert abs(portfolio_rate - 116.67) < 0.01
    
    def test_empty_reservations(self):
        """Test portfolio average with no reservations."""
        reservations = []
        portfolio_rate = calculate_portfolio_average_daily_rate(reservations)
        assert portfolio_rate == 0.0


class TestCalculateLostIncomeByProperty:
    """Test lost income aggregation by property."""
    
    def test_aggregate_by_property(self):
        """Test basic aggregation by property."""
        # Mock reservations
        reservations = [
            Mock(
                property_id=1,
                reservation_revenue=300.0,
                check_in='2024-01-01',
                check_out='2024-01-03',  # Rate = 150/night
                reservation_id=1
            ),
            Mock(
                property_id=2,
                reservation_revenue=400.0,
                check_in='2024-01-01',
                check_out='2024-01-05',  # Rate = 100/night
                reservation_id=2
            )
        ]
        
        # Mock maintenance blocks
        maintenance_blocks = [
            Mock(
                property_id=1,
                start_date='2024-02-01',
                end_date='2024-02-03',
                blocked_days=2,
                property_name='Property 1',
                maintenance_id=1
            ),
            Mock(
                property_id=1,
                start_date='2024-02-10',
                end_date='2024-02-12',
                blocked_days=2,
                property_name='Property 1',
                maintenance_id=2
            ),
            Mock(
                property_id=2,
                start_date='2024-02-01',
                end_date='2024-02-04',
                blocked_days=3,
                property_name='Property 2',
                maintenance_id=3
            )
        ]
        
        result = calculate_lost_income_by_property(reservations, maintenance_blocks)
        
        # Property 1: 150 * (2 + 2) = 600
        # Property 2: 100 * 3 = 300
        assert result[1]['total_lost_income'] == 600.0
        assert result[1]['total_blocked_days'] == 4
        assert result[1]['maintenance_blocks_count'] == 2
        
        assert result[2]['total_lost_income'] == 300.0
        assert result[2]['total_blocked_days'] == 3
        assert result[2]['maintenance_blocks_count'] == 1
    
    def test_date_filtering(self):
        """Test date filtering for maintenance blocks."""
        reservations = [
            Mock(
                property_id=1,
                reservation_revenue=300.0,
                check_in='2024-01-01',
                check_out='2024-01-03',
                reservation_id=1
            )
        ]
        
        maintenance_blocks = [
            Mock(
                property_id=1,
                start_date='2024-01-01',
                end_date='2024-01-03',
                blocked_days=2,
                property_name='Property 1',
                maintenance_id=1
            ),
            Mock(
                property_id=1,
                start_date='2024-03-01',  # Outside filter range
                end_date='2024-03-03',
                blocked_days=2,
                property_name='Property 1',
                maintenance_id=2
            )
        ]
        
        # Filter to February only
        result = calculate_lost_income_by_property(
            reservations, 
            maintenance_blocks,
            start_date='2024-02-01',
            end_date='2024-02-29'
        )
        
        # No maintenance blocks in February, so no results
        assert len(result) == 0


class TestCreateLostIncomeSummary:
    """Test lost income summary creation."""
    
    def test_create_summary(self):
        """Test basic summary creation."""
        reservations = [
            Mock(
                property_id=1,
                reservation_revenue=300.0,
                check_in='2024-01-01',
                check_out='2024-01-03',
                reservation_id=1
            ),
            Mock(
                property_id=2,
                reservation_revenue=200.0,
                check_in='2024-01-01',
                check_out='2024-01-03',
                reservation_id=2
            )
        ]
        
        maintenance_blocks = [
            Mock(
                property_id=1,
                start_date='2024-02-01',
                end_date='2024-02-03',
                blocked_days=2,
                property_name='Property 1',
                maintenance_id=1
            ),
            Mock(
                property_id=2,
                start_date='2024-02-01',
                end_date='2024-02-05',
                blocked_days=4,
                property_name='Property 2',
                maintenance_id=2
            )
        ]
        
        summary = create_lost_income_summary(reservations, maintenance_blocks)
        
        # Should be sorted by lost income descending
        # Property 2: 100 * 4 = 400
        # Property 1: 150 * 2 = 300
        assert len(summary) == 2
        assert summary[0]['property_id'] == 2
        assert summary[0]['lost_income'] == 400.0
        assert summary[1]['property_id'] == 1
        assert summary[1]['lost_income'] == 300.0


class TestValidateMaintenanceBlockData:
    """Test maintenance block data validation."""
    
    def test_valid_maintenance_block(self):
        """Test validation of valid maintenance block."""
        maintenance_block = Mock(
            property_id=1,
            blocked_days=5,
            start_date='2024-01-01',
            end_date='2024-01-06',
            maintenance_id=1
        )
        
        assert validate_maintenance_block_data(maintenance_block) is True
    
    def test_invalid_property_id(self):
        """Test validation with invalid property ID."""
        maintenance_block = Mock(
            property_id=0,  # Invalid
            blocked_days=5,
            start_date='2024-01-01',
            end_date='2024-01-06',
            maintenance_id=1
        )
        
        assert validate_maintenance_block_data(maintenance_block) is False
    
    def test_invalid_blocked_days(self):
        """Test validation with invalid blocked days."""
        maintenance_block = Mock(
            property_id=1,
            blocked_days=0,  # Invalid
            start_date='2024-01-01',
            end_date='2024-01-06',
            maintenance_id=1
        )
        
        assert validate_maintenance_block_data(maintenance_block) is False
    
    def test_invalid_date_range(self):
        """Test validation with invalid date range."""
        maintenance_block = Mock(
            property_id=1,
            blocked_days=5,
            start_date='2024-01-06',  # After end date
            end_date='2024-01-01',
            maintenance_id=1
        )
        
        assert validate_maintenance_block_data(maintenance_block) is False
    
    def test_missing_dates(self):
        """Test validation with missing date fields."""
        maintenance_block = Mock(
            property_id=1,
            blocked_days=5,
            maintenance_id=1
            # Missing start_date and end_date
        )
        
        assert validate_maintenance_block_data(maintenance_block) is False


class TestMaintenanceCalculationError:
    """Test error handling in maintenance calculations."""
    
    def test_calculation_error_propagation(self):
        """Test that calculation errors are properly raised."""
        # This should raise an error due to invalid maintenance block
        with pytest.raises(MaintenanceCalculationError):
            invalid_block = Mock(
                property_id="invalid",  # Should be int
                blocked_days=5,
                start_date='2024-01-01',
                end_date='2024-01-06'
            )
            calculate_lost_income_for_maintenance_block([], invalid_block)


if __name__ == '__main__':
    pytest.main([__file__])