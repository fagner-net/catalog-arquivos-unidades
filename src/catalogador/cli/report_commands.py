"""CLI commands for generating reports."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from catalogador.db.session import get_session
from catalogador.reports.duplicates import find_duplicate_files_by_hash
from catalogador.reports.export import export_all_records_csv

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command("duplicates")
def report_duplicates() -> None:
    """Show duplicate files detected across storage units."""
    session = get_session()
    try:
        groups = find_duplicate_files_by_hash(session)
        if not groups:
            console.print("[yellow]No duplicate files found.[/yellow]")
            return

        for file_hash, count, files in groups:
            table = Table(title=f"Hash: {file_hash[:16]}... ({count} copies)")
            table.add_column("Unit", style="bold")
            table.add_column("Path")
            table.add_column("Size (bytes)", justify="right")

            for f in files:
                table.add_row(f["unit"], f["path"], f["size"])

            console.print(table)
            console.print()

        console.print(f"[green]Total: {len(groups)} groups of duplicates.[/green]")
    finally:
        session.close()


@app.command("export")
def report_export(
    output: str = typer.Option("catalog_export.csv", "--output", "-o", help="Output CSV path."),
) -> None:
    """Export all cataloged records to CSV."""
    session = get_session()
    try:
        out_path = Path(output)
        count = export_all_records_csv(session, out_path)
        console.print(f"[green]Exported {count} records to {out_path}[/green]")
    finally:
        session.close()
