"""CLI commands for managing storage units."""

import typer
from rich.console import Console
from rich.table import Table

from catalogador.db.repository import add_unit, list_units, remove_unit
from catalogador.db.session import get_session
from catalogador.utils.exceptions import DuplicateUnitError, UnitNotFoundError

app = typer.Typer(no_args_is_help=True)
console = Console()

VALID_TYPES = ("disco_fisico", "nas", "google_drive", "outro")


@app.command("add")
def unit_add(
    alias: str = typer.Option(..., "--alias", "-a", help="Unique short name for the unit."),
    unit_type: str = typer.Option(
        ..., "--type", "-t", help=f"Unit type: {', '.join(VALID_TYPES)}."
    ),
) -> None:
    """Register a new storage unit."""
    if unit_type not in VALID_TYPES:
        console.print(f"[red]Invalid type '{unit_type}'. Must be one of: {VALID_TYPES}[/red]")
        raise typer.Exit(code=1)

    session = get_session()
    try:
        unit = add_unit(session, alias=alias, unit_type=unit_type)
        console.print(f"[green]Unit registered:[/green] {unit.alias} ({unit.unit_type})")
    except DuplicateUnitError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc
    finally:
        session.close()


@app.command("list")
def unit_list() -> None:
    """List all registered storage units."""
    session = get_session()
    try:
        units = list_units(session)
        if not units:
            console.print("[yellow]No storage units registered.[/yellow]")
            return

        table = Table(title="Storage Units")
        table.add_column("ID", style="dim")
        table.add_column("Alias", style="bold")
        table.add_column("Type")
        table.add_column("Created At")

        for u in units:
            table.add_row(
                str(u.id),
                u.alias,
                u.unit_type,
                str(u.created_at),
            )
        console.print(table)
    finally:
        session.close()


@app.command("remove")
def unit_remove(
    alias: str = typer.Option(..., "--alias", "-a", help="Alias of the unit to remove."),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
) -> None:
    """Remove a storage unit and all its scan data."""
    if not confirm:
        typer.confirm(
            f"This will delete unit '{alias}' and ALL associated scan data. Continue?",
            abort=True,
        )

    session = get_session()
    try:
        remove_unit(session, alias)
        console.print(f"[green]Unit '{alias}' removed.[/green]")
    except UnitNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc
    finally:
        session.close()
