"""
Script to train and serialize the Core ML Models (Classifier + GMM + Scaler) 
so they can be loaded rapidly at application startup without synchronous cold-starts.
"""
import os
import joblib
import numpy as np
import logging
from src.core.classifier import CognitiveStateClassifier
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def train_and_save_models():
    logger.info("Initializing models...")
    classifier = CognitiveStateClassifier(model_type='gb')
    unsupervised_model = GaussianMixture(n_components=3, random_state=42)
    scaler = StandardScaler()
    
    logger.info("Bootstrapping Supervised Gradient Boosting Model...")
    # Synthetic generator matching clinical boundaries
    X_train = []
    y_train = []
    
    # Generate 100 Normal cases (High RMSSD, good SDNN, balanced LF_HF)
    for _ in range(100):
        X_train.append([np.random.normal(45, 10), np.random.normal(50, 15), 
                        np.random.normal(400, 50), np.random.normal(1.5, 0.3), np.random.normal(15, 5)])
        y_train.append("normal")
        
    # Generate 100 Suspect cases (Medium RMSSD, high LF_HF)
    for _ in range(100):
        X_train.append([np.random.normal(25, 8), np.random.normal(35, 10), 
                        np.random.normal(450, 50), np.random.normal(2.5, 0.4), np.random.normal(8, 3)])
        y_train.append("suspect")
        
    # Generate 100 Pathological cases (Low RMSSD, low SDNN, extreme LF_HF)
    for _ in range(100):
        X_train.append([np.random.normal(10, 5), np.random.normal(15, 5), 
                        np.random.normal(500, 50), np.random.normal(3.5, 0.5), np.random.normal(2, 1)])
        y_train.append("pathological")
        
    classifier.train(np.array(X_train), np.array(y_train))
    
    # Bootstrap the Unsupervised Model with the synthetic distribution
    X_train_scaled = scaler.fit_transform(np.array(X_train))
    unsupervised_model.fit(X_train_scaled)
    logger.info("Unsupervised Gaussian Mixture Model Bootstrapped.")
    
    model_dir = os.getenv("MODEL_DIR", "data/models")
    os.makedirs(model_dir, exist_ok=True)
    
    logger.info(f"Saving models to {model_dir}...")
    joblib.dump(classifier.model, f"{model_dir}/classifier.pkl")
    joblib.dump(unsupervised_model, f"{model_dir}/unsupervised.pkl")
    joblib.dump(scaler, f"{model_dir}/scaler.pkl")
    
    logger.info("Models successfully saved! You can now start the API.")

if __name__ == "__main__":
    train_and_save_models()
