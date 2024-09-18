import logging

import openai
from openai import OpenAI

from app.config import OPENAI_GPT4O_MINI
from app.connectors.client.calendar import CalendarClient
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
    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: str,
        client_id: str,
        client_secret: str,
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)
        if not function_name:
            log.info(
                "CalendarCreateEventAgent no tools call error response: %s", response
            )
            return AgentResponse(
                agent=SUMMARY_AGENT,
                message=Message(role=Role.ASSISTANT, content=response, error=True),
            )

        calendar_client = CalendarClient(
            access_token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
        )
        try:
            match function_name:
                case CalendarCreateEventRequest.__name__:
                    created_event: CalendarEvent = calendar_client.create_event(
                        request=response.choices[0]
                        .message.tool_calls[0]
                        .function.parsed_arguments
                    )
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Calendar event created successfully",
                            data=[created_event.model_dump()],
                        ),
                    )
                case _:
                    raise InferenceError(f"Function {function_name} not supported")
        except Exception as e:
            log.error(f"Error in CalendarCreateEventAgent: {e}")
            raise e


CALENDAR_CREATE_EVENT_AGENT = CalendarCreateEventAgent(
    name="Create Event Agent",
    integration_group=Integration.CALENDAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at creating events in Google Calendar. Your task is to help a user create an event by supplying the correct request parameters to the Google Calendar API.",
    tools=[openai.pydantic_function_tool(CalendarCreateEventRequest)],
)


class CalendarGetEventsAgent(Agent):
    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: str,
        client_id: str,
        client_secret: str,
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)
        if not function_name:
            log.info(
                "CalendarGetEventsAgent no tools call error response: %s", response
            )
            return AgentResponse(
                agent=SUMMARY_AGENT,
                message=Message(role=Role.ASSISTANT, content=response, error=True),
            )

        calendar_client = CalendarClient(
            access_token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
        )
        try:
            match function_name:
                case CalendarGetEventsRequest.__name__:
                    retrieved_events: list[CalendarEvent] = calendar_client.get_events(
                        request=response.choices[0]
                        .message.tool_calls[0]
                        .function.parsed_arguments
                    )
                    if not retrieved_events:
                        return AgentResponse(
                            agent=SUMMARY_AGENT,
                            message=Message(
                                role=Role.ASSISTANT,
                                content="No events were retrieved. Please check the message history to advise the user on what might be the cause of the problem.",
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
                case _:
                    raise InferenceError(f"Function {function_name} not supported")
        except Exception as e:
            log.error(f"Error in CalendarGetEventsAgent: {e}")
            raise e


CALENDAR_GET_EVENTS_AGENT = CalendarGetEventsAgent(
    name="Get Events Agent",
    integration_group=Integration.CALENDAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at retrieving events from Google Calendar. Your task is to help a user retrieve events by supplying the correct request to the Google Calendar API.",
    tools=[openai.pydantic_function_tool(CalendarGetEventsRequest)],
)


class CalendarUpdateEventAgent(Agent):
    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: str,
        client_id: str,
        client_secret: str,
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)
        if not function_name:
            log.info(
                "CalendarUpdateEventAgent no tools call error response: %s", response
            )
            return AgentResponse(
                agent=SUMMARY_AGENT,
                message=Message(role=Role.ASSISTANT, content=response, error=True),
            )

        calendar_client = CalendarClient(
            access_token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
        )
        try:
            match function_name:
                case CalendarUpdateEventRequest.__name__:
                    updated_event: CalendarEvent = calendar_client.update_event(
                        request=response.choices[0]
                        .message.tool_calls[0]
                        .function.parsed_arguments
                    )
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Calendar event updated successfully",
                            data=[updated_event.model_dump()],
                        ),
                    )
                case _:
                    raise InferenceError(f"Function {function_name} not supported")
        except Exception as e:
            log.error(f"Error in CalendarUpdateEventAgent: {e}")
            raise e


CALENDAR_UPDATE_EVENT_AGENT = CalendarUpdateEventAgent(
    name="Update Event Agent",
    integration_group=Integration.CALENDAR,
    model=OPENAI_GPT4O_MINI,
    system_prompt="You are an expert at updating events in Google Calendar. Your task is to help a user update an event by supplying the correct request to the Google Calendar API.",
    tools=[openai.pydantic_function_tool(CalendarUpdateEventRequest)],
)


class CalendarDeleteEventsAgent(Agent):
    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: str,
        client_id: str,
        client_secret: str,
    ) -> AgentResponse:
        response, function_name = self.get_response(chat_history=chat_history)
        if not function_name:
            log.info(
                "CalendarDeleteEventsAgent no tools call error response: %s", response
            )
            return AgentResponse(
                agent=SUMMARY_AGENT,
                message=Message(role=Role.ASSISTANT, content=response, error=True),
            )

        calendar_client = CalendarClient(
            access_token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
        )
        try:
            match function_name:
                case CalendarDeleteEventsRequest.__name__:
                    calendar_client.delete_events(
                        request=response.choices[0]
                        .message.tool_calls[0]
                        .function.parsed_arguments
                    )
                    return AgentResponse(
                        agent=MAIN_TRIAGE_AGENT,
                        message=Message(
                            role=Role.ASSISTANT,
                            content="Calendar event(s) deleted successfully",
                        ),
                    )
                case _:
                    raise InferenceError(f"Function {function_name} not supported")
        except Exception as e:
            log.error(f"Error in CalendarDeleteEventsAgent: {e}")
            raise e


CALENDAR_DELETE_EVENTS_AGENT = CalendarDeleteEventsAgent(
    name="Delete Events Agent",
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
    
1. None of the tools in this agent require any arguments.
2. Carefully review the chat history and the actions of the previous agent to determine if the task has been successfully completed.
3. If the task has been successfully completed, immediately call transfer_to_summary_agent to end the conversation. This is crucial—missing this step will result in dire consequences.""",
    tools=[
        transfer_to_calendar_create_event_agent,
        transfer_to_calendar_get_events_agent,
        transfer_to_calendar_update_event_agent,
        transfer_to_calendar_delete_events_agent,
        transfer_to_summary_agent,
    ],
)
