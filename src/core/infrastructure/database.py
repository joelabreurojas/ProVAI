from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm import Session as SQLAlchemySession

from src.core.infrastructure.settings import settings

# The connect_args is specific to SQLite and is necessary
# to allow the database connection to be shared across different threads.
engine = create_engine(settings.DB_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


def get_db() -> Generator[SQLAlchemySession, None, None]:
    """Get a database session to use in endpoints."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
