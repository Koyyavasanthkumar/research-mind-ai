from backend.tests.conftest import client


def test_auth_memory_e2e() -> None:
    user = {"email": "e2e@example.com", "full_name": "E2E User", "password": "StrongPass123"}
    client.post("/auth/register", json=user)
    login = client.post("/auth/login", json={"email": user["email"], "password": user["password"]})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    profile = client.get("/auth/profile", headers=headers)
    assert profile.status_code == 200

    stored = client.post("/memory/store", json={"content": "End to end memory record"}, headers=headers)
    assert stored.status_code == 201

    searched = client.get("/memory/search?q=memory", headers=headers)
    assert searched.status_code == 200
