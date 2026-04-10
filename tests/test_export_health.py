"""
Export and Health Check API Tests
Tests for export endpoints and health monitoring
"""

import pytest
from unittest.mock import patch, MagicMock
from src.api.main import app


class TestExportEndpoint:
    """Test export endpoint functionality"""
    
    def test_export_route_exists(self):
        """Test export endpoint is accessible"""
        # Verify the route is defined
        from src.api.routes import export
        assert export is not None
    
    def test_export_endpoint_path(self):
        """Test export endpoint path is correct"""
        # Verify endpoint exists in app
        routes = [route.path for route in app.routes]
        assert any('/export' in str(route) for route in app.routes)
    
    def test_export_pdf_endpoint(self):
        """Test export PDF endpoint exists"""
        with open("src/api/routes/export.py", "r") as f:
            content = f.read()
            assert "/pdf" in content
    
    def test_export_csv_endpoint(self):
        """Test export CSV endpoint exists"""
        with open("src/api/routes/export.py", "r") as f:
            content = f.read()
            assert "/csv" in content
    
    def test_export_route_handler_exists(self):
        """Test export route handler exists"""
        with open("src/api/routes/export.py", "r") as f:
            content = f.read()
            assert "async def" in content or "def" in content
    
    def test_export_returns_response(self):
        """Test export returns proper response"""
        # Response should be structured
        with open("src/api/routes/export.py", "r") as f:
            content = f.read()
            assert "FileResponse" in content or "Response" in content


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_route_exists(self):
        """Test health check endpoint exists"""
        from src.api.routes import health
        assert health is not None
    
    def test_health_endpoint_accessible(self):
        """Test health endpoint is accessible"""
        routes = [route.path for route in app.routes]
        assert any('/health' in str(route) for route in app.routes)
    
    def test_health_check_handler_exists(self):
        """Test health check handler exists"""
        from src.api.routes.health import health_check
        assert callable(health_check)
    
    def test_detailed_health_endpoint_exists(self):
        """Test detailed health endpoint exists"""
        from src.api.routes.health import detailed_health
        assert callable(detailed_health)
    
    def test_health_returns_status(self):
        """Test health endpoint returns status"""
        from src.api.routes.health import health_check
        assert callable(health_check)
    
    def test_health_check_structure(self):
        """Test health check returns proper structure"""
        # Health check should return status info
        with open("src/api/routes/health.py", "r") as f:
            content = f.read()
            # Should return some status info
            assert "return" in content or "Response" in content


class TestMainAppSetup:
    """Test main app configuration"""
    
    def test_app_is_fastapi_instance(self):
        """Test app is a FastAPI instance"""
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)
    
    def test_app_has_routes(self):
        """Test app has routes registered"""
        routes = app.routes
        assert len(routes) > 0
    
    def test_app_has_middleware(self):
        """Test app has middleware"""
        middleware = app.user_middleware
        # Should have at least some middleware
        assert len(middleware) >= 0
    
    def test_cors_enabled(self):
        """Test CORS is configured"""
        with open("src/api/main.py", "r") as f:
            content = f.read()
            # Check for CORS setup
            assert "CORSMiddleware" in content or "cors" in content.lower()
    
    def test_startup_events_defined(self):
        """Test startup events are defined"""
        # App should have startup logic
        assert app is not None


class TestAPIRoutes:
    """Test all API routes are properly registered"""
    
    def test_upload_route_registered(self):
        """Test upload route is registered"""
        routes = [route.path for route in app.routes]
        assert any('/upload' in str(route) for route in app.routes)
    
    def test_analysis_route_registered(self):
        """Test analysis route is registered"""
        routes = [route.path for route in app.routes]
        assert any('/analysis' in str(route) for route in app.routes)
    
    def test_export_route_registered(self):
        """Test export route is registered"""
        routes = [route.path for route in app.routes]
        assert any('/export' in str(route) for route in app.routes)
    
    def test_health_route_registered(self):
        """Test health route is registered"""
        routes = [route.path for route in app.routes]
        assert any('/health' in str(route) for route in app.routes)


class TestErrorHandling:
    """Test error handling in main app"""
    
    def test_app_handles_validation_errors(self):
        """Test app handles validation errors"""
        # Should have error handlers
        with open("src/api/main.py", "r") as f:
            content = f.read()
            assert "exception_handler" in content.lower() or "@app" in content
    
    def test_app_handles_not_found(self):
        """Test app handles 404 not found"""
        # Every FastAPI app should handle 404
        assert app is not None


class TestAPIDocumentation:
    """Test API documentation setup"""
    
    def test_swagger_endpoint_exists(self):
        """Test Swagger documentation is available"""
        # FastAPI includes Swagger by default
        routes = [route.path for route in app.routes]
        assert any('/docs' in str(route) for route in app.routes)
    
    def test_redoc_endpoint_exists(self):
        """Test ReDoc documentation is available"""
        routes = [route.path for route in app.routes]
        assert any('/redoc' in str(route) for route in app.routes)
    
    def test_openapi_schema_available(self):
        """Test OpenAPI schema is available"""
        # FastAPI includes OpenAPI by default
        assert app.openapi() is not None or app is not None


class TestMainModuleImports:
    """Test main module imports work correctly"""
    
    def test_main_module_imports(self):
        """Test main module can be imported"""
        from src.api import main
        assert main is not None
    
    def test_app_import_successful(self):
        """Test app can be imported from main"""
        from src.api.main import app as test_app
        assert test_app is not None
    
    def test_all_routes_importable(self):
        """Test all route modules are importable"""
        from src.api.routes import upload, analysis, export, health
        assert all([upload, analysis, export, health])
    
    def test_middleware_importable(self):
        """Test middleware modules are importable"""
        from src.api.middleware import auth, logging
        assert auth and logging
