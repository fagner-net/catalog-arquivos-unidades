"""Database engine and session factory."""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from catalogador.config import get_settings

logger = logging.getLogger(__name__)

_session_factory: sessionmaker[Session] | None = None


def get_engine(database_url: str | None = None):
    """Create a SQLAlchemy engine from settings or a provided URL."""
    url = database_url or get_settings().database_url
    return create_engine(url, echo=False)


def get_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    """Return a session factory, creating the engine on first call."""
    global _session_factory
    if _session_factory is None:
        engine = get_engine(database_url)
        _session_factory = sessionmaker(bind=engine, expire_on_commit=False)
        logger.info("Database session factory created")
    return _session_factory


def get_session(database_url: str | None = None) -> Session:
    """Open a new database session."""
    factory = get_session_factory(database_url)
    return factory()
