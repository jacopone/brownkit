"""Display utilities for orchestrator results using Rich console formatting."""

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from brownfield.models.orchestrator import (
    AssessmentResult,
    GraduationResult,
    RemediationResult,
    UnifiedPlan,
    ValidationResult,
)


console = Console()


def display_assessment_results(result: AssessmentResult) -> None:
    """Display assessment results with language detection, metrics, and tech debt.

    Args:
        result: AssessmentResult from AssessmentOrchestrator
    """
    # Header
    console.print(f"\n[bold blue]Assessment Complete[/bold blue] ({result.duration_seconds}s)")
    console.print(f"Phase: {result.current_phase.value}")
    console.print(f"Report: {result.report_path}\n")

    # Language detection
    console.print(f"[bold]Language:[/bold] {result.language_detection.language}")
    console.print(f"[bold]Confidence:[/bold] {result.language_detection.confidence.name}")
    if result.language_detection.version:
        console.print(f"[bold]Version:[/bold] {result.language_detection.version}")
    if result.language_detection.framework:
        console.print(f"[bold]Framework:[/bold] {result.language_detection.framework}")

    if result.language_detection.secondary_languages:
        console.print("\n[bold]Secondary Languages:[/bold]")
        for lang, confidence in result.language_detection.secondary_languages:
            console.print(f"  • {lang} ({confidence:.0%})")

    # Baseline metrics
    metrics_table = Table(title="\nBaseline Metrics", show_header=True)
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", justify="right")

    metrics_table.add_row("Total Lines", str(result.baseline_metrics.total_loc))
    metrics_table.add_row("Test Lines", str(result.baseline_metrics.test_loc))
    metrics_table.add_row("Test Coverage", f"{result.baseline_metrics.test_coverage:.1%}")
    metrics_table.add_row("Avg Complexity", f"{result.baseline_metrics.complexity_avg:.1f}")
    metrics_table.add_row("Max Complexity", str(result.baseline_metrics.complexity_max))
    metrics_table.add_row("Doc Coverage", f"{result.baseline_metrics.documentation_coverage:.1%}")
    metrics_table.add_row("Build Status", result.baseline_metrics.build_status)

    console.print(metrics_table)

    # Tech debt
    if result.tech_debt:
        debt_table = Table(title="\nTechnical Debt", show_header=True)
        debt_table.add_column("Category", style="cyan")
        debt_table.add_column("Severity", style="yellow")
        debt_table.add_column("Issues", justify="right")
        debt_table.add_column("Est. Time")

        for debt in result.tech_debt:
            severity_color = {
                "critical": "red",
                "high": "yellow",
                "medium": "blue",
                "low": "green"
            }.get(debt.severity.lower(), "white")

            debt_table.add_row(
                debt.category,
                f"[{severity_color}]{debt.severity.upper()}[/{severity_color}]",
                str(len(debt.issues)),
                debt.estimated_remediation_time
            )

        console.print(debt_table)

    # Regression detection
    if result.regression:
        console.print(
            Panel(
                f"[yellow]Regression Detected[/yellow]\n"
                f"Trigger: {result.regression.trigger}\n"
                f"Re-entry Phase: {result.regression.re_entry_phase.value}\n"
                f"Details: {result.regression.details}",
                border_style="yellow"
            )
        )


