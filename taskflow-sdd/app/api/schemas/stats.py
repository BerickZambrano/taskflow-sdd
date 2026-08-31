import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class TimeEntryCreate(BaseModel):
    task_id: uuid.UUID | None = None
    minutes: int = Field(gt=0, le=1440)
    entry_date: date | None = None


class TimeEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_id: uuid.UUID | None
    minutes: int
    entry_date: date
    created_at: datetime


class MinutesByDay(BaseModel):
    date: str
    minutes: int


class MinutesByTag(BaseModel):
    tag_id: str
    name: str
    minutes: int


class MinutesByProject(BaseModel):
    project_id: str
    name: str
    minutes: int


class StatsOut(BaseModel):
    streak: int
    days_studied: int
    tasks_completed: int
    minutes_total: int
    minutes_by_day: list[MinutesByDay]
    minutes_by_tag: list[MinutesByTag]
    minutes_by_project: list[MinutesByProject]
