"""CLI command for resuming interrupted workflows."""

import sys

import click
from rich.console import Console
from rich.table import Table

from brownfield.config import BrownfieldConfig
from brownfield.orchestrator.checkpoint_manager import CheckpointManager
from brownfield.state.state_store import StateStore


@click.command()
@click.option(
    "--restart",
    is_flag=True,
    help="Restart phase from beginning instead of resuming",
)
def resume(restart: bool):
    """
    Resume interrupted phase from checkpoint.

    When a brownfield phase is interrupted (Ctrl+C, system crash, etc.),
    this command allows you to resume from the last checkpoint instead of
    starting over.

    Without --restart flag: Resumes from last checkpoint
    With --restart flag: Clears checkpoint and restarts phase from beginning
    """
    console = Console()
    project_root = BrownfieldConfig.get_project_root()

    console.print("\n[cyan]🔄 Resume Interrupted Workflow[/cyan]\n")

    # Load state
    state_store = StateStore(project_root / ".specify" / "memory" / "brownfield-state.json")

    if not state_store.exists():
        console.print("[red]Error:[/red] No brownfield state found. Run 'brownfield assess' first.")
        sys.exit(1)

    state = state_store.load()

    # Check for checkpoints
    checkpoint_manager = CheckpointManager(project_root)
    checkpoints = checkpoint_manager.list_all_checkpoints()

    if not checkpoints:
        console.print("[yellow]No checkpoints found.[/yellow]")
        console.print(f"\nCurrent phase: {state.current_phase.value}")
        console.print("No interruption detected - continue with current phase.")
        sys.exit(0)

    # Display available checkpoints
    console.print("[cyan]Available Checkpoints:[/cyan]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Phase", style="white", width=15)
    table.add_column("Status", justify="center", width=12)
    table.add_column("Completed", justify="right", width=12)
    table.add_column("Pending", justify="right", width=12)
    table.add_column("Timestamp", width=20)

    for cp in checkpoints:
        status = "⚠ Interrupted" if cp["interrupted"] else "✓ Complete"
        status_color = "yellow" if cp["interrupted"] else "green"

        table.add_row(
            cp["phase"],
            f"[{status_color}]{status}[/{status_color}]",
            str(cp["completed_tasks"]),
            str(cp["pending_tasks"]),
            cp["timestamp"][:19],  # Truncate to datetime without microseconds
        )

    console.print(table)

    # Find interrupted checkpoint
    interrupted_checkpoints = [cp for cp in checkpoints if cp["interrupted"]]

    if not interrupted_checkpoints:
        console.print("\n[green]✓[/green] No interrupted phases found.")
        console.print("All checkpoints completed successfully.")
        sys.exit(0)

    # Use most recent interrupted checkpoint
    target_checkpoint = interrupted_checkpoints[0]
    phase_name = target_checkpoint["phase"]

    from brownfield.models.state import Phase

    phase = Phase(phase_name)

    console.print(f"\n[cyan]Resuming Phase:[/cyan] {phase.value}")

    if restart:
        # Clear checkpoint and restart
        console.print("[yellow]--restart flag set: Clearing checkpoint and restarting phase[/yellow]\n")
        checkpoint_manager.clear_checkpoint(phase)

        console.print(f"[green]✓[/green] Checkpoint cleared for {phase.value} phase")
        console.print(f"\nRun: [cyan]brownfield {phase.value}[/cyan] to restart from beginning")
        sys.exit(0)

    # Get resumption options
    options = checkpoint_manager.get_resumption_options(phase)

    if not options["can_resume"]:
        console.print(f"[red]Cannot resume:[/red] {options['reason']}")
        sys.exit(1)

    # Display resumption info
    console.print(f"  Completed tasks: {options['completed_count']}")
    console.print(f"  Pending tasks: {options['pending_count']}")

    if options["next_task"]:
        console.print("\n[cyan]Next Task:[/cyan]")
        console.print(f"  {options['next_task'].description}")

    console.print(f"\n[green]✓[/green] Ready to resume {phase.value} phase")
    console.print(f"\nRun: [cyan]brownfield {phase.value}[/cyan] to continue from checkpoint")
    console.print("\nOr use: [cyan]brownfield resume --restart[/cyan] to start over")

    sys.exit(0)
