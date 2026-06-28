from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from database.session import SessionLocal
from repositories.research_repository import ResearchRepository
from utils.metrics import metrics_registry

logger = logging.getLogger("researchmind.requests")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        started = time.perf_counter()
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            status_code = getattr(response, "status_code", 500)
            metrics_registry.record_request(request.url.path, status_code, elapsed_ms)
            message = f"{request.method} {request.url.path} completed with {status_code} in {elapsed_ms}ms"
            logger.info(message)
            db = SessionLocal()
            try:
                try:
                    ResearchRepository(db).save_execution_log(
                        project_id=None,
                        user_id=getattr(request.state, "user_id", None),
                        level="INFO",
                        message=message,
                        context={
                            "method": request.method,
                            "path": request.url.path,
                            "status_code": status_code,
                            "elapsed_ms": elapsed_ms,
                        },
                    )
                except Exception:
                    logger.exception("Failed to store request log in database")
            finally:
                db.close()
