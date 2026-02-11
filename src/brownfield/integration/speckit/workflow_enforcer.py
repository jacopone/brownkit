"""Workflow phase enforcement for sequential BrownKit execution."""

from pathlib import Path

from brownfield.config import BrownfieldConfig
from brownfield.models.workflow import PhaseExecution, PhaseStatus, WorkflowPhase
from brownfield.state.state_store import StateStore


class WorkflowEnforcer:
    """Enforces sequential execution of BrownKit workflow phases.

    Prevents out-of-order slash command execution by checking prerequisites
    before allowing phase execution.
    """

    def __init__(self, project_root: Path | None = None):
        """Initialize workflow enforcer.

        Args:
            project_root: Project root directory (uses config default if None)
        """
        self.project_root = project_root or BrownfieldConfig.get_project_root()
        self.state_path = BrownfieldConfig.get_state_path(self.project_root)

        # Load state if exists
        if self.state_path.exists():
            store = StateStore(self.state_path)
            self.state = store.load()
        else:
            self.state = None

    def can_execute_phase(self, phase: WorkflowPhase) -> tuple[bool, str | None]:
        """Check if phase can be executed.

        Args:
            phase: Workflow phase to check

        Returns:
            Tuple of (can_execute, error_message)
            - can_execute: True if phase can be executed
            - error_message: Detailed error if can_execute is False, None otherwise
        """
        # Special case: ASSESSMENT can always run (initializes state)
        if phase == WorkflowPhase.ASSESSMENT:
            return True, None

        # State must exist after assessment
        if not self.state:
            return (
                False,
                "Project not initialized. Run /brownkit.assess first to begin workflow.",
            )

        # Check workflow prerequisites using WorkflowState
        can_execute, reason = self.state.workflow_state.can_execute_phase(phase)

        if not can_execute:
            # Build detailed error message with workflow status
            status_display = self.state.workflow_state.get_workflow_status_display()
            full_message = f"{reason}\n\n{status_display}"
            return False, full_message

        return True, None

    def mark_phase_started(self, phase: WorkflowPhase) -> None:
        """Mark phase as in progress.

        Args:
            phase: Phase that has started

        Raises:
            ValueError: If state not initialized
        """
        if not self.state:
            raise ValueError("State not initialized. Run /brownkit.assess first.")

        # Get or create phase execution
        execution = self.state.workflow_state.phase_executions.get(phase)
        if not execution:
            execution = PhaseExecution(phase=phase, status=PhaseStatus.NOT_STARTED)
            self.state.workflow_state.phase_executions[phase] = execution

        # Mark as started
        execution.mark_started()

        # Update workflow state current phase
        self.state.workflow_state.current_phase = phase

        # Save state
        self._save_state()

    def mark_phase_completed(self, phase: WorkflowPhase) -> None:
        """Mark phase as completed successfully.

        Args:
            phase: Phase that has completed
        """
        if not self.state:
            return

        execution = self.state.workflow_state.phase_executions.get(phase)
        if execution:
            execution.mark_completed()
            self._save_state()

    def mark_phase_failed(self, phase: WorkflowPhase, error: str) -> None:
        """Mark phase as failed with error message.

        Args:
            phase: Phase that failed
            error: Error message describing the failure
        """
        if not self.state:
            return

        execution = self.state.workflow_state.phase_executions.get(phase)
        if execution:
            execution.mark_failed(error)
            self._save_state()

    def get_next_phase(self) -> WorkflowPhase | None:
        """Get the next recommended phase to execute.

        Returns:
            Next phase to execute, or None if workflow complete
        """
        if not self.state:
            return WorkflowPhase.ASSESSMENT

        return self.state.workflow_state.get_next_phase()

    def get_workflow_status(self) -> str:
        """Get human-readable workflow status.

        Returns:
            Formatted string showing all phases and their status
        """
        if not self.state:
            return "Workflow not started. Run /brownkit.assess to begin."

        return self.state.workflow_state.get_workflow_status_display()

    def is_phase_completed(self, phase: WorkflowPhase) -> bool:
        """Check if a specific phase has been completed.

        Args:
            phase: Phase to check

        Returns:
            True if phase completed, False otherwise
        """
        if not self.state:
            return False

        return self.state.workflow_state.is_phase_completed(phase)

    def is_graduated(self) -> bool:
        """Check if project has graduated.

        Returns:
            True if GRADUATION phase completed, False otherwise
        """
        return self.is_phase_completed(WorkflowPhase.GRADUATION)

    def _save_state(self) -> None:
        """Save current state to disk."""
        if self.state:
            store = StateStore(self.state_path)
            store.save(self.state)
