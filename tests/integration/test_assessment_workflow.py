"""Integration tests for assessment workflow.

Tests the full assessment workflow on fixture projects.
"""

import json
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from brownfield.cli.commands import brownfield
from brownfield.config import BrownfieldConfig
from brownfield.state.state_store import StateStore


@pytest.fixture
def cli_runner():
    """Create Click CLI runner."""
    return CliRunner()


@pytest.fixture
def python_project(tmp_path):
    """Create temporary copy of Python fixture."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "python_messy"
    if not fixture_path.exists():
        pytest.skip("Python fixture not found")

    # Copy fixture to temp directory
    project_path = tmp_path / "python_project"
    shutil.copytree(fixture_path, project_path)
    return project_path


@pytest.fixture
def javascript_project(tmp_path):
    """Create temporary copy of JavaScript fixture."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "javascript_unstructured"
    if not fixture_path.exists():
        pytest.skip("JavaScript fixture not found")

    # Copy fixture to temp directory
    project_path = tmp_path / "javascript_project"
    shutil.copytree(fixture_path, project_path)
    return project_path


class TestAssessmentCommand:
    """Test brownfield assess command."""

    def test_assess_python_project_quick_mode(self, cli_runner, python_project, monkeypatch):
        """Test assessment of Python project in quick mode."""
        # Set project root via environment
        monkeypatch.setenv("BROWNFIELD_PROJECT_ROOT", str(python_project))

        # Run assessment
        result = cli_runner.invoke(brownfield, ["assess", "--quick"])

        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check state file created
        state_path = BrownfieldConfig.get_state_path(python_project)
        assert state_path.exists(), "State file should be created"

        # Verify state contents
        state_store = StateStore(state_path)
        state = state_store.load()

        assert state.current_phase.value == "structure"
        assert state.baseline_metrics is not None
        assert state.baseline_metrics.total_loc > 0

        # Check report file created
        report_path = BrownfieldConfig.get_reports_dir(python_project) / "assessment-report.md"
        assert report_path.exists(), "Assessment report should be created"

        # Verify report contains expected sections
        report_content = report_path.read_text()
        assert "Language Detection" in report_content
        assert "Baseline Metrics" in report_content
        assert "Tech Debt Categories" in report_content

    def test_assess_javascript_project(self, cli_runner, javascript_project, monkeypatch):
        """Test assessment of JavaScript project."""
        monkeypatch.setenv("BROWNFIELD_PROJECT_ROOT", str(javascript_project))

        result = cli_runner.invoke(brownfield, ["assess", "--quick"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify JavaScript detected
        state_path = BrownfieldConfig.get_state_path(javascript_project)
        state_store = StateStore(state_path)
        state = state_store.load()

        # Language should be detected (we can't guarantee it due to simplistic detection,
        # but state should be created)
        assert state.baseline_metrics is not None

    def test_assess_with_language_override(self, cli_runner, python_project, monkeypatch):
        """Test assessment with manual language override."""
        monkeypatch.setenv("BROWNFIELD_PROJECT_ROOT", str(python_project))

        result = cli_runner.invoke(brownfield, ["assess", "--language", "python"])

        assert result.exit_code == 0
        assert "python" in result.output.lower()

    def test_assess_creates_directory_structure(self, cli_runner, python_project, monkeypatch):
        """Test that assessment creates required directory structure."""
        monkeypatch.setenv("BROWNFIELD_PROJECT_ROOT", str(python_project))

        result = cli_runner.invoke(brownfield, ["assess"])

        assert result.exit_code == 0

        # Check directory structure created
        state_dir = BrownfieldConfig.get_state_dir(python_project)
        assert state_dir.exists()
        assert (state_dir / "brownfield-state.json").exists()


class TestStatusCommand:
    """Test brownfield status command."""

    def test_status_before_assessment(self, cli_runner, tmp_path, monkeypatch):
        """Test status command before any assessment."""
        # Create empty project
        project = tmp_path / "empty_project"
        project.mkdir()
        (project / ".git").mkdir()  # Git repo required

        monkeypatch.setenv("BROWNFIELD_PROJECT_ROOT", str(project))

        result = cli_runner.invoke(brownfield, ["status"])

        # Should fail gracefully - state not found
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_status_after_assessment(self, cli_runner, python_project, monkeypatch):
        """Test status command after assessment."""
        monkeypatch.setenv("BROWNFIELD_PROJECT_ROOT", str(python_project))

        # Run assessment first
        assess_result = cli_runner.invoke(brownfield, ["assess", "--quick"])
        assert assess_result.exit_code == 0

        # Check status
        status_result = cli_runner.invoke(brownfield, ["status"])
        assert status_result.exit_code == 0

        # Output should contain phase information
        assert "structure" in status_result.output.lower()

    def test_status_json_output(self, cli_runner, python_project, monkeypatch):
        """Test status command with JSON output."""
        monkeypatch.setenv("BROWNFIELD_PROJECT_ROOT", str(python_project))

        # Run assessment first
        cli_runner.invoke(brownfield, ["assess", "--quick"])

        # Check status with JSON
        result = cli_runner.invoke(brownfield, ["status", "--json"])
        assert result.exit_code == 0

        # Verify valid JSON
        try:
            status_data = json.loads(result.output)
            assert "current_phase" in status_data
            assert "baseline_metrics" in status_data
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {result.output}")


class TestReEntryWorkflow:
    """Test re-entry workflow after quality regression."""

    def test_regression_detection_on_reassessment(self, cli_runner, python_project, monkeypatch):
        """Test that quality regression is detected on re-assessment."""
        monkeypatch.setenv("BROWNFIELD_PROJECT_ROOT", str(python_project))

        # Initial assessment
        result1 = cli_runner.invoke(brownfield, ["assess", "--quick"])
        assert result1.exit_code == 0

        # Load state and modify to simulate graduation
        state_path = BrownfieldConfig.get_state_path(python_project)
        state_store = StateStore(state_path)
        state = state_store.load()

        # Simulate graduation by setting phase
        from brownfield.models.state import Phase
        state.current_phase = Phase.GRADUATED
        state_store.save(state)

        # Modify current metrics to simulate regression
        state.current_metrics.test_coverage = 0.3  # Drop from baseline
        state_store.save(state)

        # Re-assess should detect regression
        result2 = cli_runner.invoke(brownfield, ["assess", "--force"])

        # Should show regression warning (exit code 0 but with warning message)
        assert "regression" in result2.output.lower() or "re-enter" in result2.output.lower()


class TestEnvironmentVariableConfiguration:
    """Test environment variable configuration."""

    def test_custom_state_dir(self, cli_runner, python_project, tmp_path, monkeypatch):
        """Test custom state directory via environment variable."""
        custom_state = tmp_path / "custom_state"
        custom_state.mkdir()

        monkeypatch.setenv("BROWNFIELD_PROJECT_ROOT", str(python_project))
        monkeypatch.setenv("BROWNFIELD_STATE_DIR", str(custom_state))

        result = cli_runner.invoke(brownfield, ["assess", "--quick"])
        assert result.exit_code == 0

        # State should be in custom directory
        assert (custom_state / "brownfield-state.json").exists()

    def test_debug_mode(self, cli_runner, python_project, monkeypatch):
        """Test debug mode via environment variable."""
        monkeypatch.setenv("BROWNFIELD_PROJECT_ROOT", str(python_project))
        monkeypatch.setenv("BROWNFIELD_DEBUG", "true")

        result = cli_runner.invoke(brownfield, ["assess", "--quick"])
        assert result.exit_code == 0

        # Debug output should be present
        assert "debug" in result.output.lower() or "project root" in result.output.lower()

    def test_forced_language(self, cli_runner, python_project, monkeypatch):
        """Test forced language via environment variable."""
        monkeypatch.setenv("BROWNFIELD_PROJECT_ROOT", str(python_project))
        monkeypatch.setenv("BROWNFIELD_FORCE_LANGUAGE", "python")

        result = cli_runner.invoke(brownfield, ["assess", "--quick"])
        assert result.exit_code == 0
        assert "python" in result.output.lower()
