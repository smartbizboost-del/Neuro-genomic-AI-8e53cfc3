"""
Logging utilities
"""

import logging
import sys
import os
from pathlib import Path

try:
    from elasticsearch import Elasticsearch
except ImportError:
    Elasticsearch = None

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
ES_CLIENT = None
if ELASTICSEARCH_URL and Elasticsearch is not None:
    try:
        ES_CLIENT = Elasticsearch(ELASTICSEARCH_URL)
    except Exception:
        ES_CLIENT = None


def setup_logging(level=logging.INFO):
    """Setup application logging"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('neuro_genomic.log')
        ]
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('boto3').setLevel(logging.WARNING)


def index_log_record(record: dict):
    """Index a log record into Elasticsearch if configured."""
    if ES_CLIENT is None:
        return

    try:
        ES_CLIENT.index(index="neuro_genomic_logs", document=record)
    except Exception:
        logging.getLogger(__name__).warning("Failed to index log record to Elasticsearch")
    logging.getLogger('botocore').setLevel(logging.WARNING)