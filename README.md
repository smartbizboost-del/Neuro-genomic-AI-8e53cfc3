# 📚 NEURO-GENOMIC AI – COMPLETE DOCUMENTATION

## Professional Documentation for Your Project

---

# PART 1: API DOCUMENTATION

## 1.1 Overview

| **Item** | **Details** |
|----------|-------------|
| **Base URL** | `http://localhost:8000` |
| **Version** | 2.0.0 |
| **Authentication** | JWT (JSON Web Token) |
| **Data Format** | JSON |
| **Documentation** | `/docs` (Swagger UI), `/redoc` (ReDoc) |

---

## 1.2 Endpoints Summary

| **Method** | **Endpoint** | **Description** | **Auth** |
|------------|--------------|-----------------|----------|
| GET | `/` | API information | No |
| GET | `/health` | Health check | No |
| GET | `/ready` | Readiness probe | No |
| GET | `/docs` | Swagger UI | No |
| POST | `/api/v1/auth/register` | User registration | No |
| POST | `/api/v1/auth/login` | User login | No |
| GET | `/api/v1/auth/me` | Current user info | Yes |
| POST | `/api/v1/analysis` | Analyze RR intervals | No |
| GET | `/api/v1/analysis/{id}` | Get stored analysis | Yes |
| POST | `/api/v1/upload` | Upload ECG file | Yes |
| GET | `/api/v1/export/csv` | Export as CSV | Yes |
| GET | `/api/v1/export/json` | Export as JSON | Yes |
| GET | `/api/v1/export/pdf` | Export as PDF | Yes |
| GET | `/api/v1/admin/users` | List all users | Admin |
| PUT | `/api/v1/admin/users/{id}/role` | Update user role | Admin |
| GET | `/api/v1/admin/metrics` | System metrics | Admin |

---

## 1.3 Request/Response Examples

### Register User

**Request:**
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
    "email": "researcher@example.com",
    "password": "securepassword",
    "full_name": "Dr. Jane Researcher",
    "role": "researcher"
}
```

**Response:**
```json
{
    "id": "user_001",
    "email": "researcher@example.com",
    "full_name": "Dr. Jane Researcher",
    "role": "researcher",
    "created_at": "2026-04-09T10:00:00Z"
}
```

### Login

**Request:**
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
    "email": "researcher@example.com",
    "password": "securepassword"
}
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 86400
}
```

### Analyze RR Intervals

**Request:**
```bash
POST /api/v1/analysis
Content-Type: application/json

{
    "rr_intervals": [450, 455, 448, 452, 460, 458, 455],
    "gestational_weeks": 34,
    "patient_id": "PT_001"
}
```

**Response:**
```json
{
    "file_id": "analysis_001",
    "features": {
        "rmssd": 28.5,
        "sdnn": 45.2,
        "lf_hf_ratio": 1.2,
        "sample_entropy": 1.15,
        "mean_rr": 454.2,
        "pnn50": 28.6,
        "lf_power": 0.85,
        "hf_power": 0.71,
        "total_power": 1.56,
        "poincare_sd1": 18.3,
        "poincare_sd2": 42.1,
        "sd1_sd2_ratio": 0.43
    },
    "risk": {
        "normal": 0.85,
        "suspect": 0.12,
        "pathological": 0.03,
        "predicted_class": "Normal"
    },
    "developmental_index": 0.72,
    "interpretation": [
        "RMSSD within normal range for 34 weeks",
        "LF/HF indicates balanced autonomic tone",
        "Sample entropy suggests appropriate neural complexity"
    ],
    "confidence_intervals": {
        "rmssd": {"lower": 26.2, "upper": 30.8, "confidence": 0.95}
    }
}
```

---

# PART 2: DEPLOYMENT DOCUMENTATION

## 2.1 System Requirements

| **Component** | **Minimum** | **Recommended** |
|---------------|-------------|-----------------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Storage | 10 GB | 20 GB |
| OS | Linux (Ubuntu 20.04+) | Linux (Ubuntu 22.04+) |
| Docker | 20.10+ | 24.0+ |
| Python | 3.10+ | 3.12+ |

---

## 2.2 Quick Start (5 Minutes)

```bash
# 1. Clone the repository
git clone https://github.com/smartbizboost-del/Neuro-genomic-AI.git
cd Neuro-genomic-AI

# 2. Copy environment file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Verify installation
curl http://localhost:8000/health

# 5. Open dashboard
# http://localhost:8501
```

---

## 2.3 Docker Services

| **Service** | **Container Name** | **Port** | **Purpose** |
|-------------|-------------------|----------|-------------|
| API | neuro-api | 8000 | FastAPI backend |
| Dashboard | neuro-dashboard | 8501 | Streamlit UI |
| PostgreSQL | neuro-postgres | 5432 | Database |
| Redis | neuro-redis | 6379 | Cache/queues |
| MinIO | neuro-minio | 9000, 9001 | File storage |
| Worker | neuro-worker | — | Celery tasks |

---

## 2.4 Environment Variables

```bash
# Database
DATABASE_URL=postgresql://neuro_user:neuro_pass@postgres:5432/neuro_genomic

# Redis
REDIS_URL=redis://redis:6379/0

# MinIO
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-bytes
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Environment
ENVIRONMENT=production
LOG_LEVEL=info
```

