"""Unit tests for workflow models (Phase 1)."""

from datetime import datetime

from brownfield.models.workflow import (
    PHASE_PREREQUISITES,
    PHASE_TO_COMMAND,
    PhaseExecution,
    PhaseStatus,
    WorkflowPhase,
    WorkflowState,
)


class TestWorkflowPhase:
    """Test WorkflowPhase enum."""

    def test_all_phases_defined(self):
        """Test all workflow phases are defined."""
        assert WorkflowPhase.NOT_STARTED.value == "not_started"
        assert WorkflowPhase.ASSESSMENT.value == "assessment"
        assert WorkflowPhase.PLANNING.value == "planning"
        assert WorkflowPhase.REMEDIATION.value == "remediation"
        assert WorkflowPhase.VALIDATION.value == "validation"
        assert WorkflowPhase.GRADUATION.value == "graduation"
        assert WorkflowPhase.SPEC_KIT_READY.value == "speckit_ready"


class TestPhaseStatus:
    """Test PhaseStatus enum."""

    def test_all_statuses_defined(self):
        """Test all phase statuses are defined."""
        assert PhaseStatus.NOT_STARTED.value == "not_started"
        assert PhaseStatus.IN_PROGRESS.value == "in_progress"
        assert PhaseStatus.COMPLETED.value == "completed"
        assert PhaseStatus.FAILED.value == "failed"


class TestPhaseExecution:
    """Test PhaseExecution dataclass."""

    def test_creation(self):
        """Test creating a phase execution."""
        exec = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.NOT_STARTED)
        assert exec.phase == WorkflowPhase.ASSESSMENT
        assert exec.status == PhaseStatus.NOT_STARTED
        assert exec.started_at is None
        assert exec.completed_at is None
        assert exec.attempts == 0
        assert exec.error_message is None

    def test_mark_started(self):
        """Test marking phase as started."""
        exec = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.NOT_STARTED)

        exec.mark_started()

        assert exec.status == PhaseStatus.IN_PROGRESS
        assert exec.started_at is not None
        assert isinstance(exec.started_at, datetime)
        assert exec.attempts == 1
        assert exec.completed_at is None

    def test_mark_started_increments_attempts(self):
        """Test marking started multiple times increments attempts."""
        exec = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.NOT_STARTED)

        exec.mark_started()
        assert exec.attempts == 1

        exec.mark_started()
        assert exec.attempts == 2

    def test_mark_completed(self):
        """Test marking phase as completed."""
        exec = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.IN_PROGRESS)
        exec.mark_started()

        exec.mark_completed()

        assert exec.status == PhaseStatus.COMPLETED
        assert exec.completed_at is not None
        assert isinstance(exec.completed_at, datetime)
        assert exec.error_message is None

    def test_mark_failed(self):
        """Test marking phase as failed."""
        exec = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.IN_PROGRESS)

        error_msg = "Test error message"
        exec.mark_failed(error_msg)

        assert exec.status == PhaseStatus.FAILED
        assert exec.error_message == error_msg