def display_unified_plan(plan: UnifiedPlan) -> None:
    """Display unified remediation plan with phases, tasks, and estimates.

    Args:
        plan: UnifiedPlan from PlanOrchestrator
    """
    # Header
    console.print(f"\n[bold green]Unified Remediation Plan[/bold green]")
    console.print(f"Plan: {plan.plan_path}")
    console.print(f"Total Tasks: {plan.total_tasks}")
    console.print(f"Estimated Duration: {plan.estimated_duration_hours:.1f} hours\n")

    # Structure plan
    if plan.structure_plan:
        structure_tree = Tree("[bold cyan]Structure Phase[/bold cyan]")

        if plan.structure_plan.compliant:
            structure_tree.add("[green]✓[/green] Already compliant")
        else:
            structure_tree.add(f"[yellow]{len(plan.structure_plan.files_to_move)}[/yellow] files to move")
            structure_tree.add(f"[yellow]{len(plan.structure_plan.directories_to_create)}[/yellow] directories to create")

            if plan.structure_plan.issues_found:
                issues_node = structure_tree.add(f"[red]{len(plan.structure_plan.issues_found)}[/red] issues found")
                for issue in plan.structure_plan.issues_found[:3]:  # Show first 3
                    issues_node.add(issue)

        console.print(structure_tree)

    # Testing plan
    testing_tree = Tree("[bold cyan]Testing Phase[/bold cyan]")
    testing_tree.add(f"Framework: {plan.testing_plan.framework}")
    testing_tree.add(f"Core Modules: {len(plan.testing_plan.core_modules)}")
    testing_tree.add(f"Smoke Tests Needed: {plan.testing_plan.smoke_tests_needed}")
    testing_tree.add(f"Contract Tests Needed: {plan.testing_plan.contract_tests_needed}")
    testing_tree.add(
        f"Coverage: {plan.testing_plan.current_coverage:.1f}% → "
        f"{plan.testing_plan.target_coverage:.1f}%"
    )

    console.print(testing_tree)

    # Quality plan
    quality_tree = Tree("[bold cyan]Quality Phase[/bold cyan]")
    quality_tree.add(f"Linter: {plan.quality_plan.linter}")
    quality_tree.add(f"Formatter: {plan.quality_plan.formatter}")
    quality_tree.add(f"Hooks to Install: {', '.join(plan.quality_plan.hooks_to_install)}")

    if plan.quality_plan.complexity_violations > 0:
        quality_tree.add(f"[yellow]Complexity Violations: {plan.quality_plan.complexity_violations}[/yellow]")

    if plan.quality_plan.security_issues > 0:
        quality_tree.add(f"[red]Security Issues: {plan.quality_plan.security_issues}[/red]")

    console.print(quality_tree)

    # Dependencies
    if plan.dependencies:
        console.print("\n[bold]Phase Dependencies:[/bold]")
        for phase, prereqs in plan.dependencies.items():
            prereqs_str = ", ".join(prereqs) if prereqs else "None"
            console.print(f"  {phase}: {prereqs_str}")


def display_remediation_results(result: RemediationResult) -> None:
    """Display remediation results with task status, commits, and metrics.

    Args:
        result: RemediationResult from RemediationOrchestrator
    """
    # Header
    status_icon = "[green]✓[/green]" if result.success else "[red]✗[/red]"
    console.print(f"\n[bold]{status_icon} Remediation: {result.phase.value}[/bold] ({result.duration_seconds}s)")

    # Task summary
    tasks_table = Table(show_header=True, title="Task Summary")
    tasks_table.add_column("Status", style="cyan")
    tasks_table.add_column("Count", justify="right")

    tasks_table.add_row("Completed", f"[green]{len(result.tasks_completed)}[/green]")
    tasks_table.add_row("Failed", f"[red]{len(result.tasks_failed)}[/red]")
    tasks_table.add_row("Total", str(len(result.tasks_completed) + len(result.tasks_failed)))

    console.print(tasks_table)

    # Failed tasks (if any)
    if result.tasks_failed:
        failed_table = Table(title="Failed Tasks", show_header=True)
        failed_table.add_column("Task", style="yellow")
        failed_table.add_column("Description")

        for task in result.tasks_failed:
            failed_table.add_row(task.name, task.description[:60] + "..." if len(task.description) > 60 else task.description)

        console.print(failed_table)

    # Git commits
    if result.git_commits:
        console.print(f"\n[bold]Git Commits:[/bold] {len(result.git_commits)}")
        for commit in result.git_commits[:5]:  # Show first 5
            console.print(f"  • {commit}")

    # Checkpoint
    if result.checkpoint_path:
        console.print(f"\n[bold]Checkpoint:[/bold] {result.checkpoint_path}")

    # Metrics after
    console.print(f"\n[bold]Metrics After:[/bold]")
    console.print(f"  Test Coverage: {result.metrics_after.test_coverage:.1%}")
    console.print(f"  Avg Complexity: {result.metrics_after.complexity_avg:.1f}")
    console.print(f"  Max Complexity: {result.metrics_after.complexity_max}")


