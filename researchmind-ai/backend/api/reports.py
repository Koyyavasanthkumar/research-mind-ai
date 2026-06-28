from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session

from database.session import get_db
from models.database import GeneratedReport, User
from schemas.research import ReportResponse
from services.auth_service import get_current_user
from services.report_service import ReportService


router = APIRouter(prefix="/report", tags=["reports"])


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> GeneratedReport:
    return ReportService(db).get_report(report_id, current_user)


@router.get("/{report_id}/pdf")
async def get_report_pdf(report_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> FileResponse:
    path = ReportService(db).get_pdf_path(report_id, current_user)
    return FileResponse(path, media_type="application/pdf", filename=path.name)


@router.get("/{report_id}/markdown")
async def get_report_markdown(report_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PlainTextResponse:
    report = ReportService(db).get_report(report_id, current_user)
    return PlainTextResponse(report.markdown, media_type="text/markdown")
