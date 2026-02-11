"""Tests for remediation orchestrator."""

from datetime import datetime
from pathlib import Path

import pytest

from brownfield.models.assessment import Metrics
from brownfield.models.checkpoint import Task
from brownfield.models.state import BrownfieldState, Phase


class TestRemediationOrchestrator:
    """Test RemediationOrchestrator."""

    @pytest.fixture
    def metrics(self):
        """Create test metrics."""
        return Metrics(
            test_coverage=0.4,
            complexity_avg=12.0,
            complexity_max=20,
            critical_vulnerabilities=0,
            high_vulnerabilities=1,
            medium_vulnerabilities=3,
            build_status="passing",
            documentation_coverage=0.3,
            total_loc=1000,
            test_loc=400,
            git_commits=15,
            git_secrets_found=0,
        )

    @pytest.fixture
    def test_state(self, metrics):
        """Create test state."""
        return BrownfieldState(
            workflow="brownfield",
            schema_version="1.0",
            project_root=Path("/tmp/test"),
            current_phase=Phase.STRUCTURE,
            baseline_metrics=metrics,
            current_metrics=metrics,
            phase_timestamps={"assessment_complete": datetime.utcnow()},
        )

    def test_remediation_result_structure(self, test_state):
        """Test RemediationResult has expected structure."""
        # We can't easily instantiate RemediationOrchestrator without a real project
        # But we can test the result model structure
        from brownfield.models.orchestrator import RemediationResult

        result = RemediationResult(
            phase=Phase.TESTING,
            tasks_completed=[
                Task(
                    task_id="task1",
                    description="Test task",
                    phase=Phase.TESTING,
                    estimated_minutes=10,
                    completed=True,
                )
            ],
            tasks_failed=[],
            git_commits=["abc123"],
            checkpoint_path=Path("/tmp/checkpoint.json"),
            metrics_after=test_state.current_metrics,
            success=True,
            duration_seconds=120,
        )

        assert result.phase == Phase.TESTING
        assert len(result.tasks_completed) == 1
        assert len(result.tasks_failed) == 0
        assert result.success is True

    def test_task_failure_tracking(self):
        """Test failed tasks are tracked correctly."""
        failed_task = Task(
            task_id="failed_task",
            description="This task failed",
            phase=Phase.QUALITY,
            estimated_minutes=20,
            completed=False,
            error_message="ImportError: module not found",
        )

        assert failed_task.completed is False
        assert failed_task.error_message is not None
        assert "module not found" in failed_task.error_message
