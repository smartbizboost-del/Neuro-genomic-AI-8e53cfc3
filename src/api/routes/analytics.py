from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

from src.core.predictive import predict_developmental_trajectory, benchmark_against_cohort

router = APIRouter()


class HistoricalDataPoint(BaseModel):
    gestational_weeks: int
    developmental_index: float


class AnalyticsRequest(BaseModel):
    historical_data: List[HistoricalDataPoint]


class BenchmarkRequest(BaseModel):
    patient_features: Dict[str, float]
    cohort_data: List[HistoricalDataPoint]


@router.post("/analytics/predict")
async def predict_trajectory(request: AnalyticsRequest):
    """Predict future developmental trajectory based on historical data."""
    if len(request.historical_data) < 2:
        raise HTTPException(status_code=400, detail="At least two historical points are required for prediction")
    return predict_developmental_trajectory([d.model_dump() for d in request.historical_data])


@router.post("/analytics/benchmark")
async def benchmark_patient(request: BenchmarkRequest):
    """Benchmark patient features against a matched cohort."""
    return benchmark_against_cohort(request.patient_features, [d.model_dump() for d in request.cohort_data])
