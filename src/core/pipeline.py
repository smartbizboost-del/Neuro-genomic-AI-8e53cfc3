"""
Core processing pipeline for Neuro-Genomic AI
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import logging

from src.core.ecg_unsupervised.preprocessing import ECGPreprocessor
from src.core.ecg_unsupervised.separation import FetalECGSeparator
from src.core.ecg_unsupervised.features import WindowedFeatureExtractor

# Import the Core ML Classifiers
from src.core.classifier import CognitiveStateClassifier
import joblib
import os
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class NeuroGenomicPipeline:
    """Main processing pipeline for fetal ECG analysis"""
    
    def __init__(self):
        self.feature_extractor = None
        self.classifier = CognitiveStateClassifier(model_type='gb')
        self.unsupervised_model = GaussianMixture(n_components=3, random_state=42)
        self.scaler = StandardScaler()
        self.model_dir = os.getenv("MODEL_DIR", "data/models")
        # Do not bootstrap synchronously anymore
        
    def load_models(self):
        """Load pre-trained models from disk to avoid cold starts"""
        try:
            logger.info(f"Loading models from {self.model_dir}...")
            if os.path.exists(f"{self.model_dir}/classifier.pkl"):
                self.classifier.model = joblib.load(f"{self.model_dir}/classifier.pkl")
                self.unsupervised_model = joblib.load(f"{self.model_dir}/unsupervised.pkl")
                self.scaler = joblib.load(f"{self.model_dir}/scaler.pkl")
                logger.info("Models directly loaded successfully.")
                return True
            else:
                logger.warning(f"No models found at {self.model_dir}. Please run scripts/train_models.py")
                return False
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return False
        
    def process_recording(self, mixed_signal: np.ndarray, sampling_rate: int = 500, gestational_weeks: Optional[int] = None) -> Dict[str, Any]:
        """
        Process raw multichannel ECG signals and extract features
        
        Args:
            mixed_signal: np.ndarray of shape (samples, channels)
            sampling_rate: Sampling rate in Hz
            gestational_weeks: Gestational age in weeks
            
        Returns:
            Dictionary with features, risk assessment, and interpretation
        """
        logger.info("Preprocessing signal...")
        preprocessor = ECGPreprocessor(sampling_rate=sampling_rate)
        # Ensure we have a valid 2D array for cleaning
        if mixed_signal.ndim == 1:
            mixed_signal = np.column_stack([mixed_signal, mixed_signal])
            
        cleaned = preprocessor.transform(mixed_signal)
        
        logger.info("Separating fetal and maternal components...")
        separator = FetalECGSeparator(n_components=2, random_state=42)
        comps = separator.fit_transform(cleaned)
        maternal_idx, fetal_idx = separator.infer_maternal_fetal_indices(fs=sampling_rate)
        
        maternal_ecg = comps[:, maternal_idx]
        fetal_ecg = comps[:, fetal_idx]
        
        logger.info("Extracting windowed features...")
        extractor = WindowedFeatureExtractor(sampling_rate=sampling_rate, window_sec=10)
        features_df = extractor.extract(maternal=maternal_ecg, fetal=fetal_ecg)
        
        if features_df.empty:
            raise ValueError("No valid features could be extracted from the signal windows.")
            
        # Average features across all windows to give a singular result to the front-end
        avg_features = features_df.mean().to_dict()
        
        # Calculate developmental index using actual mathematical features from the array
        features = {
            "rmssd": float(avg_features.get("fet_rmssd", 0.0)),
            "sdnn": float(avg_features.get("fet_rr_std", 0.0)),
            "mean_rr": float(1000.0 / avg_features.get("fet_hr_mean", 1.0)) if avg_features.get("fet_hr_mean", 0) > 0 else 0,
            "lf_power": float(avg_features.get("fet_low_freq_power", 0.0)),
            "hf_power": float(avg_features.get("fet_high_freq_power", 0.0)),
            "pnn50": float(avg_features.get("fet_pnn50", 0.0)),
            "sample_entropy": float(avg_features.get("fet_sampen", 1.15)),
        }
        
        # Calculate LF/HF
        if features["hf_power"] > 0:
            features["lf_hf_ratio"] = float(features["lf_power"] / features["hf_power"])
        else:
            features["lf_hf_ratio"] = 0.0
            
        developmental_index = self._calculate_developmental_index(features, gestational_weeks)
        risk = self._classify_risk(features)
        risk["developmental_index"] = developmental_index
        interpretation = self._generate_interpretation(features, risk)
        
        return {
            "features": features,
            "developmental_index": developmental_index,
            "risk": risk,
            "interpretation": interpretation
        }
        
    def _calculate_developmental_index(self, features: Dict[str, float], gestational_weeks: Optional[int]) -> float:
        """Calculate composite developmental index"""
        weights = {
            "rmssd": 0.3,
            "lf_hf_ratio": 0.2,
            "sample_entropy": 0.3,
            "sdnn": 0.2
        }
        index = sum(features.get(feature, 0) * weight for feature, weight in weights.items())
        return min(max(index / 100, 0), 1)
    
    def _classify_risk(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Classify risk using the Supervised Gradient Boosting Model built from Legacy Code"""
        X_test = np.array([[
            features.get("rmssd", 0),
            features.get("sdnn", 0),
            features.get("mean_rr", 0),
            features.get("lf_hf_ratio", 0),
            features.get("pnn50", 0)
        ]])
        
        prediction = self.classifier.predict(X_test)[0]
        
        # Pull probabilities if supported
        probabilities = [0.0, 0.0, 0.0]
        try:
            proba = self.classifier.model.predict_proba(X_test)[0]
            classes = self.classifier.model.classes_
            prob_dict = {classes[i]: proba[i] for i in range(len(classes))}
            normal_p = prob_dict.get("normal", 0.0)
            suspect_p = prob_dict.get("suspect", 0.0)
            pathological_p = prob_dict.get("pathological", 0.0)
        except AttributeError:
            normal_p, suspect_p, pathological_p = 0.0, 0.0, 0.0

        # Unsupervised Risk Assessment
        X_test_scaled = self.scaler.transform(X_test)
        unsupervised_cluster = self.unsupervised_model.predict(X_test_scaled)[0]
        # score_samples returns log-likelihoods. Negative log-likelihood = anomaly score
        anomaly_score = -float(self.unsupervised_model.score_samples(X_test_scaled)[0])

        return {
            "normal": float(normal_p),
            "suspect": float(suspect_p),
            "pathological": float(pathological_p),
            "predicted_class": prediction,
            "model_used": "GradientBoostingClassifier",
            "unsupervised_cluster": int(unsupervised_cluster),
            "anomaly_score": anomaly_score
        }
    
    def _generate_interpretation(self, features: Dict[str, float], risk: Dict[str, Any]) -> List[str]:
        """Generate clinical interpretation"""
        interpretation = []
        interpretation.append(f"AI Prediction Method: {risk.get('model_used', 'Supervised Rules')}")
        
        if features.get("rmssd", 0) > 30:
            interpretation.append("RMSSD indicates good vagal tone")
        else:
            interpretation.append("RMSSD suggests reduced vagal tone")
            
        if features.get("lf_hf_ratio", 0) < 2.0:
            interpretation.append("LF/HF ratio suggests healthy autonomic balance")
        else:
            interpretation.append("LF/HF ratio indicates autonomic imbalance")
            
        if risk["predicted_class"] == "normal":
            interpretation.append("Supervised Model predicts physiological state is Normal")
        elif risk["predicted_class"] == "suspect":
            interpretation.append("Supervised Model identified Suspect characteristics for monitoring")
        else:
            interpretation.append("Supervised Model identified Pathological warnings!")
            
        anomaly_score = risk.get("anomaly_score", 0.0)
        if anomaly_score > 15.0:
            interpretation.append("Unsupervised Analysis: High anomaly score detected, unusual physiological pattern.")
        else:
            interpretation.append("Unsupervised Analysis: Values fall within expected physiological clusters.")
            
        return interpretation