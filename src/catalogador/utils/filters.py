"""Extension filtering logic for file cataloging."""

# Extensions we want to catalog
INCLUDED_EXTENSIONS: frozenset[str] = frozenset(
    {
        # Spreadsheets
        ".xls",
        ".xlsx",
        ".xlsm",
        ".xlsb",
        ".csv",
        # Databases
        ".mdb",
        ".accdb",
        # Documents
        ".pdf",
        ".doc",
        ".docx",
        # SFP
        ".sfp",
        # Archives
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        # Images
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".tif",
        ".webp",
        ".svg",
        # Videos
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        # Audio
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
    }
)

# Extensions to always ignore
IGNORED_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".exe",
        ".com",
        ".dll",
        ".sys",
        ".drv",
        ".ocx",
        ".bat",
        ".cmd",
        ".msi",
        ".scr",
        ".cpl",
        ".tmp",
        ".log",
        ".bak",
    }
)

# Video extensions (skip hash for large videos — compare by size only)
VIDEO_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
    }
)


def should_include(extension: str) -> bool:
    """Return True if the file extension should be cataloged."""
    ext = extension.lower()
    if ext in IGNORED_EXTENSIONS:
        return False
    return ext in INCLUDED_EXTENSIONS


def is_video(extension: str) -> bool:
    """Return True if the file extension is a video format."""
    return extension.lower() in VIDEO_EXTENSIONS
