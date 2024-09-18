from enum import StrEnum

from pydantic import BaseModel


class Integration(StrEnum):
    GMAIL = "gmail"
    CALENDAR = "calendar"
    LINEAR = "linear"
    SLACK = "slack"
    NONE = "none"


class SummaryResponse(BaseModel):
    summary: str
