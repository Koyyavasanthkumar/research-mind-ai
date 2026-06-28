from __future__ import annotations

from models.schemas import AgentLog, ResearchState


class BaseAgent:
    name = "Base Agent"

    def event(self, state: ResearchState, message: str, status: str = "completed", attempt: int = 1) -> None:
        state.logs.append(AgentLog(agent=self.name, status=status, message=message, attempt=attempt))
