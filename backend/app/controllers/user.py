import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from app.connectors.native.stores.user import User
from app.exceptions.exception import DatabaseError
from app.models.user.login import LoginRequest, LoginResponse
from app.services.user import UserService

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

router = APIRouter()


class UserController:

    def __init__(self, service: UserService):
        self.router = APIRouter()
        self.service = service
        self.setup_routes()

    def setup_routes(self):

        router = self.router

        @router.post("/login")
        async def login(input: LoginRequest) -> JSONResponse:
            try:
                user: User = await self.service.login(
                    id=input.id, name=input.name, email=input.email
                )
                return JSONResponse(
                    status_code=200,
                    content=LoginResponse(api_key=user.api_key).model_dump(),
                )
            except ValidationError as e:
                log.error("Validation error in user controller: %s", str(e))
                raise HTTPException(status_code=422, detail="Validation error") from e
            except DatabaseError as e:
                log.error("Database error in user controller: %s", str(e))
                raise HTTPException(status_code=500, detail="Database error") from e
            except Exception as e:
                log.error("Unexpected error in user controller.py: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="An unexpected error occurred"
                ) from e
