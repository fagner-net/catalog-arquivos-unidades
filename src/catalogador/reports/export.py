"""Report export to CSV and Excel."""

import csv
import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from catalogador.db.models import FileRecord, ScanSession, StorageUnit

logger = logging.getLogger(__name__)


def export_all_records_csv(session: Session, output_path: Path) -> int:
    """Export all file records to a CSV file. Returns the number of rows written."""
    stmt = (
        select(
            StorageUnit.alias,
            ScanSession.root_path,
            FileRecord.full_path,
            FileRecord.file_name,
            FileRecord.extension,
            FileRecord.size_bytes,
            FileRecord.file_hash,
            FileRecord.hash_algorithm,
            FileRecord.created_at_os,
            FileRecord.modified_at_os,
            FileRecord.cataloged_at,
        )
        .join(ScanSession, FileRecord.scan_session_id == ScanSession.id)
        .join(StorageUnit, ScanSession.storage_unit_id == StorageUnit.id)
        .order_by(StorageUnit.alias, FileRecord.full_path)
    )

    rows = session.execute(stmt).all()

    headers = [
        "unit_alias",
        "root_path",
        "full_path",
        "file_name",
        "extension",
        "size_bytes",
        "file_hash",
        "hash_algorithm",
        "created_at_os",
        "modified_at_os",
        "cataloged_at",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)

    logger.info("Exported %d records to %s", len(rows), output_path)
    return len(rows)
