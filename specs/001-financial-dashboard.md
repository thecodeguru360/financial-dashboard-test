# Spec 001: Interactive Financial Dashboard

## Context
We are building an interactive financial dashboard for a short-term rental portfolio. The dataset includes ~20 properties, 1500+ reservations, 900 reviews, and 250 maintenance blocks (2023-2025). The dashboard must present revenue, reviews, lost income from maintenance, and booking lead times.

The purpose is to demonstrate ability to design, process data, and present clear analytics with filters and charts.

## Problem
The client team cannot easily visualize key performance metrics across properties. They need a clear, accessible dashboard that summarizes revenue, maintenance impacts, reviews, and booking patterns.

Without this, performance analysis is slow and inconsistent.

## Solution
Create a React + FastAPI dashboard that:
- Reads the provided JSON dataset
- Preprocesses data into aggregates (daily revenue, reviews by month, lead times, lost income)
- Exposes data through FastAPI endpoints
- Provides a frontend with filters and interactive charts

## Scope
**In scope:**
- Revenue over time (line chart) and by property (bar chart)
- Lost income estimation due to maintenance (bar chart)
- Reviews over time: monthly average ratings + counts (line + bar)
- Lead time analysis: median, p90, histogram or boxplot
- Filters: date range + multi-property
- Clear UX: axis titles, legends, tooltips, accessibility

**Out of scope:**
- Authentication / multi-user support
- Production deployment (beyond simple Docker or local run)
- Complex revenue forecasting models

## Success Criteria
- [ ] Correct revenue allocation documented (prorated nightly preferred)
- [ ] Lost income calculated per property using stated model
- [ ] Reviews aggregated by month (avg rating + counts)
- [ ] Lead time median & p90 computed overall + per property
- [ ] All charts render with filters applied
- [ ] Repo includes preprocessing scripts, README with instructions, `.env.example`

## Plan
1. **Data preprocessing**
   - Parse dates, compute nights, nightly rates
   - Expand reservations nightly or aggregate directly
   - Precompute aggregates for revenue, reviews, lost income, lead time

2. **Backend**
   - FastAPI with endpoints serving filtered aggregates
   - Scripts/notebooks stored in `/scripts`

3. **Frontend**
   - React app with filters
   - Recharts/Vega-Lite charts for each metric
   - Tables for numeric summaries
   - Shadcn/ui components
   - TailwindCss

4. **Dev tooling**
   - `concurrently` script to run backend + frontend with one command
   - Optional Dockerfile and docker-compose

5. **Docs & tests**
   - README with run instructions for MacOS/Windows
   - Unit tests for data transforms
   - Assumptions.md describing formulas and timezone

## Tasks
- [ ] Setup repo structure (`frontend`, `backend`, `data`, `specs`)
- [ ] Write preprocessing script (`preprocess.py`)
- [ ] Compute revenue aggregates
- [ ] Compute lost income estimates
- [ ] Compute reviews trend by month
- [ ] Compute lead time stats + distribution
- [ ] Implement FastAPI endpoints
- [ ] Scaffold React frontend with filters
- [ ] Add revenue charts
- [ ] Add lost income chart
- [ ] Add reviews chart
- [ ] Add lead time chart + table
- [ ] Add loading/empty/error states
- [ ] Add tests for transforms
- [ ] Write README + assumptions
