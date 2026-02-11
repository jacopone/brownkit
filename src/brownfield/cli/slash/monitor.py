"""Slash command: /brownkit.monitor - Post-graduation monitoring."""

import sys

import click
from rich.console import Console

from brownfield.config import BrownfieldConfig
from brownfield.exceptions import BrownfieldError, InvalidStateError
from brownfield.integration.speckit import MonitoringIntegration
from brownfield.integration.speckit.monitoring import RegressionSeverity
from brownfield.models.workflow import WorkflowPhase
from brownfield.state.state_store import StateStore

console = Console()


@click.command("brownfield.monitor")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results as JSON",
)
@click.option(
    "--fail-on-critical",
    is_flag=True,
    help="Exit with non-zero status if critical regressions detected",
)
def monitor_workflow(output_json: bool, fail_on_critical: bool) -> None:
    """Monitor post-graduation quality metrics and detect regressions (workflow command).

    This command compares current metrics against graduation baseline to detect
    quality regressions. It's designed to run after graduation to ensure quality
    standards are maintained.

    Part of post-graduation maintenance: monitor → (re-entry if needed)
    """
    project_root = BrownfieldConfig.get_project_root()

    if not output_json:
        console.print("\n[bold blue]📊 Post-Graduation Monitoring[/bold blue]\n")
        console.print(f"Project: {project_root.name}\n")

    try:
        # Load current state
        state_path = BrownfieldConfig.get_state_path(project_root)
        state_store = StateStore(state_path)

        if not state_store.exists():
            raise InvalidStateError(
                "Project not initialized. Run /brownkit.assess first.",
                suggestion="Initialize the project with /brownkit.assess",
            )

        state = state_store.load()

        # Verify project is graduated
        if state.workflow_state.current_phase != WorkflowPhase.SPEC_KIT_READY:
            raise InvalidStateError(
                f"Monitoring only available after graduation. Current phase: {state.workflow_state.current_phase.value}",
                suggestion="Complete the workflow and graduate before monitoring",
            )

        # Verify baseline metrics exist
        if not state.baseline_metrics:
            raise InvalidStateError(
                "No baseline metrics found. Cannot compare for regressions.",
                suggestion="Re-run graduation to establish baseline",
            )

        # Initialize monitoring integration
        monitor = MonitoringIntegration(state)

        # Run current assessment to get fresh metrics
        from brownfield.orchestrator.assessment import AssessmentOrchestrator

        orchestrator = AssessmentOrchestrator(project_root=project_root, quick_mode=True)
        result = orchestrator.execute()

        # Update current metrics
        state.current_metrics = result.baseline_metrics

        # Check for regressions
        regressions = monitor.check_for_regressions()

        # Determine if re-entry is needed
        needs_reentry = monitor.should_trigger_reentry(regressions)

        # Save updated state
        state_store.save(state)

        # Display results
        if output_json:
            import json

            output = {
                "project": project_root.name,
                "phase": state.workflow_state.current_phase.value,
                "baseline_coverage": state.baseline_metrics.test_coverage * 100,
                "current_coverage": state.current_metrics.test_coverage * 100,
                "regressions_count": len(regressions),
                "critical_count": sum(1 for r in regressions if r.severity == RegressionSeverity.CRITICAL),
                "warning_count": sum(1 for r in regressions if r.severity == RegressionSeverity.WARNING),
                "needs_reentry": needs_reentry,
                "regressions": [
                    {
                        "metric": r.metric_name,
                        "severity": r.severity.value,
                        "baseline": r.baseline_value,
                        "current": r.current_value,
                        "threshold": r.threshold,
                        "message": r.message,
                    }
                    for r in regressions
                ],
            }
            console.print(json.dumps(output, indent=2))
        else:
            # Generate and display monitoring report
            report = monitor.generate_monitoring_report(regressions)
            console.print(report)

            # Show next steps
            console.print("\n[cyan]Next Steps:[/cyan]")
            if needs_reentry:
                console.print("  [yellow]⚠️  Critical regressions detected - workflow re-entry recommended[/yellow]")
                console.print("  Run: [yellow]brownfield brownfield.assess[/yellow] to re-enter workflow")
            elif regressions:
                console.print("  [yellow]⚠️  Warnings detected - consider addressing proactively[/yellow]")
                console.print("  Continue monitoring regularly (weekly/bi-weekly)")
            else:
                console.print("  [green]✓[/green] All metrics healthy")
                console.print("  Continue using Spec-Kit workflow")
                console.print("  Re-run monitoring regularly to track quality")

        # Exit with appropriate status
        if fail_on_critical and needs_reentry:
            sys.exit(1)

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
