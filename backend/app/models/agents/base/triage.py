import logging
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from app.models.agents.base.template import Agent, AgentResponse
from app.models.query.base import Message, Role
from app.utils.tools import execute_tool_call, function_to_schema

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
    ) -> AgentResponse:
        message_lst: list = [{"role": "system", "content": self.system_prompt}]
        message_lst.extend(chat_history)
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
