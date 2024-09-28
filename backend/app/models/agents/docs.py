import logging

import openai
from openai import OpenAI

from app.config import OPENAI_GPT4O_MINI
from app.connectors.client.docs import GoogleDocsClient
from app.exceptions.exception import InferenceError
from app.models.agents.base.summary import transfer_to_summary_agent
from app.models.agents.base.template import Agent, AgentResponse
from app.models.agents.base.triage import TriageAgent
from app.models.agents.main import MAIN_TRIAGE_AGENT
from app.models.integrations.base import Integration
from app.models.integrations.docs import (
    Docs,
    DocsCreateRequest,
    DocsGetRequest,
    DocsUpdateRequest,
)
from app.models.query.base import Message, Role

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger(__name__)
openai_client = OpenAI()


class DocsCreateRequestAgent(Agent):
    async def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: str,
        client_id: str,
        client_secret: str,
        enable_verification: bool,
    ) -> AgentResponse:
        response, function_name = await self.get_response(chat_history=chat_history)

        try:
            match function_name:
                case DocsCreateRequest.__name__:
                    if enable_verification:
                        return AgentResponse(
                            agent=MAIN_TRIAGE_AGENT,
                            message=Message(
                                role=Role.ASSISTANT,
                                content="Please confirm that you want to create a Google Doc containing the following fields (Yes/No)",
                                data=[
                                    DocsCreateRequest.model_validate(
                                        response.choices[0]
                                        .message.tool_calls[0]
                                        .function.parsed_arguments
                                    ).model_dump()
                                ],
                            ),
                            function_to_verify=DocsCreateRequest.__name__,
                        )
                    return await create_document(
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
        except Exception as e:
            log.error(f"Error in CalendarCreateEventAgent: {e}")
            raise e


async def create_document(
    request: DocsCreateRequest,
    access_token: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
) -> AgentResponse:
    docs_client = GoogleDocsClient(
        access_token=access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
    )
    created_document: Docs = await docs_client.create_document(request=request)
    await docs_client.close()
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content="Gogole Doc created successfully",
            data=[created_document.model_dump()],
        ),
    )


DOCS_CREATE_REQUEST_AGENT = DocsCreateRequestAgent(
    name="Google Docs Post Request Agent",
    integration_group=Integration.DOCS,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at creating documents in Google Docs. Your task is to help a user create a google doc by supplying the correct request parameters to the Google Docs API.",
    tools=[openai.pydantic_function_tool(DocsCreateRequest)],
)


class DocsGetRequestAgent(Agent):
    async def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: str,
        client_id: str,
        client_secret: str,
        enable_verification: bool,
    ) -> AgentResponse:
        response, function_name = await self.get_response(chat_history=chat_history)

        try:
            match function_name:
                case DocsGetRequest.__name__:
                    return await get_document(
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
        except Exception as e:
            log.error(f"Error in DocsGetRequestAgent: {e}")
            raise e


async def get_document(
    request: DocsGetRequest,
    access_token: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
) -> AgentResponse:
    docs_client = GoogleDocsClient(
        access_token=access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
    )
    retrieved_document: Docs = await docs_client.get_document(request=request)
    await docs_client.close()
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content="Here are the retrieved calendar events",
            data=[retrieved_document.model_dump()],
        ),
    )


DOCS_GET_REQUEST_AGENT = DocsGetRequestAgent(
    name="Google Docs Get Request Agent",
    integration_group=Integration.DOCS,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at retrieving documents from Google Docs. Your task is to help a user retrieve documents by supplying the correct request parameters to the Google Docs API.",
    tools=[openai.pydantic_function_tool(DocsGetRequest)],
)


class DocsUpdateRequestAgent(Agent):
    async def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: str,
        client_id: str,
        client_secret: str,
        enable_verification: bool,
    ) -> AgentResponse:
        response, function_name = await self.get_response(chat_history=chat_history)

        try:
            match function_name:
                case DocsUpdateRequest.__name__:
                    if enable_verification:
                        return AgentResponse(
                            agent=MAIN_TRIAGE_AGENT,
                            message=Message(
                                role=Role.ASSISTANT,
                                content="Please confirm that you want to update a google doc containing the following fields (Yes/No)",
                                data=[
                                    DocsUpdateRequest.model_validate(
                                        response.choices[0]
                                        .message.tool_calls[0]
                                        .function.parsed_arguments
                                    ).model_dump()
                                ],
                            ),
                            function_to_verify=DocsUpdateRequest.__name__,
                        )
                    return await update_document(
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
        except Exception as e:
            log.error(f"Error in DocsUpdateRequestAgent: {e}")
            raise e


async def update_document(
    request: DocsUpdateRequest,
    access_token: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
) -> AgentResponse:
    docs_client = GoogleDocsClient(
        access_token=access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
    )
    updated_document: Docs = await docs_client.update_document(request=request)
    await docs_client.close()
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content="Google Docs updated successfully",
            data=[updated_document.model_dump()],
        ),
    )


DOCS_UPDATE_REQUEST_AGENT = DocsUpdateRequestAgent(
    name="Google Docs Update Request Agent",
    integration_group=Integration.DOCS,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at updating documents in Google Docs. Your task is to help a user update a doc by supplying the correct request parameters to the Google Docs API.",
    tools=[openai.pydantic_function_tool(DocsUpdateRequest)],
)


def transfer_to_docs_create_request_agent() -> DocsCreateRequestAgent:
    return DOCS_CREATE_REQUEST_AGENT


def transfer_to_docs_get_request_agent() -> DocsGetRequestAgent:
    return DOCS_GET_REQUEST_AGENT


def transfer_to_docs_update_request_agent() -> DocsUpdateRequestAgent:
    return DOCS_UPDATE_REQUEST_AGENT


DOCS_TRIAGE_AGENT = TriageAgent(
    name="Google Docs Triage Agent",
    integration_group=Integration.DOCS,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at choosing the right agent to perform the task described by the user. Follow these guidelines:

1. To update a google doc, you need the document id, which can be obtained by invoking the Google Docs Get Request Agent.
2. None of the tools in this agent require any arguments.
3. Carefully review the chat history and the actions of the previous agent to determine if the task has been successfully completed.
4. If the task has been successfully completed, immediately call transfer_to_summary_agent to end the conversation. This is crucial—missing this step will result in dire consequences.""",
    tools=[
        transfer_to_docs_create_request_agent,
        transfer_to_docs_get_request_agent,
        transfer_to_docs_update_request_agent,
        transfer_to_summary_agent,
    ],
)
