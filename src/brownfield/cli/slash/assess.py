"""Slash command: /brownfield.assess - Workflow-oriented assessment."""

import sys

import click
from rich.console import Console

from brownfield.config import BrownfieldConfig
from brownfield.exceptions import BrownfieldError
from brownfield.orchestrator.assessment import AssessmentOrchestrator
from brownfield.orchestrator.utils.display import display_assessment_results

console = Console()


@click.command("brownfield.assess")
@click.option(
    "--quick/--full",
    default=True,
    help="Analysis mode (quick: sampling, full: comprehensive)",
)
@click.option(
    "--language",
    type=click.Choice(["python", "javascript", "rust", "go"]),
    help="Override language detection",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results as JSON",
)
def assess_workflow(quick: bool, language: str, output_json: bool) -> None:
    """Run comprehensive codebase assessment (workflow command).

    This is the workflow-oriented entry point for brownfield assessment.
    It orchestrates language detection, metrics collection, tech debt analysis,
    and state initialization/regression detection.

    Part of the brownfield workflow: assess → plan → remediate → validate → graduate
    """
    project_root = BrownfieldConfig.get_project_root()

    if not output_json:
        console.print("\n[bold blue]🔍 Brownfield Assessment[/bold blue]\n")
        console.print(f"Project: {project_root.name}")
        console.print(f"Mode: {'Quick' if quick else 'Full'}\n")

    try:
        # Execute assessment via orchestrator
        orchestrator = AssessmentOrchestrator(
            project_root=project_root,
            language_override=language,
            quick_mode=quick,
        )

        result = orchestrator.execute()

        # Display results
        if output_json:
            import json

            output = {
                "language": result.language_detection.language,
                "confidence": result.language_detection.confidence.name,
                "test_coverage": result.baseline_metrics.test_coverage,
                "complexity_avg": result.baseline_metrics.complexity_avg,
                "complexity_max": result.baseline_metrics.complexity_max,
                "tech_debt_count": len(result.tech_debt),
                "regression_detected": result.regression is not None,
                "current_phase": result.current_phase.value,
                "duration_seconds": result.duration_seconds,
                "report_path": str(result.report_path),
            }
            console.print(json.dumps(output, indent=2))
        else:
            display_assessment_results(result)

            # Show next step
            console.print("\n[cyan]Next Step:[/cyan]")
            if result.regression:
                console.print(
                    f"  Run: [yellow]brownfield remediate --phase {result.regression.re_entry_phase.value}[/yellow]"
                )
            else:
                console.print("  Run: [yellow]brownfield plan[/yellow]")
                console.print("  This will generate a unified remediation plan")

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
