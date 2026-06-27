from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.config.settings import settings
from backend.database.db import init_db
from backend.middleware.auth_context import AuthContextMiddleware
from backend.middleware.errors import register_exception_handlers
from backend.middleware.rate_limiter import RateLimiterMiddleware
from backend.middleware.request_logging import RequestLoggingMiddleware
from backend.middleware.security import CSRFMiddleware, SecurityHeadersMiddleware
from backend.middleware.timeout import RequestTimeoutMiddleware
from backend.services.recovery_service import recover_interrupted_research
from backend.utils.logging import configure_logging


configure_logging()
settings.validate_for_startup()
init_db()
recover_interrupted_research()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Production backend for ResearchMind AI autonomous multi-agent research.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(RequestTimeoutMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(AuthContextMiddleware)
app.add_middleware(RequestLoggingMiddleware)
register_exception_handlers(app)

app.include_router(router, prefix=settings.api_prefix)

@app.on_event("shutdown")
async def shutdown() -> None:
    from backend.database.session import engine

    engine.dispose()