class TestWorkflowState:
    """Test WorkflowState dataclass."""

    def test_creation_defaults(self):
        """Test creating workflow state with defaults."""
        state = WorkflowState()

        assert state.current_phase == WorkflowPhase.NOT_STARTED
        assert state.phase_executions == {}
        assert state.can_skip_phases is False

    def test_can_execute_assessment_always_true(self):
        """Test ASSESSMENT can always be executed."""
        state = WorkflowState()

        can_exec, reason = state.can_execute_phase(WorkflowPhase.ASSESSMENT)

        assert can_exec is True
        assert reason is None

    def test_can_execute_planning_requires_assessment(self):
        """Test PLANNING requires ASSESSMENT to be completed."""
        state = WorkflowState()

        # Without assessment completed
        can_exec, reason = state.can_execute_phase(WorkflowPhase.PLANNING)
        assert can_exec is False
        assert "brownkit.assess" in reason

    def test_can_execute_planning_after_assessment(self):
        """Test PLANNING can execute after ASSESSMENT completed."""
        state = WorkflowState()

        # Complete assessment
        assessment = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.COMPLETED)
        state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment

        can_exec, reason = state.can_execute_phase(WorkflowPhase.PLANNING)
        assert can_exec is True
        assert reason is None

    def test_sequential_workflow_enforcement(self):
        """Test full sequential workflow enforcement."""
        state = WorkflowState()

        # ASSESSMENT allowed
        can_exec, _ = state.can_execute_phase(WorkflowPhase.ASSESSMENT)
        assert can_exec is True

        # PLANNING not allowed yet
        can_exec, _ = state.can_execute_phase(WorkflowPhase.PLANNING)
        assert can_exec is False

        # Complete ASSESSMENT
        state.phase_executions[WorkflowPhase.ASSESSMENT] = PhaseExecution(
            phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.COMPLETED
        )

        # PLANNING now allowed
        can_exec, _ = state.can_execute_phase(WorkflowPhase.PLANNING)
        assert can_exec is True

        # REMEDIATION not allowed yet
        can_exec, _ = state.can_execute_phase(WorkflowPhase.REMEDIATION)
        assert can_exec is False

        # Complete PLANNING
        state.phase_executions[WorkflowPhase.PLANNING] = PhaseExecution(
            phase=WorkflowPhase.PLANNING, status=PhaseStatus.COMPLETED
        )

        # REMEDIATION now allowed
        can_exec, _ = state.can_execute_phase(WorkflowPhase.REMEDIATION)
        assert can_exec is True

    def test_failed_phase_blocks_next(self):
        """Test that failed phase blocks next phase."""
        state = WorkflowState()

        # Mark ASSESSMENT as failed
        assessment = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.FAILED)
        assessment.error_message = "Test error"
        state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment

        # PLANNING should be blocked
        can_exec, reason = state.can_execute_phase(WorkflowPhase.PLANNING)
        assert can_exec is False
        assert "failed" in reason.lower()
        assert "Test error" in reason

    def test_in_progress_phase_blocks_next(self):
        """Test that in-progress phase blocks next phase."""
        state = WorkflowState()

        # Mark ASSESSMENT as in progress
        assessment = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.IN_PROGRESS)
        state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment

        # PLANNING should be blocked
        can_exec, reason = state.can_execute_phase(WorkflowPhase.PLANNING)
        assert can_exec is False
        assert "in_progress" in reason.lower()

    def test_get_next_phase_on_fresh_state(self):
        """Test get_next_phase on fresh state returns ASSESSMENT."""
        state = WorkflowState()

        next_phase = state.get_next_phase()
        assert next_phase == WorkflowPhase.ASSESSMENT

    def test_get_next_phase_progression(self):
        """Test get_next_phase progresses through workflow."""
        state = WorkflowState()

        # Complete ASSESSMENT
        state.phase_executions[WorkflowPhase.ASSESSMENT] = PhaseExecution(
            phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.COMPLETED
        )

        next_phase = state.get_next_phase()
        assert next_phase == WorkflowPhase.PLANNING

        # Complete PLANNING
        state.phase_executions[WorkflowPhase.PLANNING] = PhaseExecution(
            phase=WorkflowPhase.PLANNING, status=PhaseStatus.COMPLETED
        )

        next_phase = state.get_next_phase()
        assert next_phase == WorkflowPhase.REMEDIATION

    def test_get_next_phase_when_all_complete(self):
        """Test get_next_phase returns None when all phases complete."""
        state = WorkflowState()

        # Complete all phases
        for phase in [
            WorkflowPhase.ASSESSMENT,
            WorkflowPhase.PLANNING,
            WorkflowPhase.REMEDIATION,
            WorkflowPhase.VALIDATION,
            WorkflowPhase.GRADUATION,
            WorkflowPhase.SPEC_KIT_READY,
        ]:
            state.phase_executions[phase] = PhaseExecution(phase=phase, status=PhaseStatus.COMPLETED)

        next_phase = state.get_next_phase()
        assert next_phase is None

    def test_get_workflow_status_display(self):
        """Test workflow status display generation."""
        state = WorkflowState()

        # Add some phase executions
        state.phase_executions[WorkflowPhase.ASSESSMENT] = PhaseExecution(
            phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.COMPLETED
        )
        state.phase_executions[WorkflowPhase.PLANNING] = PhaseExecution(
            phase=WorkflowPhase.PLANNING, status=PhaseStatus.IN_PROGRESS
        )

        display = state.get_workflow_status_display()

        assert "Current workflow status:" in display
        assert "✅" in display  # Completed
        assert "🔄" in display  # In progress
        assert "⬜" in display  # Not started
        assert "/brownkit.assess" in display
        assert "/brownkit.plan" in display

    def test_is_phase_completed(self):
        """Test is_phase_completed check."""
        state = WorkflowState()

        # Phase not started
        assert state.is_phase_completed(WorkflowPhase.ASSESSMENT) is False

        # Phase in progress
        state.phase_executions[WorkflowPhase.ASSESSMENT] = PhaseExecution(
            phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.IN_PROGRESS
        )
        assert state.is_phase_completed(WorkflowPhase.ASSESSMENT) is False

        # Phase completed
        state.phase_executions[WorkflowPhase.ASSESSMENT].status = PhaseStatus.COMPLETED
        assert state.is_phase_completed(WorkflowPhase.ASSESSMENT) is True


