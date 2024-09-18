import os

from dotenv import load_dotenv

load_dotenv()

CALENDAR_ACCESS_TOKEN = os.getenv("CALENDAR_ACCESS_TOKEN")
CALENDAR_REFRESH_TOKEN = os.getenv("CALENDAR_REFRESH_TOKEN")
CALENDAR_CLIENT_ID = os.getenv("CALENDAR_CLIENT_ID")
CALENDAR_CLIENT_SECRET = os.getenv("CALENDAR_CLIENT_SECRET")


def main():
    from app.connectors.client.calendar import CalendarClient
    from app.models.integrations.calendar import (
        CalendarCreateEventRequest,
        CalendarDeleteEventsRequest,
        CalendarGetEventsRequest,
        CalendarUpdateEventRequest,
        Timezone,
    )

    client = CalendarClient(
        access_token=CALENDAR_ACCESS_TOKEN,
        refresh_token=CALENDAR_REFRESH_TOKEN,
        client_id=CALENDAR_CLIENT_ID,
        client_secret=CALENDAR_CLIENT_SECRET,
    )

    # HARD CODE TEST
    print(
        client.get_events(
            request=CalendarGetEventsRequest(
                time_min="2024-09-01T09:00:00Z",
                time_max="2024-09-15T09:00:00Z",
                max_results=10,
            )
        )
    )

    client.update_event(
        request=CalendarUpdateEventRequest(
            event_id="4hn8ukbpdebk0tsmp4u5a8rocj",
            summary="Updated Summary",
            description="Updated Description",
            location=None,
            start_time=None,
            end_time=None,
            attendees=["chenjinyang4192@gmail.com"],
        )
    )

    ## AGENT TEST
    # chat_history: list[Message] = []
    # message = Message(
    #     role=Role.USER,
    #     content="I want get all emails from hugeewhale@gmail.com that are unread. There should be one in particular that asks for my address. I live at 91 Yishun Ave 1, S(769135) so please send a reply to that email containing the information",
    # ).model_dump()
    # chat_history.append(message)
    # response = AgentResponse(agent=GMAIL_TRIAGE_AGENT, message=message)
    # while response.agent:
    #     response = response.agent.query(
    #         chat_history=chat_history,
    #         access_token=GMAIL_ACCESS_TOKEN,
    #         refresh_token=GMAIL_REFRESH_TOKEN,
    #         client_id=GMAIL_CLIENT_ID,
    #         client_secret=GMAIL_CLIENT_SECRET,
    #     )
    #     chat_history.append(Message(role=Role.ASSISTANT, content=str(response.message)))
    # print(chat_history)


if __name__ == "__main__":
    main()

### HARD CODE TEST
## Create Calendar Event
# print(
#     client.create_event(
#         request=CalendarCreateEventRequest(
#             summary="Test Event",
#             description="This is a test event from the sandbox.",
#             location="Singapore",
#             timezone=Timezone.UTC,
#             start_time="2024-09-01T09:00:00Z",
#             end_time="2024-09-01T21:00:00Z",
#             attendees=["chenjinyang4192@gmail.com"]
#         )
#     )
# )

## Delete Calendar Events
# client.delete_events(
#     request=CalendarDeleteEventsRequest(
#         event_id_lst=["3ts6hp3qrjckdh7mhj0u4dgr21", "73mb5lbc33878tc8kbl8bg26mf"]
#     )
# )

## Get Calendar Event
# print(client.get_events(
#     request=CalendarGetEventsRequest(
#         time_min="2024-09-01T09:00:00Z",
#         time_max="2024-09-15T09:00:00Z",
#         max_results=10
#     )
# ))

## Get Calendar Events
# response = client.get_emails(
#     request=GmailGetEmailsRequest(
#         query="from:apply@ycombinator.com is:unread"
#     )
# )

### AGENT TEST
## Send Email
# messages = [
#     Message(role="user", content="I want to send an email to hugeewhale@gmail.com with the subject. For the content body, crack a funny joke that an aspiring entrepreneur would relate with. You can come up with an appropriate subject title").model_dump()
# ]
# agent = GMAIL_TRIAGE_AGENT.query(
#     messages=messages,
#     access_token=GMAIL_ACCESS_TOKEN,
#     refresh_token=GMAIL_REFRESH_TOKEN,
#     client_id=GMAIL_CLIENT_ID,
#     client_secret=GMAIL_CLIENT_SECRET
# )
# agent.query(
#     messages=messages,
#     access_token=GMAIL_ACCESS_TOKEN,
#     refresh_token=GMAIL_REFRESH_TOKEN,
#     client_id=GMAIL_CLIENT_ID,
#     client_secret=GMAIL_CLIENT_SECRET
# )

## Get Emails
# messages = [
#     Message(role="user", content="I want get all emails from apply@ycombinator.com that are unread").model_dump()
# ]
# agent = GMAIL_TRIAGE_AGENT.query(
#     messages=messages,
#     access_token=GMAIL_ACCESS_TOKEN,
#     refresh_token=GMAIL_REFRESH_TOKEN,
#     client_id=GMAIL_CLIENT_ID,
#     client_secret=GMAIL_CLIENT_SECRET
# )
# response = agent.query(
#     messages=messages,
#     access_token=GMAIL_ACCESS_TOKEN,
#     refresh_token=GMAIL_REFRESH_TOKEN,
#     client_id=GMAIL_CLIENT_ID,
#     client_secret=GMAIL_CLIENT_SECRET
# )
# print(response)
