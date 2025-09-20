import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock the filter components to avoid ES module issues
jest.mock('./components/filters', () => ({
  FilterControls: () => <div data-testid="filter-controls">Filter Controls</div>,
}));

// Mock the API hooks
jest.mock('./hooks/useApiQueries', () => ({
  useProperties: () => ({
    data: [],
    isLoading: false,
    error: null,
    refetch: jest.fn(),
  }),
  useRevenueTimeline: () => ({
    data: { data: [] },
    isLoading: false,
    error: null,
    refetch: jest.fn(),
  }),
  useRevenueByProperty: () => ({
    data: { data: [] },
    isLoading: false,
    error: null,
    refetch: jest.fn(),
  }),
  useMaintenanceLostIncome: () => ({
    data: { data: [] },
    isLoading: false,
    error: null,
    refetch: jest.fn(),
  }),
  useReviewTrends: () => ({
    data: { data: [] },
    isLoading: false,
    error: null,
    refetch: jest.fn(),
  }),
}));

test('renders financial dashboard', () => {
  render(<App />);
  const titleElement = screen.getByText(/Financial Dashboard/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders filter controls', () => {
  render(<App />);
  const filterElement = screen.getByTestId('filter-controls');
  expect(filterElement).toBeInTheDocument();
});
