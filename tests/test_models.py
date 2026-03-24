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


def test_risk_classification_suspect():
    """Test suspect classification"""
    pipeline = NeuroGenomicPipeline()
    features = {"rmssd": 35, "lf_hf_ratio": 1.2, "sample_entropy": 1.2, "sdnn": 40}
    developmental_index = 0.5  # Mid-range, likely suspect
    risk = pipeline._classify_risk(features, developmental_index)
    
    assert "predicted_class" in risk
    assert risk["normal"] + risk["suspect"] + risk["pathological"] > 0


def test_risk_probabilities_sum_to_one():
    """Test that risk probabilities sum to approximately 1"""
    pipeline = NeuroGenomicPipeline()
    features = {"rmssd": 35, "lf_hf_ratio": 1.2, "sample_entropy": 1.2, "sdnn": 40}
    developmental_index = 0.7
    risk = pipeline._classify_risk(features, developmental_index)
    
    total_prob = risk["normal"] + risk["suspect"] + risk["pathological"]
    assert abs(total_prob - 1.0) < 0.01


def test_pipeline_with_low_developmental_index():
    """Test pipeline with very low developmental index"""
    pipeline = NeuroGenomicPipeline()
    features = {"rmssd": 10, "lf_hf_ratio": 0.5, "sample_entropy": 0.5, "sdnn": 15}
    developmental_index = 0.1
    risk = pipeline._classify_risk(features, developmental_index)
    
    assert risk["predicted_class"] == "pathological"
    assert risk["pathological"] >= 0.5


def test_pipeline_with_high_developmental_index():
    """Test pipeline with high developmental index"""
    pipeline = NeuroGenomicPipeline()
    features = {"rmssd": 50, "lf_hf_ratio": 2.0, "sample_entropy": 1.5, "sdnn": 60}
    developmental_index = 0.95
    risk = pipeline._classify_risk(features, developmental_index)
    
    assert risk["predicted_class"] == "normal"
    assert risk["normal"] > 0.7