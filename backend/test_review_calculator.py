"""
Unit tests for review calculation and aggregation module.

Tests cover monthly review aggregation, property-based aggregation,
date filtering, and edge cases like missing data and invalid inputs.
"""

import pytest
from datetime import date, datetime
from unittest.mock import Mock

from app.services.review_calculator import (
    validate_review_data,
    aggregate_reviews_by_month,
    aggregate_reviews_by_month_and_property,
    aggregate_reviews_by_property,
    create_monthly_review_timeline,
    create_property_review_summary,
    fill_missing_months,
    get_review_statistics,
    ReviewCalculationError
)
from app.services.date_utils import DateParsingError


class TestValidateReviewData:
    """Test review data validation."""
    
    def test_valid_review_data(self):
        """Test validation with valid review data."""
        assert validate_review_data(1, 4.5, '2024-01-15') == True
        assert validate_review_data(2, 5.0, '2023-12-01') == True
        assert validate_review_data(3, 1.0, '2024-06-30') == True
    
    def test_invalid_rating_type(self):
        """Test validation with non-numeric rating."""
        assert validate_review_data(1, "4.5", '2024-01-15') == False
        assert validate_review_data(2, None, '2024-01-15') == False
    
    def test_invalid_rating_range(self):
        """Test validation with rating outside valid range."""
        assert validate_review_data(1, 0.5, '2024-01-15') == False
        assert validate_review_data(2, 5.5, '2024-01-15') == False
        assert validate_review_data(3, -1.0, '2024-01-15') == False
    
    def test_invalid_date_format(self):
        """Test validation with invalid date format."""
        assert validate_review_data(1, 4.5, '2024/01/15') == False
        assert validate_review_data(2, 4.5, '15-01-2024') == False
        assert validate_review_data(3, 4.5, 'invalid-date') == False
        assert validate_review_data(4, 4.5, '') == False


class TestAggregateReviewsByMonth:
    """Test monthly review aggregation."""
    
    def create_mock_review(self, review_id, rating, review_date, property_id=1):
        """Create a mock review object."""
        review = Mock()
        review.review_id = review_id
        review.rating = rating
        review.review_date = review_date
        review.property_id = property_id
        return review
    
    def test_basic_monthly_aggregation(self):
        """Test basic monthly aggregation functionality."""
        reviews = [
            self.create_mock_review(1, 4.5, '2024-01-15'),
            self.create_mock_review(2, 4.0, '2024-01-20'),
            self.create_mock_review(3, 5.0, '2024-02-10'),
            self.create_mock_review(4, 3.5, '2024-02-15'),
            self.create_mock_review(5, 4.5, '2024-02-20')
        ]
        
        result = aggregate_reviews_by_month(reviews)
        
        # Check January data
        assert '2024-01' in result
        assert result['2024-01']['avg_rating'] == 4.25  # (4.5 + 4.0) / 2
        assert result['2024-01']['review_count'] == 2
        
        # Check February data
        assert '2024-02' in result
        assert result['2024-02']['avg_rating'] == 4.33  # (5.0 + 3.5 + 4.5) / 3
        assert result['2024-02']['review_count'] == 3
    
    def test_monthly_aggregation_with_date_filters(self):
        """Test monthly aggregation with date range filters."""
        reviews = [
            self.create_mock_review(1, 4.5, '2023-12-15'),
            self.create_mock_review(2, 4.0, '2024-01-20'),
            self.create_mock_review(3, 5.0, '2024-02-10'),
            self.create_mock_review(4, 3.5, '2024-03-15')
        ]
        
        # Filter to only January-February 2024
        result = aggregate_reviews_by_month(reviews, '2024-01-01', '2024-02-28')
        
        assert '2023-12' not in result  # Filtered out
        assert '2024-01' in result
        assert '2024-02' in result
        assert '2024-03' not in result  # Filtered out
        
        assert result['2024-01']['review_count'] == 1
        assert result['2024-02']['review_count'] == 1
    
    def test_empty_reviews_list(self):
        """Test aggregation with empty reviews list."""
        result = aggregate_reviews_by_month([])
        assert result == {}
    
    def test_invalid_reviews_skipped(self):
        """Test that invalid reviews are skipped."""
        reviews = [
            self.create_mock_review(1, 4.5, '2024-01-15'),  # Valid
            self.create_mock_review(2, 6.0, '2024-01-20'),  # Invalid rating
            self.create_mock_review(3, 4.0, 'invalid-date')  # Invalid date
        ]
        
        result = aggregate_reviews_by_month(reviews)
        
        # Only valid review should be included
        assert '2024-01' in result
        assert result['2024-01']['review_count'] == 1
        assert result['2024-01']['avg_rating'] == 4.5
    
    def test_single_review_per_month(self):
        """Test aggregation with single review per month."""
        reviews = [
            self.create_mock_review(1, 4.7, '2024-01-15'),
            self.create_mock_review(2, 3.8, '2024-02-10')
        ]
        
        result = aggregate_reviews_by_month(reviews)
        
        assert result['2024-01']['avg_rating'] == 4.7
        assert result['2024-01']['review_count'] == 1
        assert result['2024-02']['avg_rating'] == 3.8
        assert result['2024-02']['review_count'] == 1


