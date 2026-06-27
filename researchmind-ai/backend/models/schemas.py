from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class CitationStyle(str, Enum):
    APA = "APA"
    IEEE = "IEEE"
    MLA = "MLA"


class ResearchStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500)
    depth: int = Field(2, ge=1, le=4)
    citation_style: CitationStyle = CitationStyle.APA


class ReportRequest(BaseModel):
    research_id: str
    citation_style: CitationStyle = CitationStyle.APA


class ResearchTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    query: str
    rationale: str
    priority: int = Field(ge=1, le=10, default=5)


class ResearchPlan(BaseModel):
    objective: str
    intent: str
    strategy: str
    tasks: list[ResearchTask] = Field(default_factory=list)


class SearchResult(BaseModel):
    sub_topic: str
    title: str
    url: str
    content: str
    author: str | None = None
    published_date: str | None = None
    domain: str


class RankedSource(SearchResult):
    trust_score: float = Field(0, ge=0, le=100)
    domain_authority: float = Field(0, ge=0, le=100)
    freshness_score: float = Field(0, ge=0, le=100)
    academic_score: float = Field(0, ge=0, le=100)
    government_score: float = Field(0, ge=0, le=100)
    industry_score: float = Field(0, ge=0, le=100)
    evaluation_reason: str = ""


class ExtractedInformation(BaseModel):
    sub_topic: str
    source_url: str
    facts: list[str] = Field(default_factory=list)
    statistics: list[str] = Field(default_factory=list)
    important_statements: list[str] = Field(default_factory=list)
    definitions: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    tables: list[dict[str, Any]] = Field(default_factory=list)


class VerifiedClaim(BaseModel):
    claim: str
    sub_topic: str
    source_urls: list[str] = Field(default_factory=list)
    status: Literal["Verified", "Unverified", "Needs More Research"]
    confidence: float = Field(0.5, ge=0, le=1)
    evidence: str


class VerifiedInformation(BaseModel):
    verified: list[VerifiedClaim] = Field(default_factory=list)
    unverified: list[VerifiedClaim] = Field(default_factory=list)
    needs_more_research: list[VerifiedClaim] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)


class SummaryBundle(BaseModel):
    executive_summary: str
    detailed_summary: str
    bullet_summary: list[str] = Field(default_factory=list)
    key_takeaways: list[str] = Field(default_factory=list)


class Citation(BaseModel):
    style: CitationStyle
    source_url: str
    text: str


class Report(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    research_id: str
    title: str
    table_of_contents: list[str] = Field(default_factory=list)
    sections: dict[str, str] = Field(default_factory=dict)
    conclusion: str
    references: list[Citation] = Field(default_factory=list)
    source_cards: list[RankedSource] = Field(default_factory=list)
    markdown: str
    html: str
    pdf_path: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentLog(BaseModel):
    agent: str
    status: str
    message: str
    attempt: int = 1
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ExecutionHistoryItem(BaseModel):
    step: str
    agent: str
    started_at: datetime
    completed_at: datetime | None = None
    status: str = "running"
    attempts: int = 1
    error: str | None = None


class ResearchState(BaseModel):
    research_id: str = Field(default_factory=lambda: str(uuid4()))
    user_query: str
    research_plan: ResearchPlan | None = None
    sub_topics: list[str] = Field(default_factory=list)
    search_results: list[SearchResult] = Field(default_factory=list)
    ranked_sources: list[RankedSource] = Field(default_factory=list)
    extracted_information: list[ExtractedInformation] = Field(default_factory=list)
    verified_information: VerifiedInformation = Field(default_factory=VerifiedInformation)
    missing_topics: list[ResearchTask] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    report: Report | None = None
    history: list[ExecutionHistoryItem] = Field(default_factory=list)
    current_step: str = "START"
    logs: list[AgentLog] = Field(default_factory=list)
    summaries: SummaryBundle | None = None
    citation_style: CitationStyle = CitationStyle.APA
    depth: int = Field(2, ge=1, le=4)
    loop_count: int = 0
    max_loops: int = 2
    error: str | None = None

    def as_graph_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="python")


class ResearchResponse(BaseModel):
    id: str
    status: ResearchStatus
    topic: str
    report: Report | None = None
    events: list[AgentLog] = Field(default_factory=list)


class HistoryItem(BaseModel):
    id: str
    topic: str
    status: ResearchStatus
    created_at: datetime
    updated_at: datetime
    report_id: str | None = None
