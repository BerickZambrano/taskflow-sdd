import uuid
from unittest.mock import Mock, create_autospec

import pytest

from app.core.exceptions import ConflictError, NotFoundError
from app.models.tag import Tag
from app.models.task import Task
from app.repositories.tag_repository import TagRepository
from app.services.tag_service import TAG_COLORS, TagService

TASK_ID = uuid.uuid4()
TAG_ID = uuid.uuid4()


def _build_tag(name: str = "Estudio", tag_id: uuid.UUID = TAG_ID) -> Tag:
    tag = Tag(name=name, color=TAG_COLORS[0])
    tag.id = tag_id
    return tag


def _build_task() -> Task:
    task = Task(title="Estudiar")
    task.id = TASK_ID
    return task


def _make_service(tags=None) -> TagService:
    session = Mock()
    tags = tags or create_autospec(TagRepository)
    return TagService(session, tags)


def test_create_tag_assigns_color_auto() -> None:
    repo = create_autospec(TagRepository)
    repo.get_by_name.return_value = None
    repo.count.return_value = 0
    repo.create.return_value = _build_tag()
    service = _make_service(repo)

    tag = service.create("Estudio")

    assert tag.name == "Estudio"
    assert repo.create.call_args.args[1] == TAG_COLORS[0]
    repo.commit.assert_called_once()


def test_create_tag_cycles_colors() -> None:
    repo = create_autospec(TagRepository)
    repo.get_by_name.return_value = None
    repo.count.return_value = 2
    repo.create.return_value = _build_tag()
    service = _make_service(repo)

    service.create("Estudio")

    assert repo.create.call_args.args[1] == TAG_COLORS[2 % len(TAG_COLORS)]


def test_create_tag_rejects_duplicate() -> None:
    repo = create_autospec(TagRepository)
    repo.get_by_name.return_value = _build_tag()
    service = _make_service(repo)

    with pytest.raises(ConflictError):
        service.create("Estudio")
    repo.create.assert_not_called()


def test_delete_tag() -> None:
    repo = create_autospec(TagRepository)
    repo.get_by_id.return_value = _build_tag()
    service = _make_service(repo)

    service.delete(TAG_ID)

    repo.delete.assert_called_once()
    repo.commit.assert_called_once()


def test_delete_tag_not_found() -> None:
    repo = create_autospec(TagRepository)
    repo.get_by_id.return_value = None
    service = _make_service(repo)

    with pytest.raises(NotFoundError):
        service.delete(TAG_ID)


def test_assign_tag_to_task() -> None:
    session = Mock()
    repo = create_autospec(TagRepository)
    repo.get_by_id.return_value = _build_tag()
    session.scalar.return_value = _build_task()
    service = TagService(session, repo)

    task = service.assign_tag(TASK_ID, TAG_ID)

    assert task.id == TASK_ID
    repo.assign_tag.assert_called_once()
    repo.commit.assert_called_once()


def test_assign_tag_not_found() -> None:
    session = Mock()
    repo = create_autospec(TagRepository)
    repo.get_by_id.return_value = None
    session.scalar.return_value = _build_task()
    service = TagService(session, repo)

    with pytest.raises(NotFoundError):
        service.assign_tag(TASK_ID, TAG_ID)


def test_remove_tag_from_task() -> None:
    session = Mock()
    repo = create_autospec(TagRepository)
    repo.get_by_id.return_value = _build_tag()
    session.scalar.return_value = _build_task()
    service = TagService(session, repo)

    service.remove_tag(TASK_ID, TAG_ID)

    repo.remove_tag.assert_called_once()
    repo.commit.assert_called_once()
