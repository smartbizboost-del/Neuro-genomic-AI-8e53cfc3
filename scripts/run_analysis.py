"""CLI runner for analysis modules converted from notebooks.
Usage:
    python scripts/run_analysis.py --file /path/to/ecg.csv --patient PT_001 --weeks 32
Or:
    python scripts/run_analysis.py --db ../data/processed/neuro_genomic.db
"""
import argparse
import json
from pathlib import Path
from src.analysis import load_ecg_from_db, butter_bandpass_filter, run_ica, extract_heart_rate_features


def run_from_file(path: Path, patient_id: str = "PT_001", weeks: int = 32):
    try:
        import pandas as pd
        df = pd.read_csv(path)
        if {"time_s", "ch1", "ch2"}.issubset(df.columns):
            t = df["time_s"].values
            ecg_signal = df[["ch1", "ch2"]].to_numpy()
            fs = int(df["fs"].iloc[0]) if "fs" in df.columns else 500
        else:
            raise ValueError("CSV missing expected columns")
    except Exception:
        # fallback to DB loader
        t, ecg_signal, fs, duration, src = load_ecg_from_db(Path("../data/processed/neuro_genomic.db"))

    filtered = butter_bandpass_filter(ecg_signal, fs)
    ics, mixing = run_ica(filtered)
    feat1, peaks1 = extract_heart_rate_features(ics[:, 0], fs, "IC1")
    feat2, peaks2 = extract_heart_rate_features(ics[:, 1], fs, "IC2")

    output = {
        "patient_id": patient_id,
        "gestational_weeks": weeks,
        "features": {"ic1": feat1, "ic2": feat2},
    }
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, help='ECG CSV file to analyze')
    parser.add_argument('--db', type=str, help='Path to processed DB')
    parser.add_argument('--patient', type=str, default='PT_001')
    parser.add_argument('--weeks', type=int, default=32)
    args = parser.parse_args()

    if args.file:
        run_from_file(Path(args.file), args.patient, args.weeks)
    else:
        # use DB
        t, ecg_signal, fs, duration, src = load_ecg_from_db(Path(args.db or '../data/processed/neuro_genomic.db'))
        filtered = butter_bandpass_filter(ecg_signal, fs)
        ics, mixing = run_ica(filtered)
        feat1, peaks1 = extract_heart_rate_features(ics[:, 0], fs, "IC1")
        feat2, peaks2 = extract_heart_rate_features(ics[:, 1], fs, "IC2")
        import json
        out = {"patient": args.patient, "weeks": args.weeks, "features": {"ic1": feat1, "ic2": feat2}}
        print(json.dumps(out, indent=2))
