from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code: int = 500
    default_detail: str = "Internal server error"

    def __init__(self, detail: str | None = None) -> None:
        self.detail: str = detail or self.default_detail
        super().__init__(self.detail)


class TaskNotFoundError(AppError):
    status_code = 404

    def __init__(self, task_id: int) -> None:
        super().__init__(f"Task {task_id} not found")


class AuthenticationError(AppError):
    status_code = 401
    default_detail = "Authentication failed"


class AuthRequestError(AppError):
    status_code = 400
    default_detail = "Invalid authentication request"


class AuthServiceUnavailableError(AppError):
    status_code = 502
    default_detail = "Authentication provider is unavailable"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=headers,
        )
