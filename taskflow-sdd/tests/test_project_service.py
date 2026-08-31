import uuid
from unittest.mock import Mock, create_autospec

import pytest

from app.core.enums import ProjectStatus
from app.core.exceptions import ConflictError, NotFoundError
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.services.project_service import ProjectService

OWNER_ID = uuid.uuid4()
PROJECT_ID = uuid.uuid4()


def _build_project(
    project_id: uuid.UUID = PROJECT_ID,
    name: str = "Lanzamiento",
    owner_id: uuid.UUID = OWNER_ID,
    status: ProjectStatus = ProjectStatus.ACTIVE,
) -> Project:
    project = Project(name=name, description=None, owner_id=owner_id, status=status)
    project.id = project_id
    return project


def _make_service(
    projects: ProjectRepository,
    tasks=None,
) -> ProjectService:
    return ProjectService(projects, tasks)


def test_create_success() -> None:
    repo = create_autospec(ProjectRepository)
    repo.get_by_name_for_owner.return_value = None
    repo.create.return_value = _build_project()
    service = _make_service(repo)

    project = service.create(OWNER_ID, "Lanzamiento", "Descripción")

    assert project.name == "Lanzamiento"
    repo.create.assert_called_once()
    repo.commit.assert_called_once()


def test_create_rejects_duplicate_name() -> None:
    repo = create_autospec(ProjectRepository)
    repo.get_by_name_for_owner.return_value = _build_project()
    service = _make_service(repo)

    with pytest.raises(ConflictError):
        service.create(OWNER_ID, "lanzamiento", None)
    repo.create.assert_not_called()


def test_list_returns_owner_projects() -> None:
    repo = create_autospec(ProjectRepository)
    repo.get_by_owner.return_value = [_build_project()]
    service = _make_service(repo)

    projects = service.list_for_owner(OWNER_ID)

    assert len(projects) == 1


def test_get_returns_project() -> None:
    repo = create_autospec(ProjectRepository)
    repo.get_by_id.return_value = _build_project()
    service = _make_service(repo)

    project = service.get(PROJECT_ID, OWNER_ID)

    assert project.id == PROJECT_ID


def test_get_not_found() -> None:
    repo = create_autospec(ProjectRepository)
    repo.get_by_id.return_value = None
    service = _make_service(repo)

    with pytest.raises(NotFoundError):
        service.get(PROJECT_ID, OWNER_ID)


def test_get_rejects_other_owner() -> None:
    repo = create_autospec(ProjectRepository)
    repo.get_by_id.return_value = _build_project(owner_id=uuid.uuid4())
    service = _make_service(repo)

    with pytest.raises(NotFoundError):
        service.get(PROJECT_ID, OWNER_ID)


def test_update_success() -> None:
    repo = create_autospec(ProjectRepository)
    repo.get_by_id.return_value = _build_project()
    repo.get_by_name_for_owner.return_value = None
    repo.update.return_value = _build_project(name="Renombrado")
    service = _make_service(repo)

    project = service.update(PROJECT_ID, OWNER_ID, name="Renombrado")

    assert project.name == "Renombrado"
    repo.commit.assert_called_once()


def test_update_rejects_duplicate_name_of_another_project() -> None:
    repo = create_autospec(ProjectRepository)
    repo.get_by_id.return_value = _build_project()
    repo.get_by_name_for_owner.return_value = _build_project(
        project_id=uuid.uuid4(), name="Renombrado"
    )
    service = _make_service(repo)

    with pytest.raises(ConflictError):
        service.update(PROJECT_ID, OWNER_ID, name="Renombrado")


def test_inactivate_blocks_with_incomplete_tasks() -> None:
    repo = create_autospec(ProjectRepository)
    repo.get_by_id.return_value = _build_project()
    tasks = Mock()
    tasks.has_incomplete.return_value = True
    service = _make_service(repo, tasks)

    with pytest.raises(ConflictError):
        service.inactivate(PROJECT_ID, OWNER_ID)


def test_inactivate_success_when_all_tasks_done() -> None:
    repo = create_autospec(ProjectRepository)
    repo.get_by_id.return_value = _build_project()
    tasks = Mock()
    tasks.has_incomplete.return_value = False
    service = _make_service(repo, tasks)

    project = service.inactivate(PROJECT_ID, OWNER_ID)

    assert project.status == ProjectStatus.INACTIVE
    repo.commit.assert_called_once()
