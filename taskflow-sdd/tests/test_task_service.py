import uuid
from unittest.mock import create_autospec

import pytest

from app.core.enums import Priority, TaskStatus
from app.core.exceptions import ConflictError, NotFoundError
from app.models.project import Project
from app.models.task import Task
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskService

OWNER_ID = uuid.uuid4()
OTHER_ID = uuid.uuid4()
PROJECT_ID = uuid.uuid4()
TASK_ID = uuid.uuid4()


def _build_project(owner_id: uuid.UUID = OWNER_ID) -> Project:
    project = Project(name="Lanzamiento", owner_id=owner_id)
    project.id = PROJECT_ID
    return project


def _build_task(
    task_id: uuid.UUID = TASK_ID,
    owner_id: uuid.UUID = OWNER_ID,
    status: TaskStatus = TaskStatus.TODO,
) -> Task:
    task = Task(title="Tarea", project_id=PROJECT_ID, status=status)
    task.id = task_id
    task.project = _build_project(owner_id)
    return task


def _make_service(tasks=None, projects=None) -> TaskService:
    return TaskService(
        tasks or create_autospec(TaskRepository),
        projects or create_autospec(ProjectRepository),
    )


def test_create_success_with_defaults() -> None:
    tasks = create_autospec(TaskRepository)
    projects = create_autospec(ProjectRepository)
    projects.get_by_id.return_value = _build_project()
    tasks.create.return_value = _build_task()
    service = TaskService(tasks, projects)

    task = service.create(OWNER_ID, PROJECT_ID, "Tarea")

    assert task.title == "Tarea"
    tasks.create.assert_called_once()
    assert tasks.create.call_args.kwargs["priority"] == Priority.MEDIUM
    tasks.commit.assert_called_once()


def test_create_rejects_nonexistent_project() -> None:
    tasks = create_autospec(TaskRepository)
    projects = create_autospec(ProjectRepository)
    projects.get_by_id.return_value = None
    service = TaskService(tasks, projects)

    with pytest.raises(NotFoundError):
        service.create(OWNER_ID, PROJECT_ID, "Tarea")
    tasks.create.assert_not_called()


def test_create_rejects_other_owners_project() -> None:
    tasks = create_autospec(TaskRepository)
    projects = create_autospec(ProjectRepository)
    projects.get_by_id.return_value = _build_project(owner_id=OTHER_ID)
    service = TaskService(tasks, projects)

    with pytest.raises(NotFoundError):
        service.create(OWNER_ID, PROJECT_ID, "Tarea")


def test_get_returns_task() -> None:
    tasks = create_autospec(TaskRepository)
    tasks.get_by_id.return_value = _build_task()
    service = _make_service(tasks=tasks)

    task = service.get(TASK_ID, OWNER_ID)

    assert task.id == TASK_ID


def test_get_rejects_nonexistent_task() -> None:
    tasks = create_autospec(TaskRepository)
    tasks.get_by_id.return_value = None
    service = _make_service(tasks=tasks)

    with pytest.raises(NotFoundError):
        service.get(TASK_ID, OWNER_ID)


def test_get_rejects_other_owners_task() -> None:
    tasks = create_autospec(TaskRepository)
    tasks.get_by_id.return_value = _build_task(owner_id=OTHER_ID)
    service = _make_service(tasks=tasks)

    with pytest.raises(NotFoundError):
        service.get(TASK_ID, OWNER_ID)


def test_update_success() -> None:
    tasks = create_autospec(TaskRepository)
    tasks.get_by_id.return_value = _build_task()
    service = _make_service(tasks=tasks)

    task = service.update(TASK_ID, OWNER_ID, title="Nuevo título")

    assert task.title == "Nuevo título"
    tasks.commit.assert_called_once()


def test_update_blocked_when_done() -> None:
    tasks = create_autospec(TaskRepository)
    tasks.get_by_id.return_value = _build_task(status=TaskStatus.DONE)
    service = _make_service(tasks=tasks)

    with pytest.raises(ConflictError):
        service.update(TASK_ID, OWNER_ID, title="Nuevo título")


def test_update_valid_forward_transition() -> None:
    tasks = create_autospec(TaskRepository)
    tasks.get_by_id.return_value = _build_task(status=TaskStatus.TODO)
    service = _make_service(tasks=tasks)

    task = service.update(TASK_ID, OWNER_ID, status=TaskStatus.IN_PROGRESS)

    assert task.status == TaskStatus.IN_PROGRESS


def test_update_rejects_backward_transition() -> None:
    tasks = create_autospec(TaskRepository)
    tasks.get_by_id.return_value = _build_task(status=TaskStatus.IN_PROGRESS)
    service = _make_service(tasks=tasks)

    with pytest.raises(ConflictError):
        service.update(TASK_ID, OWNER_ID, status=TaskStatus.TODO)


def test_update_rejects_jump_forward_transition() -> None:
    tasks = create_autospec(TaskRepository)
    tasks.get_by_id.return_value = _build_task(status=TaskStatus.TODO)
    service = _make_service(tasks=tasks)

    with pytest.raises(ConflictError):
        service.update(TASK_ID, OWNER_ID, status=TaskStatus.DONE)


def test_list_delegates_to_repository() -> None:
    tasks = create_autospec(TaskRepository)
    projects = create_autospec(ProjectRepository)
    projects.get_by_id.return_value = _build_project()
    tasks.list_by_project.return_value = ([_build_task()], 1)
    service = TaskService(tasks, projects)

    items, total = service.list(OWNER_ID, PROJECT_ID, status=TaskStatus.DONE)

    assert total == 1
    tasks.list_by_project.assert_called_once()


def test_list_rejects_nonexistent_project() -> None:
    tasks = create_autospec(TaskRepository)
    projects = create_autospec(ProjectRepository)
    projects.get_by_id.return_value = None
    service = TaskService(tasks, projects)

    with pytest.raises(NotFoundError):
        service.list(OWNER_ID, PROJECT_ID)


def test_delete_removes_task() -> None:
    tasks = create_autospec(TaskRepository)
    tasks.get_by_id.return_value = _build_task()
    service = _make_service(tasks=tasks)

    service.delete(TASK_ID, OWNER_ID)

    tasks.delete.assert_called_once()
    tasks.commit.assert_called_once()
