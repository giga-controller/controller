import asyncio
import logging
from collections import defaultdict
from typing import Optional

import httpx
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from pydantic import BaseModel

from app.models.integrations.linear import (
    Label,
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
    Project,
    State,
    Title,
    User,
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
        transport = AIOHTTPTransport(
            url=LINEAR_API_URL,
            headers=self.headers,
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)
    
    async def close(self):
        await self.client.transport.close()

    async def query_grapql(self, query):
        async with httpx.AsyncClient() as client:
            r = await client.post(
                LINEAR_API_URL, json={"query": query}, headers=self.headers
            )

        response = r.json()

        if "errors" in response:
            raise Exception(response["errors"])

        return response

    async def query_basic_resource(self, resource: str, subfields: str):

        resource_response = await self.query_grapql(
            f"""
                query Resource {{
                    {resource} {{
                        nodes {{
                            {subfields}
                        }}
                    }}
                }}
            """
        )

        return resource_response["data"][resource]["nodes"]

    async def teams(self) -> list[dict]:
        return await self.query_basic_resource(resource="teams", subfields="id,name")

    async def states(self) -> list[dict]:
        return await self.query_basic_resource(
            resource="workflowStates", subfields="name"
        )

    async def projects(self) -> list[dict]:
        return await self.query_basic_resource(resource="projects", subfields="name")

    async def users(self) -> list[dict]:
        return await self.query_basic_resource(resource="users", subfields="name")

    async def labels(self) -> list[dict]:
        return await self.query_basic_resource(resource="issueLabels", subfields="name")

    async def titles(self) -> list[dict]:
        return await self.query_basic_resource(resource="issues", subfields="title")

    async def create_issue(self, request: LinearCreateIssueRequest) -> LinearIssue:
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

        state_id_task = asyncio.create_task(self.get_state_id_by_name(state=request.state))
        assignee_id_task = asyncio.create_task(self.get_id_by_name(name=request.assignee, target="users"))
        cycle_id_task = asyncio.create_task(self.get_id_by_number(number=request.cycle, target="cycles"))
        project_id_task = asyncio.create_task(self.get_id_by_name(name=request.project, target="projects"))
        team_id_task = asyncio.create_task(self.teams())

        state_id, assignee_id, cycle_id, project_id, teams = await asyncio.gather(
            state_id_task, assignee_id_task, cycle_id_task, project_id_task, team_id_task
        )
        
        variables = {
            "input": {
                "title": request.title,
                "description": request.description,
                "stateId": state_id,
                "priority": request.priority,
                "assigneeId": assignee_id,
                "estimate": request.estimate,
                "cycleId": cycle_id,
                "labels": request.labels if request.labels else None,
                "projectId": project_id,
                "teamId": teams[0]["id"],  # QUICK FIX WE ONLY GET FROM FIRST TEAM (THIS IS A HACK)
            }
        }

        variables["input"] = {
            k: v for k, v in variables["input"].items() if v is not None
        }

        result = await self.client.execute_async(mutation, variable_values=variables)
        return LinearIssue.model_validate(
            await _flatten_linear_response_issue(result[MUTATION_NAME]["issue"])
        )

    async def get_issues(self, request: LinearGetIssuesRequest) -> list[LinearIssue]:
        if request.issue_ids:
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
            get_issue_tasks = [
                asyncio.create_task(self.client.execute_async(query, variable_values={"id": issue_id}))
                for issue_id in request.issue_ids
            ]
            get_issue_results = await asyncio.gather(*get_issue_tasks)
            
            flatten_issue_tasks = [
                asyncio.create_task(_flatten_linear_response_issue(result[QUERY_OBJ_NAME])) for result in get_issue_results
            ]
            flattened_issue_results = await asyncio.gather(*flatten_issue_tasks)
            
            return flattened_issue_results

        return await self._get_issues_with_boolean_clause(issue_query=request.query)

    def get_zero_match_parameters(
        self, query: LinearIssueQuery
    ) -> dict[str, list[BaseModel]]:
        """Returns a dictionary where the keys are the parameters provided in the query and the values are the paramter values that did not have any matches with any items"""

        QUERY_OBJ_GROUP = "issues"
        QUERY_OBJ_LIST = "nodes"
        test_query = gql(
            f"""
            query TestFilter($filter: IssueFilter) {{
                {QUERY_OBJ_GROUP}(filter: $filter) {{
                    {QUERY_OBJ_LIST} {{
                        id
                    }}
                }}
            }}
            """
        )

        def is_parameter_valid(filter_clause: dict) -> bool:
            """Returns True if the filter clause matches with at least one item and False otherwise"""
            test_variables = {"filter": {"and": [filter_clause]}}
            test_result = self.client.execute(
                test_query, variable_values=test_variables
            )
            if test_result[QUERY_OBJ_GROUP][
                QUERY_OBJ_LIST
            ]:  # Parameter is valid if there is at least one item that matches the parameter
                return True
            return False

        zero_match_parameters = defaultdict(list[BaseModel])
        query_dict = query.model_dump()

        for param, value_lst in query_dict.items():
            if not value_lst:  # No need to test if the parameter is not provided
                continue

            for value in value_lst:
                match param:
                    case "title":
                        filter_clause = {"title": {"contains": value}}
                        if is_parameter_valid(filter_clause=filter_clause):
                            continue
                        zero_match_parameters[param].append(Title(title=value))
                    case "assignee":
                        filter_clause = {"assignee": {"name": {"eq": value}}}
                        if is_parameter_valid(filter_clause=filter_clause):
                            continue
                        zero_match_parameters[param].append(User(name=value))
                    case "creator":
                        filter_clause = {"creator": {"name": {"eq": value}}}
                        if is_parameter_valid(filter_clause=filter_clause):
                            continue
                        zero_match_parameters[param].append(User(name=value))
                    case "project":
                        filter_clause = {"project": {"name": {"eq": value}}}
                        if is_parameter_valid(filter_clause=filter_clause):
                            continue
                        zero_match_parameters[param].append(Project(name=value))
                    case "labels":
                        filter_clause = {"labels": {"some": {"name": {"in": value}}}}
                        if is_parameter_valid(filter_clause=filter_clause):
                            continue
                        zero_match_parameters[param].append(Label(name=value))
                    case _:
                        raise ValueError(f"Unknown parameter: {param}")

        return zero_match_parameters

    async def _get_issues_with_boolean_clause(
        self, issue_query: LinearIssueQuery
    ) -> list[LinearIssue]:
        variables = {}
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
        if issue_query.labels:
            variables["filter"][boolean_clause].extend(
                [
                    {"labels": {"some": {"name": {"in": _label}}}}
                    for _label in issue_query.labels
                ]
            )
        if issue_query.state:
            variables["filter"][boolean_clause].extend(
                [{"state": {"name": {"eq": _state}}} for _state in issue_query.state]
            )
        if issue_query.number:
            variables["filter"][boolean_clause].extend(
                [{"number": {"eq": _number}} for _number in issue_query.number]
            )
        if issue_query.cycle:
            variables["filter"][boolean_clause].extend(
                [{"cycle": {"number": {"eq": _cycle}}} for _cycle in issue_query.cycle]
            )
        if issue_query.estimate:
            variables["filter"][boolean_clause].extend(
                [{"estimate": {"eq": _estimate}} for _estimate in issue_query.estimate]
            )
        get_issue_results = await self.client.execute_async(query, variable_values=variables)
        flatten_issue_tasks = [
            asyncio.create_task(_flatten_linear_response_issue(result)) for result in get_issue_results[QUERY_OBJ_GROUP][QUERY_OBJ_LIST]
        ]
        flattened_issue_results: list[LinearIssue] = await asyncio.gather(*flatten_issue_tasks)
            
        return flattened_issue_results

    async def update_issues(self, request: LinearFilterIssuesRequest) -> list[LinearIssue]:
        variables = {}

        issues_to_update = await self.get_issues(request=request)

        mutation_name: str = "issueUpdate"
        mutation = _get_update_mutation(mutation_name=mutation_name)

        update_issue_tasks = []
        for issue in issues_to_update:
            variables["id"] = issue.id
            variables["update"] = {}
            if isinstance(request, LinearUpdateIssuesStateRequest):
                variables["update"]["stateId"] = await self.get_state_id_by_name(
                    state=request.updated_state
                )
            elif isinstance(request, LinearUpdateIssuesAssigneeRequest):
                variables["update"]["assigneeId"] = await self.get_id_by_name(
                    name=request.updated_assignee, target="users"
                )
            elif isinstance(request, LinearUpdateIssuesTitleRequest):
                variables["update"]["title"] = request.updated_title
            elif isinstance(request, LinearUpdateIssuesDescriptionRequest):
                variables["update"]["description"] = request.updated_description
            elif isinstance(request, LinearUpdateIssuesLabelsRequest):
                variables["update"]["labelIds"] = [
                    await self.get_label_id_by_name(name=label)
                    for label in request.updated_labels
                ]
            elif isinstance(request, LinearUpdateIssuesCycleRequest):
                variables["update"]["cycleId"] = await self.get_id_by_number(
                    number=request.updated_cycle, target="cycles"
                )
            elif isinstance(request, LinearUpdateIssuesProjectRequest):
                variables["update"]["projectId"] = await self.get_id_by_name(
                    name=request.updated_project, target="projects"
                )
            elif isinstance(request, LinearUpdateIssuesEstimateRequest):
                variables["update"]["estimate"] = request.updated_estimate
            else:
                raise ValueError(f"Unsupported request type: {type(request)}")

            update_issue_tasks.append(asyncio.create_task(self.client.execute_async(mutation, variable_values=variables)))
            
        update_issue_results = await asyncio.gather(*update_issue_tasks) 
    
        flatten_issue_tasks = [
            asyncio.create_task(_flatten_linear_response_issue(result[mutation_name]["issue"])) for result in update_issue_results
        ]
        
        flatten_issue_results: list[LinearIssue] = await asyncio.gather(*flatten_issue_tasks)

        return flatten_issue_results

    async def delete_issues(self, request: LinearDeleteIssuesRequest) -> list[LinearIssue]:
        issues_to_delete = await self.get_issues(request=request)

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

        delete_issue_tasks = [
            asyncio.create_task(self.client.execute_async(mutation, variable_values={"id": issue.id}))
            for issue in issues_to_delete
        ]
        
        await asyncio.gather(*delete_issue_tasks)

        return issues_to_delete

    ###
    ### Helper
    ###
    async def get_id_by_name(self, name: Optional[str], target: str) -> Optional[str]:
        if not name:
            return None
        
        query = f"""
        query GetIdByName($name: String!) {{
            {target}(filter: {{ name: {{ eq: $name }} }}) {{
                nodes {{
                    id
                }}
            }}
        }}
        """

        variables = {"name": name}
        payload = {"query": query, "variables": variables}

        async with httpx.AsyncClient() as client:
            response = await client.post(LINEAR_API_URL, json=payload, headers=self.headers)

        result = response.json()
        users = result.get("data", {}).get(target, {}).get("nodes", [])

        if users:
            return users[0]["id"]
        
        return None

    async def get_id_by_number(self, number: Optional[int], target: str) -> Optional[str]:
        if not number:
            return None
        
        query = f"""
        query GetIdByNumber($number: Float!) {{
            {target}(filter: {{ number: {{ eq: $number }} }}) {{
                nodes {{
                    id
                }}
            }}
        }}
        """

        variables = {"number": number}
        payload = {"query": query, "variables": variables}

        async with httpx.AsyncClient() as client:
            response = await client.post(LINEAR_API_URL, json=payload, headers=self.headers)

        result = response.json()
        cycles = result.get("data", {}).get(target, {}).get("nodes", [])

        if cycles:
            return cycles[0]["id"]
        return None

    async def get_state_id_by_name(self, state: Optional[State]) -> Optional[str]:
        if not state:
            return None
        
        name: str = state.value
        query = """
        query GetStateIdByName {
            workflowStates {
                nodes {
                    id
                    name
                }
            }
        }
        """

        payload = {"query": query}
        async with httpx.AsyncClient() as client:
            response = await client.post(LINEAR_API_URL, json=payload, headers=self.headers)

        result = response.json()
        states = result.get("data", {}).get("workflowStates", {}).get("nodes", [])

        for workflow_state in states:
            if workflow_state["name"] == name:
                return workflow_state["id"]

        return None

    async def get_label_id_by_name(self, name: Optional[str]) -> Optional[str]:
        if not name:
            return None
        query = """
        query GetLabelIdByName($name: String!) {
            issueLabels(filter: { name: { eq: $name } }) {
                nodes {
                    id
                    name
                }
            }
        }
        """

        variables = {"name": name}
        payload = {"query": query, "variables": variables}
        async with httpx.AsyncClient() as client:
            response = await client.post(LINEAR_API_URL, json=payload, headers=self.headers)

        result = response.json()
        labels = result.get("data", {}).get("issueLabels", {}).get("nodes", [])

        if labels:
            return labels[0]["id"]

        return None

async def _flatten_linear_response_issue(issue: dict) -> LinearIssue:
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
