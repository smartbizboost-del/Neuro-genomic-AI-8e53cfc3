"""
Pytest configuration and comprehensive fixtures
"""

import pytest
import sys
import os
import pandas as pd
import numpy as np
import tempfile
from httpx import AsyncClient, ASGITransport

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.api.main import app
from src.core.pipeline import NeuroGenomicPipeline


@pytest.fixture
def client():
    """FastAPI test client"""
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async HTTP test client"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client


@pytest.fixture
def pipeline():
    """Pipeline instance for testing"""
    return NeuroGenomicPipeline()


# ============================================================================
# ECG DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_ecg_healthy():
    """Generate healthy fetal ECG sample (34 weeks)
    
    Characteristics:
    - Heart rate: 140 bpm (normal fetal range: 120-160)
    - Good variability (RMSSD > 20)
    - Clear R-peaks for RR interval detection
    """
    np.random.seed(42)
    fs = 250  # Sampling frequency in Hz
    duration = 60  # 60 seconds
    signal_length = fs * duration
    
    # Base heart rate: 140 bpm = 2.33 Hz
    hr_base = 2.33
    # Healthy variability
    hr_variability = 0.15
    
    # Generate synthetic ECG with R-peaks
    t = np.linspace(0, duration, signal_length)
    
    # Create varying intervals (RR intervals)
    intervals = 1 / (hr_base + np.random.randn(500) * hr_variability)
    r_peaks = np.cumsum(intervals)
    r_peaks = r_peaks[r_peaks < duration]
    
    # Generate ECG signal
    ecg = np.zeros(signal_length)
    for peak in r_peaks:
        idx = int(peak * fs)
        if idx < len(ecg):
            # Create QRS complex
            if idx > 0:
                ecg[idx - 1:idx + 2] = [0.5, 1.0, 0.5]
    
    # Add noise
    ecg = ecg + np.random.randn(len(ecg)) * 0.05
    
    return ecg


@pytest.fixture
def sample_ecg_suspect():
    """Generate suspect fetal ECG sample
    
    Characteristics:
    - Reduced variability (RMSSD 10-20)
    - Still detectable peaks but less variable
    - Possible early signs of distress
    """
    np.random.seed(123)
    fs = 250
    duration = 60
    signal_length = fs * duration
    
    hr_base = 2.33
    hr_variability = 0.05  # Reduced variability
    
    t = np.linspace(0, duration, signal_length)
    intervals = 1 / (hr_base + np.random.randn(500) * hr_variability)
    r_peaks = np.cumsum(intervals)
    r_peaks = r_peaks[r_peaks < duration]
    
    ecg = np.zeros(signal_length)
    for peak in r_peaks:
        idx = int(peak * fs)
        if idx < len(ecg):
            if idx > 0:
                ecg[idx - 1:idx + 2] = [0.3, 0.7, 0.3]
    
    ecg = ecg + np.random.randn(len(ecg)) * 0.03
    
    return ecg


@pytest.fixture
def sample_ecg_pathological():
    """Generate pathological fetal ECG sample
    
    Characteristics:
    - Highly irregular intervals (low variability, severe)
    - Variable heart rate
    - Clear signs of fetal distress
    """
    np.random.seed(456)
    fs = 250
    duration = 60
    signal_length = fs * duration
    
    # Highly irregular intervals (distress pattern)
    intervals = np.random.exponential(0.4, 200)
    r_peaks = np.cumsum(intervals)
    r_peaks = r_peaks[r_peaks < duration]
    
    ecg = np.zeros(signal_length)
    for peak in r_peaks:
        idx = int(peak * fs)
        if idx < len(ecg):
            if idx > 0:
                ecg[idx - 1:idx + 2] = [0.2, 0.5, 0.2]
    
    ecg = ecg + np.random.randn(len(ecg)) * 0.02
    
    return ecg


@pytest.fixture
def sample_rr_intervals_healthy():
    """Sample RR intervals for healthy fetus"""
    np.random.seed(42)
    base_rr = 430  # ms
    rr_intervals = np.random.normal(base_rr, 15, 100)
    return rr_intervals


@pytest.fixture
def sample_rr_intervals_suspect():
    """Sample RR intervals for suspect case"""
    np.random.seed(123)
    base_rr = 430
    rr_intervals = np.random.normal(base_rr, 5, 100)
    return rr_intervals


