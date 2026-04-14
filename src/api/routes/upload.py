"""
File upload endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import uuid
import boto3
from botocore.exceptions import ClientError
import os

from src.api.models.schemas import UploadResponse, FileMetadata
from src.api.routes import analysis as analysis_routes
from src.workers.tasks import process_ecg_file

router = APIRouter()

from src.workers.tasks import extract_raw_signals
from fastapi import BackgroundTasks
import tempfile
from src.core.pipeline import get_pipeline

pipeline = get_pipeline()

@router.post("/upload", response_model=UploadResponse)
async def upload_ecg(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    gestational_weeks: int = None,
    patient_id: str = None
):
    """
    Upload a fetal ECG file for processing
    """
    
    # Validate file type
    allowed_extensions = ['.csv', '.txt', '.edf', '.hea', '.dat']
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {allowed_extensions}"
        )
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    s3_key = f"uploads/{file_id}/{file.filename}"
    
    content = await file.read()
    
    def process_locally():
        import os
        temp_path = os.path.join(tempfile.gettempdir(), f"{file_id}.ecg")
        with open(temp_path, "wb") as f:
            f.write(content)
        try:
            mixed_signal = extract_raw_signals(temp_path)
            res = pipeline.process_recording(mixed_signal, 500, gestational_weeks)
            analysis_routes.RESULTS_DB[file_id] = {
                "file_id": file_id,
                "features": res["features"],
                "risk": res["risk"],
                "interpretation": res["interpretation"],
                "developmental_index": res["developmental_index"],
                "gestational_weeks": gestational_weeks or 32,
                "created_at": "2024-01-01T00:00:00Z",
                "confidence_intervals": None
            }
            analysis_routes.LATEST_FILE_ID = file_id
        except Exception as e:
            print(f"Error locally processing: {e}")
            
    if background_tasks:
        background_tasks.add_task(process_locally)
    else:
        process_locally()
    
    return UploadResponse(
        file_id=file_id,
        filename=file.filename,
        size=len(content),
        task_id="local_sync",
        status="processing",
        message="File uploaded successfully. Processing started."
    )

@router.get("/status/{file_id}")
async def get_upload_status(file_id: str):
    """
    Check processing status of uploaded file
    """
    from src.workers.celery_app import celery_app
    
    # This would typically query a database
    # Simplified version
    return {
        "file_id": file_id,
        "status": "processing"  # Would be actual status from DB
    }