class TestAggregateReviewsByMonthAndProperty:
    """Test monthly review aggregation by property."""
    
    def create_mock_review(self, review_id, rating, review_date, property_id):
        """Create a mock review object."""
        review = Mock()
        review.review_id = review_id
        review.rating = rating
        review.review_date = review_date
        review.property_id = property_id
        return review
    
    def test_property_monthly_aggregation(self):
        """Test aggregation by property and month."""
        reviews = [
            self.create_mock_review(1, 4.5, '2024-01-15', 1),
            self.create_mock_review(2, 4.0, '2024-01-20', 1),
            self.create_mock_review(3, 5.0, '2024-01-10', 2),
            self.create_mock_review(4, 3.5, '2024-02-15', 1),
            self.create_mock_review(5, 4.5, '2024-02-20', 2)
        ]
        
        result = aggregate_reviews_by_month_and_property(reviews)
        
        # Check property 1, January
        assert 1 in result
        assert '2024-01' in result[1]
        assert result[1]['2024-01']['avg_rating'] == 4.25  # (4.5 + 4.0) / 2
        assert result[1]['2024-01']['review_count'] == 2
        
        # Check property 1, February
        assert '2024-02' in result[1]
        assert result[1]['2024-02']['avg_rating'] == 3.5
        assert result[1]['2024-02']['review_count'] == 1
        
        # Check property 2, January
        assert 2 in result
        assert '2024-01' in result[2]
        assert result[2]['2024-01']['avg_rating'] == 5.0
        assert result[2]['2024-01']['review_count'] == 1
        
        # Check property 2, February
        assert '2024-02' in result[2]
        assert result[2]['2024-02']['avg_rating'] == 4.5
        assert result[2]['2024-02']['review_count'] == 1
    
    def test_property_monthly_with_filters(self):
        """Test property monthly aggregation with date filters."""
        reviews = [
            self.create_mock_review(1, 4.5, '2023-12-15', 1),
            self.create_mock_review(2, 4.0, '2024-01-20', 1),
            self.create_mock_review(3, 5.0, '2024-02-10', 2),
            self.create_mock_review(4, 3.5, '2024-03-15', 1)
        ]
        
        result = aggregate_reviews_by_month_and_property(reviews, '2024-01-01', '2024-02-28')
        
        # Property 1 should only have January data
        assert 1 in result
        assert '2024-01' in result[1]
        assert '2023-12' not in result[1]
        assert '2024-03' not in result[1]
        
        # Property 2 should only have February data
        assert 2 in result
        assert '2024-02' in result[2]


