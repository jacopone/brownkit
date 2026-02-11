"""CLI command for showing workflow status."""

import json
import sys

import click
from rich.console import Console
from rich.table import Table

from brownfield.config import BrownfieldConfig
from brownfield.state.state_store import StateStore


@click.command()
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output status as JSON",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed metrics and timestamps",
)
def status(output_json: bool, verbose: bool):
    """
    Show current workflow state and progress.

    Displays:
    - Current phase
    - Baseline and current metrics
    - Phase completion timestamps
    - Re-entry events (if any)
    - Graduation status
    """
    console = Console()
    project_root = BrownfieldConfig.get_project_root()

    # Load state
    state_path = BrownfieldConfig.get_state_path(project_root)
    state_store = StateStore(state_path)

    if not state_store.exists():
        if output_json:
            print(json.dumps({"error": "No brownfield state found"}))
        else:
            console.print("[red]Error:[/red] No brownfield state found. Run 'brownfield assess' first.")
        sys.exit(1)

    state = state_store.load()

    # JSON output
    if output_json:
        status_data = {
            "schema_version": state.schema_version,
            "current_phase": state.current_phase.value
            if hasattr(state.current_phase, "value")
            else state.current_phase,
            "graduated": state.graduated,
            "graduation_timestamp": state.graduation_timestamp.isoformat() if state.graduation_timestamp else None,
            "baseline_metrics": {
                "test_coverage": state.baseline_metrics.test_coverage,
                "complexity_avg": state.baseline_metrics.complexity_avg,
                "critical_vulnerabilities": state.baseline_metrics.critical_vulnerabilities,
                "total_loc": state.baseline_metrics.total_loc,
            },
            "current_metrics": {
                "test_coverage": state.current_metrics.test_coverage,
                "complexity_avg": state.current_metrics.complexity_avg,
                "critical_vulnerabilities": state.current_metrics.critical_vulnerabilities,
                "total_loc": state.current_metrics.total_loc,
            },
            "phase_timestamps": {k: v.isoformat() for k, v in state.phase_timestamps.items()},
            "re_entry_events": [
                {
                    "detected_at": e.detected_at.isoformat(),
                    "trigger": e.trigger,
                    "baseline_value": e.baseline_value,
                    "current_value": e.current_value,
                    "threshold_breached": e.threshold_breached,
                    "re_entry_phase": e.re_entry_phase.value,
                    "resolved": e.resolved,
                    "resolved_at": e.resolved_at.isoformat() if e.resolved_at else None,
                }
                for e in state.re_entry_events
            ],
        }
        print(json.dumps(status_data, indent=2))
        sys.exit(0)

    # Rich console output
    console.print("\n[cyan]📊 Brownfield Workflow Status[/cyan]\n")

    # Current phase
    phase_emoji = {
        "assessment": "🔍",
        "structure": "📁",
        "testing": "🧪",
        "quality": "✨",
        "validation": "✅",
        "graduation": "🎓",
        "graduated": "🎓",
    }

    phase_value = state.current_phase.value if hasattr(state.current_phase, "value") else state.current_phase
    emoji = phase_emoji.get(phase_value, "📌")
    console.print(f"[bold]Current Phase:[/bold] {emoji} {phase_value.upper()}")

    if state.graduated:
        console.print("[bold]Graduation:[/bold] ✅ GRADUATED")
        if state.graduation_timestamp:
            console.print(f"[bold]Graduated At:[/bold] {state.graduation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        console.print("[bold]Graduation:[/bold] ⏳ In Progress")

    console.print()

    # Metrics comparison
    console.print("[cyan]Metrics Overview:[/cyan]\n")

    metrics_table = Table(show_header=True, header_style="bold cyan")
    metrics_table.add_column("Metric", style="white", width=25)
    metrics_table.add_column("Baseline", justify="right", width=15)
    metrics_table.add_column("Current", justify="right", width=15)
    metrics_table.add_column("Change", justify="right", width=15)

    # Test coverage
    baseline_cov = state.baseline_metrics.test_coverage or 0.0
    current_cov = state.current_metrics.test_coverage or 0.0
    cov_change = current_cov - baseline_cov
    cov_change_str = f"{cov_change:+.1%}" if cov_change != 0 else "-"
    cov_change_color = "green" if cov_change >= 0 else "red"

    metrics_table.add_row(
        "Test Coverage",
        f"{baseline_cov:.1%}",
        f"{current_cov:.1%}",
        f"[{cov_change_color}]{cov_change_str}[/{cov_change_color}]",
    )

    # Complexity
    baseline_complex = state.baseline_metrics.complexity_avg or 0.0
    current_complex = state.current_metrics.complexity_avg or 0.0
    complex_change = current_complex - baseline_complex
    complex_change_str = f"{complex_change:+.1f}" if complex_change != 0 else "-"
    complex_change_color = "red" if complex_change > 0 else "green"

    metrics_table.add_row(
        "Avg Complexity",
        f"{baseline_complex:.1f}",
        f"{current_complex:.1f}",
        f"[{complex_change_color}]{complex_change_str}[/{complex_change_color}]",
    )

    # Security
    baseline_sec = state.baseline_metrics.critical_vulnerabilities or 0
    current_sec = state.current_metrics.critical_vulnerabilities or 0
    sec_change = current_sec - baseline_sec
    sec_change_str = f"{sec_change:+d}" if sec_change != 0 else "-"
    sec_change_color = "red" if sec_change > 0 else "green"

    metrics_table.add_row(
        "Critical Vulnerabilities",
        str(baseline_sec),
        str(current_sec),
        f"[{sec_change_color}]{sec_change_str}[/{sec_change_color}]",
    )

    # Lines of code
    baseline_loc = state.baseline_metrics.total_loc or 0
    current_loc = state.current_metrics.total_loc or 0

    metrics_table.add_row(
        "Lines of Code",
        f"{baseline_loc:,}",
        f"{current_loc:,}",
        "-",
    )

    console.print(metrics_table)
    console.print()

    # Phase timeline (verbose mode)
    if verbose and state.phase_timestamps:
        console.print("[cyan]Phase Timeline:[/cyan]\n")

        timeline_table = Table(show_header=True, header_style="bold cyan")
        timeline_table.add_column("Event", style="white", width=30)
        timeline_table.add_column("Timestamp", width=25)

        for event, timestamp in sorted(state.phase_timestamps.items(), key=lambda x: x[1]):
            timeline_table.add_row(
                event.replace("_", " ").title(),
                timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            )

        console.print(timeline_table)
        console.print()

    # Re-entry events
    if state.re_entry_events:
        console.print("[yellow]⚠ Re-entry Events:[/yellow]\n")

        for i, event in enumerate(state.re_entry_events, 1):
            status = "✅ RESOLVED" if event.resolved else "⚠ ACTIVE"
            status_color = "green" if event.resolved else "yellow"

            console.print(f"[bold]{i}. {event.trigger}[/bold] - [{status_color}]{status}[/{status_color}]")
            console.print(f"   Detected: {event.detected_at.strftime('%Y-%m-%d %H:%M:%S')}")
            console.print(f"   Baseline: {event.baseline_value:.2f} → Current: {event.current_value:.2f}")
            console.print(f"   Threshold: {event.threshold_breached:.2f}")
            console.print(f"   Re-entry Phase: {event.re_entry_phase.value}")

            if event.resolved and event.resolved_at:
                console.print(f"   Resolved: {event.resolved_at.strftime('%Y-%m-%d %H:%M:%S')}")

            console.print()

    # Next steps
    if not state.graduated:
        console.print("[cyan]Next Steps:[/cyan]")

        phase_commands = {
            "assessment": "brownfield structure",
            "structure": "brownfield testing",
            "testing": "brownfield quality",
            "quality": "brownfield validate",
            "validation": "brownfield graduate",
        }

        phase_value = state.current_phase.value if hasattr(state.current_phase, "value") else state.current_phase
        next_command = phase_commands.get(phase_value, "brownfield assess")
        console.print(f"  Run: [yellow]{next_command}[/yellow]")
        console.print()

    sys.exit(0)
