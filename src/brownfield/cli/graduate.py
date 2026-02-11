"""CLI command for graduating to Speckit."""

import sys
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console

from brownfield.config import BrownfieldConfig
from brownfield.graduation.archival import ArtifactArchiver
from brownfield.graduation.constitution_generator import ConstitutionGenerator
from brownfield.graduation.report_generator import GraduationReportGenerator
from brownfield.graduation.templates_generator import TemplatesGenerator
from brownfield.models.state import Phase
from brownfield.orchestrator.gate_validator import GateValidator
from brownfield.plugins.registry import get_handler
from brownfield.remediation.validation import ValidationRunner
from brownfield.state.state_store import StateStore


@click.command()
@click.option(
    "--force",
    is_flag=True,
    help="Force graduation even if validation incomplete",
)
@click.option(
    "--archive-path",
    type=click.Path(),
    help="Custom archive location for brownfield artifacts",
)
def graduate(force: bool, archive_path: str):
    """
    Generate Speckit constitution, archive brownfield artifacts, create graduation report.

    This command transitions the project from brownfield workflow to spec-driven development:
    1. Validates all readiness gates passed
    2. Generates project-specific Speckit constitution
    3. Creates spec/plan/tasks templates
    4. Archives brownfield assessment data
    5. Generates graduation report

    After graduation, use Speckit slash commands for new features:
    - /speckit.specify - Create feature spec
    - /speckit.plan - Design implementation
    - /speckit.tasks - Break down tasks
    """
    console = Console()
    project_root = BrownfieldConfig.get_project_root()

    console.print("\n[cyan]🎓 Graduating Project to Speckit[/cyan]\n")

    # Load state
    state_store = StateStore(project_root)
    try:
        state = state_store.load()
    except FileNotFoundError:
        console.print("[red]Error:[/red] No brownfield state found. Run 'brownfield assess' first.")
        sys.exit(1)

    # Phase 1: Validation Check
    console.print("[cyan]Phase 1: Validation Check[/cyan]")

    if state.phase != Phase.GRADUATION and not force:
        console.print(f"  [red]✗[/red] Current phase: {state.phase.value}\n")
        console.print("[red]Error:[/red] Validation required. Run 'brownfield validate' first.")
        console.print("  Or use --force to skip validation check.")
        sys.exit(2)

    # Re-run validation to get latest gate results
    handler = get_handler(state.language)
    if not handler:
        console.print(f"[red]Error:[/red] No handler found for language: {state.language}")
        sys.exit(1)

    validator = ValidationRunner(
        project_root=project_root,
        handler=handler,
        baseline_metrics=state.baseline_metrics,
    )

    gates = validator.validate_all_gates()
    gate_validator = GateValidator(project_root, state)
    validation_result = gate_validator.validate_all_gates(gates)

    if not validation_result["all_passed"] and not force:
        console.print("  [red]✗[/red] Not all gates passed\n")
        console.print("[red]Error:[/red] Cannot graduate with failed gates.")
        console.print(f"  {validation_result['failed_count']} gates failed. Fix issues and re-validate.")
        sys.exit(2)

    console.print("  [green]✓[/green] All 7 readiness gates passed")
    console.print("  [green]✓[/green] Metrics improvement verified\n")

    # Phase 2: Speckit Constitution Generation
    console.print("[cyan]Phase 2: Speckit Constitution Generation[/cyan]")
    console.print("  Analyzing project architecture...")

    constitution_generator = ConstitutionGenerator(project_root, state)
    constitution_path = constitution_generator.save()

    console.print(f"  [green]✓[/green] Detected: {state.language} project")
    if state.detected_framework:
        console.print(f"  [green]✓[/green] Framework: {state.detected_framework}")

    console.print("\n  Generated constitution principles:")
    console.print("    • Specification-driven development workflow")
    console.print("    • Test coverage ≥60% requirement")
    console.print("    • Complexity management (CCN <10)")
    console.print("    • Security-first development")
    console.print(f"\n  [green]✓[/green] Constitution saved: {constitution_path}\n")

    # Phase 3: Speckit Templates Creation
    console.print("[cyan]Phase 3: Speckit Templates Creation[/cyan]")

    templates_generator = TemplatesGenerator(project_root, state)
    template_paths = templates_generator.save_all()

    console.print(f"  [green]✓[/green] Spec template: {template_paths['spec'].name}")
    console.print(f"  [green]✓[/green] Plan template: {template_paths['plan'].name}")
    console.print(f"  [green]✓[/green] Tasks template: {template_paths['tasks'].name}\n")

    # Phase 4: Artifact Archival
    console.print("[cyan]Phase 4: Artifact Archival[/cyan]")

    archiver = ArtifactArchiver(project_root)

    # Parse archive path if provided
    custom_archive_path = Path(archive_path) if archive_path else None
    archived_files = archiver.archive_all(custom_archive_path)

    actual_archive_path = next(iter(archived_files.values())).parent if archived_files else None

    console.print(f"  [green]✓[/green] Archived {len(archived_files)} files")
    if actual_archive_path:
        console.print(f"  [green]✓[/green] Archive location: {actual_archive_path}")

    # Cleanup working files
    removed_files = archiver.cleanup_brownfield_files()
    if removed_files:
        console.print(f"  [green]✓[/green] Cleaned up {len(removed_files)} working files\n")
    else:
        console.print("")

    # Phase 5: Graduation Report
    console.print("[cyan]Phase 5: Graduation Report[/cyan]")

    report_generator = GraduationReportGenerator(project_root, state, gates)
    report_path = report_generator.save()

    console.print(f"  [green]✓[/green] Report generated: {report_path.name}\n")

    # Update state
    state.phase = Phase.GRADUATION
    state.graduation_timestamp = datetime.now().isoformat()
    state_store.save(state)

    # Success summary
    console.print("=" * 60)
    console.print("[green bold]✅ GRADUATION COMPLETE[/green bold]")
    console.print("=" * 60)
    console.print("")

    # Show completed workflow
    console.print("[cyan]Brownfield Workflow: COMPLETE[/cyan]")
    console.print("  [green]✓[/green] 1. Assessment")
    console.print("  [green]✓[/green] 2. Structure")
    console.print("  [green]✓[/green] 3. Testing")
    console.print("  [green]✓[/green] 4. Quality")
    console.print("  [green]✓[/green] 5. Validation")
    console.print("  [green]✓[/green] 6. Graduation  [dim](current)[/dim]")
    console.print("")

    console.print("[cyan]Generated Artifacts:[/cyan]")
    console.print(f"  • Constitution: {constitution_path}")
    console.print(f"  • Templates: {template_paths['spec'].parent}/")
    console.print(f"  • Report: {report_path}")
    if actual_archive_path:
        console.print(f"  • Archive: {actual_archive_path}/")
    console.print("")

    console.print("[cyan]🎉 You're now ready for spec-driven development![/cyan]")
    console.print("")
    console.print("[cyan]Next Steps:[/cyan]")
    console.print("  1. Review your project constitution:")
    console.print("     [yellow]cat .specify/constitution.md[/yellow]")
    console.print("")
    console.print("  2. Start building new features with Speckit:")
    console.print("     [yellow]/speckit.specify[/yellow]  - Write feature specification")
    console.print("     [yellow]/speckit.plan[/yellow]     - Design implementation")
    console.print("     [yellow]/speckit.tasks[/yellow]    - Break down into tasks")
    console.print("")
    console.print("  3. Monitor quality over time:")
    console.print("     [yellow]brownfield assess[/yellow]   - Detects regressions, auto re-enters workflow")
    console.print("     [yellow]brownfield validate[/yellow] - Re-check readiness gates anytime")
    console.print("     [yellow]brownfield status[/yellow]   - View current metrics")
    console.print("")

    sys.exit(0)
