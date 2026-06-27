from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.memory.vector_store import research_memory
from backend.models.database import User
from backend.repositories.research_repository import ResearchRepository
from backend.schemas.memory import MemoryStoreRequest


class MemoryService:
    def __init__(self, db: Session) -> None:
        self.repository = ResearchRepository(db)

    def store(self, payload: MemoryStoreRequest, user: User) -> None:
        self.repository.save_memory(user.id, payload.content, payload.project_id, payload.metadata)
        research_memory.store_text(user.id, payload.content, payload.metadata)

    def search(self, query: str, user: User, limit: int = 5) -> list[str]:
        if not query.strip():
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Query is required")
        return research_memory.search_user(user.id, query, limit=limit)

    def clear(self, user: User) -> int:
        research_memory.clear_user(user.id)
        return self.repository.clear_memory(user.id)
