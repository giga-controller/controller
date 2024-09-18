import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.exceptions.exception import DatabaseError
from app.models.feedback import FeedbackRequest
from app.services.feedback import FeedbackService

log = logging.getLogger(__name__)

router = APIRouter()


class FeedbackController:

    def __init__(self, service: FeedbackService):
        self.router = APIRouter()
        self.service = service
        self.setup_routes()

    def setup_routes(self):
        router = self.router

        @router.post("")
        async def post(input: FeedbackRequest) -> JSONResponse:
            try:
                await self.service.post(
                    id=input.id,
                    feedback=input.feedback,
                )
            except ValidationError as e:
                log.error("Validation error in feedback controller: %s", str(e))
                raise HTTPException(status_code=422, detail="Validation error") from e
            except DatabaseError as e:
                log.error("Database error in feedback controller: %s", str(e))
                raise HTTPException(status_code=500, detail="Database error") from e
            except Exception as e:
                log.error("Unexpected error in feedback controller.py: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="An unexpected error occurred"
                ) from e
