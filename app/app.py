
from flask import Flask, jsonify, render_template, request, Response, g
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
import random
import time

app = Flask(__name__)

# 1. Total HTTP requests
HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["endpoint", "method", "status"],
)

# 2. HTTP request duration in seconds
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "Duration of HTTP requests in seconds",
    ["endpoint", "method"],
)

# 3. Failed HTTP requests (status code 400 or higher)
HTTP_REQUESTS_FAILED = Counter(
    "http_requests_failed_total",
    "Total number of failed HTTP requests",
    ["endpoint", "method", "status"],
)

# 4. Application health: 1 = healthy, 0 = unhealthy
APP_HEALTH = Gauge(
    "app_health",
    "Application health status (1 = healthy, 0 = unhealthy)",
)
APP_HEALTH.set(1)


@app.before_request
def start_request_timer():
    # Exclude Prometheus scrapes from application request metrics.
    if request.path != "/metrics":
        g.request_start_time = time.perf_counter()


@app.after_request
def record_request_metrics(response):
    if request.path != "/metrics":
        endpoint = request.path
        method = request.method
        status = str(response.status_code)

        # Count all HTTP responses.
        HTTP_REQUESTS.labels(
            endpoint=endpoint,
            method=method,
            status=status,
        ).inc()

        # Record request duration.
        start_time = g.get("request_start_time")
        if start_time is not None:
            duration = time.perf_counter() - start_time
            HTTP_REQUEST_DURATION.labels(
                endpoint=endpoint,
                method=method,
            ).observe(duration)

        # Count unsuccessful HTTP responses.
        if response.status_code >= 400:
            HTTP_REQUESTS_FAILED.labels(
                endpoint=endpoint,
                method=method,
                status=status,
            ).inc()

    return response


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    APP_HEALTH.set(1)
    return jsonify(status="healthy"), 200


@app.route("/api/data")
def api_data():
    return jsonify(
        message="SecureMonitor API is running",
        data={"value": random.randint(1, 100)},
    ), 200


@app.route("/api/error")
def api_error():
    return jsonify(error="Simulated application error"), 500


@app.route("/metrics")
def metrics():
    return Response(
        generate_latest(),
        headers={"Content-Type": CONTENT_TYPE_LATEST},
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
