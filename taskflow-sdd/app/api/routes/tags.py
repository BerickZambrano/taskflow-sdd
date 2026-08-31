import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas.tag import TagCreate, TagOut, TaskTagAssign
from app.api.schemas.task import TaskOut
from app.repositories.tag_repository import TagRepository
from app.services.tag_service import TagService

router = APIRouter(tags=["tags"])


def _service(db: Session) -> TagService:
    return TagService(db, TagRepository(db))


@router.get("/tags", response_model=list[TagOut])
def list_tags(db: Session = Depends(get_db)) -> list:
    return _service(db).list()


@router.post("/tags", response_model=TagOut, status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)) -> TagOut:
    return _service(db).create(payload.name)


@router.delete("/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    _service(db).delete(tag_id)
    return Response(status_code=204)


@router.post("/tasks/{task_id}/tags", response_model=TagOut, status_code=201)
def assign_tag(
    task_id: uuid.UUID,
    payload: TaskTagAssign,
    db: Session = Depends(get_db),
) -> TagOut:
    _service(db).assign_tag(task_id, payload.tag_id)
    return TagOut.model_validate(TagRepository(db).get_by_id(payload.tag_id))


@router.delete("/tasks/{task_id}/tags/{tag_id}", response_model=TaskOut)
def remove_tag(
    task_id: uuid.UUID,
    tag_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> TaskOut:
    return _service(db).remove_tag(task_id, tag_id)
