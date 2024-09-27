import logging
from typing import Optional

import openai

from app.config import OPENAI_GPT4O_MINI
from app.connectors.client.gmail import GmailClient
from app.exceptions.exception import InferenceError
from app.models.agents.base.summary import transfer_to_summary_agent
from app.models.agents.base.template import Agent, AgentResponse
from app.models.agents.base.triage import TriageAgent
from app.models.agents.main import MAIN_TRIAGE_AGENT
from app.models.integrations.base import Integration
from app.models.integrations.gmail import (
    Gmail,
    GmailDeleteEmailsRequest,
    GmailGetEmailsRequest,
    GmailMarkAsReadRequest,
    GmailSendEmailRequest,
)
from app.models.query.base import Message, Role

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger(__name__)

##############################################


class GmailGetRequestAgent(Agent):

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
            case GmailGetEmailsRequest.__name__:
                return get_emails(
                    request=response.choices[0]
                    .message.tool_calls[0]
                    .function.parsed_arguments,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    client_id=client_id,
                    client_secret=client_secret,
                )
            case _:
                raise InferenceError(f"Function {function_name} not supported")


def get_emails(
    request: GmailGetEmailsRequest,
    access_token: str,
    refresh_token: Optional[str],
    client_id: str,
    client_secret: str,
) -> AgentResponse:
    client = GmailClient(
        access_token=access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
    )
    email_lst: list[Gmail] = client.get_emails(request=request)
    if not email_lst:
        return AgentResponse(
            agent=MAIN_TRIAGE_AGENT,
            message=Message(
                role=Role.ASSISTANT,
                content="No emails found for the given query",
                error=True,
            ),
            function_to_verify=None,
        )
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content=f"Here are the retrieved emails",
            data=[email.model_dump() for email in email_lst],
        ),
        function_to_verify=None,
    )


GMAIL_GET_REQUEST_AGENT = GmailGetRequestAgent(
    name="Gmail Get Request Agent",
    integration_group=Integration.GMAIL,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at retrieving emails via the Gmail API. Your task is to help a user retrieve a group of emails by supplying the correct query parameters to the gmail API. Follow the rules below:
    
1. Prioritise using the message_id as the filter condition where possible. If the get request concerns multiple emails, populate all the relevant ids in the "message_ids" parameter.""",
    tools=[openai.pydantic_function_tool(GmailGetEmailsRequest)],
)

##############################################


class GmailUpdateRequestAgent(Agent):

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
            case GmailMarkAsReadRequest.__name__:
                if enable_verification:
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Please confirm that you want to mark emails containing the following fields as read (Yes/No)",
                            data=[
                                GmailMarkAsReadRequest.model_validate(
                                    response.choices[0]
                                    .message.tool_calls[0]
                                    .function.parsed_arguments
                                ).model_dump()
                            ],
                        ),
                        function_to_verify=GmailMarkAsReadRequest.__name__,
                    )
                return mark_as_read(
                    request=response.choices[0]
                    .message.tool_calls[0]
                    .function.parsed_arguments,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    client_id=client_id,
                    client_secret=client_secret,
                )
            case _:
                raise InferenceError(f"Function {function_name} not supported")


def mark_as_read(
    request: GmailMarkAsReadRequest,
    access_token: str,
    refresh_token: Optional[str],
    client_id: str,
    client_secret: str,
) -> AgentResponse:
    client = GmailClient(
        access_token=access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
    )
    updated_emails: list[Gmail] = client.mark_as_read(request=request)
    if not updated_emails:
        return AgentResponse(
            agent=MAIN_TRIAGE_AGENT,
            message=Message(
                role=Role.ASSISTANT,
                content="No emails found for the given query",
                error=True,
            ),
            function_to_verify=None,
        )
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content=f"Here are the emails marked as read",
            data=[email.model_dump() for email in updated_emails],
        ),
        function_to_verify=None,
    )


GMAIL_UPDATE_REQUEST_AGENT = GmailUpdateRequestAgent(
    name="Gmail Update Request Agent",
    integration_group=Integration.GMAIL,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at managing emails via the Gmail API. Your task is to help a user update the state of emails by supplying the correct query parameters to the gmail API. Follow the rules below:
    
1. Prioritise using the message_id as the filter condition where possible. If the update request concerns multiple emails, populate all the relevant ids in the "message_ids" parameter.""",
    tools=[openai.pydantic_function_tool(GmailMarkAsReadRequest)],
)

##############################################


