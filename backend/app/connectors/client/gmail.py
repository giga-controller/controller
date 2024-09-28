import asyncio
import base64
from email.mime.text import MIMEText

import aiohttp
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.exceptions.exception import InferenceError
from app.models.integrations.gmail import (
    Gmail,
    GmailFilterEmailsRequest,
    GmailMarkAsReadRequest,
    GmailSendEmailRequest,
)

TOKEN_URI = "https://oauth2.googleapis.com/token"


class GmailClient:

    def __init__(
        self, access_token: str, refresh_token: str, client_id: str, client_secret: str
    ):
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri=TOKEN_URI,
        )
        self.service = build("gmail", "v1", credentials=self.credentials)
        self.session = aiohttp.ClientSession()
        self.base_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
        self.headers = {"Authorization": f"Bearer {access_token}"}

    async def close(self):
        await self.session.close()

    async def fetch_message(self, session, url):
        async with session.get(url, headers=self.headers) as response:
            return await response.json()

    async def send_email(self, request: GmailSendEmailRequest) -> Gmail:
        try:
            message = MIMEText(request.body)
            message["to"] = request.recipient
            message["subject"] = request.subject
            create_message = {
                "raw": base64.urlsafe_b64encode(message.as_bytes()).decode()
            }

            async with self.session.post(
                f"{self.base_url}/send",
                headers=self.headers,
                json=create_message,
            ) as response:
                response_data = await response.json()
                sent_message_id = response_data["id"]

            emails = await self.get_emails(
                request=GmailFilterEmailsRequest(
                    message_ids=[sent_message_id], query=None
                )
            )
            return emails[0]

        except Exception as e:
            raise InferenceError("Error sending email via GmailClient: %s" % str(e))

    async def mark_as_read(self, request: GmailMarkAsReadRequest) -> list[Gmail]:
        emails_to_update: list[Gmail] = await self.get_emails(request=request)
        updated_emails: list[Gmail] = []
        for email in emails_to_update:
            async with self.session.post(
                f"{self.base_url}/{email.id}/modify",
                headers=self.headers,
                json={"removeLabelIds": ["UNREAD"]},
            ) as response:
                await response.json()  # Ensure the request completes
            email.labelIds.remove("UNREAD")
            updated_emails.append(email)
        return updated_emails

    async def get_emails(self, request: GmailFilterEmailsRequest) -> list[Gmail]:
        try:
            gmail_lst: list[Gmail] = []
            async with aiohttp.ClientSession() as session:
                if request.message_ids:
                    tasks = [
                        self.fetch_message(
                            session,
                            f"https://www.googleapis.com/gmail/v1/users/me/messages/{message_id}",
                        )
                        for message_id in request.message_ids
                    ]
                    responses = await asyncio.gather(*tasks)
                    for full_msg in responses:
                        headers = full_msg["payload"]["headers"]
                        gmail_lst.append(
                            Gmail(
                                id=full_msg["id"],
                                labelIds=full_msg["labelIds"],
                                sender=next(
                                    (
                                        header["value"]
                                        for header in headers
                                        if header["name"].lower() == "from"
                                    ),
                                    "",
                                ),
                                subject=next(
                                    (
                                        header["value"]
                                        for header in headers
                                        if header["name"].lower() == "subject"
                                    ),
                                    "",
                                ),
                                body=_get_message_body(full_msg["payload"]),
                            )
                        )
                elif request.query:
                    url = f"https://www.googleapis.com/gmail/v1/users/me/messages?q={request.query}"
                    messages = await self.fetch_message(session, url)

                    tasks = [
                        self.fetch_message(
                            session,
                            f"https://www.googleapis.com/gmail/v1/users/me/messages/{message['id']}",
                        )
                        for message in messages.get("messages", [])
                    ]
                    responses = await asyncio.gather(*tasks)
                    for full_msg in responses:
                        headers = full_msg["payload"]["headers"]
                        gmail_lst.append(
                            Gmail(
                                id=full_msg["id"],
                                labelIds=full_msg["labelIds"],
                                sender=next(
                                    (
                                        header["value"]
                                        for header in headers
                                        if header["name"].lower() == "from"
                                    ),
                                    "",
                                ),
                                subject=next(
                                    (
                                        header["value"]
                                        for header in headers
                                        if header["name"].lower() == "subject"
                                    ),
                                    "",
                                ),
                                body=_get_message_body(full_msg["payload"]),
                            )
                        )
            return gmail_lst
        except Exception as e:
            print(
                f"Error getting emails via GmailClient: {e}"
            )  # Print the error for debugging
            raise InferenceError(f"Error getting emails via GmailClient: {e}")


def _get_message_body(payload):
    """
    Recursively extract the message body from the payload.
    """
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8")
            elif "parts" in part:
                return _get_message_body(part)
    elif payload["mimeType"] == "text/plain":
        data = payload["body"].get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8")
    return ""
