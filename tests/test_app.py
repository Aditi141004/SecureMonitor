import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

import app


def test_home():
    client = app.app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"SecureMonitor" in response.data


def test_health():
    client = app.app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_api_data():
    client = app.app.test_client()
    response = client.get("/api/data")
    assert response.status_code == 200
    assert response.json["message"] == "SecureMonitor API is running"


def test_api_error():
    client = app.app.test_client()
    response = client.get("/api/error")
    assert response.status_code == 500
    assert response.json["error"] == "Simulated application error"

def test_metrics():
    client = app.app.test_client()
    response = client.get("/metrics")

    assert response.status_code == 200
    assert b"http_requests_total" in response.data
    assert b"http_request_duration_seconds" in response.data
    assert b"http_requests_failed_total" in response.data
    assert b"app_health" in response.data

