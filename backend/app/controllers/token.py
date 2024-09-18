import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.connectors.native.stores.token import Token
from app.exceptions.exception import DatabaseError
from app.models.token import TokenGetResponse, TokenPostRequest
from app.services.token import TokenService

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

router = APIRouter()


class TokenController:

    def __init__(self, service: TokenService):
        self.router = APIRouter()
        self.service = service
        self.setup_routes()

    def setup_routes(self):

        router = self.router

        @router.post("")
        async def authenticate(input: TokenPostRequest) -> JSONResponse:
            try:
                result: Optional[Token] = await self.service.get(
                    api_key=input.api_key, table_name=input.table_name
                )
                if result:
                    await self.service.update(
                        id=result.id,
                        access_token=input.access_token,
                        refresh_token=input.refresh_token,
                        client_id=input.client_id,
                        client_secret=input.client_secret,
                        table_name=input.table_name,
                    )
                else:
                    await self.service.post(
                        api_key=input.api_key,
                        access_token=input.access_token,
                        refresh_token=input.refresh_token,
                        client_id=input.client_id,
                        client_secret=input.client_secret,
                        table_name=input.table_name,
                    )
                return JSONResponse(
                    status_code=200,
                    content={"message": "Token stored successfully"},
                )
            except ValidationError as e:
                log.error("Validation error in token controller: %s", str(e))
                raise HTTPException(status_code=422, detail="Validation error") from e
            except DatabaseError as e:
                log.error("Database error in token controller: %s", str(e))
                raise HTTPException(status_code=500, detail="Database error") from e
            except Exception as e:
                log.error("Unexpected error in token controller.py: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="An unexpected error occurred"
                ) from e

        @router.get("")
        async def check_auth(api_key: str, table_name: str) -> JSONResponse:
            try:
                result: Optional[Token] = await self.service.get(
                    api_key=api_key, table_name=table_name
                )
                if result:
                    return JSONResponse(
                        status_code=200,
                        content=TokenGetResponse(is_authenticated=True).model_dump(),
                    )
                return JSONResponse(
                    status_code=200,
                    content=TokenGetResponse(is_authenticated=False).model_dump(),
                )
            except ValidationError as e:
                log.error("Validation error in token controller: %s", str(e))
                raise HTTPException(status_code=422, detail="Validation error") from e
            except DatabaseError as e:
                log.error("Database error in token controller: %s", str(e))
                raise HTTPException(status_code=500, detail="Database error") from e
            except Exception as e:
                log.error("Unexpected error in token controller.py: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="An unexpected error occurred"
                ) from e
