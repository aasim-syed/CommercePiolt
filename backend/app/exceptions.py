# backend/app/exceptions.py

from fastapi import HTTPException


class PineLabsAPIError(Exception):
    """Raised when Pine Labs API fails."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ToolValidationError(Exception):
    """Raised when tool arguments are invalid."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class AgentExecutionError(Exception):
    """Raised when agent fails to complete a request."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def http_error(message: str, status_code: int = 400) -> HTTPException:
    return HTTPException(status_code=status_code, detail=message)