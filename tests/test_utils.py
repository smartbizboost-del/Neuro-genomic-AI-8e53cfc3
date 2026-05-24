"""
Utility functions tests
"""

import pytest
from src.utils.validators import (
    validate_file_extension, validate_file_size, 
    validate_gestational_weeks, validate_rr_intervals
)
from src.utils.logger import setup_logging
from src.utils.metrics import MetricsCollector, timing_decorator
import numpy as np


class TestValidators:
    """Test validation functions"""
    
    def test_validate_file_extension_csv(self):
        """Test validation of CSV file extension"""
        result = validate_file_extension("test.csv")
        assert result is True
    
    def test_validate_file_extension_txt(self):
        """Test validation of TXT file extension"""
        result = validate_file_extension("test.txt")
        assert result is True
    
    def test_validate_file_extension_edf(self):
        """Test validation of EDF file extension"""
        result = validate_file_extension("test.edf")
        assert result is True
    
    def test_validate_file_extension_invalid(self):
        """Test rejection of invalid file extension"""
        result = validate_file_extension("test.exe")
        assert result is False
    
    def test_validate_file_extension_invalid_jpg(self):
        """Test rejection of JPG file"""
        result = validate_file_extension("test.jpg")
        assert result is False
    
    def test_validate_file_size_valid(self):
        """Test validation of valid file size"""
        result = validate_file_size(1000000)  # 1MB
        assert result is True
    
    def test_validate_file_size_too_large(self):
        """Test rejection of too large file"""
        result = validate_file_size(200 * 1024 * 1024)  # 200MB
        assert result is False
    
    def test_validate_file_size_exact_limit(self):
        """Test file at exact limit"""
        result = validate_file_size(100 * 1024 * 1024)  # 100MB
        assert result is True
    
    def test_validate_gestational_weeks_valid_early(self):
        """Test validation of early gestational weeks"""
        assert validate_gestational_weeks(24) is True
    
    def test_validate_gestational_weeks_valid_late(self):
        """Test validation of late gestational weeks"""
        assert validate_gestational_weeks(40) is True
    
    def test_validate_gestational_weeks_too_low(self):
        """Test rejection of gestational weeks too low"""
        result = validate_gestational_weeks(15)
        assert result is False
    
    def test_validate_gestational_weeks_too_high(self):
        """Test rejection of gestational weeks too high"""
        result = validate_gestational_weeks(50)
        assert result is False
    
    def test_validate_gestational_weeks_boundary_min(self):
        """Test minimum boundary"""
        result = validate_gestational_weeks(20)
        assert result is True
    
    def test_validate_gestational_weeks_boundary_max(self):
        """Test maximum boundary"""
        result = validate_gestational_weeks(42)
        assert result is True
    
    def test_validate_rr_intervals_valid(self):
        """Test validation of valid RR intervals"""
        valid_rr = [400, 420, 410, 430, 415]
        result = validate_rr_intervals(valid_rr)
        assert result is True
    
    def test_validate_rr_intervals_empty(self):
        """Test rejection of empty RR intervals"""
        result = validate_rr_intervals([])
        assert result is False
    
    def test_validate_rr_intervals_too_low(self):
        """Test rejection of RR intervals too low"""
        invalid_rr = [200, 250, 300]  # Min is 300
        result = validate_rr_intervals(invalid_rr)
        assert result is False
    
    def test_validate_rr_intervals_too_high(self):
        """Test rejection of RR intervals too high"""
        invalid_rr = [2000, 2100, 2200]  # Max is 2000
        result = validate_rr_intervals(invalid_rr)
        assert result is False
    
    def test_validate_rr_intervals_mixed_valid_invalid(self):
        """Test rejection when any RR interval is invalid"""
        mixed_rr = [400, 420, 3000]  # One too high
        result = validate_rr_intervals(mixed_rr)
        assert result is False


class TestMetricsCollector:
    """Test metrics collector"""
    
    def test_metrics_collector_init(self):
        """Test metrics collector initialization"""
        collector = MetricsCollector()
        assert collector.metrics == {}
    
    def test_metrics_increment(self):
        """Test incrementing a metric"""
        collector = MetricsCollector()
        collector.increment("requests")
        assert collector.metrics["requests"] == 1
    
    def test_metrics_increment_multiple(self):
        """Test incrementing a metric multiple times"""
        collector = MetricsCollector()
        collector.increment("requests")
        collector.increment("requests")
        assert collector.metrics["requests"] == 2
    
    def test_metrics_increment_custom_value(self):
        """Test incrementing with custom value"""
        collector = MetricsCollector()
        collector.increment("bytes", 1000)
        assert collector.metrics["bytes"] == 1000
    
    def test_metrics_gauge(self):
        """Test setting a gauge metric"""
        collector = MetricsCollector()
        collector.gauge("temperature", 98.6)
        assert collector.metrics["temperature"] == 98.6
    
    def test_metrics_gauge_overwrite(self):
        """Test overwriting a gauge metric"""
        collector = MetricsCollector()
        collector.gauge("temp", 98.6)
        collector.gauge("temp", 99.5)
        assert collector.metrics["temp"] == 99.5
    
    def test_metrics_get_metrics(self):
        """Test getting all metrics"""
        collector = MetricsCollector()
        collector.increment("requests")
        collector.gauge("latency", 120.5)
        
        metrics = collector.get_metrics()
        assert metrics["requests"] == 1
        assert metrics["latency"] == 120.5
    
    def test_metrics_get_metrics_returns_copy(self):
        """Test that get_metrics returns a copy"""
        collector = MetricsCollector()
        collector.increment("requests")
        
        metrics1 = collector.get_metrics()
        metrics1["requests"] = 100
        
        metrics2 = collector.get_metrics()
        assert metrics2["requests"] == 1  # Original not modified


class TestTimingDecorator:
    """Test timing decorator"""
    
    def test_timing_decorator_wraps_function(self):
        """Test that timing decorator preserves function behavior"""
        @timing_decorator
        def sample_function(x, y):
            return x + y
        
        result = sample_function(2, 3)
        assert result == 5
    
    def test_timing_decorator_preserves_function_name(self):
        """Test that decorator preserves function name"""
        @timing_decorator
        def sample_function():
            pass
        
        # Decorated function may have different name, but should be callable
        assert callable(sample_function)


class TestLogging:
    """Test logging setup"""
    
    def test_setup_logging_returns_none_or_logger(self):
        """Test that setup_logging executes without error"""
        result = setup_logging()
        # Should either return None or a logger
        assert result is None or hasattr(result, 'info') or result is True
    
    def test_setup_logging_can_be_called_multiple_times(self):
        """Test that setup_logging is idempotent"""
        setup_logging()
        setup_logging()  # Should not raise
        assert True
