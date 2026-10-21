import sentry_sdk
from fastapi import FastAPI
from configs import (DSN, RATE, APP_MESSAGE, APP_ENV, SECRET_GREETING)
from app.monitoring import ( CONTENT_TYPE_LATEST, HTTP_REQUESTS, generate_latest)
from fastapi.responses import Response

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
    HTTP_REQUESTS.inc()
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