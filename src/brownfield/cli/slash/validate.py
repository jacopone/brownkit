"""Slash command: /brownfield.validate - Validate readiness gates."""

import json
import sys

import click
from rich.console import Console

from brownfield.config import BrownfieldConfig
from brownfield.exceptions import BrownfieldError
from brownfield.orchestrator.utils.display import display_validation_results
from brownfield.orchestrator.validation import ValidationOrchestrator

console = Console()


@click.command("brownfield.validate")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results as JSON",
)
def validate_workflow(output_json: bool) -> None:
    """Validate project against readiness gates for graduation.

    Checks test coverage, complexity, vulnerabilities, documentation,
    and build status against defined thresholds.

    Part of the brownfield workflow: assess → plan → remediate → validate → graduate
    """
    project_root = BrownfieldConfig.get_project_root()

    if not output_json:
        console.print("\n[bold magenta]✓ Validating Readiness Gates[/bold magenta]\n")
        console.print(f"Project: {project_root.name}\n")

    try:
        # Execute validation via orchestrator
        orchestrator = ValidationOrchestrator(project_root=project_root)
        result = orchestrator.execute()

        # Display results
        if output_json:
            output = {
                "all_passed": result.all_passed,
                "failed_count": result.failed_count,
                "gates": [
                    {
                        "name": gr.gate.name,
                        "passed": gr.passed,
                        "current_value": gr.current_value,
                        "threshold": gr.threshold,
                        "message": gr.message,
                    }
                    for gr in result.gates
                ],
                "recommended_phase": result.recommended_phase.value
                if result.recommended_phase
                else None,
                "report_path": str(result.report_path),
            }
            console.print(json.dumps(output, indent=2))
        else:
            display_validation_results(result)

            # Show next step
            console.print("\n[cyan]Next Step:[/cyan]")
            if result.all_passed:
                console.print("  Run: [yellow]brownfield graduate[/yellow]")
                console.print("  This will complete the brownfield transformation")
            else:
                console.print(
                    f"  Run: [yellow]brownfield remediate --phase {result.recommended_phase.value}[/yellow]"
                )
                console.print("  Address failed gates before attempting graduation")

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
