from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class State(StrEnum):
    BACKLOG = "Backlog"
    TODO = "Todo"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    DONE = "Done"
    CANCELED = "Canceled"
    DUPLICATE = "Duplicate"


class Label(BaseModel):
    name: str


class Labels(BaseModel):
    nodes: list[Label]


class User(BaseModel):
    name: str


class Comment(BaseModel):
    message: str
    user: str


class Cycle(BaseModel):
    number: int


class Project(BaseModel):
    name: str


class Title(BaseModel):
    title: str


class Team(BaseModel):
    id: str
    name: str


class LinearIssue(BaseModel):
    id: Optional[str]
    number: Optional[int]
    title: Optional[str]
    description: Optional[str]
    priority: Optional[int]
    estimate: Optional[
        int
    ]  # Assume T-Shirt sizes for now, which is represented as an integer in the API
    state: Optional[State]
    assignee: Optional[str]
    creator: Optional[str]
    labels: Optional[list[str]]
    createdAt: Optional[str]  # Timezone but in string format
    updatedAt: Optional[str]  # Timezone but in string format
    dueDate: Optional[str]  # YYYY-MM-DD but in string format
    cycle: Optional[int]
    project: Optional[str]
    comments: Optional[list[Comment]]
    url: Optional[str]


class LinearCreateIssueRequest(BaseModel):
    title: Optional[str]
    description: Optional[str]
    priority: Optional[int]
    estimate: Optional[int]
    state: Optional[State]
    assignee: Optional[str]
    creator: Optional[str]
    labels: Optional[list[str]]
    dueDate: Optional[str]
    cycle: Optional[int]
    project: Optional[str]


class LinearIssueQuery(BaseModel):
    use_and_clause: bool = Field(
        description="True if ALL conditions must be met for the issue to be selected, False if ANY condition being met is sufficient"
    )
    title: Optional[list[str]]
    number: Optional[list[int]]
    state: Optional[list[State]]
    assignee: Optional[list[str]]
    creator: Optional[list[str]]
    project: Optional[list[str]]
    cycle: Optional[list[int]]
    labels: Optional[list[str]]
    estimate: Optional[list[int]]

    @model_validator(mode="after")
    def list_length_match_use_and_clause(self):
        """
        Validate that the length of the other attributes are consistent in the event use_and_clause is True
        """
        if self.use_and_clause == False:
            return self
        if self.title and len(self.title) > 1:
            raise ValueError(
                "title must have a length of 1 when use_and_clause is True"
            )
        if self.number and len(self.number) > 1:
            raise ValueError(
                "number must have a length of 1 when use_and_clause is True"
            )
        if self.state and len(self.state) > 1:
            raise ValueError(
                "state must have a length of 1 when use_and_clause is True"
            )
        if self.assignee and len(self.assignee) > 1:
            raise ValueError(
                "assignee must have a length of 1 when use_and_clause is True"
            )
        if self.creator and len(self.creator) > 1:
            raise ValueError(
                "creator must have a length of 1 when use_and_clause is True"
            )
        if self.project and len(self.project) > 1:
            raise ValueError(
                "project must have a length of 1 when use_and_clause is True"
            )
        if self.estimate and len(self.estimate) > 1:
            raise ValueError(
                "estimate must have a length of 1 when use_and_clause is True"
            )

        # labels can still be a list
        return self


class LinearFilterIssuesRequest(BaseModel):
    issue_ids: Optional[list[str]] = Field(
        description="List of issue ids to filter issues with, if any"
    )
    query: Optional[LinearIssueQuery] = Field(
        description="Query to filter issues with, if any"
    )

    # Note that we dont throw an error if both are provided, because we will just prioritise reading from the issue_ids array
    @model_validator(mode="after")
    def check_at_least_one(self):
        if not self.issue_ids and not self.query:
            raise ValueError(
                "At least one of issue_ids or filter_conditions must be provided"
            )

        return self


class LinearGetIssuesRequest(LinearFilterIssuesRequest):
    pass


class LinearDeleteIssuesRequest(LinearFilterIssuesRequest):
    pass


class LinearUpdateIssuesStateRequest(LinearFilterIssuesRequest):
    updated_state: State = Field(description="The new state to update the issues to")


class LinearUpdateIssuesAssigneeRequest(LinearFilterIssuesRequest):
    updated_assignee: str = Field(
        description="The new assignee to assign the issues to"
    )


class LinearUpdateIssuesTitleRequest(LinearFilterIssuesRequest):
    updated_title: str = Field(description="The new title to update the issues to")


class LinearUpdateIssuesDescriptionRequest(LinearFilterIssuesRequest):
    updated_description: str = Field(
        description="The new description to update the issues to"
    )


class LinearUpdateIssuesLabelsRequest(LinearFilterIssuesRequest):
    updated_labels: list[str] = Field(
        description="The new set of label names to update the issues to"
    )


class LinearUpdateIssuesCycleRequest(LinearFilterIssuesRequest):
    updated_cycle: int = Field(description="The new cycle to update the issues to")


class LinearUpdateIssuesEstimateRequest(LinearFilterIssuesRequest):
    updated_estimate: int = Field(
        description="The new estimate to update the issues to"
    )


class LinearUpdateIssuesProjectRequest(LinearFilterIssuesRequest):
    updated_project: str = Field(description="The new project to update the issues to")
