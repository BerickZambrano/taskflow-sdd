import uuid

from app.core.enums import ProjectStatus
from app.core.exceptions import ConflictError, NotFoundError
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository

_NOT_SET = object()


class ProjectService:
    def __init__(self, project_repository: ProjectRepository, task_repository) -> None:
        self._projects = project_repository
        self._tasks = task_repository

    def create(
        self, owner_id: uuid.UUID, name: str, description: str | None
    ) -> Project:
        if self._projects.get_by_name_for_owner(name, owner_id) is not None:
            raise ConflictError("Ya existe un proyecto con ese nombre.")
        project = self._projects.create(name, description, owner_id)
        self._projects.commit()
        return project

    def list_for_owner(self, owner_id: uuid.UUID) -> list[Project]:
        return self._projects.get_by_owner(owner_id)

    def get(self, project_id: uuid.UUID, owner_id: uuid.UUID) -> Project:
        project = self._projects.get_by_id(project_id)
        if project is None or project.owner_id != owner_id:
            raise NotFoundError("El proyecto no existe.")
        return project

    def update(
        self,
        project_id: uuid.UUID,
        owner_id: uuid.UUID,
        name: object = _NOT_SET,
        description: object = _NOT_SET,
    ) -> Project:
        project = self.get(project_id, owner_id)
        new_name = project.name if name is _NOT_SET else name
        if name is not _NOT_SET:
            existing = self._projects.get_by_name_for_owner(new_name, owner_id)
            if existing is not None and existing.id != project.id:
                raise ConflictError("Ya existe un proyecto con ese nombre.")
        new_description = (
            project.description if description is _NOT_SET else description
        )
        project = self._projects.update(project, new_name, new_description)
        self._projects.commit()
        return project

    def inactivate(self, project_id: uuid.UUID, owner_id: uuid.UUID) -> Project:
        project = self.get(project_id, owner_id)
        if project.status == ProjectStatus.INACTIVE:
            return project
        if self._tasks.has_incomplete(project_id):
            raise ConflictError(
                "Todas las tareas deben estar completadas para inactivar el proyecto."
            )
        project.status = ProjectStatus.INACTIVE
        self._projects.commit()
        return project
