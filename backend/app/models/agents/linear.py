import logging
from typing import Optional

import openai
from openai import OpenAI

from app.config import OPENAI_GPT4O_MINI
from app.connectors.client.linear import LinearClient
from app.exceptions.exception import InferenceError
from app.models.agents.base.summary import SUMMARY_AGENT, transfer_to_summary_agent
from app.models.agents.base.template import Agent, AgentResponse
from app.models.agents.base.triage import TriageAgent
from app.models.agents.main import MAIN_TRIAGE_AGENT
from app.models.integrations.base import Integration
from app.models.integrations.linear import (
    LinearCreateIssueRequest,
    LinearDeleteIssuesRequest,
    LinearFilterIssuesRequest,
    LinearGetIssuesRequest,
    LinearIssue,
    LinearUpdateIssuesAssigneeRequest,
    LinearUpdateIssuesCycleRequest,
    LinearUpdateIssuesDescriptionRequest,
    LinearUpdateIssuesEstimateRequest,
    LinearUpdateIssuesLabelsRequest,
    LinearUpdateIssuesProjectRequest,
    LinearUpdateIssuesStateRequest,
    LinearUpdateIssuesTitleRequest,
)
from app.models.query.base import Message, Role

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger(__name__)
openai_client = OpenAI()


class LinearPostRequestAgent(Agent):

    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: Optional[str],
        client_secret: Optional[str],
        enable_verification: bool,
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)

        try:
            match function_name:
                case LinearCreateIssueRequest.__name__:
                    if enable_verification:
                        return AgentResponse(
                            agent=MAIN_TRIAGE_AGENT,
                            message=Message(
                                role=Role.ASSISTANT,
                                content="Please confirm that you want to create a Linear issue containing the following fields (Yes/No)",
                                data=[
                                    LinearCreateIssueRequest.model_validate(
                                        response.choices[0]
                                        .message.tool_calls[0]
                                        .function.parsed_arguments
                                    ).model_dump()
                                ],
                            ),
                            function_to_verify=LinearCreateIssueRequest.__name__,
                        )
                    return create_issue(
                        request=response.choices[0]
                        .message.tool_calls[0]
                        .function.parsed_arguments,
                        access_token=access_token,
                    )
                case _:
                    raise InferenceError(f"Function {function_name} not supported")

        except Exception as e:
            log.error(f"Error in LinearPostRequestAgent: {e}")
            raise e


def create_issue(request: LinearCreateIssueRequest, access_token: str) -> AgentResponse:
    linear_client = LinearClient(
        access_token=access_token,
    )
    created_issue: LinearIssue = linear_client.create_issue(request=request)
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content="The following Linear issue has been created successfully",
            data=[created_issue.model_dump()],
        ),
        function_to_verify=None,
    )


LINEAR_POST_REQUEST_AGENT = LinearPostRequestAgent(
    name="Linear Post Request Agent",
    integration_group=Integration.LINEAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at creating issues in Linear via the Linear API. Your task is to help a user create an issue by supplying the correct request parameters to the Linear API.",
    tools=[openai.pydantic_function_tool(LinearCreateIssueRequest)],
)

##############################################


class LinearGetRequestAgent(Agent):

    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: Optional[str],
        client_secret: Optional[str],
        enable_verification: bool = False,
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)

        try:
            match function_name:
                case LinearGetIssuesRequest.__name__:
                    return get_issues(
                        request=response.choices[0]
                        .message.tool_calls[0]
                        .function.parsed_arguments,
                        access_token=access_token,
                    )
                case _:
                    raise InferenceError(f"Function {function_name} not supported")
        except Exception as e:
            log.error(f"Error in LinearGetRequestAgent: {e}")
            raise e


