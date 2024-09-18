from enum import StrEnum
from typing import Optional

from pydantic import BaseModel

from app.models.integrations.base import Integration


class Role(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    role: Role
    content: str
    data: Optional[list[dict]] = None
    error: Optional[bool] = False


class QueryRequest(BaseModel):
    message: Message
    chat_history: list[Message]
    api_key: str
    enable_verification: bool
    integrations: list[Integration]
    instance: Optional[str] = None


class QueryResponse(BaseModel):
    chat_history: list[Message]
    instance: Optional[str]
    function_to_verify: Optional[str]
