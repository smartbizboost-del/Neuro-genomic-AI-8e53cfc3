"""
Core processing pipeline for Neuro-Genomic AI
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
import os

from src.core.ecg_unsupervised.preprocessing import ECGPreprocessor
from src.core.ecg_unsupervised.separation import FetalECGSeparator
from src.core.ecg_unsupervised.features import WindowedFeatureExtractor

# Import the legacy Cognitive State Classifier
from src_legacy.legacy.model import CognitiveStateClassifier
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
        self._is_bootstrapped = False
        self.confidence_high_threshold = self._read_threshold("CONFIDENCE_HIGH_THRESHOLD", 0.80)
        self.confidence_medium_threshold = self._read_threshold("CONFIDENCE_MEDIUM_THRESHOLD", 0.60)
        if self.confidence_medium_threshold > self.confidence_high_threshold:
            self.confidence_medium_threshold, self.confidence_high_threshold = (
                self.confidence_high_threshold,
                self.confidence_medium_threshold,
            )
        self._bootstrap_model()

    @staticmethod
    def _read_threshold(env_name: str, default: float) -> float:
        try:
            return min(max(float(os.getenv(env_name, str(default))), 0.0), 1.0)
        except (TypeError, ValueError):
            return default
        
    def _bootstrap_model(self):
        """Train the GradientBoosting Model on synthetic historical logic limits"""
        logger.info("Bootstrapping Supervised Gradient Boosting Model...")
        # Features order: rmssd, sdnn, mean_rr, lf_hf_ratio, pnn50
        # y format: "normal", "suspect", "pathological"
        
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
            
        self.classifier.train(np.array(X_train), np.array(y_train))
        
        # Bootstrap the Unsupervised Model with the synthetic distribution
        X_train_scaled = self.scaler.fit_transform(np.array(X_train))
        self.unsupervised_model.fit(X_train_scaled)
        self._is_bootstrapped = True
        logger.info("Unsupervised Gaussian Mixture Model Bootstrapped.")

    def train_model(self, force_retrain: bool = False) -> None:
        """Compatibility hook for API startup lifecycle."""
        if force_retrain or not self._is_bootstrapped:
            self._bootstrap_model()

    def _confidence_label(self, confidence: float) -> str:
        if confidence >= self.confidence_high_threshold:
            return "high"
        if confidence >= self.confidence_medium_threshold:
            return "medium"
        return "low"
        
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
            "sample_entropy": 1.15, # Sample Entropy placeholder as not available natively in pipeline features yet
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

        confidence_level = float(max(normal_p, suspect_p, pathological_p))
        return {
            "normal": float(normal_p),
            "suspect": float(suspect_p),
            "pathological": float(pathological_p),
            "predicted_class": prediction,
            "model_used": "GradientBoostingClassifier",
            "confidence_level": confidence_level,
            "confidence_label": self._confidence_label(confidence_level),
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