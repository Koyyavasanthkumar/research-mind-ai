from pathlib import Path

from backend.models.schemas import Citation, CitationStyle, Report, ResearchState, SummaryBundle
from backend.tests.conftest import client


def auth_headers() -> dict[str, str]:
    payload = {"email": "research@example.com", "full_name": "Research User", "password": "StrongPass123"}
    client.post("/auth/register", json=payload)
    token = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_research_start_history_detail(monkeypatch) -> None:
    def fake_run(state: ResearchState) -> ResearchState:
        path = Path("test_reports/fake.pdf")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"%PDF-1.4\n%test\n")
        state.summaries = SummaryBundle(
            executive_summary="Executive summary",
            detailed_summary="Detailed summary",
            bullet_summary=["Bullet"],
            key_takeaways=["Takeaway"],
        )
        state.citations = [Citation(style=CitationStyle.APA, source_url="https://example.org", text="Example citation")]
        state.report = Report(
            research_id=state.research_id,
            title="Research Report: Test",
            table_of_contents=["1. Executive Summary"],
            sections={"1. Executive Summary": "Executive summary"},
            conclusion="Conclusion",
            references=state.citations,
            markdown="# Test",
            html="<h1>Test</h1>",
            pdf_path=str(path),
        )
        state.current_step = "Report"
        return state

    monkeypatch.setattr("backend.services.research_service.research_workflow.run", fake_run)
    headers = auth_headers()
    started = client.post("/research/start", json={"query": "Test topic", "depth": 1}, headers=headers)
    assert started.status_code == 201
    project_id = started.json()["id"]

    history = client.get("/research/history", headers=headers)
    assert history.status_code == 200
    assert len(history.json()) >= 1

    detail = client.get(f"/research/{project_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["status"] == "completed"

