import os
import time
import sentry_sdk
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DATA_FILE = Path(os.getenv("DATA_FILE", "/data/visits.txt"))

import sentry_sdk

sentry_sdk.init(
    dsn="http://f5c2d8386e3849ffbb25fba7d9c08297@127.0.0.1/1",
    traces_sample_rate=0.01,  # 1% of transactions — adjust to your needs
    auto_session_tracking=False,  # GlitchTip does not support sessions
    # enable_logs=True,  # Opt-in: send logs to GlitchTip (uses disk space)
)

app = FastAPI(
    title="Kubernetes Config Demo",
    description="A small FastAPI app demonstrating ConfigMap, Secret, PVC, and Prometheus metrics.",
    version=APP_VERSION,
)

HTTP_REQUESTS = Counter(
    "fastapi_demo_http_requests_total",
    "Total HTTP requests handled by this application, excluding /metrics scrapes.",
    ["method", "path", "status"],
)
HTTP_REQUEST_DURATION = Histogram(
    "fastapi_demo_http_request_duration_seconds",
    "HTTP request duration in seconds, excluding /metrics scrapes.",
    ["method", "path"],
)
APP_INFO = Gauge(
    "fastapi_demo_info",
    "Static information about the running FastAPI demo.",
    ["version", "environment"],
)
PERSISTENT_VISITS = Gauge(
    "fastapi_demo_persistent_visits_total",
    "Number of visits persisted in the mounted PVC.",
)
APP_INFO.labels(
    version=APP_VERSION,
    environment=os.getenv("APP_ENV", "unset"),
).set(1)


def record_visit() -> tuple[int | None, bool]:
    """Increment a small counter stored on the PVC, if writable."""
    try:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        current = int(DATA_FILE.read_text(encoding="utf-8").strip()) if DATA_FILE.exists() else 0
        updated = current + 1
        temporary_file = DATA_FILE.with_suffix(".tmp")
        temporary_file.write_text(f"{updated}\n", encoding="utf-8")
        os.replace(temporary_file, DATA_FILE)
        PERSISTENT_VISITS.set(updated)
        return updated, True
    except (OSError, ValueError):
        return None, False


@app.middleware("http")
async def observe_http_requests(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)

    started = time.perf_counter()
    status_code = "500"
    try:
        response = await call_next(request)
        status_code = str(response.status_code)
        return response
    finally:
        elapsed = time.perf_counter() - started
        path = request.url.path
        HTTP_REQUESTS.labels(request.method, path, status_code).inc()
        HTTP_REQUEST_DURATION.labels(request.method, path).observe(elapsed)


@app.get("/")
def read_demo_values():
    visits, storage_writable = record_visit()
    return {
        "message_from_configmap": os.getenv("APP_MESSAGE", "APP_MESSAGE is not set"),
        "environment_from_configmap": os.getenv("APP_ENV", "APP_ENV is not set"),
        "demo_secret_message": os.getenv("SECRET_GREETING", "SECRET_GREETING is not set"),
        "api_token_configured": bool(os.getenv("API_TOKEN")),
        "api_token_returned": False,
        "persistent_visits": visits,
        "persistent_storage_writable": storage_writable,
        "metrics_path": "/metrics",
    }


@app.get("/healthz")
def health_check():
    return {"status": "ok", "version": APP_VERSION}


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
