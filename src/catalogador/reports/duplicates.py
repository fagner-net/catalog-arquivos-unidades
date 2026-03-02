"""Duplicate detection queries."""

import logging
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from catalogador.db.models import FileRecord, ScanSession, StorageUnit

logger = logging.getLogger(__name__)


def find_duplicate_files_by_hash(session: Session) -> list[tuple[str, int, list[dict[str, str]]]]:
    """Find files with the same hash across all units.

    Returns a list of tuples: (file_hash, count, [file_info_dicts]).
    Only considers files that have a non-null hash.
    """
    # Subquery: hashes that appear more than once
    subq = (
        select(FileRecord.file_hash)
        .where(FileRecord.file_hash.isnot(None))
        .group_by(FileRecord.file_hash)
        .having(func.count(FileRecord.id) > 1)
        .subquery()
    )

    stmt = (
        select(
            FileRecord.file_hash,
            FileRecord.full_path,
            FileRecord.size_bytes,
            FileRecord.file_name,
            StorageUnit.alias,
        )
        .join(ScanSession, FileRecord.scan_session_id == ScanSession.id)
        .join(StorageUnit, ScanSession.storage_unit_id == StorageUnit.id)
        .where(FileRecord.file_hash.in_(select(subq.c.file_hash)))
        .order_by(FileRecord.file_hash, StorageUnit.alias)
    )

    rows = session.execute(stmt).all()

    # Group by hash
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        h = row.file_hash
        entry = {
            "path": row.full_path,
            "name": row.file_name,
            "size": str(row.size_bytes),
            "unit": row.alias,
        }
        grouped.setdefault(h, []).append(entry)

    result = [(h, len(files), files) for h, files in grouped.items()]
    logger.info("Found %d groups of duplicate files", len(result))
    return result


def find_duplicate_files_by_size(
    session: Session,
    min_size: int = 0,
) -> Sequence[tuple[int, int]]:
    """Find file sizes that appear in multiple units (useful for large videos).

    Returns list of (size_bytes, count) tuples.
    """
    stmt = (
        select(FileRecord.size_bytes, func.count(FileRecord.id).label("cnt"))
        .where(FileRecord.size_bytes > min_size)
        .group_by(FileRecord.size_bytes)
        .having(func.count(FileRecord.id) > 1)
        .order_by(func.count(FileRecord.id).desc())
    )
    return session.execute(stmt).all()  # type: ignore[return-value]
