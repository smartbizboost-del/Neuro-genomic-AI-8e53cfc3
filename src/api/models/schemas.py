"""
Pydantic models for API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class HealthStatus(str, Enum):
    NORMAL = "normal"
    SUSPECT = "suspect"
    PATHOLOGICAL = "pathological"

class FeatureResponse(BaseModel):
    rmssd: Optional[float] = Field(None, description="Root mean square of successive differences (vagal tone)")
    sdnn: Optional[float] = Field(None, description="Standard deviation of RR intervals")
    lf_hf_ratio: Optional[float] = Field(None, description="LF/HF ratio (autonomic balance)")
    sample_entropy: Optional[float] = Field(None, description="Signal complexity")
    mean_rr: Optional[float] = Field(None, description="Mean RR interval")
    pnn50: Optional[float] = Field(None, description="Percentage of NN50")
    lf_power: Optional[float] = Field(None, description="Low frequency power")
    hf_power: Optional[float] = Field(None, description="High frequency power")
    t_qrs_ratio: Optional[float] = Field(None, description="T/QRS amplitude ratio for hypoxia screening")
    hypoxia_risk: Optional[str] = Field(None, description="Hypoxia risk classification from ST analysis")
    developmental_index: Optional[float] = Field(None, description="Composite developmental score")

class RiskAssessment(BaseModel):
    normal: float = Field(..., description="Probability of normal development")
    suspect: float = Field(..., description="Probability of suspect development")
    pathological: float = Field(..., description="Probability of pathological development")
    predicted_class: HealthStatus = Field(..., description="Predicted health status")

class ClinicalInterpretation(BaseModel):
    text: str = Field(..., description="Interpretation text")
    severity: str = Field(..., description="Severity level: info, warning, alert")

class AnalysisResponse(BaseModel):
    file_id: str
    features: FeatureResponse
    risk: RiskAssessment
    interpretation: List[str]
    developmental_index: float
    gestational_weeks: Optional[int]
    created_at: datetime
    confidence_intervals: Optional[Dict[str, Any]]

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    size: int
    task_id: str
    status: str
    message: str

class FileMetadata(BaseModel):
    file_id: str
    filename: str
    size: int
    uploaded_at: datetime
    gestational_weeks: Optional[int]
    patient_id: Optional[str]
    status: str

class BatchAnalysisRequest(BaseModel):
    file_ids: List[str] = Field(..., min_length=1, max_length=100)

class BatchAnalysisResponse(BaseModel):
    batch_id: str
    total_files: int
    status: str
    results_url: Optional[str]