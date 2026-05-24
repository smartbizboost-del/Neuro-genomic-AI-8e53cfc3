"""Unified local launcher for Neuro-Genomic AI backend and dashboard."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_API_HOST = os.getenv("API_HOST", "127.0.0.1")
DEFAULT_API_PORT = os.getenv("API_PORT", "8000")
DEFAULT_DASH_HOST = os.getenv("DASHBOARD_HOST", "127.0.0.1")
DEFAULT_DASH_PORT = os.getenv("STREAMLIT_PORT", "8501")


def _spawn_process(command: list[str], env: dict[str, str] | None = None) -> subprocess.Popen:
    return subprocess.Popen(
        command,
        cwd=ROOT,
        env=env or os.environ.copy(),
    )


def _terminate_process(proc: subprocess.Popen) -> None:
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def _wait_for_any_process(processes: dict[str, subprocess.Popen]) -> tuple[str, int | None]:
    while True:
        for name, proc in processes.items():
            if proc.poll() is not None:
                return name, proc.returncode
        time.sleep(0.5)


def start_backend(host: str, port: str, reload: bool) -> subprocess.Popen:
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "src.api.main:app",
        "--host",
        host,
        "--port",
        port,
    ]
    if reload:
        command.append("--reload")
    print(f"Starting API server: {' '.join(command)}")
    return _spawn_process(command)


def start_dashboard(host: str, port: str) -> subprocess.Popen:
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "src/dashboard/app.py",
        "--server.address",
        host,
        "--server.port",
        port,
        "--server.headless",
        "true",
    ]
    print(f"Starting dashboard: {' '.join(command)}")
    return _spawn_process(command)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Neuro-Genomic AI backend and Streamlit dashboard together."
    )
    parser.add_argument("--no-api", action="store_true", help="Do not start the backend API.")
    parser.add_argument(
        "--no-dashboard",
        action="store_true",
        help="Do not start the Streamlit dashboard.",
    )
    parser.add_argument(
        "--api-host",
        default=DEFAULT_API_HOST,
        help="API host address.",
    )
    parser.add_argument(
        "--api-port",
        default=DEFAULT_API_PORT,
        help="API port.",
    )
    parser.add_argument(
        "--dashboard-host",
        default=DEFAULT_DASH_HOST,
        help="Dashboard host address.",
    )
    parser.add_argument(
        "--dashboard-port",
        default=DEFAULT_DASH_PORT,
        help="Dashboard port.",
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable Uvicorn auto-reload for the backend.",
    )

    args = parser.parse_args()
    processes: dict[str, subprocess.Popen] = {}

    if not args.no_api:
        processes["api"] = start_backend(args.api_host, args.api_port, not args.no_reload)
    if not args.no_dashboard:
        processes["dashboard"] = start_dashboard(args.dashboard_host, args.dashboard_port)

    if not processes:
        print("Nothing to start. Use --no-api or --no-dashboard to disable services.")
        return 0

    def shutdown(signum: int, frame: object | None) -> None:
        print("Shutting down services...")
        for proc in processes.values():
            _terminate_process(proc)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        process_name, returncode = _wait_for_any_process(processes)
        print(f"Service '{process_name}' exited with code {returncode}.")
        return 0 if returncode == 0 else returncode or 1
    finally:
        for proc in processes.values():
            _terminate_process(proc)


if __name__ == "__main__":
    raise SystemExit(main())
