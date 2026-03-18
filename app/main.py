from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from redis import Redis
from redis.exceptions import RedisError
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import os
import socket
import time

app = FastAPI(title="Legacy Service Modernized")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

REQUEST_COUNT = Counter("app_requests_total", "Total app requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Request latency", ["endpoint"])

class Task(BaseModel):
    id: str
    description: str
    status: str

def get_redis():
    return Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.get("/health")
def health():
    start = time.time()
    try:
        r = get_redis()
        r.ping()
        status = "ok"
        redis_status = "connected"
    except RedisError:
        status = "degraded"
        redis_status = "unreachable"

    REQUEST_COUNT.labels(method="GET", endpoint="/health", status=status).inc()
    REQUEST_LATENCY.labels(endpoint="/health").observe(time.time() - start)

    return {
        "status": status,
        "redis": redis_status,
        "hostname": socket.gethostname()
    }

@app.get("/api/v1/status")
def status():
    start = time.time()
    response = {
        "service": "legacy-modernized-api",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "dev")
    }
    REQUEST_COUNT.labels(method="GET", endpoint="/api/v1/status", status="200").inc()
    REQUEST_LATENCY.labels(endpoint="/api/v1/status").observe(time.time() - start)
    return response

@app.post("/api/v1/tasks")
def create_task(task: Task):
    start = time.time()
    try:
        r = get_redis()
        r.hset(f"task:{task.id}", mapping=task.dict())
        REQUEST_COUNT.labels(method="POST", endpoint="/api/v1/tasks", status="201").inc()
        REQUEST_LATENCY.labels(endpoint="/api/v1/tasks").observe(time.time() - start)
        return {"message": "task stored", "task": task}
    except RedisError as e:
        REQUEST_COUNT.labels(method="POST", endpoint="/api/v1/tasks", status="500").inc()
        REQUEST_LATENCY.labels(endpoint="/api/v1/tasks").observe(time.time() - start)
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)