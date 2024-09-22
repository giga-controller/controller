import os

from dotenv import load_dotenv

load_dotenv()

DOCS_ACCESS_TOKEN = os.getenv("DOCS_ACCESS_TOKEN")
DOCS_REFRESH_TOKEN = os.getenv("DOCS_REFRESH_TOKEN")
DOCS_CLIENT_ID = os.getenv("DOCS_CLIENT_ID")
DOCS_CLIENT_SECRET = os.getenv("DOCS_CLIENT_SECRET")


def main():
    from app.connectors.client.docs import GoogleDocsClient
    from app.models.integrations.docs import (
        DocsCreateRequest,
        DocsDeleteRequest,
        DocsGetRequest,
        DocsUpdateRequest,
    )

    client = GoogleDocsClient(
        access_token=DOCS_ACCESS_TOKEN,
        refresh_token=DOCS_REFRESH_TOKEN,
        client_id=DOCS_CLIENT_ID,
        client_secret=DOCS_CLIENT_SECRET,
    )

    # HARD CODE TEST
    # print(
    #     client.create_document(
    #         request=DocsCreateRequest(
    #             title="AI aaron",
    #             content="Test content"
    #         )
    #     )
    # )
    # print(
    #     client.get_document(
    #         request=DocsGetRequest(
    #             id=""
    #         )
    #     )
    # )
    # print(
    #     client.update_document(
    #         request=DocsUpdateRequest(
    #             id="",
    #             updated_content="AI aaorn talks to users"
    #         )
    #     )
    # )
    print(
        client.delete_document(
            request=DocsDeleteRequest(id="1jCmgYTASurMu1QfMzpINnHTKWOcMA1nCCZmvUYrJl-M")
        )
    )


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
