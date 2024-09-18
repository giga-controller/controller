import os

from dotenv import load_dotenv

from app.connectors.client.gmail import GmailClient
from app.models.agents.base.template import AgentResponse
from app.models.agents.gmail import GMAIL_TRIAGE_AGENT
from app.models.integrations.gmail import (
    GmailFilterEmailsRequest,
    GmailMarkAsReadRequest,
)
from app.models.query.base import Message, Role

load_dotenv()

GMAIL_ACCESS_TOKEN = os.getenv("GMAIL_ACCESS_TOKEN")
GMAIL_REFRESH_TOKEN = os.getenv("GMAIL_REFRESH_TOKEN")
GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")

client = GmailClient(
    access_token=GMAIL_ACCESS_TOKEN,
    refresh_token=GMAIL_REFRESH_TOKEN,
    client_id=GMAIL_CLIENT_ID,
    client_secret=GMAIL_CLIENT_SECRET,
)


def main():
    # HARD CODE TESTcd
    # print(client.mark_as_read(
    #     request=MarkAsReadRequest(
    #         filter_conditions=GmailFilterEmailsRequest(
    #             query='id:191dc984027d9550'
    #         )
    #     )
    # ))
    print(
        client.get_emails(
            request=GmailFilterEmailsRequest(
                query="id:190d75079242e682 OR id:190dc76db933f558"
            )
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
## Send Email
# client.send_email(
#     request=GmailSendEmailRequest(
#         recipient="hugeewhale@gmail.com",
#         subject="Test Email3",
#         body="This is a test email2 from the sandbox."
#     )
# )

## Get Emails
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