class TestAggregateReviewsByProperty:
    """Test property-level review aggregation."""
    
    def create_mock_review(self, review_id, rating, review_date, property_id, property_name=None):
        """Create a mock review object."""
        review = Mock()
        review.review_id = review_id
        review.rating = rating
        review.review_date = review_date
        review.property_id = property_id
        review.property_name = property_name or f'Property {property_id}'
        return review
    
    def test_property_aggregation(self):
        """Test basic property aggregation."""
        reviews = [
            self.create_mock_review(1, 4.5, '2024-01-15', 1, 'Blue Loft #1'),
            self.create_mock_review(2, 4.0, '2024-02-20', 1, 'Blue Loft #1'),
            self.create_mock_review(3, 5.0, '2024-01-10', 2, 'Red Villa #2'),
            self.create_mock_review(4, 3.5, '2024-03-15', 2, 'Red Villa #2'),
            self.create_mock_review(5, 4.5, '2024-02-20', 2, 'Red Villa #2')
        ]
        
        result = aggregate_reviews_by_property(reviews)
        
        # Check property 1
        assert 1 in result
        assert result[1]['avg_rating'] == 4.25  # (4.5 + 4.0) / 2
        assert result[1]['review_count'] == 2
        assert result[1]['property_name'] == 'Blue Loft #1'
        assert result[1]['earliest_review'] == '2024-01-15'
        assert result[1]['latest_review'] == '2024-02-20'
        
        # Check property 2
        assert 2 in result
        assert result[2]['avg_rating'] == 4.33  # (5.0 + 3.5 + 4.5) / 3
        assert result[2]['review_count'] == 3
        assert result[2]['property_name'] == 'Red Villa #2'
        assert result[2]['earliest_review'] == '2024-01-10'
        assert result[2]['latest_review'] == '2024-03-15'
    
    def test_property_aggregation_with_filters(self):
        """Test property aggregation with date filters."""
        reviews = [
            self.create_mock_review(1, 4.5, '2023-12-15', 1),
            self.create_mock_review(2, 4.0, '2024-01-20', 1),
            self.create_mock_review(3, 5.0, '2024-02-10', 1),
            self.create_mock_review(4, 3.5, '2024-03-15', 1)
        ]
        
        result = aggregate_reviews_by_property(reviews, '2024-01-01', '2024-02-28')
        
        # Should only include January and February reviews
        assert 1 in result
        assert result[1]['review_count'] == 2  # Jan and Feb only
        assert result[1]['avg_rating'] == 4.5  # (4.0 + 5.0) / 2


class TestCreateMonthlyReviewTimeline:
    """Test monthly review timeline creation."""
    
    def create_mock_review(self, review_id, rating, review_date, property_id=1):
        """Create a mock review object."""
        review = Mock()
        review.review_id = review_id
        review.rating = rating
        review.review_date = review_date
        review.property_id = property_id
        return review
    
    def test_timeline_creation(self):
        """Test timeline creation and sorting."""
        reviews = [
            self.create_mock_review(1, 4.5, '2024-02-15'),
            self.create_mock_review(2, 4.0, '2024-01-20'),
            self.create_mock_review(3, 5.0, '2024-03-10')
        ]
        
        timeline = create_monthly_review_timeline(reviews)
        
        # Should be sorted by month
        assert len(timeline) == 3
        assert timeline[0]['month'] == '2024-01'
        assert timeline[1]['month'] == '2024-02'
        assert timeline[2]['month'] == '2024-03'
        
        # Check data structure
        assert timeline[0]['avg_rating'] == 4.0
        assert timeline[0]['review_count'] == 1
        assert timeline[1]['avg_rating'] == 4.5
        assert timeline[1]['review_count'] == 1


class TestCreatePropertyReviewSummary:
    """Test property review summary creation."""
    
    def create_mock_review(self, review_id, rating, review_date, property_id, property_name=None):
        """Create a mock review object."""
        review = Mock()
        review.review_id = review_id
        review.rating = rating
        review.review_date = review_date
        review.property_id = property_id
        review.property_name = property_name or f'Property {property_id}'
        return review
    
    def test_summary_creation_and_sorting(self):
        """Test summary creation and sorting by review count."""
        reviews = [
            self.create_mock_review(1, 4.5, '2024-01-15', 1, 'Property A'),  # 1 review
            self.create_mock_review(2, 4.0, '2024-02-20', 2, 'Property B'),  # 3 reviews
            self.create_mock_review(3, 5.0, '2024-01-10', 2, 'Property B'),
            self.create_mock_review(4, 3.5, '2024-03-15', 2, 'Property B'),
            self.create_mock_review(5, 4.5, '2024-02-20', 3, 'Property C'),  # 2 reviews
            self.create_mock_review(6, 4.0, '2024-03-10', 3, 'Property C')
        ]
        
        summary = create_property_review_summary(reviews)
        
        # Should be sorted by review count descending
        assert len(summary) == 3
        assert summary[0]['property_id'] == 2  # 3 reviews
        assert summary[0]['review_count'] == 3
        assert summary[1]['property_id'] == 3  # 2 reviews
        assert summary[1]['review_count'] == 2
        assert summary[2]['property_id'] == 1  # 1 review
        assert summary[2]['review_count'] == 1


