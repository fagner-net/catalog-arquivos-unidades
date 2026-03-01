# AGENTS.md — catalog-arquivos-unidades

## Project Overview

File cataloging tool that scans multiple storage units (physical disks, NAS,
Google Drive, etc.) and records metadata (hash, timestamps, full path, size)
into PostgreSQL. The goal is detecting duplicate files and backup folders
without copying files — only reading and indexing them.

Each storage unit is registered with an **alias** (unique short name) and a
**type** (disco_fisico, nas, google_drive, outro). The root path is provided
at scan time, not stored on the unit, since mount points may change.

Focus file types: Excel, Access, SFP, ZIP, images, videos, PDFs (extensible).
Ignored: .exe, .com, Windows system files.
Large files (>100MB): skip hash for video; for others, use partial hashing or
size-only comparison.

## Tech Stack

- **Language:** Python 3.12+
- **Package manager:** Poetry (pyproject.toml)
- **Database:** PostgreSQL via SQLAlchemy 2.x ORM + Alembic migrations
- **Testing:** pytest
- **Linting/Formatting:** Ruff (linter + formatter)
- **Type checking:** mypy (strict mode)
- **CLI framework:** click or typer

## Project Structure

```
catalog-arquivos-unidades/
├── pyproject.toml
├── poetry.lock
├── alembic.ini
├── alembic/
│   └── versions/
├── src/
│   └── catalogador/
│       ├── __init__.py
│       ├── config.py              # Settings / env vars
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── main.py            # CLI entry point, group commands
│       │   ├── unit_commands.py   # unit add/list/remove
│       │   ├── scan_commands.py   # scan --unit --path
│       │   └── report_commands.py # report duplicates/export
│       ├── db/
│       │   ├── __init__.py
│       │   ├── models.py          # StorageUnit, ScanSession, FileRecord
│       │   ├── session.py         # Engine / session factory
│       │   └── repository.py     # Data access layer (queries)
│       ├── scanner/
│       │   ├── __init__.py
│       │   ├── filesystem.py      # Walk directories, collect metadata
│       │   └── hasher.py          # File hashing strategies
│       ├── reports/
│       │   ├── __init__.py
│       │   ├── duplicates.py      # Duplicate detection queries
│       │   └── export.py          # CSV/Excel report generation
│       └── utils/
│           ├── __init__.py
│           ├── exceptions.py      # Custom exceptions
│           └── filters.py         # Extension filtering logic
├── tests/
│   ├── conftest.py                # Shared fixtures (db, tmp dirs)
│   ├── test_units.py
│   ├── test_scanner.py
│   ├── test_hasher.py
│   ├── test_models.py
│   ├── test_reports.py
│   └── test_filters.py
└── AGENTS.md
```

## Build & Run Commands

```bash
poetry install                                    # Install dependencies
poetry shell                                      # Activate virtualenv
poetry run catalogador unit add --alias "hd1" --type disco_fisico  # Register unit
poetry run catalogador unit list                  # List registered units
poetry run catalogador scan --unit "hd1" --path /mnt/hd-externo    # Run scan
poetry run catalogador report duplicates          # Generate duplicates report
poetry run alembic upgrade head                   # Apply migrations
poetry run alembic revision --autogenerate -m "msg"  # Create migration
```

## Lint / Format / Type Check

```bash
poetry run ruff check src/ tests/                 # Lint (check only)
poetry run ruff check --fix src/ tests/           # Lint (auto-fix)
poetry run ruff format src/ tests/                # Format code
poetry run mypy src/                              # Type check (strict)
```

## Testing

```bash
poetry run pytest                                 # Run all tests
poetry run pytest -v                              # Verbose output
poetry run pytest tests/test_scanner.py           # Single test file
poetry run pytest tests/test_scanner.py::test_walk_directory  # Single function
poetry run pytest -k "test_hash_large_file"       # Keyword match
poetry run pytest --cov=catalogador --cov-report=term-missing  # With coverage
```

## Code Style Guidelines

### General
- Python 3.12+ — use modern syntax (`str | None`, `match` statements).
- Maximum line length: 100 characters.
- All code must pass `ruff check`, `ruff format`, and `mypy --strict`.

### Imports
- Absolute imports from the package root: `from catalogador.db.models import FileRecord`.
- Order: stdlib, third-party, local — separated by blank lines.
- Never use wildcard imports (`from x import *`).
- Ruff enforces isort-compatible import sorting.

### Naming Conventions
- **Modules/packages:** `snake_case` (`file_scanner.py`).
- **Classes:** `PascalCase` (`FileRecord`, `StorageUnit`).
- **Functions/methods/variables:** `snake_case` (`compute_hash`).
- **Constants:** `UPPER_SNAKE_CASE` (`IGNORED_EXTENSIONS`).
- **Private:** prefix with `_` (`_internal_helper`).

### Type Annotations
- All public functions: full annotations (params + return).
- Use `pathlib.Path` for filesystem paths, never raw `str`.
- Prefer `str | None` over `Optional[str]`.
- Use `Sequence`, `Mapping`, `Iterator` for complex types.

### Error Handling
- Never use bare `except:` — always catch specific exceptions.
- Domain exceptions in `catalogador/utils/exceptions.py` (e.g., `ScanError`,
  `HashError`, `DatabaseError`).
- Log with `logger.exception()` for full tracebacks.
- File I/O: handle `PermissionError`, `FileNotFoundError`, `OSError` gracefully
  — log warning and continue scanning.

### Database Conventions
- Models inherit from shared `Base` (declarative base).
- Use `Mapped[]` + `mapped_column()` (SQLAlchemy 2.x style).
- Table names: plural `snake_case` (`file_records`, `storage_units`).
- Schema changes only via Alembic — never modify DB manually.
- Repository pattern: queries in `repository.py`, not in business logic.

### Testing Conventions
- Mirror source structure: `src/catalogador/scanner/hasher.py` -> `tests/test_hasher.py`.
- Fixtures in `conftest.py` for DB sessions and temp directories.
- Use `tmp_path` for filesystem tests — never write to real directories.
- Tests must be independent; no reliance on execution order.
- Name pattern: `test_<unit>_<scenario>_<expected>`.

### Logging
- Use `logging` with `__name__` loggers.
- Format: `"%(asctime)s [%(levelname)s] %(name)s: %(message)s"`.
- DEBUG: scanning details. INFO: progress. WARNING: skipped files.
  ERROR: non-fatal failures.

### Configuration
- Sensitive settings via environment variables (DB credentials).
- Use `pydantic-settings` for typed config.
- Default DB URL: `postgresql://localhost:5432/catalogador`.

### Git & Versioning
- Hosted on GitHub (managed via `gh` CLI).
- Conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`.
- `.gitignore`: `__pycache__`, `.mypy_cache`, `.ruff_cache`, `*.egg-info`, `.env`.
- `poetry.lock` is committed.

### Language
- Code identifiers (variables, functions, classes): English.
- Comments and docstrings: Portuguese (pt-BR) or English.
- Commit messages: English.
