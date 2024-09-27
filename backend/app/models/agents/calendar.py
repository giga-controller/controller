import logging

import openai
from openai import OpenAI

from app.config import OPENAI_GPT4O_MINI
from app.connectors.client.calendar import GoogleCalendarClient
from app.exceptions.exception import InferenceError
from app.models.agents.base.summary import SUMMARY_AGENT, transfer_to_summary_agent
from app.models.agents.base.template import Agent, AgentResponse
from app.models.agents.base.triage import TriageAgent
from app.models.agents.main import MAIN_TRIAGE_AGENT
from app.models.integrations.base import Integration
from app.models.integrations.calendar import (
    CalendarCreateEventRequest,
    CalendarDeleteEventsRequest,
    CalendarEvent,
    CalendarGetEventsRequest,
    CalendarUpdateEventRequest,
)
from app.models.query.base import Message, Role

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger(__name__)
openai_client = OpenAI()


class CalendarCreateEventAgent(Agent):
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
                case CalendarCreateEventRequest.__name__:
                    if enable_verification:
                        return AgentResponse(
                            agent=MAIN_TRIAGE_AGENT,
                            message=Message(
                                role=Role.ASSISTANT,
                                content="Please confirm that you want to create a calendar event containing the following fields (Yes/No)",
                                data=[
                                    CalendarCreateEventRequest.model_validate(
                                        response.choices[0]
                                        .message.tool_calls[0]
                                        .function.parsed_arguments
                                    ).model_dump()
                                ],
                            ),
                            function_to_verify=CalendarCreateEventRequest.__name__,
                        )
                    return await create_calendar_event(
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


async def create_calendar_event(
    request: CalendarCreateEventRequest,
    access_token: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
) -> AgentResponse:
    calendar_client = GoogleCalendarClient(
        access_token=access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
    )
    created_event: CalendarEvent = await calendar_client.create_event(request=request)
    await calendar_client.close()

    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content="Calendar event created successfully",
            data=[created_event.model_dump()],
        ),
    )


CALENDAR_CREATE_EVENT_AGENT = CalendarCreateEventAgent(
    name="Google Calendar Create Event Agent",
    integration_group=Integration.CALENDAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at creating events in Google Calendar. Your task is to help a user create an event by supplying the correct request parameters to the Google Calendar API.",
    tools=[openai.pydantic_function_tool(CalendarCreateEventRequest)],
)


class CalendarGetEventsAgent(Agent):
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
                case CalendarGetEventsRequest.__name__:
                    return await get_calendar_events(
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
            log.error(f"Error in CalendarGetEventsAgent: {e}")
            raise e


async def get_calendar_events(
    request: CalendarGetEventsRequest,
    access_token: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
) -> AgentResponse:
    calendar_client = GoogleCalendarClient(
        access_token=access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
    )
    retrieved_events: list[CalendarEvent] = await calendar_client.get_events(request=request)
    await calendar_client.close()
    
    if not retrieved_events:
        return AgentResponse(
            agent=SUMMARY_AGENT,
            message=Message(
                role=Role.ASSISTANT,
                content="No calendar events were retrieved. Please check the message history and advise the user on what might be the cause of the problem.",
                error=True,
            ),
        )
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content="Here are the retrieved calendar events",
            data=[event.model_dump() for event in retrieved_events],
        ),
    )


CALENDAR_GET_EVENTS_AGENT = CalendarGetEventsAgent(
    name="Google Calendar Get Events Agent",
    integration_group=Integration.CALENDAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at retrieving events from Google Calendar. Your task is to help a user retrieve events by supplying the correct request to the Google Calendar API.",
    tools=[openai.pydantic_function_tool(CalendarGetEventsRequest)],
)


