"""Testing command implementation."""

from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

from brownfield.assessment.language_detector import LanguageDetector
from brownfield.config import BrownfieldConfig
from brownfield.models.state import Phase
from brownfield.plugins.registry import get_handler
from brownfield.remediation.testing import TestingBootstrapper
from brownfield.state.state_store import StateStore

console = Console()


@click.command("testing")
@click.option(
    "--coverage-target",
    type=float,
    default=0.6,
    help="Target coverage percentage (default: 0.6 for 60%)",
)
@click.option(
    "--core-modules",
    type=click.Path(exists=True),
    multiple=True,
    help="Paths to core modules to prioritize for testing",
)
@click.option(
    "--skip-framework-install",
    is_flag=True,
    help="Skip test framework installation (assumes already installed)",
)
@click.option(
    "--test-type",
    type=click.Choice(["smoke", "contract", "both"]),
    default="both",
    help="Type of tests to generate",
)
def testing(coverage_target: float, core_modules: tuple, skip_framework_install: bool, test_type: str) -> None:
    """Bootstrap test infrastructure for brownfield project."""
    project_root = BrownfieldConfig.get_project_root()
    console.print("\n[bold blue]🧪 Bootstrapping test infrastructure...[/bold blue]\n")

    try:
        # Load state
        state_path = BrownfieldConfig.get_state_path(project_root)
        state_store = StateStore(state_path)

        if not state_path.exists():
            console.print("[yellow]⚠[/yellow] No brownfield state found. Run [cyan]brownfield assess[/cyan] first.")
            raise click.Abort()

        state = state_store.load()

        # Verify we're in the right phase
        if state.current_phase not in [Phase.TESTING, Phase.STRUCTURE]:
            console.print(
                f"[yellow]⚠[/yellow] Current phase is {state.current_phase.name}. Expected STRUCTURE or TESTING phase."
            )
            if not click.confirm("Continue anyway?"):
                raise click.Abort()

        # Detect language
        detector = LanguageDetector()
        lang_detection = detector.detect(project_root)
        console.print(f"Language: {lang_detection.language}")

        # Get language handler
        handler = get_handler(lang_detection.language)

        # Convert core_modules to Path objects
        core_module_paths = [Path(m) for m in core_modules] if core_modules else None

        # Bootstrap testing with progress indicators
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            bootstrapper = TestingBootstrapper(handler, project_root)

            if core_module_paths is None:
                task1 = progress.add_task("Identifying core modules...", total=1)
                core_module_paths = bootstrapper._identify_core_modules()
                progress.update(task1, completed=1)

            # Generate tests based on test_type
            test_files = []

            if test_type in ["smoke", "both"]:
                task2 = progress.add_task("Generating smoke tests...", total=1)
                smoke_tests = bootstrapper.generate_smoke_tests(core_module_paths[:10])
                test_files.extend(smoke_tests)
                progress.update(task2, completed=1)

            if test_type in ["contract", "both"]:
                task3 = progress.add_task("Generating contract tests...", total=1)
                contract_tests = bootstrapper.generate_contract_tests(core_module_paths[:10])
                test_files.extend(contract_tests)
                progress.update(task3, completed=1)

            # Run full bootstrap (creates test directory, conftest, etc.)
            if not skip_framework_install:
                task4 = progress.add_task("Installing test framework...", total=1)
                result = handler.bootstrap_tests(project_root, core_module_paths, coverage_target)
                progress.update(task4, completed=1)

        console.print(f"\n[cyan]Found {len(core_module_paths)} core modules[/cyan]")

        if not skip_framework_install:
            console.print(f"\n[green]✓[/green] Test framework: {result.framework}")
            if result.dependencies_added:
                console.print(f"[green]✓[/green] Dependencies added: {', '.join(result.dependencies_added)}")
            console.print(f"[green]✓[/green] Test files created: {len(result.test_files_created)}")

            if result.tests_passing > 0 or result.tests_failing > 0:
                console.print("\nTest Results:")
                console.print(f"  ✓ Passing: {result.tests_passing}")
                if result.tests_failing > 0:
                    console.print(f"  ✗ Failing: {result.tests_failing}")

            console.print(f"\nCoverage: {result.coverage:.1%}")

            if result.coverage >= coverage_target:
                console.print(f"[green]✓[/green] Coverage target met ({coverage_target:.1%})")
            else:
                console.print(
                    f"[yellow]⚠[/yellow] Coverage below target ({result.coverage:.1%} < {coverage_target:.1%})"
                )
        else:
            console.print(f"\n[green]✓[/green] Test files created: {len(test_files)}")

        # Update state
        state.current_phase = Phase.QUALITY
        state.phase_timestamps["testing"] = datetime.utcnow()
        state_store.save(state)

        console.print("\n[green]✓[/green] Testing infrastructure bootstrapped!")

        # Show workflow progress
        console.print("\n[cyan]Brownfield Workflow Progress:[/cyan]")
        console.print("  [green]✓[/green] 1. Assessment")
        console.print("  [green]✓[/green] 2. Structure")
        console.print("  [green]✓[/green] 3. Testing  [dim](current)[/dim]")
        console.print("  [ ] 4. Quality")
        console.print("  [ ] 5. Validation")
        console.print("  [ ] 6. Graduation")

        console.print("\n[cyan]Optional Review:[/cyan]")
        console.print("  • Review generated tests in tests/")
        console.print("  • Run tests manually: [dim]pytest[/dim]")
        console.print("  • Refine tests as needed")

        console.print("\n[cyan]Next Step:[/cyan]")
        console.print("  Run: [yellow]brownfield quality[/yellow]")
        console.print("  This will install linters, formatters, and pre-commit hooks")

    except Exception as e:
        console.print(f"\n[red]✗ Error:[/red] {e}")
        raise click.Abort() from e
