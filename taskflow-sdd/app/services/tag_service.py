import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import ConflictError, NotFoundError
from app.models.tag import Tag
from app.models.task import Task
from app.repositories.tag_repository import TagRepository

TAG_COLORS = [
    "#C4553A",
    "#4A7C59",
    "#C08A2D",
    "#5B7FA6",
    "#8A5BA6",
    "#A65261",
    "#4E8A8A",
]


class TagService:
    def __init__(
        self,
        session: Session,
        tag_repository: TagRepository,
    ) -> None:
        self._session = session
        self._tags = tag_repository

    def list(self) -> list[Tag]:
        return self._tags.list_all()

    def create(self, name: str) -> Tag:
        if self._tags.get_by_name(name) is not None:
            raise ConflictError("Ya existe una etiqueta con ese nombre.")
        color = TAG_COLORS[self._tags.count() % len(TAG_COLORS)]
        tag = self._tags.create(name, color)
        self._tags.commit()
        return tag

    def delete(self, tag_id: uuid.UUID) -> None:
        tag = self._tags.get_by_id(tag_id)
        if tag is None:
            raise NotFoundError("La etiqueta no existe.")
        self._tags.delete(tag)
        self._tags.commit()

    def assign_tag(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> Task:
        task = self._load_task_with_tags(task_id)
        tag = self._tags.get_by_id(tag_id)
        if tag is None:
            raise NotFoundError("La etiqueta no existe.")
        self._tags.assign_tag(task, tag)
        self._tags.commit()
        return task

    def remove_tag(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> Task:
        task = self._load_task_with_tags(task_id)
        tag = self._tags.get_by_id(tag_id)
        if tag is None:
            raise NotFoundError("La etiqueta no existe.")
        self._tags.remove_tag(task, tag)
        self._tags.commit()
        return task

    def _load_task_with_tags(self, task_id: uuid.UUID) -> Task:
        stmt = select(Task).options(selectinload(Task.tags)).where(Task.id == task_id)
        task = self._session.scalar(stmt)
        if task is None:
            raise NotFoundError("La tarea no existe.")
        return task