class CalendarUpdateEventAgent(Agent):
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
                case CalendarUpdateEventRequest.__name__:
                    if enable_verification:
                        return AgentResponse(
                            agent=MAIN_TRIAGE_AGENT,
                            message=Message(
                                role=Role.ASSISTANT,
                                content="Please confirm that you want to update a calendar event containing the following fields (Yes/No)",
                                data=[
                                    CalendarUpdateEventRequest.model_validate(
                                        response.choices[0]
                                        .message.tool_calls[0]
                                        .function.parsed_arguments
                                    ).model_dump()
                                ],
                            ),
                            function_to_verify=CalendarUpdateEventRequest.__name__,
                        )
                    return await update_calendar_event(
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
            log.error(f"Error in CalendarUpdateEventAgent: {e}")
            raise e


async def update_calendar_event(
    request: CalendarUpdateEventRequest,
    access_token: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
) -> AgentResponse:
    calendar_client = GoogleCalendarClient(
        access_token=access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
    )
    updated_event: CalendarEvent = await calendar_client.update_event(request=request)
    await calendar_client.close()
    
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content="Calendar event updated successfully",
            data=[updated_event.model_dump()],
        ),
    )


CALENDAR_UPDATE_EVENT_AGENT = CalendarUpdateEventAgent(
    name="Google Calendar Update Event Agent",
    integration_group=Integration.CALENDAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at updating events in Google Calendar. Your task is to help a user update an event by supplying the correct request to the Google Calendar API.",
    tools=[openai.pydantic_function_tool(CalendarUpdateEventRequest)],
)


class CalendarDeleteEventsAgent(Agent):
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
                case CalendarDeleteEventsRequest.__name__:
                    if enable_verification:
                        return AgentResponse(
                            agent=MAIN_TRIAGE_AGENT,
                            message=Message(
                                role=Role.ASSISTANT,
                                content="Please confirm that you want to delete calendar events containing the following fields (Yes/No)",
                                data=[
                                    CalendarDeleteEventsRequest.model_validate(
                                        response.choices[0]
                                        .message.tool_calls[0]
                                        .function.parsed_arguments
                                    ).model_dump()
                                ],
                            ),
                            function_to_verify=CalendarDeleteEventsRequest.__name__,
                        )
                    return await delete_calendar_events(
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
            log.error(f"Error in CalendarDeleteEventsAgent: {e}")
            raise e


async def delete_calendar_events(
    request: CalendarDeleteEventsRequest,
    access_token: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
) -> AgentResponse:
    calendar_client = GoogleCalendarClient(
        access_token=access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
    )
    deleted_events: list[CalendarEvent] = await calendar_client.delete_events(request=request)
    await calendar_client.close()
    return AgentResponse(
        agent=MAIN_TRIAGE_AGENT,
        message=Message(
            role=Role.ASSISTANT,
            content="Calendar event(s) deleted successfully",
            data=[event.model_dump() for event in deleted_events],
        ),
    )


CALENDAR_DELETE_EVENTS_AGENT = CalendarDeleteEventsAgent(
    name="Google Calendar Delete Events Agent",
    integration_group=Integration.CALENDAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at deleting events from Google Calendar. Your task is to help a user delete events by supplying the correct request to the Google Calendar API.",
    tools=[openai.pydantic_function_tool(CalendarDeleteEventsRequest)],
)


def transfer_to_calendar_create_event_agent() -> CalendarCreateEventAgent:
    return CALENDAR_CREATE_EVENT_AGENT


def transfer_to_calendar_get_events_agent() -> CalendarGetEventsAgent:
    return CALENDAR_GET_EVENTS_AGENT


def transfer_to_calendar_update_event_agent() -> CalendarUpdateEventAgent:
    return CALENDAR_UPDATE_EVENT_AGENT


def transfer_to_calendar_delete_events_agent() -> CalendarDeleteEventsAgent:
    return CALENDAR_DELETE_EVENTS_AGENT


CALENDAR_TRIAGE_AGENT = TriageAgent(
    name="Google Calendar Triage Agent",
    integration_group=Integration.CALENDAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at choosing the right agent to perform the task described by the user. Follow these guidelines:

1. To delete a calendar event, you need the event id, which can be obtained by invoking the Google Calendar Get Request Agent.
2. None of the tools in this agent require any arguments.
3. Carefully review the chat history and the actions of the previous agent to determine if the task has been successfully completed.
4. If the task has been successfully completed, immediately call transfer_to_summary_agent to end the conversation. This is crucial—missing this step will result in dire consequences.""",
    tools=[
        transfer_to_calendar_create_event_agent,
        transfer_to_calendar_get_events_agent,
        transfer_to_calendar_update_event_agent,
        transfer_to_calendar_delete_events_agent,
        transfer_to_summary_agent,
    ],
)
