import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_empty_response_returns_400(sample_evaluate_body: dict) -> None:
    body = {**sample_evaluate_body, "ai_response": "   "}
    res = client.post("/api/v1/evaluate", json=body)
    assert res.status_code == 400
    assert res.json()["code"] == "EMPTY_RESPONSE"


def test_incomplete_criteria_returns_422(sample_evaluate_body: dict) -> None:
    body = {**sample_evaluate_body, "criteria": ["missing_factors"]}
    res = client.post("/api/v1/evaluate", json=body)
    assert res.status_code == 422


def test_upload_txt_file() -> None:
    res = client.post(
        "/api/v1/uploads",
        files={"file": ("notes.txt", b"Bangalore footfall up 12%", "text/plain")},
    )
    assert res.status_code == 200
    assert res.json()["file_id"]


def test_upload_rejects_invalid_extension() -> None:
    res = client.post(
        "/api/v1/uploads",
        files={"file": ("bad.exe", b"data", "application/octet-stream")},
    )
    assert res.status_code == 400
    assert res.json()["code"] == "INVALID_UPLOAD"


def test_fetch_url_blocks_localhost() -> None:
    res = client.post(
        "/api/v1/context/fetch-url",
        json={"url": "http://127.0.0.1/secret"},
    )
    assert res.status_code == 400
    assert res.json()["code"] == "INVALID_URL"
