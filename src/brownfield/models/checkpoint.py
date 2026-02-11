"""Phase checkpoint models for interruption recovery."""

from dataclasses import dataclass, field
from datetime import datetime

from brownfield.models.state import Phase


@dataclass
class Task:
    """Individual task within a phase.

    Unified task model for both orchestrator execution and checkpoint persistence.
    """

    task_id: str  # Unique identifier (e.g., "install_pytest")
    description: str  # Human-readable description
    phase: Phase  # STRUCTURE, TESTING, or QUALITY
    estimated_minutes: int  # Time estimate for planning
    completed: bool = False  # Completion status
    completed_at: datetime | None = None  # When task completed
    git_commit_sha: str | None = None  # Git commit if task was committed
    status: str | None = None  # "pending", "in_progress", "completed", "failed"
    error_message: str | None = None  # Captured error if task failed

    def __post_init__(self):
        """Auto-set status from completed if not provided."""
        if self.status is None:
            self.status = "completed" if self.completed else "pending"


@dataclass
class PhaseCheckpoint:
    """Checkpoint for interruption recovery.

    Unified model matching CheckpointManager serialization format.
    """

    phase: Phase
    completed_tasks: list[Task] = field(default_factory=list)
    pending_tasks: list[Task] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    interrupted: bool = False
    context: dict = field(default_factory=dict)

    @property
    def tasks(self) -> list[Task]:
        """Return all tasks (completed + pending)."""
        return self.completed_tasks + self.pending_tasks

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        total_tasks = len(self.completed_tasks) + len(self.pending_tasks)
        if total_tasks == 0:
            return 0.0
        return len(self.completed_tasks) / total_tasks * 100

    def mark_task_complete(self, task_id: str, commit_sha: str | None = None) -> None:
        """Mark task as completed and update checkpoint timestamp."""
        # Find task in pending_tasks
        for i, task in enumerate(self.pending_tasks):
            if task.task_id == task_id:
                task.completed = True
                task.completed_at = datetime.utcnow()
                task.git_commit_sha = commit_sha
                task.status = "completed"
                # Move from pending to completed
                self.completed_tasks.append(task)
                self.pending_tasks.pop(i)
                break
        self.timestamp = datetime.utcnow()

    def detect_interruption(self) -> bool:
        """Check if process was interrupted."""
        if not self.interrupted:
            return False

        # Consider interrupted if last checkpoint > 5 minutes ago and incomplete
        time_since_checkpoint = datetime.utcnow() - self.timestamp
        return time_since_checkpoint.total_seconds() > 300 and len(self.pending_tasks) > 0
