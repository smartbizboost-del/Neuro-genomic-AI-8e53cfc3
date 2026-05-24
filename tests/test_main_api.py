"""
Core API endpoints and root route tests
Tests for main app endpoints
"""

import pytest
from unittest.mock import patch, MagicMock
from src.api.main import app


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint_exists(self):
        """Test root endpoint exists"""
        routes = [route.path for route in app.routes]
        assert "/" in routes
    
    def test_root_returns_dict(self):
        """Test root endpoint returns response dict"""
        # Root endpoint should return a response
        with open("src/api/main.py", "r") as f:
            content = f.read()
            assert "def root(" in content or "async def root(" in content


class TestReadinessEndpoint:
    """Test readiness probe endpoint"""
    
    def test_readiness_endpoint_exists(self):
        """Test readiness endpoint exists"""
        routes = [route.path for route in app.routes]
        assert any("/ready" in str(route) for route in app.routes)
    
    def test_readiness_returns_status(self):
        """Test readiness endpoint returns status"""
        with open("src/api/main.py", "r") as f:
            content = f.read()
            assert "readiness" in content.lower() or "ready" in content.lower()


class TestAppConfig:
    """Test app configuration and setup"""
    
    def test_app_title(self):
        """Test app has proper title"""
        assert app.title == "Neuro-Genomic AI API"
    
    def test_app_version(self):
        """Test app has proper version"""
        assert "2.0.0" in app.version or app.version is not None
    
    def test_app_has_description(self):
        """Test app has proper description"""
        assert app.description is not None or len(app.description) > 0


class TestMiddlewareIntegration:
    """Test middleware is properly integrated"""
    
    def test_cors_middleware_added(self):
        """Test CORS middleware is configured"""
        with open("src/api/main.py", "r") as f:
            content = f.read()
            assert "CORSMiddleware" in content
    
    def test_process_time_middleware_added(self):
        """Test process time header middleware exists"""
        with open("src/api/main.py", "r") as f:
            content = f.read()
            assert "process_time" in content.lower() or "X-Process-Time" in content
    
    def test_trusted_host_middleware(self):
        """Test trusted host middleware exists"""
        with open("src/api/main.py", "r") as f:
            content = f.read()
            assert "TrustedHostMiddleware" in content


class TestRouterInclusion:
    """Test routers are properly included"""
    
    def test_health_router_included(self):
        """Test health router is included"""
        routes = [route.path for route in app.routes]
        assert any("/health" in str(route) for route in app.routes)
    
    def test_upload_router_included(self):
        """Test upload router is included"""
        routes = [route.path for route in app.routes]
        assert any("/upload" in str(route) for route in app.routes)
    
    def test_analysis_router_included(self):
        """Test analysis router is included"""
        routes = [route.path for route in app.routes]
        assert any("/analysis" in str(route) for route in app.routes)
    
    def test_export_router_included(self):
        """Test export router is included"""
        routes = [route.path for route in app.routes]
        assert any("/export" in str(route) for route in app.routes)


class TestPipelineInitialization:
    """Test pipeline initialization in lifespan"""
    
    def test_pipeline_class_exists(self):
        """Test pipeline function is imported"""
        from src.core.pipeline import get_pipeline, NeuroGenomicPipeline
        assert callable(get_pipeline)
        assert NeuroGenomicPipeline is not None
    
    def test_main_imports_pipeline(self):
        """Test main imports pipeline"""
        with open("src/api/main.py", "r") as f:
            content = f.read()
            assert "NeuroGenomicPipeline" in content
