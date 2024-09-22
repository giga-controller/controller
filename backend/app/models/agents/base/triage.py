import logging
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from app.models.agents.base.template import Agent, AgentResponse
from app.models.integrations.base import Integration
from app.models.query.base import Message, Role
from app.utils.tools import execute_tool_call, function_to_schema
from app.models.agents.base.summary import transfer_to_summary_agent

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)


class TriageAgent(Agent):

    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        enable_verification: bool = False,
        integrations: list[Integration] = [],
    ) -> AgentResponse:
        message_lst: list = [{"role": "system", "content": self.system_prompt}]
        message_lst.extend(chat_history)
    
        # Only gets triggerd for main triage agent
        if integrations:
            self.tools = get_integration_agent_tools(integrations)

        tool_schemas = [function_to_schema(tool) for tool in self.tools]
        tools = {tool.__name__: tool for tool in self.tools}

        response = openai_client.chat.completions.create(
            model=self.model,
            messages=message_lst,
            tools=tool_schemas,
            tool_choice="required",
        )

        tool_call = response.choices[0].message.tool_calls[0]
        message_content: str = f"Triage Agent invokes {tool_call.function.name}"

        return AgentResponse(
            agent=execute_tool_call(tool_call, tools, self.name),
            message=Message(role=Role.ASSISTANT, content=message_content),
            function_to_verify=None,
        )
        
def get_integration_agent_tools(integrations: list[Integration]) -> list:
    """Returns the main triage agent's tools based on the integrations passed in"""
    
    if not integrations:
        raise ValueError("At least one integration must be provided")
    
    tools: list = [transfer_to_summary_agent]
    
    for integration in integrations:
        match integration:
            case Integration.GMAIL:
                tools.append(transfer_to_gmail_triage_agent)
            case Integration.LINEAR:
                tools.append(transfer_to_linear_triage_agent)
            case Integration.SLACK:
                tools.append(transfer_to_slack_triage_agent)
            case Integration.CALENDAR:
                tools.append(transfer_to_calendar_triage_agent)
            case Integration.X:
                tools.append(transfer_to_x_triage_agent)
            case Integration.DOCS:
                tools.append(transfer_to_docs_triage_agent)
            case _:
                pass

    return tools

def transfer_to_gmail_triage_agent():
    from app.models.agents.gmail import GMAIL_TRIAGE_AGENT

    return GMAIL_TRIAGE_AGENT


def transfer_to_calendar_triage_agent():
    from app.models.agents.calendar import CALENDAR_TRIAGE_AGENT

    return CALENDAR_TRIAGE_AGENT


def transfer_to_linear_triage_agent():
    from app.models.agents.linear import LINEAR_TRIAGE_AGENT

    return LINEAR_TRIAGE_AGENT


def transfer_to_slack_triage_agent():
    from app.models.agents.slack import SLACK_TRIAGE_AGENT

    return SLACK_TRIAGE_AGENT


def transfer_to_sheets_triage_agent():
    from app.models.agents.sheets import SHEETS_TRIAGE_AGENT

    return SHEETS_TRIAGE_AGENT

def transfer_to_docs_triage_agent():
    from app.models.agents.docs import DOCS_TRIAGE_AGENT

    return DOCS_TRIAGE_AGENT


def transfer_to_x_triage_agent():
    from app.models.agents.x import X_TRIAGE_AGENT

    return X_TRIAGE_AGENT

