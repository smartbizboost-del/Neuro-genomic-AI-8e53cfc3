# 🧬 Neuro-Genomic AI

[![CI/CD Pipeline](https://github.com/neuro-genomic-ai/core/actions/workflows/ci.yml/badge.svg)](https://github.com/neuro-genomic-ai/core/actions/workflows/ci.yml)
[![Code Coverage](https://codecov.io/gh/neuro-genomic-ai/core/branch/main/graph/badge.svg)](https://codecov.io/gh/neuro-genomic-ai/core)
[![Docker Pulls](https://img.shields.io/docker/pulls/neurogenomic/api)](https://hub.docker.com/r/neurogenomic/api)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![OCI Ready](https://img.shields.io/badge/OCI-Ready-orange.svg)](https://www.oracle.com/cloud/)

> **Ethical AI for Fetal Development Monitoring**  
> *Understanding human development by listening to the earliest signals of life*

---

## 📖 Overview

**Neuro-Genomic AI** is an end-to-end platform that uses machine learning to analyze fetal heart rate variability (HRV) and assess autonomic nervous system development. Unlike traditional fetal monitoring that only measures heart rate, our system provides insights into:

- 🧠 **Neural Complexity** (Sample Entropy)
- ❤️ **Vagal Tone** (RMSSD)
- ⚖️ **Autonomic Balance** (LF/HF Ratio)
- 📈 **Developmental Trajectories** (Longitudinal tracking)

**What sets us apart:**
- 🔒 **Ethics by Design** — Uncertainty visualization built into every layer
- 📊 **Unsupervised Learning** — Discover patterns without predefined labels
- 🌍 **Clinically Validated** — Trained on 1,800+ fetal recordings
- ☁️ **Cloud-Native** — Deploy on Oracle Cloud Infrastructure (OCI)

---

## 🏆 Key Achievements

| Achievement | Status |
|-------------|--------|
| 🥈 Pitched | Kirinyaga University Innovation Day 2026 |
| 🚀 Innovation Hub Space | Kirinyaga University |
| 🤝 Oracle Meeting | Scheduled |
| 📊 1,800+ Recordings Analyzed | PhysioNet Datasets |
| 📈 21,600+ Data Points | HRV Features Extracted |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEURO-GENOMIC AI ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────────┤
│  DATA LAYER → PROCESSING → MODELING → VALIDATION → ETHICS → HCI │
└─────────────────────────────────────────────────────────────────┘
```

| Layer | Components |
|-------|------------|
| **Data** | PhysioNet, ADFECGDB, NIFECGDB, LONGFECG |
| **Processing** | Filtering, Maternal ECG Cancellation, R-peak Detection |
| **Modeling** | VAE Encoding, K-means, Hierarchical Clustering |
| **Validation** | Silhouette Score, Davies-Bouldin, Biological Correlation |
| **Ethics** | Uncertainty Visualization, Confidence Intervals, Transparency |
| **HCI** | Interactive Dashboard, Cluster Visualization, Export |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- 8GB RAM minimum

> ⚠️ Compatibility note: This project uses `starlette` test utilities with `httpx==0.28.x`.
> If you upgrade httpx, ensure `starlette`/`fastapi` versions remain aligned (520+), and update tests to use `httpx.AsyncClient` + `ASGITransport` as shown in `tests/test_api.py`.

### Installation (5 minutes)

```bash
# Clone the repository
git clone https://github.com/neuro-genomic-ai/core.git
cd core

# Copy environment file
cp .env.example .env

# Start with Docker
docker-compose up -d

# Access the application
# API: http://localhost:8000/docs
# Dashboard: http://localhost:8501
```

### Local Development

```bash

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/base.txt

# Run API server
uvicorn src.api.main:app --reload --port 8000

# Run dashboard (in another terminal)
streamlit run src/dashboard/app.py
```

---

## 📊 Features

### 1. HRV Feature Extraction
Extract 12 clinically validated HRV features:
- **Time Domain:** Mean RR, SDNN, RMSSD, pNN50
- **Frequency Domain:** LF Power, HF Power, LF/HF Ratio
- **Nonlinear:** Sample Entropy, Poincaré SD1/SD2

### 2. Developmental Index
Composite score combining:
- Vagal maturity (RMSSD)
- Autonomic balance (LF/HF)
- Neural complexity (Sample Entropy)

### 3. Risk Classification
- **Normal:** Healthy development trajectory
- **Suspect:** Monitor closely
- **Pathological:** Immediate intervention recommended

### 4. Uncertainty Visualization
- Confidence intervals on every prediction
- Signal quality indicators
- Transparent limitations

---

## 🧪 API Documentation

### Upload ECG File
```bash
POST /api/v1/upload
Content-Type: multipart/form-data

Response:
{
  "file_id": "uuid",
  "task_id": "celery-task-id",
  "status": "processing"
}
```

### Get Analysis Results
```bash
GET /api/v1/analysis/{file_id}

Response:
{
  "features": {
    "rmssd": 28.5,
    "lf_hf_ratio": 1.2,
    "sample_entropy": 1.15
  },
  "risk": {
    "normal": 0.85,
    "suspect": 0.12,
    "pathological": 0.03
  },
  "developmental_index": 0.72
}
```

### Full API Documentation
Visit `/docs` after starting the server.

---

## 🏥 Clinical Interpretation

| Feature | Biological Meaning | Clinical Significance |
|---------|-------------------|----------------------|
| **RMSSD** | Vagal tone | High = mature parasympathetic system |
| **LF/HF** | Autonomic balance | Low = healthy rest state |
| **Sample Entropy** | Neural complexity | Peak at 32 weeks = optimal development |

---

## 🚢 Deployment

### Oracle Cloud Infrastructure (OCI)

```bash
# Deploy infrastructure
cd infrastructure/terraform
terraform init
terraform apply

# Deploy application
make deploy
```

### Kubernetes

```bash
kubectl apply -f infrastructure/kubernetes/
```

### Docker Hub

```bash
docker pull neurogenomic/api:latest
docker pull neurogenomic/worker:latest
docker pull neurogenomic/dashboard:latest
```

---

## 📁 Repository Structure

```
neuro-genomic-ai/
├── .github/workflows/      # CI/CD pipelines
├── infrastructure/          # Terraform + K8s
├── docker/                  # Dockerfiles
├── src/
│   ├── api/                 # FastAPI application
│   ├── core/                # Core algorithms
│   ├── workers/             # Celery tasks
│   └── dashboard/           # Streamlit UI
├── tests/                   # Unit tests
├── scripts/                 # Utility scripts
└── config/                  # Configuration files
```

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Lint
make lint
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Kirinyaga University** — Innovation Hub support
- **PhysioNet** — Public fetal ECG datasets
- **Oracle** — Cloud infrastructure mentorship
- **Villgro Africa** — Wekebere for inspiration

---

## 📞 Contact

**Collins Omondi** — Founder & CEO  
📧 onyango.17163@students.kyu.ac.ke  
🔗 [LinkedIn](https://linkedin.com/in/collins-omondi)  
🌐 [neuro-genomic.com](https://neuro-genomic.com)

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neuro-genomic-ai/core&type=Date)](https://star-history.com/#neuro-genomic-ai/core&Date)

---

**Made with 🧬 by Collins Omondi and the Neuro-Genomic AI Team**
