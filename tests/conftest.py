"""Shared test fixtures."""

from pathlib import Path

import pytest


@pytest.fixture()
def sample_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with sample files for testing."""
    # Create some sample files with known extensions
    (tmp_path / "document.pdf").write_bytes(b"PDF content here")
    (tmp_path / "spreadsheet.xlsx").write_bytes(b"Excel content here")
    (tmp_path / "image.jpg").write_bytes(b"JPEG content here")
    (tmp_path / "archive.zip").write_bytes(b"ZIP content here")
    (tmp_path / "program.exe").write_bytes(b"EXE should be ignored")
    (tmp_path / "system.dll").write_bytes(b"DLL should be ignored")
    (tmp_path / "readme.txt").write_bytes(b"TXT not in included list")

    # Subdirectory
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "nested.pdf").write_bytes(b"Nested PDF content")

    return tmp_path


@pytest.fixture()
def large_file(tmp_path: Path) -> Path:
    """Create a file larger than 100 MB threshold for testing."""
    # We use a small file but test the logic with a lowered threshold
    large = tmp_path / "large_video.mp4"
    large.write_bytes(b"x" * 1024)
    return large
