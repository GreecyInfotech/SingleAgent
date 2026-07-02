from __future__ import annotations

from prometheus_client import Counter, Histogram

REQUESTS_TOTAL = Counter(
    "app_requests_total",
    "Total number of requests",
    ["path", "method", "status"],
)

LATENCY_SECONDS = Histogram(
    "app_request_latency_seconds",
    "Request latency in seconds",
    ["path", "method"],
)
