from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.exceptions.exception import InferenceError
from app.models.integrations.docs import (
    Docs,
    DocsCreateRequest,
    DocsDeleteRequest,
    DocsGetRequest,
    DocsUpdateRequest,
)

TOKEN_URI = "https://oauth2.googleapis.com/token"


class GoogleDocsClient:
    def __init__(
        self, access_token: str, refresh_token: str, client_id: str, client_secret: str
    ):
        self.service = build(
            "docs",
            "v1",
            credentials=Credentials(
                token=access_token,
                refresh_token=refresh_token,
                client_id=client_id,
                client_secret=client_secret,
                token_uri=TOKEN_URI,
            ),
        )

    def create_document(self, request: DocsCreateRequest) -> Docs:
        try:
            document = (
                self.service.documents().create(body={"title": request.title}).execute()
            )

            # If content is provided, update the document
            if request.content:
                self.service.documents().batchUpdate(
                    documentId=document["documentId"],
                    body={
                        "requests": [
                            {
                                "insertText": {
                                    "location": {
                                        "index": 1,
                                    },
                                    "text": request.content,
                                }
                            }
                        ]
                    },
                ).execute()

            return Docs(
                id=document["documentId"],
                title=document["title"],
                content=request.content,
            )
        except HttpError as error:
            raise InferenceError(
                f"Error creating document via GoogleDocsClient: {error}"
            )

    def get_document(self, request: DocsGetRequest) -> Docs:
        try:
            document = self.service.documents().get(documentId=request.id).execute()
            content = document.get("body", {}).get("content", [])
            full_content = ""
            for element in content:
                if "paragraph" in element:
                    for par_element in element["paragraph"]["elements"]:
                        if "textRun" in par_element:
                            full_content += par_element["textRun"]["content"]

            return Docs(
                id=document["documentId"], title=document["title"], content=full_content
            )
        except HttpError as error:
            raise InferenceError(
                f"Error reading document via GoogleDocsClient: {error}"
            )

    def update_document(self, request: DocsUpdateRequest) -> Docs:
        try:
            # Get the current document content length
            current_content_length = len(self.get_document(DocsGetRequest(id=request.id)).content)
        
            # Clear the existing content (tentative for now)
            self.service.documents().batchUpdate(
                documentId=request.id,
                body={
                    "requests": [
                        {
                            "deleteContentRange": {
                                "range": {
                                    "startIndex": 1,
                                    "endIndex": current_content_length,  # Exclude the newline character
                                }
                            }
                        }
                    ]
                },
            ).execute()
            
            # Insert the new content
            self.service.documents().batchUpdate(
                documentId=request.id,
                body={
                    "requests": [
                        {
                            "insertText": {
                                "location": {
                                    "index": 1,
                                },
                                "text": request.updated_content,
                            }
                        }
                    ]
                },
            ).execute()

            return self.get_document(DocsGetRequest(id=request.id))
        except HttpError as error:
            raise InferenceError(
                f"Error updating document via GoogleDocsClient: {error}"
            )
