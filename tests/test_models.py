"""Tests for SQLAlchemy models (structure only — no DB connection needed)."""

from catalogador.db.models import Base, FileRecord, ScanSession, StorageUnit


class TestModelStructure:
    def test_storage_unit_tablename(self):
        assert StorageUnit.__tablename__ == "storage_units"

    def test_scan_session_tablename(self):
        assert ScanSession.__tablename__ == "scan_sessions"

    def test_file_record_tablename(self):
        assert FileRecord.__tablename__ == "file_records"

    def test_base_has_metadata(self):
        tables = Base.metadata.tables
        assert "storage_units" in tables
        assert "scan_sessions" in tables
        assert "file_records" in tables

    def test_storage_unit_repr(self):
        unit = StorageUnit(alias="hd1", unit_type="disco_fisico")
        r = repr(unit)
        assert "hd1" in r
        assert "disco_fisico" in r

    def test_file_record_repr(self):
        record = FileRecord(
            scan_session_id=1,
            full_path="/tmp/test.pdf",
            file_name="test.pdf",
            extension=".pdf",
            size_bytes=1024,
        )
        r = repr(record)
        assert "test.pdf" in r
        assert "1024" in r
