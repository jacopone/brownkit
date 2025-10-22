"""Integration tests for phase transitions with validation."""

import pytest
from pathlib import Path
from datetime import datetime

from brownfield.models.state import BrownfieldState, Phase
from brownfield.models.assessment import Metrics
from brownfield.orchestrator.phase_machine import PhaseOrchestrator
from brownfield.state.state_store import StateStore


class TestPhaseTransitionIntegration:
    """Integration tests for complete phase transition workflows."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create temporary project directory."""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        memory_dir = project_root / ".specify" / "memory"
        memory_dir.mkdir(parents=True)
        return project_root

    @pytest.fixture
    def good_metrics(self):
        """Metrics that meet all requirements."""
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
            git_commits=20,
            git_secrets_found=0,
        )

    def test_complete_workflow_with_validation(self, temp_project, good_metrics):
        """Test complete workflow from ASSESSMENT to GRADUATED with validation."""
        memory_dir = temp_project / ".specify" / "memory"
        state_store = StateStore(memory_dir)

        # Initialize state in ASSESSMENT phase
        state = BrownfieldState(
            workflow="brownfield",
            schema_version="1.0",
            project_root=temp_project,
            current_phase=Phase.ASSESSMENT,
            baseline_metrics=good_metrics,
            current_metrics=good_metrics,
        )

        state_store.save(state)

        # Create orchestrator
        orchestrator = PhaseOrchestrator(state)

        # Step 1: ASSESSMENT → STRUCTURE
        can_advance, reason = orchestrator.can_advance_to(Phase.STRUCTURE)
        assert can_advance is True, f"Should advance to STRUCTURE: {reason}"

        orchestrator.advance_with_validation(Phase.STRUCTURE)
        assert state.current_phase == Phase.STRUCTURE

        # Mark structure complete
        state.phase_timestamps["structure_complete"] = datetime.utcnow()
        state_store.save(state)

        # Reload orchestrator with updated state
        state = state_store.load()
        orchestrator = PhaseOrchestrator(state)

        # Step 2: STRUCTURE → TESTING
        can_advance, reason = orchestrator.can_advance_to(Phase.TESTING)
        assert can_advance is True, f"Should advance to TESTING: {reason}"

        orchestrator.advance_with_validation(Phase.TESTING)
        assert state.current_phase == Phase.TESTING

        # Mark testing complete with good coverage
        state.phase_timestamps["testing_complete"] = datetime.utcnow()
        state.current_metrics.test_coverage = 0.7
        state_store.save(state)

        # Reload
        state = state_store.load()
        orchestrator = PhaseOrchestrator(state)

        # Step 3: TESTING → QUALITY
        can_advance, reason = orchestrator.can_advance_to(Phase.QUALITY)
        assert can_advance is True, f"Should advance to QUALITY: {reason}"

        orchestrator.advance_with_validation(Phase.QUALITY)
        assert state.current_phase == Phase.QUALITY

        # Mark quality complete
        state.phase_timestamps["quality_complete"] = datetime.utcnow()
        state_store.save(state)

        # Reload
        state = state_store.load()
        orchestrator = PhaseOrchestrator(state)

        # Step 4: QUALITY → VALIDATION
        can_advance, reason = orchestrator.can_advance_to(Phase.VALIDATION)
        assert can_advance is True, f"Should advance to VALIDATION: {reason}"

        orchestrator.advance_with_validation(Phase.VALIDATION)
        assert state.current_phase == Phase.VALIDATION

        # Mark validation passed
        state.phase_timestamps["validation_passed"] = datetime.utcnow()
        state_store.save(state)

        # Reload
        state = state_store.load()
        orchestrator = PhaseOrchestrator(state)

        # Step 5: VALIDATION → GRADUATED
        can_advance, reason = orchestrator.can_advance_to(Phase.GRADUATED)
        assert can_advance is True, f"Should advance to GRADUATED: {reason}"

        orchestrator.advance_with_validation(Phase.GRADUATED)
        assert state.current_phase == Phase.GRADUATED

        # Save final state
        state_store.save(state)

        # Verify all phase timestamps exist
        assert "structure_complete" in state.phase_timestamps
        assert "testing_complete" in state.phase_timestamps
        assert "quality_complete" in state.phase_timestamps
        assert "validation_passed" in state.phase_timestamps

    def test_workflow_blocked_by_missing_requirements(self, temp_project):
        """Test workflow is blocked when requirements not met."""
        memory_dir = temp_project / ".specify" / "memory"
        state_store = StateStore(memory_dir)

        # Create state with poor metrics
        poor_metrics = Metrics(
            test_coverage=0.3,  # Below 60% threshold
            complexity_avg=15.0,
            complexity_max=25,
            critical_vulnerabilities=1,
            high_vulnerabilities=3,
            medium_vulnerabilities=5,
            build_status="failing",
            documentation_coverage=0.2,
            total_loc=1000,
            test_loc=300,
            git_commits=5,
            git_secrets_found=0,
        )

        state = BrownfieldState(
            workflow="brownfield",
            schema_version="1.0",
            project_root=temp_project,
            current_phase=Phase.TESTING,
            baseline_metrics=poor_metrics,
            current_metrics=poor_metrics,
            phase_timestamps={
                "structure_complete": datetime.utcnow(),
                "testing_complete": datetime.utcnow(),
            },
        )

        state_store.save(state)

        orchestrator = PhaseOrchestrator(state)

        # Should NOT be able to advance to QUALITY due to low coverage
        can_advance, reason = orchestrator.can_advance_to(Phase.QUALITY)

        assert can_advance is False
        assert "test_coverage_min_60" in reason

    def test_state_persists_across_reloads(self, temp_project, good_metrics):
        """Test state persists correctly with new state.json filename."""
        memory_dir = temp_project / ".specify" / "memory"
        state_store = StateStore(memory_dir)

        # Create and save state
        state = BrownfieldState(
            workflow="brownfield",
            schema_version="1.0",
            project_root=temp_project,
            current_phase=Phase.STRUCTURE,
            baseline_metrics=good_metrics,
            current_metrics=good_metrics,
            phase_timestamps={"structure_complete": datetime.utcnow()},
        )

        state_store.save(state)

        # Verify state.json was created (not brownfield-state.json)
        state_path = memory_dir / "state.json"
        assert state_path.exists()

        # Reload state
        loaded_state = state_store.load()

        assert loaded_state.workflow == "brownfield"
        assert loaded_state.current_phase == Phase.STRUCTURE
        assert loaded_state.project_root == temp_project
        assert "structure_complete" in loaded_state.phase_timestamps

    def test_graduated_re_entry_workflow(self, temp_project, good_metrics):
        """Test re-entry from graduated state."""
        memory_dir = temp_project / ".specify" / "memory"
        state_store = StateStore(memory_dir)

        # Create graduated state
        state = BrownfieldState(
            workflow="brownfield",
            schema_version="1.0",
            project_root=temp_project,
            current_phase=Phase.GRADUATED,
            baseline_metrics=good_metrics,
            current_metrics=good_metrics,
            graduated=True,
            graduation_timestamp=datetime.utcnow(),
            phase_timestamps={
                "structure_complete": datetime.utcnow(),
                "testing_complete": datetime.utcnow(),
                "quality_complete": datetime.utcnow(),
                "validation_passed": datetime.utcnow(),
            },
        )

        state_store.save(state)

        orchestrator = PhaseOrchestrator(state)

        # Should be able to re-enter TESTING phase
        can_advance, reason = orchestrator.can_advance_to(Phase.TESTING)
        assert can_advance is True

        # Re-enter testing
        orchestrator.advance_with_validation(Phase.TESTING)
        assert state.current_phase == Phase.TESTING

        # Should be able to re-enter QUALITY
        state.current_phase = Phase.GRADUATED
        can_advance, reason = orchestrator.can_advance_to(Phase.QUALITY)
        assert can_advance is True

        # Should be able to re-enter STRUCTURE
        state.current_phase = Phase.GRADUATED
        can_advance, reason = orchestrator.can_advance_to(Phase.STRUCTURE)
        assert can_advance is True
