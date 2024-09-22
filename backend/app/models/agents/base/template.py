import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from app.models.integrations.base import Integration
from app.models.query.base import Message

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

openai_client = OpenAI()


class Agent(BaseModel, ABC):
    name: str
    integration_group: Integration
    model: str
    system_prompt: str
    tools: list

    @abstractmethod
    def query(
        self,
        chat_history: list[dict],
        access_token: str,
        refresh_token: Optional[str],
        client_id: str,
        client_secret: str,
        enable_verification: bool,
        **kwargs,
    ) -> "AgentResponse":
        pass

    def get_response(
        self,
        chat_history: list[dict],
    ) -> tuple[Any, Optional[str]]:
        message_lst: list = [{"role": "system", "content": self.system_prompt}]
        message_lst.extend(chat_history)
        response = openai_client.beta.chat.completions.parse(
            model=self.model,
            messages=message_lst,
            tools=self.tools,
            tool_choice="required",
        )

        if not response.choices[0].message.tool_calls:
            log.info("No tool calls")
            return response.choices[0].message.content, None

        function_name: str = response.choices[0].message.tool_calls[0].function.name
        parsed_arguments = (
            response.choices[0].message.tool_calls[0].function.parsed_arguments
        )
        log.info(f"Parsed Arguments: {parsed_arguments}")

        return response, function_name


class AgentResponse(BaseModel):
    agent: Optional[Agent]
    message: Message
    function_to_verify: Optional[str] = None
