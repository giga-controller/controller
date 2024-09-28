import logging
from typing import Any

from slack_sdk.web.async_client import AsyncWebClient

from app.models.integrations.slack import (
    SlackGetChannelIdRequest,
    SlackSendMessageRequest,
)
from app.utils.levenshtein import get_most_similar_string

logging.basicConfig(level=logging.INFO)

log = logging.getLogger(__name__)


class SlackClient:
    def __init__(self, access_token: str):
        self.client = AsyncWebClient(token=access_token)

    async def get_all_channel_names(self) -> list[str]:
        response = await self.client.conversations_list()
        channels = response["channels"]
        channel_names = [channel["name"] for channel in channels]
        return channel_names
    
    async def get_all_channel_ids(
        self, request: SlackGetChannelIdRequest
    ) -> list[dict[str, Any]]:
        response = await self.client.conversations_list()
        channels = response["channels"]
        request = await self._repair_channel_names(request=request)
        
        channel_info = [
            {"channel_name": channel["name"], "channel_id": channel["id"]}
            for channel in channels
            if channel["name"]
            in request.channel_names
        ]
        return channel_info

    async def _repair_channel_names(self, request: SlackGetChannelIdRequest) -> SlackGetChannelIdRequest:
        possible_channel_names: list[str] = await self.get_all_channel_names()
        updated_channel_names: list[str] = []
        for channel_name in request.channel_names:
            updated_channel_names.append(
                get_most_similar_string(
                    target=channel_name, 
                    candidates=possible_channel_names
                )
            )
        return SlackGetChannelIdRequest(channel_names=updated_channel_names)
        
    async def send_message(self, request: SlackSendMessageRequest):
        response = await self.client.chat_postMessage(
            channel=request.channel_id, text=request.text
        )
        return response
