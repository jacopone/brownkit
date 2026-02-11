"""Unit tests for WorkflowEnforcer (Phase 1)."""

import pytest

from brownfield.config import BrownfieldConfig
from brownfield.integration.speckit import WorkflowEnforcer
from brownfield.models.state import BrownfieldState
from brownfield.models.workflow import PhaseExecution, PhaseStatus, WorkflowPhase


class TestWorkflowEnforcerInitialization:
    """Test WorkflowEnforcer initialization."""

    def test_init_without_existing_state(self, tmp_path):
        """Test initialization when no state file exists."""
        enforcer = WorkflowEnforcer(project_root=tmp_path)

        assert enforcer.project_root == tmp_path
        assert enforcer.state_path == BrownfieldConfig.get_state_path(tmp_path)
        assert enforcer.state is None

    def test_init_with_existing_state(self, tmp_path):
        """Test initialization when state file exists."""
        # Use state.json directly (post-migration name)
        state_path = BrownfieldConfig.get_state_path(tmp_path)

        state = BrownfieldState()
        state.project_root = tmp_path
        state.save(state_path)

        # Initialize enforcer
        enforcer = WorkflowEnforcer(project_root=tmp_path)

        assert enforcer.state is not None
        assert enforcer.state.project_root == tmp_path

    def test_init_uses_config_default_root(self, tmp_path, monkeypatch):
        """Test initialization uses BrownfieldConfig default if no root provided."""
        # Mock BrownfieldConfig.get_project_root
        monkeypatch.setattr(BrownfieldConfig, "get_project_root", lambda: tmp_path)

        enforcer = WorkflowEnforcer()

        assert enforcer.project_root == tmp_path