def get_issues(request: LinearGetIssuesRequest, access_token: str) -> AgentResponse:
    linear_client = LinearClient(
        access_token=access_token,
    )
    retrieved_issues: list[LinearIssue] = linear_client.get_issues(request=request)

    if not retrieved_issues:
        return AgentResponse(
            agent=SUMMARY_AGENT,
            message=Message(
                role=Role.ASSISTANT,
                content="No Linear issues were retrieved. Please check the message history to advise the user on what might be the cause of the problem. It could be an issue with spelling or capitalization.",
                error=True,
            ),
        )
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content="The following Linear issues have been successfully retrieved",
            data=[issue.model_dump() for issue in retrieved_issues],
        ),
    )
    


LINEAR_GET_REQUEST_AGENT = LinearGetRequestAgent(
    name="Linear Get Request Agent",
    integration_group=Integration.LINEAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at retrieving information from linear. Your task is to help a user retrieve information by supplying the correct request to the linear API. Follow the rules below:

1. Prioritise using the id as the filter condition where possible.
2. Be careful not to mix up the "number" and "id" of the issue. The "id" is an uuid but the "number" is an integer.
3. Be as restrictive as possible when filtering for the issues to update, which means you should provide as many filter conditions as possible.
4. Set use_and_clause to True if all filter conditions must be met, and False if meeting any single condition is sufficient.""",
    tools=[openai.pydantic_function_tool(LinearGetIssuesRequest)],
)

##############################################


class LinearUpdateRequestAgent(Agent):
    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: Optional[str],
        client_secret: Optional[str],
        enable_verification: bool,
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)

        match function_name:
            case LinearUpdateIssuesStateRequest.__name__:
                if enable_verification:
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Please confirm that you want to update the state of Linear issues containing the following fields (Yes/No)",
                            data=[
                                LinearUpdateIssuesStateRequest.model_validate(
                                    response.choices[0]
                                    .message.tool_calls[0]
                                    .function.parsed_arguments
                                ).model_dump()
                            ],
                        ),
                        function_to_verify=LinearUpdateIssuesStateRequest.__name__,
                    )
            case LinearUpdateIssuesAssigneeRequest.__name__:
                if enable_verification:
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Please confirm that you want to update the assignee of Linear issues containing the following fields (Yes/No)",
                            data=[
                                LinearUpdateIssuesAssigneeRequest.model_validate(
                                    response.choices[0]
                                    .message.tool_calls[0]
                                    .function.parsed_arguments
                                ).model_dump()
                            ],
                        ),
                        function_to_verify=LinearUpdateIssuesAssigneeRequest.__name__,
                    )
            case LinearUpdateIssuesTitleRequest.__name__:
                if enable_verification:
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Please confirm that you want to update the title of Linear issues containing the following fields (Yes/No)",
                            data=[
                                LinearUpdateIssuesTitleRequest.model_validate(
                                    response.choices[0]
                                    .message.tool_calls[0]
                                    .function.parsed_arguments
                                ).model_dump()
                            ],
                        ),
                        function_to_verify=LinearUpdateIssuesTitleRequest.__name__,
                    )
            case LinearUpdateIssuesDescriptionRequest.__name__:
                if enable_verification:
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Please confirm that you want to update the description of Linear issues containing the following fields (Yes/No)",
                            data=[
                                LinearUpdateIssuesDescriptionRequest.model_validate(
                                    response.choices[0]
                                    .message.tool_calls[0]
                                    .function.parsed_arguments
                                ).model_dump()
                            ],
                        ),
                        function_to_verify=LinearUpdateIssuesDescriptionRequest.__name__,
                    )
            case LinearUpdateIssuesLabelsRequest.__name__:
                if enable_verification:
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Please confirm that you want to update the labels of Linear issues containing the following fields (Yes/No)",
                            data=[
                                LinearUpdateIssuesLabelsRequest.model_validate(
                                    response.choices[0]
                                    .message.tool_calls[0]
                                    .function.parsed_arguments
                                ).model_dump()
                            ],
                        ),
                        function_to_verify=LinearUpdateIssuesLabelsRequest.__name__,
                    )
            case LinearUpdateIssuesCycleRequest.__name__:
                if enable_verification:
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Please confirm that you want to update the cycle of Linear issues containing the following fields (Yes/No)",
                            data=[
                                LinearUpdateIssuesCycleRequest.model_validate(
                                    response.choices[0]
                                    .message.tool_calls[0]
                                    .function.parsed_arguments
                                ).model_dump()
                            ],
                        ),
                        function_to_verify=LinearUpdateIssuesCycleRequest.__name__,
                    )
            case LinearUpdateIssuesEstimateRequest.__name__:
                if enable_verification:
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Please confirm that you want to update the estimate of Linear issues containing the following fields (Yes/No)",
                            data=[
                                LinearUpdateIssuesEstimateRequest.model_validate(
                                    response.choices[0]
                                    .message.tool_calls[0]
                                    .function.parsed_arguments
                                ).model_dump()
                            ],
                        ),
                        function_to_verify=LinearUpdateIssuesEstimateRequest.__name__,
                    )
            case LinearUpdateIssuesProjectRequest.__name__:
                if enable_verification:
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Please confirm that you want to update the project of Linear issues containing the following fields (Yes/No)",
                            data=[
                                LinearUpdateIssuesProjectRequest.model_validate(
                                    response.choices[0]
                                    .message.tool_calls[0]
                                    .function.parsed_arguments
                                ).model_dump()
                            ],
                        ),
                        function_to_verify=LinearUpdateIssuesProjectRequest.__name__,
                    )
            case _:
                raise InferenceError(f"Function {function_name} not supported")

        return update_issues(
            request=response.choices[0].message.tool_calls[0].function.parsed_arguments,
            access_token=access_token,
        )


def update_issues(
    request: LinearFilterIssuesRequest, access_token: str
) -> AgentResponse:
    linear_client = LinearClient(
        access_token=access_token,
    )
    updated_issues: list[LinearIssue] = linear_client.update_issues(request=request)

    if not updated_issues:
        return AgentResponse(
            agent=SUMMARY_AGENT,
            message=Message(
                role=Role.ASSISTANT,
                content="No Linear issues were updated. Please check the message history and advise the user on what might be the cause of the problem. It could be an issue with spelling or capitalization.",
                error=True,
            ),
        )
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content=f"The following Linear issues have their state successfully updated",
            data=[issue.model_dump() for issue in updated_issues],
        ),
    )


LINEAR_UPDATE_REQUEST_AGENT = LinearUpdateRequestAgent(
    name="Linear Update Request Agent",
    integration_group=Integration.LINEAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at updating information in linear. Your task is to help a user update information by supplying the correct request to the linear API. Follow the rules below:

1. Prioritise using the id as the filter condition where possible.
2. Be careful not to mix up the "number" and "id" of the issue. The "id" is an uuid but the "number" is an integer.
3. Be as restrictive as possible when filtering for the issues to update, which means you should provide as many filter conditions as possible.     
4. Set use_and_clause to True if all filter conditions must be met, and False if meeting any single condition is sufficient.""",
    tools=[
        openai.pydantic_function_tool(LinearUpdateIssuesStateRequest),
        openai.pydantic_function_tool(LinearUpdateIssuesAssigneeRequest),
        openai.pydantic_function_tool(LinearUpdateIssuesTitleRequest),
        openai.pydantic_function_tool(LinearUpdateIssuesDescriptionRequest),
        openai.pydantic_function_tool(LinearUpdateIssuesLabelsRequest),
        openai.pydantic_function_tool(LinearUpdateIssuesCycleRequest),
        openai.pydantic_function_tool(LinearUpdateIssuesEstimateRequest),
        openai.pydantic_function_tool(LinearUpdateIssuesProjectRequest),
    ],
)

