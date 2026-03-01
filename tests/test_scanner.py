"""Tests for the filesystem scanner."""

from pathlib import Path
from unittest.mock import patch

from catalogador.scanner.filesystem import collect_file_metadata, walk_directory


class TestCollectFileMetadata:
    def test_collect_included_file(self, tmp_path: Path):
        f = tmp_path / "doc.pdf"
        f.write_bytes(b"PDF content")
        record = collect_file_metadata(f, scan_session_id=1)
        assert record is not None
        assert record.file_name == "doc.pdf"
        assert record.extension == ".pdf"
        assert record.size_bytes == len(b"PDF content")
        assert record.file_hash is not None
        assert record.hash_algorithm == "sha256"

    def test_skip_ignored_extension(self, tmp_path: Path):
        f = tmp_path / "app.exe"
        f.write_bytes(b"EXE content")
        record = collect_file_metadata(f, scan_session_id=1)
        assert record is None

    def test_skip_unknown_extension(self, tmp_path: Path):
        f = tmp_path / "data.xyz"
        f.write_bytes(b"unknown")
        record = collect_file_metadata(f, scan_session_id=1)
        assert record is None

    def test_nonexistent_file_returns_none(self, tmp_path: Path):
        f = tmp_path / "missing.pdf"
        record = collect_file_metadata(f, scan_session_id=1)
        assert record is None

    def test_large_video_skips_hash(self, tmp_path: Path):
        f = tmp_path / "video.mp4"
        f.write_bytes(b"x" * 1024)
        # Patch settings to lower the threshold
        with patch("catalogador.scanner.filesystem.get_settings") as mock_settings:
            mock_settings.return_value.large_file_threshold_mb = 0  # 0 MB = everything is "large"
            record = collect_file_metadata(f, scan_session_id=1)
        assert record is not None
        assert record.file_hash is None
        assert record.hash_algorithm is None

    def test_large_nonvideo_uses_partial_hash(self, tmp_path: Path):
        f = tmp_path / "archive.zip"
        f.write_bytes(b"x" * 1024)
        with patch("catalogador.scanner.filesystem.get_settings") as mock_settings:
            mock_settings.return_value.large_file_threshold_mb = 0
            record = collect_file_metadata(f, scan_session_id=1)
        assert record is not None
        assert record.file_hash is not None
        assert record.hash_algorithm == "sha256-partial"


class TestWalkDirectory:
    def test_walk_finds_included_files(self, sample_dir: Path):
        records, errors = walk_directory(sample_dir, scan_session_id=1)
        # sample_dir has: document.pdf, spreadsheet.xlsx, image.jpg, archive.zip, subdir/nested.pdf
        # Excluded: program.exe, system.dll, readme.txt
        names = {r.file_name for r in records}
        assert "document.pdf" in names
        assert "spreadsheet.xlsx" in names
        assert "image.jpg" in names
        assert "archive.zip" in names
        assert "nested.pdf" in names
        assert "program.exe" not in names
        assert "system.dll" not in names
        assert "readme.txt" not in names
        assert errors == 0

    def test_walk_empty_directory(self, tmp_path: Path):
        records, errors = walk_directory(tmp_path, scan_session_id=1)
        assert records == []
        assert errors == 0

    def test_walk_counts_records(self, sample_dir: Path):
        records, _errors = walk_directory(sample_dir, scan_session_id=1)
        assert len(records) == 5  # pdf, xlsx, jpg, zip, nested pdf
