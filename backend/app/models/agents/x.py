import logging
from typing import Optional

import openai

from app.config import OPENAI_GPT4O_MINI
from app.connectors.client.x import XClient
from app.models.agents.base.summary import SUMMARY_AGENT, transfer_to_summary_agent
from app.models.agents.base.template import Agent, AgentResponse
from app.models.agents.base.triage import TriageAgent
from app.models.agents.main import MAIN_TRIAGE_AGENT
from app.models.integrations.base import Integration
from app.models.integrations.x import XSendTweetRequest
from app.models.query.base import Message, Role

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger(__name__)

class XPostRequestAgent(Agent):
    
    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: str,
        client_secret: str,
        enable_verification: bool,
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)

        match function_name:
            case XSendTweetRequest.__name__:
                if enable_verification:
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Please confirm that you want to send a X tweet containing the following fields (Yes/No)",
                            data=[
                                XSendTweetRequest.model_validate(
                                    response.choices[0]
                                    .message.tool_calls[0]
                                    .function.parsed_arguments
                                ).model_dump()
                            ],
                        ),
                        function_to_verify=XSendTweetRequest.__name__,
                    )
                return send_tweet(
                    request=response.choices[0]
                    .message.tool_calls[0]
                    .function.parsed_arguments,
                    access_token=access_token,
                )


def send_tweet(request: XSendTweetRequest, access_token: str) -> AgentResponse:
    client = XClient(access_token=access_token)
    client_response = client.send_tweet(request=request)
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content="X tweet is sent successfully",
            data=[
                client_response.model_dump()
            ],
        ),
        function_to_verify=None,
    )


X_POST_REQUEST_AGENT = XPostRequestAgent(
    name="X Post Request Agent",
    integration_group=Integration.X,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at sending tweets through X. Your task is to help a user send tweets by supplying the correct request to the X API.",
    tools=[
        openai.pydantic_function_tool(XSendTweetRequest)
    ],
)


##############################################


def transfer_to_post_request_agent() -> XPostRequestAgent:
    return X_POST_REQUEST_AGENT


X_TRIAGE_AGENT = TriageAgent(
    name="X Triage Agent",
    integration_group=Integration.X,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at choosing the right agent to perform the task described by the user.""",
    tools=[
        transfer_to_post_request_agent,
        transfer_to_summary_agent,
    ],
)