class TestCanExecutePhase:
    """Test WorkflowEnforcer.can_execute_phase()."""

    def test_assessment_always_allowed(self, tmp_path):
        """Test ASSESSMENT can always be executed."""
        enforcer = WorkflowEnforcer(project_root=tmp_path)

        can_exec, error = enforcer.can_execute_phase(WorkflowPhase.ASSESSMENT)

        assert can_exec is True
        assert error is None

    def test_planning_blocked_without_state(self, tmp_path):
        """Test PLANNING blocked when state doesn't exist."""
        enforcer = WorkflowEnforcer(project_root=tmp_path)

        can_exec, error = enforcer.can_execute_phase(WorkflowPhase.PLANNING)

        assert can_exec is False
        assert "not initialized" in error.lower()
        assert "/brownkit.assess" in error

    def test_planning_blocked_without_assessment(self, tmp_path):
        """Test PLANNING blocked when ASSESSMENT not completed."""
        # Create state without completing assessment
        state_path = BrownfieldConfig.get_state_path(tmp_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = BrownfieldState()
        state.project_root = tmp_path
        state.save(state_path)

        enforcer = WorkflowEnforcer(project_root=tmp_path)
        can_exec, error = enforcer.can_execute_phase(WorkflowPhase.PLANNING)

        assert can_exec is False
        assert "/brownkit.assess" in error

    def test_planning_allowed_after_assessment(self, tmp_path):
        """Test PLANNING allowed after ASSESSMENT completed."""
        # Create state with completed assessment
        state_path = BrownfieldConfig.get_state_path(tmp_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = BrownfieldState()
        state.project_root = tmp_path
        assessment = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.COMPLETED)
        state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment
        state.save(state_path)

        enforcer = WorkflowEnforcer(project_root=tmp_path)
        can_exec, error = enforcer.can_execute_phase(WorkflowPhase.PLANNING)

        assert can_exec is True
        assert error is None

    def test_remediation_blocked_without_planning(self, tmp_path):
        """Test REMEDIATION blocked when PLANNING not completed."""
        # Create state with only assessment completed
        state_path = BrownfieldConfig.get_state_path(tmp_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = BrownfieldState()
        state.project_root = tmp_path
        assessment = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.COMPLETED)
        state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment
        state.save(state_path)

        enforcer = WorkflowEnforcer(project_root=tmp_path)
        can_exec, error = enforcer.can_execute_phase(WorkflowPhase.REMEDIATION)

        assert can_exec is False
        assert "/brownkit.plan" in error

    def test_failed_phase_blocks_next(self, tmp_path):
        """Test failed phase blocks next phase with error message."""
        # Create state with failed assessment
        state_path = BrownfieldConfig.get_state_path(tmp_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = BrownfieldState()
        state.project_root = tmp_path
        assessment = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.FAILED)
        assessment.error_message = "Mock assessment error"
        state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment
        state.save(state_path)

        enforcer = WorkflowEnforcer(project_root=tmp_path)
        can_exec, error = enforcer.can_execute_phase(WorkflowPhase.PLANNING)

        assert can_exec is False
        assert "failed" in error.lower()
        assert "Mock assessment error" in error

    def test_in_progress_phase_blocks_next(self, tmp_path):
        """Test in-progress phase blocks next phase."""
        # Create state with in-progress assessment
        state_path = BrownfieldConfig.get_state_path(tmp_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = BrownfieldState()
        state.project_root = tmp_path
        assessment = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.IN_PROGRESS)
        state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment
        state.save(state_path)

        enforcer = WorkflowEnforcer(project_root=tmp_path)
        can_exec, error = enforcer.can_execute_phase(WorkflowPhase.PLANNING)

        assert can_exec is False
        assert "in_progress" in error.lower()


class TestMarkPhaseLifecycle:
    """Test phase lifecycle marking methods."""

    def test_mark_phase_started_creates_execution(self, tmp_path):
        """Test mark_phase_started creates new PhaseExecution."""
        # Create initial state
        state_path = BrownfieldConfig.get_state_path(tmp_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = BrownfieldState()
        state.project_root = tmp_path
        state.save(state_path)

        enforcer = WorkflowEnforcer(project_root=tmp_path)
        enforcer.mark_phase_started(WorkflowPhase.ASSESSMENT)

        # Verify execution created
        execution = enforcer.state.workflow_state.phase_executions.get(WorkflowPhase.ASSESSMENT)
        assert execution is not None
        assert execution.status == PhaseStatus.IN_PROGRESS
        assert execution.attempts == 1

        # Verify current phase updated
        assert enforcer.state.workflow_state.current_phase == WorkflowPhase.ASSESSMENT

        # Verify state persisted
        reloaded_state = BrownfieldState.load(state_path)
        assert reloaded_state.workflow_state.current_phase == WorkflowPhase.ASSESSMENT

    def test_mark_phase_started_increments_attempts(self, tmp_path):
        """Test mark_phase_started increments attempts on retry."""
        # Create state with existing execution
        state_path = BrownfieldConfig.get_state_path(tmp_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = BrownfieldState()
        state.project_root = tmp_path
        assessment = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.IN_PROGRESS)
        assessment.attempts = 1
        state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment
        state.save(state_path)

        enforcer = WorkflowEnforcer(project_root=tmp_path)
        enforcer.mark_phase_started(WorkflowPhase.ASSESSMENT)

        # Verify attempts incremented
        execution = enforcer.state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT]
        assert execution.attempts == 2

    def test_mark_phase_started_without_state_raises_error(self, tmp_path):
        """Test mark_phase_started raises error without state."""
        enforcer = WorkflowEnforcer(project_root=tmp_path)

        with pytest.raises(ValueError, match="State not initialized"):
            enforcer.mark_phase_started(WorkflowPhase.PLANNING)

    def test_mark_phase_completed(self, tmp_path):
        """Test mark_phase_completed marks phase as completed."""
        # Create state with in-progress phase
        state_path = BrownfieldConfig.get_state_path(tmp_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = BrownfieldState()
        state.project_root = tmp_path
        assessment = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.IN_PROGRESS)
        state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment
        state.save(state_path)

        enforcer = WorkflowEnforcer(project_root=tmp_path)
        enforcer.mark_phase_completed(WorkflowPhase.ASSESSMENT)

        # Verify status updated
        execution = enforcer.state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT]
        assert execution.status == PhaseStatus.COMPLETED
        assert execution.error_message is None

        # Verify state persisted
        reloaded_state = BrownfieldState.load(state_path)
        execution = reloaded_state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT]
        assert execution.status == PhaseStatus.COMPLETED

    def test_mark_phase_failed(self, tmp_path):
        """Test mark_phase_failed marks phase as failed with error."""
        # Create state with in-progress phase
        state_path = BrownfieldConfig.get_state_path(tmp_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = BrownfieldState()
        state.project_root = tmp_path
        assessment = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.IN_PROGRESS)
        state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment
        state.save(state_path)

        enforcer = WorkflowEnforcer(project_root=tmp_path)
        error_msg = "Test error message"
        enforcer.mark_phase_failed(WorkflowPhase.ASSESSMENT, error_msg)

        # Verify status and error updated
        execution = enforcer.state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT]
        assert execution.status == PhaseStatus.FAILED
        assert execution.error_message == error_msg

        # Verify state persisted
        reloaded_state = BrownfieldState.load(state_path)
        execution = reloaded_state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT]
        assert execution.status == PhaseStatus.FAILED
        assert execution.error_message == error_msg


