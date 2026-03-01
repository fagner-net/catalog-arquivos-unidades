"""Tests for report generation (duplicates and export)."""

# These tests verify module imports and basic structure.
# Full integration tests require a database connection.

from catalogador.reports.duplicates import (
    find_duplicate_files_by_hash,
    find_duplicate_files_by_size,
)
from catalogador.reports.export import export_all_records_csv


class TestReportImports:
    """Verify report modules are importable and functions exist."""

    def test_find_duplicate_files_by_hash_callable(self):
        assert callable(find_duplicate_files_by_hash)

    def test_find_duplicate_files_by_size_callable(self):
        assert callable(find_duplicate_files_by_size)

    def test_export_all_records_csv_callable(self):
        assert callable(export_all_records_csv)
