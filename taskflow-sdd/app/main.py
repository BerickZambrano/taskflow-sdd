from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.routes.auth import router as auth_router
from app.api.routes.projects import router as projects_router
from app.api.routes.stats import router as stats_router
from app.api.routes.tags import router as tags_router
from app.api.routes.tasks import router as tasks_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers

settings = get_settings()

app = FastAPI(title="TaskFlow")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return RedirectResponse(url=settings.frontend_url)


register_exception_handlers(app)
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(tags_router)
app.include_router(stats_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}