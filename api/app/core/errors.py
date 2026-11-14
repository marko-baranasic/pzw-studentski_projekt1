from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

HTTP_CODES = {
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
}


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message},
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    first = exc.errors()[0]
    field = ".".join(str(part) for part in first["loc"])
    return JSONResponse(
        status_code=422,
        content={"code": "validation_error", "message": f"{field}: {first['msg']}"},
    )


async def http_error_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    code = HTTP_CODES.get(exc.status_code, "http_error")
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": code, "message": str(exc.detail)},
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
