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
│   │   └── services/       # Business logic services
│   └── requirements.txt    # Python dependencies
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── types/          # TypeScript type definitions
│   │   └── utils/          # Utility functions
│   └── package.json        # Node.js dependencies
├── data/                   # Data files
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

## Development Notes

- The backend serves API endpoints for data processing and analytics
- The frontend provides interactive charts and filtering capabilities
- CORS is configured to allow frontend-backend communication during development