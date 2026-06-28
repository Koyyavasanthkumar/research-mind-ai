"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-27
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("users", sa.Column("email", sa.String(length=255), nullable=False), sa.Column("full_name", sa.String(length=255), nullable=False), sa.Column("hashed_password", sa.String(length=255), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("id", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_table("research_projects", sa.Column("title", sa.String(length=500), nullable=False), sa.Column("query", sa.Text(), nullable=False), sa.Column("status", sa.String(length=50), nullable=False), sa.Column("user_id", sa.Integer(), nullable=False), sa.Column("id", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_research_projects_id"), "research_projects", ["id"], unique=False)
    op.create_index(op.f("ix_research_projects_user_id"), "research_projects", ["user_id"], unique=False)
    op.create_table("agent_executions", sa.Column("project_id", sa.Integer(), nullable=False), sa.Column("agent_name", sa.String(length=100), nullable=False), sa.Column("execution_order", sa.Integer(), nullable=False), sa.Column("execution_time", sa.Float(), nullable=False), sa.Column("status", sa.String(length=50), nullable=False), sa.Column("logs", sa.JSON(), nullable=False), sa.Column("id", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(["project_id"], ["research_projects.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_agent_executions_id"), "agent_executions", ["id"], unique=False)
    op.create_index(op.f("ix_agent_executions_project_id"), "agent_executions", ["project_id"], unique=False)
    op.create_table("execution_logs", sa.Column("project_id", sa.Integer(), nullable=True), sa.Column("user_id", sa.Integer(), nullable=True), sa.Column("level", sa.String(length=20), nullable=False), sa.Column("message", sa.Text(), nullable=False), sa.Column("context", sa.JSON(), nullable=False), sa.Column("id", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(["project_id"], ["research_projects.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_execution_logs_id"), "execution_logs", ["id"], unique=False)
    op.create_index(op.f("ix_execution_logs_project_id"), "execution_logs", ["project_id"], unique=False)
    op.create_index(op.f("ix_execution_logs_user_id"), "execution_logs", ["user_id"], unique=False)
    op.create_table("generated_reports", sa.Column("project_id", sa.Integer(), nullable=False), sa.Column("title", sa.String(length=500), nullable=False), sa.Column("summary", sa.Text(), nullable=False), sa.Column("markdown", sa.Text(), nullable=False), sa.Column("html", sa.Text(), nullable=False), sa.Column("pdf_path", sa.Text(), nullable=False), sa.Column("citations", sa.JSON(), nullable=False), sa.Column("id", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(["project_id"], ["research_projects.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_generated_reports_id"), "generated_reports", ["id"], unique=False)
    op.create_index(op.f("ix_generated_reports_project_id"), "generated_reports", ["project_id"], unique=False)
    op.create_table("memory", sa.Column("user_id", sa.Integer(), nullable=False), sa.Column("project_id", sa.Integer(), nullable=True), sa.Column("content", sa.Text(), nullable=False), sa.Column("metadata_json", sa.JSON(), nullable=False), sa.Column("id", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(["project_id"], ["research_projects.id"], ondelete="SET NULL"), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_memory_id"), "memory", ["id"], unique=False)
    op.create_index(op.f("ix_memory_project_id"), "memory", ["project_id"], unique=False)
    op.create_index(op.f("ix_memory_user_id"), "memory", ["user_id"], unique=False)
    op.create_table("research_history", sa.Column("research_id", sa.Integer(), nullable=False), sa.Column("user_id", sa.Integer(), nullable=False), sa.Column("execution_time", sa.Float(), nullable=False), sa.Column("status", sa.String(length=50), nullable=False), sa.Column("token_usage", sa.Integer(), nullable=False), sa.Column("id", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(["research_id"], ["research_projects.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_research_history_id"), "research_history", ["id"], unique=False)
    op.create_index(op.f("ix_research_history_research_id"), "research_history", ["research_id"], unique=False)
    op.create_index(op.f("ix_research_history_user_id"), "research_history", ["user_id"], unique=False)
    op.create_table("research_sessions", sa.Column("project_id", sa.Integer(), nullable=False), sa.Column("state_json", sa.JSON(), nullable=False), sa.Column("current_step", sa.String(length=100), nullable=False), sa.Column("status", sa.String(length=50), nullable=False), sa.Column("id", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(["project_id"], ["research_projects.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_research_sessions_id"), "research_sessions", ["id"], unique=False)
    op.create_index(op.f("ix_research_sessions_project_id"), "research_sessions", ["project_id"], unique=False)
    op.create_table("citations", sa.Column("project_id", sa.Integer(), nullable=False), sa.Column("report_id", sa.Integer(), nullable=True), sa.Column("style", sa.String(length=20), nullable=False), sa.Column("source_url", sa.Text(), nullable=False), sa.Column("text", sa.Text(), nullable=False), sa.Column("id", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(["project_id"], ["research_projects.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["report_id"], ["generated_reports.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_citations_id"), "citations", ["id"], unique=False)
    op.create_index(op.f("ix_citations_project_id"), "citations", ["project_id"], unique=False)
    op.create_index(op.f("ix_citations_report_id"), "citations", ["report_id"], unique=False)


def downgrade() -> None:
    for table in ("citations", "research_sessions", "research_history", "memory", "generated_reports", "execution_logs", "agent_executions", "research_projects", "users"):
        op.drop_table(table)
