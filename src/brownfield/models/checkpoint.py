"""Phase checkpoint models for interruption recovery."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from brownfield.models.state import Phase


@dataclass
class Task:
    """Individual task within a phase."""

    task_id: str
    description: str
    completed: bool
    completed_at: Optional[datetime] = None
    git_commit_sha: Optional[str] = None


@dataclass
class PhaseCheckpoint:
    """Checkpoint for interruption recovery."""

    phase: Phase
    started_at: datetime
    last_checkpoint_at: datetime
    tasks: list[Task] = field(default_factory=list)
    interrupted: bool = False

    @property
    def completed_tasks(self) -> list[Task]:
        """Return list of completed tasks."""
        return [t for t in self.tasks if t.completed]

    @property
    def pending_tasks(self) -> list[Task]:
        """Return list of pending tasks."""
        return [t for t in self.tasks if not t.completed]

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if not self.tasks:
            return 0.0
        return len(self.completed_tasks) / len(self.tasks) * 100

    def mark_task_complete(
        self, task_id: str, commit_sha: Optional[str] = None
    ) -> None:
        """Mark task as completed and update checkpoint timestamp."""
        for task in self.tasks:
            if task.task_id == task_id:
                task.completed = True
                task.completed_at = datetime.utcnow()
                task.git_commit_sha = commit_sha
                break
        self.last_checkpoint_at = datetime.utcnow()

    def detect_interruption(self) -> bool:
        """Check if process was interrupted."""
        if not self.interrupted:
            return False

        # Consider interrupted if last checkpoint > 5 minutes ago and incomplete
        time_since_checkpoint = datetime.utcnow() - self.last_checkpoint_at
        return (
            time_since_checkpoint.total_seconds() > 300
            and len(self.pending_tasks) > 0
        )
