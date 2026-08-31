from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.projects import router as projects_router
from app.api.routes.tasks import router as tasks_router
from app.core.exceptions import register_exception_handlers

app = FastAPI(title="TaskFlow")
register_exception_handlers(app)
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(tasks_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
