from backend.tests.conftest import client


def test_health_metrics_and_security_headers() -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.headers["X-Content-Type-Options"] == "nosniff"

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "request_count" in metrics.json()


def test_profile_uses_demo_user_without_token() -> None:
    response = client.get("/auth/profile")
    assert response.status_code == 200
    assert response.json()["email"] == "demo@researchmind.example.com"
