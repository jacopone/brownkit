"""Tests for phase transition validation."""

import pytest
from datetime import datetime
from pathlib import Path

from brownfield.orchestrator.phase_machine import PhaseOrchestrator
from brownfield.models.state import Phase, BrownfieldState
from brownfield.models.assessment import Metrics


class TestPhaseTransitions:
    """Test phase transition rules."""

    @pytest.fixture
    def minimal_metrics(self):
        """Create minimal metrics for testing."""
        return Metrics(
            test_coverage=0.0,
            complexity_avg=15.0,
            complexity_max=25,
            critical_vulnerabilities=0,
            high_vulnerabilities=0,
            medium_vulnerabilities=0,
            build_status="unknown",
            documentation_coverage=0.0,
            total_loc=1000,
            test_loc=0,
            git_commits=1,
            git_secrets_found=0,
        )

    @pytest.fixture
    def good_metrics(self):
        """Create metrics that pass requirements."""
        return Metrics(
            test_coverage=0.7,
            complexity_avg=8.0,
            complexity_max=12,
            critical_vulnerabilities=0,
            high_vulnerabilities=0,
            medium_vulnerabilities=0,
            build_status="passing",
            documentation_coverage=0.6,
            total_loc=1000,
            test_loc=700,
            git_commits=10,
            git_secrets_found=0,
        )

    @pytest.fixture
    def assessment_state(self, minimal_metrics):
        """Create state in ASSESSMENT phase."""
        return BrownfieldState(
            schema_version="1.0",
            project_root=Path("/tmp/test"),
            current_phase=Phase.ASSESSMENT,
            baseline_metrics=minimal_metrics,
            current_metrics=minimal_metrics,
        )

    def test_can_advance_from_assessment_to_structure(self, assessment_state):
        """Test valid transition: ASSESSMENT → STRUCTURE."""
        orchestrator = PhaseOrchestrator(assessment_state)
        can_advance, reason = orchestrator.can_advance_to(Phase.STRUCTURE)

        assert can_advance is True
        assert reason is None

    def test_cannot_advance_from_assessment_to_testing(self, assessment_state):
        """Test invalid transition: ASSESSMENT → TESTING (skip phase)."""
        orchestrator = PhaseOrchestrator(assessment_state)
        can_advance, reason = orchestrator.can_advance_to(Phase.TESTING)

        assert can_advance is False
        assert "Cannot transition" in reason
        assert "testing" in reason.lower()
        assert "structure" in reason.lower()

    def test_cannot_advance_from_assessment_to_quality(self, assessment_state):
        """Test invalid transition: ASSESSMENT → QUALITY (skip phases)."""
        orchestrator = PhaseOrchestrator(assessment_state)
        can_advance, reason = orchestrator.can_advance_to(Phase.QUALITY)

        assert can_advance is False
        assert "Cannot transition" in reason

    def test_cannot_advance_from_assessment_to_graduated(self, assessment_state):
        """Test invalid transition: ASSESSMENT → GRADUATED (skip all phases)."""
        orchestrator = PhaseOrchestrator(assessment_state)
        can_advance, reason = orchestrator.can_advance_to(Phase.GRADUATED)

        assert can_advance is False
        assert "Cannot transition" in reason

    def test_sequential_phase_progression(self, assessment_state):
        """Test correct sequential phase progression."""
        orchestrator = PhaseOrchestrator(assessment_state)

        # ASSESSMENT → STRUCTURE
        can_advance, _ = orchestrator.can_advance_to(Phase.STRUCTURE)
        assert can_advance is True

        # Mark structure complete and move to structure
        assessment_state.advance_phase(Phase.STRUCTURE)
        assessment_state.phase_timestamps["structure_complete"] = datetime.utcnow()

        # STRUCTURE → TESTING
        can_advance, _ = orchestrator.can_advance_to(Phase.TESTING)
        assert can_advance is True

        # Mark testing complete and move to testing
        assessment_state.advance_phase(Phase.TESTING)
        assessment_state.phase_timestamps["testing_complete"] = datetime.utcnow()
        assessment_state.current_metrics.test_coverage = 0.7  # Meet coverage requirement

        # TESTING → QUALITY
        can_advance, _ = orchestrator.can_advance_to(Phase.QUALITY)
        assert can_advance is True

        # Mark quality complete and move to quality
        assessment_state.advance_phase(Phase.QUALITY)
        assessment_state.phase_timestamps["quality_complete"] = datetime.utcnow()

        # QUALITY → VALIDATION
        can_advance, _ = orchestrator.can_advance_to(Phase.VALIDATION)
        assert can_advance is True


