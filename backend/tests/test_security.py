from fastapi.testclient import TestClient

from app.main import create_app


def test_security_headers_are_present():
    response = TestClient(create_app()).get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]


def test_oversized_request_is_rejected(monkeypatch):
    monkeypatch.setenv("MAX_REQUEST_BODY_BYTES", "16")
    from app.core.config import get_settings
    get_settings.cache_clear()
    try:
        response = TestClient(create_app()).post(
            "/api/v1/auth/login",
            json={"username": "investigator", "password": "too-long-for-this-test"},
        )
        assert response.status_code == 413
        assert response.json()["code"] == "request_too_large"
    finally:
        get_settings.cache_clear()
