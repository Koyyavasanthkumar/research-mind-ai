from backend.tests.conftest import client


def test_register_login_profile() -> None:
    payload = {"email": "researcher@example.com", "full_name": "Researcher One", "password": "StrongPass123"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code in (201, 409)

    login = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert login.status_code == 200
    token = login.json()["access_token"]

    profile = client.get("/auth/profile", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    assert profile.json()["email"] == payload["email"]

