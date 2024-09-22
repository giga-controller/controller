from enum import StrEnum

from pydantic import BaseModel


class Integration(StrEnum):
    GMAIL = "gmail"
    CALENDAR = "calendar"
    DOCS = "docs"
    LINEAR = "linear"
    SLACK = "slack"
    X = "x"
    NONE = "none"


class SummaryResponse(BaseModel):
    summary: str
