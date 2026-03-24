"""
Feature extraction tests
"""

import pytest
import numpy as np
from src.core.pipeline import NeuroGenomicPipeline

@pytest.fixture
def pipeline():
    return NeuroGenomicPipeline()

@pytest.fixture
def sample_rr_intervals():
    """Generate sample RR intervals"""
    np.random.seed(42)
    rr_baseline = 450
    rr_variability = 25
    n_beats = 100
    return rr_baseline + np.random.randn(n_beats) * rr_variability

def test_extract_hrv_features(pipeline, sample_rr_intervals):
    """Test HRV feature extraction"""
    features = pipeline._extract_hrv_features(sample_rr_intervals)
    
    assert isinstance(features, dict)
    assert "rmssd" in features
    assert "sdnn" in features
    assert "lf_hf_ratio" in features
    assert "sample_entropy" in features
    
    # Check reasonable value ranges
    assert features["rmssd"] > 0
    assert features["sdnn"] > 0

def test_calculate_developmental_index(pipeline, sample_rr_intervals):
    """Test developmental index calculation"""
    features = pipeline._extract_hrv_features(sample_rr_intervals)
    index = pipeline._calculate_developmental_index(features, 32)
    
    assert 0 <= index <= 1

def test_process_recording(pipeline, sample_rr_intervals):
    """Test full recording processing"""
    results = pipeline.process_recording(sample_rr_intervals, 32)
    
    assert "features" in results
    assert "developmental_index" in results
    assert "risk" in results
    assert "interpretation" in results