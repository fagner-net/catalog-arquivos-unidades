"""Data access layer — queries and persistence operations."""

import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from catalogador.db.models import FileRecord, ScanSession, StorageUnit
from catalogador.utils.exceptions import DuplicateUnitError, UnitNotFoundError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# StorageUnit operations
# ---------------------------------------------------------------------------


def add_unit(session: Session, alias: str, unit_type: str) -> StorageUnit:
    """Register a new storage unit. Raises DuplicateUnitError if alias exists."""
    existing = session.execute(
        select(StorageUnit).where(StorageUnit.alias == alias)
    ).scalar_one_or_none()
    if existing is not None:
        raise DuplicateUnitError(f"Unit with alias '{alias}' already exists")
    unit = StorageUnit(alias=alias, unit_type=unit_type)
    session.add(unit)
    session.commit()
    logger.info("Registered storage unit: %s (%s)", alias, unit_type)
    return unit


def list_units(session: Session) -> list[StorageUnit]:
    """Return all registered storage units."""
    result = session.execute(select(StorageUnit).order_by(StorageUnit.alias))
    return list(result.scalars().all())


def get_unit_by_alias(session: Session, alias: str) -> StorageUnit:
    """Fetch a unit by alias. Raises UnitNotFoundError if missing."""
    unit = session.execute(
        select(StorageUnit).where(StorageUnit.alias == alias)
    ).scalar_one_or_none()
    if unit is None:
        raise UnitNotFoundError(f"No unit found with alias '{alias}'")
    return unit


def remove_unit(session: Session, alias: str) -> None:
    """Delete a storage unit and its cascade (sessions, file records)."""
    unit = get_unit_by_alias(session, alias)
    session.delete(unit)
    session.commit()
    logger.info("Removed storage unit: %s", alias)


# ---------------------------------------------------------------------------
# ScanSession operations
# ---------------------------------------------------------------------------


def create_scan_session(session: Session, unit: StorageUnit, root_path: str) -> ScanSession:
    """Start a new scan session for the given unit."""
    scan = ScanSession(storage_unit_id=unit.id, root_path=root_path)
    session.add(scan)
    session.commit()
    logger.info("Scan session started: unit=%s, path=%s", unit.alias, root_path)
    return scan


def finish_scan_session(
    session: Session,
    scan: ScanSession,
    total_files: int,
    total_errors: int,
) -> None:
    """Mark a scan session as finished."""
    scan.finished_at = datetime.now(UTC)
    scan.total_files = total_files
    scan.total_errors = total_errors
    session.commit()
    logger.info("Scan session finished: %d files, %d errors", total_files, total_errors)


# ---------------------------------------------------------------------------
# FileRecord operations
# ---------------------------------------------------------------------------


def bulk_insert_records(session: Session, records: list[FileRecord]) -> None:
    """Insert a batch of file records."""
    session.add_all(records)
    session.commit()
    logger.debug("Inserted %d file records", len(records))
