"""Filesystem walker — collects file metadata for cataloging."""

import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from catalogador.config import get_settings
from catalogador.db.models import FileRecord
from catalogador.scanner.hasher import compute_hash, compute_partial_hash
from catalogador.utils.exceptions import HashError
from catalogador.utils.filters import is_video, should_include

logger = logging.getLogger(__name__)


def _timestamp_or_none(epoch: float) -> datetime | None:
    """Convert an OS epoch timestamp to an aware datetime, or None on error."""
    try:
        return datetime.fromtimestamp(epoch, tz=UTC)
    except (OSError, ValueError):
        return None


def collect_file_metadata(
    file_path: Path,
    scan_session_id: int,
) -> FileRecord | None:
    """Build a FileRecord from a single file, or None if it should be skipped."""
    ext = file_path.suffix.lower()
    if not should_include(ext):
        return None

    try:
        stat = file_path.stat()
    except (PermissionError, FileNotFoundError, OSError) as exc:
        logger.warning("Cannot stat %s: %s", file_path, exc)
        return None

    size = stat.st_size
    settings = get_settings()
    large_threshold = settings.large_file_threshold_mb * 1024 * 1024

    # Decide hashing strategy
    file_hash: str | None = None
    hash_algorithm: str | None = None

    if is_video(ext) and size > large_threshold:
        # Large videos: no hash, compare by size only
        logger.debug("Skipping hash for large video: %s (%d bytes)", file_path, size)
    elif size > large_threshold:
        # Large non-video: partial hash
        try:
            file_hash = compute_partial_hash(file_path)
            hash_algorithm = "sha256-partial"
        except HashError:
            logger.warning("Partial hash failed for %s", file_path)
    else:
        # Normal file: full hash
        try:
            file_hash = compute_hash(file_path)
            hash_algorithm = "sha256"
        except HashError:
            logger.warning("Hash failed for %s", file_path)

    return FileRecord(
        scan_session_id=scan_session_id,
        full_path=str(file_path),
        file_name=file_path.name,
        extension=ext,
        size_bytes=size,
        file_hash=file_hash,
        hash_algorithm=hash_algorithm,
        created_at_os=_timestamp_or_none(stat.st_ctime),
        modified_at_os=_timestamp_or_none(stat.st_mtime),
    )


def walk_directory(
    root: Path,
    scan_session_id: int,
    batch_size: int = 500,
) -> tuple[list[FileRecord], int]:
    """Walk a directory tree and collect FileRecords for all included files.

    Returns a tuple of (records, error_count).
    """
    records: list[FileRecord] = []
    errors = 0

    for dirpath, _dirnames, filenames in os.walk(root):
        for fname in filenames:
            file_path = Path(dirpath) / fname
            try:
                record = collect_file_metadata(file_path, scan_session_id)
                if record is not None:
                    records.append(record)
            except Exception:
                logger.exception("Unexpected error processing %s", file_path)
                errors += 1

    logger.info(
        "Walk complete: %d files cataloged, %d errors in %s",
        len(records),
        errors,
        root,
    )
    return records, errors
