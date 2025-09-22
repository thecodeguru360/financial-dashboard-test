# Financial Dashboard

Interactive financial dashboard for short-term rental portfolio management system.

## Project Structure

```
financial-dashboard/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI application entry point
│   │   ├── models.py       # Pydantic data models
│   │   ├── api/            # API endpoints
│   │   ├── config/         # Configuration modules
│   │   │   └── cache_config.py
│   │   ├── middleware/     # Custom middleware
│   │   │   └── performance.py
│   │   └── services/       # Business logic services
│   │       ├── cache_manager.py
│   │       ├── cache_warming.py
│   │       ├── data_loader.py
│   │       ├── date_utils.py
│   │       ├── lead_time_calculator.py
│   │       ├── maintenance_calculator.py
│   │       ├── revenue_calculator.py
│   │       └── review_calculator.py
│   ├── data/               # Data files
│   ├── requirements.txt    # Python dependencies
│   └── test_*.py          # Test files
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── charts/     # Chart components
│   │   │   ├── filters/    # Filter components
│   │   │   ├── kpis/       # KPI components
│   │   │   ├── layout/     # Layout components
│   │   │   └── ui/         # UI components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── lib/            # Utility libraries
│   │   ├── providers/      # Context providers
│   │   └── types/          # TypeScript type definitions
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
├── specs/                  # Project specifications
└── package.json            # Root package.json with dev scripts
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd financial-dashboard
   ```

2. **Install all dependencies**
   ```bash
   npm run install-all
   ```

   Or install manually:
   ```bash
   # Backend dependencies
   cd backend
   pip install -r requirements.txt
   
   # Frontend dependencies
   cd ../frontend
   npm install
   ```

### Development

**Start both services concurrently:**
```bash
npm run dev
```

**Or start services individually:**

Backend (FastAPI):
```bash
npm run backend
# or
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (React):
```bash
npm run frontend
# or
cd frontend && npm start
```

### Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Technology Stack

**Backend:**
- FastAPI (Python web framework)
- Pandas (data processing)
- Pydantic (data validation)
- Uvicorn (ASGI server)

**Frontend:**
- React 18 with TypeScript
- Recharts (data visualization)
- TailwindCSS (styling)
- React Query (API state management)

## Calculations

The backend implements several key financial calculations for short-term rental analytics:

### Revenue Calculations

**Nightly Rate Calculation:**
```
Nightly Rate = Total Reservation Revenue ÷ Number of Nights
```
- Handles same-day bookings by treating them as 1 night
- Used for prorating revenue across stay dates

**Revenue Proration:**
```
Daily Revenue = Nightly Rate × 1 (for each stay date)
```
- Revenue is distributed equally across all stay dates (check-in to check-out, excluding check-out date)
- For a 3-night stay, revenue is split across 3 dates

**Property Revenue Aggregation:**
```
Total Property Revenue = Σ(Reservation Revenue) for all reservations
Average Nightly Rate = Total Property Revenue ÷ Total Nights
```

### Lead Time Calculations

**Lead Time:**
```
Lead Time (days) = Check-in Date - Reservation Date
```
- Can be negative for bookings made after check-in date
- Same-day bookings have 0 lead time

**Lead Time Statistics:**
```
Median Lead Time = 50th percentile of all lead times
P90 Lead Time = 90th percentile of all lead times
```

### Maintenance Impact Calculations

**Historical Average Daily Rate:**
```
Property ADR = Total Historical Revenue ÷ Total Historical Nights
```
- Excludes maintenance period from historical calculation
- Falls back to portfolio average if insufficient property data

**Lost Income Calculation:**
```
Lost Income = Average Daily Rate × Blocked Days
```
- Uses property-specific ADR when available
- Falls back to portfolio-wide ADR for properties with insufficient data

**Portfolio Average Daily Rate:**
```
Portfolio ADR = Total Portfolio Revenue ÷ Total Portfolio Nights
```

### Review Calculations

**Monthly Average Rating:**
```
Monthly Avg Rating = Σ(Individual Ratings) ÷ Number of Reviews in Month
```

**Property Average Rating:**
```
Property Avg Rating = Σ(All Property Ratings) ÷ Total Property Reviews
```

**Review Statistics:**
```
Overall Avg Rating = Σ(All Ratings) ÷ Total Reviews
Rating Distribution = Count of reviews per rating value (rounded to 0.5)
```

## Development Notes

- The backend serves API endpoints for data processing and analytics
- The frontend provides interactive charts and filtering capabilities
- CORS is configured to allow frontend-backend communication during development
- Caching is implemented for performance optimization of calculation-heavy operations
- All calculations include comprehensive error handling and validation