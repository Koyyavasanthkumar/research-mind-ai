from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base


class BaseModelMixin(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(BaseModelMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    projects: Mapped[list["ResearchProject"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class ResearchProject(BaseModelMixin):
    __tablename__ = "research_projects"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    user: Mapped[User] = relationship(back_populates="projects")
    sessions: Mapped[list["ResearchSession"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    histories: Mapped[list["ResearchHistory"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    reports: Mapped[list["GeneratedReport"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    agent_executions: Mapped[list["AgentExecution"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    execution_logs: Mapped[list["ExecutionLog"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class ResearchSession(BaseModelMixin):
    __tablename__ = "research_sessions"

    project_id: Mapped[int] = mapped_column(ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    state_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    current_step: Mapped[str] = mapped_column(String(100), default="START", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="running", nullable=False)

    project: Mapped[ResearchProject] = relationship(back_populates="sessions")


class ResearchHistory(BaseModelMixin):
    __tablename__ = "research_history"

    research_id: Mapped[int] = mapped_column(ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_time: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    token_usage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    project: Mapped[ResearchProject] = relationship(back_populates="histories")


class Citation(BaseModelMixin):
    __tablename__ = "citations"

    project_id: Mapped[int] = mapped_column(ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    report_id: Mapped[int | None] = mapped_column(ForeignKey("generated_reports.id", ondelete="CASCADE"), nullable=True, index=True)
    style: Mapped[str] = mapped_column(String(20), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    report: Mapped["GeneratedReport"] = relationship(back_populates="citation_rows")


class GeneratedReport(BaseModelMixin):
    __tablename__ = "generated_reports"

    project_id: Mapped[int] = mapped_column(ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    markdown: Mapped[str] = mapped_column(Text, nullable=False)
    html: Mapped[str] = mapped_column(Text, nullable=False)
    pdf_path: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    project: Mapped[ResearchProject] = relationship(back_populates="reports")
    citation_rows: Mapped[list[Citation]] = relationship(back_populates="report", cascade="all, delete-orphan")


class ExecutionLog(BaseModelMixin):
    __tablename__ = "execution_logs"

    project_id: Mapped[int | None] = mapped_column(ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    level: Mapped[str] = mapped_column(String(20), default="INFO", nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    project: Mapped[ResearchProject | None] = relationship(back_populates="execution_logs")


class AgentExecution(BaseModelMixin):
    __tablename__ = "agent_executions"

    project_id: Mapped[int] = mapped_column(ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    execution_order: Mapped[int] = mapped_column(Integer, nullable=False)
    execution_time: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    logs: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    project: Mapped[ResearchProject] = relationship(back_populates="agent_executions")


class Memory(BaseModelMixin):
    __tablename__ = "memory"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("research_projects.id", ondelete="SET NULL"), nullable=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
