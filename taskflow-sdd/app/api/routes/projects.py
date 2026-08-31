import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


def _service(db: Session) -> ProjectService:
    return ProjectService(ProjectRepository(db), TaskRepository(db))


@router.get("", response_model=list[ProjectOut])
def list_projects(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list:
    return _service(db).list_for_owner(user.id)


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(
    payload: ProjectCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectOut:
    return _service(db).create(user.id, payload.name, payload.description)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectOut:
    return _service(db).get(project_id, user.id)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectOut:
    return _service(db).update(
        project_id, user.id, **payload.model_dump(exclude_unset=True)
    )


@router.delete("/{project_id}", status_code=204)
def inactivate_project(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    _service(db).inactivate(project_id, user.id)
    return Response(status_code=204)
