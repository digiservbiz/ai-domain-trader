from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_generate_returns_domains():
    with patch("app.api.routes.brainstorm", return_value=["aitools.io", "fastbot.com"]):
        resp = client.get("/generate?niche=tech&keywords=ai,fast")
    assert resp.status_code == 200
    assert resp.json() == {"domains": ["aitools.io", "fastbot.com"]}


def test_generate_empty_results():
    with patch("app.api.routes.brainstorm", return_value=[]):
        resp = client.get("/generate?niche=tech&keywords=x")
    assert resp.status_code == 200
    assert resp.json()["domains"] == []


def test_generate_missing_params():
    resp = client.get("/generate?niche=tech")
    assert resp.status_code == 422


def test_value_endpoint():
    with patch("app.api.routes.value", return_value=1234.5678):
        resp = client.get("/value/example.com")
    assert resp.status_code == 200
    data = resp.json()
    assert data["domain"] == "example.com"
    assert data["estValue"] == 1234.57


def test_value_fallback_no_model():
    with patch("app.api.routes.value", return_value=50.0):
        resp = client.get("/value/unknown.io")
    assert resp.status_code == 200
    assert resp.json()["estValue"] == 50.0
