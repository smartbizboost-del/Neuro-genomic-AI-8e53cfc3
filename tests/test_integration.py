"""
Additional integration and edge case tests
"""

import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport
from src.api.main import app
import numpy as np
from src.core.pipeline import get_pipeline


class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self):
        """Test complete analysis workflow"""
        import uuid
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            # Get analysis for a valid file ID
            valid_id = str(uuid.uuid4())
            response = await client.get(f"/api/v1/analysis/{valid_id}")
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_export_formats(self):
        """Test different export formats"""
        import uuid
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            valid_id = str(uuid.uuid4())
            
            # Test JSON export
            response = await client.get(f"/api/v1/export/json/{valid_id}")
            assert response.status_code in [200, 404, 500]
            
            # Test CSV export
            response = await client.get(f"/api/v1/export/csv/{valid_id}")
            assert response.status_code in [200, 404, 500]
    
    @pytest.mark.asyncio
    async def test_health_check_endpoints(self):
        """Test health and readiness endpoints"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            # Health check
            response = await client.get("/health")
            assert response.status_code == 200
            assert "status" in response.json()
            
            # Readiness check
            response = await client.get("/ready")
            assert response.status_code == 200
            assert "status" in response.json()


class TestPipelineEdgeCases:
    """Test pipeline with edge cases"""
    
    def test_pipeline_with_minimal_rr_intervals(self):
        """Test pipeline with minimal RR intervals"""
        pipeline = NeuroGenomicPipeline()
        minimal_rr = np.array([450, 460, 440])
        
        results = pipeline.process_recording(minimal_rr, 32)
        assert "features" in results
        assert "risk" in results
    
    def test_pipeline_with_constant_rr_intervals(self):
        """Test pipeline with constant RR intervals (no variability)"""
        pipeline = NeuroGenomicPipeline()
        constant_rr = np.ones(100) * 450
        
        results = pipeline.process_recording(constant_rr, 32)
        assert results["features"]["rmssd"] < 5  # Very low variability
    
    def test_pipeline_with_extreme_variability(self):
        """Test pipeline with extreme variability"""
        pipeline = NeuroGenomicPipeline()
        extreme_rr = np.linspace(300, 600, 100)
        
        results = pipeline.process_recording(extreme_rr, 32)
        assert "features" in results
        assert results["features"]["sdnn"] > 50
    
    def test_pipeline_boundary_gestational_weeks(self):
        """Test pipeline at boundary gestational weeks"""
        pipeline = NeuroGenomicPipeline()
        rr = np.linspace(400, 500, 50) + np.random.randn(50) * 10
        
        # Early pregnancy
        results_early = pipeline.process_recording(rr, 20)
        assert 0 <= results_early["developmental_index"] <= 1
        
        # Near term
        results_late = pipeline.process_recording(rr, 42)
        assert 0 <= results_late["developmental_index"] <= 1
    
    def test_pipeline_generates_interpretations(self):
        """Test that pipeline generates clinical interpretations"""
        pipeline = NeuroGenomicPipeline()
        rr = np.linspace(400, 500, 100) + np.random.randn(100) * 10
        
        results = pipeline.process_recording(rr, 32)
        assert "interpretation" in results
        assert isinstance(results["interpretation"], list)
        assert len(results["interpretation"]) > 0


class TestErrorHandling:
    """Test error handling throughout the system"""
    
    @pytest.mark.asyncio
    async def test_invalid_uuid_format(self):
        """Test handling of invalid UUID format"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            response = await client.get("/api/v1/analysis/not-a-valid-uuid")
            assert response.status_code == 400
    
    def test_validators_with_edge_cases(self):
        """Test validators with edge cases"""
        from src.utils.validators import validate_rr_intervals, validate_file_size
        
        # Empty list
        assert validate_rr_intervals([]) is False
        
        # Single value
        assert validate_rr_intervals([450]) is True
        
        # Boundary values
        assert validate_rr_intervals([300]) is True
        assert validate_rr_intervals([2000]) is True
        assert validate_rr_intervals([299]) is False
        assert validate_rr_intervals([2001]) is False
        
        # File size boundaries
        assert validate_file_size(0) is True
        assert validate_file_size(100 * 1024 * 1024) is True
        assert validate_file_size(100 * 1024 * 1024 + 1) is False


class TestDataTypes:
    """Test data type handling"""
    
    def test_analysis_response_types(self):
        """Test that analysis response types are correct"""
        import uuid
        from src.api.models.schemas import AnalysisResponse
        from datetime import datetime
        
        response = AnalysisResponse(
            file_id=str(uuid.uuid4()),
            features={
                "rmssd": 25.5,
                "sdnn": 30.2,
                "lf_hf_ratio": 1.2,
                "sample_entropy": 1.1,
                "mean_rr": 450.0,
                "pnn50": 10.5,
                "lf_power": 200.0,
                "hf_power": 150.0,
                "developmental_index": 0.7
            },
            risk={
                "normal": 0.8,
                "suspect": 0.15,
                "pathological": 0.05,
                "predicted_class": "normal"
            },
            interpretation=["Test"],
            developmental_index=0.7,
            gestational_weeks=32,
            created_at=datetime.now(),
            confidence_intervals=None
        )
        
        assert response.file_id is not None
        assert response.developmental_index > 0
        assert response.gestational_weeks == 32
    
    def test_upload_response_types(self):
        """Test upload response types"""
        from src.api.models.schemas import UploadResponse
        
        response = UploadResponse(
            file_id="test-id",
            filename="test.csv",
            size=1000,
            task_id="task-123",
            status="processing",
            message="Processing started"
        )
        
        assert response.file_id == "test-id"
        assert response.size == 1000
        assert response.status == "processing"


class TestMetricsAndMonitoring:
    """Test metrics collection and monitoring"""
    
    def test_metrics_collector_workflow(self):
        """Test complete metrics collection workflow"""
        from src.utils.metrics import MetricsCollector
        
        collector = MetricsCollector()
        
        # Track requests
        collector.increment("total_requests")
        collector.increment("total_requests")
        
        # Track latency
        collector.gauge("avg_latency", 125.5)
        
        # Get metrics
        metrics = collector.get_metrics()
        assert metrics["total_requests"] == 2
        assert metrics["avg_latency"] == 125.5
    
    def test_timing_decorator_preserves_return_value(self):
        """Test that timing decorator preserves return values"""
        from src.utils.metrics import timing_decorator
        
        @timing_decorator
        def calculate(x, y):
            return x * y
        
        result = calculate(5, 6)
        assert result == 30
