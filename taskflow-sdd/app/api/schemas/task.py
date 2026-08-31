import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import Priority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    priority: Priority = Priority.MEDIUM
    due_date: date | None = None
    assignee_id: uuid.UUID | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    priority: Priority | None = None
    status: TaskStatus | None = None
    due_date: date | None = None
    assignee_id: uuid.UUID | None = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    priority: Priority
    status: TaskStatus
    due_date: date | None
    assignee_id: uuid.UUID | None
    project_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TaskListOut(BaseModel):
    items: list[TaskOut]
    total: int
    page: int
    page_size: int
