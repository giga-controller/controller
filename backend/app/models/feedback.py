from typing import Optional

from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    id: Optional[str] = None
    feedback: str
