from fastapi import APIRouter

from config.settings import settings
from utils.metrics import metrics_registry


router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "environment": settings.app_env}


@router.get("/metrics")
async def metrics() -> dict:
    return metrics_registry.snapshot()
