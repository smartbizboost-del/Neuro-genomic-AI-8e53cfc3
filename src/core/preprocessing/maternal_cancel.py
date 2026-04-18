import numpy as np
from sklearn.decomposition import FastICA
from scipy import signal
from typing import Tuple, Dict, Optional
from scipy.signal import find_peaks


def hybrid_maternal_cancellation(raw_ecg: np.ndarray, 
                                 sampling_rate: int = 250,
                                 maternal_reference: Optional[np.ndarray] = None) -> Tuple[np.ndarray, Dict]:
    """
    Hybrid maternal cancellation with built-in morphology quality check.
    Returns: (cleaned_ecg, quality_report)
    
    Args:
        raw_ecg: Input signal (1D or 2D)
        sampling_rate: Sampling frequency (default 250 Hz)
        maternal_reference: Optional reference maternal signal
    
    Returns:
        Tuple of (cleaned_ecg, quality_report)
    """
    if len(raw_ecg.shape) == 1:
        raw_ecg = raw_ecg.reshape(1, -1)

    try:
        # FastICA separation
        n_components = min(4, raw_ecg.shape[0])
        ica = FastICA(n_components=n_components, random_state=42, max_iter=500)
        sources = ica.fit_transform(raw_ecg.T).T

        # Remove maternal-dominant component
        variances = np.var(sources, axis=1)
        maternal_idx = np.argmax(variances)
        fetal_sources = np.delete(sources, maternal_idx, axis=0)

        cleaned = ica.inverse_transform(fetal_sources.T).T

        # Post-processing: high-pass filter
        b, a = signal.butter(4, 0.5 / (sampling_rate / 2), btype='high')
        cleaned = signal.filtfilt(b, a, cleaned, axis=1)

        final_signal = np.mean(cleaned, axis=0)

        # Morphology Quality Score
        morph_quality = compute_morphology_snr(final_signal, sampling_rate)

        quality_report = {
            "morphology_snr": round(morph_quality, 2),
            "status": "good" if morph_quality > 3.0 else "marginal" if morph_quality > 1.5 else "poor"
        }

        return final_signal, quality_report

    except Exception as e:
        print(f"Maternal cancellation failed: {e}")
        fallback_signal = np.mean(raw_ecg, axis=0) if len(raw_ecg.shape) > 1 else raw_ecg
        return fallback_signal, {"morphology_snr": 0.0, "status": "poor"}


def compute_morphology_snr(cleaned_ecg: np.ndarray, sampling_rate: int) -> float:
    """Compute SNR focused on morphological features (QRS and T-wave regions)"""
    # Simple QRS detection for SNR estimation
    peaks, _ = find_peaks(cleaned_ecg, distance=sampling_rate//2, prominence=np.std(cleaned_ecg)*0.5)
    
    if len(peaks) < 3:
        return 0.0
    
    # Estimate noise in non-QRS regions
    signal_power = np.var(cleaned_ecg)
    noise_segments = []
    for i in range(len(peaks)-1):
        mid = (peaks[i] + peaks[i+1]) // 2
        segment_start = max(0, mid - 50)
        segment_end = min(len(cleaned_ecg), mid + 50)
        if segment_end - segment_start > 0:
            noise_segments.append(cleaned_ecg[segment_start:segment_end])
    
    noise_power = np.mean([np.var(seg) for seg in noise_segments if len(seg) > 0])
    snr = 10 * np.log10(signal_power / (noise_power + 1e-8))
    return max(0.0, snr)


# Optional: Keep your individual functions for future advanced use
def fastica_separation(abdominal_signals: np.ndarray, n_components: int = 4):
    """Separate sources using FastICA"""
    ica = FastICA(n_components=n_components, random_state=42)
    sources = ica.fit_transform(abdominal_signals.T)
    return sources.T


def bilstm_cancel(maternal_signal, mixed_signal):
    """Placeholder for BiLSTM non-linear cancellation (not yet fully implemented)"""
    # TODO: Load pre-trained BiLSTM model here
    # For now return mixed_signal as fallback
    return mixed_signal
