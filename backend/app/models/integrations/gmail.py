from typing import Optional

from pydantic import BaseModel, Field, model_validator


class Gmail(BaseModel):
    id: str
    labelIds: list[str]
    sender: str
    subject: str
    body: str


class GmailEditableFields(BaseModel):
    labelIds: Optional[list[str]]


class GmailFilterEmailsRequest(BaseModel):
    message_ids: Optional[list[str]] = Field(
        description="List of message ids to filter emails with, if any"
    )
    query: Optional[str] = Field(
        description="Query to filter emails with, if message ids are unavailable"
    )

    @model_validator(mode="after")
    def check_at_least_one(self):
        if not self.message_ids and not self.query:
            raise ValueError("At least one of message_ids or query must be provided")

        return self


class GmailGetEmailsRequest(GmailFilterEmailsRequest):
    pass


class GmailDeleteEmailsRequest(GmailFilterEmailsRequest):
    pass


class GmailMarkAsReadRequest(GmailFilterEmailsRequest):
    pass


class GmailReadEmailsRequest(BaseModel):
    query: str


class GmailSendEmailRequest(BaseModel):
    recipient: str
    subject: str
    body: str
