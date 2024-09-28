import logging
from typing import Any, Optional

import openai

from app.config import OPENAI_GPT4O_MINI
from app.connectors.client.slack import SlackClient
from app.models.agents.base.summary import SUMMARY_AGENT, transfer_to_summary_agent
from app.models.agents.base.template import Agent, AgentResponse
from app.models.agents.base.triage import TriageAgent
from app.models.agents.main import MAIN_TRIAGE_AGENT
from app.models.integrations.base import Integration
from app.models.integrations.slack import (
    SlackGetChannelIdRequest,
    SlackSendMessageRequest,
)
from app.models.query.base import Message, Role

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger(__name__)


class SlackPostRequestAgent(Agent):

    async def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: str,
        client_secret: str,
        enable_verification: bool,
    ) -> AgentResponse:
        response, function_name = await self.get_response(chat_history=chat_history)

        match function_name:
            case SlackSendMessageRequest.__name__:
                if enable_verification:
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Please confirm that you want to send a slack message containing the following fields (Yes/No)",
                            data=[
                                SlackSendMessageRequest.model_validate(
                                    response.choices[0]
                                    .message.tool_calls[0]
                                    .function.parsed_arguments
                                ).model_dump()
                            ],
                        ),
                        function_to_verify=SlackSendMessageRequest.__name__,
                    )
                return send_message(
                    request=response.choices[0]
                    .message.tool_calls[0]
                    .function.parsed_arguments,
                    access_token=access_token,
                )


def send_message(request: SlackSendMessageRequest, access_token: str) -> AgentResponse:
    client = SlackClient(access_token=access_token)
    client_response = client.send_message(request=request)
    if not client_response["ok"]:
        return AgentResponse(
            agent=SUMMARY_AGENT,
            message=Message(
                role=Role.ASSISTANT,
                content=f"Failed to send slack message. Please check the message history and advise the user on what might be the cause of the problem.\nError: {client_response['error']}",
                error=True,
            ),
            function_to_verify=None,
        )
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content="Slack message is sent successfully",
            data=[
                {
                    "channel_id": client_response["channel"],
                    "message": client_response["message"]["text"],
                }
            ],
        ),
        function_to_verify=None,
    )


SLACK_POST_REQUEST_AGENT = SlackPostRequestAgent(
    name="Slack Post Request Agent",
    integration_group=Integration.SLACK,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at sending information to slack. Your task is to help a user send information by supplying the correct request to the slack API.",
    tools=[openai.pydantic_function_tool(SlackSendMessageRequest)],
)

##############################################


class SlackGetRequestAgent(Agent):

    async def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: str,
        client_secret: str,
        enable_verification: bool = False,
    ) -> AgentResponse:
        response, function_name = await self.get_response(chat_history=chat_history)

        match function_name:
            case SlackGetChannelIdRequest.__name__:
                return get_all_channel_ids(
                    request=response.choices[0]
                    .message.tool_calls[0]
                    .function.parsed_arguments,
                    access_token=access_token,
                )


def get_all_channel_ids(
    request: SlackGetChannelIdRequest, access_token: str
) -> AgentResponse:
    client = SlackClient(access_token=access_token)
    client_response: list[dict[str, Any]] = client.get_all_channel_ids(request=request)
    if not client_response:
        return AgentResponse(
            agent=SUMMARY_AGENT,
            message=Message(
                role=Role.ASSISTANT,
                content="No channel IDs were retrieved. Please check the message history to advise the user on what might be the cause of the problem. It could be an issue with spelling or capitalization.",
                error=True,
            ),
        )
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content="Here are the channel ids of the requested channel names",
            data=client_response,
        ),
    )


SLACK_GET_REQUEST_AGENT = SlackGetRequestAgent(
    name="Slack Get Request Agent",
    integration_group=Integration.SLACK,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at retrieving information from slack. Your task is to help a user retrieve information by supplying the correct request to the slack API.",
    tools=[openai.pydantic_function_tool(SlackGetChannelIdRequest)],
)

##############################################


def transfer_to_get_request_agent() -> SlackGetRequestAgent:
    return SLACK_GET_REQUEST_AGENT


def transfer_to_post_request_agent() -> SlackPostRequestAgent:
    return SLACK_POST_REQUEST_AGENT


SLACK_TRIAGE_AGENT = TriageAgent(
    name="Slack Triage Agent",
    integration_group=Integration.SLACK,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at choosing the right agent to perform the task described by the user. Take note of the following:

1. Always look at the chat history to see if the information you need to proceed with the next stage of the task is available. If it is already available, do not request for it again.
2. To send a message, you need to pass SlackPostRequestAgent the channel_id "CXXXXXXXXXX". If the channel_id is not provided by the user or available in the chat history, you can retrieve the channel_id by transferring the task to the SlackGetRequestAgent.
3. Do not pass any parameters into your tools.
""",
    tools=[
        transfer_to_post_request_agent,
        transfer_to_get_request_agent,
        transfer_to_summary_agent,
    ],
)
