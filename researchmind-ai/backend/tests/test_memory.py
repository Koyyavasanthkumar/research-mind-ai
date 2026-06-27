from backend.tests.conftest import client


def auth_headers() -> dict[str, str]:
    payload = {"email": "memory@example.com", "full_name": "Memory User", "password": "StrongPass123"}
    client.post("/auth/register", json=payload)
    token = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_memory_store_search_clear() -> None:
    headers = auth_headers()
    stored = client.post("/memory/store", json={"content": "Agentic research systems coordinate specialized AI agents."}, headers=headers)
    assert stored.status_code == 201
    searched = client.get("/memory/search?q=agentic", headers=headers)
    assert searched.status_code == 200
    cleared = client.delete("/memory/clear", headers=headers)
    assert cleared.status_code == 200