class TestRequirementChecking:
    """Test phase requirement validation."""

    @pytest.fixture
    def metrics_no_coverage(self):
        """Metrics with no test coverage."""
        return Metrics(
            test_coverage=0.0,
            complexity_avg=8.0,
            complexity_max=12,
            critical_vulnerabilities=0,
            high_vulnerabilities=0,
            medium_vulnerabilities=0,
            build_status="passing",
            documentation_coverage=0.5,
            total_loc=1000,
            test_loc=0,
            git_commits=5,
            git_secrets_found=0,
        )

    @pytest.fixture
    def metrics_with_coverage(self):
        """Metrics with good test coverage."""
        return Metrics(
            test_coverage=0.7,
            complexity_avg=8.0,
            complexity_max=12,
            critical_vulnerabilities=0,
            high_vulnerabilities=0,
            medium_vulnerabilities=0,
            build_status="passing",
            documentation_coverage=0.6,
            total_loc=1000,
            test_loc=700,
            git_commits=10,
            git_secrets_found=0,
        )

    def test_cannot_advance_without_baseline_metrics(self):
        """Test transition blocked when baseline_metrics is None."""
        state = BrownfieldState(
            schema_version="1.0",
            project_root=Path("/tmp/test"),
            current_phase=Phase.ASSESSMENT,
            baseline_metrics=None,  # Missing baseline metrics
            current_metrics=None,
        )

        orchestrator = PhaseOrchestrator(state)
        can_advance, reason = orchestrator.can_advance_to(Phase.STRUCTURE)

        assert can_advance is False
        assert "Unmet requirements" in reason
        assert "baseline_metrics_captured" in reason

    def test_cannot_advance_to_testing_without_structure_complete(
        self, metrics_no_coverage
    ):
        """Test TESTING requires STRUCTURE phase completion."""
        state = BrownfieldState(
            schema_version="1.0",
            project_root=Path("/tmp/test"),
            current_phase=Phase.STRUCTURE,
            baseline_metrics=metrics_no_coverage,
            current_metrics=metrics_no_coverage,
        )
        # No structure_complete timestamp

        orchestrator = PhaseOrchestrator(state)
        can_advance, reason = orchestrator.can_advance_to(Phase.TESTING)

        assert can_advance is False
        assert "structure_phase_completed" in reason

    def test_can_advance_to_testing_with_structure_complete(self, metrics_no_coverage):
        """Test TESTING allowed when STRUCTURE is complete."""
        state = BrownfieldState(
            schema_version="1.0",
            project_root=Path("/tmp/test"),
            current_phase=Phase.STRUCTURE,
            baseline_metrics=metrics_no_coverage,
            current_metrics=metrics_no_coverage,
            phase_timestamps={"structure_complete": datetime.utcnow()},
        )

        orchestrator = PhaseOrchestrator(state)
        can_advance, reason = orchestrator.can_advance_to(Phase.TESTING)

        assert can_advance is True
        assert reason is None

    def test_cannot_advance_to_quality_without_coverage(self, metrics_no_coverage):
        """Test QUALITY requires 60% test coverage."""
        state = BrownfieldState(
            schema_version="1.0",
            project_root=Path("/tmp/test"),
            current_phase=Phase.TESTING,
            baseline_metrics=metrics_no_coverage,
            current_metrics=metrics_no_coverage,  # Coverage is 0.0
            phase_timestamps={
                "structure_complete": datetime.utcnow(),
                "testing_complete": datetime.utcnow(),
            },
        )

        orchestrator = PhaseOrchestrator(state)
        can_advance, reason = orchestrator.can_advance_to(Phase.QUALITY)

        assert can_advance is False
        assert "test_coverage_min_60" in reason

    def test_can_advance_to_quality_with_coverage(self, metrics_with_coverage):
        """Test QUALITY allowed with 60%+ coverage."""
        state = BrownfieldState(
            schema_version="1.0",
            project_root=Path("/tmp/test"),
            current_phase=Phase.TESTING,
            baseline_metrics=metrics_with_coverage,
            current_metrics=metrics_with_coverage,  # Coverage is 0.7
            phase_timestamps={
                "structure_complete": datetime.utcnow(),
                "testing_complete": datetime.utcnow(),
            },
        )

        orchestrator = PhaseOrchestrator(state)
        can_advance, reason = orchestrator.can_advance_to(Phase.QUALITY)

        assert can_advance is True
        assert reason is None

    def test_cannot_advance_to_graduated_without_validation(self, metrics_with_coverage):
        """Test GRADUATED requires validation_passed."""
        state = BrownfieldState(
            schema_version="1.0",
            project_root=Path("/tmp/test"),
            current_phase=Phase.VALIDATION,
            baseline_metrics=metrics_with_coverage,
            current_metrics=metrics_with_coverage,
            phase_timestamps={
                "structure_complete": datetime.utcnow(),
                "testing_complete": datetime.utcnow(),
                "quality_complete": datetime.utcnow(),
            },
        )
        # No validation_passed timestamp

        orchestrator = PhaseOrchestrator(state)
        can_advance, reason = orchestrator.can_advance_to(Phase.GRADUATED)

        assert can_advance is False
        assert "all_gates_passed" in reason

    def test_can_advance_to_graduated_with_validation(self, metrics_with_coverage):
        """Test GRADUATED allowed when all gates pass."""
        state = BrownfieldState(
            schema_version="1.0",
            project_root=Path("/tmp/test"),
            current_phase=Phase.VALIDATION,
            baseline_metrics=metrics_with_coverage,
            current_metrics=metrics_with_coverage,
            phase_timestamps={
                "structure_complete": datetime.utcnow(),
                "testing_complete": datetime.utcnow(),
                "quality_complete": datetime.utcnow(),
                "validation_passed": datetime.utcnow(),  # All gates passed
            },
        )

        orchestrator = PhaseOrchestrator(state)
        can_advance, reason = orchestrator.can_advance_to(Phase.GRADUATED)

        assert can_advance is True
        assert reason is None


