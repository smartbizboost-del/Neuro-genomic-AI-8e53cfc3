# Neuro-Genomic AI - Complete Setup Guide

## Main Entry Points

### Backend (FastAPI)
- **Entry Point**: `src/api/main.py`
- **Port**: 8000
- **Command**: `python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000`

### Streamlit Dashboard
- **Entry Point**: `src/dashboard/app.py`
- **Port**: 8501
- **Command**: `python -m streamlit run src/dashboard/app.py`

### Unified local startup
- **Command**: `python -m src.run`
- Starts both the backend and dashboard together for local development.

### Legacy Frontend (optional)
- **Location**: `frontend/`
- **Status**: Legacy React prototype, not required for the current unified local workflow.

## Quick Start

Open **two separate terminals** in the project root:

### Terminal 1: FastAPI Backend + Streamlit Dashboard
```bash
source venv/bin/activate
python -m src.run
```

### Optional: Run services separately
```bash
# API only
python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000

# Dashboard only
python -m streamlit run src/dashboard/app.py
```

## Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| FastAPI Backend | http://127.0.0.1:8000/ | API endpoints, assessment data |
| API Docs | http://127.0.0.1:8000/docs | Swagger UI for API testing |
| Streamlit Dashboard | http://127.0.0.1:8501/ | ECG upload, analysis, patient viewer |

## Project Structure

```
src/                           ← MAIN APPLICATION
├── api/
│   ├── main.py              ← FastAPI entry point
│   ├── routes/
│   │   ├── assessment.py
│   │   ├── analysis.py
│   │   └── health.py
│   └── middleware/
├── dashboard/                ← Streamlit dashboard UI
├── core/
├── workers/
└── utils/

frontend/                      ← Legacy React prototype
├── src/
├── package.json
└── vite.config.js

src/run.py                    ← Unified local launcher for backend + dashboard
```
## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              Streamlit Dashboard (src/dashboard/)              │
│  - Secure login and token-based auth                           │
│  - ECG upload, analysis, and clinical visualization            │
│  - Results viewer with explainability and risk scoring         │
└─────────────────────────────────────────────────────────────────┘
                      ↓
         http://127.0.0.1:8501
                      ↓
        ┌─────────────┴─────────────┐
        │                           │
    ┌───▼────────┐          ┌──────▼──────┐
    │  FastAPI   │          │  Streamlit  │
    │   Backend  │          │(src/dashboard)│
    │ (src/api)  │          │             │
    └───┬────────┘          └──────┬──────┘
        │                          │
    :8000                      :8501
        │                          │
        └──────────┬───────────────┘
                   │
            ┌──────▼──────┐
            │  Analysis   │
            │  & Pipeline │
            └─────────────┘
```

## Key Features

### 1. Backend (src/api/main.py)
- FastAPI server with JWT auth and protected routes
- Health checks and operational diagnostics
- Analysis upload and result retrieval
- Assessment endpoint for clinical scoring

### 2. Dashboard (src/dashboard/app.py)
- Streamlit-based clinical dashboard
- Secure login gate and token forwarding
- ECG upload, polling, and result visualization
- Explainability, trajectory, and risk summary panels

### 3. Unified local launcher (src/run.py)
- Starts backend and dashboard together
- Keeps local development workflow centralized
- No React frontend required for the current main flow

## Testing

### Test API Health
```bash
curl http://127.0.0.1:8000/
```

### Test Assessment Endpoint
```bash
curl http://127.0.0.1:8000/api/assessment
```

### Test Streamlit
Open http://127.0.0.1:8501/ in browser

## Troubleshooting

### FastAPI not starting
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill process on port 8000
kill -9 <PID>

# Try different port
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8002
```

### Streamlit issues
```bash
# Clear cache
streamlit cache clear

# Run with debug
streamlit run src/dashboard/app.py --logger.level=debug

# Different port
streamlit run src/dashboard/app.py --server.port 8502
```

## Environment Variables

Create a `.env` file if needed:
```
FASTAPI_ENV=development
DATABASE_URL=sqlite:///./data/neuro_genomic.db
API_TIMEOUT=30
LOG_LEVEL=INFO
```

## Dependencies

### Backend (Python)
- FastAPI
- Uvicorn
- Pydantic
- NumPy
- Pandas
- Scikit-learn

### Frontend (Node.js)
- React 18.3.1
- Vite 5.4.21
- @vitejs/plugin-react

### Analysis (Python)
- Streamlit 1.57.0
- Pandas
- NumPy
- Altair

## Notes

- All three services must be running for full functionality
- Frontend will show a link to Streamlit dashboard
- Backend serves both API requests and assessment data
- Analysis results are stored in Streamlit's session state (not persistent)

---

✅ Ready to launch! Start the three services above.
