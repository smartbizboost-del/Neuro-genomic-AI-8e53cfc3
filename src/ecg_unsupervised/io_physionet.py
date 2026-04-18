"""Compatibility wrapper for PhysioNet data helpers."""

from src.core.ecg_unsupervised.io_physionet import PHYSIONET_DATASETS, download_record_dataframe, resolve_dataset_name

__all__ = [
    "PHYSIONET_DATASETS",
    "download_record_dataframe",
    "resolve_dataset_name"]