class TestGraduatedReEntry:
    """Test re-entry from graduated state."""

    @pytest.fixture
    def graduated_state(self):
        """Create state in GRADUATED phase."""
        metrics = Metrics(
            test_coverage=0.7,
            complexity_avg=8.0,
            complexity_max=12,
            critical_vulnerabilities=0,
            high_vulnerabilities=0,
            medium_vulnerabilities=0,
            build_status="passing",
            documentation_coverage=0.6,
            total_loc=1000,
            test_loc=700,
            git_commits=20,
            git_secrets_found=0,
        )

        return BrownfieldState(
            schema_version="1.0",
            project_root=Path("/tmp/test"),
            current_phase=Phase.GRADUATED,
            baseline_metrics=metrics,
            current_metrics=metrics,
            graduated=True,
            graduation_timestamp=datetime.utcnow(),
            phase_timestamps={
                "structure_complete": datetime.utcnow(),
                "testing_complete": datetime.utcnow(),
                "quality_complete": datetime.utcnow(),
                "validation_passed": datetime.utcnow(),
            },
        )

    def test_graduated_can_reenter_structure(self, graduated_state):
        """Test graduated projects can re-enter STRUCTURE phase."""
        orchestrator = PhaseOrchestrator(graduated_state)
        can_advance, reason = orchestrator.can_advance_to(Phase.STRUCTURE)

        assert can_advance is True
        assert reason is None

    def test_graduated_can_reenter_testing(self, graduated_state):
        """Test graduated projects can re-enter TESTING phase."""
        orchestrator = PhaseOrchestrator(graduated_state)
        can_advance, reason = orchestrator.can_advance_to(Phase.TESTING)

        assert can_advance is True
        assert reason is None

    def test_graduated_can_reenter_quality(self, graduated_state):
        """Test graduated projects can re-enter QUALITY phase."""
        orchestrator = PhaseOrchestrator(graduated_state)
        can_advance, reason = orchestrator.can_advance_to(Phase.QUALITY)

        assert can_advance is True
        assert reason is None

    def test_graduated_cannot_advance_to_assessment(self, graduated_state):
        """Test graduated projects cannot go back to ASSESSMENT."""
        orchestrator = PhaseOrchestrator(graduated_state)
        can_advance, reason = orchestrator.can_advance_to(Phase.ASSESSMENT)

        assert can_advance is False
        assert "Cannot transition" in reason

    def test_graduated_cannot_advance_to_validation(self, graduated_state):
        """Test graduated projects cannot go back to VALIDATION."""
        orchestrator = PhaseOrchestrator(graduated_state)
        can_advance, reason = orchestrator.can_advance_to(Phase.VALIDATION)

        assert can_advance is False
        assert "Cannot transition" in reason


