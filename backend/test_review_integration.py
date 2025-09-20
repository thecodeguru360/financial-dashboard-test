"""
Integration tests for review calculation module using real data.

Tests the review aggregation functionality with the actual JSON dataset
to ensure it works correctly with real-world data.
"""

import pytest
import json
from unittest.mock import Mock

from app.services.review_calculator import (
    aggregate_reviews_by_month,
    aggregate_reviews_by_month_and_property,
    aggregate_reviews_by_property,
    create_monthly_review_timeline,
    create_property_review_summary,
    get_review_statistics
)


class TestReviewIntegrationWithRealData:
    """Integration tests using real JSON data."""
    
    @pytest.fixture
    def real_data(self):
        """Load real data from JSON file."""
        with open('data/str_dummy_data_with_booking_date.json', 'r') as f:
            return json.load(f)
    
    @pytest.fixture
    def mock_reviews(self, real_data):
        """Convert real review data to mock objects."""
        reviews = []
        for review_data in real_data['reviews']:
            review = Mock()
            review.review_id = review_data['review_id']
            review.rating = review_data['rating']
            review.review_date = review_data['review_date']
            review.property_id = review_data['property_id']
            review.property_name = review_data['property_name']
            reviews.append(review)
        return reviews
    
    def test_monthly_aggregation_with_real_data(self, mock_reviews):
        """Test monthly aggregation with real dataset."""
        result = aggregate_reviews_by_month(mock_reviews)
        
        # Should have multiple months of data
        assert len(result) > 0
        
        # Check that all months have valid data
        for month, data in result.items():
            assert 'avg_rating' in data
            assert 'review_count' in data
            assert data['avg_rating'] >= 1.0
            assert data['avg_rating'] <= 5.0
            assert data['review_count'] > 0
            
            # Verify month format
            assert len(month) == 7  # YYYY-MM format
            assert month[4] == '-'
        
        print(f"Found {len(result)} months of review data")
        
        # Print sample data for verification
        sample_months = sorted(result.keys())[:3]
        for month in sample_months:
            data = result[month]
            print(f"Month {month}: {data['review_count']} reviews, avg rating {data['avg_rating']}")
    
    def test_property_monthly_aggregation_with_real_data(self, mock_reviews):
        """Test property monthly aggregation with real dataset."""
        result = aggregate_reviews_by_month_and_property(mock_reviews)
        
        # Should have multiple properties
        assert len(result) > 0
        
        # Check that all properties have valid monthly data
        for property_id, monthly_data in result.items():
            assert isinstance(property_id, int)
            assert len(monthly_data) > 0
            
            for month, data in monthly_data.items():
                assert 'avg_rating' in data
                assert 'review_count' in data
                assert data['avg_rating'] >= 1.0
                assert data['avg_rating'] <= 5.0
                assert data['review_count'] > 0
        
        print(f"Found {len(result)} properties with monthly review data")
        
        # Print sample data for verification
        sample_property = list(result.keys())[0]
        sample_months = sorted(result[sample_property].keys())[:2]
        print(f"Property {sample_property} sample months:")
        for month in sample_months:
            data = result[sample_property][month]
            print(f"  {month}: {data['review_count']} reviews, avg rating {data['avg_rating']}")
    
    def test_property_aggregation_with_real_data(self, mock_reviews):
        """Test property aggregation with real dataset."""
        result = aggregate_reviews_by_property(mock_reviews)
        
        # Should have multiple properties
        assert len(result) > 0
        
        # Check that all properties have valid data
        for property_id, data in result.items():
            assert isinstance(property_id, int)
            assert 'avg_rating' in data
            assert 'review_count' in data
            assert 'property_name' in data
            assert 'earliest_review' in data
            assert 'latest_review' in data
            
            assert data['avg_rating'] >= 1.0
            assert data['avg_rating'] <= 5.0
            assert data['review_count'] > 0
            assert data['property_name'] is not None
        
        print(f"Found {len(result)} properties with review data")
        
        # Print top 3 properties by review count
        sorted_properties = sorted(result.items(), key=lambda x: x[1]['review_count'], reverse=True)
        print("Top 3 properties by review count:")
        for property_id, data in sorted_properties[:3]:
            print(f"  Property {property_id} ({data['property_name']}): {data['review_count']} reviews, avg {data['avg_rating']}")
    
    def test_monthly_timeline_with_real_data(self, mock_reviews):
        """Test monthly timeline creation with real dataset."""
        timeline = create_monthly_review_timeline(mock_reviews)
        
        # Should have multiple months
        assert len(timeline) > 0
        
        # Check timeline is sorted by month
        months = [item['month'] for item in timeline]
        assert months == sorted(months)
        
        # Check all timeline items have required fields
        for item in timeline:
            assert 'month' in item
            assert 'avg_rating' in item
            assert 'review_count' in item
            assert item['avg_rating'] >= 1.0
            assert item['avg_rating'] <= 5.0
            assert item['review_count'] > 0
        
        print(f"Timeline has {len(timeline)} months")
        print(f"Date range: {timeline[0]['month']} to {timeline[-1]['month']}")
        
        # Print first and last months
        print(f"First month: {timeline[0]['month']} - {timeline[0]['review_count']} reviews, avg {timeline[0]['avg_rating']}")
        print(f"Last month: {timeline[-1]['month']} - {timeline[-1]['review_count']} reviews, avg {timeline[-1]['avg_rating']}")
    
    def test_property_summary_with_real_data(self, mock_reviews):
        """Test property summary creation with real dataset."""
        summary = create_property_review_summary(mock_reviews)
        
        # Should have multiple properties
        assert len(summary) > 0
        
        # Check summary is sorted by review count (descending)
        review_counts = [item['review_count'] for item in summary]
        assert review_counts == sorted(review_counts, reverse=True)
        
        # Check all summary items have required fields
        for item in summary:
            assert 'property_id' in item
            assert 'property_name' in item
            assert 'avg_rating' in item
            assert 'review_count' in item
            assert 'earliest_review' in item
            assert 'latest_review' in item
            
            assert item['avg_rating'] >= 1.0
            assert item['avg_rating'] <= 5.0
            assert item['review_count'] > 0
        
        print(f"Summary has {len(summary)} properties")
        print(f"Most reviewed property: {summary[0]['property_name']} with {summary[0]['review_count']} reviews")
        print(f"Least reviewed property: {summary[-1]['property_name']} with {summary[-1]['review_count']} reviews")
    
    def test_review_statistics_with_real_data(self, mock_reviews):
        """Test review statistics calculation with real dataset."""
        stats = get_review_statistics(mock_reviews)
        
        # Check all required fields are present
        assert 'total_reviews' in stats
        assert 'avg_rating' in stats
        assert 'min_rating' in stats
        assert 'max_rating' in stats
        assert 'rating_distribution' in stats
        
        # Check values are reasonable
        assert stats['total_reviews'] > 0
        assert stats['avg_rating'] >= 1.0
        assert stats['avg_rating'] <= 5.0
        assert stats['min_rating'] >= 1.0
        assert stats['max_rating'] <= 5.0
        assert stats['min_rating'] <= stats['max_rating']
        
        print(f"Total reviews: {stats['total_reviews']}")
        print(f"Average rating: {stats['avg_rating']}")
        print(f"Rating range: {stats['min_rating']} - {stats['max_rating']}")
        print(f"Rating distribution: {stats['rating_distribution']}")
    
    def test_date_filtering_with_real_data(self, mock_reviews):
        """Test date filtering functionality with real dataset."""
        # Test filtering to 2024 only
        result_2024 = aggregate_reviews_by_month(mock_reviews, '2024-01-01', '2024-12-31')
        
        # All months should be in 2024
        for month in result_2024.keys():
            assert month.startswith('2024')
        
        # Test filtering to first quarter 2024
        result_q1 = aggregate_reviews_by_month(mock_reviews, '2024-01-01', '2024-03-31')
        
        # All months should be in Q1 2024
        for month in result_q1.keys():
            assert month in ['2024-01', '2024-02', '2024-03']
        
        print(f"2024 reviews: {len(result_2024)} months")
        print(f"Q1 2024 reviews: {len(result_q1)} months")
        
        # Verify filtering reduces the dataset
        result_all = aggregate_reviews_by_month(mock_reviews)
        assert len(result_2024) <= len(result_all)
        assert len(result_q1) <= len(result_2024)
    
    def test_property_filtering_with_real_data(self, mock_reviews, real_data):
        """Test that property filtering works correctly."""
        # Get a sample of property IDs
        property_ids = list(set(review['property_id'] for review in real_data['reviews']))
        sample_properties = property_ids[:3]  # First 3 properties
        
        # Filter reviews to only include sample properties
        filtered_reviews = [r for r in mock_reviews if r.property_id in sample_properties]
        
        result = aggregate_reviews_by_property(filtered_reviews)
        
        # Should only have the sample properties
        assert len(result) <= 3
        for property_id in result.keys():
            assert property_id in sample_properties
        
        print(f"Filtered to {len(result)} properties: {list(result.keys())}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])