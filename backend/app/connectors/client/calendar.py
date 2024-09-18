from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.exceptions.exception import InferenceError
from app.models.integrations.calendar import (
    CalendarCreateEventRequest,
    CalendarDeleteEventsRequest,
    CalendarEvent,
    CalendarGetEventsRequest,
    CalendarUpdateEventRequest,
    Timezone,
)

TOKEN_URI = "https://oauth2.googleapis.com/token"


class CalendarClient:

    def __init__(
        self, access_token: str, refresh_token: str, client_id: str, client_secret: str
    ):
        self.service = build(
            "calendar",
            "v3",
            credentials=Credentials(
                token=access_token,
                refresh_token=refresh_token,
                client_id=client_id,
                client_secret=client_secret,
                token_uri=TOKEN_URI,
            ),
        )

    def create_event(self, request: CalendarCreateEventRequest) -> CalendarEvent:
        try:
            event = {
                "summary": request.summary,
                "location": request.location,
                "description": request.description,
                "start": {
                    "dateTime": request.start_time,
                    "timeZone": Timezone.EST,
                },
                "end": {
                    "dateTime": request.end_time,
                    "timeZone": Timezone.EST,
                },
                "attendees": [{"email": attendee} for attendee in request.attendees],
            }

            created_event = (
                self.service.events().insert(calendarId="primary", body=event).execute()
            )
            return CalendarEvent(
                id=created_event["id"],
                summary=request.summary,
                description=request.description,
                location=request.location,
                timezone=request.timezone,
                start_time=request.start_time,
                end_time=request.end_time,
                attendees=request.attendees,
                html_link=created_event.get("htmlLink"),
            )
        except Exception as e:
            raise InferenceError(f"Error creating event via CalendarClient: {str(e)}")

    def get_events(self, request: CalendarGetEventsRequest) -> list[CalendarEvent]:
        try:
            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=request.time_min,
                    timeMax=request.time_max,
                    maxResults=request.max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])

            calendar_list: list[CalendarEvent] = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))
                calendar_list.append(
                    CalendarEvent(
                        id=event["id"],
                        summary=event["summary"],
                        description=event.get("description", ""),
                        location=event.get("location", ""),
                        timezone=event.get("timeZone", Timezone.UTC),
                        start_time=start,
                        end_time=end,
                        attendees=[
                            attendee["email"] for attendee in event.get("attendees", [])
                        ],
                        html_link=event.get("htmlLink"),
                    )
                )
            return calendar_list
        except Exception as e:
            raise InferenceError(f"Error getting events via CalendarClient: {str(e)}")

    def delete_events(self, request: CalendarDeleteEventsRequest) -> None:
        try:
            for event_id in request.event_id_lst:
                self.service.events().delete(
                    calendarId="primary", eventId=event_id
                ).execute()
        except Exception as e:
            raise InferenceError(f"Error deleting event via CalendarClient: {str(e)}")

    def update_event(self, request: CalendarUpdateEventRequest) -> CalendarEvent:
        try:
            event = (
                self.service.events()
                .get(calendarId="primary", eventId=request.event_id)
                .execute()
            )

            if request.summary:
                event["summary"] = request.summary
            if request.description:
                event["description"] = request.description
            if request.location:
                event["location"] = request.location
            if request.start_time:
                event["start"]["dateTime"] = request.start_time.isoformat()
            if request.end_time:
                event["end"]["dateTime"] = request.end_time.isoformat()
            if request.attendees:
                event["attendees"] = [
                    {"email": attendee} for attendee in request.attendees
                ]

            updated_event = (
                self.service.events()
                .update(calendarId="primary", eventId=request.event_id, body=event)
                .execute()
            )

            return CalendarEvent(
                id=updated_event["id"],
                summary=updated_event["summary"],
                description=updated_event.get("description", ""),
                location=updated_event.get("location", ""),
                timezone=updated_event.get("timeZone", Timezone.UTC),
                start_time=updated_event["start"].get(
                    "dateTime", updated_event["start"].get("date")
                ),
                end_time=updated_event["end"].get(
                    "dateTime", updated_event["end"].get("date")
                ),
                attendees=[
                    attendee["email"] for attendee in updated_event.get("attendees", [])
                ],
                html_link=updated_event.get("htmlLink"),
            )
        except Exception as e:
            raise InferenceError(f"Error updating event via CalendarClient: {str(e)}")
