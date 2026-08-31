import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.time_entry import TimeEntry


class TimeEntryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        minutes: int,
        entry_date: date,
        task_id: uuid.UUID | None = None,
    ) -> TimeEntry:
        entry = TimeEntry(minutes=minutes, entry_date=entry_date, task_id=task_id)
        self._session.add(entry)
        self._session.flush()
        return entry

    def list_between(
        self, start: date | None = None, end: date | None = None
    ) -> list[TimeEntry]:
        stmt = select(TimeEntry)
        if start is not None:
            stmt = stmt.where(TimeEntry.entry_date >= start)
        if end is not None:
            stmt = stmt.where(TimeEntry.entry_date <= end)
        stmt = stmt.order_by(TimeEntry.entry_date)
        return list(self._session.scalars(stmt))

    def commit(self) -> None:
        self._session.commit()
