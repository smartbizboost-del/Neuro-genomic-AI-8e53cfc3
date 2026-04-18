"""Top-level compatibility package for notebook and API imports."""

try:
    from .feature_extraction import HRVExtractor
except Exception:  # optional legacy dependency chain
    HRVExtractor = None

try:
    from .preprocessing import DataCleaner, ECGPreprocessor, SignalPreprocessor
except Exception:  # optional legacy dependency chain
    DataCleaner = None
    ECGPreprocessor = None
    SignalPreprocessor = None

try:
    from .visualization import AnalysisVisualizer, SignalVisualizer
except Exception:  # optional legacy dependency chain
    AnalysisVisualizer = None
    SignalVisualizer = None

__all__ = [
    name
    for name in [
        "AnalysisVisualizer",
        "DataCleaner",
        "ECGPreprocessor",
        "HRVExtractor",
        "SignalPreprocessor",
        "SignalVisualizer",
    ]
    if globals().get(name) is not None
]
