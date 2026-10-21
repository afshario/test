from prometheus_client import (Counter, generate_latest, CONTENT_TYPE_LATEST)

HTTP_REQUESTS = Counter(
    "fastapi_demo_http_requests_total",
    "Total HTTP requests handled by this application, excluding /metrics scrapes.",
    ["method", "path", "status"]
)