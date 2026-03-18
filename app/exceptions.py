"""Custom exceptions to handle the errors that may happen in the use"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# Custom exception classes

class InvalidFileError(Exception):
    """Raised when the uploaded file type is not supported."""

    def __init__(self, detail: str = "Invalid or unsupported file type."):
        self.detail = detail


class FileTooLargeError(Exception):
    """Raised when the uploaded file exceeds the size limit."""

    def __init__(self, detail: str = "File exceeds the maximum allowed size."):
        self.detail = detail


class ConversionError(Exception):
    """Raised when a file conversion fails."""

    def __init__(self, detail: str = "An error occurred during conversion."):
        self.detail = detail


# Handler registration

def register_exception_handlers(app: FastAPI) -> None:
    """Attach custom exception handlers to the FastAPI app."""

    @app.exception_handler(InvalidFileError)
    async def invalid_file_handler(_request: Request, exc: InvalidFileError):
        return JSONResponse(status_code=400, content={"detail": exc.detail})

    @app.exception_handler(FileTooLargeError)
    async def file_too_large_handler(_request: Request, exc: FileTooLargeError):
        return JSONResponse(status_code=413, content={"detail": exc.detail})

    @app.exception_handler(ConversionError)
    async def conversion_error_handler(_request: Request, exc: ConversionError):
        return JSONResponse(status_code=422, content={"detail": exc.detail})
