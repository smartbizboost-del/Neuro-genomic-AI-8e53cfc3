"""
File upload endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import uuid
import boto3
from botocore.exceptions import ClientError
import os
import numpy as np
import logging
from datetime import datetime

from src.api.models.schemas import UploadResponse, FileMetadata, AnalysisResponse, FeatureResponse, RiskAssessment, HealthStatus
from src.api.routes import analysis as analysis_routes
from src.workers.tasks import process_ecg_file

router = APIRouter()
logger = logging.getLogger(__name__)

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
    
    def process_in_background():
        """Background task: Full analysis"""
        import os
        import tempfile
        
        temp_path = os.path.join(tempfile.gettempdir(), f"{file_id}.ecg")
        with open(temp_path, "wb") as f:
            f.write(content)
        try:
            mixed_signal = extract_raw_signals(temp_path)
            
            # Run FULL analysis with all features and SHAP
            res = pipeline.analyze(
                raw_ecg=mixed_signal, 
                sampling_rate=250,
                gestational_age=gestational_weeks or 32
            )
            
            # Store complete result in schema-compliant format
            # Build features response
            features_data = res.get("hrv_metrics", {})
            features = FeatureResponse(
                rmssd=features_data.get("rmssd"),
                sdnn=features_data.get("sdnn"),
                lf_hf_ratio=features_data.get("lf_hf"),
                sample_entropy=features_data.get("sample_entropy"),
                mean_rr=features_data.get("mean_rr"),
                pnn50=features_data.get("pnn50"),
                lf_power=features_data.get("lf_power"),
                hf_power=features_data.get("hf_power"),
                developmental_index=res.get("developmental_index", 0.72)
            )
            
            # Build risk assessment
            risk_data = res.get("risk_assessment", {})
            risk = RiskAssessment(
                normal=risk_data.get("iugr_risk", {}).get("score", 20) / 100,
                suspect=risk_data.get("preterm_risk", {}).get("score", 15) / 100,
                pathological=risk_data.get("hypoxia_risk", {}).get("score", 10) / 100,
                predicted_class=HealthStatus.NORMAL,
                confidence_level=res.get("confidence", 0.85),
                confidence_label="high" if res.get("confidence", 0.85) > 0.80 else "medium" if res.get("confidence", 0.85) > 0.60 else "low"
            )
            
            analysis_routes.RESULTS_DB[file_id] = AnalysisResponse(
                file_id=file_id,
                features=features,
                risk=risk,
                developmental_index=res.get("developmental_index", 0.72),
                gestational_weeks=gestational_weeks or 32,
                interpretation=[res.get("recommendation", "Analysis complete")],
                created_at=datetime.now(),
                confidence_intervals=None
            )
            analysis_routes.LATEST_FILE_ID = file_id
            logger.info(f"Background processing completed for {file_id}")
        except Exception as e:
            logger.error(f"Background processing error for {file_id}: {e}")
            # Store error result with minimum required fields
            features = FeatureResponse()
            risk = RiskAssessment(
                normal=0.5,
                suspect=0.3,
                pathological=0.2,
                predicted_class=HealthStatus.SUSPECT,
                confidence_level=0.5,
                confidence_label="low"
            )
            analysis_routes.RESULTS_DB[file_id] = AnalysisResponse(
                file_id=file_id,
                features=features,
                risk=risk,
                developmental_index=0.5,
                gestational_weeks=gestational_weeks or 32,
                interpretation=[f"Analysis failed: {str(e)}"],
                created_at=datetime.now(),
                confidence_intervals=None
            )
    
    # Run FAST analysis for immediate response (~2-3 seconds)
    try:
        fast_result = pipeline.analyze_fast(
            raw_ecg=content if isinstance(content, np.ndarray) else np.frombuffer(content, dtype=np.float32),
            sampling_rate=250,
            gestational_age=gestational_weeks or 32
        )
    except Exception as e:
        logger.warning(f"Fast analysis failed: {e}")
        fast_result = {"status": "processing", "is_preliminary": True}
    
    # Store fast result temporarily in schema-compliant format
    if fast_result.get("status") in ["success", "error"]:
        # Build response from fast result
        features_data = fast_result.get("hrv_metrics", {})
        features = FeatureResponse(
            rmssd=features_data.get("rmssd"),
            sdnn=features_data.get("sdnn"),
            lf_hf_ratio=features_data.get("lf_hf"),
            sample_entropy=features_data.get("sample_entropy")
        )
        
        risk_data = fast_result.get("risk_assessment", {})
        risk = RiskAssessment(
            normal=risk_data.get("iugr_risk", {}).get("score", 20) / 100,
            suspect=risk_data.get("preterm_risk", {}).get("score", 15) / 100,
            pathological=risk_data.get("hypoxia_risk", {}).get("score", 10) / 100,
            predicted_class=HealthStatus.NORMAL,
            confidence_level=fast_result.get("confidence", 0.70),
            confidence_label="medium"
        )
        
        analysis_routes.RESULTS_DB[file_id] = AnalysisResponse(
            file_id=file_id,
            features=features,
            risk=risk,
            developmental_index=fast_result.get("developmental_index", 0.70),
            gestational_weeks=gestational_weeks or 32,
            interpretation=["⏳ Analysis in progress - Preliminary results shown"],
            created_at=datetime.now(),
            confidence_intervals=None
        )
        analysis_routes.LATEST_FILE_ID = file_id
    
    # Queue background task for full analysis
    if background_tasks:
        background_tasks.add_task(process_in_background)
    else:
        # Fallback to synchronous if no bg task support
        import threading
        thread = threading.Thread(target=process_in_background, daemon=True)
        thread.start()
    
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