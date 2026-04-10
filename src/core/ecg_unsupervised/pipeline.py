from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .features import WindowedFeatureExtractor
from .io_physionet import download_record_dataframe, get_record_candidates, resolve_dataset_name
from .preprocessing import ECGPreprocessor
from .separation import FetalECGSeparator
from .unsupervised_model import UnsupervisedFetalECGModel


def _numeric_signal_columns(df: pd.DataFrame) -> list[str]:
    excluded = {"sample_index", "time_sec", "record_name", "dataset", "sampling_rate"}
    return [c for c in df.columns if c not in excluded and pd.api.types.is_numeric_dtype(df[c])]


def _load_one_dataset(dataset_name: str, explicit_record: str | None = None) -> tuple[pd.DataFrame, str, str]:
    dataset = resolve_dataset_name(dataset_name)
    for rec in get_record_candidates(dataset=dataset, explicit_record=explicit_record):
        try:
            return download_record_dataframe(dataset=dataset, record=rec), dataset, rec
        except Exception:
            continue
    raise ValueError(f"No readable record found for dataset: {dataset}")


def run_unsupervised_pipeline(
    datasets: list[str],
    record: str | None = None,
    window_sec: int = 10,
    method: str = "gmm",
    n_clusters: int = 3,
    output_dir: str | Path = "results/unsupervised",
) -> dict[str, object]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    parts: list[pd.DataFrame] = []
    sources: list[dict[str, str]] = []

    for dataset_name in datasets:
        raw_df, resolved_dataset, selected_record = _load_one_dataset(dataset_name, explicit_record=record)
        raw_df = raw_df.copy()
        raw_df["source_dataset"] = resolved_dataset
        raw_df["source_record"] = selected_record
        parts.append(raw_df)
        sources.append({"dataset": resolved_dataset, "record": selected_record, "rows": str(len(raw_df))})

    merged = pd.concat(parts, ignore_index=True, sort=False)
    numeric_cols = _numeric_signal_columns(merged)
    if len(numeric_cols) < 1:
        raise ValueError("No numeric ECG channels found in downloaded records.")

    primary_col = numeric_cols[0]
    secondary_col = numeric_cols[1] if len(numeric_cols) > 1 else None

    x1 = pd.to_numeric(merged[primary_col], errors="coerce").interpolate(limit_direction="both")
    if secondary_col is None:
        x2 = x1.shift(1).fillna(method="bfill") * 0.95
    else:
        x2 = pd.to_numeric(merged[secondary_col], errors="coerce").interpolate(limit_direction="both")

    x1 = x1.fillna(method="ffill").fillna(method="bfill").to_numpy(dtype=float)
    x2 = x2.fillna(method="ffill").fillna(method="bfill").to_numpy(dtype=float)

    fs = int(float(merged["sampling_rate"].dropna().iloc[0])) if "sampling_rate" in merged.columns else 500

    mixed = np.column_stack([x1, x2])
    preprocessor = ECGPreprocessor(sampling_rate=fs)
    cleaned = preprocessor.transform(mixed)

    separator = FetalECGSeparator(n_components=2, random_state=42)
    comps = separator.fit_transform(cleaned)
    maternal_idx, fetal_idx = separator.infer_maternal_fetal_indices(fs=fs)

    maternal = comps[:, maternal_idx]
    fetal = comps[:, fetal_idx]

    extractor = WindowedFeatureExtractor(sampling_rate=fs, window_sec=window_sec)
    features = extractor.extract(maternal=maternal, fetal=fetal)
    if len(features) < 8:
        raise ValueError(
            f"Only {len(features)} windows produced after preprocessing. Use longer records or smaller window_sec."
        )

    model = UnsupervisedFetalECGModel(method=method, n_clusters=n_clusters, random_state=42)
    labels, x_pca = model.fit_predict(features)
    metrics = model.evaluate_clusters(x=x_pca, labels=labels)

    features_with_labels = features.copy()
    features_with_labels["cluster"] = labels

    source_table = pd.DataFrame(sources)
    features_file = output_path / "window_features_with_clusters.csv"
    metrics_file = output_path / "cluster_metrics.csv"
    source_file = output_path / "source_records.csv"

    features_with_labels.to_csv(features_file, index=False)
    pd.DataFrame([metrics]).to_csv(metrics_file, index=False)
    source_table.to_csv(source_file, index=False)

    return {
        "features": features_with_labels,
        "metrics": metrics,
        "sources": source_table,
        "primary_channel": primary_col,
        "secondary_channel": secondary_col if secondary_col is not None else "synthetic_shifted_copy",
        "sampling_rate": fs,
        "output_dir": str(output_path),
    }
