"""
Logging middleware
"""

from fastapi import Request
import logging
import time

logger = logging.getLogger(__name__)


async def log_requests(request: Request, call_next):
    """Log incoming requests"""
    start_time = time.time()

    logger.info(f"Request: {request.method} {request.url}")

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.2f}s")

    return response
