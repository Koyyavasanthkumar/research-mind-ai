from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from api.routes import router

from config.settings import settings

from database.db import init_db

from middleware.auth_context import AuthContextMiddleware
from middleware.errors import register_exception_handlers
from middleware.rate_limiter import RateLimiterMiddleware
from middleware.request_logging import RequestLoggingMiddleware
from middleware.security import (
    CSRFMiddleware,
    SecurityHeadersMiddleware
)
from middleware.timeout import RequestTimeoutMiddleware

from services.recovery_service import recover_interrupted_research

from utils.logging import configure_logging



configure_logging()


settings.validate_for_startup()


init_db()


recover_interrupted_research()



app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Production backend for ResearchMind AI autonomous multi-agent research."
)



# CORS FIX

app.add_middleware(
    CORSMiddleware,

    allow_origins=settings.allowed_origins,

    allow_credentials=True,

    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS"
    ],

    allow_headers=["*"],
)



app.add_middleware(
    RateLimiterMiddleware
)


app.add_middleware(
    RequestTimeoutMiddleware
)


app.add_middleware(
    SecurityHeadersMiddleware
)


app.add_middleware(
    CSRFMiddleware
)


app.add_middleware(
    AuthContextMiddleware
)


app.add_middleware(
    RequestLoggingMiddleware
)



register_exception_handlers(app)



app.include_router(
    router,
    prefix=settings.api_prefix
)



@app.get("/")
async def root():

    return {
        "status": "running",
        "service": "ResearchMind AI"
    }



@app.on_event("shutdown")
async def shutdown():

    from database.session import engine

    engine.dispose()