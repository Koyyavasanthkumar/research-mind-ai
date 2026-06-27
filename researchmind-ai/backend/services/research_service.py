from __future__ import annotations

import time
from pathlib import Path

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from backend.graph.workflow import research_workflow
from backend.config.settings import settings
from backend.models.database import ResearchProject, User
from backend.models.schemas import ResearchState
from backend.repositories.research_repository import ResearchRepository
from backend.schemas.research import ResearchStartRequest
from backend.utils.cache import TTLCache


RESEARCH_CACHE_VERSION = "depth-v2"
research_state_cache: TTLCache[ResearchState] = TTLCache(ttl_seconds=300)


class ResearchService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ResearchRepository(db)

    def start_research(self, payload: ResearchStartRequest, user: User, background_tasks: BackgroundTasks) -> ResearchProject:
        title = payload.title or payload.query[:120]
        project = self.repository.create_project(user.id, title, payload.query)
        started = time.perf_counter()
        state = ResearchState(
            research_id=str(project.id),
            user_query=payload.query,
            depth=payload.depth,
            citation_style=payload.citation_style,
        )
        cache_key = f"{RESEARCH_CACHE_VERSION}:{payload.query}:{payload.depth}:{payload.citation_style.value}"
        cached_state = research_state_cache.get(cache_key)
        if cached_state:
            final_state = cached_state.model_copy(deep=True, update={"research_id": str(project.id)})
        else:
            final_state = research_workflow.run(state)
            if not final_state.error:
                research_state_cache.set(cache_key, final_state)
        status_value = "failed" if final_state.error else "completed"
        self.repository.update_status(project, status_value)
        self.repository.save_session(project.id, final_state.model_dump(mode="json"), final_state.current_step, status_value)
        report_row = None
        if final_state.report:
            report_row = self.repository.save_report(
                project.id,
                final_state.report.title,
                final_state.summaries.executive_summary if final_state.summaries else final_state.report.title,
                final_state.report.markdown,
                final_state.report.html,
                final_state.report.pdf_path or "",
                [citation.model_dump(mode="json") for citation in final_state.citations],
            )
            for citation in final_state.citations:
                self.repository.save_citation(project.id, report_row.id, citation.style.value, citation.source_url, citation.text)
        elapsed = time.perf_counter() - started
        token_usage = self._estimate_token_usage(final_state)
        self.repository.save_history(project.id, user.id, elapsed, status_value, token_usage)
        self._persist_agent_executions(project.id, final_state)
        self._persist_logs(project.id, user.id, final_state)
        background_tasks.add_task(self._cleanup_temporary_files)
        self.db.refresh(project)
        return project

    def get_project(self, project_id: int, user: User) -> ResearchProject:
        project = self.repository.get_project(project_id, user.id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research project not found")
        return project

    def delete_project(self, project_id: int, user: User) -> None:
        project = self.get_project(project_id, user)
        self.repository.delete_project(project)

    def _persist_agent_executions(self, project_id: int, state: ResearchState) -> None:
        for index, item in enumerate(state.history, start=1):
            execution_time = 0.0
            if item.completed_at:
                execution_time = (item.completed_at - item.started_at).total_seconds()
            self.repository.save_agent_execution(
                project_id,
                item.agent,
                index,
                execution_time,
                item.status,
                item.model_dump(mode="json"),
            )

    def _persist_logs(self, project_id: int, user_id: int, state: ResearchState) -> None:
        for log in state.logs:
            self.repository.save_execution_log(project_id, user_id, log.status.upper(), log.message, log.model_dump(mode="json"))

    def _estimate_token_usage(self, state: ResearchState) -> int:
        serialized = state.model_dump_json()
        return max(1, len(serialized) // 4)

    def _cleanup_temporary_files(self) -> None:
        for path in Path(settings.reports_dir).glob("*.tmp"):
            try:
                path.unlink()
            except OSError:
                continue
