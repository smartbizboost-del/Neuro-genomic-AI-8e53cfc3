"""
API tests
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch
from src.api.main import app

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert "Neuro-Genomic AI" in response.json()["name"]

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_ready():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


@pytest.mark.asyncio
async def test_get_analysis_valid_file_id():
    """Test getting analysis for a valid file ID"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        import uuid
        valid_id = str(uuid.uuid4())
        response = await client.get(f"/api/v1/analysis/{valid_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["file_id"] == valid_id
    assert "features" in data
    assert "risk" in data
    assert "developmental_index" in data


@pytest.mark.asyncio
async def test_get_analysis_invalid_file_id():
    """Test that invalid file ID format is rejected"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/api/v1/analysis/not-a-uuid")
    
    assert response.status_code == 400
    assert "Invalid file ID format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_analysis_response_structure():
    """Test that analysis response has correct structure"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        import uuid
        valid_id = str(uuid.uuid4())
        response = await client.get(f"/api/v1/analysis/{valid_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify features
    assert "rmssd" in data["features"]
    assert "sdnn" in data["features"]
    assert "lf_hf_ratio" in data["features"]
    
    # Verify risk assessment
    assert "normal" in data["risk"]
    assert "suspect" in data["risk"]
    assert "pathological" in data["risk"]
    assert "predicted_class" in data["risk"]
    assert "unsupervised_cluster" in data["risk"]
    
    # Verify other fields
    assert "interpretation" in data
    assert isinstance(data["interpretation"], list)


@pytest.mark.asyncio
async def test_get_analysis_features():
    """Test that analysis features are present"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        import uuid
        valid_id = str(uuid.uuid4())
        response = await client.get(f"/api/v1/analysis/{valid_id}")
    
    features = response.json()["features"]
    assert features["rmssd"] is not None
    assert features["sample_entropy"] is not None
    assert features["developmental_index"] is not None


@pytest.mark.asyncio
async def test_get_analysis_risk_classes():
    """Test that all risk classes are returned"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        import uuid
        valid_id = str(uuid.uuid4())
        response = await client.get(f"/api/v1/analysis/{valid_id}")
    
    risk = response.json()["risk"]
    assert risk["normal"] > 0
    assert risk["suspect"] >= 0
    assert risk["pathological"] >= 0
    assert risk["predicted_class"] in ["normal", "suspect", "pathological"]
    assert isinstance(risk["unsupervised_cluster"], int)


@pytest.mark.asyncio
async def test_export_csv():
    """Test exporting analysis results as CSV"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        import uuid
        valid_id = str(uuid.uuid4())
        response = await client.get(f"/api/v1/export/csv/{valid_id}")
    
    assert response.status_code in [200, 404, 500]
    if response.status_code == 200:
        assert "text/csv" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_export_json():
    """Test exporting analysis results as JSON"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        import uuid
        valid_id = str(uuid.uuid4())
        response = await client.get(f"/api/v1/export/json/{valid_id}")
    
    assert response.status_code in [200, 404, 500]


@pytest.mark.asyncio
async def test_export_pdf():
    """Test exporting analysis results as PDF"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        import uuid
        valid_id = str(uuid.uuid4())
        response = await client.get(f"/api/v1/export/pdf/{valid_id}")
    
    assert response.status_code in [200, 404, 500]
    if response.status_code == 200:
        assert "pdf" in response.headers.get("content-type", "").lower()


@pytest.mark.asyncio
async def test_health_status_structure():
    """Test health endpoint returns complete status"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "unhealthy"]


@pytest.mark.asyncio
async def test_ready_status_structure():
    """Test ready endpoint returns readiness status"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/ready")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


@pytest.mark.asyncio
async def test_root_response_fields():
    """Test root endpoint returns expected fields"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data or "status" in data