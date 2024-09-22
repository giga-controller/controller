import json
import logging

import requests
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from app.models.integrations.linear import (
    LinearCreateIssueRequest,
    LinearDeleteIssuesRequest,
    LinearFilterIssuesRequest,
    LinearGetIssuesRequest,
    LinearIssue,
    LinearIssueQuery,
    LinearUpdateIssuesAssigneeRequest,
    LinearUpdateIssuesCycleRequest,
    LinearUpdateIssuesDescriptionRequest,
    LinearUpdateIssuesEstimateRequest,
    LinearUpdateIssuesLabelsRequest,
    LinearUpdateIssuesProjectRequest,
    LinearUpdateIssuesStateRequest,
    LinearUpdateIssuesTitleRequest,
)

logging.getLogger("gql").setLevel(logging.WARNING)
logging.getLogger("gql.transport.requests").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)

log = logging.getLogger(__name__)

LINEAR_API_URL = "https://api.linear.app/graphql"


class LinearClient:
    def __init__(self, access_token: str):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        transport = RequestsHTTPTransport(
            url=LINEAR_API_URL,
            headers=self.headers,
            use_json=True,
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def query_grapql(self, query):
        r = requests.post(LINEAR_API_URL, json={"query": query}, headers=self.headers)

        response = json.loads(r.content)

        if "errors" in response:
            raise Exception(response["errors"])

        return response

    def query_basic_resource(self, resource=""):
        resource_response = self.query_grapql(
            """
                query Resource {"""
            + resource
            + """{nodes{id,name}}}
            """
        )

        return resource_response["data"][resource]["nodes"]

    def teams(self):
        return self.query_basic_resource("teams")

    def states(self):
        return self.query_basic_resource("workflowStates")

    def projects(self):
        return self.query_basic_resource("projects")

    def create_issue(self, request: LinearCreateIssueRequest) -> LinearIssue:
        MUTATION_NAME = "issueCreate"

        mutation = gql(
            f"""
            mutation CreateIssue($input: IssueCreateInput!) {{
                {MUTATION_NAME}(input: $input) {{
                    success
                    issue {{
                        id
                        number
                        title
                        description
                        priority
                        estimate
                        state {{ name }}
                        assignee {{ name }}
                        creator {{ name }}
                        labels {{ nodes {{ name }} }}
                        createdAt
                        updatedAt
                        dueDate
                        cycle {{ number }}
                        project {{ name }}
                        comments {{ nodes {{ body user {{ name }} }} }}
                        url
                    }}
                }}
            }}
            """
        )

        variables = {
            "input": {
                "title": request.title,
                "description": request.description,
                "stateId": (
                    self.get_state_id_by_name(name=request.state.value)
                    if request.state
                    else None
                ),
                "priority": request.priority,
                "assigneeId": (
                    self.get_id_by_name(name=request.assignee, target="users")
                    if request.assignee
                    else None
                ),
                "estimate": request.estimate,
                "cycleId": (
                    self.get_id_by_number(number=request.cycle, target="cycles")
                    if request.cycle
                    else None
                ),
                "labels": request.labels if request.labels else None,
                "projectId": (
                    self.get_id_by_name(name=request.project, target="projects")
                    if request.project
                    else None
                ),
                "teamId": self.teams()[0][
                    "id"
                ],  # QUICK FIX WE ONLY GET FROM FIRST TEAM (THIS IS A HACK)
            }
        }

        variables["input"] = {
            k: v for k, v in variables["input"].items() if v is not None
        }

        result = self.client.execute(mutation, variable_values=variables)
        return LinearIssue.model_validate(
            _flatten_linear_response_issue(result[MUTATION_NAME]["issue"])
        )

    def get_issues(self, request: LinearGetIssuesRequest) -> list[LinearIssue]:
        validated_results: list[LinearIssue] = []
        if request.issue_ids:
            variables = {}
            QUERY_OBJ_NAME: str = "issue"
            query = gql(
                f"""
                query GetIssue($id: String!) {{
                    {QUERY_OBJ_NAME}(id: $id) {{
                        id
                        number
                        title
                        description
                        priority
                        estimate
                        state {{ name }}
                        assignee {{ name }}
                        creator {{ name }}
                        labels {{ nodes {{ name }} }}
                        createdAt
                        updatedAt
                        dueDate
                        cycle {{ number }}
                        project {{ name }}
                        comments {{ nodes {{ body user {{ name }} }} }}
                        url
                    }}
                }}
            """
            )
            for issue_id in request.issue_ids:
                variables["id"] = issue_id
                result = self.client.execute(query, variable_values=variables)
                validated_results.append(
                    _flatten_linear_response_issue(result[QUERY_OBJ_NAME])
                )
            return validated_results

        validated_results.extend(
            self._get_issues_with_boolean_clause(issue_query=request.query)
        )
        return validated_results

    def _get_issues_with_boolean_clause(
        self, issue_query: LinearIssueQuery
    ) -> list[LinearIssue]:
        variables = {}
        validated_results: list[LinearIssue] = []
        QUERY_OBJ_GROUP: str = "issues"
        QUERY_OBJ_LIST: str = "nodes"
        boolean_clause: str = "and" if issue_query.use_and_clause else "or"
        query = gql(
            f"""
            query GetIssues($filter: IssueFilter) {{
                {QUERY_OBJ_GROUP}(filter: $filter) {{
                    {QUERY_OBJ_LIST}{{
                        id
                        number
                        title
                        description
                        priority
                        estimate
                        state {{ name }}
                        assignee {{ name }}
                        creator {{ name }}
                        labels {{ nodes {{ name }} }}
                        createdAt
                        updatedAt
                        dueDate
                        cycle {{ number }}
                        project {{ name }}
                        comments {{ nodes {{ body user {{ name }} }} }}
                        url
                    }}
                }}
            }}
        """
        )
        variables["filter"] = {boolean_clause: []}
        if issue_query.state:
            variables["filter"][boolean_clause].extend(
                [{"state": {"name": {"eq": _state}}} for _state in issue_query.state]
            )
        if issue_query.number:
            variables["filter"][boolean_clause].extend(
                [{"number": {"eq": _number}} for _number in issue_query.number]
            )
        if issue_query.title:
            variables["filter"][boolean_clause].extend(
                [{"title": {"contains": _title}} for _title in issue_query.title]
            )
        if issue_query.assignee:
            variables["filter"][boolean_clause].extend(
                [
                    {"assignee": {"name": {"eq": _assignee}}}
                    for _assignee in issue_query.assignee
                ]
            )
        if issue_query.creator:
            variables["filter"][boolean_clause].extend(
                [
                    {"creator": {"name": {"eq": _creator}}}
                    for _creator in issue_query.creator
                ]
            )
        if issue_query.project:
            variables["filter"][boolean_clause].extend(
                [
                    {"project": {"name": {"eq": _project}}}
                    for _project in issue_query.project
                ]
            )
        if issue_query.cycle:
            variables["filter"][boolean_clause].extend(
                [{"cycle": {"number": {"eq": _cycle}}} for _cycle in issue_query.cycle]
            )
        if issue_query.labels:
            variables["filter"][boolean_clause].extend(
                [
                    {"labels": {"some": {"name": {"in": _labels}}}}
                    for _labels in issue_query.labels
                ]
            )
        if issue_query.estimate:
            variables["filter"][boolean_clause].extend(
                [{"estimate": {"eq": _estimate}} for _estimate in issue_query.estimate]
            )
        result = self.client.execute(query, variable_values=variables)

        for issue in result[QUERY_OBJ_GROUP][QUERY_OBJ_LIST]:
            validated_results.append(_flatten_linear_response_issue(issue))
        return validated_results

    def update_issues(self, request: LinearFilterIssuesRequest) -> list[LinearIssue]:
        variables = {}
        validated_results: list[LinearIssue] = []

        issues_to_update = self.get_issues(request=request)

        mutation_name: str = "issueUpdate"
        mutation = _get_update_mutation(mutation_name=mutation_name)

        for issue in issues_to_update:
            variables["id"] = issue.id
            variables["update"] = {}
            if isinstance(request, LinearUpdateIssuesStateRequest):
                variables["update"]["stateId"] = self.get_state_id_by_name(
                    name=request.updated_state.value
                )
            elif isinstance(request, LinearUpdateIssuesAssigneeRequest):
                variables["update"]["assigneeId"] = self.get_id_by_name(
                    name=request.updated_assignee, target="users"
                )
            elif isinstance(request, LinearUpdateIssuesTitleRequest):
                variables["update"]["title"] = request.updated_title
            elif isinstance(request, LinearUpdateIssuesDescriptionRequest):
                variables["update"]["description"] = request.updated_description
            elif isinstance(request, LinearUpdateIssuesLabelsRequest):
                variables["update"]["labelIds"] = [
                    self.get_label_id_by_name(name=label)
                    for label in request.updated_labels
                ]
            elif isinstance(request, LinearUpdateIssuesCycleRequest):
                variables["update"]["cycleId"] = self.get_id_by_number(
                    number=request.updated_cycle, target="cycles"
                )
            elif isinstance(request, LinearUpdateIssuesProjectRequest):
                variables["update"]["projectId"] = self.get_id_by_name(
                    name=request.updated_project, target="projects"
                )
            elif isinstance(request, LinearUpdateIssuesEstimateRequest):
                variables["update"]["estimate"] = request.updated_estimate
            else:
                raise ValueError(f"Unsupported request type: {type(request)}")

            result = self.client.execute(mutation, variable_values=variables)
            validated_results.append(
                _flatten_linear_response_issue(result[mutation_name]["issue"])
            )

        return validated_results

    def delete_issues(self, request: LinearDeleteIssuesRequest) -> list[LinearIssue]:
        variables = {}
        issues_to_delete = self.get_issues(request=request)

        MUTATION_NAME: str = "issueDelete"
        mutation = gql(
            f"""
            mutation DeleteIssue($id: String!) {{
                {MUTATION_NAME}(id: $id) {{
                    success
                }}
            }}
            """
        )

        for issue in issues_to_delete:
            variables["id"] = issue.id
            self.client.execute(mutation, variable_values=variables)

        return issues_to_delete

    ###
    ### Helper
    ###
    def get_id_by_name(self, name: str, target: str) -> str:
        query = gql(
            f"""
            query GetIdByName($name: String!) {{
                {target}(filter: {{ name: {{ eq: $name }} }}) {{
                    nodes {{
                        id
                    }}
                }}
            }}
            """
        )

        variables = {"name": name}

        result = self.client.execute(query, variable_values=variables)
        users = result.get(target, {}).get("nodes", [])

        if users:
            return users[0]["id"]
        else:
            raise ValueError(f"{target} with name '{name}' not found.")

    def get_id_by_number(self, number: int, target: str) -> str:
        query = gql(
            f"""
            query GetIdByNumber($number: Float!) {{
                {target}(filter: {{ number: {{ eq: $number }} }}) {{
                    nodes {{
                        id
                    }}
                }}
            }}
            """
        )

        variables = {"number": number}

        result = self.client.execute(query, variable_values=variables)
        cycles = result.get(target, {}).get("nodes", [])

        if cycles:
            return cycles[0]["id"]
        else:
            raise ValueError(f"Cycle with number '{number}' not found.")

    def get_state_id_by_name(self, name: str) -> str:
        query = gql(
            """
            query GetStateIdByName {
                workflowStates {
                    nodes {
                        id
                        name
                    }
                }
            }
            """
        )

        result = self.client.execute(query)
        states = result.get("workflowStates", {}).get("nodes", [])

        # Filter the states by name in the application code
        for state in states:
            if state["name"] == name:
                return state["id"]

        raise ValueError(f"State with name '{name}' not found.")

    def get_label_id_by_name(self, name: str) -> str:
        query = gql(
            """
            query GetLabelIdByName($name: String!) {
                issueLabels(filter: { name: { eq: $name } }) {
                    nodes {
                        id
                        name
                    }
                }
            }
            """
        )

        variables = {"name": name}
        result = self.client.execute(query, variable_values=variables)
        labels = result.get("issueLabels", {}).get("nodes", [])

        if labels:
            return labels[0]["id"]

        raise ValueError(f"Label with name '{name}' not found.")


def _flatten_linear_response_issue(issue: dict) -> LinearIssue:
    if "labels" in issue and "nodes" in issue["labels"]:
        issue["labels"] = [label["name"] for label in issue["labels"]["nodes"]]
    if "comments" in issue and "nodes" in issue["comments"]:
        issue["comments"] = [
            {"message": comment["body"], "user": comment["user"]["name"]}
            for comment in issue["comments"]["nodes"]
        ]
    if "project" in issue and issue["project"]:
        issue["project"] = issue["project"]["name"]
    if "cycle" in issue and issue["cycle"]:
        issue["cycle"] = issue["cycle"]["number"]
    if "state" in issue and issue["state"]:
        issue["state"] = issue["state"]["name"]
    if "assignee" in issue and issue["assignee"]:
        issue["assignee"] = issue["assignee"]["name"]
    if "creator" in issue and issue["creator"]:
        issue["creator"] = issue["creator"]["name"]

    return LinearIssue.model_validate(issue)


def _get_update_mutation(mutation_name: str) -> str:
    mutation = gql(
        f"""
        mutation UpdateIssueState($id: String!, $update: IssueUpdateInput!) {{
            {mutation_name}(id: $id, input: $update) {{
                success
                issue {{
                    id
                    number
                    title
                    description
                    priority
                    estimate
                    state {{ name }}
                    assignee {{ name }}
                    creator {{ name }}
                    labels {{ nodes {{ name }} }}
                    createdAt
                    updatedAt
                    dueDate
                    cycle {{ number }}
                    project {{ name }}
                    comments {{ nodes {{ body user {{ name }} }} }}
                    url
                }}
            }}
        }}
        """
    )
    return mutation