class TestAdvanceWithValidation:
    """Test advance_with_validation method."""

    @pytest.fixture
    def valid_state(self):
        """Create state ready for advancement."""
        metrics = Metrics(
            test_coverage=0.7,
            complexity_avg=8.0,
            complexity_max=12,
            critical_vulnerabilities=0,
            high_vulnerabilities=0,
            medium_vulnerabilities=0,
            build_status="passing",
            documentation_coverage=0.6,
            total_loc=1000,
            test_loc=700,
            git_commits=10,
            git_secrets_found=0,
        )

        return BrownfieldState(
            schema_version="1.0",
            project_root=Path("/tmp/test"),
            current_phase=Phase.ASSESSMENT,
            baseline_metrics=metrics,
            current_metrics=metrics,
        )

    def test_advance_with_validation_success(self, valid_state):
        """Test advance_with_validation succeeds for valid transition."""
        orchestrator = PhaseOrchestrator(valid_state)

        # Should succeed without exception
        orchestrator.advance_with_validation(Phase.STRUCTURE)

        assert valid_state.current_phase == Phase.STRUCTURE

    def test_advance_with_validation_raises_on_invalid_transition(self, valid_state):
        """Test advance_with_validation raises ValueError for invalid transition."""
        orchestrator = PhaseOrchestrator(valid_state)

        with pytest.raises(ValueError, match="Cannot transition"):
            orchestrator.advance_with_validation(Phase.GRADUATED)

        # State should remain unchanged
        assert valid_state.current_phase == Phase.ASSESSMENT

    def test_advance_with_validation_raises_on_unmet_requirements(self):
        """Test advance_with_validation raises ValueError for unmet requirements."""
        state = BrownfieldState(
            schema_version="1.0",
            project_root=Path("/tmp/test"),
            current_phase=Phase.STRUCTURE,
            baseline_metrics=Metrics(
                test_coverage=0.0,
                complexity_avg=8.0,
                complexity_max=12,
                critical_vulnerabilities=0,
                high_vulnerabilities=0,
                medium_vulnerabilities=0,
                build_status="passing",
                documentation_coverage=0.0,
                total_loc=1000,
                test_loc=0,
                git_commits=1,
                git_secrets_found=0,
            ),
            current_metrics=Metrics(
                test_coverage=0.0,
                complexity_avg=8.0,
                complexity_max=12,
                critical_vulnerabilities=0,
                high_vulnerabilities=0,
                medium_vulnerabilities=0,
                build_status="passing",
                documentation_coverage=0.0,
                total_loc=1000,
                test_loc=0,
                git_commits=1,
                git_secrets_found=0,
            ),
        )
        # No structure_complete timestamp

        orchestrator = PhaseOrchestrator(state)

        with pytest.raises(ValueError, match="structure_phase_completed"):
            orchestrator.advance_with_validation(Phase.TESTING)

        # State should remain unchanged
        assert state.current_phase == Phase.STRUCTURE


