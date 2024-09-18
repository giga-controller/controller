from pydantic import BaseModel


class SlackGetChannelIdRequest(BaseModel):
    channel_names: list[str]


class SlackSendMessageRequest(BaseModel):
    channel_id: str
    text: str
