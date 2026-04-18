# src/core/signal_quality.py
import numpy as np
from scipy import stats, signal
from sklearn.ensemble import RandomForestClassifier


def extract_sqi_features(ecg_channel, fs=250):
    """Extract 37 SQI features from a single ECG channel"""
    features = {}

    # Frequency domain features
    freqs, psd = signal.welch(ecg_channel, fs, nperseg=fs * 2)

    # pband2: power in 10-20 Hz (fetal band)
    features['pband2'] = np.trapz(psd[(freqs >= 10) & (
        freqs <= 20)], freqs[(freqs >= 10) & (freqs <= 20)])

    # pband4: power in 48-52 Hz (power line interference)
    features['pband4'] = np.trapz(psd[(freqs >= 48) & (
        freqs <= 52)], freqs[(freqs >= 48) & (freqs <= 52)])

    # seSQI: spectral entropy
    psd_norm = psd / np.sum(psd)
    features['seSQI'] = -np.sum(psd_norm * np.log2(psd_norm + 1e-12))

    # Time domain features
    features['kSQI'] = stats.kurtosis(ecg_channel)
    features['sSQI'] = stats.skew(ecg_channel)
    features['snr'] = 10 * \
        np.log10(np.var(ecg_channel) / np.var(np.diff(ecg_channel)))

    return features


def classify_signal_quality(features):
    """Return GOOD, ACCEPTABLE, or POOR based on trained classifier"""
    # Load pre-trained model
    model = RandomForestClassifier()
    # ... load model weights
    quality_score = model.predict_proba([features])[0]
    if quality_score[0] > 0.8:
        return "GOOD"
    elif quality_score[0] > 0.5:
        return "ACCEPTABLE"
    else:
        return "POOR"
