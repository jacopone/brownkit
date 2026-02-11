"""Checkpoint manager for interruption recovery."""

import json
from datetime import datetime
from pathlib import Path

from brownfield.models.checkpoint import PhaseCheckpoint, Task
from brownfield.models.state import Phase


class CheckpointManager:
    """Manages checkpoints for interruption recovery."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.checkpoint_dir = project_root / ".specify" / "brownfield" / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(
        self,
        phase: Phase,
        completed_tasks: list[Task],
        pending_tasks: list[Task],
        context: dict | None = None,
        interrupted: bool = False,
    ) -> Path:
        """
        Save checkpoint for current phase.

        Args:
            phase: Current phase
            completed_tasks: List of completed tasks
            pending_tasks: List of pending tasks
            context: Additional context data

        Returns:
            Path to saved checkpoint file
        """
        checkpoint = PhaseCheckpoint(
            phase=phase,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            timestamp=datetime.utcnow(),
            interrupted=interrupted,
            context=context or {},
        )

        checkpoint_path = self.checkpoint_dir / f"{phase.value}-checkpoint.json"
        checkpoint_path.write_text(
            json.dumps(self._checkpoint_to_dict(checkpoint), indent=2),
            encoding="utf-8",
        )

        return checkpoint_path

    def load_checkpoint(self, phase: Phase) -> PhaseCheckpoint | None:
        """
        Load checkpoint for given phase.

        Args:
            phase: Phase to load checkpoint for

        Returns:
            PhaseCheckpoint if exists, None otherwise
        """
        checkpoint_path = self.checkpoint_dir / f"{phase.value}-checkpoint.json"

        if not checkpoint_path.exists():
            return None

        with open(checkpoint_path, encoding="utf-8") as f:
            data = json.load(f)

        return self._dict_to_checkpoint(data)

    def mark_interrupted(self, phase: Phase) -> None:
        """
        Mark checkpoint as interrupted.

        Args:
            phase: Phase that was interrupted
        """
        checkpoint = self.load_checkpoint(phase)
        if checkpoint:
            checkpoint.interrupted = True
            self.save_checkpoint(
                phase,
                checkpoint.completed_tasks,
                checkpoint.pending_tasks,
                checkpoint.context,
                interrupted=True,
            )

    def detect_interruption(self, phase: Phase) -> bool:
        """
        Check if phase was interrupted.

        Args:
            phase: Phase to check

        Returns:
            True if phase was interrupted
        """
        checkpoint = self.load_checkpoint(phase)
        return checkpoint.interrupted if checkpoint else False

    def get_resumption_options(self, phase: Phase) -> dict:
        """
        Get options for resuming interrupted phase.

        Args:
            phase: Interrupted phase

        Returns:
            Dictionary with resumption options
        """
        checkpoint = self.load_checkpoint(phase)

        if not checkpoint:
            return {"can_resume": False, "reason": "No checkpoint found"}

        if not checkpoint.interrupted:
            return {"can_resume": False, "reason": "Phase not interrupted"}

        return {
            "can_resume": True,
            "completed_count": len(checkpoint.completed_tasks),
            "pending_count": len(checkpoint.pending_tasks),
            "timestamp": checkpoint.timestamp.isoformat(),
            "next_task": checkpoint.pending_tasks[0] if checkpoint.pending_tasks else None,
        }

    def clear_checkpoint(self, phase: Phase) -> None:
        """
        Clear checkpoint for given phase.

        Args:
            phase: Phase to clear checkpoint for
        """
        checkpoint_path = self.checkpoint_dir / f"{phase.value}-checkpoint.json"
        if checkpoint_path.exists():
            checkpoint_path.unlink()

    def list_all_checkpoints(self) -> list[dict]:
        """
        List all available checkpoints.

        Returns:
            List of checkpoint summaries
        """
        checkpoints = []

        for checkpoint_file in self.checkpoint_dir.glob("*-checkpoint.json"):
            with open(checkpoint_file, encoding="utf-8") as f:
                data = json.load(f)

            checkpoints.append(
                {
                    "phase": data["phase"],
                    "timestamp": data["timestamp"],
                    "interrupted": data["interrupted"],
                    "completed_tasks": len(data["completed_tasks"]),
                    "pending_tasks": len(data["pending_tasks"]),
                }
            )

        return sorted(checkpoints, key=lambda x: x["timestamp"], reverse=True)

    def _checkpoint_to_dict(self, checkpoint: PhaseCheckpoint) -> dict:
        """Convert checkpoint to dictionary for JSON serialization."""
        return {
            "phase": checkpoint.phase.value,
            "completed_tasks": [
                {
                    "id": t.task_id,
                    "description": t.description,
                    "phase": t.phase.value,
                    "estimated_minutes": t.estimated_minutes,
                    "completed": t.completed,
                    "status": t.status,
                    "error_message": t.error_message,
                    "git_commit_sha": t.git_commit_sha,
                }
                for t in checkpoint.completed_tasks
            ],
            "pending_tasks": [
                {
                    "id": t.task_id,
                    "description": t.description,
                    "phase": t.phase.value,
                    "estimated_minutes": t.estimated_minutes,
                    "completed": t.completed,
                    "status": t.status,
                    "error_message": t.error_message,
                    "git_commit_sha": t.git_commit_sha,
                }
                for t in checkpoint.pending_tasks
            ],
            "timestamp": checkpoint.timestamp.isoformat(),
            "interrupted": checkpoint.interrupted,
            "context": checkpoint.context,
        }

    def _dict_to_checkpoint(self, data: dict) -> PhaseCheckpoint:
        """Convert dictionary to PhaseCheckpoint."""
        return PhaseCheckpoint(
            phase=Phase(data["phase"]),
            completed_tasks=[
                Task(
                    task_id=t["id"],
                    description=t["description"],
                    phase=Phase(t["phase"]),
                    estimated_minutes=t["estimated_minutes"],
                    completed=t.get("completed", True),
                    status=t.get("status", "completed"),
                    error_message=t.get("error_message"),
                    git_commit_sha=t.get("git_commit_sha"),
                )
                for t in data["completed_tasks"]
            ],
            pending_tasks=[
                Task(
                    task_id=t["id"],
                    description=t["description"],
                    phase=Phase(t["phase"]),
                    estimated_minutes=t["estimated_minutes"],
                    completed=t.get("completed", False),
                    status=t.get("status", "pending"),
                    error_message=t.get("error_message"),
                    git_commit_sha=t.get("git_commit_sha"),
                )
                for t in data["pending_tasks"]
            ],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            interrupted=data["interrupted"],
            context=data.get("context", {}),
        )
