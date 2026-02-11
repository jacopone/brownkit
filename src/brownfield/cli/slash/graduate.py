"""Slash command: /brownfield.graduate - Complete graduation to Speckit."""

import json
import sys

import click
from rich.console import Console

from brownfield.config import BrownfieldConfig
from brownfield.exceptions import BrownfieldError
from brownfield.orchestrator.graduation import GraduationOrchestrator
from brownfield.orchestrator.utils.display import display_graduation_results

console = Console()


@click.command("brownfield.graduate")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results as JSON",
)
def graduate_workflow(output_json: bool) -> None:
    """Complete graduation to Speckit-ready state.

    Generates constitution, creates templates, archives brownfield state,
    and transitions project to spec-driven development workflow.

    Part of the brownfield workflow: assess → plan → remediate → validate → graduate
    """
    project_root = BrownfieldConfig.get_project_root()

    if not output_json:
        console.print("\n[bold green]🎓 Graduating to Speckit[/bold green]\n")
        console.print(f"Project: {project_root.name}\n")

    try:
        # Execute graduation via orchestrator
        orchestrator = GraduationOrchestrator(project_root=project_root)
        result = orchestrator.execute()

        # Display results
        if output_json:
            output = {
                "success": result.success,
                "constitution_path": str(result.constitution_path),
                "template_paths": {k: str(v) for k, v in result.template_paths.items()},
                "archive_path": str(result.archive_path),
                "report_path": str(result.report_path),
                "graduation_timestamp": result.graduation_timestamp.isoformat(),
                "baseline_test_coverage": result.baseline_metrics.test_coverage,
                "final_test_coverage": result.final_metrics.test_coverage,
                "baseline_complexity_avg": result.baseline_metrics.complexity_avg,
                "final_complexity_avg": result.final_metrics.complexity_avg,
            }
            console.print(json.dumps(output, indent=2))
        else:
            display_graduation_results(result)

            # Show completion message
            console.print("\n" + "=" * 60)
            console.print("[bold green]🎉 Congratulations![/bold green]")
            console.print(f"\n{project_root.name} is now Speckit-ready!")
            console.print("\nYou can now use spec-driven development:")
            console.print("  • [cyan]specify[/cyan] - Create feature specifications")
            console.print("  • [cyan]brownfield assess[/cyan] - Monitor for regressions")
            console.print("=" * 60 + "\n")

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
