from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()

database_url = settings.database_url.replace(
    "postgresql://",
    "postgresql+psycopg://",
    1,
)

engine = create_engine(database_url)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)   