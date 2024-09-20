import asyncio
import logging
from typing import Optional

from app.connectors.native.stores.token import Token
from app.exceptions.exception import DatabaseError, PipelineError
from app.models.agents.base.template import Agent, AgentResponse
from app.models.agents.base.triage import TriageAgent
from app.models.agents.gmail import delete_emails, mark_as_read, send_email
from app.models.agents.linear import create_issue, delete_issues, update_issues
from app.models.agents.main import MAIN_TRIAGE_AGENT
from app.models.agents.slack import send_message
from app.models.integrations.base import Integration
from app.models.integrations.gmail import (
    GmailDeleteEmailsRequest,
    GmailMarkAsReadRequest,
    GmailSendEmailRequest,
)
from app.models.integrations.linear import (
    LinearCreateIssueRequest,
    LinearDeleteIssuesRequest,
    LinearUpdateIssuesAssigneeRequest,
    LinearUpdateIssuesCycleRequest,
    LinearUpdateIssuesDescriptionRequest,
    LinearUpdateIssuesEstimateRequest,
    LinearUpdateIssuesLabelsRequest,
    LinearUpdateIssuesProjectRequest,
    LinearUpdateIssuesStateRequest,
    LinearUpdateIssuesTitleRequest,
)
from app.models.integrations.slack import SlackSendMessageRequest
from app.models.query.base import Message, QueryResponse, Role
from app.services.message import MessageService
from app.services.token import TokenService
from app.services.user import UserService

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class QueryService:

    async def query(
        self,
        message: Message,
        chat_history: list[Message],
        api_key: str,
        integrations: list[Integration],
        instance: Optional[str],
        enable_verification: bool,
    ) -> QueryResponse:
        tokens: dict[str, Token] = await _construct_tokens_map(
            integrations=integrations, api_key=api_key
        )

        chat_history.append(message)

        response: QueryResponse = await _infer(
            tokens=tokens,
            message=message,
            chat_history=chat_history,
            api_key=api_key,
            integrations=integrations,
            instance=instance,
            enable_verification=enable_verification,
        )

        return response

    async def confirm(
        self,
        chat_history: list[Message],
        api_key: str,
        enable_verification: bool,
        integrations: list[Integration],
        function_to_verify: str,
        instance: Optional[str],
    ) -> QueryResponse:
        tokens: dict[str, Token] = await _construct_tokens_map(
            integrations=integrations, api_key=api_key
        )
        client_argument = chat_history[-1].data[0]
        match function_to_verify:
            case GmailMarkAsReadRequest.__name__:
                client_response = mark_as_read(
                    request=GmailMarkAsReadRequest.model_validate(client_argument),
                    access_token=tokens[Integration.GMAIL].access_token,
                    refresh_token=tokens[Integration.GMAIL].refresh_token,
                    client_id=tokens[Integration.GMAIL].client_id,
                    client_secret=tokens[Integration.GMAIL].client_secret,
                )
            case GmailSendEmailRequest.__name__:
                client_response = send_email(
                    request=GmailSendEmailRequest.model_validate(client_argument),
                    access_token=tokens[Integration.GMAIL].access_token,
                    refresh_token=tokens[Integration.GMAIL].refresh_token,
                    client_id=tokens[Integration.GMAIL].client_id,
                    client_secret=tokens[Integration.GMAIL].client_secret,
                )
            case GmailDeleteEmailsRequest.__name__:
                client_response = delete_emails(
                    request=GmailDeleteEmailsRequest.model_validate(client_argument),
                    access_token=tokens[Integration.GMAIL].access_token,
                    refresh_token=tokens[Integration.GMAIL].refresh_token,
                    client_id=tokens[Integration.GMAIL].client_id,
                    client_secret=tokens[Integration.GMAIL].client_secret,
                )
            case LinearCreateIssueRequest.__name__:
                client_response = create_issue(
                    request=LinearCreateIssueRequest.model_validate(client_argument),
                    access_token=tokens[Integration.LINEAR].access_token,
                )
            case LinearUpdateIssuesStateRequest.__name__:
                client_response = update_issues(
                    request=LinearUpdateIssuesStateRequest.model_validate(
                        client_argument
                    ),
                    access_token=tokens[Integration.LINEAR].access_token,
                )
            case LinearUpdateIssuesAssigneeRequest.__name__:
                client_response = update_issues(
                    request=LinearUpdateIssuesAssigneeRequest.model_validate(
                        client_argument
                    ),
                    access_token=tokens[Integration.LINEAR].access_token,
                )
            case LinearUpdateIssuesTitleRequest.__name__:
                client_response = update_issues(
                    request=LinearUpdateIssuesTitleRequest.model_validate(
                        client_argument
                    ),
                    access_token=tokens[Integration.LINEAR].access_token,
                )
            case LinearUpdateIssuesDescriptionRequest.__name__:
                client_response = update_issues(
                    request=LinearUpdateIssuesDescriptionRequest.model_validate(
                        client_argument
                    ),
                    access_token=tokens[Integration.LINEAR].access_token,
                )
            case LinearUpdateIssuesLabelsRequest.__name__:
                client_response = update_issues(
                    request=LinearUpdateIssuesLabelsRequest.model_validate(
                        client_argument
                    ),
                    access_token=tokens[Integration.LINEAR].access_token,
                )
            case LinearUpdateIssuesCycleRequest.__name__:
                client_response = update_issues(
                    request=LinearUpdateIssuesCycleRequest.model_validate(
                        client_argument
                    ),
                    access_token=tokens[Integration.LINEAR].access_token,
                )
            case LinearUpdateIssuesEstimateRequest.__name__:
                client_response = update_issues(
                    request=LinearUpdateIssuesEstimateRequest.model_validate(
                        client_argument
                    ),
                    access_token=tokens[Integration.LINEAR].access_token,
                )
            case LinearUpdateIssuesProjectRequest.__name__:
                client_response = update_issues(
                    request=LinearUpdateIssuesProjectRequest.model_validate(
                        client_argument
                    ),
                    access_token=tokens[Integration.LINEAR].access_token,
                )
            case LinearDeleteIssuesRequest.__name__:
                client_response = delete_issues(
                    request=LinearDeleteIssuesRequest.model_validate(client_argument),
                    access_token=tokens[Integration.LINEAR].access_token,
                )
            case SlackSendMessageRequest.__name__:
                client_response = send_message(
                    request=SlackSendMessageRequest.model_validate(client_argument),
                    access_token=tokens[Integration.SLACK].access_token,
                )
            case _:
                raise PipelineError(
                    f"Function {function_to_verify} not supported in the confirmation process"
                )
        chat_history.pop()  # Delete the confirmation request from the chat history
        chat_history.append(client_response.message)

        agent_message = Message(
            role=Role.ASSISTANT,
            content=f"{client_response.message.content}: {str(client_response.message.data)}",
            data=None,
        )

        response: QueryResponse = await _infer(
            tokens=tokens,
            message=agent_message,
            chat_history=chat_history,
            api_key=api_key,
            integrations=integrations,
            instance=instance,
            enable_verification=enable_verification,
        )
        return response