@pytest.fixture
def sample_rr_intervals_pathological():
    """Sample RR intervals for pathological case"""
    np.random.seed(456)
    rr_intervals = np.random.exponential(0.43, 100) * 1000
    return rr_intervals


# ============================================================================
# FILE FIXTURES
# ============================================================================

@pytest.fixture
def temp_ecg_file_healthy(sample_ecg_healthy):
    """Temporary CSV file with healthy ECG data"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df = pd.DataFrame({'ecg': sample_ecg_healthy})
        df.to_csv(f.name, index=False)
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_ecg_file_suspect(sample_ecg_suspect):
    """Temporary CSV file with suspect ECG data"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df = pd.DataFrame({'ecg': sample_ecg_suspect})
        df.to_csv(f.name, index=False)
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_ecg_file_pathological(sample_ecg_pathological):
    """Temporary CSV file with pathological ECG data"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df = pd.DataFrame({'ecg': sample_ecg_pathological})
        df.to_csv(f.name, index=False)
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def invalid_csv_file():
    """Temporary file with invalid CSV data"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("invalid,data\n")
        f.write("not,a,number\n")
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def empty_csv_file():
    """Temporary empty CSV file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        yield f.name
    os.unlink(f.name)


# ============================================================================
# MOCK DATA FIXTURES
# ============================================================================

@pytest.fixture
def analysis_result_healthy():
    """Mock analysis result for healthy case"""
    return {
        'file_id': 'test_healthy_001',
        'features': {
            'rmssd': 28.5,
            'sdnn': 45.2,
            'lf_hf_ratio': 1.2,
            'sample_entropy': 1.15,
            'mean_rr': 430.0,
            'pnn50': 15.5,
            'lf_power': 245.3,
            'hf_power': 203.6,
            'developmental_index': 0.72
        },
        'risk': {
            'normal': 0.85,
            'suspect': 0.12,
            'pathological': 0.03,
            'predicted_class': 'normal'
        },
        'interpretation': [
            'Heart rate variability within normal range',
            'Autonomic balance appropriate for gestational age',
            'No signs of significant distress'
        ],
        'developmental_index': 0.72,
        'gestational_weeks': 34
    }


@pytest.fixture
def analysis_result_suspect():
    """Mock analysis result for suspect case"""
    return {
        'file_id': 'test_suspect_001',
        'features': {
            'rmssd': 12.3,
            'sdnn': 15.8,
            'lf_hf_ratio': 0.8,
            'sample_entropy': 0.85,
            'mean_rr': 430.0,
            'pnn50': 3.2,
            'lf_power': 180.5,
            'hf_power': 225.3,
            'developmental_index': 0.48
        },
        'risk': {
            'normal': 0.45,
            'suspect': 0.40,
            'pathological': 0.15,
            'predicted_class': 'suspect'
        },
        'interpretation': [
            'Reduced heart rate variability',
            'Possible autonomic dysregulation',
            'Further monitoring recommended'
        ],
        'developmental_index': 0.48,
        'gestational_weeks': 34
    }


@pytest.fixture
def analysis_result_pathological():
    """Mock analysis result for pathological case"""
    return {
        'file_id': 'test_pathological_001',
        'features': {
            'rmssd': 5.1,
            'sdnn': 7.2,
            'lf_hf_ratio': 0.3,
            'sample_entropy': 0.45,
            'mean_rr': 430.0,
            'pnn50': 0.5,
            'lf_power': 95.2,
            'hf_power': 320.1,
            'developmental_index': 0.18
        },
        'risk': {
            'normal': 0.10,
            'suspect': 0.20,
            'pathological': 0.70,
            'predicted_class': 'pathological'
        },
        'interpretation': [
            'Severely reduced heart rate variability',
            'Significant autonomic dysregulation',
            'Signs of acute fetal distress',
            'Urgent clinical intervention recommended'
        ],
        'developmental_index': 0.18,
        'gestational_weeks': 34
    }


# ============================================================================
# PARAMETER FIXTURES
# ============================================================================

@pytest.fixture(params=[20, 28, 34, 40])
def gestational_weeks(request):
    """Parametrized gestational weeks fixture"""
    return request.param


@pytest.fixture(params=['normal', 'suspect', 'pathological'])
def risk_class(request):
    """Parametrized risk classification """
    return request.param


@pytest.fixture
def valid_patient_ids():
    """List of valid patient IDs for testing"""
    return [
        'PATIENT_001',
        'P-2024-0001',
        'patient_test_01'
    ]