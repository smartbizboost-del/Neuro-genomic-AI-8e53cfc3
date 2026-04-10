"""
Logging middleware
"""

from fastapi import Request
import logging
import time

from src.utils.logger import index_log_record

logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    """Log incoming requests"""
    start_time = time.time()
    
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    log_payload = {
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "level": "INFO",
        "method": request.method,
        "endpoint": str(request.url.path),
        "status_code": response.status_code,
        "response_time_ms": int(process_time * 1000),
    }
    logger.info(f"Response: {response.status_code} - {process_time:.2f}s")
    index_log_record(log_payload)
    
    return response