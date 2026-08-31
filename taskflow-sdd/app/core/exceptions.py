from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class TaskFlowError(Exception):
    status_code = 500

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(TaskFlowError):
    status_code = 404


class ConflictError(TaskFlowError):
    status_code = 409


class UnauthorizedError(TaskFlowError):
    status_code = 401


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(TaskFlowError)
    async def _handle_taskflow_error(
        request: Request, exc: TaskFlowError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )
