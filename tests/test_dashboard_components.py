"""
Dashboard components tests
"""

import pytest
from unittest.mock import patch, MagicMock
import os


class TestDashboardSidebar:
    """Test dashboard sidebar component"""
    
    def test_sidebar_module_exists(self):
        """Test that sidebar module exists"""
        try:
            from src.dashboard.components import sidebar
            assert sidebar is not None
        except ImportError:
            pytest.skip("Streamlit not available")
    
    def test_sidebar_file_readable(self):
        """Test that sidebar file can be read"""
        try:
            with open("src/dashboard/components/sidebar.py", "r") as f:
                content = f.read()
                assert len(content) > 0
                # Should contain sidebar rendering code
                assert "def" in content or "streamlit" in content.lower()
        except FileNotFoundError:
            pytest.skip("File not found")


class TestDashboardReports:
    """Test dashboard reports component"""
    
    def test_reports_module_exists(self):
        """Test that reports module exists"""
        try:
            from src.dashboard.components import reports
            assert reports is not None
        except ImportError:
            pytest.skip("Streamlit not available")
    
    def test_reports_file_readable(self):
        """Test that reports file can be read"""
        try:
            with open("src/dashboard/components/reports.py", "r") as f:
                content = f.read()
                assert len(content) > 0
                # Should contain report rendering code
                assert "def" in content or "streamlit" in content.lower()
        except FileNotFoundError:
            pytest.skip("File not found")


class TestDashboardVisualizations:
    """Test dashboard visualizations component"""
    
    def test_visualizations_module_exists(self):
        """Test that visualizations module exists"""
        try:
            from src.dashboard.components import visualizations
            assert visualizations is not None
        except ImportError:
            pytest.skip("Streamlit not available")
    
    def test_visualizations_file_readable(self):
        """Test that visualizations file can be read"""
        try:
            with open("src/dashboard/components/visualizations.py", "r") as f:
                content = f.read()
                assert len(content) > 0
                # Should contain visualization rendering code
                assert "def" in content or "plotly" in content.lower()
        except FileNotFoundError:
            pytest.skip("File not found")


class TestDashboardApp:
    """Test main dashboard app"""
    
    def test_dashboard_app_file_exists(self):
        """Test that dashboard app file exists"""
        import os
        assert os.path.exists("src/dashboard/app.py")
    
    def test_dashboard_app_has_required_sections(self):
        """Test that dashboard has all required sections"""
        with open("src/dashboard/app.py", "r") as f:
            content = f.read()
        
        # Check for main sections
        assert "Upload & Analyze" in content
        assert "Results Viewer" in content
        assert "Clinical Insights" in content
    
    def test_dashboard_uses_api_client(self):
        """Test that dashboard uses API client"""
        with open("src/dashboard/app.py", "r") as f:
            content = f.read()
        
        # Should make API calls
        assert "requests" in content or "API_URL" in content
    
    def test_dashboard_page_config(self):
        """Test that dashboard has page configuration"""
        with open("src/dashboard/app.py", "r") as f:
            content = f.read()
        
        # Check for page config
        assert "set_page_config" in content or "page_icon" in content
    
    def test_dashboard_has_file_uploader(self):
        """Test that dashboard has file uploader"""
        with open("src/dashboard/app.py", "r") as f:
            content = f.read()
        
        assert "file_uploader" in content or "upload" in content.lower()
    
    def test_dashboard_has_error_handling(self):
        """Test that dashboard handles errors"""
        with open("src/dashboard/app.py", "r") as f:
            content = f.read()
        
        # Should have error/exception handling
        assert "error" in content.lower() or "except" in content.lower()
    
    def test_dashboard_has_spinner(self):
        """Test that dashboard shows loading state"""
        with open("src/dashboard/app.py", "r") as f:
            content = f.read()
        
        # Should have loading indicator
        assert "spinner" in content.lower() or "loading" in content.lower()


class TestComponentStructure:
    """Test component structure and organization"""
    
    def test_components_package_init_exists(self):
        """Test that components package is properly initialized"""
        import os
        assert os.path.exists("src/dashboard/components/__init__.py")
    
    def test_all_component_files_exist(self):
        """Test that all expected component files exist"""
        components = [
            "sidebar.py",
            "reports.py",
            "visualizations.py"
        ]
        
        for component in components:
            path = f"src/dashboard/components/{component}"
            assert os.path.exists(path), f"{component} not found"
    
    def test_components_are_python_files(self):
        """Test that all components are valid Python files"""
        import os
        components_dir = "src/dashboard/components"
        
        for filename in os.listdir(components_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                filepath = os.path.join(components_dir, filename)
                # Should be readable as Python
                with open(filepath, "r") as f:
                    content = f.read()
                    # Should not be empty (excluding __init__)
                    assert len(content) > 0
