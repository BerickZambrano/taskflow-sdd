import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import ProjectStatus
from app.models.project import Project


class ProjectRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        return self._session.get(Project, project_id)

    def get_by_owner(self, owner_id: uuid.UUID) -> list[Project]:
        stmt = (
            select(Project)
            .where(Project.owner_id == owner_id)
            .order_by(Project.created_at)
        )
        return list(self._session.scalars(stmt))

    def get_by_name_for_owner(self, name: str, owner_id: uuid.UUID) -> Project | None:
        stmt = select(Project).where(
            Project.owner_id == owner_id,
            func.lower(Project.name) == name.lower(),
        )
        return self._session.scalar(stmt)

    def create(
        self,
        name: str,
        description: str | None,
        owner_id: uuid.UUID,
    ) -> Project:
        project = Project(
            name=name,
            description=description,
            owner_id=owner_id,
            status=ProjectStatus.ACTIVE,
        )
        self._session.add(project)
        self._session.flush()
        return project

    def update(
        self,
        project: Project,
        name: str,
        description: str | None,
    ) -> Project:
        project.name = name
        project.description = description
        self._session.flush()
        return project

    def commit(self) -> None:
        self._session.commit()
