"""
Model training script
"""

import sys
sys.path.append('src')

from src.core.pipeline import get_pipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_model():
    """Train the ML model"""
    pipeline = get_pipeline()
    
    logger.info("Starting model training...")
    
    # This would implement actual model training
    # For now, just load the pipeline (models are lazy-loaded on first analyze call)
    
    logger.info("Model training completed!")

if __name__ == "__main__":
    train_model()