import aiohttp
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.exceptions.exception import InferenceError
from app.models.integrations.docs import (
    Docs,
    DocsCreateRequest,
    DocsGetRequest,
    DocsUpdateRequest,
)

TOKEN_URI = "https://oauth2.googleapis.com/token"


class GoogleDocsClient:
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
        self.service = build("docs", "v1", credentials=self.credentials)
        self.session = aiohttp.ClientSession()
        self.base_url = "https://docs.googleapis.com/v1/documents"
        self.headers = {"Authorization": f"Bearer {access_token}"}

    async def close(self):
        await self.session.close()

    async def create_document(self, request: DocsCreateRequest) -> Docs:
        try:
            async with self.session.post(
                self.base_url,
                headers=self.headers,
                json={"title": request.title},
            ) as response:
                print(response)
                document = await response.json()

            # If content is provided, update the document
            if request.content:
                async with self.session.post(
                    f"{self.base_url}/{document['documentId']}:batchUpdate",
                    headers=self.headers,
                    json={
                        "requests": [
                            {
                                "insertText": {
                                    "location": {"index": 1},
                                    "text": request.content,
                                }
                            }
                        ]
                    },
                ) as response:
                    await response.json()

            return Docs(
                id=document["documentId"],
                title=document["title"],
                content=request.content,
            )
        except HttpError as e:
            raise InferenceError(
                f"Error creating document via GoogleDocsClient: {str(e)}"
            )

    async def get_document(self, request: DocsGetRequest) -> Docs:
        try:
            async with self.session.get(
                f"{self.base_url}/{request.id}",
                headers=self.headers,
            ) as response:
                document = await response.json()
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
        except aiohttp.ClientError as error:
            raise InferenceError(
                f"Error reading document via GoogleDocsClient: {error}"
            )

    async def update_document(self, request: DocsUpdateRequest) -> Docs:
        try:
            # Get the current document content length
            current_content_length = len(
                (await self.get_document(DocsGetRequest(id=request.id))).content
            )

            # Clear the existing content
            async with self.session.post(
                f"{self.base_url}/{request.id}:batchUpdate",
                headers=self.headers,
                json={
                    "requests": [
                        {
                            "deleteContentRange": {
                                "range": {
                                    "startIndex": 1,
                                    "endIndex": current_content_length,
                                }
                            }
                        }
                    ]
                },
            ) as response:
                await response.json()

            # Insert the new content
            async with self.session.post(
                f"{self.base_url}/{request.id}:batchUpdate",
                headers=self.headers,
                json={
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
            ) as response:
                await response.json()

            return await self.get_document(DocsGetRequest(id=request.id))
        except aiohttp.ClientError as error:
            raise InferenceError(
                f"Error updating document via GoogleDocsClient: {error}"
            )