async def _infer(
    tokens: dict[str, Token],
    message: Message,
    chat_history: list[Message],
    api_key: str,
    integrations: list[Integration],
    instance: Optional[str],
    enable_verification: bool,
) -> QueryResponse:
    """This function is responsible for managing the main inference loop"""

    agent_chat_history: list[Message] = _construct_agent_chat_history(
        chat_history=chat_history
    )
    response = AgentResponse(
        agent=MAIN_TRIAGE_AGENT, message=message, verification_needed=False
    )
    while response.agent:
        prev_agent: Agent = response.agent
        integration_group: Integration = response.agent.integration_group
        if integration_group == Integration.NONE:
            response = response.agent.query(
                chat_history=agent_chat_history,
                access_token="",
                refresh_token="",
                client_id="",
                client_secret="",
                enable_verification=False,
            )
        else:
            response = response.agent.query(
                chat_history=agent_chat_history,
                access_token=tokens[integration_group].access_token,
                refresh_token=tokens[integration_group].refresh_token,
                client_id=tokens[integration_group].client_id,
                client_secret=tokens[integration_group].client_secret,
                enable_verification=enable_verification,
            )
        if isinstance(prev_agent, TriageAgent):
            continue
        chat_history, agent_chat_history = _append_chat_history(
            response=response,
            chat_history=chat_history,
            agent_chat_history=agent_chat_history,
        )
        if not response.function_to_verify:
            continue
        return QueryResponse(
            chat_history=[msg for msg in chat_history if not msg.error],
            instance=instance,
            function_to_verify=response.function_to_verify,
        )

    results = await asyncio.gather(
        UserService().increment_usage(api_key=api_key),
        MessageService().post(
            chat_history=chat_history,
            api_key=api_key,
            integrations=integrations,
            instance=instance,
        ),
    )

    return QueryResponse(
        chat_history=[msg for msg in chat_history if not msg.error],
        instance=results[1],
        function_to_verify=None,
    )


