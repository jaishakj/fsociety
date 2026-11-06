from fastapi.testclient import TestClient

from app.main import app


def test_login_limits_requests_by_client_ip(monkeypatch) -> None:
    monkeypatch.setattr("app.modules.auth.router.authenticate", lambda *_args: None)
    client = TestClient(app)
    payload = {"email": "nobody@example.com", "password": "wrong-password"}

    for _ in range(5):
        assert client.post("/api/v1/auth/login", json=payload).status_code == 401

    limited = client.post("/api/v1/auth/login", json=payload)
    assert limited.status_code == 429
    assert limited.json() == {"detail": "Rate limit exceeded. Protocol cooldown active."}


def test_registration_limits_requests_by_client_ip(monkeypatch) -> None:
    monkeypatch.setattr("app.modules.auth.router.get_user_by_email", lambda *_args: object())
    client = TestClient(app)
    payload = {
        "email": "already-used@example.com",
        "password": "some-long-password",
        "display_name": "Test",
    }

    for _ in range(3):
        assert client.post("/api/v1/auth/register", json=payload).status_code == 400

    limited = client.post("/api/v1/auth/register", json=payload)
    assert limited.status_code == 429
    assert limited.json() == {"detail": "Rate limit exceeded. Protocol cooldown active."}
