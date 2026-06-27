from sqlalchemy.orm import Session, joinedload

from backend.models.database import (
    AgentExecution,
    Citation,
    ExecutionLog,
    GeneratedReport,
    Memory,
    ResearchHistory,
    ResearchProject,
    ResearchSession,
)


class ResearchRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_project(self, user_id: int, title: str, query: str) -> ResearchProject:
        project = ResearchProject(user_id=user_id, title=title, query=query, status="running")
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_project(self, project_id: int, user_id: int) -> ResearchProject | None:
        return (
            self.db.query(ResearchProject)
            .options(joinedload(ResearchProject.reports), joinedload(ResearchProject.sessions))
            .filter(ResearchProject.id == project_id, ResearchProject.user_id == user_id)
            .first()
        )

    def list_projects(self, user_id: int) -> list[ResearchProject]:
        return (
            self.db.query(ResearchProject)
            .filter(ResearchProject.user_id == user_id)
            .order_by(ResearchProject.created_at.desc())
            .all()
        )

    def delete_project(self, project: ResearchProject) -> None:
        self.db.delete(project)
        self.db.commit()

    def update_status(self, project: ResearchProject, status: str) -> ResearchProject:
        project.status = status
        self.db.commit()
        self.db.refresh(project)
        return project

    def save_session(self, project_id: int, state_json: dict, current_step: str, status: str) -> ResearchSession:
        session = ResearchSession(project_id=project_id, state_json=state_json, current_step=current_step, status=status)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def save_report(self, project_id: int, title: str, summary: str, markdown: str, html: str, pdf_path: str, citations: list[dict]) -> GeneratedReport:
        report = GeneratedReport(project_id=project_id, title=title, summary=summary, markdown=markdown, html=html, pdf_path=pdf_path, citations=citations)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def save_citation(self, project_id: int, report_id: int, style: str, source_url: str, text: str) -> Citation:
        citation = Citation(project_id=project_id, report_id=report_id, style=style, source_url=source_url, text=text)
        self.db.add(citation)
        self.db.commit()
        self.db.refresh(citation)
        return citation

    def save_history(self, project_id: int, user_id: int, execution_time: float, status: str, token_usage: int) -> ResearchHistory:
        history = ResearchHistory(research_id=project_id, user_id=user_id, execution_time=execution_time, status=status, token_usage=token_usage)
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def list_history(self, user_id: int) -> list[ResearchHistory]:
        return self.db.query(ResearchHistory).filter(ResearchHistory.user_id == user_id).order_by(ResearchHistory.created_at.desc()).all()

    def save_agent_execution(self, project_id: int, agent_name: str, execution_order: int, execution_time: float, status: str, logs: dict) -> AgentExecution:
        execution = AgentExecution(project_id=project_id, agent_name=agent_name, execution_order=execution_order, execution_time=execution_time, status=status, logs=logs)
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def save_execution_log(self, project_id: int | None, user_id: int | None, level: str, message: str, context: dict) -> ExecutionLog:
        row = ExecutionLog(project_id=project_id, user_id=user_id, level=level, message=message, context=context)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def get_report(self, report_id: int, user_id: int) -> GeneratedReport | None:
        return (
            self.db.query(GeneratedReport)
            .join(ResearchProject)
            .filter(GeneratedReport.id == report_id, ResearchProject.user_id == user_id)
            .first()
        )

    def save_memory(self, user_id: int, content: str, project_id: int | None, metadata: dict) -> Memory:
        row = Memory(user_id=user_id, project_id=project_id, content=content, metadata_json=metadata)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def clear_memory(self, user_id: int) -> int:
        deleted = self.db.query(Memory).filter(Memory.user_id == user_id).delete()
        self.db.commit()
        return deleted

    def recover_interrupted_projects(self) -> int:
        rows = self.db.query(ResearchProject).filter(ResearchProject.status == "running").all()
        for row in rows:
            row.status = "interrupted"
        self.db.commit()
        return len(rows)
