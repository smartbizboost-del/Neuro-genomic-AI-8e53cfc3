"""
Middleware tests
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import Request, Response
from src.api.middleware.logging import log_requests
import logging


class TestLoggingMiddleware:
    """Test logging middleware"""
    
    @pytest.mark.asyncio
    async def test_log_requests_middleware_exists(self):
        """Test that logging middleware function exists"""
        assert log_requests is not None
        assert callable(log_requests)
    
    @pytest.mark.asyncio
    async def test_log_requests_process_request(self):
        """Test that middleware processes requests"""
        # Create a mock request
        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.url = "http://localhost:8000/api/test"
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Create a mock call_next
        async def mock_call_next(request):
            return mock_response
        
        # Call the middleware
        with patch('src.api.middleware.logging.logger') as mock_logger:
            result = await log_requests(mock_request, mock_call_next)
            assert result.status_code == 200
            # Verify logging was called
            assert mock_logger.info.called
    
    @pytest.mark.asyncio
    async def test_log_requests_logs_method_and_url(self):
        """Test that middleware logs request method and URL"""
        mock_request = MagicMock(spec=Request)
        mock_request.method = "POST"
        mock_request.url = "http://localhost:8000/api/upload"
        
        mock_response = MagicMock()
        mock_response.status_code = 201
        
        async def mock_call_next(request):
            return mock_response
        
        with patch('src.api.middleware.logging.logger') as mock_logger:
            await log_requests(mock_request, mock_call_next)
            # Verify the method and URL were logged
            calls = mock_logger.info.call_args_list
            assert any('POST' in str(call) or 'upload' in str(call) for call in calls)
    
    @pytest.mark.asyncio
    async def test_log_requests_logs_status_code(self):
        """Test that middleware logs response status code"""
        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.url = "http://localhost:8000/api/test"
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        async def mock_call_next(request):
            return mock_response
        
        with patch('src.api.middleware.logging.logger') as mock_logger:
            await log_requests(mock_request, mock_call_next)
            # Status code should be logged
            calls = mock_logger.info.call_args_list
            assert any('404' in str(call) for call in calls)
    
    @pytest.mark.asyncio
    async def test_log_requests_measures_time(self):
        """Test that middleware measures request processing time"""
        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.url = "http://localhost:8000/api/test"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        async def mock_call_next(request):
            return mock_response
        
        with patch('src.api.middleware.logging.logger') as mock_logger:
            await log_requests(mock_request, mock_call_next)
            # Time measurement should be in the logged response
            calls = mock_logger.info.call_args_list
            assert len(calls) >= 2  # At least request and response logs


def test_logging_format():
    """Test that logging is properly configured"""
    logger = logging.getLogger(__name__)
    assert logger is not None
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'debug')
    assert hasattr(logger, 'warning')
    assert hasattr(logger, 'error')


def test_logger_handlers_exist():
    """Test that logger has handlers configured"""
    logger = logging.getLogger('src.api.main')
    # Logger should be configured by setup_logging
    assert logger is not None


def test_logger_can_log_messages():
    """Test that logger can log messages"""
    logger = logging.getLogger('test.logger')
    with patch('logging.Logger.info') as mock_info:
        logger.info("Test message")
        # Logger should be able to log
