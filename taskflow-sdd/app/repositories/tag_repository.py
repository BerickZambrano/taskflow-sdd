import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.tag import Tag, task_tags
from app.models.task import Task


class TagRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, tag_id: uuid.UUID) -> Tag | None:
        return self._session.get(Tag, tag_id)

    def get_by_name(self, name: str) -> Tag | None:
        stmt = select(Tag).where(func.lower(Tag.name) == name.lower())
        return self._session.scalar(stmt)

    def list_all(self) -> list[Tag]:
        return list(self._session.scalars(select(Tag).order_by(Tag.name)))

    def count(self) -> int:
        return self._session.scalar(select(func.count()).select_from(Tag)) or 0

    def create(self, name: str, color: str) -> Tag:
        tag = Tag(name=name, color=color)
        self._session.add(tag)
        self._session.flush()
        return tag

    def delete(self, tag: Tag) -> None:
        self._session.delete(tag)
        self._session.flush()

    def assigned_tags(self, task: Task) -> list[Tag]:
        stmt = (
            select(Tag)
            .join(task_tags, task_tags.c.tag_id == Tag.id)
            .where(task_tags.c.task_id == task.id)
            .order_by(Tag.name)
        )
        return list(self._session.scalars(stmt))

    def assign_tag(self, task: Task, tag: Tag) -> None:
        if tag not in task.tags:
            task.tags.append(tag)
        self._session.flush()

    def remove_tag(self, task: Task, tag: Tag) -> None:
        if tag in task.tags:
            task.tags.remove(tag)
        self._session.flush()

    def commit(self) -> None:
        self._session.commit()