class TestFillMissingMonths:
    """Test filling missing months functionality."""
    
    def test_fill_missing_months(self):
        """Test filling gaps in monthly data."""
        monthly_data = {
            '2024-01': {'avg_rating': 4.5, 'review_count': 2},
            '2024-03': {'avg_rating': 4.0, 'review_count': 1}
        }
        
        filled_data = fill_missing_months(monthly_data, '2024-01', '2024-03')
        
        # Should have all three months
        assert '2024-01' in filled_data
        assert '2024-02' in filled_data
        assert '2024-03' in filled_data
        
        # Original data should be preserved
        assert filled_data['2024-01']['avg_rating'] == 4.5
        assert filled_data['2024-03']['avg_rating'] == 4.0
        
        # Missing month should have zero values
        assert filled_data['2024-02']['avg_rating'] == 0.0
        assert filled_data['2024-02']['review_count'] == 0
    
    def test_fill_across_year_boundary(self):
        """Test filling months across year boundary."""
        monthly_data = {
            '2023-12': {'avg_rating': 4.5, 'review_count': 2},
            '2024-02': {'avg_rating': 4.0, 'review_count': 1}
        }
        
        filled_data = fill_missing_months(monthly_data, '2023-12', '2024-02')
        
        # Should have all three months
        assert '2023-12' in filled_data
        assert '2024-01' in filled_data
        assert '2024-02' in filled_data
        
        # Missing January should have zero values
        assert filled_data['2024-01']['avg_rating'] == 0.0
        assert filled_data['2024-01']['review_count'] == 0


class TestGetReviewStatistics:
    """Test review statistics calculation."""
    
    def create_mock_review(self, review_id, rating, review_date, property_id=1):
        """Create a mock review object."""
        review = Mock()
        review.review_id = review_id
        review.rating = rating
        review.review_date = review_date
        review.property_id = property_id
        return review
    
    def test_review_statistics(self):
        """Test calculation of review statistics."""
        reviews = [
            self.create_mock_review(1, 4.5, '2024-01-15'),
            self.create_mock_review(2, 4.0, '2024-02-20'),
            self.create_mock_review(3, 5.0, '2024-01-10'),
            self.create_mock_review(4, 3.5, '2024-03-15'),
            self.create_mock_review(5, 4.5, '2024-02-20')
        ]
        
        stats = get_review_statistics(reviews)
        
        assert stats['total_reviews'] == 5
        assert stats['avg_rating'] == 4.3  # (4.5 + 4.0 + 5.0 + 3.5 + 4.5) / 5
        assert stats['min_rating'] == 3.5
        assert stats['max_rating'] == 5.0
        
        # Check rating distribution
        assert 4.5 in stats['rating_distribution']
        assert stats['rating_distribution'][4.5] == 2  # Two 4.5 ratings
    
    def test_empty_reviews_statistics(self):
        """Test statistics with empty reviews list."""
        stats = get_review_statistics([])
        
        assert stats['total_reviews'] == 0
        assert stats['avg_rating'] == 0.0
        assert stats['min_rating'] is None
        assert stats['max_rating'] is None
        assert stats['rating_distribution'] == {}
    
    def test_statistics_with_invalid_reviews(self):
        """Test statistics calculation skipping invalid reviews."""
        reviews = [
            self.create_mock_review(1, 4.5, '2024-01-15'),  # Valid
            self.create_mock_review(2, 6.0, '2024-02-20'),  # Invalid rating
            self.create_mock_review(3, 4.0, 'invalid-date')  # Invalid date
        ]
        
        stats = get_review_statistics(reviews)
        
        # Should only count valid review
        assert stats['total_reviews'] == 1
        assert stats['avg_rating'] == 4.5


if __name__ == '__main__':
    pytest.main([__file__])