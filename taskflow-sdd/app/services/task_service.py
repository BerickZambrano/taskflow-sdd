import uuid
from datetime import date

from app.core.enums import Priority, TaskStatus
from app.core.exceptions import ConflictError, NotFoundError
from app.models.task import Task
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository

_NOT_SET = object()

_TRANSITION_ORDER = {
    TaskStatus.TODO: 0,
    TaskStatus.IN_PROGRESS: 1,
    TaskStatus.DONE: 2,
}


class TaskService:
    def __init__(
        self,
        task_repository: TaskRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._tasks = task_repository
        self._projects = project_repository

    def create(
        self,
        owner_id: uuid.UUID,
        project_id: uuid.UUID,
        title: str,
        description: str | None = None,
        priority: Priority = Priority.MEDIUM,
        due_date: date | None = None,
        assignee_id: uuid.UUID | None = None,
    ) -> Task:
        project = self._projects.get_by_id(project_id)
        if project is None or project.owner_id != owner_id:
            raise NotFoundError("El proyecto no existe.")
        task = self._tasks.create(
            project_id=project_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            assignee_id=assignee_id,
        )
        self._tasks.commit()
        return task

    def get(self, task_id: uuid.UUID, owner_id: uuid.UUID) -> Task:
        task = self._tasks.get_by_id(task_id)
        if task is None or task.project.owner_id != owner_id:
            raise NotFoundError("La tarea no existe.")
        return task

    def list(
        self,
        owner_id: uuid.UUID,
        project_id: uuid.UUID,
        status: TaskStatus | None = None,
        priority: Priority | None = None,
        sort_by: str = "priority",
        order: str = "asc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Task], int]:
        project = self._projects.get_by_id(project_id)
        if project is None or project.owner_id != owner_id:
            raise NotFoundError("El proyecto no existe.")
        return self._tasks.list_by_project(
            project_id,
            status=status,
            priority=priority,
            sort_by=sort_by,
            order=order,
            page=page,
            page_size=page_size,
        )

    def update(
        self,
        task_id: uuid.UUID,
        owner_id: uuid.UUID,
        title: object = _NOT_SET,
        description: object = _NOT_SET,
        priority: object = _NOT_SET,
        status: object = _NOT_SET,
        due_date: object = _NOT_SET,
        assignee_id: object = _NOT_SET,
    ) -> Task:
        task = self.get(task_id, owner_id)
        if task.status == TaskStatus.DONE:
            raise ConflictError("No se puede modificar una tarea completada.")
        if status is not _NOT_SET:
            self._validate_transition(task.status, status)
        if title is not _NOT_SET:
            task.title = title
        if description is not _NOT_SET:
            task.description = description
        if priority is not _NOT_SET:
            task.priority = priority
        if status is not _NOT_SET:
            task.status = status
        if due_date is not _NOT_SET:
            task.due_date = due_date
        if assignee_id is not _NOT_SET:
            task.assignee_id = assignee_id
        self._tasks.update(task)
        self._tasks.commit()
        return task

    def _validate_transition(self, current: TaskStatus, new: TaskStatus) -> None:
        if new == current:
            return
        if _TRANSITION_ORDER[new] != _TRANSITION_ORDER[current] + 1:
            raise ConflictError("No se puede retroceder el estado de la tarea.")

    def delete(self, task_id: uuid.UUID, owner_id: uuid.UUID) -> None:
        task = self.get(task_id, owner_id)
        self._tasks.delete(task)
        self._tasks.commit()
