"""Tests for file hashing strategies."""

from pathlib import Path

import pytest

from catalogador.scanner.hasher import compute_hash, compute_partial_hash
from catalogador.utils.exceptions import HashError


class TestComputeHash:
    def test_hash_known_content(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"hello world")
        result = compute_hash(f)
        assert isinstance(result, str)
        assert len(result) == 64  # sha256 hex digest length

    def test_hash_empty_file(self, tmp_path: Path):
        f = tmp_path / "empty.txt"
        f.write_bytes(b"")
        result = compute_hash(f)
        assert isinstance(result, str)
        assert len(result) == 64

    def test_hash_same_content_same_hash(self, tmp_path: Path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        content = b"identical content"
        f1.write_bytes(content)
        f2.write_bytes(content)
        assert compute_hash(f1) == compute_hash(f2)

    def test_hash_different_content_different_hash(self, tmp_path: Path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_bytes(b"content A")
        f2.write_bytes(b"content B")
        assert compute_hash(f1) != compute_hash(f2)

    def test_hash_nonexistent_file_raises(self, tmp_path: Path):
        f = tmp_path / "nonexistent.txt"
        with pytest.raises(HashError):
            compute_hash(f)


class TestComputePartialHash:
    def test_partial_hash_small_file(self, tmp_path: Path):
        f = tmp_path / "small.txt"
        f.write_bytes(b"small content")
        result = compute_partial_hash(f)
        assert isinstance(result, str)
        assert len(result) == 64

    def test_partial_hash_larger_file(self, tmp_path: Path):
        f = tmp_path / "larger.bin"
        # Create a file with distinct head, middle, tail sections
        f.write_bytes(b"A" * 100_000 + b"B" * 100_000 + b"C" * 100_000)
        result = compute_partial_hash(f)
        assert isinstance(result, str)
        assert len(result) == 64

    def test_partial_hash_nonexistent_raises(self, tmp_path: Path):
        f = tmp_path / "nonexistent.bin"
        with pytest.raises(HashError):
            compute_partial_hash(f)
