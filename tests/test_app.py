"""Unit tests for student-ml-api."""

import json

import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["application"] == "student-ml-api"
    assert data["application_version"] == "1.1.0"
    assert data["model_version"] == "model-1"


def test_predict_success(client):
    response = client.post(
        "/predict",
        data=json.dumps({"value": 10}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["input"] == 10
    assert data["prediction"] == 20


def test_predict_missing_input(client):
    response = client.post(
        "/predict",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_predict_invalid_input(client):
    response = client.post(
        "/predict",
        data=json.dumps({"value": "not-a-number"}),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
