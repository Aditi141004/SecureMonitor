from flask import Flask, jsonify, render_template, request, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import random

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of HTTP requests",
    ["endpoint", "method", "status"]
)


@app.after_request
def record_request(response):
    if request.path != "/metrics":
        REQUEST_COUNT.labels(
            endpoint=request.path,
            method=request.method,
            status=response.status_code
        ).inc()
    return response

def request_endpoint():
    from flask import request
    return request.path

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify(status="healthy"), 200

@app.route("/api/data")
def api_data():
    return jsonify(
        message="SecureMonitor API is running",
        data={"value": random.randint(1, 100)}
    ), 200

@app.route("/api/error")
def api_error():
    return jsonify(error="Simulated application error"), 500

@app.route("/metrics")
def metrics():
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)