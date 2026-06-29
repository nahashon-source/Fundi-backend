"""
Database engine and session management.

`get_db` is a FastAPI dependency — routes never import this directly.
It's injected into repositories via Depends(get_db), keeping the
session's lifecycle (open -> use -> close) handled in one place.
"""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from app.core.config import settings

# SQLite needs this flag for multi-threaded FastAPI access; Postgres ignores it.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Yields a DB session for the duration of a single request, then closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()