def display_validation_results(result: ValidationResult) -> None:
    """Display validation results with readiness gates status.

    Args:
        result: ValidationResult from ValidationOrchestrator
    """
    # Header
    status_icon = "[green]✓[/green]" if result.all_passed else "[red]✗[/red]"
    console.print(f"\n[bold]{status_icon} Validation Results[/bold]")
    console.print(f"Report: {result.report_path}")
    console.print(f"Timestamp: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Gates table
    gates_table = Table(title="Readiness Gates", show_header=True)
    gates_table.add_column("Gate", style="cyan")
    gates_table.add_column("Status", justify="center")
    gates_table.add_column("Current", justify="right")
    gates_table.add_column("Threshold", justify="right")
    gates_table.add_column("Message")

    for gate_result in result.gates:
        status_icon = "[green]✓[/green]" if gate_result.passed else "[red]✗[/red]"
        gates_table.add_row(
            gate_result.gate.name,
            status_icon,
            f"{gate_result.current_value:.1f}",
            f"{gate_result.threshold:.1f}",
            gate_result.message
        )

    console.print(gates_table)

    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Passed: [green]{len(result.gates) - result.failed_count}[/green]")
    console.print(f"  Failed: [red]{result.failed_count}[/red]")

    # Recommendation
    if result.recommended_phase:
        console.print(
            Panel(
                f"[yellow]Recommended Action[/yellow]\n"
                f"Return to phase: {result.recommended_phase.value}\n"
                f"Address failed gates before graduation.",
                border_style="yellow"
            )
        )


def display_graduation_results(result: GraduationResult) -> None:
    """Display graduation results with artifacts and metrics comparison.

    Args:
        result: GraduationResult from GraduationOrchestrator
    """
    # Header
    status_icon = "[green]✓[/green]" if result.success else "[red]✗[/red]"
    console.print(f"\n[bold]{status_icon} Graduation Complete[/bold]")
    console.print(f"Timestamp: {result.graduation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Artifacts
    artifacts_tree = Tree("[bold green]Generated Artifacts[/bold green]")
    artifacts_tree.add(f"Constitution: {result.constitution_path}")

    templates_node = artifacts_tree.add(f"Templates: {len(result.template_paths)}")
    for template_name, template_path in result.template_paths.items():
        templates_node.add(f"{template_name}: {template_path}")

    artifacts_tree.add(f"Archive: {result.archive_path}")
    artifacts_tree.add(f"Report: {result.report_path}")

    console.print(artifacts_tree)

    # Metrics comparison
    metrics_table = Table(title="\nMetrics Improvement", show_header=True)
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Baseline", justify="right")
    metrics_table.add_column("Final", justify="right")
    metrics_table.add_column("Change", justify="right")

    # Test coverage (stored as 0.0-1.0)
    coverage_change = result.final_metrics.test_coverage - result.baseline_metrics.test_coverage
    coverage_color = "green" if coverage_change >= 0 else "red"
    metrics_table.add_row(
        "Test Coverage",
        f"{result.baseline_metrics.test_coverage:.1%}",
        f"{result.final_metrics.test_coverage:.1%}",
        f"[{coverage_color}]{coverage_change:+.1%}[/{coverage_color}]"
    )

    # Average complexity
    complexity_change = result.final_metrics.complexity_avg - result.baseline_metrics.complexity_avg
    complexity_color = "green" if complexity_change <= 0 else "red"
    metrics_table.add_row(
        "Avg Complexity",
        f"{result.baseline_metrics.complexity_avg:.1f}",
        f"{result.final_metrics.complexity_avg:.1f}",
        f"[{complexity_color}]{complexity_change:+.1f}[/{complexity_color}]"
    )

    # Max complexity
    max_complexity_change = result.final_metrics.complexity_max - result.baseline_metrics.complexity_max
    max_complexity_color = "green" if max_complexity_change <= 0 else "red"
    metrics_table.add_row(
        "Max Complexity",
        str(result.baseline_metrics.complexity_max),
        str(result.final_metrics.complexity_max),
        f"[{max_complexity_color}]{max_complexity_change:+d}[/{max_complexity_color}]"
    )

    # Documentation coverage
    doc_change = result.final_metrics.documentation_coverage - result.baseline_metrics.documentation_coverage
    doc_color = "green" if doc_change >= 0 else "red"
    metrics_table.add_row(
        "Doc Coverage",
        f"{result.baseline_metrics.documentation_coverage:.1%}",
        f"{result.final_metrics.documentation_coverage:.1%}",
        f"[{doc_color}]{doc_change:+.1%}[/{doc_color}]"
    )

    console.print(metrics_table)

    # Next steps
    console.print(
        Panel(
            "[bold green]Next Steps[/bold green]\n"
            "1. Review constitution.md for project principles\n"
            "2. Use Spec Kit templates for new features\n"
            "3. Monitor metrics for regressions (brownfield status)\n"
            "4. Re-assess if quality thresholds breached",
            border_style="green"
        )
    )
