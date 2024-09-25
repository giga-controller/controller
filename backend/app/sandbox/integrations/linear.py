import os

from dotenv import load_dotenv

from app.connectors.client.linear import LinearClient
from app.models.agents.base.template import AgentResponse
from app.models.agents.linear import LINEAR_TRIAGE_AGENT
from app.models.integrations.linear import (
    Label,
    Labels,
    LinearCreateIssueRequest,
    LinearDeleteIssuesRequest,
    LinearGetIssuesRequest,
)
from app.models.query.base import Message, Role

load_dotenv()

LINEAR_ACCESS_TOKEN = os.getenv("LINEAR_ACCESS_TOKEN")

client = LinearClient(
    access_token=LINEAR_ACCESS_TOKEN,
)


def main():
    # chat_history: list[Message] = []
    # message = Message(
    #     role=Role.USER,
    #     content="I want to update the status of all the issues assigned to huge whale to todo.",
    # ).model_dump()
    # chat_history.append(message)
    # response = AgentResponse(agent=LINEAR_TRIAGE_AGENT, message=message)
    # while response.agent:
    #     response = response.agent.query(
    #         chat_history=chat_history,
    #         access_token=LINEAR_ACCESS_TOKEN,
    #         refresh_token=None,
    #         client_id=None,
    #         client_secret=None,
    #     )
    #     chat_history.append(Message(role=Role.ASSISTANT, content=str(response.message)))
    # print(chat_history)
    print(
        client.titles()
    )


if __name__ == "__main__":
    main()

### HARD CODE TEST
## Create Issue
#     # TODO: Change the types of some of these (e.g. priority 1 doesnt actually make any sense from a natural language standpoint)
#     client.create_issue(
#         LinearCreateIssueRequest(
#             title="Test Issue",
#             description="This is a test issue",
#             priority=1,
#             estimate=1,
#             state=Status.TODO,
#             assignee="huge whale",
#             creator="huge whale",
#             labels=None,
#             dueDate=None,
#             cycle=1,
#             project="Onboarding",
#         )
#     )
# )

## Get Issues
#     client.get_issues(
#         LinearGetIssueRequest(
#             id=None,
#             state=None,
#             assignee="huge whale",
#             creator=None,
#             project=None,
#             cycle=1,
#         )
#     )

## Update Issues
#   print(client.update_issues(
#         LinearUpdateIssuesRequest(
#             filter_conditions=LinearGetIssuesRequest(
#                 id=None,
#                 state=None,
#                 assignee="huge whale",
#                 creator=None,
#                 project=None,
#                 cycle=None,
#                 labels=None,
#                 estimate=None
#             ),
#             update_conditions=LinearCreateIssueRequest(
#                 title=None,
#                 description=None,
#                 priority=None,
#                 estimate=None,
#                 state=Status.DONE,
#                 assignee=None,
#                 creator=None,
#                 labels=None,
#                 dueDate=None,
#                 cycle=None,
#                 project=None
#             )
#         )
#     ))


### AGENT TEST
# chat_history: list[Message] = []
# message = Message(
#     role=Role.USER,
#     content="I want to get all issues in the team that has high priority or above. The state, assignee, creator, project, cycle of the issue can be anything",
# ).model_dump()
# chat_history.append(message)
# response = AgentResponse(agent=LINEAR_TRIAGE_AGENT, message=message)
# while response.agent:
#     response = response.agent.query(
#         chat_history=chat_history,
#         access_token=LINEAR_ACCESS_TOKEN,
#         refresh_token=None,
#         client_id=None,
#         client_secret=None,
#     )
#     chat_history.append(Message(role=Role.ASSISTANT, content=str(response.message)))
# print(chat_history)
