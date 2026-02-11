"""Tests for checkpoint directory migration (.brownfield/ → .specify/brownfield/)."""

import json

import pytest

from brownfield.models.checkpoint import Task
from brownfield.models.state import Phase
from brownfield.orchestrator.checkpoint_manager import CheckpointManager


class TestCheckpointDirectoryMigration:
    """Test checkpoint directory migration from old to new location."""

    @pytest.fixture
    def temp_project_root(self, tmp_path):
        """Create temporary project root."""
        return tmp_path

    @pytest.fixture
    def old_checkpoint_dir(self, temp_project_root):
        """Create old checkpoint directory."""
        old_dir = temp_project_root / ".brownfield" / "checkpoints"
        old_dir.mkdir(parents=True)
        return old_dir

    @pytest.fixture
    def new_checkpoint_dir(self, temp_project_root):
        """Create new checkpoint directory."""
        new_dir = temp_project_root / ".specify" / "brownfield" / "checkpoints"
        return new_dir

    @pytest.fixture
    def sample_checkpoint_data(self):
        """Create sample checkpoint data."""
        return {
            "phase": "testing",
            "completed_tasks": [
                {
                    "id": "task1",
                    "description": "Install pytest",
                    "phase": "testing",
                    "estimated_minutes": 10,
                    "completed": True,
                    "status": "completed",
                    "error_message": None,
                }
            ],
            "pending_tasks": [
                {
                    "id": "task2",
                    "description": "Write tests",
                    "phase": "testing",
                    "estimated_minutes": 60,
                    "completed": False,
                    "status": "pending",
                    "error_message": None,
                }
            ],
            "timestamp": "2025-01-01T00:00:00",
            "interrupted": False,
            "context": {},
        }

    def test_checkpoint_manager_uses_new_path(self, temp_project_root):
        """Test CheckpointManager creates checkpoints in new location."""
        manager = CheckpointManager(temp_project_root)

        expected_dir = temp_project_root / ".specify" / "brownfield" / "checkpoints"
        assert manager.checkpoint_dir == expected_dir

    def test_checkpoint_manager_creates_new_directory(self, temp_project_root):
        """Test CheckpointManager creates new directory structure."""
        CheckpointManager(temp_project_root)

        new_dir = temp_project_root / ".specify" / "brownfield" / "checkpoints"
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_save_checkpoint_uses_new_location(self, temp_project_root, new_checkpoint_dir):
        """Test saving checkpoint uses new location."""
        manager = CheckpointManager(temp_project_root)

        task = Task(
            task_id="test_task",
            description="Test task",
            phase=Phase.TESTING,
            estimated_minutes=10,
            completed=False,
        )

        checkpoint_path = manager.save_checkpoint(
            Phase.TESTING,
            completed_tasks=[],
            pending_tasks=[task],
        )

        assert checkpoint_path.exists()
        assert ".specify/brownfield/checkpoints" in str(checkpoint_path)
        assert checkpoint_path.parent == new_checkpoint_dir

    def test_load_checkpoint_from_new_location(self, temp_project_root):
        """Test loading checkpoint from new location."""
        manager = CheckpointManager(temp_project_root)

        # Save checkpoint
        task = Task(
            task_id="test_task",
            description="Test task",
            phase=Phase.TESTING,
            estimated_minutes=10,
            completed=False,
        )

        manager.save_checkpoint(
            Phase.TESTING,
            completed_tasks=[],
            pending_tasks=[task],
        )

        # Load checkpoint
        loaded = manager.load_checkpoint(Phase.TESTING)

        assert loaded is not None
        assert loaded.phase == Phase.TESTING
        assert len(loaded.pending_tasks) == 1
        assert loaded.pending_tasks[0].task_id == "test_task"

    def test_list_checkpoints_from_new_location(self, temp_project_root):
        """Test listing checkpoints from new location."""
        manager = CheckpointManager(temp_project_root)

        # Create multiple checkpoints
        for phase in [Phase.STRUCTURE, Phase.TESTING, Phase.QUALITY]:
            task = Task(
                task_id=f"{phase.value}_task",
                description=f"{phase.value} task",
                phase=phase,
                estimated_minutes=10,
            )
            manager.save_checkpoint(phase, completed_tasks=[], pending_tasks=[task])

        # List all checkpoints
        checkpoints = manager.list_all_checkpoints()

        assert len(checkpoints) == 3
        phases = {cp["phase"] for cp in checkpoints}
        assert phases == {"structure", "testing", "quality"}

    def test_clear_checkpoint_from_new_location(self, temp_project_root):
        """Test clearing checkpoint from new location."""
        manager = CheckpointManager(temp_project_root)

        # Create checkpoint
        task = Task(
            task_id="test_task",
            description="Test task",
            phase=Phase.TESTING,
            estimated_minutes=10,
        )
        manager.save_checkpoint(Phase.TESTING, completed_tasks=[], pending_tasks=[task])

        # Verify it exists
        assert manager.load_checkpoint(Phase.TESTING) is not None

        # Clear it
        manager.clear_checkpoint(Phase.TESTING)

        # Verify it's gone
        assert manager.load_checkpoint(Phase.TESTING) is None

    def test_old_checkpoint_location_not_created(self, temp_project_root):
        """Test that CheckpointManager doesn't create old .brownfield/ directory."""
        CheckpointManager(temp_project_root)

        old_dir = temp_project_root / ".brownfield" / "checkpoints"
        assert not old_dir.exists()


