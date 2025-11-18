"""
Database initialization helpers.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
)

Base = declarative_base()


def init_db() -> None:
    """Create database tables."""
    # Importing ORM models ensures metadata is populated before create_all is executed.
    from app.models import orm  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db_session():
    """Provide a transactional scope for DB interactions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


