# Requirements Document

## Introduction

This project involves building an interactive financial dashboard for a short-term rental portfolio management system. The dashboard will analyze and visualize key performance metrics across approximately 20 properties, processing data from 1500+ reservations, 900+ reviews, and 250+ maintenance blocks spanning 2023-2025. The system must provide clear, accessible analytics with interactive filters and charts to enable efficient performance analysis and decision-making for property managers.

## Requirements

### Requirement 1: Revenue Analytics and Visualization

**User Story:** As a property manager, I want to view revenue analytics across time periods and properties, so that I can track financial performance and identify trends.

#### Acceptance Criteria

1. WHEN I access the dashboard THEN the system SHALL display a line chart showing revenue over time with daily granularity
2. WHEN I view revenue analytics THEN the system SHALL display a bar chart showing total revenue by property
3. WHEN I select a date range filter THEN the system SHALL update revenue charts to show data only within the selected period
4. WHEN I select specific properties THEN the system SHALL update revenue charts to show data only for selected properties
5. IF reservation data spans multiple days THEN the system SHALL prorate revenue across nights using nightly rate calculations

### Requirement 2: Maintenance Impact Analysis

**User Story:** As a property manager, I want to understand lost income due to maintenance blocks, so that I can assess the financial impact of property maintenance.

#### Acceptance Criteria

1. WHEN I view maintenance analytics THEN the system SHALL display a bar chart showing estimated lost income per property due to maintenance blocks
2. WHEN calculating lost income THEN the system SHALL use historical average daily rates for each property during blocked periods
3. WHEN I apply date range filters THEN the system SHALL update lost income calculations to reflect only maintenance blocks within the selected period
4. WHEN I apply property filters THEN the system SHALL update lost income calculations to show only selected properties

### Requirement 3: Review Trend Analysis

**User Story:** As a property manager, I want to track review trends over time, so that I can monitor guest satisfaction and service quality.

#### Acceptance Criteria

1. WHEN I access review analytics THEN the system SHALL display monthly average ratings as a line chart
2. WHEN I view review analytics THEN the system SHALL display monthly review counts as a bar chart overlaid or adjacent to the ratings chart
3. WHEN I apply date range filters THEN the system SHALL update review charts to show data only within the selected period
4. WHEN I apply property filters THEN the system SHALL update review charts to aggregate data only for selected properties
5. WHEN aggregating monthly data THEN the system SHALL calculate accurate average ratings and total counts per month

### Requirement 4: Booking Lead Time Analysis

**User Story:** As a property manager, I want to analyze booking lead times, so that I can understand guest booking patterns and optimize pricing strategies.

#### Acceptance Criteria

1. WHEN I access lead time analytics THEN the system SHALL display median lead time across all bookings
2. WHEN I view lead time analytics THEN the system SHALL display 90th percentile (p90) lead time statistics
3. WHEN I access lead time analytics THEN the system SHALL display a histogram or boxplot showing lead time distribution
4. WHEN I apply property filters THEN the system SHALL calculate lead time statistics for selected properties only
5. WHEN I apply date range filters THEN the system SHALL calculate lead time statistics for reservations within the selected period
6. WHEN calculating lead time THEN the system SHALL compute days between reservation_date and check_in date

### Requirement 5: Interactive Filtering and User Experience

**User Story:** As a property manager, I want to filter data by date ranges and properties, so that I can focus my analysis on specific time periods or property subsets.

#### Acceptance Criteria

1. WHEN I access the dashboard THEN the system SHALL provide a date range picker for filtering all analytics
2. WHEN I access the dashboard THEN the system SHALL provide a multi-select property filter
3. WHEN I change any filter THEN the system SHALL update all charts and statistics within 2 seconds
4. WHEN charts are displayed THEN the system SHALL include clear axis titles, legends, and tooltips
5. WHEN I hover over chart elements THEN the system SHALL display detailed information in tooltips
6. WHEN charts are rendered THEN the system SHALL meet accessibility standards for color contrast and screen readers

### Requirement 6: Data Processing and API

**User Story:** As a developer, I want a robust backend API that processes the raw data efficiently, so that the frontend can display analytics quickly and reliably.

#### Acceptance Criteria

1. WHEN the system starts THEN the backend SHALL preprocess the JSON dataset into optimized aggregates
2. WHEN the frontend requests data THEN the API SHALL respond with filtered aggregates within 500ms
3. WHEN processing reservations THEN the system SHALL correctly parse all date fields and handle timezone considerations
4. WHEN calculating nightly rates THEN the system SHALL divide total reservation revenue by number of nights
5. WHEN the API receives filter parameters THEN the system SHALL return only data matching the specified criteria
6. WHEN errors occur during data processing THEN the system SHALL return appropriate HTTP status codes and error messages

### Requirement 7: Development and Deployment Setup

**User Story:** As a developer, I want clear setup instructions and development tools, so that I can run and maintain the application efficiently.

#### Acceptance Criteria

1. WHEN setting up the project THEN the system SHALL include a README with clear installation instructions for macOS and Windows
2. WHEN running the application THEN the system SHALL provide a single command to start both backend and frontend services
3. WHEN the project is set up THEN the system SHALL include a .env.example file with required environment variables
4. WHEN running tests THEN the system SHALL include unit tests for all data transformation functions
5. WHEN documenting the system THEN the project SHALL include an assumptions.md file describing calculation formulas and timezone handling
