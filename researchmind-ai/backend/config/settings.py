from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_name: str = "ResearchMind AI"
    app_env: str = "development"
    api_prefix: str = ""
    gemini_api_key: str = ""
    tavily_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    database_url: str = "sqlite:///./researchmind.db"
    chroma_path: str = "./chroma_store"
    reports_dir: str = "./reports"
    logs_dir: str = "./logs"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    bcrypt_rounds: int = 12
    allowed_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    tavily_max_results: int = 5
    request_timeout_seconds: int = 120
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60
    csrf_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def prepare_filesystem(self) -> None:
        Path(self.reports_dir).mkdir(parents=True, exist_ok=True)
        Path(self.logs_dir).mkdir(parents=True, exist_ok=True)
        Path(self.chroma_path).mkdir(parents=True, exist_ok=True)

    def validate_for_startup(self) -> None:
        errors: list[str] = []
        if self.app_env.lower() == "production":
            if not self.gemini_api_key:
                errors.append("GEMINI_API_KEY is required in production")
            if not self.tavily_api_key:
                errors.append("TAVILY_API_KEY is required in production")
            if self.jwt_secret == "change-me-in-production" or len(self.jwt_secret) < 32:
                errors.append("JWT_SECRET must be at least 32 characters and not the default in production")
            if not self.allowed_origins or "*" in self.allowed_origins:
                errors.append("ALLOWED_ORIGINS must be explicit in production")
        if self.access_token_expire_minutes < 5:
            errors.append("ACCESS_TOKEN_EXPIRE_MINUTES must be at least 5")
        if self.rate_limit_requests < 1:
            errors.append("RATE_LIMIT_REQUESTS must be positive")
        if errors:
            raise RuntimeError("Invalid environment configuration: " + "; ".join(errors))


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.prepare_filesystem()
    return settings


settings = get_settings()