class GmailPostRequestAgent(Agent):

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
            case GmailSendEmailRequest.__name__:
                if enable_verification:
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Please confirm that you want to send an email containing the following fields (Yes/No)",
                            data=[
                                GmailSendEmailRequest.model_validate(
                                    response.choices[0]
                                    .message.tool_calls[0]
                                    .function.parsed_arguments
                                ).model_dump()
                            ],
                        ),
                        function_to_verify=GmailSendEmailRequest.__name__,
                    )
                return send_email(
                    request=response.choices[0]
                    .message.tool_calls[0]
                    .function.parsed_arguments,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    client_id=client_id,
                    client_secret=client_secret,
                )

            case _:
                raise InferenceError(f"Function {function_name} not supported")


def send_email(
    request: GmailSendEmailRequest,
    access_token: str,
    refresh_token: Optional[str],
    client_id: str,
    client_secret: str,
) -> AgentResponse:
    client = GmailClient(
        access_token=access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
    )
    sent_email: Gmail = client.send_email(request=request)
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content=f"The following email have been sent successfully",
            data=[sent_email.model_dump()],
        ),
        function_to_verify=None,
    )


GMAIL_POST_REQUEST_AGENT = GmailPostRequestAgent(
    name="Gmail Post Request Agent",
    integration_group=Integration.GMAIL,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at sending emails via the Gmail API. Your task is to help a user send an email by supplying the correct request parameters to the gmail API.",
    tools=[openai.pydantic_function_tool(GmailSendEmailRequest)],
)

##############################################


class GmailDeleteRequestAgent(Agent):

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
            case GmailDeleteEmailsRequest.__name__:
                if enable_verification:
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Please confirm that you want to delete emails containing the following fields (Yes/No)",
                            data=[
                                GmailDeleteEmailsRequest.model_validate(
                                    response.choices[0]
                                    .message.tool_calls[0]
                                    .function.parsed_arguments
                                ).model_dump()
                            ],
                        ),
                        function_to_verify=GmailDeleteEmailsRequest.__name__,
                    )
                return delete_emails(
                    request=response.choices[0]
                    .message.tool_calls[0]
                    .function.parsed_arguments,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    client_id=client_id,
                    client_secret=client_secret,
                )
            case _:
                raise InferenceError(f"Function {function_name} not supported")


def delete_emails(
    request: GmailDeleteEmailsRequest,
    access_token: str,
    refresh_token: Optional[str],
    client_id: str,
    client_secret: str,
) -> AgentResponse:
    client = GmailClient(
        access_token=access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
    )
    deleted_emails: list[Gmail] = client.delete_emails(request=request)
    if not deleted_emails:
        return AgentResponse(
            agent=MAIN_TRIAGE_AGENT,
            message=Message(
                role=Role.ASSISTANT,
                content="No emails found for the given query",
                error=True,
            ),
            function_to_verify=None,
        )
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content=f"The following emails have been successfully deleted",
            data=[email.model_dump() for email in deleted_emails],
        ),
        function_to_verify=None,
    )


GMAIL_DELETE_REQUEST_AGENT = GmailDeleteRequestAgent(
    name="Gmail Delete Request Agent",
    integration_group=Integration.GMAIL,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at deleting emails via the Gmail API. Your task is to help a user delete emails by supplying the correct request parameters to the gmail API. Follow the rules below:
    
1. Prioritise using the message_id as the filter condition where possible. If the delete request concerns multiple emails, populate all the relevant ids in the "message_ids" parameter.""",
    tools=[openai.pydantic_function_tool(GmailDeleteEmailsRequest)],
)

##############################################


def transfer_to_gmail_post_request_agent() -> GmailPostRequestAgent:
    return GMAIL_POST_REQUEST_AGENT


def transfer_to_gmail_get_request_agent() -> GmailGetRequestAgent:
    return GMAIL_GET_REQUEST_AGENT


def transfer_to_gmail_update_request_agent() -> GmailUpdateRequestAgent:
    return GMAIL_UPDATE_REQUEST_AGENT


def transfer_to_gmail_delete_request_agent() -> GmailDeleteRequestAgent:
    return GMAIL_DELETE_REQUEST_AGENT


GMAIL_TRIAGE_AGENT = TriageAgent(
    name="Triage Agent",
    integration_group=Integration.GMAIL,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at choosing the right agent to perform the task described by the user.",
    tools=[
        transfer_to_gmail_post_request_agent,
        transfer_to_gmail_get_request_agent,
        transfer_to_gmail_update_request_agent,
        transfer_to_gmail_delete_request_agent,
        transfer_to_summary_agent,
    ],
)
