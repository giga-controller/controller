from fastapi import HTTPException, status


class UsageLimitExceededError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=message)


class UnauthorizedAccess(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


class PipelineError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        )


class DatabaseError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        )


class InferenceError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        )
