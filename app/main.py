import os
import sentry_sdk
from fastapi import FastAPI
from app.monitoring import CONTENT_TYPE_LATEST, http_request_counter, generate_latest
from fastapi.responses import Response

DSN = os.getenv("DSN", "")
RATE = os.getenv("RATE")
APP_MESSAGE = os.getenv("APP_MESSAGE", "APP_MESSAGE is not set")
APP_ENV = os.getenv("APP_ENV", "APP_ENV is not set")
SECRET_GREETING = os.getenv("SECRET_GREETING", "SECRET_GREETING is not set")

sentry_sdk.init(
    dsn= DSN,
    traces_sample_rate= RATE,
    auto_session_tracking=False
)

app = FastAPI(
    title="Kubernetes",
)

@app.get("/")
async def read_values():
    http_request_counter.labels(
        method="GET",
        path="/",
        status="200"
    ).inc()

    return {
        "message_from_configmap": APP_MESSAGE,
        "environment_from_configmap": APP_ENV,
        "demo_secret_message": SECRET_GREETING
    }

@app.get("/healthz")
async def health_check():
    return {"status": "ok"}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)