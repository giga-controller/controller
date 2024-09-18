from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field


class Timezone(StrEnum):
    UTC = "UTC"
    PST = "America/Los_Angeles"
    EST = "America/New_York"


class CalendarEvent(BaseModel):
    id: str
    summary: str
    description: str
    location: str
    timezone: Timezone
    start_time: str = Field(description="Must be in ISO format")
    end_time: str = Field(description="Must be in ISO format")
    attendees: list[str] = Field(description="List of emails")
    html_link: str


class CalendarCreateEventRequest(BaseModel):
    summary: str
    description: str
    location: str
    timezone: Timezone
    start_time: str = Field(description="Must be in ISO format")
    end_time: str = Field(description="Must be in ISO format")
    attendees: list[str] = Field(description="List of emails")


class CalendarGetEventsRequest(BaseModel):
    time_min: str = Field(description="Must be in ISO format")
    time_max: str = Field(description="Must be in ISO format")
    max_results: int


class CalendarDeleteEventsRequest(BaseModel):
    event_id_lst: list[str] = Field(description="List of event ids to delete")


class CalendarUpdateEventRequest(BaseModel):
    event_id: str = Field(description="Event id to update")
    summary: Optional[str] = Field(description="Updated summary, if any")
    description: Optional[str] = Field(description="Updated description, if any")
    location: Optional[str] = Field(description="Updated location, if any")
    start_time: Optional[str] = Field(
        description="Updated start time in ISO format, if any"
    )
    end_time: Optional[str] = Field(
        description="Updated end time in ISO format, if any"
    )
    attendees: Optional[list[str]] = Field(description="Updated list of emails, if any")
