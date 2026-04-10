"""
Upload endpoint tests
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
from src.api.main import app
from io import BytesIO

@pytest.mark.asyncio
async def test_upload_valid_csv_file():
    """Test uploading a valid CSV ECG file"""
    with patch('src.api.routes.upload.s3_client') as mock_s3, \
         patch('src.api.routes.upload.process_ecg_file') as mock_task:
        
        mock_s3.put_object.return_value = None
        mock_task.delay.return_value = MagicMock(id="task-123")
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            # Create a test CSV file
            csv_content = b"time,ecg\n0.0,100\n0.1,101\n0.2,102"
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("sample_ecg.csv", csv_content, "text/csv")},
                data={"gestational_weeks": "32", "patient_id": "TEST001"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert data["filename"] == "sample_ecg.csv"
        assert data["status"] == "processing"
        assert "task_id" in data


@pytest.mark.asyncio
async def test_upload_valid_txt_file():
    """Test uploading a valid TXT ECG file"""
    with patch('src.api.routes.upload.s3_client') as mock_s3, \
         patch('src.api.routes.upload.process_ecg_file') as mock_task:
        
        mock_s3.put_object.return_value = None
        mock_task.delay.return_value = MagicMock(id="task-456")
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            txt_content = b"100\n101\n102\n103"
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("sample_ecg.txt", txt_content, "text/plain")},
                data={"gestational_weeks": "28"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "sample_ecg.txt"


@pytest.mark.asyncio
async def test_upload_invalid_file_type():
    """Test uploading invalid file type"""
    with patch('src.api.routes.upload.s3_client') as mock_s3:
        mock_s3.put_object.return_value = None
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            invalid_content = b"invalid content"
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("sample.jpg", invalid_content, "image/jpeg")}
            )
        
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_pdf_file_rejected():
    """Test that PDF files are rejected"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        pdf_content = b"%PDF-1.4"
        
        response = await client.post(
            "/api/v1/upload",
            files={"file": ("document.pdf", pdf_content, "application/pdf")}
        )
        
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_missing_file():
    """Test upload request without file"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post("/api/v1/upload")
        
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_upload_s3_failure():
    """Test handling of S3 upload failure"""
    with patch('src.api.routes.upload.s3_client') as mock_s3, \
         patch('src.api.routes.upload.process_ecg_file') as mock_task:
        
        from botocore.exceptions import ClientError
        mock_s3.put_object.side_effect = ClientError(
            {"Error": {"Code": "NoSuchBucket"}},
            "PutObject"
        )
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            csv_content = b"time,ecg\n0.0,100"
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("sample.csv", csv_content, "text/csv")}
            )
        
        assert response.status_code == 500


@pytest.mark.asyncio
async def test_get_upload_status():
    """Test getting upload status"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/api/v1/status/test-file-id")
    
    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert data["file_id"] == "test-file-id"


@pytest.mark.asyncio
async def test_upload_edf_file():
    """Test uploading a valid EDF file"""
    with patch('src.api.routes.upload.s3_client') as mock_s3, \
         patch('src.api.routes.upload.process_ecg_file') as mock_task:
        
        mock_s3.put_object.return_value = None
        mock_task.delay.return_value = MagicMock(id="task-789")
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            edf_content = b"0     19 1 1 1 1 1 1 1 1 256"
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("sample_ecg.edf", edf_content, "application/edf")}
            )
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_upload_empty_file():
    """Test uploading an empty file"""
    with patch('src.api.routes.upload.s3_client') as mock_s3, \
         patch('src.api.routes.upload.process_ecg_file') as mock_task:
        
        mock_s3.put_object.return_value = None
        mock_task.delay.return_value = MagicMock(id="task-empty")
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("empty.csv", b"", "text/csv")}
            )
        
        # Should still accept but may fail during processing
        assert response.status_code == 200