---

# PART 3: USER GUIDE

## 3.1 Dashboard Overview

### Accessing the Dashboard

1. Open browser to `http://localhost:8501`
2. Upload an ECG file (CSV, EDF, or TXT format)
3. Set gestational age (30-42 weeks)
4. Click "Run Analysis"

### Dashboard Sections

| **Section** | **Description** |
|-------------|-----------------|
| **Upload Area** | Drag and drop ECG files |
| **Gestational Age Slider** | Set weeks (30-42) |
| **Developmental Index** | Composite score (0-1) |
| **Risk Classification** | Normal / Suspect / Pathological |
| **HRV Metrics** | RMSSD, SDNN, LF/HF, Entropy |
| **Clinical Interpretation** | Plain English explanation |
| **Uncertainty Visualization** | Confidence intervals |
| **Export Options** | CSV, JSON, PDF |

---

## 3.2 Supported File Formats

| **Format** | **Extension** | **Description** |
|------------|---------------|-----------------|
| CSV | .csv | Comma-separated values with ECG column |
| EDF | .edf | European Data Format |
| TXT | .txt | Tab-separated or space-separated |
| PhysioNet | .hea, .dat | WFDB format |

### Sample CSV Format

```csv
ecg
0.12
0.15
-0.08
-0.22
0.45
...
```

---

## 3.3 Understanding Results

### Developmental Index

| **Score** | **Interpretation** |
|-----------|-------------------|
| 0.8 - 1.0 | Advanced maturation |
| 0.6 - 0.8 | Age-appropriate development |
| 0.4 - 0.6 | Mild delay – monitor closely |
| 0.0 - 0.4 | Significant delay – refer to specialist |

### Risk Classification

| **Class** | **Meaning** | **Recommended Action** |
|-----------|-------------|------------------------|
| Normal | Development on track | Routine care |
| Suspect | Monitor closely | Repeat in 2 weeks |
| Pathological | Intervention may be needed | Refer to MFM specialist |

---

# PART 4: DEVELOPMENT GUIDE

## 4.1 Project Structure

```
neuro-genomic-ai/
├── src/
│   ├── api/           # FastAPI backend
│   ├── core/          # Core algorithms
│   ├── workers/       # Celery tasks
│   ├── dashboard/     # Streamlit UI
│   └── utils/         # Helper functions
├── tests/             # Unit tests (329 tests)
├── website/           # Marketing website
├── docker/            # Dockerfiles
├── infrastructure/    # Terraform + K8s
├── requirements/      # Python dependencies
└── config/            # Configuration files
```

---

## 4.2 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=src --cov-report=term

# Run specific test file
pytest tests/test_features.py -v

# Run with HTML report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html
```

---

## 4.3 Adding New Features

### Add New API Endpoint

```python
# src/api/routes/new_feature.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/new-endpoint")
async def new_endpoint():
    return {"message": "New feature"}
```

Then register in `src/api/main.py`:

```python
from src.api.routes import new_feature
app.include_router(new_feature.router)
```

### Add New HRV Feature

```python
# src/core/features/new_feature.py
def calculate_new_feature(rr_intervals):
    # Your implementation
    return value
```

---

# PART 5: TROUBLESHOOTING

## 5.1 Common Issues & Solutions

| **Issue** | **Solution** |
|-----------|--------------|
| Port 8000 already in use | `lsof -i :8000` then `kill -9 <PID>` |
| Redis connection refused | `docker-compose up -d redis` |
| Database connection failed | `docker exec neuro-postgres pg_isready -U neuro_user` |
| MinIO endpoint error | Ensure `MINIO_ENDPOINT=http://minio:9000` |
| Tests failing | `pip install -r requirements/base.txt` |
| Dashboard not loading | `streamlit run src/dashboard/app.py` |

---

## 5.2 Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker logs neuro-api -f
docker logs neuro-worker -f
docker logs neuro-postgres -f

# View last 100 lines
docker logs neuro-api --tail 100
```

---

## 5.3 Reset Everything

```bash
# Stop all containers
docker-compose down

# Remove volumes (reset database)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

---

# PART 6: API REFERENCE (Quick Card)

## Authentication

```bash
# Get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}'

# Use token
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <token>"
```

## Analysis

```bash
# Analyze RR intervals
curl -X POST http://localhost:8000/api/v1/analysis \
  -H "Content-Type: application/json" \
  -d '{"rr_intervals": [450,455,448],"gestational_weeks":34}'
```

## Export

```bash
# Export as CSV
curl -X GET "http://localhost:8000/api/v1/export/csv?analysis_id=abc123"

# Export as PDF
curl -X GET "http://localhost:8000/api/v1/export/pdf?analysis_id=abc123"
```

---

# PART 7: CONTACT & SUPPORT

| **Purpose** | **Contact** |
|-------------|-------------|
| Technical Support | demoivresphenomenal@gmail.com |
| Partnership Inquiries | collins.omondi@students.kirinyaga.ac.ke |
| GitHub Issues | https://github.com/smartbizboost-del/Neuro-genomic-AI/issues |

---

**Documentation Version:** 2.0  
**Last Updated:** April 2026  
**Status:** ✅ Complete

---

*Your friend and partner in innovation* 🤝
