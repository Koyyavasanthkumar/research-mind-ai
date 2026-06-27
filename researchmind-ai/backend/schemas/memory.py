from typing import Any

from pydantic import BaseModel, Field, field_validator

from backend.utils.sanitization import sanitize_text


class MemoryStoreRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    project_id: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, value: str) -> str:
        return sanitize_text(value)


class MemorySearchResponse(BaseModel):
    results: list[str]
