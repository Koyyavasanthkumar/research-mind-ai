from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from backend.models.schemas import CitationStyle, Report, ResearchState
from backend.utils.sanitization import sanitize_text


class ResearchStartRequest(BaseModel):
    title: str | None = Field(None, max_length=500)
    query: str = Field(..., min_length=3, max_length=2000)
    depth: int = Field(2, ge=1, le=4)
    citation_style: CitationStyle = CitationStyle.APA

    @field_validator("title", "query")
    @classmethod
    def sanitize_research_text(cls, value: str | None) -> str | None:
        return sanitize_text(value) if value is not None else value


class ResearchProjectResponse(BaseModel):
    id: int
    title: str
    query: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResearchDetailResponse(ResearchProjectResponse):
    state: ResearchState | None = None
    report: Report | None = None
    report_id: int | None = None
    execution_logs: list[dict[str, Any]] = Field(default_factory=list)
    agent_executions: list[dict[str, Any]] = Field(default_factory=list)


class ResearchHistoryResponse(BaseModel):
    id: int
    research_id: int
    execution_time: float
    status: str
    token_usage: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportResponse(BaseModel):
    id: int
    project_id: int
    title: str
    summary: str
    markdown: str
    html: str
    pdf_path: str
    citations: list[dict[str, Any]]
    created_at: datetime

    model_config = {"from_attributes": True}
