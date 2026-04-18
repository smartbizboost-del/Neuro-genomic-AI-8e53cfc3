"""
Monitoring service for Prometheus metrics and live system telemetry.
"""

from datetime import datetime
from typing import Dict

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'api_request_latency_seconds',
    'API request latency',
    ['method', 'endpoint']
)
ACTIVE_USERS_GAUGE = Gauge(
    'active_users',
    'Number of active users in the system'
)

# Store the latest latency for live streaming and dashboards
LAST_REQUEST_LATENCY_MS = 0.0


def record_request(method: str, endpoint: str,
                   status_code: int, elapsed_seconds: float):
    """Record Prometheus metrics for an API request."""
    global LAST_REQUEST_LATENCY_MS
    REQUEST_COUNT.labels(
        method=method,
        endpoint=endpoint,
        status=str(status_code)).inc()
    REQUEST_LATENCY.labels(
        method=method,
        endpoint=endpoint).observe(elapsed_seconds)
    LAST_REQUEST_LATENCY_MS = elapsed_seconds * 1000


def set_active_users(active_users: int):
    """Update the active users gauge."""
    ACTIVE_USERS_GAUGE.set(active_users)


def get_api_call_count() -> int:
    """Return the accumulated API call count from Prometheus metrics."""
    total = 0
    for metric in REQUEST_COUNT.collect():
        for sample in metric.samples:
            if sample.name == 'api_requests_total':
                total += sample.value
    return int(total)


def get_last_latency_ms() -> float:
    """Return the last recorded request latency in milliseconds."""
    return LAST_REQUEST_LATENCY_MS


def get_prometheus_metrics() -> Response:
    """Return a Prometheus-compatible metrics response."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def get_live_metrics(active_users: int = 0) -> Dict[str, object]:
    """Return a lightweight live metrics payload for WebSocket streaming."""
    return {
        'active_users': active_users,
        'api_calls': get_api_call_count(),
        'latency_ms': round(get_last_latency_ms(), 2),
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'status': 'healthy'
    }
