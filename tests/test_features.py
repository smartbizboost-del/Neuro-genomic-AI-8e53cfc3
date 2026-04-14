"""
Feature extraction tests
"""

import pytest
import numpy as np
from src.core.pipeline import get_pipeline

@pytest.fixture
def pipeline():
    return get_pipeline()

@pytest.fixture
def sample_rr_intervals():
    """Generate sample RR intervals"""
    np.random.seed(42)
    rr_baseline = 450
    rr_variability = 25
    n_beats = 100
    return rr_baseline + np.random.randn(n_beats) * rr_variability

@pytest.fixture
def sample_rr_intervals_low_variability():
    """Generate low variability RR intervals"""
    np.random.seed(42)
    rr_baseline = 450
    rr_variability = 5
    n_beats = 100
    return rr_baseline + np.random.randn(n_beats) * rr_variability

@pytest.fixture
def sample_rr_intervals_high_variability():
    """Generate high variability RR intervals"""
    np.random.seed(42)
    rr_baseline = 450
    rr_variability = 50
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

def test_extract_hrv_features_mean_rr(pipeline, sample_rr_intervals):
    """Test that mean RR is extracted"""
    features = pipeline._extract_hrv_features(sample_rr_intervals)
    
    assert "mean_rr" in features
    assert 400 < features["mean_rr"] < 500  # Should be close to 450

def test_extract_hrv_features_pnn50(pipeline, sample_rr_intervals):
    """Test PNN50 feature"""
    features = pipeline._extract_hrv_features(sample_rr_intervals)
    
    assert "pnn50" in features
    assert 0 <= features["pnn50"] <= 100

def test_extract_hrv_features_frequency_domain(pipeline, sample_rr_intervals):
    """Test frequency domain features"""
    features = pipeline._extract_hrv_features(sample_rr_intervals)
    
    assert "lf_power" in features
    assert "hf_power" in features
    assert features["lf_power"] > 0
    assert features["hf_power"] > 0

def test_extract_hrv_features_low_variability(pipeline, sample_rr_intervals_low_variability):
    """Test HRV with low variability"""
    features = pipeline._extract_hrv_features(sample_rr_intervals_low_variability)
    
    assert features["rmssd"] < 20  # Low variability should have low RMSSD

def test_extract_hrv_features_high_variability(pipeline, sample_rr_intervals_high_variability):
    """Test HRV with high variability"""
    features = pipeline._extract_hrv_features(sample_rr_intervals_high_variability)
    
    assert features["rmssd"] > 30  # High variability should have high RMSSD

def test_calculate_developmental_index(pipeline, sample_rr_intervals):
    """Test developmental index calculation"""
    features = pipeline._extract_hrv_features(sample_rr_intervals)
    index = pipeline._calculate_developmental_index(features, 32)
    
    assert 0 <= index <= 1

def test_calculate_developmental_index_different_gestational_weeks(pipeline, sample_rr_intervals):
    """Test developmental index at different gestational weeks"""
    features = pipeline._extract_hrv_features(sample_rr_intervals)
    
    index_24 = pipeline._calculate_developmental_index(features, 24)
    index_32 = pipeline._calculate_developmental_index(features, 32)
    index_40 = pipeline._calculate_developmental_index(features, 40)
    
    assert 0 <= index_24 <= 1
    assert 0 <= index_32 <= 1
    assert 0 <= index_40 <= 1

def test_process_recording(pipeline, sample_rr_intervals):
    """Test full recording processing"""
    results = pipeline.process_recording(sample_rr_intervals, 32)
    
    assert "features" in results
    assert "developmental_index" in results
    assert "risk" in results
    assert "interpretation" in results

def test_process_recording_returns_features(pipeline, sample_rr_intervals):
    """Test that processing returns all features"""
    results = pipeline.process_recording(sample_rr_intervals, 32)
    features = results["features"]
    
    assert "rmssd" in features
    assert "sdnn" in features
    assert "lf_hf_ratio" in features
    # developmental_index is a separate field, not inside features
    assert "developmental_index" in results

def test_process_recording_returns_risk(pipeline, sample_rr_intervals):
    """Test that processing returns risk assessment"""
    results = pipeline.process_recording(sample_rr_intervals, 32)
    risk = results["risk"]
    
    assert "normal" in risk
    assert "suspect" in risk
    assert "pathological" in risk
    assert "predicted_class" in risk

def test_process_recording_returns_interpretation(pipeline, sample_rr_intervals):
    """Test that processing returns interpretation"""
    results = pipeline.process_recording(sample_rr_intervals, 32)
    
    assert "interpretation" in results
    assert isinstance(results["interpretation"], list)
    assert len(results["interpretation"]) > 0

def test_process_recording_with_different_lengths(pipeline):
    """Test processing with different recording lengths"""
    # Short recording
    short_recording = np.random.randn(50) * 25 + 450
    results_short = pipeline.process_recording(short_recording, 32)
    assert "features" in results_short
    
    # Long recording
    long_recording = np.random.randn(500) * 25 + 450
    results_long = pipeline.process_recording(long_recording, 32)
    assert "features" in results_long