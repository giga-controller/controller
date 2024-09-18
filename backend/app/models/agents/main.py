from app.config import OPENAI_GPT4O_MINI
from app.models.agents.base.summary import transfer_to_summary_agent
from app.models.agents.base.triage import TriageAgent
from app.models.integrations.base import Integration


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


def transfer_to_x_triage_agent():
    from app.models.agents.x import X_TRIAGE_AGENT

    return X_TRIAGE_AGENT


# this is a very delicate prompt carefully engineered by dear aaron. do not tamper unless strictly necessary
MAIN_TRIAGE_AGENT = TriageAgent(
    name="Main Triage Agent",
    integration_group=Integration.NONE,
    model=OPENAI_GPT4O_MINI,
    system_prompt="""You are an expert at choosing the right integration agent to perform the task described by the user and reflecting on the actions of previously called agents. Follow these guidelines:

1. Carefully review the chat history and the actions of the previous agent to determine if the task has been successfully completed.
2. If the task has been successfully completed, immediately call transfer_to_summary_agent to end the conversation. This is crucial—missing this step will result in dire consequences.
3. If the task is not yet complete, choose the appropriate integration triage agent based on the user's request and the current progress.
4. Remember, transfer_to_summary_agent must be called under two conditions:
   - When the task is completed.
   - When the instructions are unclear, or you are unsure which integration agent to choose. Missing these conditions will cause the world to end.
5. Do not pass any arguments when calling the transfer functions; they do not accept any parameters.
""",
    tools=[
        transfer_to_gmail_triage_agent,
        transfer_to_linear_triage_agent,
        transfer_to_slack_triage_agent,
        transfer_to_calendar_triage_agent,
        transfer_to_summary_agent,
    ],
)
