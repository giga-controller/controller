import os

from dotenv import load_dotenv

from app.connectors.client.slack import SlackClient
from app.models.agents.base.template import Agent, AgentResponse
from app.models.agents.base.triage import TriageAgent
from app.models.agents.main import MAIN_TRIAGE_AGENT
from app.models.integrations.slack import (
    SlackGetChannelIdRequest,
    SlackSendMessageRequest,
)
from app.models.query.base import Message, Role

load_dotenv()

SLACK_ACCESS_TOKEN = os.getenv("SLACK_ACCESS_TOKEN")
client = SlackClient(access_token=SLACK_ACCESS_TOKEN)


def main():
    # HARD CODE TEST

    ## AGENT TEST
    chat_history: list[Message] = []
    message = Message(
        role=Role.USER,
        content="I am the new intern and I want to send an introductory message to the channel named startup. You can write the introductory message for me and send it directly",
    ).model_dump()
    chat_history.append(message)
    response = AgentResponse(agent=MAIN_TRIAGE_AGENT, message=message)
    while response.agent:
        prev_agent: Agent = response.agent
        response = response.agent.query(
            chat_history=chat_history,
            access_token=SLACK_ACCESS_TOKEN,
            refresh_token=None,
            client_id=None,
            client_secret=None,
        )
        if isinstance(prev_agent, TriageAgent):
            continue
        chat_history.append(Message(role=Role.ASSISTANT, content=str(response.message)))
        print("CHAT HISTORY", chat_history)
    print("Final chat history", chat_history)


if __name__ == "__main__":
    main()


### HARD CODE TEST
## Get all channel ids
# print(client.get_all_channel_ids(request=SlackGetChannelIdRequest(channel_names=["startup"])))


## Send message
# client.send_message(
#     request=SlackSendMessageRequest(
#         channel_id="C07JXRTPJPM",
#         text="Hey Im Jin Yang"
#     )
# )
