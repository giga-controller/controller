import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.feedback import FeedbackController
from app.controllers.query import QueryController
from app.controllers.token import TokenController
from app.controllers.user import UserController
from app.middleware import LimitRequestSizeMiddleware
from app.services.feedback import FeedbackService
from app.services.query import QueryService
from app.services.token import TokenService
from app.services.user import UserService

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.add_middleware(LimitRequestSizeMiddleware, max_body_size=128 * 1024 * 1024)


def get_user_controller_router():
    service = UserService()
    return UserController(service=service).router


def get_query_controller_router():
    service = QueryService()
    return QueryController(service=service).router


def get_token_controller_router():
    service = TokenService()
    return TokenController(service=service).router


def get_feedback_controller_router():
    service = FeedbackService()
    return FeedbackController(service=service).router


app.include_router(get_user_controller_router(), tags=["user"], prefix="/api/user")
app.include_router(get_query_controller_router(), tags=["query"], prefix="/api/query")
app.include_router(get_token_controller_router(), tags=["token"], prefix="/api/token")
app.include_router(
    get_feedback_controller_router(), tags=["feedback"], prefix="/api/feedback"
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        reload=True,
        limit_concurrency=10,
        limit_max_requests=100,
    )
