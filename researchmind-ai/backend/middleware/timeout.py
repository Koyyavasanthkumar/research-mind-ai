from __future__ import annotations

import anyio
from fastapi import HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from config.settings import settings


class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        with anyio.move_on_after(settings.request_timeout_seconds) as scope:
            response = await call_next(request)
        if scope.cancel_called:
            raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Request timed out")
        return response
