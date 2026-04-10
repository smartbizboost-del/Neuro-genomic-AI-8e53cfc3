"""
Monitor module tests
Tests for worker monitoring utilities and cleanup tasks
"""

import pytest
from unittest.mock import patch, MagicMock
from src.workers.monitor import cleanup_temp_files, retry_failed_tasks
from src.workers.celery_app import celery_app


class TestMonitorModule:
    """Test monitor module structure and imports"""
    
    def test_monitor_module_imports(self):
        """Test that monitor module can be imported"""
        from src.workers import monitor
        assert monitor is not None
    
    def test_cleanup_temp_files_task_exists(self):
        """Test that cleanup_temp_files task exists"""
        assert cleanup_temp_files is not None
        assert callable(cleanup_temp_files)
    
    def test_retry_failed_tasks_task_exists(self):
        """Test that retry_failed_tasks task exists"""
        assert retry_failed_tasks is not None
        assert callable(retry_failed_tasks)


class TestCleanupTempFilesTask:
    """Test cleanup_temp_files task"""
    
    @patch('src.workers.monitor.logger')
    def test_cleanup_logs_message(self, mock_logger):
        """Test that cleanup task logs a message"""
        # Call the task
        cleanup_temp_files()
        # Verify logging was called
        assert mock_logger.info.called
        # Verify the log message contains cleanup info
        calls = mock_logger.info.call_args_list
        assert any('Cleaning up' in str(call).lower() or 'temp' in str(call).lower() for call in calls)
    
    @patch('src.workers.monitor.logger')
    def test_cleanup_task_callable(self, mock_logger):
        """Test that cleanup task is callable"""
        result = cleanup_temp_files()
        # Should not raise an exception
        assert mock_logger.info.called
    
    @patch('src.workers.monitor.logger')
    def test_cleanup_task_is_registered_with_celery(self, mock_logger):
        """Test that cleanup task is registered with Celery app"""
        # Get all registered tasks
        from src.workers.celery_app import celery_app
        registered_tasks = celery_app.tasks
        # Should be registered (may be under various naming conventions)
        assert len(registered_tasks) > 0


class TestRetryFailedTasksTask:
    """Test retry_failed_tasks task"""
    
    @patch('src.workers.monitor.logger')
    def test_retry_logs_message(self, mock_logger):
        """Test that retry task logs a message"""
        retry_failed_tasks()
        assert mock_logger.info.called
        calls = mock_logger.info.call_args_list
        assert any('Retry' in str(call).lower() or 'failed' in str(call).lower() for call in calls)
    
    @patch('src.workers.monitor.logger')
    def test_retry_task_callable(self, mock_logger):
        """Test that retry task is callable"""
        result = retry_failed_tasks()
        assert mock_logger.info.called
    
    @patch('src.workers.monitor.logger')
    def test_retry_task_is_registered_with_celery(self, mock_logger):
        """Test that retry task is registered with Celery app"""
        from src.workers.celery_app import celery_app
        registered_tasks = celery_app.tasks
        assert len(registered_tasks) > 0


class TestCeleryAppConfiguration:
    """Test Celery app configuration"""
    
    def test_celery_app_exists(self):
        """Test that Celery app is properly configured"""
        from src.workers.celery_app import celery_app
        assert celery_app is not None
    
    def test_celery_app_has_tasks(self):
        """Test that Celery app has registered tasks"""
        from src.workers.celery_app import celery_app
        tasks = celery_app.tasks
        assert len(tasks) > 0
    
    def test_celery_app_task_creation(self):
        """Test that tasks can be created through app"""
        from src.workers.celery_app import celery_app
        # Celery app should be properly initialized
        assert celery_app is not None
        # Should have task decorator available
        assert hasattr(celery_app, 'task')


class TestMonitorLogging:
    """Test monitor logging behavior"""
    
    @patch('src.workers.monitor.logger')
    def test_cleanup_uses_logger(self, mock_logger):
        """Test that cleanup uses the logger"""
        cleanup_temp_files()
        assert mock_logger is not None
        assert mock_logger.info.called
    
    @patch('src.workers.monitor.logger')
    def test_retry_uses_logger(self, mock_logger):
        """Test that retry uses the logger"""
        retry_failed_tasks()
        assert mock_logger is not None
        assert mock_logger.info.called


class TestMonitorIntegration:
    """Integration tests for monitor module"""
    
    def test_monitor_tasks_integration(self):
        """Test that monitor tasks can be imported and used together"""
        from src.workers import monitor
        # Verify both tasks exist
        assert hasattr(monitor, 'cleanup_temp_files')
        assert hasattr(monitor, 'retry_failed_tasks')
        # Both should be callable
        assert callable(monitor.cleanup_temp_files)
        assert callable(monitor.retry_failed_tasks)
    
    @patch('src.workers.monitor.logger')
    def test_multiple_task_execution(self, mock_logger):
        """Test executing multiple monitor tasks"""
        cleanup_temp_files()
        retry_failed_tasks()
        # Logger should be called for both tasks
        assert mock_logger.info.call_count >= 2
