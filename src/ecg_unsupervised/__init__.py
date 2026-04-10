"""Compatibility package that re-exports the ECG unsupervised workflow."""

from .features import WindowedFeatureExtractor
from .io_physionet import PHYSIONET_DATASETS, download_record_dataframe, resolve_dataset_name
from .pipeline import run_unsupervised_pipeline
from .preprocessing import ECGPreprocessor
from .separation import FetalECGSeparator
from .unsupervised_model import UnsupervisedFetalECGModel

__all__ = [
    "ECGPreprocessor",
    "FetalECGSeparator",
    "PHYSIONET_DATASETS",
    "UnsupervisedFetalECGModel",
    "WindowedFeatureExtractor",
    "download_record_dataframe",
    "resolve_dataset_name",
    "run_unsupervised_pipeline",
]