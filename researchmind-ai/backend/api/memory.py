from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database.session import get_db
from models.database import User
from schemas.common import MessageResponse
from schemas.memory import MemorySearchResponse, MemoryStoreRequest
from services.auth_service import get_current_user
from services.memory_service import MemoryService


router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("/store", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def store_memory(payload: MemoryStoreRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MessageResponse:
    MemoryService(db).store(payload, current_user)
    return MessageResponse(message="Memory stored")


@router.get("/search", response_model=MemorySearchResponse)
async def search_memory(
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemorySearchResponse:
    return MemorySearchResponse(results=MemoryService(db).search(q, current_user, limit))


@router.delete("/clear", response_model=MessageResponse)
async def clear_memory(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MessageResponse:
    deleted = MemoryService(db).clear(current_user)
    return MessageResponse(message=f"Cleared {deleted} memory records")
