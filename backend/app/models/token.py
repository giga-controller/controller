from typing import Optional

from pydantic import BaseModel


class TokenPostRequest(BaseModel):
    api_key: str
    access_token: str
    refresh_token: Optional[str]
    client_id: str
    client_secret: str
    table_name: str


class TokenGetRequest(BaseModel):
    api_key: str
    table_name: str


class TokenGetResponse(BaseModel):
    is_authenticated: bool
