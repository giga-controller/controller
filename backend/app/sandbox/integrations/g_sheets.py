import os

from dotenv import load_dotenv

load_dotenv()

SHEETS_ACCESS_TOKEN = os.getenv("SHEETS_ACCESS_TOKEN")
SHEETS_REFRESH_TOKEN = os.getenv("SHEETS_REFRESH_TOKEN")
SHEETS_CLIENT_ID = os.getenv("SHEETS_CLIENT_ID")
SHEETS_CLIENT_SECRET = os.getenv("SHEETS_CLIENT_SECRET")


def main():
    from app.connectors.client.sheets import GoogleSheetsClient
    from app.models.integrations.sheets import SheetsGetRequest

    client = GoogleSheetsClient(
        access_token=SHEETS_ACCESS_TOKEN,
        refresh_token=SHEETS_REFRESH_TOKEN,
        client_id=SHEETS_CLIENT_ID,
        client_secret=SHEETS_CLIENT_SECRET,
    )

    # HARD CODE TEST

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
## Read Sheets
# print(
#     client.read_sheet(
#         request=SheetsGetRequest(
#             spreadsheet_id="1YVgOzMDESAGBaAjXlvB941HDzyrFvNqzcHOnwEifzoY",
#             sheet_name="Controllers",
#         )
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
