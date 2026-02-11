"""Post-graduation monitoring for regression detection."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from brownfield.models.assessment import Metrics
from brownfield.models.state import BrownfieldState


class RegressionSeverity(Enum):
    """Severity level of detected regression."""

    INFO = "info"  # Metric changed but within acceptable range
    WARNING = "warning"  # Approaching threshold
    CRITICAL = "critical"  # Threshold breached, re-entry recommended


@dataclass
class RegressionDetection:
    """Details of a detected regression."""

    metric_name: str
    severity: RegressionSeverity
    baseline_value: float
    current_value: float
    threshold: float
    message: str
    detected_at: datetime


class MonitoringIntegration:
    """Monitors graduated projects for quality regressions."""

    # Default regression thresholds (can be overridden from constitution)
    DEFAULT_THRESHOLDS = {
        "test_coverage_drop": 5.0,  # percentage points
        "complexity_increase": 20.0,  # percentage increase
        "critical_vulnerabilities": 0,  # zero tolerance
        "build_failures": 0,  # zero tolerance
    }

    def __init__(self, state: BrownfieldState, thresholds: dict | None = None):
        """Initialize monitoring integration.

        Args:
            state: BrownfieldState with baseline and current metrics
            thresholds: Custom regression thresholds (uses defaults if None)
        """
        self.state = state
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS.copy()

        if not state.baseline_metrics:
            raise ValueError("State must have baseline_metrics for monitoring")

    def check_for_regressions(self, current_metrics: Metrics | None = None) -> list[RegressionDetection]:
        """Check current metrics against baseline for regressions.

        Args:
            current_metrics: Latest metrics (uses state.current_metrics if None)

        Returns:
            List of detected regressions (empty if none found)
        """
        if current_metrics is None:
            current_metrics = self.state.current_metrics

        if not current_metrics:
            raise ValueError("No current metrics available for comparison")

        regressions = []
        baseline = self.state.baseline_metrics
        now = datetime.utcnow()

        # Check test coverage
        coverage_drop = (baseline.test_coverage - current_metrics.test_coverage) * 100
        if coverage_drop > 0:
            threshold = self.thresholds.get("test_coverage_drop", 5.0)

            if coverage_drop >= threshold:
                regressions.append(
                    RegressionDetection(
                        metric_name="test_coverage",
                        severity=RegressionSeverity.CRITICAL,
                        baseline_value=baseline.test_coverage * 100,
                        current_value=current_metrics.test_coverage * 100,
                        threshold=threshold,
                        message=f"Test coverage dropped {coverage_drop:.1f} percentage points "
                        f"(from {baseline.test_coverage * 100:.1f}% to "
                        f"{current_metrics.test_coverage * 100:.1f}%)",
                        detected_at=now,
                    )
                )
            elif coverage_drop >= threshold * 0.7:  # 70% of threshold
                regressions.append(
                    RegressionDetection(
                        metric_name="test_coverage",
                        severity=RegressionSeverity.WARNING,
                        baseline_value=baseline.test_coverage * 100,
                        current_value=current_metrics.test_coverage * 100,
                        threshold=threshold,
                        message=f"Test coverage dropped {coverage_drop:.1f} percentage points "
                        f"(approaching threshold of {threshold})",
                        detected_at=now,
                    )
                )

        # Check complexity increase
        complexity_increase_pct = (
            (current_metrics.complexity_avg - baseline.complexity_avg) / baseline.complexity_avg * 100
        )

        if complexity_increase_pct > 0:
            threshold = self.thresholds.get("complexity_increase", 20.0)

            if complexity_increase_pct >= threshold:
                regressions.append(
                    RegressionDetection(
                        metric_name="complexity",
                        severity=RegressionSeverity.CRITICAL,
                        baseline_value=baseline.complexity_avg,
                        current_value=current_metrics.complexity_avg,
                        threshold=threshold,
                        message=f"Average complexity increased {complexity_increase_pct:.1f}% "
                        f"(from {baseline.complexity_avg:.1f} to "
                        f"{current_metrics.complexity_avg:.1f})",
                        detected_at=now,
                    )
                )
            elif complexity_increase_pct >= threshold * 0.7:
                regressions.append(
                    RegressionDetection(
                        metric_name="complexity",
                        severity=RegressionSeverity.WARNING,
                        baseline_value=baseline.complexity_avg,
                        current_value=current_metrics.complexity_avg,
                        threshold=threshold,
                        message=f"Average complexity increased {complexity_increase_pct:.1f}% "
                        f"(approaching threshold of {threshold}%)",
                        detected_at=now,
                    )
                )

        # Check critical vulnerabilities (zero tolerance)
        if current_metrics.critical_vulnerabilities > 0:
            regressions.append(
                RegressionDetection(
                    metric_name="critical_vulnerabilities",
                    severity=RegressionSeverity.CRITICAL,
                    baseline_value=baseline.critical_vulnerabilities,
                    current_value=current_metrics.critical_vulnerabilities,
                    threshold=0,
                    message=f"Critical vulnerabilities detected: "
                    f"{current_metrics.critical_vulnerabilities} (zero tolerance policy)",
                    detected_at=now,
                )
            )

        # Check build status
        if current_metrics.build_status != "passing":
            regressions.append(
                RegressionDetection(
                    metric_name="build_status",
                    severity=RegressionSeverity.CRITICAL,
                    baseline_value=0,  # passing = 0 failures
                    current_value=1,  # failing = 1 failure
                    threshold=0,
                    message=f"Build status changed to: {current_metrics.build_status}",
                    detected_at=now,
                )
            )

        return regressions

    def should_trigger_reentry(self, regressions: list[RegressionDetection]) -> bool:
        """Determine if regressions warrant workflow re-entry.

        Args:
            regressions: List of detected regressions

        Returns:
            True if critical regressions detected requiring re-entry
        """
        # Any CRITICAL regression triggers re-entry
        return any(r.severity == RegressionSeverity.CRITICAL for r in regressions)

    def generate_monitoring_report(self, regressions: list[RegressionDetection]) -> str:
        """Generate human-readable monitoring report.

        Args:
            regressions: List of detected regressions

        Returns:
            Formatted report string
        """
        lines = ["Post-Graduation Monitoring Report", "=" * 50, ""]

        lines.append(f"Monitoring Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append(f"Project: {self.state.project_root.name if self.state.project_root else 'Unknown'}")
        lines.append("")

        if not regressions:
            lines.append("✅ No regressions detected - all metrics within acceptable ranges")
            lines.append("")
            lines.append("Current Metrics vs Baseline:")
            if self.state.current_metrics and self.state.baseline_metrics:
                curr = self.state.current_metrics
                base = self.state.baseline_metrics
                lines.append(
                    f"  Test Coverage: {curr.test_coverage * 100:.1f}% (baseline: {base.test_coverage * 100:.1f}%)"
                )
                lines.append(f"  Avg Complexity: {curr.complexity_avg:.1f} (baseline: {base.complexity_avg:.1f})")
                lines.append(
                    f"  Critical Vulns: {curr.critical_vulnerabilities} (baseline: {base.critical_vulnerabilities})"
                )
                lines.append(f"  Build Status: {curr.build_status}")

            return "\n".join(lines)

        # Group regressions by severity
        critical = [r for r in regressions if r.severity == RegressionSeverity.CRITICAL]
        warnings = [r for r in regressions if r.severity == RegressionSeverity.WARNING]

        if critical:
            lines.append(f"❌ {len(critical)} CRITICAL regression(s) detected")
            lines.append("")
            lines.append("Critical Regressions:")
            for reg in critical:
                lines.append(f"  • {reg.message}")
            lines.append("")

        if warnings:
            lines.append(f"⚠️  {len(warnings)} warning(s) detected")
            lines.append("")
            lines.append("Warnings:")
            for reg in warnings:
                lines.append(f"  • {reg.message}")
            lines.append("")

        # Recommendation
        if self.should_trigger_reentry(regressions):
            lines.append("🔄 RECOMMENDATION: Trigger BrownKit workflow re-entry")
            lines.append("")
            lines.append("Critical regressions detected. Consider re-running brownfield workflow:")
            lines.append("  1. Review and address the regressions above")
            lines.append("  2. Run /brownkit.assess to re-enter workflow")
            lines.append("  3. Complete remediation phases to restore quality")
        else:
            lines.append("📊 RECOMMENDATION: Address warnings in next sprint")
            lines.append("")
            lines.append("Metrics are approaching thresholds. Take action soon to prevent")
            lines.append("critical regressions.")

        return "\n".join(lines)

    def log_monitoring_check(self, regressions: list[RegressionDetection]) -> None:
        """Log monitoring check to state.

        Args:
            regressions: Detected regressions to log
        """
        # Update last monitor check timestamp
        self.state.speckit.last_monitor_check = datetime.utcnow()

        # Store regression count in state (for tracking over time)
        # You might want to add a field to SpecKitIntegration for this
