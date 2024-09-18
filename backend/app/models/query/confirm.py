from typing import Optional

from pydantic import BaseModel

from app.models.integrations.base import Integration
from app.models.query.base import Message


class ConfirmRequest(BaseModel):
    chat_history: list[Message]
    api_key: str
    enable_verification: bool
    integrations: list[Integration]
    function_to_verify: str
    instance: Optional[str] = None