##############################################


class LinearDeleteRequestAgent(Agent):
    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: Optional[str],
        client_secret: Optional[str],
        enable_verification: bool,
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)

        match function_name:
            case LinearDeleteIssuesRequest.__name__:
                if enable_verification:
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Please confirm that you want to delete Linear issues containing the following fields (Yes/No)",
                            data=[
                                LinearDeleteIssuesRequest.model_validate(
                                    response.choices[0]
                                    .message.tool_calls[0]
                                    .function.parsed_arguments
                                ).model_dump()
                            ],
                        ),
                        function_to_verify=LinearDeleteIssuesRequest.__name__,
                    )
                return delete_issues(
                    request=response.choices[0]
                    .message.tool_calls[0]
                    .function.parsed_arguments,
                    access_token=access_token,
                )
            case _:
                raise InferenceError(f"Function {function_name} not supported")


def delete_issues(
    request: LinearDeleteIssuesRequest, access_token: str
) -> AgentResponse:
    linear_client = LinearClient(
        access_token=access_token,
    )
    deleted_issues: list[LinearIssue] = linear_client.delete_issues(request=request)
    if not deleted_issues:
        return AgentResponse(
            agent=SUMMARY_AGENT,
            message=Message(
                role=Role.ASSISTANT,
                content="No Linear issues were deleted. Please check the message history and advise the user on what might be the cause of the problem. It could be an issue with spelling or capitalization.",
                error=True,
            ),
        )
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content="The following Linear issues have been successfully deleted",
            data=[issue.model_dump() for issue in deleted_issues],
        ),
    )