async def _construct_tokens_map(
    integrations: Integration, api_key: str
) -> dict[str, Token]:
    """Returns a map where the key is the integration name and value is a Token object containing all the necessary credentials of the user"""
    tokens: dict[str, Token] = {}
    for integration in integrations:
        token: Optional[Token] = await TokenService().get(
            api_key=api_key, table_name=integration
        )
        if not token:
            raise DatabaseError(
                f"User has not authenticated with the {integration} table. Please authenticate before trying again."
            )
        tokens[integration] = token
    return tokens


def _construct_agent_chat_history(chat_history: list[Message]) -> list[Message]:
    """Modifies the chat history such that the information in the data attribute is appended behind the content attribute. The observation is that LLMs are performing significantly worse when the data is not appended immediately behind the message content. However, we want to preserve the data attribute for ease of content display in frontend and consumption via REST endpoints in the future"""
    agent_chat_history: list[Message] = []
    for msg in chat_history:
        agent_chat_history.append(
            Message(
                role=Role.ASSISTANT,
                content=f"{msg.content}: {str(msg.data)}",
                data=None,
            )
        )
    return agent_chat_history


def _append_chat_history(
    response: AgentResponse,
    chat_history: list[Message],
    agent_chat_history: list[Message],
) -> tuple[list[Message], list[Message]]:
    chat_history.append(
        Message(
            role=Role.ASSISTANT,
            content=response.message.content,
            data=response.message.data,
            error=response.message.error,
        )
    )
    agent_chat_history.append(
        Message(
            role=Role.ASSISTANT,
            content=f"{response.message.content}: {str(response.message.data)}",
            data=None,
            error=response.message.error,
        )
    )
    return chat_history, agent_chat_history


# async def query_linear(
#     self, chat_history: list[Message], api_key: str
# ) -> list[BaseModel]:
#     TABLE_NAME = "linear"
#     token: Optional[Token] = await TokenService().get(
#         api_key=api_key, table_name=TABLE_NAME
#     )
#     if not token:
#         raise DatabaseError(
#             f"User has not authenticated with the {TABLE_NAME} table. Please authenticate before trying again."
#         )

#     curr_agent: Agent = LINEAR_TRIAGE_AGENT.query(
#         chat_history=chat_history,
#         access_token=token.access_token,
#         refresh_token=token.refresh_token,
#     )
#     response: list[BaseModel] = curr_agent.query(
#         chat_history=chat_history,
#         access_token=token.access_token,
#         refresh_token=token.refresh_token,
#     )
#     return response

# async def query_gmail(
#     self, chat_history: list[Message], api_key: str
# ) -> list[BaseModel]:
#     TABLE_NAME = "gmail"
#     token: Optional[Token] = await TokenService().get(
#         api_key=api_key, table_name=TABLE_NAME
#     )
#     if not token:
#         raise DatabaseError(
#             f"User has not authenticated with the {TABLE_NAME} table. Please authenticate before trying again."
#         )

#     curr_agent: Agent = GMAIL_TRIAGE_AGENT.query(
#         messages=chat_history,
#         access_token=token.access_token,
#         refresh_token=token.refresh_token,
#         client_id=token.client_id,
#         client_secret=token.client_secret,
#     )
#     response: list[BaseModel] = curr_agent.query(
#         chat_history=chat_history,
#         access_token=token.access_token,
#         refresh_token=token.refresh_token,
#         client_id=token.client_id,
#         client_secret=token.client_secret,
#     )
#     return response
