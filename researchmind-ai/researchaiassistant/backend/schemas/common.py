from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    code: str = "error"


class MessageResponse(BaseModel):
    message: str

