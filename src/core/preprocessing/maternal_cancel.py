# src/core/preprocessing/maternal_cancel.py
from sklearn.decomposition import FastICA
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Bidirectional, Dense
import numpy as np

def fastica_separation(abdominal_signals, n_components=4):
    """Separate sources using FastICA (no thoracic reference needed)"""
    ica = FastICA(n_components=n_components, random_state=42)
    sources = ica.fit_transform(abdominal_signals.T)
    return sources.T

def identify_maternal_component(sources, maternal_template=None):
    """Identify which ICA component is maternal-dominant"""
    # Correlation with maternal template or highest power
    maternal_idx = np.argmax([np.var(src) for src in sources])
    return sources[maternal_idx]

def bilstm_cancel(maternal_signal, mixed_signal):
    """BiLSTM for non-linear adaptive cancellation"""
    model = Sequential([
        Bidirectional(LSTM(64, return_sequences=True), input_shape=(None, 1)),
        Bidirectional(LSTM(32)),
        Dense(1)
    ])
    # ... train or load pre-trained weights
    fetal_estimate = model.predict(maternal_signal)
    return mixed_signal - fetal_estimate