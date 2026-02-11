"""Unit tests for Monitoring Integration (Phase 2)."""

from datetime import datetime

import pytest

from brownfield.integration.speckit import (
    MonitoringIntegration,
    RegressionDetection,
    RegressionSeverity,
)
from brownfield.models.assessment import Metrics
from brownfield.models.state import BrownfieldState


class TestMonitoringIntegration:
    """Test MonitoringIntegration class."""

    def test_init_requires_baseline_metrics(self):
        """Test initialization requires baseline metrics."""
        state = BrownfieldState()
        # No baseline_metrics set

        with pytest.raises(ValueError, match="must have baseline_metrics"):
            MonitoringIntegration(state)

    def test_init_with_default_thresholds(self):
        """Test initialization uses default thresholds."""
        state = BrownfieldState()
        state.baseline_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )

        monitor = MonitoringIntegration(state)

        assert monitor.thresholds["test_coverage_drop"] == 5.0
        assert monitor.thresholds["complexity_increase"] == 20.0
        assert monitor.thresholds["critical_vulnerabilities"] == 0
        assert monitor.thresholds["build_failures"] == 0

    def test_init_with_custom_thresholds(self):
        """Test initialization with custom thresholds."""
        state = BrownfieldState()
        state.baseline_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )

        custom_thresholds = {"test_coverage_drop": 10.0, "complexity_increase": 30.0}

        monitor = MonitoringIntegration(state, thresholds=custom_thresholds)

        assert monitor.thresholds["test_coverage_drop"] == 10.0
        assert monitor.thresholds["complexity_increase"] == 30.0

    def test_check_for_regressions_no_regressions(self):
        """Test check_for_regressions returns empty list when no regressions."""
        state = BrownfieldState()
        baseline = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )
        state.baseline_metrics = baseline
        # Current metrics same as baseline
        state.current_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )

        monitor = MonitoringIntegration(state)
        regressions = monitor.check_for_regressions()

        assert regressions == []

    def test_check_for_regressions_coverage_drop_critical(self):
        """Test critical regression when coverage drops significantly."""
        state = BrownfieldState()
        state.baseline_metrics = Metrics(
            test_coverage=0.75,  # 75%
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )
        state.current_metrics = Metrics(
            test_coverage=0.68,  # 68% - dropped 7 points
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )

        monitor = MonitoringIntegration(state)
        regressions = monitor.check_for_regressions()

        assert len(regressions) == 1
        assert regressions[0].metric_name == "test_coverage"
        assert regressions[0].severity == RegressionSeverity.CRITICAL
        assert regressions[0].baseline_value == 75.0
        assert regressions[0].current_value == 68.0

    def test_check_for_regressions_coverage_drop_warning(self):
        """Test warning when coverage drop approaches threshold."""
        state = BrownfieldState()
        state.baseline_metrics = Metrics(
            test_coverage=0.75,  # 75%
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )
        state.current_metrics = Metrics(
            test_coverage=0.71,  # 71% - dropped 4 points (70% of 5.0 threshold)
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )

        monitor = MonitoringIntegration(state)
        regressions = monitor.check_for_regressions()

        assert len(regressions) == 1
        assert regressions[0].metric_name == "test_coverage"
        assert regressions[0].severity == RegressionSeverity.WARNING

    def test_check_for_regressions_complexity_increase_critical(self):
        """Test critical regression when complexity increases significantly."""
        state = BrownfieldState()
        state.baseline_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )
        state.current_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=16.0,  # Increased 28% (from 12.5 to 16.0)
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )

        monitor = MonitoringIntegration(state)
        regressions = monitor.check_for_regressions()

        assert len(regressions) == 1
        assert regressions[0].metric_name == "complexity"
        assert regressions[0].severity == RegressionSeverity.CRITICAL

    def test_check_for_regressions_critical_vulnerabilities(self):
        """Test critical regression for any critical vulnerabilities."""
        state = BrownfieldState()
        state.baseline_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )
        state.current_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=1,  # NEW critical vulnerability
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )

        monitor = MonitoringIntegration(state)
        regressions = monitor.check_for_regressions()

        assert len(regressions) == 1
        assert regressions[0].metric_name == "critical_vulnerabilities"
        assert regressions[0].severity == RegressionSeverity.CRITICAL
        assert "zero tolerance" in regressions[0].message.lower()

    def test_check_for_regressions_build_failure(self):
        """Test critical regression when build fails."""
        state = BrownfieldState()
        state.baseline_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )
        state.current_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="failing",  # Build now failing
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )

        monitor = MonitoringIntegration(state)
        regressions = monitor.check_for_regressions()

        assert len(regressions) == 1
        assert regressions[0].metric_name == "build_status"
        assert regressions[0].severity == RegressionSeverity.CRITICAL

    def test_check_for_regressions_multiple_regressions(self):
        """Test detecting multiple regressions simultaneously."""
        state = BrownfieldState()
        state.baseline_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )
        state.current_metrics = Metrics(
            test_coverage=0.68,  # Coverage dropped
            complexity_avg=16.0,  # Complexity increased
            complexity_max=45,
            critical_vulnerabilities=1,  # Critical vuln
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="failing",  # Build failing
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )

        monitor = MonitoringIntegration(state)
        regressions = monitor.check_for_regressions()

        # Should detect all 4 regressions
        assert len(regressions) == 4
        metrics = {r.metric_name for r in regressions}
        assert "test_coverage" in metrics
        assert "complexity" in metrics
        assert "critical_vulnerabilities" in metrics
        assert "build_status" in metrics

    def test_should_trigger_reentry_with_critical_regressions(self):
        """Test should_trigger_reentry returns True for critical regressions."""
        regressions = [
            RegressionDetection(
                metric_name="test_coverage",
                severity=RegressionSeverity.CRITICAL,
                baseline_value=75.0,
                current_value=68.0,
                threshold=5.0,
                message="Coverage dropped",
                detected_at=datetime.utcnow(),
            )
        ]

        state = BrownfieldState()
        state.baseline_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )

        monitor = MonitoringIntegration(state)

        assert monitor.should_trigger_reentry(regressions) is True

    def test_should_trigger_reentry_with_only_warnings(self):
        """Test should_trigger_reentry returns False for only warnings."""
        regressions = [
            RegressionDetection(
                metric_name="test_coverage",
                severity=RegressionSeverity.WARNING,
                baseline_value=75.0,
                current_value=71.0,
                threshold=5.0,
                message="Coverage approaching threshold",
                detected_at=datetime.utcnow(),
            )
        ]

        state = BrownfieldState()
        state.baseline_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )

        monitor = MonitoringIntegration(state)

        assert monitor.should_trigger_reentry(regressions) is False

    def test_generate_monitoring_report_no_regressions(self, tmp_path):
        """Test generate_monitoring_report with no regressions."""
        state = BrownfieldState()
        state.project_root = tmp_path
        state.baseline_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )
        state.current_metrics = state.baseline_metrics

        monitor = MonitoringIntegration(state)
        regressions = monitor.check_for_regressions()
        report = monitor.generate_monitoring_report(regressions)

        assert "Post-Graduation Monitoring Report" in report
        assert "✅" in report
        assert "No regressions detected" in report
        assert "75.0%" in report  # Coverage percentage

    def test_generate_monitoring_report_with_critical(self, tmp_path):
        """Test generate_monitoring_report with critical regressions."""
        state = BrownfieldState()
        state.project_root = tmp_path
        state.baseline_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )
        state.current_metrics = Metrics(
            test_coverage=0.68,  # Critical drop
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )

        monitor = MonitoringIntegration(state)
        regressions = monitor.check_for_regressions()
        report = monitor.generate_monitoring_report(regressions)

        assert "❌" in report
        assert "CRITICAL" in report
        assert "RECOMMENDATION: Trigger BrownKit workflow re-entry" in report
        assert "/brownkit.assess" in report
