"""Assess command implementation."""

import sys
import time
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from brownfield.assessment.language_detector import LanguageDetector
from brownfield.assessment.metrics_collector import MetricsCollector
from brownfield.assessment.report_generator import ReportGenerator
from brownfield.assessment.tech_debt_analyzer import TechDebtAnalyzer
from brownfield.config import BrownfieldConfig
from brownfield.exceptions import (
    BrownfieldError,
    InvalidStateError,
    LanguageDetectionError,
    MetricsCollectionError,
    StateNotFoundError,
)
from brownfield.models.state import BrownfieldState, Phase
from brownfield.state.report_writer import ReportWriter
from brownfield.state.state_store import StateStore

console = Console()


@click.command("assess")
@click.option(
    "--quick/--full",
    default=True,
    help="Analysis mode (quick: sampling, full: comprehensive)",
)
@click.option(
    "--output",
    type=click.Path(),
    default=".specify/memory/assessment-report.md",
    help="Output path for assessment report",
)
@click.option("--force", is_flag=True, help="Force re-assessment even if report exists")
@click.option(
    "--language",
    type=click.Choice(["python", "javascript", "rust", "go"]),
    help="Override language detection",
)
def assess(quick: bool, output: str, force: bool, language: str) -> None:
    """Run codebase assessment and generate baseline metrics."""
    # Use configured project root (supports BROWNFIELD_PROJECT_ROOT env var)
    project_root = BrownfieldConfig.get_project_root()

    # Apply environment variable defaults
    if not language:
        language = BrownfieldConfig.get_forced_language()
    if quick and BrownfieldConfig.get_default_analysis_mode() == "full":
        quick = False

    # Ensure directories exist
    BrownfieldConfig.ensure_directories(project_root)

    console.print("\n[bold blue]🔍 Assessing codebase...[/bold blue]\n")

    if BrownfieldConfig.is_debug_enabled():
        console.print(f"[dim]Debug: Project root: {project_root}[/dim]")
        console.print(f"[dim]Debug: State dir: {BrownfieldConfig.get_state_dir(project_root)}[/dim]")

    start_time = time.time()

    try:
        # Use rich progress for visual feedback
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            # Language detection
            task1 = progress.add_task("Detecting language...", total=1)
            detector = LanguageDetector()
            try:
                lang_detection = detector.detect(project_root)
                progress.update(task1, completed=1)
            except Exception as e:
                progress.stop()
                raise LanguageDetectionError(str(e)) from e

            # Metrics collection
            mode = "quick" if quick else "full"
            detected_language = language if language else lang_detection.language
            task2 = progress.add_task(f"Collecting metrics ({mode} mode)...", total=1)
            collector = MetricsCollector()
            metrics = collector.collect(project_root, detected_language, mode)
            progress.update(task2, completed=1)

            # Tech debt analysis
            task3 = progress.add_task("Analyzing tech debt...", total=1)
            analyzer = TechDebtAnalyzer()
            tech_debt = analyzer.analyze(project_root)
            progress.update(task3, completed=1)

            # Generate report
            task4 = progress.add_task("Generating report...", total=1)
            duration = int(time.time() - start_time)
            generator = ReportGenerator()
            report = generator.generate(
                project_name=project_root.name,
                project_root=project_root,
                language_detection=lang_detection,
                baseline_metrics=metrics,
                tech_debt=tech_debt,
                analysis_mode=mode,
                duration_seconds=duration,
            )
            progress.update(task4, completed=1)

        # Display results
        console.print("\n[bold cyan]Language Detection:[/bold cyan]")
        console.print(f"  Primary: {lang_detection.language} (confidence: {lang_detection.confidence.name})")
        if lang_detection.version:
            console.print(f"  Version: {lang_detection.version}")
        if lang_detection.framework:
            console.print(f"  Framework: {lang_detection.framework}")

        console.print("\n[bold cyan]Baseline Metrics:[/bold cyan]")
        console.print(f"  Test Coverage: {metrics.test_coverage:.1%}")
        console.print(f"  Avg Complexity: {metrics.complexity_avg:.1f}")
        console.print(f"  Critical Vulnerabilities: {metrics.critical_vulnerabilities}")

        console.print("\n[bold cyan]Tech Debt Categories:[/bold cyan]")
        if tech_debt:
            for debt in tech_debt:
                severity_emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢",
                }.get(debt.severity.lower(), "⚪")
                console.print(f"  {severity_emoji} {debt.severity.upper()} - {debt.category}")
        else:
            console.print("  (No tech debt identified)")

        # Write report
        # Resolve relative paths against project_root
        output_path = Path(output)
        if not output_path.is_absolute():
            output_path = project_root / output_path
        ReportWriter.write_assessment_report(report, output_path)

        # Check for existing state (re-entry scenario)
        state_path = BrownfieldConfig.get_state_path(project_root)
        state_store = StateStore(state_path)

        if state_store.exists():
            # Load existing state and check for regression
            existing_state = state_store.load()

            # Update current metrics
            existing_state.current_metrics = metrics

            # Detect regression if project was graduated
            regression = state_store.detect_regression(existing_state)

            if regression:
                console.print(f"\n[yellow]⚠ Quality Regression Detected:[/yellow] {regression.trigger}")
                console.print(f"  Baseline: {regression.baseline_value:.2f}")
                console.print(f"  Current: {regression.current_value:.2f}")
                console.print(f"  Threshold: {regression.threshold_breached:.2f}")
                console.print(f"\n[yellow]Re-entering {regression.re_entry_phase.value} phase[/yellow]")

                # Handle re-entry via orchestrator
                from brownfield.orchestrator.phase_machine import PhaseOrchestrator
                orchestrator = PhaseOrchestrator(existing_state)
                orchestrator.handle_re_entry(regression)

                state_store.save(existing_state)

                console.print(f"\n[yellow]Recommendation:[/yellow] Run [cyan]brownfield {regression.re_entry_phase.value}[/cyan] to address regression")
                sys.exit(0)
            else:
                # No regression, just update metrics
                state_store.save(existing_state)
                console.print("\n[green]✓[/green] No regression detected - metrics remain within thresholds")
        else:
            # Initialize state (first assessment)
            state = BrownfieldState(
                schema_version="1.0",
                project_root=project_root,
                current_phase=Phase.STRUCTURE,
                baseline_metrics=metrics,
                current_metrics=metrics,
                phase_timestamps={"assessment": datetime.utcnow()},
            )
            state_store.save(state)

        console.print("\n[green]✓[/green] Assessment complete!")
        console.print("\nReport saved to:")
        console.print(f"  {output_path}")
        console.print(f"\nAnalysis Mode: {mode} (completed in {duration}s)")

        # Show workflow progress
        console.print("\n[cyan]Brownfield Workflow Progress:[/cyan]")
        console.print("  [green]✓[/green] 1. Assessment  [dim](current)[/dim]")
        console.print("  [ ] 2. Structure")
        console.print("  [ ] 3. Testing")
        console.print("  [ ] 4. Quality")
        console.print("  [ ] 5. Validation")
        console.print("  [ ] 6. Graduation")

        console.print("\n[cyan]Next Step:[/cyan]")
        console.print("  Run: [yellow]brownfield structure[/yellow]")
        console.print("  This will analyze directory structure and generate refactoring plan")

    except BrownfieldError as e:
        # Handle our custom exceptions with formatted output
        console.print(f"\n[red]✗ Error:[/red] {e.message}")
        if e.suggestion:
            console.print(f"\n[yellow]Suggestion:[/yellow] {e.suggestion}")
        sys.exit(1)
    except Exception as e:
        # Handle unexpected errors
        console.print(f"\n[red]✗ Unexpected Error:[/red] {e}")
        if BrownfieldConfig.is_debug_enabled():
            import traceback
            console.print("\n[dim]Traceback:[/dim]")
            console.print(traceback.format_exc())
        sys.exit(1)
