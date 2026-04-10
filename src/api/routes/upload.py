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
from src.workers.tasks import process_ecg_file
import logging
logger = logging.getLogger(__name__)

router = APIRouter()

from src.workers.tasks import extract_raw_signals
from src.api.routes.analysis import RESULTS_DB
from fastapi import BackgroundTasks
import tempfile
from src.core.pipeline import NeuroGenomicPipeline

pipeline = NeuroGenomicPipeline()

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
    
    # Upload file to MinIO/S3
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=os.getenv('MINIO_ENDPOINT', 'http://minio:9000'),
            aws_access_key_id=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
            aws_secret_access_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin')
        )
        s3_client.put_object(
            Bucket=os.getenv('MINIO_BUCKET', 'neuro-genomic-ecg'),
            Key=s3_key,
            Body=content
        )
    except Exception as e:
        logger.error(f"Failed to upload to S3: {e}")
        # Local fallback if S3 isn't available
        temp_path = os.path.join(tempfile.gettempdir(), f"{file_id}.ecg")
        with open(temp_path, "wb") as f:
            f.write(content)
        s3_key = temp_path # Hack to let worker find it locally
    
    # Dispatch Celery Task
    task = process_ecg_file.delay(
        file_id=file_id, 
        s3_key=s3_key, 
        gestational_weeks=gestational_weeks, 
        patient_id=patient_id
    )
    
    return UploadResponse(
        file_id=file_id,
        filename=file.filename,
        size=len(content),
        task_id=task.id,
        status="processing",
        message="File uploaded successfully. Celery processing started."
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