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

# Normalizar la URL del frontend eliminando comillas, espacios o barras al final
frontend_url = settings.frontend_url.strip().strip("'\"").rstrip("/")

origins = [
    frontend_url,
    "https://taskflow-sdd.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]

# Eliminar duplicados manteniendo el orden
origins = list(dict.fromkeys(origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://taskflow-sdd-.*-beritozambrano-2391s-projects\.vercel\.app",
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