class TestPhaseTransitionMatrix:
    """Test complete phase transition matrix."""

    @pytest.fixture
    def all_phase_states(self):
        """Create states for all phases."""
        metrics = Metrics(
            test_coverage=0.7,
            complexity_avg=8.0,
            complexity_max=12,
            critical_vulnerabilities=0,
            high_vulnerabilities=0,
            medium_vulnerabilities=0,
            build_status="passing",
            documentation_coverage=0.6,
            total_loc=1000,
            test_loc=700,
            git_commits=15,
            git_secrets_found=0,
        )

        states = {}
        for phase in Phase:
            states[phase] = BrownfieldState(
                schema_version="1.0",
                project_root=Path("/tmp/test"),
                current_phase=phase,
                baseline_metrics=metrics,
                current_metrics=metrics,
                phase_timestamps={
                    "structure_complete": datetime.utcnow(),
                    "testing_complete": datetime.utcnow(),
                    "quality_complete": datetime.utcnow(),
                    "validation_passed": datetime.utcnow(),
                },
            )

        return states

    @pytest.mark.parametrize(
        "from_phase,to_phase,should_succeed",
        [
            # Valid transitions
            (Phase.ASSESSMENT, Phase.STRUCTURE, True),
            (Phase.STRUCTURE, Phase.TESTING, True),
            (Phase.TESTING, Phase.QUALITY, True),
            (Phase.QUALITY, Phase.VALIDATION, True),
            (Phase.VALIDATION, Phase.GRADUATED, True),
            # Re-entry transitions
            (Phase.GRADUATED, Phase.STRUCTURE, True),
            (Phase.GRADUATED, Phase.TESTING, True),
            (Phase.GRADUATED, Phase.QUALITY, True),
            # Invalid transitions (phase skipping)
            (Phase.ASSESSMENT, Phase.TESTING, False),
            (Phase.ASSESSMENT, Phase.QUALITY, False),
            (Phase.ASSESSMENT, Phase.VALIDATION, False),
            (Phase.ASSESSMENT, Phase.GRADUATED, False),
            (Phase.STRUCTURE, Phase.QUALITY, False),
            (Phase.STRUCTURE, Phase.VALIDATION, False),
            (Phase.TESTING, Phase.VALIDATION, False),
            # Invalid backward transitions
            (Phase.STRUCTURE, Phase.ASSESSMENT, False),
            (Phase.TESTING, Phase.ASSESSMENT, False),
            (Phase.QUALITY, Phase.ASSESSMENT, False),
            (Phase.VALIDATION, Phase.ASSESSMENT, False),
            (Phase.GRADUATED, Phase.ASSESSMENT, False),
            (Phase.GRADUATED, Phase.VALIDATION, False),
        ],
    )
    def test_phase_transition_matrix(
        self, all_phase_states, from_phase, to_phase, should_succeed
    ):
        """Test comprehensive phase transition matrix."""
        state = all_phase_states[from_phase]
        orchestrator = PhaseOrchestrator(state)

        can_advance, reason = orchestrator.can_advance_to(to_phase)

        if should_succeed:
            assert (
                can_advance is True
            ), f"Expected {from_phase.value} → {to_phase.value} to succeed, but got: {reason}"
        else:
            assert (
                can_advance is False
            ), f"Expected {from_phase.value} → {to_phase.value} to fail, but it succeeded"
