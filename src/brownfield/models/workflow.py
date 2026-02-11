"""Workflow phase tracking models for enforced sequential execution."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class WorkflowPhase(Enum):
    """BrownKit workflow phases (enforced sequential order)."""

    NOT_STARTED = "not_started"
    ASSESSMENT = "assessment"
    PLANNING = "planning"
    REMEDIATION = "remediation"
    VALIDATION = "validation"
    GRADUATION = "graduation"
    SPEC_KIT_READY = "speckit_ready"


class PhaseStatus(Enum):
    """Status of a workflow phase execution."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PhaseExecution:
    """Tracks execution of a single workflow phase."""

    phase: WorkflowPhase
    status: PhaseStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    attempts: int = 0
    error_message: str | None = None

    def mark_started(self) -> None:
        """Mark phase as started."""
        self.status = PhaseStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()
        self.attempts += 1

    def mark_completed(self) -> None:
        """Mark phase as completed successfully."""
        self.status = PhaseStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.error_message = None

    def mark_failed(self, error: str) -> None:
        """Mark phase as failed with error message."""
        self.status = PhaseStatus.FAILED
        self.error_message = error


# Class-level constants for phase prerequisites and commands
PHASE_PREREQUISITES: dict[WorkflowPhase, list[WorkflowPhase]] = {
    WorkflowPhase.NOT_STARTED: [],
    WorkflowPhase.ASSESSMENT: [],  # Entry point, no prerequisites
    WorkflowPhase.PLANNING: [WorkflowPhase.ASSESSMENT],
    WorkflowPhase.REMEDIATION: [WorkflowPhase.PLANNING],
    WorkflowPhase.VALIDATION: [WorkflowPhase.REMEDIATION],
    WorkflowPhase.GRADUATION: [WorkflowPhase.VALIDATION],
    WorkflowPhase.SPEC_KIT_READY: [WorkflowPhase.GRADUATION],
}

PHASE_TO_COMMAND: dict[WorkflowPhase, str] = {
    WorkflowPhase.ASSESSMENT: "brownkit.assess",
    WorkflowPhase.PLANNING: "brownkit.plan",
    WorkflowPhase.REMEDIATION: "brownkit.remediate",
    WorkflowPhase.VALIDATION: "brownkit.validate",
    WorkflowPhase.GRADUATION: "brownkit.graduate",
    WorkflowPhase.SPEC_KIT_READY: "speckit.specify",
}


@dataclass
class WorkflowState:
    """Tracks overall BrownKit workflow progression with enforcement."""

    current_phase: WorkflowPhase = WorkflowPhase.NOT_STARTED
    phase_executions: dict[WorkflowPhase, PhaseExecution] = field(default_factory=dict)
    can_skip_phases: bool = False  # Always False for enforced workflow

    def can_execute_phase(self, phase: WorkflowPhase) -> tuple[bool, str | None]:
        """Check if phase can be executed based on workflow state.

        Args:
            phase: The phase to check

        Returns:
            Tuple of (can_execute, reason)
            - can_execute: True if phase can be executed
            - reason: Error message if can_execute is False, None otherwise
        """
        # Get required prerequisites for this phase
        required_phases = PHASE_PREREQUISITES.get(phase, [])

        # Check all prerequisites are completed
        for prereq_phase in required_phases:
            prereq_execution = self.phase_executions.get(prereq_phase)

            if not prereq_execution:
                # Prerequisite never started
                prereq_cmd = PHASE_TO_COMMAND.get(prereq_phase, "unknown")
                return False, f"Must complete /{prereq_cmd} first"

            if prereq_execution.status != PhaseStatus.COMPLETED:
                # Prerequisite started but not completed
                prereq_cmd = PHASE_TO_COMMAND.get(prereq_phase, "unknown")
                status = prereq_execution.status.value

                if prereq_execution.status == PhaseStatus.FAILED:
                    return (
                        False,
                        f"/{prereq_cmd} failed: {prereq_execution.error_message}. Fix the issue and retry.",
                    )
                return False, f"/{prereq_cmd} is {status}. Complete it first."

        return True, None

    def get_next_phase(self) -> WorkflowPhase | None:
        """Get the next recommended phase based on current state.

        Returns:
            Next phase to execute, or None if workflow complete
        """
        # Define phase progression order
        phase_order = [
            WorkflowPhase.ASSESSMENT,
            WorkflowPhase.PLANNING,
            WorkflowPhase.REMEDIATION,
            WorkflowPhase.VALIDATION,
            WorkflowPhase.GRADUATION,
            WorkflowPhase.SPEC_KIT_READY,
        ]

        for phase in phase_order:
            execution = self.phase_executions.get(phase)
            if not execution or execution.status != PhaseStatus.COMPLETED:
                can_execute, _ = self.can_execute_phase(phase)
                if can_execute:
                    return phase

        # All phases completed
        return None

    def get_workflow_status_display(self) -> str:
        """Generate human-readable workflow status display.

        Returns:
            Formatted string showing all phases and their status
        """
        phases = [
            (WorkflowPhase.ASSESSMENT, "/brownkit.assess"),
            (WorkflowPhase.PLANNING, "/brownkit.plan"),
            (WorkflowPhase.REMEDIATION, "/brownkit.remediate"),
            (WorkflowPhase.VALIDATION, "/brownkit.validate"),
            (WorkflowPhase.GRADUATION, "/brownkit.graduate"),
        ]

        lines = ["Current workflow status:"]
        for phase, command in phases:
            execution = self.phase_executions.get(phase)

            if execution:
                if execution.status == PhaseStatus.COMPLETED:
                    lines.append(f"  ✅ {command}")
                elif execution.status == PhaseStatus.IN_PROGRESS:
                    lines.append(f"  🔄 {command} (in progress)")
                elif execution.status == PhaseStatus.FAILED:
                    lines.append(f"  ❌ {command} (failed)")
                else:
                    lines.append(f"  ⬜ {command} (not started)")
            else:
                lines.append(f"  ⬜ {command} (not started)")

        return "\n".join(lines)

    def is_phase_completed(self, phase: WorkflowPhase) -> bool:
        """Check if a specific phase has been completed.

        Args:
            phase: Phase to check

        Returns:
            True if phase completed, False otherwise
        """
        execution = self.phase_executions.get(phase)
        return execution is not None and execution.status == PhaseStatus.COMPLETED
