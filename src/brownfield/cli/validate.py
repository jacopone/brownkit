"""CLI command for validating readiness gates."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from brownfield.orchestrator.gate_validator import GateValidator
from brownfield.plugins.registry import get_handler
from brownfield.remediation.validation import ValidationRunner
from brownfield.state.state_store import StateStore


@click.command()
@click.option(
    "--gate",
    type=str,
    help="Validate specific gate only (by name)",
)
@click.option(
    "--fail-fast",
    is_flag=True,
    help="Stop at first gate failure",
)
@click.option(
    "--report",
    type=click.Path(),
    help="Output validation report to file",
)
def validate(gate: str, fail_fast: bool, report: str):
    """
    Check all 7 readiness gates to determine graduation eligibility.

    Validates:
    - Test Coverage ≥60%
    - Cyclomatic Complexity <10 (or documented)
    - Directory Structure follows conventions
    - Build Status passes cleanly
    - API Documentation ≥80%
    - Security: 0 critical vulnerabilities
    - Git Hygiene: no secrets or large binaries
    """
    console = Console()
    project_root = BrownfieldConfig.get_project_root()

    console.print("\n[cyan]🔍 Validating Readiness Gates[/cyan]\n")

    # Load state
    state_store = StateStore(project_root)
    try:
        state = state_store.load()
    except FileNotFoundError:
        console.print(
            "[red]Error:[/red] No brownfield state found. "
            "Run 'brownfield assess' first."
        )
        sys.exit(1)

    # Get language handler
    handler = get_handler(state.language)
    if not handler:
        console.print(
            f"[red]Error:[/red] No handler found for language: {state.language}"
        )
        sys.exit(1)

    # Create validation runner
    validator = ValidationRunner(
        project_root=project_root,
        handler=handler,
        baseline_metrics=state.baseline_metrics,
    )

    # Run validation
    if gate:
        # Validate specific gate only
        console.print(f"[yellow]Validating single gate:[/yellow] {gate}\n")
        gates = validator.validate_all_gates()
        matching_gates = [g for g in gates if g.name.lower() == gate.lower()]

        if not matching_gates:
            console.print(f"[red]Error:[/red] Gate '{gate}' not found.")
            console.print("\nAvailable gates:")
            for g in gates:
                console.print(f"  - {g.name}")
            sys.exit(1)

        gates_to_validate = matching_gates
    else:
        # Validate all gates
        gates_to_validate = validator.validate_all_gates()

    # Create gate validator for reporting
    gate_validator = GateValidator(project_root, state)

    # Display results
    _display_gate_results(console, gates_to_validate, fail_fast)

    # Generate validation result
    validation_result = gate_validator.validate_all_gates(gates_to_validate)

    # Display summary
    _display_summary(console, validation_result, state)

    # Save report if requested
    if report:
        report_path = Path(report)
        report_content = gate_validator.generate_validation_report(validation_result)
        report_path.write_text(report_content, encoding="utf-8")
        console.print(f"\n[green]✓[/green] Report saved to: {report_path}")

    # Update state if all gates passed
    if validation_result["all_passed"]:
        from brownfield.models.state import Phase
        from brownfield.config import BrownfieldConfig

        state.phase = Phase.GRADUATION
        state_store.save(state)

        # Show workflow progress
        console.print("\n[cyan]Brownfield Workflow Progress:[/cyan]")
        console.print("  [green]✓[/green] 1. Assessment")
        console.print("  [green]✓[/green] 2. Structure")
        console.print("  [green]✓[/green] 3. Testing")
        console.print("  [green]✓[/green] 4. Quality")
        console.print("  [green]✓[/green] 5. Validation  [dim](current)[/dim]")
        console.print("  [ ] 6. Graduation")

        console.print("\n[green]✓[/green] All readiness gates passed!")
        console.print("\n[cyan]Next Step:[/cyan]")
        console.print("  Run: [yellow]brownfield graduate[/yellow]")
        console.print("  This will generate Speckit constitution and complete graduation")
        sys.exit(0)
    else:
        # Recommend phase to return to
        recommended_phase = gate_validator.recommend_next_phase(validation_result)
        if recommended_phase:
            console.print(f"\n[yellow]Recommendation:[/yellow] Return to {recommended_phase.value} phase")

        console.print("\n[red]Cannot graduate until all gates pass.[/red]")
        sys.exit(1)


def _display_gate_results(console: Console, gates: list, fail_fast: bool):
    """Display individual gate results."""
    table = Table(title="Gate Validation Results", show_header=True, header_style="bold cyan")
    table.add_column("Gate", style="white", width=25)
    table.add_column("Threshold", justify="right", width=12)
    table.add_column("Current", justify="right", width=12)
    table.add_column("Status", justify="center", width=10)

    for gate in gates:
        status_icon = "✅ PASS" if gate.passed else "❌ FAIL"
        status_color = "green" if gate.passed else "red"

        # Format threshold and current value based on gate type
        if gate.name in ["Test Coverage", "API Documentation"]:
            threshold_str = f"{gate.threshold:.0%}"
            current_str = f"{gate.current_value:.0%}"
        elif gate.name == "Cyclomatic Complexity":
            threshold_str = f"<{gate.threshold:.0f}"
            current_str = f"{gate.current_value:.0f}"
        elif gate.name == "Security":
            threshold_str = "0 critical"
            current_str = f"{int(gate.current_value)} critical"
        else:
            threshold_str = "Pass" if gate.threshold == 1.0 else str(gate.threshold)
            current_str = "Yes" if gate.current_value >= gate.threshold else "No"

        table.add_row(
            gate.name,
            threshold_str,
            current_str,
            f"[{status_color}]{status_icon}[/{status_color}]",
        )

        # Show justification if present
        if gate.justification:
            console.print(f"  [dim]ℹ {gate.justification}[/dim]")

        # Fail fast if requested
        if fail_fast and not gate.passed:
            console.print(table)
            console.print(f"\n[yellow]Stopped at first failure:[/yellow] {gate.name}")
            console.print(f"[dim]{gate.remediation_guidance}[/dim]")
            return

    console.print(table)


def _display_summary(console: Console, validation_result: dict, state):
    """Display validation summary."""
    console.print("\n" + "=" * 60)

    if validation_result["all_passed"]:
        console.print("[green bold]Result: ALL GATES PASSED ✅[/green bold]")
    else:
        console.print(
            f"[red bold]Result: {validation_result['failed_count']} of "
            f"{validation_result['total_gates']} GATES FAILED ❌[/red bold]"
        )

    console.print("=" * 60)

    # Show metrics improvement if baseline exists
    if state.baseline_metrics and state.baseline_metrics.test_coverage:
        console.print("\n[cyan]Metrics Improvement Summary:[/cyan]")

        # This would show before/after comparison
        # For now, just show current state
        console.print(f"  Language: {state.language}")
        if state.baseline_metrics.lines_of_code:
            console.print(f"  Lines of Code: {state.baseline_metrics.lines_of_code:,}")

    # Show failed gates with remediation
    if validation_result["failed_gates"]:
        console.print("\n[yellow]Failed Gates - Remediation Required:[/yellow]\n")
        for i, failed in enumerate(validation_result["failed_gates"], 1):
            gate = failed["gate"]
            guidance = failed["guidance"]

            console.print(f"{i}. [red]{gate.name}[/red]")
            console.print(f"   {guidance}")
            console.print()