class TestPhaseConstants:
    """Test module-level phase constants."""

    def test_phase_prerequisites_defined(self):
        """Test all phases have prerequisites defined."""
        assert WorkflowPhase.NOT_STARTED in PHASE_PREREQUISITES
        assert WorkflowPhase.ASSESSMENT in PHASE_PREREQUISITES
        assert WorkflowPhase.PLANNING in PHASE_PREREQUISITES
        assert WorkflowPhase.REMEDIATION in PHASE_PREREQUISITES
        assert WorkflowPhase.VALIDATION in PHASE_PREREQUISITES
        assert WorkflowPhase.GRADUATION in PHASE_PREREQUISITES
        assert WorkflowPhase.SPEC_KIT_READY in PHASE_PREREQUISITES

    def test_assessment_has_no_prerequisites(self):
        """Test ASSESSMENT phase has no prerequisites."""
        assert PHASE_PREREQUISITES[WorkflowPhase.ASSESSMENT] == []

    def test_planning_requires_assessment(self):
        """Test PLANNING requires ASSESSMENT."""
        prereqs = PHASE_PREREQUISITES[WorkflowPhase.PLANNING]
        assert WorkflowPhase.ASSESSMENT in prereqs

    def test_remediation_requires_planning(self):
        """Test REMEDIATION requires PLANNING."""
        prereqs = PHASE_PREREQUISITES[WorkflowPhase.REMEDIATION]
        assert WorkflowPhase.PLANNING in prereqs

    def test_phase_to_command_mapping(self):
        """Test phase to command mapping exists."""
        assert PHASE_TO_COMMAND[WorkflowPhase.ASSESSMENT] == "brownkit.assess"
        assert PHASE_TO_COMMAND[WorkflowPhase.PLANNING] == "brownkit.plan"
        assert PHASE_TO_COMMAND[WorkflowPhase.REMEDIATION] == "brownkit.remediate"
        assert PHASE_TO_COMMAND[WorkflowPhase.VALIDATION] == "brownkit.validate"
        assert PHASE_TO_COMMAND[WorkflowPhase.GRADUATION] == "brownkit.graduate"
        assert PHASE_TO_COMMAND[WorkflowPhase.SPEC_KIT_READY] == "speckit.specify"
