from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class LimitRequestSizeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_body_size: int):
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next):
        if request.headers.get("content-length"):
            content_length = int(request.headers["content-length"])
            if content_length > self.max_body_size:
                raise HTTPException(status_code=413, detail="Request body too large")
        return await call_next(request)
