import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from app.models.query.confirm import ConfirmRequest
from app.models.query.base import QueryRequest, QueryResponse
from app.services.query import QueryService

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

router = APIRouter()


class QueryController:

    def __init__(self, service: QueryService):
        self.router = APIRouter()
        self.service = service
        self.setup_routes()

    def setup_routes(self):

        router = self.router

        @router.post("")
        async def query(request: Request) -> JSONResponse:
            input = QueryRequest.model_validate(await request.json())
            try:
                response: QueryResponse = await self.service.query(
                    message=input.message,
                    chat_history=input.chat_history,
                    api_key=input.api_key,
                    integrations=input.integrations,
                    instance=input.instance,
                    enable_verification=input.enable_verification,
                )
                return JSONResponse(
                    status_code=200,
                    content=response.model_dump(),
                )
            except ValidationError as e:
                log.error(
                    "Validation error in query controller for general query endpoint: %s",
                    str(e),
                )
                raise HTTPException(status_code=422, detail="Validation error") from e
            except Exception as e:
                log.error(
                    "Unexpected error in query controller for general query endpoint: %s",
                    str(e),
                )
                raise HTTPException(
                    status_code=500,
                    detail="An unexpected error occurred in query controller for general query endpoint",
                ) from e

        @router.post("/confirm")
        async def confirm(input: ConfirmRequest) -> JSONResponse:
            try:
                response: QueryResponse = await self.service.confirm(
                    chat_history=input.chat_history,
                    api_key=input.api_key,
                    enable_verification=input.enable_verification,
                    integrations=input.integrations,
                    function_to_verify=input.function_to_verify,
                    instance=input.instance,
                )

                return JSONResponse(
                    status_code=200,
                    content=response.model_dump(),
                )
            except ValidationError as e:
                log.error(
                    "Validation error in query controller for general query endpoint: %s",
                    str(e),
                )
                raise HTTPException(status_code=422, detail="Validation error") from e
            except Exception as e:
                log.error(
                    "Unexpected error in query controller for general query endpoint: %s",
                    str(e),
                )
                raise HTTPException(
                    status_code=500,
                    detail="An unexpected error occurred in query controller for general query endpoint",
                ) from e


# @router.post("/linear")
# async def query_linear(input: QueryRequest) -> JSONResponse:
#     try:
#         response: list[BaseModel] = await self.service.query_linear(
#             chat_history=input.chat_history,
#             api_key=input.api_key,
#         )
#         return JSONResponse(
#             status_code=200,
#             content=[result.model_dump() for result in response],
#         )
#     except ValidationError as e:
#         log.error(
#             "Validation error in query controller for linear endpoint", str(e)
#         )
#         raise HTTPException(status_code=422, detail="Validation error") from e
#     except Exception as e:
#         log.error(
#             "Unexpected error in query controller for linear endpoint: %s",
#             str(e),
#         )
#         raise HTTPException(
#             status_code=500,
#             detail="An unexpected error occurred in query controller for linear endpoint",
#         ) from e

# @router.post("/gmail")
# async def query_gmail(input: QueryRequest) -> JSONResponse:
#     try:
#         response: list[BaseModel] = await self.service.query_gmail(
#             chat_history=input.chat_history,
#             api_key=input.api_key,
#         )
#         return JSONResponse(
#             status_code=200,
#             content=[result.model_dump() for result in response],
#         )
#     except ValidationError as e:
#         log.error(
#             "Validation error in query controller for gmail endpoint: %s",
#             str(e),
#         )
#         raise HTTPException(status_code=422, detail="Validation error") from e
#     except Exception as e:
#         log.error(
#             "Unexpected error in query controller for gmail endpoint: %s",
#             str(e),
#         )
#         raise HTTPException(
#             status_code=500,
#             detail="An unexpected error occurred in query controller for gmail endpoint",
#         ) from e
