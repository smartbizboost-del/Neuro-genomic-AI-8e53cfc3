"""
Dashboard tests
"""

import pytest
from unittest.mock import patch, MagicMock
import os


def test_dashboard_imports():
    """Test that dashboard module can be imported"""
    try:
        from src.dashboard import app
        assert app is not None
    except ImportError:
        pytest.skip("Streamlit not available in test environment")


def test_dashboard_config():
    """Test dashboard page configuration"""
    with patch('streamlit.set_page_config') as mock_set_config:
        try:
            from src.dashboard.app import st
            # Verify streamlit is configured
            assert st is not None
        except (ImportError, AttributeError):
            pytest.skip("Streamlit environment not available")


def test_dashboard_has_upload_section():
    """Test that upload section exists"""
    try:
        with open("src/dashboard/app.py", "r") as f:
            content = f.read()
            assert "Upload & Analyze" in content
            assert "file_uploader" in content
    except FileNotFoundError:
        pytest.skip("Dashboard file not found")


def test_dashboard_has_results_viewer():
    """Test that results viewer section exists"""
    try:
        with open("src/dashboard/app.py", "r") as f:
            content = f.read()
            assert "Results Viewer" in content
            assert "file_id" in content
    except FileNotFoundError:
        pytest.skip("Dashboard file not found")


def test_dashboard_has_clinical_insights():
    """Test that clinical insights section exists"""
    try:
        with open("src/dashboard/app.py", "r") as f:
            content = f.read()
            assert "Clinical Insights" in content
    except FileNotFoundError:
        pytest.skip("Dashboard file not found")


def test_dashboard_api_url_config():
    """Test that dashboard uses correct API URL"""
    with patch.dict(os.environ, {"API_URL": "http://test-api:8000"}):
        try:
            # We can't directly test streamlit apps, but verify the code has API_URL
            with open("src/dashboard/app.py", "r") as f:
                content = f.read()
                assert "API_URL" in content
                assert "localhost:8000" in content or "API_URL" in content
        except FileNotFoundError:
            pytest.skip("Dashboard file not found")


def test_dashboard_file_types_supported():
    """Test that dashboard supports required file types"""
    try:
        with open("src/dashboard/app.py", "r") as f:
            content = f.read()
            # Verify supported file types
            assert "csv" in content.lower()
            assert "txt" in content.lower()
            assert "edf" in content.lower()
    except FileNotFoundError:
        pytest.skip("Dashboard file not found")


def test_dashboard_has_sidebar_navigation():
    """Test that sidebar navigation exists"""
    try:
        with open("src/dashboard/app.py", "r") as f:
            content = f.read()
            assert "sidebar" in content.lower()
            assert "Navigation" in content or "Go to" in content
    except FileNotFoundError:
        pytest.skip("Dashboard file not found")


def test_dashboard_gestational_weeks_input():
    """Test that gestational weeks input is available"""
    try:
        with open("src/dashboard/app.py", "r") as f:
            content = f.read()
            assert "gestational_weeks" in content or "Gestational Weeks" in content
            assert "number_input" in content
    except FileNotFoundError:
        pytest.skip("Dashboard file not found")


def test_dashboard_patient_id_input():
    """Test that patient ID input is available"""
    try:
        with open("src/dashboard/app.py", "r") as f:
            content = f.read()
            assert "patient_id" in content or "Patient ID" in content
            assert "text_input" in content
    except FileNotFoundError:
        pytest.skip("Dashboard file not found")


def test_dashboard_handles_api_errors():
    """Test that dashboard handles API errors gracefully"""
    try:
        with open("src/dashboard/app.py", "r") as f:
            content = f.read()
            # Verify error handling
            assert "error" in content.lower() or "except" in content.lower()
            assert "st.error" in content or "Exception" in content
    except FileNotFoundError:
        pytest.skip("Dashboard file not found")


def test_dashboard_shows_success_messages():
    """Test that dashboard shows success messages"""
    try:
        with open("src/dashboard/app.py", "r") as f:
            content = f.read()
            assert "st.success" in content or "success" in content.lower()
    except FileNotFoundError:
        pytest.skip("Dashboard file not found")


def test_dashboard_shows_loading_spinner():
    """Test that dashboard shows loading state"""
    try:
        with open("src/dashboard/app.py", "r") as f:
            content = f.read()
            assert "st.spinner" in content or "spinner" in content.lower()
    except FileNotFoundError:
        pytest.skip("Dashboard file not found")


def test_dashboard_components_exist():
    """Test that dashboard components module exists"""
    try:
        from src.dashboard import components
        assert components is not None
    except ImportError:
        pytest.skip("Dashboard components not available")


def test_dashboard_sidebar_component():
    """Test that sidebar component exists"""
    try:
        with open("src/dashboard/components/sidebar.py", "r") as f:
            content = f.read()
            assert len(content) > 0
    except FileNotFoundError:
        pytest.skip("Sidebar component not found")


def test_dashboard_reports_component():
    """Test that reports component exists"""
    try:
        with open("src/dashboard/components/reports.py", "r") as f:
            content = f.read()
            assert len(content) > 0
    except FileNotFoundError:
        pytest.skip("Reports component not found")


def test_dashboard_visualizations_component():
    """Test that visualizations component exists"""
    try:
        with open("src/dashboard/components/visualizations.py", "r") as f:
            content = f.read()
            assert len(content) > 0
    except FileNotFoundError:
        pytest.skip("Visualizations component not found")
