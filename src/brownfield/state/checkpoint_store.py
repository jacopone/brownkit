"""Checkpoint persistence for interruption recovery."""

from pathlib import Path

from brownfield.models.checkpoint import PhaseCheckpoint


class CheckpointStore:
    """Manages phase checkpoint persistence."""

    def __init__(self, checkpoint_path: Path):
        self.checkpoint_path = checkpoint_path

    def save(self, checkpoint: PhaseCheckpoint) -> None:
        """Save checkpoint to file."""
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        # TODO: Implement JSON serialization

    def load(self) -> PhaseCheckpoint:
        """Load checkpoint from file."""
        # TODO: Implement JSON deserialization

    def exists(self) -> bool:
        """Check if checkpoint file exists."""
        return self.checkpoint_path.exists()
