from fastapi import APIRouter

from backend.api.auth import router as auth_router
from backend.api.memory import router as memory_router
from backend.api.reports import router as reports_router
from backend.api.research import router as research_router
from backend.api.system import router as system_router


router = APIRouter()
router.include_router(auth_router)
router.include_router(research_router)
router.include_router(reports_router)
router.include_router(memory_router)
router.include_router(system_router)