LINEAR_DELETE_REQUEST_AGENT = LinearDeleteRequestAgent(
    name="Linear Delete Request Agent",
    integration_group=Integration.LINEAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at deleting information in linear. Your task is to help a user delete information by supplying the correct request to the linear API. Follow the rules below:

1. Prioritise using the id as the filter condition where possible.
2. Be careful not to mix up the "number" and "id" of the issue. The "id" is an uuid but the "number" is an integer.
3. Be as restrictive as possible when filtering for the issues to update, which means you should provide as many filter conditions as possible.
4. Set use_and_clause to True if all filter conditions must be met, and False if meeting any single condition is sufficient.""",
    tools=[openai.pydantic_function_tool(LinearDeleteIssuesRequest)],
)

##############################################


class LinearRepairRequestAgent(Agent):
    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: Optional[str],
        client_secret: Optional[str],
        enable_verification: bool,
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)
        

LINEAR_REPAIR_REQUEST_AGENT = LinearRepairRequestAgent(
    name="Linear Repair Request Agent",
    integration_group=Integration.LINEAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at repairing the request parameters passed into a Linear API call. Your task is to help a user repair the request parameters by choosing the most likely candidate given what the user has provided.""",
    tools=[] # Wil be populated at runtime
)

    
##############################################


def transfer_to_linear_get_request_agent() -> LinearGetRequestAgent:
    return LINEAR_GET_REQUEST_AGENT


def transfer_to_linear_post_request_agent() -> LinearPostRequestAgent:
    return LINEAR_POST_REQUEST_AGENT


def transfer_to_linear_update_request_agent() -> LinearUpdateRequestAgent:
    return LINEAR_UPDATE_REQUEST_AGENT


def transfer_to_linear_delete_request_agent() -> LinearDeleteRequestAgent:
    return LINEAR_DELETE_REQUEST_AGENT


LINEAR_TRIAGE_AGENT = TriageAgent(
    name="Triage Agent",
    integration_group=Integration.LINEAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at choosing the right agent to perform the task described by the user. Follow these guidelines:
    
1. None of the tools in this agent require any arguments.
2. Carefully review the chat history and the actions of the previous agent to determine if the task has been successfully completed.
3. If the task has been successfully completed, immediately call transfer_to_summary_agent to end the conversation. This is crucial—missing this step will result in dire consequences.""",
    tools=[
        transfer_to_linear_post_request_agent,
        transfer_to_linear_get_request_agent,
        transfer_to_linear_update_request_agent,
        transfer_to_linear_delete_request_agent,
        transfer_to_summary_agent,
    ],
)
