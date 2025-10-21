"""Structure command implementation - human-in-the-loop refactoring."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from brownfield.assessment.language_detector import LanguageDetector
from brownfield.config import BrownfieldConfig
from brownfield.models.state import Phase
from brownfield.remediation.structure import StructurePlanGenerator
from brownfield.remediation.structure_verifier import StructureVerifier
from brownfield.state.state_store import StateStore
from brownfield.utils.output_formatter import OutputFormatter

console = Console()


@click.command("structure")
@click.option(
    "--verify",
    is_flag=True,
    help="Verify structure after manual refactoring (instead of generating plan)",
)
@click.option(
    "--output",
    type=click.Path(),
    default=None,
    help="Output path for refactoring plan (default: .specify/memory/structure-plan.md)",
)
@click.option(
    "--format",
    type=click.Choice(["markdown", "json"]),
    default="markdown",
    help="Output format for verification report",
)
def structure(verify: bool, output: str | None, format: str) -> None:
    """Generate refactoring plan or verify structure after manual refactoring.

    Default mode: Generates detailed refactoring plan with IDE instructions.
    Verify mode (--verify): Validates structure compliance after manual refactoring.
    """
    project_root = BrownfieldConfig.get_project_root()
    formatter = OutputFormatter()

    try:
        # Check prerequisites
        state_path = BrownfieldConfig.get_state_path(project_root)
        if not state_path.exists():
            console.print(
                "[red]✗ Error:[/red] Assessment required. Run 'brownfield assess' first."
            )
            raise click.Abort()

        # Load state
        state_store = StateStore(state_path)
        state = state_store.load()

        # Detect language
        detector = LanguageDetector()
        lang_detection = detector.detect(project_root)

        if verify:
            # ========== VERIFY MODE ==========
            console.print("\n[bold blue]🔍 Verifying project structure...[/bold blue]\n")

            # Run verification
            verifier = StructureVerifier(project_root, lang_detection)
            result = verifier.verify()

            # Generate report
            report = verifier.generate_verification_report(result)

            # Save report
            report_dir = BrownfieldConfig.get_reports_dir(project_root)
            report_dir.mkdir(parents=True, exist_ok=True)
            report_path = report_dir / "structure-verification.md"
            report_path.write_text(report, encoding="utf-8")

            # Display summary
            console.print()
            if result.passed:
                console.print(Panel(
                    "[green]✅ Structure verification PASSED![/green]\n\n"
                    "All checks passed:\n"
                    f"  ✓ Directory structure compliant\n"
                    f"  ✓ Build integrity verified\n"
                    f"  ✓ Import integrity confirmed\n"
                    f"  ✓ No stray files in root\n\n"
                    f"Report saved: {report_path.relative_to(project_root)}",
                    title="Verification Complete",
                    border_style="green",
                ))

                # Update state to next phase
                state.advance_phase(Phase.TESTING)
                state_store.save(state)

                # Show workflow progress
                console.print("\n[cyan]Brownfield Workflow Progress:[/cyan]")
                console.print("  [green]✓[/green] 1. Assessment")
                console.print("  [green]✓[/green] 2. Structure  [dim](current)[/dim]")
                console.print("  [ ] 3. Testing")
                console.print("  [ ] 4. Quality")
                console.print("  [ ] 5. Validation")
                console.print("  [ ] 6. Graduation")

                console.print("\n[cyan]Next Step:[/cyan]")
                console.print("  Run: [yellow]brownfield testing[/yellow]")
                console.print("  This will bootstrap test framework and generate tests to achieve 60% coverage")
            else:
                console.print(Panel(
                    "[red]❌ Structure verification FAILED[/red]\n\n"
                    "Failed checks:\n"
                    f"  {'✗' if not result.directory_structure else '✓'} Directory structure\n"
                    f"  {'✗' if not result.build_integrity else '✓'} Build integrity\n"
                    f"  {'✗' if not result.import_integrity else '✓'} Import integrity\n"
                    f"  {'⚠' if not result.no_stray_files else '✓'} No stray files\n\n"
                    f"See full report: {report_path.relative_to(project_root)}",
                    title="Verification Failed",
                    border_style="red",
                ))

                # Show issue summary
                if result.issues:
                    console.print()
                    console.print("[yellow]Issue summary:[/yellow]")
                    error_count = len([i for i in result.issues if i.severity == "error"])
                    warning_count = len([i for i in result.issues if i.severity == "warning"])
                    console.print(f"  ❌ {error_count} errors")
                    console.print(f"  ⚠️  {warning_count} warnings")

                console.print()
                console.print("To fix issues:")
                console.print("  1. Review the verification report")
                console.print("  2. Use IDE refactoring tools to fix issues")
                console.print("  3. Re-run: [cyan]brownfield structure --verify[/cyan]")

        else:
            # ========== PLAN GENERATION MODE (DEFAULT) ==========
            console.print("\n[bold blue]🏗️  Generating structure refactoring plan...[/bold blue]\n")

            # Check if already past this phase
            if state.current_phase not in [Phase.STRUCTURE, Phase.ASSESSMENT]:
                console.print(
                    f"[yellow]⚠️  Warning:[/yellow] Already past structure phase "
                    f"(current: {state.current_phase.value})"
                )
                if not click.confirm("Re-generate structure plan?", default=False):
                    return

            # Analyze structure
            plan_generator = StructurePlanGenerator(project_root, lang_detection)
            analysis = plan_generator.analyze_structure()

            # Generate plan
            markdown_plan = plan_generator.generate_markdown_plan(analysis)
            shell_script = plan_generator.generate_shell_script(analysis)

            # Determine output path
            if output:
                plan_path = Path(output)
            else:
                plan_dir = BrownfieldConfig.get_reports_dir(project_root)
                plan_dir.mkdir(parents=True, exist_ok=True)
                plan_path = plan_dir / "structure-plan.md"

            script_path = plan_path.parent / "structure-moves.sh"

            # Save files
            plan_path.write_text(markdown_plan, encoding="utf-8")
            script_path.write_text(shell_script, encoding="utf-8")
            script_path.chmod(0o755)  # Make executable

            # Display summary
            console.print()
            if analysis.compliant:
                formatter.success("✅ Project structure already compliant!")
                console.print()
                console.print("Your project follows ecosystem conventions.")
                console.print("No refactoring needed.")
                console.print()
                console.print("Next steps:")
                console.print("  Run: [cyan]brownfield testing[/cyan]")

                # Advance to testing phase
                state.advance_phase(Phase.TESTING)
                state_store.save(state)
            else:
                console.print(Panel(
                    f"[yellow]📋 Refactoring plan generated[/yellow]\n\n"
                    f"Files to move: {len(analysis.files_to_move)}\n"
                    f"Directories to create: {len(analysis.missing_directories)}\n"
                    f"Config files to create: {len(analysis.config_files_to_create)}\n\n"
                    f"Plan saved to:\n"
                    f"  📄 {plan_path.relative_to(project_root)}\n"
                    f"  🔧 {script_path.relative_to(project_root)}\n\n"
                    "[bold]⚠️  IMPORTANT: Use IDE refactoring tools![/bold]\n"
                    "IDEs handle import updates correctly via AST parsing.",
                    title="Refactoring Plan Ready",
                    border_style="yellow",
                ))

                console.print()
                console.print("Next steps:")
                console.print("  1. Read the refactoring plan")
                console.print(f"     [cyan]cat {plan_path.relative_to(project_root)}[/cyan]")
                console.print("  2. Use IDE refactoring tools (PyCharm 'Move Module', VSCode drag-and-drop)")
                console.print("  3. Follow IDE-specific instructions in the plan")
                console.print("  4. Verify structure:")
                console.print("     [cyan]brownfield structure --verify[/cyan]")

                # Show file examples
                if analysis.files_to_move:
                    console.print()
                    console.print("[yellow]Example file moves:[/yellow]")
                    for move_op in analysis.files_to_move[:3]:
                        rel_dest = move_op.destination.relative_to(project_root)
                        console.print(f"  • {move_op.source.name} → {rel_dest}")
                    if len(analysis.files_to_move) > 3:
                        console.print(f"  ... and {len(analysis.files_to_move) - 3} more")

    except Exception as e:
        console.print(f"\n[red]✗ Error:[/red] {e}")
        raise click.Abort()
