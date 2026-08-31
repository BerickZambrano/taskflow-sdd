import uuid
from datetime import date

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.core.enums import Priority, TaskStatus
from app.models.task import Task


class TaskRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, task_id: uuid.UUID) -> Task | None:
        return self._session.get(Task, task_id)

    def has_incomplete(self, project_id: uuid.UUID) -> bool:
        stmt = (
            select(Task.id)
            .where(Task.project_id == project_id, Task.status != TaskStatus.DONE)
            .limit(1)
        )
        return self._session.scalar(stmt) is not None

    def list_by_project(
        self,
        project_id: uuid.UUID,
        status: TaskStatus | None = None,
        priority: Priority | None = None,
        sort_by: str = "priority",
        order: str = "asc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Task], int]:
        filters = [Task.project_id == project_id]
        if status is not None:
            filters.append(Task.status == status)
        if priority is not None:
            filters.append(Task.priority == priority)

        count_stmt = select(func.count()).select_from(Task).where(*filters)
        total = self._session.scalar(count_stmt) or 0

        ordering: list[object]
        if sort_by == "due_date":
            column = Task.due_date.asc() if order == "asc" else Task.due_date.desc()
            ordering = [Task.due_date.is_(None), column]
        else:
            priority_rank = case(
                (Task.priority == Priority.LOW, 0),
                (Task.priority == Priority.MEDIUM, 1),
                (Task.priority == Priority.HIGH, 2),
                else_=1,
            )
            column = priority_rank.asc() if order == "asc" else priority_rank.desc()
            ordering = [column]

        stmt = (
            select(Task)
            .where(*filters)
            .order_by(*ordering)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self._session.scalars(stmt))
        return items, total

    def create(
        self,
        project_id: uuid.UUID,
        title: str,
        description: str | None = None,
        priority: Priority = Priority.MEDIUM,
        due_date: date | None = None,
        assignee_id: uuid.UUID | None = None,
    ) -> Task:
        task = Task(
            project_id=project_id,
            title=title,
            description=description,
            priority=priority,
            status=TaskStatus.TODO,
            due_date=due_date,
            assignee_id=assignee_id,
        )
        self._session.add(task)
        self._session.flush()
        return task

    def update(self, task: Task) -> Task:
        self._session.flush()
        return task

    def delete(self, task: Task) -> None:
        self._session.delete(task)
        self._session.flush()

    def commit(self) -> None:
        self._session.commit()
