import uuid
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.task import Task
from app.models.time_entry import TimeEntry
from app.repositories.time_entry_repository import TimeEntryRepository


class StatsService:
    def __init__(self, session: Session, time_entries: TimeEntryRepository) -> None:
        self._session = session
        self._time_entries = time_entries

    def get_stats(self) -> dict:
        today = date.today()
        completed_count = self._completed_count()
        completed_dates = self._completed_dates(today)
        entries = self._time_entries.list_between()

        minutes_by_day = self._tally_by_day(entries)
        minutes_by_tag = self._tally_by_tag(entries)
        minutes_by_project = self._tally_by_project(entries)

        return {
            "streak": self._streak(completed_dates, today),
            "days_studied": len({e.entry_date for e in entries}),
            "tasks_completed": completed_count,
            "minutes_total": sum(e.minutes for e in entries),
            "minutes_by_day": minutes_by_day,
            "minutes_by_tag": minutes_by_tag,
            "minutes_by_project": minutes_by_project,
        }

    def _completed_count(self) -> int:
        stmt = (
            select(func.count()).select_from(Task).where(Task.completed_at.is_not(None))
        )
        return self._session.scalar(stmt) or 0

    def _completed_dates(self, today: date) -> set[date]:
        stmt = select(Task.completed_at).where(Task.completed_at.is_not(None))
        rows = self._session.scalars(stmt)
        return {self._as_local_date(dt, today) for dt in rows}

    @staticmethod
    def _as_local_date(value: datetime, today: date) -> date:
        if value.tzinfo is not None:
            value = value.astimezone().replace(tzinfo=None)
        return value.date()

    @staticmethod
    def _streak(completed_dates: set[date], today: date) -> int:
        day = today
        if day not in completed_dates:
            day = day - timedelta(days=1)
        streak = 0
        while day in completed_dates:
            streak += 1
            day -= timedelta(days=1)
        return streak

    @staticmethod
    def _tally_by_day(entries: list[TimeEntry]) -> list[dict]:
        by_day: dict[date, int] = {}
        for entry in entries:
            by_day[entry.entry_date] = by_day.get(entry.entry_date, 0) + entry.minutes
        return [
            {"date": day.isoformat(), "minutes": minutes}
            for day, minutes in sorted(by_day.items())
        ]

    def _tally_by_tag(self, entries: list[TimeEntry]) -> list[dict]:
        result: dict[uuid.UUID, dict] = {}
        ids = [e.task_id for e in entries if e.task_id]
        if not ids:
            return []
        tasks = self._tasks_with_tags(ids)
        task_by_id = {t.id: t for t in tasks}
        for entry in entries:
            task = task_by_id.get(entry.task_id)
            if task is None or not task.tags:
                continue
            for tag in task.tags:
                bucket = result.setdefault(
                    tag.id, {"tag_id": str(tag.id), "name": tag.name, "minutes": 0}
                )
                bucket["minutes"] += entry.minutes
        return sorted(result.values(), key=lambda b: b["name"])

    def _tally_by_project(self, entries: list[TimeEntry]) -> list[dict]:
        result: dict[uuid.UUID, dict] = {}
        ids = [e.task_id for e in entries if e.task_id]
        if not ids:
            return []
        tasks = self._tasks_with_tags(ids)
        task_by_id = {t.id: t for t in tasks}
        for entry in entries:
            task = task_by_id.get(entry.task_id)
            if task is None:
                continue
            project = task.project
            bucket = result.setdefault(
                project.id,
                {"project_id": str(project.id), "name": project.name, "minutes": 0},
            )
            bucket["minutes"] += entry.minutes
        return sorted(result.values(), key=lambda b: b["name"])

    def _tasks_with_tags(self, task_ids: list[uuid.UUID]) -> list[Task]:
        stmt = (
            select(Task)
            .options(selectinload(Task.tags), selectinload(Task.project))
            .where(Task.id.in_(task_ids))
        )
        return list(self._session.scalars(stmt))
