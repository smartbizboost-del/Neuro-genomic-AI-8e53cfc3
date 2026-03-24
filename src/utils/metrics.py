"""
Metrics and monitoring utilities
"""

import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def timing_decorator(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

class MetricsCollector:
    """Simple metrics collector"""
    
    def __init__(self):
        self.metrics = {}
    
    def increment(self, name: str, value: int = 1):
        """Increment a counter metric"""
        if name not in self.metrics:
            self.metrics[name] = 0
        self.metrics[name] += value
    
    def gauge(self, name: str, value: float):
        """Set a gauge metric"""
        self.metrics[name] = value
    
    def get_metrics(self):
        """Get all metrics"""
        return self.metrics.copy()

# Global metrics instance
metrics = MetricsCollector()