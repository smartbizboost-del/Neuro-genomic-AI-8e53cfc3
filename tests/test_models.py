"""
Model tests
"""

import pytest
from src.core.pipeline import NeuroGenomicPipeline

def test_pipeline_initialization():
    """Test pipeline initialization"""
    pipeline = NeuroGenomicPipeline()
    assert pipeline.model is None
    assert pipeline.feature_extractor is None

def test_risk_classification():
    """Test risk classification logic"""
    pipeline = NeuroGenomicPipeline()
    
    # Test normal case
    features = {"rmssd": 35, "lf_hf_ratio": 1.2, "sample_entropy": 1.2, "sdnn": 40}
    developmental_index = 0.8
    risk = pipeline._classify_risk(features, developmental_index)
    
    assert "normal" in risk
    assert "suspect" in risk
    assert "pathological" in risk
    assert "predicted_class" in risk
    assert risk["predicted_class"] == "normal"
    
    # Test pathological case
    developmental_index = 0.2
    risk = pipeline._classify_risk(features, developmental_index)
    assert risk["predicted_class"] == "pathological"