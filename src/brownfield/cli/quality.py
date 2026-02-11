"""Quality gates command implementation."""

from datetime import datetime

import click
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table

from brownfield.assessment.language_detector import LanguageDetector
from brownfield.config import BrownfieldConfig
from brownfield.models.state import Phase
from brownfield.plugins.registry import get_handler
from brownfield.remediation.quality import QualityGatesInstaller
from brownfield.state.state_store import StateStore

console = Console()


@click.command("quality")
@click.option(
    "--skip-linter",
    is_flag=True,
    help="Skip linter installation and configuration",
)
@click.option(
    "--skip-formatter",
    is_flag=True,
    help="Skip formatter installation and configuration",
)
@click.option(
    "--skip-hooks",
    is_flag=True,
    help="Skip pre-commit hooks installation",
)
@click.option(
    "--complexity-threshold",
    type=int,
    default=10,
    help="Maximum allowed cyclomatic complexity (default: 10)",
)
@click.option(
    "--fix-auto",
    is_flag=True,
    help="Automatically fix issues where possible",
)
def quality(
    skip_linter: bool,
    skip_formatter: bool,
    skip_hooks: bool,
    complexity_threshold: int,
    fix_auto: bool,
) -> None:
    """Install quality gates including linters, formatters, and pre-commit hooks."""
    project_root = BrownfieldConfig.get_project_root()
    console.print("\n[bold blue]🔒 Installing quality gates...[/bold blue]\n")

    try:
        # Load state
        state_path = BrownfieldConfig.get_state_path(project_root)
        state_store = StateStore(state_path)

        if not state_path.exists():
            console.print("[yellow]⚠[/yellow] No brownfield state found. Run [cyan]brownfield assess[/cyan] first.")
            raise click.Abort()

        state = state_store.load()

        # Verify we're in the right phase
        if state.current_phase not in [Phase.QUALITY, Phase.TESTING]:
            console.print(
                f"[yellow]⚠[/yellow] Current phase is {state.current_phase.name}. Expected TESTING or QUALITY phase."
            )
            if not click.confirm("Continue anyway?"):
                raise click.Abort()

        # Detect language
        detector = LanguageDetector()
        lang_detection = detector.detect(project_root)
        console.print(f"Language: {lang_detection.language}")

        # Get language handler
        handler = get_handler(lang_detection.language)
        installer = QualityGatesInstaller(handler, project_root)

        # Install quality gates with progress indicators
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            if not skip_linter:
                task1 = progress.add_task("Creating linter configuration...", total=1)
                installer.create_linter_config()
                progress.update(task1, completed=1)

            if not skip_formatter:
                task2 = progress.add_task("Creating formatter configuration...", total=1)
                installer.create_formatter_config()
                progress.update(task2, completed=1)

            if not skip_hooks:
                task3 = progress.add_task("Installing pre-commit hooks...", total=1)
                installer.install_pre_commit_hooks()
                progress.update(task3, completed=1)

            # Run full installation via handler
            task4 = progress.add_task("Running quality gates installation...", total=1)
            result = handler.install_quality_gates(project_root, complexity_threshold)
            progress.update(task4, completed=1)

        # Display results
        console.print("\n[bold]Quality Analysis Results:[/bold]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Tool", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Issues Found", justify="right")

        table.add_row(
            "Linter",
            result.linter,
            str(result.linter_issues_found) if result.linter_issues_found > 0 else "Clean",
        )
        table.add_row(
            "Formatter",
            result.formatter,
            f"{result.formatter_files_changed} files" if result.formatter_files_changed > 0 else "Clean",
        )
        table.add_row(
            "Pre-commit Hooks",
            f"{len(result.hooks_installed)} installed",
            "-",
        )

        console.print(table)

        # Complexity analysis
        console.print("\n[bold]Complexity Analysis:[/bold]")
        if result.complexity_violations > 0:
            console.print(
                f"  [yellow]⚠[/yellow] {result.complexity_violations} functions exceed complexity threshold ({complexity_threshold})"
            )
            console.print("  [cyan]ℹ[/cyan] See complexity-justification.md for details")
        else:
            console.print(f"  [green]✓[/green] All functions below threshold ({complexity_threshold})")

        # Security scan
        console.print("\n[bold]Security Scan:[/bold]")
        security_issues = installer.scan_security_issues()

        total_issues = sum(len(issues) for issues in security_issues.values())

        if total_issues > 0:
            for severity, issues in security_issues.items():
                if issues:
                    severity_emoji = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(severity, "⚪")
                    console.print(f"  {severity_emoji} {severity.upper()}: {len(issues)} issues")
        else:
            console.print("  [green]✓[/green] No security issues found")

        # Auto-fix if requested
        if fix_auto and result.formatter_files_changed > 0:
            console.print("\n[bold]Auto-fixing...[/bold]")
            import subprocess

            try:
                subprocess.run(
                    ["black", "src"],
                    cwd=project_root,
                    timeout=120,
                )
                console.print("  [green]✓[/green] Code formatted with Black")
            except Exception as e:
                console.print(f"  [red]✗[/red] Auto-fix failed: {e}")

        # Update state
        state.current_phase = Phase.VALIDATION
        state.phase_timestamps["quality"] = datetime.utcnow()
        state_store.save(state)

        console.print("\n[green]✓[/green] Quality gates installed!")

        # Show workflow progress
        console.print("\n[cyan]Brownfield Workflow Progress:[/cyan]")
        console.print("  [green]✓[/green] 1. Assessment")
        console.print("  [green]✓[/green] 2. Structure")
        console.print("  [green]✓[/green] 3. Testing")
        console.print("  [green]✓[/green] 4. Quality  [dim](current)[/dim]")
        console.print("  [ ] 5. Validation")
        console.print("  [ ] 6. Graduation")

        # Optional fixes
        if (
            result.linter_issues_found > 0
            or result.formatter_files_changed > 0
            or result.complexity_violations > 0
            or total_issues > 0
        ):
            console.print("\n[cyan]Optional Cleanup:[/cyan]")
            if result.linter_issues_found > 0:
                console.print("  • Review linter issues: [dim]pylint src[/dim]")
            if result.formatter_files_changed > 0:
                console.print("  • Format code: [dim]black src[/dim]")
            if result.complexity_violations > 0:
                console.print("  • Review complexity-justification.md")
            if total_issues > 0:
                console.print("  • Review security issues: [dim]bandit -r src[/dim]")

        console.print("\n[cyan]Next Step:[/cyan]")
        console.print("  Run: [yellow]brownfield validate[/yellow]")
        console.print("  This will check all 7 readiness gates for graduation eligibility")

    except Exception as e:
        console.print(f"\n[red]✗ Error:[/red] {e}")
        import traceback

        traceback.print_exc()
        raise click.Abort() from e
