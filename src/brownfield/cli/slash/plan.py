"""Slash command: /brownfield.plan - Generate unified remediation plan."""

import json
import sys

import click
from rich.console import Console

from brownfield.config import BrownfieldConfig
from brownfield.exceptions import BrownfieldError
from brownfield.orchestrator.plan import PlanOrchestrator
from brownfield.orchestrator.utils.display import display_unified_plan

console = Console()


@click.command("brownfield.plan")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results as JSON",
)
def plan_workflow(output_json: bool) -> None:
    """Generate unified remediation plan combining all phases.

    Analyzes structure, testing, and quality needs to create a comprehensive
    remediation roadmap with effort estimates and phase dependencies.

    Part of the brownfield workflow: assess → plan → remediate → validate → graduate
    """
    project_root = BrownfieldConfig.get_project_root()

    if not output_json:
        console.print("\n[bold green]📋 Generating Remediation Plan[/bold green]\n")
        console.print(f"Project: {project_root.name}\n")

    try:
        # Execute planning via orchestrator
        orchestrator = PlanOrchestrator(project_root=project_root)
        plan = orchestrator.execute()

        # Display results
        if output_json:
            output = {
                "estimated_duration_hours": plan.estimated_duration_hours,
                "total_tasks": plan.total_tasks,
                "structure_compliant": plan.structure_plan.compliant if plan.structure_plan else True,
                "testing_framework": plan.testing_plan.framework,
                "smoke_tests_needed": plan.testing_plan.smoke_tests_needed,
                "contract_tests_needed": plan.testing_plan.contract_tests_needed,
                "current_coverage": plan.testing_plan.current_coverage,
                "target_coverage": plan.testing_plan.target_coverage,
                "linter": plan.quality_plan.linter,
                "formatter": plan.quality_plan.formatter,
                "complexity_violations": plan.quality_plan.complexity_violations,
                "security_issues": plan.quality_plan.security_issues,
                "plan_path": str(plan.plan_path),
            }
            console.print(json.dumps(output, indent=2))
        else:
            display_unified_plan(plan)

            # Show next step
            console.print("\n[cyan]Next Step:[/cyan]")
            if plan.structure_plan and not plan.structure_plan.compliant:
                console.print("  Run: [yellow]brownfield remediate --phase structure[/yellow]")
            else:
                console.print("  Run: [yellow]brownfield remediate --phase testing[/yellow]")
            console.print("  This will execute the first remediation phase")

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
