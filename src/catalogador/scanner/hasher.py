"""File hashing strategies for the catalogador."""

import hashlib
import logging
from pathlib import Path

from catalogador.utils.exceptions import HashError

logger = logging.getLogger(__name__)

DEFAULT_ALGORITHM = "sha256"
DEFAULT_CHUNK_SIZE = 8192


def compute_hash(
    file_path: Path,
    algorithm: str = DEFAULT_ALGORITHM,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> str:
    """Compute the full hash of a file by reading it in chunks."""
    try:
        h = hashlib.new(algorithm)
        with file_path.open("rb") as f:
            while chunk := f.read(chunk_size):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, ValueError) as exc:
        raise HashError(f"Failed to hash {file_path}: {exc}") from exc


def compute_partial_hash(
    file_path: Path,
    algorithm: str = DEFAULT_ALGORITHM,
    sample_size: int = 65536,
) -> str:
    """Compute a partial hash (head + middle + tail) for large files.

    Reads ``sample_size`` bytes from the beginning, middle, and end of the
    file and hashes them together. This is much faster than a full hash for
    files >100 MB while still providing reasonable uniqueness.
    """
    try:
        size = file_path.stat().st_size
        h = hashlib.new(algorithm)

        with file_path.open("rb") as f:
            # Head
            h.update(f.read(sample_size))

            # Middle
            mid = max(0, size // 2 - sample_size // 2)
            f.seek(mid)
            h.update(f.read(sample_size))

            # Tail
            tail = max(0, size - sample_size)
            f.seek(tail)
            h.update(f.read(sample_size))

        return h.hexdigest()
    except (OSError, ValueError) as exc:
        raise HashError(f"Failed to partial-hash {file_path}: {exc}") from exc
