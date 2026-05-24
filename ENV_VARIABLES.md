# Environment Variables Configuration

This file documents all environment variables for the Neuro-Genomic AI application across different deployment scenarios.

## Auto-Detection

The application **automatically detects** its environment and configures itself accordingly:

- **Local**: `http://127.0.0.1:8000`, SQLite database, no auth required
- **Docker Compose**: `http://api:8000`, PostgreSQL, Redis, MinIO
- **Streamlit Cloud**: Requires explicit `API_URL`
- **Azure**: Detected from cloud-init, PostgreSQL + Azure Storage
- **ngrok/Generic Cloud**: Detected from public `API_URL`

## Explicit Configuration (Optional)

Override auto-detection by setting these variables:

### API Configuration

| Variable | Default | Local | Docker | Cloud | Purpose |
|----------|---------|-------|--------|-------|---------|
| `API_URL` | Auto-detected | `http://127.0.0.1:8000` | `http://api:8000` | **Required** | Backend API endpoint |
| `API_TOKEN` | *(empty)* | - | - | - | Optional API authentication token |

### Database Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | Auto-detected | PostgreSQL/SQLite connection string |
| `POSTGRES_USER` | `neuro_user` | PostgreSQL username (docker-compose) |
| `POSTGRES_PASSWORD` | `neuro_pass` | PostgreSQL password (docker-compose) |
| `POSTGRES_DB` | `neuro_genomic` | PostgreSQL database name |

### Cache Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `REDIS_URL` | Auto-detected | Redis connection for caching/tasks |

### Storage Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `STORAGE_BACKEND` | Auto-detected | `local`, `s3`, or `minio` |
| `S3_BUCKET_NAME` | `neuro-genomic-ai` | AWS S3 bucket for uploads |
| `MINIO_ENDPOINT` | `http://minio:9000` | MinIO endpoint (docker-compose) |
| `MINIO_ACCESS_KEY` | `minioadmin` | MinIO access key |
| `MINIO_SECRET_KEY` | `minioadmin` | MinIO secret key |
| `LOCAL_UPLOAD_DIR` | `./data/uploads` | Local directory for file uploads |

### Deployment Environment

| Variable | Purpose |
|----------|---------|
| `DEBUG` | Enable debug logging (`true`/`false`) |
| `DOCKER_COMPOSE` | Set `true` if running in docker-compose |
| `AZURE_DEPLOYMENT` | Set `true` if running on Azure VM |
| `STREAMLIT_APP_ID` | *(auto-set by Streamlit Cloud)* |

## Setup Examples

### Local Development

```bash
# PowerShell
$env:API_URL = "http://127.0.0.1:8000"
$env:DEBUG = "true"
streamlit run streamlit_app.py
```

```bash
# Bash/Linux
export API_URL="http://127.0.0.1:8000"
export DEBUG="true"
streamlit run streamlit_app.py
```

### Docker Compose

```bash
docker compose up -d
# Auto-configured, no env vars needed
```

### Streamlit Cloud + ngrok

**Terminal 1 (ngrok tunnel):**
```bash
ngrok http 8000
# Note the forwarding URL: https://abc123.ngrok-free.dev
```

**Streamlit Cloud Settings → Secrets:**
```toml
API_URL = "https://abc123.ngrok-free.dev"
```

### Streamlit Cloud + Azure

**Terminal (Azure deployment):**
```powershell
az login
.\deploy-azure.ps1
# Note the public IP: 20.123.456.789
```

**Streamlit Cloud Settings → Secrets:**
```toml
API_URL = "http://20.123.456.789:8000"
```

### Streamlit Cloud + Generic Backend

```toml
API_URL = "https://your-backend.example.com"
DATABASE_URL = "postgresql://user:pass@db.example.com/neuro_genomic"
REDIS_URL = "redis://cache.example.com:6379/0"
```

## Quick Start Checklist

1. **Determine your environment:** Local? Docker? Cloud?
2. **Set required variables:**
   - Cloud deployments: Must set `API_URL`
   - Local: Usually no vars needed (auto-detected)
   - Docker Compose: No vars needed (auto-detected)
3. **Start the app:**
   - Local: `streamlit run streamlit_app.py`
   - Docker: `docker compose up -d`
   - Cloud: Push to GitHub (auto-deployed)
4. **Verify:** Check `http://localhost:8000/health` (or your backend URL)

## Troubleshooting

### "API_URL not configured" error
- Local? Set `API_URL=http://127.0.0.1:8000`
- Cloud? Check Streamlit Cloud Secrets page
- ngrok? Make sure ngrok tunnel is running

### "Connection refused" on upload
- Verify backend is running: `curl http://localhost:8000/health`
- Check `API_URL` is correct (no localhost if using cloud)
- For ngrok: Check tunnel is still active

### Wrong database being used
- Local should use SQLite: check `DATABASE_URL` not set
- Production should use PostgreSQL: set `DATABASE_URL` explicitly if needed

## Feature Availability by Environment

| Feature | Local | Docker | Cloud | Azure |
|---------|-------|--------|-------|-------|
| File Upload | ✅ | ✅ | ✅ | ✅ |
| ECG Analysis | ✅ | ✅ | ✅ | ✅ |
| Auth | ✅ | ✅ | ✅ | ✅ |
| Export | ❌ | ✅ | ✅ | ✅ |
| Admin Dashboard | ✅ | ✅ | ❌ | ❌ |
| Background Tasks | ❌ | ✅ | ❌ | ✅ |
| Caching | ❌ | ✅ | ✅ | ✅ |
