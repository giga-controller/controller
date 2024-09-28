import asyncio
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


async def main():
    # HARD CODE TEST
    print(await client.get_all_channel_names())
    ## AGENT TEST



if __name__ == "__main__":
    asyncio.run(main())


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
