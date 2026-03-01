"""CLI commands for scanning storage units."""

from pathlib import Path

import typer
from rich.console import Console

from catalogador.db.repository import (
    bulk_insert_records,
    create_scan_session,
    finish_scan_session,
    get_unit_by_alias,
)
from catalogador.db.session import get_session
from catalogador.scanner.filesystem import walk_directory
from catalogador.utils.exceptions import UnitNotFoundError

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command("run")
def scan_run(
    unit_alias: str = typer.Option(..., "--unit", "-u", help="Alias of the storage unit."),
    path: str = typer.Option(..., "--path", "-p", help="Root path to scan."),
) -> None:
    """Scan a directory tree and catalog file metadata."""
    root = Path(path)
    if not root.is_dir():
        console.print(f"[red]Path does not exist or is not a directory: {root}[/red]")
        raise typer.Exit(code=1)

    session = get_session()
    try:
        unit = get_unit_by_alias(session, unit_alias)
    except UnitNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    scan = create_scan_session(session, unit, str(root))
    console.print(f"[cyan]Scanning {root} for unit '{unit_alias}'...[/cyan]")

    records, errors = walk_directory(root, scan_session_id=scan.id)

    if records:
        bulk_insert_records(session, records)

    finish_scan_session(session, scan, total_files=len(records), total_errors=errors)

    console.print(f"[green]Scan complete:[/green] {len(records)} files cataloged, {errors} errors.")
    session.close()
