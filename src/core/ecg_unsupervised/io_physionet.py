from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

try:
    import wfdb
except ImportError:
    wfdb = None


@dataclass(frozen=True)
class DatasetInfo:
    slug: str
    title: str
    url: str
    supports_fetal_ecg: bool


PHYSIONET_DATASETS: dict[str, DatasetInfo] = {
    "adfecgdb": DatasetInfo(
        slug="adfecgdb",
        title="Abdominal and Direct Fetal ECG Database",
        url="https://physionet.org/content/adfecgdb/",
        supports_fetal_ecg=True,
    ),
    "nifecgdb": DatasetInfo(
        slug="nifecgdb",
        title="Non-Invasive Fetal ECG Database",
        url="https://physionet.org/content/nifecgdb/",
        supports_fetal_ecg=True,
    ),
    "fecgsyndb": DatasetInfo(
        slug="fecgsyndb",
        title="Fetal ECG Synthetic Database",
        url="https://physionet.org/content/fecgsyndb/",
        supports_fetal_ecg=True,
    ),
    "ltdb": DatasetInfo(
        slug="ltdb",
        title="MIT-BIH Long-Term ECG Database",
        url="https://physionet.org/content/ltdb/",
        supports_fetal_ecg=False,
    ),
}

ALIASES = {
    "adecg": "adfecgdb",
    "adfecg": "adfecgdb",
    "longfecg": "ltdb",
    "longecg": "ltdb",
    "longecgdb": "ltdb",
    "nifecg": "nifecgdb",
    "fecgsynde": "fecgsyndb",
}


def resolve_dataset_name(name: str) -> str:
    normalized = name.lower().strip()
    normalized = ALIASES.get(normalized, normalized)
    if normalized not in PHYSIONET_DATASETS:
        supported = ", ".join(sorted(PHYSIONET_DATASETS))
        raise ValueError(
            f"Unsupported dataset '{name}'. Supported datasets: {supported}")
    return normalized


def get_record_candidates(
        dataset: str,
        explicit_record: str | None = None,
        limit: int = 20) -> list[str]:
    if explicit_record:
        return [explicit_record]
    if wfdb is None:
        return ["100"]

    try:
        records = wfdb.get_record_list(dataset)
    except Exception:
        records = []

    if not records:
        return ["100"]

    candidates: list[str] = []
    for rec in records[:limit]:
        for candidate in [str(rec), str(rec).replace(
                ".hea", ""), str(rec).replace(".dat", "")]:
            candidate = candidate.strip()
            if candidate and candidate not in candidates:
                candidates.append(candidate)
    return candidates or ["100"]


def download_record_dataframe(
        dataset: str,
        record: str,
        channels: list[int] | None = None) -> pd.DataFrame:
    if wfdb is None:
        raise ImportError(
            "wfdb is not installed. Install dependencies from requirements.txt first.")

    wf_record = wfdb.rdrecord(record, pn_dir=dataset, channels=channels)
    values = wf_record.p_signal
    if values.ndim == 1:
        values = values.reshape(-1, 1)

    names = wf_record.sig_name or [f"ch_{i}" for i in range(values.shape[1])]
    df = pd.DataFrame(values, columns=names)
    df.insert(0, "sample_index", np.arange(len(df), dtype=int))
    df.insert(1, "time_sec", df["sample_index"] / float(wf_record.fs))
    df["record_name"] = record
    df["dataset"] = dataset
    df["sampling_rate"] = float(wf_record.fs)
    return df
