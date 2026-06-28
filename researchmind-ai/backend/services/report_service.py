from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models.database import GeneratedReport, User
from backend.repositories.research_repository import ResearchRepository
from backend.utils.cache import TTLCache


report_cache: TTLCache[GeneratedReport] = TTLCache(ttl_seconds=120)


class ReportService:
    def __init__(self, db: Session) -> None:
        self.repository = ResearchRepository(db)

    def get_report(self, report_id: int, user: User) -> GeneratedReport:
        cache_key = f"{user.id}:{report_id}"
        cached = report_cache.get(cache_key)
        if cached:
            return cached
        report = self.repository.get_report(report_id, user.id)
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        report_cache.set(cache_key, report)
        return report

    def get_pdf_path(self, report_id: int, user: User) -> Path:
        report = self.get_report(report_id, user)
        path = Path(report.pdf_path)
        if not path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF file not found")
        return path
