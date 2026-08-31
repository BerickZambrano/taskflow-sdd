from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas.stats import StatsOut, TimeEntryCreate, TimeEntryOut
from app.repositories.time_entry_repository import TimeEntryRepository
from app.services.stats_service import StatsService

router = APIRouter(tags=["stats"])


@router.post("/time-entries", response_model=TimeEntryOut, status_code=201)
def create_time_entry(
    payload: TimeEntryCreate,
    db: Session = Depends(get_db),
) -> TimeEntryOut:
    repo = TimeEntryRepository(db)
    entry = repo.create(
        minutes=payload.minutes,
        entry_date=payload.entry_date or date.today(),
        task_id=payload.task_id,
    )
    repo.commit()
    return entry


@router.get("/time-entries", response_model=list[TimeEntryOut])
def list_time_entries(
    from_date: date | None = None,
    to: date | None = None,
    db: Session = Depends(get_db),
) -> list:
    return TimeEntryRepository(db).list_between(start=from_date, end=to)


@router.get("/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)) -> dict:
    return StatsService(db, TimeEntryRepository(db)).get_stats()
