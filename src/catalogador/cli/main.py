"""CLI entry point — groups all subcommands."""

import logging

import typer

from catalogador.cli.report_commands import app as report_app
from catalogador.cli.scan_commands import app as scan_app
from catalogador.cli.unit_commands import app as unit_app

app = typer.Typer(
    name="catalogador",
    help="File cataloging tool for detecting duplicates across storage units.",
    no_args_is_help=True,
)

app.add_typer(unit_app, name="unit", help="Manage storage units.")
app.add_typer(scan_app, name="scan", help="Scan storage units.")
app.add_typer(report_app, name="report", help="Generate reports.")


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging."),
) -> None:
    """Configure logging level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


if __name__ == "__main__":
    app()
