from pathlib import Path

from backend.models.database import GeneratedReport, ResearchProject, User
from backend.services.auth_service import AuthService
from backend.tests.conftest import client


def test_report_markdown_pdf_direct_db() -> None:
    from backend.database.session import SessionLocal

    db = SessionLocal()
    try:
        service = AuthService(db)
        user = service.users.get_by_email("report@example.com") or service.users.create(
            "report@example.com", "Report User", service.hash_password("StrongPass123")
        )
        project = ResearchProject(user_id=user.id, title="Report", query="Report query", status="completed")
        db.add(project)
        db.commit()
        db.refresh(project)
        path = Path("test_reports/report.pdf")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"%PDF-1.4\n%test\n")
        report = GeneratedReport(
            project_id=project.id,
            title="Report",
            summary="Summary",
            markdown="# Report",
            html="<h1>Report</h1>",
            pdf_path=str(path),
            citations=[],
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        token = service.create_token({"sub": str(user.id), "type": "access"}, minutes=30)
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {token}"}
    assert client.get(f"/report/{report.id}", headers=headers).status_code == 200
    assert client.get(f"/report/{report.id}/markdown", headers=headers).status_code == 200
    assert client.get(f"/report/{report.id}/pdf", headers=headers).status_code == 200
