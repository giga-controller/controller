import logging
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from app.config import OPENAI_GPT4O_MINI
from app.models.agents.base.template import Agent, AgentResponse
from app.models.integrations.base import Integration
from app.models.query.base import Message, Role

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)


class SummaryAgent(Agent):

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
        # No need for tools in this agent (for now)
        message_lst: list = [{"role": "system", "content": self.system_prompt}]
        message_lst.extend(chat_history)
        response = openai_client.chat.completions.create(
            model=self.model, messages=message_lst
        )
        return AgentResponse(
            agent=None,
            message=Message(
                role=Role.ASSISTANT, content=response.choices[0].message.content
            ),
            function_to_verify=None,
        )


SUMMARY_AGENT = SummaryAgent(
    name="Summary Agent",
    integration_group=Integration.NONE,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at summarizing conversations between a human user and an AI agent named Controller. Create a clear, concise summary of actions taken and results achieved in no more than a few lines. Include:
- Brief overview of accomplishments or attempts
- Main tasks executed by Controller
- Important results or information obtained
- Any errors or failures, or suggested next steps if no tasks were executed, such as asking the user to provide more information in the instruction
Use simple language and avoid technical jargon. You may use bullet points, dashes or emojis for clarity. Your response will be formatted markdown-style, so make sure to use appropriate markdown syntax for headings, lists, and other formatting to make it more readable.""".strip(),
    tools=[],
)


def transfer_to_summary_agent() -> SummaryAgent:
    return SUMMARY_AGENT