class TestCheckpointBackwardCompatibility:
    """Test backward compatibility for projects with old checkpoints."""

    @pytest.fixture
    def temp_project_root(self, tmp_path):
        """Create temporary project root."""
        return tmp_path

    @pytest.fixture
    def old_checkpoint_file(self, temp_project_root):
        """Create old checkpoint file in .brownfield/ location."""
        old_dir = temp_project_root / ".brownfield" / "checkpoints"
        old_dir.mkdir(parents=True)

        checkpoint_data = {
            "phase": "testing",
            "completed_tasks": [
                {
                    "id": "task1",
                    "description": "Install pytest",
                    "phase": "testing",
                    "estimated_minutes": 10,
                    "completed": True,
                    "status": "completed",
                    "error_message": None,
                }
            ],
            "pending_tasks": [],
            "timestamp": "2025-01-01T00:00:00",
            "interrupted": False,
            "context": {},
        }

        checkpoint_path = old_dir / "testing-checkpoint.json"
        with open(checkpoint_path, "w") as f:
            json.dump(checkpoint_data, f, indent=2)

        return checkpoint_path

    def test_detect_old_checkpoint_location(self, temp_project_root, old_checkpoint_file):
        """Test detecting checkpoints in old location."""
        old_dir = temp_project_root / ".brownfield" / "checkpoints"
        assert old_checkpoint_file.exists()
        assert old_checkpoint_file in list(old_dir.glob("*.json"))

    def test_manual_migration_preserves_checkpoints(self, temp_project_root, old_checkpoint_file):
        """Test manual checkpoint migration preserves all data."""
        import shutil

        # Manually migrate checkpoint (simulating migration command)
        new_dir = temp_project_root / ".specify" / "brownfield" / "checkpoints"
        new_dir.mkdir(parents=True)

        shutil.copy2(old_checkpoint_file, new_dir / old_checkpoint_file.name)

        # Verify checkpoint is accessible in new location
        manager = CheckpointManager(temp_project_root)
        loaded = manager.load_checkpoint(Phase.TESTING)

        assert loaded is not None
        assert loaded.phase == Phase.TESTING
        assert len(loaded.completed_tasks) == 1
        assert loaded.completed_tasks[0].task_id == "task1"

    def test_checkpoint_manager_ignores_old_location(self, temp_project_root, old_checkpoint_file):
        """Test that CheckpointManager ignores old checkpoint location."""
        # Old checkpoint exists but CheckpointManager uses new location
        manager = CheckpointManager(temp_project_root)

        # Should not find checkpoint (it's in old location)
        loaded = manager.load_checkpoint(Phase.TESTING)
        assert loaded is None

        # List should be empty
        checkpoints = manager.list_all_checkpoints()
        assert len(checkpoints) == 0
