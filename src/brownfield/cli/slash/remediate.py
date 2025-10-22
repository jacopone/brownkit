"""Slash command: /brownfield.remediate - Execute phase remediation."""

import json
import sys

import click
from rich.console import Console

from brownfield.config import BrownfieldConfig
from brownfield.exceptions import BrownfieldError
from brownfield.models.state import Phase
from brownfield.orchestrator.remediation import RemediationOrchestrator
from brownfield.orchestrator.utils.display import display_remediation_results

console = Console()


@click.command("brownfield.remediate")
@click.option(
    "--phase",
    type=click.Choice(["structure", "testing", "quality"], case_sensitive=False),
    required=True,
    help="Phase to remediate",
)
@click.option(
    "--no-commit",
    is_flag=True,
    help="Skip automatic git commits",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results as JSON",
)
def remediate_workflow(phase: str, no_commit: bool, output_json: bool) -> None:
    """Execute remediation for a specific phase (structure, testing, or quality).

    Executes tasks with checkpoint-based recovery, tracks progress,
    and automatically commits changes (unless --no-commit specified).

    Part of the brownfield workflow: assess → plan → remediate → validate → graduate
    """
    project_root = BrownfieldConfig.get_project_root()

    # Convert phase string to Phase enum
    phase_map = {
        "structure": Phase.STRUCTURE,
        "testing": Phase.TESTING,
        "quality": Phase.QUALITY,
    }
    phase_enum = phase_map[phase.lower()]

    if not output_json:
        console.print(f"\n[bold yellow]🔧 Remediating {phase.title()} Phase[/bold yellow]\n")
        console.print(f"Project: {project_root.name}\n")

    try:
        # Execute remediation via orchestrator
        orchestrator = RemediationOrchestrator(project_root=project_root)
        result = orchestrator.execute(phase=phase_enum, auto_commit=not no_commit)

        # Display results
        if output_json:
            output = {
                "phase": result.phase.value,
                "success": result.success,
                "tasks_completed": len(result.tasks_completed),
                "tasks_failed": len(result.tasks_failed),
                "git_commits": result.git_commits,
                "checkpoint_path": str(result.checkpoint_path),
                "duration_seconds": result.duration_seconds,
                "test_coverage_after": result.metrics_after.test_coverage,
                "complexity_avg_after": result.metrics_after.complexity_avg,
            }
            console.print(json.dumps(output, indent=2))
        else:
            display_remediation_results(result)

            # Show next step
            if result.success:
                console.print("\n[cyan]Next Step:[/cyan]")
                if phase == "structure":
                    console.print("  Run: [yellow]brownfield remediate --phase testing[/yellow]")
                elif phase == "testing":
                    console.print("  Run: [yellow]brownfield remediate --phase quality[/yellow]")
                elif phase == "quality":
                    console.print("  Run: [yellow]brownfield validate[/yellow]")
            else:
                console.print("\n[yellow]Some tasks failed. Address failures and re-run remediation.[/yellow]")

    except BrownfieldError as e:
        console.print(f"\n[red]✗ Error:[/red] {e.message}")
        if e.suggestion:
            console.print(f"\n[yellow]Suggestion:[/yellow] {e.suggestion}")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]✗ Unexpected Error:[/red] {e}")
        if BrownfieldConfig.is_debug_enabled():
            import traceback

            console.print("\n[dim]Traceback:[/dim]")
            console.print(traceback.format_exc())
        sys.exit(1)
