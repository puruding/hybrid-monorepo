"""CLI commands using Typer with Rich output."""
from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from src.application.compare_usecase import CompareResult, CompareUseCase
from src.config.settings import get_settings
from src.domain.exceptions import CompareDataError
from src.infrastructure.csv_reader import CSVReader
from src.infrastructure.db_reader import DBReader
from src.infrastructure.report_writer import ReportWriter

app = typer.Typer(
    name="lgu-compare",
    help="LGU+ CSV-DB Data Comparison Tool",
    add_completion=False,
)

console = Console()


def _display_header() -> None:
    """Display the report header."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(
        Panel(
            f"[bold blue]LGU+ Data Comparison Report[/bold blue]\n[dim]{now}[/dim]",
            expand=False,
        )
    )
    console.print()


def _display_summary(result: CompareResult) -> None:
    """Display the summary table."""
    summary = result.summary

    table = Table(title="Summary", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", width=30)
    table.add_column("Value", justify="right", style="green", width=12)

    # Data metrics
    table.add_row("Total Source Records", f"{summary.total_source:,}")
    table.add_row("Total Target Records", f"{summary.total_target:,}")
    table.add_row("", "")
    table.add_row("Extra Duplicate Source", f"{summary.extra_duplicate_source_count:,}")
    table.add_row("Extra Duplicate Target", f"{summary.extra_duplicate_target_count:,}")
    table.add_row("", "")
    table.add_row("Unique Source Serials", f"{summary.unique_source_count:,}")
    table.add_row("Unique Target Serials", f"{summary.unique_target_count:,}")
    table.add_row("", "")
    table.add_row("Matched", f"{summary.matched_count:,}")
    table.add_row("Name Mismatch", f"{summary.name_mismatch_count:,}")
    table.add_row("Source Only", f"{summary.source_only_count:,}")
    table.add_row("Target Only", f"{summary.target_only_count:,}")

    console.print(table)
    console.print()

    # Validation check
    if summary.validate_consistency():
        console.print("[green]Validation:[/green]")
        console.print(
            f"  [dim]{summary.total_source} = {summary.unique_source_count} + "
            f"{summary.extra_duplicate_source_count} (Total Source = Unique + Extra Dup)[/dim]"
        )
        console.print(
            f"  [dim]{summary.total_target} = {summary.unique_target_count} + "
            f"{summary.extra_duplicate_target_count} (Total Target = Unique + Extra Dup)[/dim]"
        )
        console.print(
            f"  [dim]{summary.unique_source_count} = {summary.matched_count} + "
            f"{summary.name_mismatch_count} + {summary.source_only_count} "
            f"(Unique Source = Matched + Mismatch + Source Only)[/dim]"
        )
        console.print(
            f"  [dim]{summary.unique_target_count} = {summary.matched_count} + "
            f"{summary.name_mismatch_count} + {summary.target_only_count} "
            f"(Unique Target = Matched + Mismatch + Target Only)[/dim]"
        )
    else:
        console.print("[red]Validation: FAILED - Mathematical inconsistency detected![/red]")

    console.print()


def _display_warnings(result: CompareResult) -> None:
    """Display warnings for duplicates."""
    summary = result.summary

    if summary.extra_duplicate_source_count > 0:
        console.print(
            f"[yellow]Warning: SOURCE has {summary.extra_duplicate_source_count} "
            f"extra duplicate serials - see Duplicates sheet[/yellow]"
        )

    if summary.extra_duplicate_target_count > 0:
        console.print(
            f"[yellow]Warning: TARGET has {summary.extra_duplicate_target_count} "
            f"extra duplicate serials - see Duplicates sheet[/yellow]"
        )

    if result.duplicates:
        console.print()


def _display_mismatches(result: CompareResult, max_display: int = 10) -> None:
    """Display name mismatches table."""
    from src.domain.models import MatchStatus

    mismatches = [r for r in result.comparison_results if r.status == MatchStatus.NAME_MISMATCH]

    if not mismatches:
        return

    table = Table(
        title=f"Name Mismatches (showing first {min(len(mismatches), max_display)})",
        show_header=True,
        header_style="bold yellow",
    )
    table.add_column("Serial Number", style="cyan")
    table.add_column("Source Product", style="green")
    table.add_column("Target Product", style="red")

    for mismatch in mismatches[:max_display]:
        table.add_row(
            mismatch.serial_number,
            mismatch.source_product_name or "",
            mismatch.target_product_name or "",
        )

    if len(mismatches) > max_display:
        table.add_row("...", "...", "...")

    console.print(table)
    console.print()


def _display_report_paths(result: CompareResult) -> None:
    """Display generated report paths."""
    console.print("[bold]Reports generated:[/bold]")
    for path in result.report_paths:
        console.print(f"  [cyan]{path}[/cyan]")
    console.print()


@app.command()
def compare(
    csv_file: Annotated[
        Optional[Path],
        typer.Option(
            "--csv",
            "-c",
            help="Path to source CSV file",
        ),
    ] = None,
    output_format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: xlsx, csv, or both",
        ),
    ] = "xlsx",
    output_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Output directory for reports",
        ),
    ] = None,
    has_header: Annotated[
        bool,
        typer.Option(
            "--header/--no-header",
            help="Whether CSV has header row",
        ),
    ] = False,
    show_mismatches: Annotated[
        int,
        typer.Option(
            "--show-mismatches",
            "-m",
            help="Number of name mismatches to display (0 = none)",
        ),
    ] = 10,
) -> None:
    """Compare CSV file with LGU database and generate report."""
    try:
        # Load settings
        settings = get_settings()

        # Resolve paths
        csv_path = csv_file or settings.csv_file_path
        out_dir = output_dir or settings.output_dir

        if not csv_path.exists():
            console.print(f"[red]Error: CSV file not found: {csv_path}[/red]")
            raise typer.Exit(1)

        _display_header()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            # Initialize components
            task = progress.add_task("Initializing...", total=None)

            csv_reader = CSVReader(csv_path, has_header=has_header)
            db_settings = settings.get_lgu_db()
            db_reader = DBReader(db_settings.get_connection_string())
            report_writer = ReportWriter(out_dir)

            # Execute comparison
            progress.update(task, description="Loading source data (CSV)...")
            _ = csv_reader.load_records()

            progress.update(task, description="Loading target data (DB)...")
            _ = db_reader.load_records()

            progress.update(task, description="Comparing datasets...")
            usecase = CompareUseCase(
                source_port=csv_reader,
                target_port=db_reader,
                report_writer=report_writer,
                output_format=output_format,
            )
            result = usecase.execute()

            progress.update(task, description="Complete!")

        # Display results
        _display_summary(result)
        _display_warnings(result)

        if show_mismatches > 0:
            _display_mismatches(result, max_display=show_mismatches)

        _display_report_paths(result)

        # Cleanup
        db_reader.close()

        console.print("[green]Comparison completed successfully![/green]")

    except CompareDataError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def version() -> None:
    """Show version information."""
    console.print("[bold]LGU+ CSV-DB Comparison Tool[/bold]")
    console.print("Version: 1.0.0")


if __name__ == "__main__":
    app()
