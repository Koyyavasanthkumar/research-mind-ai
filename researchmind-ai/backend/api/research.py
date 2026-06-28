from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from database.session import get_db
from models.database import ResearchProject, User
from models.schemas import ResearchState
from repositories.research_repository import ResearchRepository
from schemas.common import MessageResponse
from schemas.research import ResearchDetailResponse, ResearchHistoryResponse, ResearchProjectResponse, ResearchStartRequest
from services.auth_service import get_current_user
from services.research_service import ResearchService


router = APIRouter(prefix="/research", tags=["research"])


@router.post("/start", response_model=ResearchProjectResponse, status_code=status.HTTP_201_CREATED)
async def start_research(
    payload: ResearchStartRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchProject:
    service = ResearchService(db)
    return await run_in_threadpool(service.start_research, payload, current_user, background_tasks)


@router.get("/history", response_model=list[ResearchHistoryResponse])
async def research_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ResearchRepository(db).list_history(current_user.id)


@router.get("/{project_id}", response_model=ResearchDetailResponse)
async def get_research(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = ResearchService(db).get_project(project_id, current_user)
    latest_session = project.sessions[-1] if project.sessions else None
    latest_report = project.reports[-1] if project.reports else None
    state = ResearchState.model_validate(latest_session.state_json) if latest_session else None
    report = state.report if state else None
    if latest_report and report is None:
        report = None
    return ResearchDetailResponse(
        id=project.id,
        title=project.title,
        query=project.query,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        state=state,
        report=report,
        report_id=latest_report.id if latest_report else None,
        execution_logs=[row.context for row in project.execution_logs],
        agent_executions=[row.logs for row in project.agent_executions],
    )


@router.delete("/{project_id}", response_model=MessageResponse)
async def delete_research(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MessageResponse:
    ResearchService(db).delete_project(project_id, current_user)
    return MessageResponse(message="Research project deleted")
