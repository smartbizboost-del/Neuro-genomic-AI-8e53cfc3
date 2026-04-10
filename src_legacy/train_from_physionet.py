import argparse
from pathlib import Path

from ecg_unsupervised import PHYSIONET_DATASETS, run_unsupervised_pipeline


def _dataset_help() -> str:
    lines = []
    for key, info in PHYSIONET_DATASETS.items():
        support = "fetal-ecg" if info.supports_fetal_ecg else "general-ecg"
        lines.append(f"- {key}: {info.title} ({support}) -> {info.url}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run unsupervised fetal ECG clustering from PhysioNet records.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--datasets",
        default="nifecgdb,adfecgdb,fecgsyndb",
        help="Comma-separated dataset slugs or aliases.\n" + _dataset_help(),
    )
    parser.add_argument("--record", default=None, help="Optional specific record name to use for all datasets.")
    parser.add_argument("--window-sec", type=int, default=10, help="Window size for feature extraction.")
    parser.add_argument("--method", choices=["gmm", "kmeans", "dbscan"], default="gmm", help="Unsupervised clustering method.")
    parser.add_argument("--clusters", type=int, default=3, help="Cluster count for gmm/kmeans.")
    parser.add_argument("--output-dir", default="results/unsupervised", help="Directory for csv outputs.")

    args = parser.parse_args()

    datasets = [d.strip() for d in args.datasets.split(",") if d.strip()]
    if not datasets:
        raise ValueError("At least one dataset must be supplied with --datasets")

    result = run_unsupervised_pipeline(
        datasets=datasets,
        record=args.record,
        window_sec=args.window_sec,
        method=args.method,
        n_clusters=args.clusters,
        output_dir=Path(args.output_dir),
    )

    print("Unsupervised ECG pipeline completed.")
    print(f"Sources:\n{result['sources']}")
    print(f"Primary channel: {result['primary_channel']}")
    print(f"Secondary channel: {result['secondary_channel']}")
    print(f"Sampling rate: {result['sampling_rate']} Hz")
    print(f"Cluster metrics: {result['metrics']}")
    print(f"Outputs written to: {result['output_dir']}")


if __name__ == "__main__":
    main()
