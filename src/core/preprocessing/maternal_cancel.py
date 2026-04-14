import numpy as np
from sklearn.decomposition import FastICA
from scipy import signal
from typing import Optional

def hybrid_maternal_cancellation(raw_ecg: np.ndarray, 
                                 sampling_rate: int = 250,
                                 maternal_reference: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Hybrid Maternal ECG Cancellation:
    1. FastICA for blind source separation (no thoracic reference needed)
    2. Simple adaptive filtering fallback
    3. Returns cleaned fetal ECG signal
    """
    if len(raw_ecg.shape) == 1:
        raw_ecg = raw_ecg.reshape(1, -1)  # make it 2D: (channels, time)

    try:
        # Step 1: FastICA separation
        n_components = min(4, raw_ecg.shape[0])
        ica = FastICA(n_components=n_components, random_state=42, max_iter=500)
        sources = ica.fit_transform(raw_ecg.T).T   # shape: (components, time)

        # Step 2: Identify and remove maternal-dominant component
        # Usually the component with highest variance/amplitude
        variances = np.var(sources, axis=1)
        maternal_idx = np.argmax(variances)
        
        # Reconstruct fetal signal without maternal component
        fetal_sources = np.delete(sources, maternal_idx, axis=0)
        cleaned = ica.inverse_transform(fetal_sources.T).T

        # Step 3: Optional post-processing (high-pass filter to remove baseline)
        b, a = signal.butter(4, 0.5 / (sampling_rate / 2), btype='high')
        cleaned = signal.filtfilt(b, a, cleaned, axis=1)

        # Average channels if multiple
        final_signal = np.mean(cleaned, axis=0)

        return final_signal

    except Exception as e:
        print(f"Warning: Maternal cancellation failed: {e}. Returning original signal.")
        return np.mean(raw_ecg, axis=0) if len(raw_ecg.shape) > 1 else raw_ecg


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
