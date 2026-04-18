"""
Celery application configuration
"""

from celery import Celery
import os

# Redis configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery app
celery_app = Celery(
    'neuro_genomic',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['src.workers.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Africa/Nairobi',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

# Configure result backends
celery_app.conf.result_backend = REDIS_URL
celery_app.conf.result_expires = 3600 * 24 * 7  # 7 days

# Configure task routing
celery_app.conf.task_routes = {
    'process_ecg_file': {'queue': 'processing'},
    'train_model': {'queue': 'training'},
    'batch_analysis': {'queue': 'batch'},
}

# Configure beat schedule (periodic tasks)
celery_app.conf.beat_schedule = {
    'cleanup-temp-files': {
        'task': 'src.workers.tasks.cleanup_temp_files',
        'schedule': 3600.0,  # Every hour
    },
    'retry-failed-tasks': {
        'task': 'src.workers.tasks.retry_failed',
        'schedule': 300.0,  # Every 5 minutes
    },
}
