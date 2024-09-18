import base64
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.exceptions.exception import InferenceError
from app.models.integrations.gmail import (
    Gmail,
    GmailDeleteEmailsRequest,
    GmailFilterEmailsRequest,
    GmailMarkAsReadRequest,
    GmailSendEmailRequest,
)

TOKEN_URI = "https://oauth2.googleapis.com/token"


class GmailClient:

    def __init__(
        self, access_token: str, refresh_token: str, client_id: str, client_secret: str
    ):
        self.service = build(
            "gmail",
            "v1",
            credentials=Credentials(
                token=access_token,
                refresh_token=refresh_token,
                client_id=client_id,
                client_secret=client_secret,
                token_uri=TOKEN_URI,
            ),
        )

    def send_email(self, request: GmailSendEmailRequest) -> Gmail:
        try:
            message = MIMEText(request.body)
            message["to"] = request.recipient
            message["subject"] = request.subject
            create_message = {
                "raw": base64.urlsafe_b64encode(message.as_bytes()).decode()
            }

            sent_message = (
                self.service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            return self.get_emails(
                request=GmailFilterEmailsRequest(
                    message_ids=[sent_message["id"]], query=None
                )
            )[0]

        except Exception as e:
            raise InferenceError("Error sending email via GmailClient: %s", str(e))

    def mark_as_read(self, request: GmailMarkAsReadRequest) -> list[Gmail]:
        emails_to_update: list[Gmail] = self.get_emails(request=request)
        updated_emails: list[Gmail] = []
        for email in emails_to_update:
            self.service.users().messages().modify(
                userId="me",
                id=email.id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()
            email.labelIds.remove("UNREAD")
            updated_emails.append(email)
        return updated_emails

    def get_emails(self, request: GmailFilterEmailsRequest) -> list[Gmail]:
        try:
            gmail_lst: list[Gmail] = []

            if request.message_ids:
                for message_id in request.message_ids:
                    full_msg = (
                        self.service.users()
                        .messages()
                        .get(userId="me", id=message_id)
                        .execute()
                    )

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
                messages = (
                    self.service.users()
                    .messages()
                    .list(userId="me", q=request.query)
                    .execute()
                )

                for message in messages.get("messages", []):
                    full_msg = (
                        self.service.users()
                        .messages()
                        .get(userId="me", id=message["id"])
                        .execute()
                    )

                    headers = full_msg["payload"]["headers"]
                    gmail_lst.append(
                        Gmail(
                            id=message["id"],
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

    def delete_emails(self, request: GmailDeleteEmailsRequest) -> list[Gmail]:
        try:
            gmail_lst: list[Gmail] = self.get_emails(request=request)
            if request.message_ids:
                for message_id in request.message_ids:
                    self.service.users().messages().delete(
                        userId="me", id=message_id
                    ).execute()
            elif request.query:
                messages = (
                    self.service.users()
                    .messages()
                    .list(userId="me", q=request.query)
                    .execute()
                )
                for message in messages.get("messages", []):
                    self.service.users().messages().delete(
                        userId="me", id=message["id"]
                    ).execute()
            return gmail_lst
        except Exception as e:
            raise InferenceError("Error deleting emails via GmailClient: %s", str(e))


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
