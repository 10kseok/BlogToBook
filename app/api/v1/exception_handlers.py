from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

from app.api.v1.exceptions import (
    TaskException,
    InvalidRequestException,
    ConversionException,
)

logger = logging.getLogger("uvicorn")

def register_exception_handlers(app: FastAPI) -> None:
    """
    모든 예외 핸들러를 등록하는 함수
    """

    @app.exception_handler(TaskException)
    async def task_exception_handler(request: Request, exc: TaskException) -> JSONResponse:
        # 태스크 관련 모든 예외를 공통으로 처리
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(InvalidRequestException)
    async def invalid_request_handler(request: Request, exc: InvalidRequestException) -> JSONResponse:
        logger.error(f"Invalid request: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(ConversionException)
    async def conversion_exception_handler(request: Request, exc: ConversionException) -> JSONResponse:
        logger.error(f"Conversion error: {exc.detail}", exc_info=True)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred."}
        )
