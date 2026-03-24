"""
Model training script
"""

import sys
sys.path.append('src')

from src.core.pipeline import NeuroGenomicPipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_model():
    """Train the ML model"""
    pipeline = NeuroGenomicPipeline()
    
    logger.info("Starting model training...")
    
    # This would implement actual model training
    # For now, just load the pipeline
    pipeline.train_model()
    
    logger.info("Model training completed!")

if __name__ == "__main__":
    train_model()