class TestGetNextPhase:
    """Test WorkflowEnforcer.get_next_phase()."""

    def test_get_next_phase_without_state(self, tmp_path):
        """Test get_next_phase returns ASSESSMENT when no state exists."""
        enforcer = WorkflowEnforcer(project_root=tmp_path)

        next_phase = enforcer.get_next_phase()

        assert next_phase == WorkflowPhase.ASSESSMENT

    def test_get_next_phase_on_fresh_state(self, tmp_path):
        """Test get_next_phase returns ASSESSMENT on fresh state."""
        # Create fresh state
        state_path = BrownfieldConfig.get_state_path(tmp_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = BrownfieldState()
        state.project_root = tmp_path
        state.save(state_path)

        enforcer = WorkflowEnforcer(project_root=tmp_path)
        next_phase = enforcer.get_next_phase()

        assert next_phase == WorkflowPhase.ASSESSMENT

    def test_get_next_phase_progression(self, tmp_path):
        """Test get_next_phase progresses through workflow."""
        # Create state with completed assessment
        state_path = BrownfieldConfig.get_state_path(tmp_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = BrownfieldState()
        state.project_root = tmp_path
        assessment = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.COMPLETED)
        state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment
        state.save(state_path)

        enforcer = WorkflowEnforcer(project_root=tmp_path)
        next_phase = enforcer.get_next_phase()

        assert next_phase == WorkflowPhase.PLANNING


class TestWorkflowStatus:
    """Test WorkflowEnforcer.get_workflow_status()."""

    def test_get_workflow_status_without_state(self, tmp_path):
        """Test get_workflow_status when no state exists."""
        enforcer = WorkflowEnforcer(project_root=tmp_path)

        status = enforcer.get_workflow_status()

        assert "not started" in status.lower()
        assert "/brownkit.assess" in status

    def test_get_workflow_status_with_progression(self, tmp_path):
        """Test get_workflow_status shows phase progression."""
        # Create state with some completed phases
        state_path = BrownfieldConfig.get_state_path(tmp_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = BrownfieldState()
        state.project_root = tmp_path

        # Complete assessment, planning in progress
        assessment = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.COMPLETED)
        planning = PhaseExecution(phase=WorkflowPhase.PLANNING, status=PhaseStatus.IN_PROGRESS)
        state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment
        state.workflow_state.phase_executions[WorkflowPhase.PLANNING] = planning
        state.save(state_path)

        enforcer = WorkflowEnforcer(project_root=tmp_path)
        status = enforcer.get_workflow_status()

        assert "✅" in status  # Completed
        assert "🔄" in status  # In progress
        assert "/brownkit.assess" in status
        assert "/brownkit.plan" in status


class TestIsPhaseCompleted:
    """Test WorkflowEnforcer.is_phase_completed()."""

    def test_is_phase_completed_without_state(self, tmp_path):
        """Test is_phase_completed returns False when no state exists."""
        enforcer = WorkflowEnforcer(project_root=tmp_path)

        assert enforcer.is_phase_completed(WorkflowPhase.ASSESSMENT) is False

    def test_is_phase_completed_for_completed_phase(self, tmp_path):
        """Test is_phase_completed returns True for completed phase."""
        # Create state with completed assessment
        state_path = BrownfieldConfig.get_state_path(tmp_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = BrownfieldState()
        state.project_root = tmp_path
        assessment = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.COMPLETED)
        state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment
        state.save(state_path)

        enforcer = WorkflowEnforcer(project_root=tmp_path)

        assert enforcer.is_phase_completed(WorkflowPhase.ASSESSMENT) is True
        assert enforcer.is_phase_completed(WorkflowPhase.PLANNING) is False


class TestIsGraduated:
    """Test WorkflowEnforcer.is_graduated()."""

    def test_is_graduated_without_state(self, tmp_path):
        """Test is_graduated returns False when no state exists."""
        enforcer = WorkflowEnforcer(project_root=tmp_path)

        assert enforcer.is_graduated() is False

    def test_is_graduated_after_graduation(self, tmp_path):
        """Test is_graduated returns True after GRADUATION completed."""
        # Create state with completed graduation
        state_path = BrownfieldConfig.get_state_path(tmp_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = BrownfieldState()
        state.project_root = tmp_path

        # Complete all phases up to graduation
        for phase in [
            WorkflowPhase.ASSESSMENT,
            WorkflowPhase.PLANNING,
            WorkflowPhase.REMEDIATION,
            WorkflowPhase.VALIDATION,
            WorkflowPhase.GRADUATION,
        ]:
            execution = PhaseExecution(phase=phase, status=PhaseStatus.COMPLETED)
            state.workflow_state.phase_executions[phase] = execution

        state.save(state_path)

        enforcer = WorkflowEnforcer(project_root=tmp_path)

        assert enforcer.is_graduated() is True


class TestFullWorkflowIntegration:
    """Integration tests for full workflow enforcement."""

    def test_full_workflow_from_scratch(self, tmp_path):
        """Test full workflow enforcement from initialization to graduation."""
        enforcer = WorkflowEnforcer(project_root=tmp_path)

        # Phase 1: ASSESSMENT
        can_exec, _ = enforcer.can_execute_phase(WorkflowPhase.ASSESSMENT)
        assert can_exec is True

        # Create state by marking assessment started
        state_path = BrownfieldConfig.get_state_path(tmp_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state = BrownfieldState()
        state.project_root = tmp_path
        state.save(state_path)

        enforcer = WorkflowEnforcer(project_root=tmp_path)
        enforcer.mark_phase_started(WorkflowPhase.ASSESSMENT)
        enforcer.mark_phase_completed(WorkflowPhase.ASSESSMENT)

        # Phase 2: PLANNING now allowed
        can_exec, _ = enforcer.can_execute_phase(WorkflowPhase.PLANNING)
        assert can_exec is True

        enforcer.mark_phase_started(WorkflowPhase.PLANNING)
        enforcer.mark_phase_completed(WorkflowPhase.PLANNING)

        # Phase 3: REMEDIATION now allowed
        can_exec, _ = enforcer.can_execute_phase(WorkflowPhase.REMEDIATION)
        assert can_exec is True

        # Verify next phase is REMEDIATION
        assert enforcer.get_next_phase() == WorkflowPhase.REMEDIATION

        # Verify workflow status shows progression
        status = enforcer.get_workflow_status()
        assert "✅" in status  # Some completed phases
