import uuid
from typing import Literal

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.schemas.task import TaskCreate, TaskListOut, TaskOut, TaskUpdate
from app.core.enums import Priority, TaskStatus
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskService

router = APIRouter(tags=["tasks"])


def _service(db: Session) -> TaskService:
    return TaskService(TaskRepository(db), ProjectRepository(db))


@router.post("/projects/{project_id}/tasks", response_model=TaskOut, status_code=201)
def create_task(
    project_id: uuid.UUID,
    payload: TaskCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskOut:
    return _service(db).create(
        owner_id=user.id,
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        due_date=payload.due_date,
        assignee_id=payload.assignee_id,
    )


@router.get("/projects/{project_id}/tasks", response_model=TaskListOut)
def list_tasks(
    project_id: uuid.UUID,
    status: TaskStatus | None = None,
    priority: Priority | None = None,
    tag_id: uuid.UUID | None = None,
    sort_by: Literal["priority", "due_date"] = "priority",
    order: Literal["asc", "desc"] = "asc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskListOut:
    items, total = _service(db).list(
        owner_id=user.id,
        project_id=project_id,
        status=status,
        priority=priority,
        tag_id=tag_id,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
    )
    return TaskListOut(items=items, total=total, page=page, page_size=page_size)


@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(
    task_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskOut:
    return _service(db).get(task_id, user.id)


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: uuid.UUID,
    payload: TaskUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskOut:
    return _service(db).update(
        task_id, user.id, **payload.model_dump(exclude_unset=True)
    )


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    _service(db).delete(task_id, user.id)
    return Response(status_code=204)
