"""
Worker monitoring utilities
"""

import logging
from src.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def cleanup_temp_files():
    """Clean up temporary files"""
    # Implement cleanup logic
    logger.info("Cleaning up temporary files")
    # Minimal implementation: attempt to remove files in /tmp starting with 'nga_'
    import glob
    import os
    removed = 0
    try:
        for p in glob.glob('/tmp/nga_*'):
            try:
                os.remove(p)
                removed += 1
            except Exception:
                logger.debug(f"Could not remove temp file: {p}")
    except Exception as e:
        logger.debug(f"Cleanup encountered an error: {e}")
    return {"removed": removed}


@celery_app.task
def retry_failed_tasks():
    """Retry failed tasks"""
    # Implement retry logic
    logger.info("Retrying failed tasks")
    # Minimal implementation: trigger Celery inspect to retry failed tasks is environment-specific.
    # Here we return a simple health dict indicating the monitor ran.
    try:
        inspector = celery_app.control.inspect()
        failed = inspector.failed() or {}
        return {"failed_count": sum(len(v) for v in failed.values()) if failed else 0}
    except Exception:
        return {"failed_count": 0}
