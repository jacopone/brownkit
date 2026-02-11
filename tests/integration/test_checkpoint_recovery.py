"""Integration tests for checkpoint-based recovery workflows.

Tests interruption recovery and checkpoint validation.
"""

import pytest

from brownfield.models.assessment import Metrics
from brownfield.models.checkpoint import Task
from brownfield.models.state import BrownfieldState, Phase
from brownfield.orchestrator.checkpoint_manager import CheckpointManager
from brownfield.state.state_store import StateStore


class TestCheckpointRecovery:
    """Test checkpoint-based interruption recovery."""

    @pytest.fixture
    def project_with_checkpoints(self, tmp_path):
        """Create project with checkpoint state."""
        project_root = tmp_path / "checkpoint_project"
        project_root.mkdir()

        # Create directory structure
        memory_dir = project_root / ".specify" / "memory"
        memory_dir.mkdir(parents=True)

        checkpoint_dir = project_root / ".specify" / "brownfield" / "checkpoints"
        checkpoint_dir.mkdir(parents=True)

        # Create baseline state
        metrics = Metrics(
            test_coverage=0.5,
            complexity_avg=10.0,
            complexity_max=15,
            critical_vulnerabilities=0,
            high_vulnerabilities=1,
            medium_vulnerabilities=3,
            build_status="passing",
            documentation_coverage=0.4,
            total_loc=1000,
            test_loc=500,
            git_commits=10,
            git_secrets_found=0,
        )

        state = BrownfieldState(
            workflow="brownfield",
            schema_version="2.0",
            project_root=project_root,
            current_phase=Phase.TESTING,
            baseline_metrics=metrics,
            current_metrics=metrics,
        )

        state_store = StateStore(memory_dir / "state.json")
        state_store.save(state)

        return project_root

    def test_save_checkpoint_during_remediation(self, project_with_checkpoints):
        """Test checkpoint is saved during remediation."""
        manager = CheckpointManager(project_with_checkpoints)

        # Create test tasks
        tasks = [
            Task(
                task_id="install_pytest",
                description="Install pytest framework",
                phase=Phase.TESTING,
                estimated_minutes=10,
                completed=False,
            ),
            Task(
                task_id="write_tests",
                description="Write unit tests",
                phase=Phase.TESTING,
                estimated_minutes=60,
                completed=False,
            ),
        ]

        # Save checkpoint with one task completed
        completed = [tasks[0]]
        completed[0].completed = True
        pending = [tasks[1]]

        checkpoint_path = manager.save_checkpoint(
            Phase.TESTING,
            completed_tasks=completed,
            pending_tasks=pending,
        )

        # Verify checkpoint was created
        assert checkpoint_path.exists()
        assert "testing-checkpoint.json" in str(checkpoint_path)

    def test_load_checkpoint_after_interruption(self, project_with_checkpoints):
        """Test checkpoint can be loaded after interruption."""
        manager = CheckpointManager(project_with_checkpoints)

        # Create and save checkpoint
        completed_task = Task(
            task_id="setup_test_framework",
            description="Setup testing framework",
            phase=Phase.TESTING,
            estimated_minutes=15,
            completed=True,
        )

        pending_task = Task(
            task_id="write_tests",
            description="Write unit tests",
            phase=Phase.TESTING,
            estimated_minutes=60,
            completed=False,
        )

        manager.save_checkpoint(
            Phase.TESTING,
            completed_tasks=[completed_task],
            pending_tasks=[pending_task],
        )

        # Simulate interruption and reload
        loaded_checkpoint = manager.load_checkpoint(Phase.TESTING)

        assert loaded_checkpoint is not None
        assert len(loaded_checkpoint.completed_tasks) == 1
        assert len(loaded_checkpoint.pending_tasks) == 1
        assert loaded_checkpoint.completed_tasks[0].task_id == "setup_test_framework"
        assert loaded_checkpoint.pending_tasks[0].task_id == "write_tests"

    def test_checkpoint_resume_from_interruption(self, project_with_checkpoints):
        """Test resuming work from checkpoint after interruption."""
        manager = CheckpointManager(project_with_checkpoints)

        # Create multi-task checkpoint
        completed_tasks = [
            Task(
                task_id=f"task_{i}",
                description=f"Completed task {i}",
                phase=Phase.TESTING,
                estimated_minutes=10,
                completed=True,
            )
            for i in range(3)
        ]

        pending_tasks = [
            Task(
                task_id=f"task_{i}",
                description=f"Pending task {i}",
                phase=Phase.TESTING,
                estimated_minutes=10,
                completed=False,
            )
            for i in range(3, 6)
        ]

        manager.save_checkpoint(
            Phase.TESTING,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
        )

        # Load checkpoint
        checkpoint = manager.load_checkpoint(Phase.TESTING)

        # Verify we can resume from correct position
        assert len(checkpoint.completed_tasks) == 3
        assert len(checkpoint.pending_tasks) == 3
        assert checkpoint.progress_percentage == 50.0  # 3/6 = 50%

        # Complete next task
        next_task = checkpoint.pending_tasks[0]
        checkpoint.mark_task_complete(next_task.task_id)

        # Verify progress updated
        assert len(checkpoint.completed_tasks) == 4
        assert len(checkpoint.pending_tasks) == 2
        assert checkpoint.progress_percentage == pytest.approx(66.67, rel=0.1)

    def test_checkpoint_interruption_detection(self, project_with_checkpoints):
        """Test detection of interrupted workflow."""
        manager = CheckpointManager(project_with_checkpoints)

        # Create checkpoint with pending tasks
        pending_tasks = [
            Task(
                task_id="incomplete_task",
                description="Task that was interrupted",
                phase=Phase.TESTING,
                estimated_minutes=30,
                completed=False,
            )
        ]

        manager.save_checkpoint(
            Phase.TESTING,
            completed_tasks=[],
            pending_tasks=pending_tasks,
        )

        # Mark as interrupted
        manager.mark_interrupted(Phase.TESTING)

        # Verify interruption is detected
        assert manager.detect_interruption(Phase.TESTING) is True

    def test_get_resumption_options(self, project_with_checkpoints):
        """Test get resumption options for interrupted phase."""
        manager = CheckpointManager(project_with_checkpoints)

        # Create checkpoint
        completed = [
            Task(
                task_id="done",
                description="Completed",
                phase=Phase.TESTING,
                estimated_minutes=10,
                completed=True,
            )
        ]

        pending = [
            Task(
                task_id="pending_1",
                description="Pending 1",
                phase=Phase.TESTING,
                estimated_minutes=20,
                completed=False,
            ),
            Task(
                task_id="pending_2",
                description="Pending 2",
                phase=Phase.TESTING,
                estimated_minutes=30,
                completed=False,
            ),
        ]

        manager.save_checkpoint(Phase.TESTING, completed_tasks=completed, pending_tasks=pending)
        manager.mark_interrupted(Phase.TESTING)

        # Get resumption options
        options = manager.get_resumption_options(Phase.TESTING)

        assert options["can_resume"] is True
        assert options["completed_count"] == 1
        assert options["pending_count"] == 2
        assert options["next_task"] is not None
        assert options["next_task"].task_id == "pending_1"

    def test_clear_checkpoint_after_completion(self, project_with_checkpoints):
        """Test clearing checkpoint after phase completion."""
        manager = CheckpointManager(project_with_checkpoints)

        # Save checkpoint
        task = Task(
            task_id="test_task",
            description="Test task",
            phase=Phase.TESTING,
            estimated_minutes=10,
        )

        manager.save_checkpoint(Phase.TESTING, completed_tasks=[], pending_tasks=[task])

        # Verify checkpoint exists
        assert manager.load_checkpoint(Phase.TESTING) is not None

        # Clear checkpoint
        manager.clear_checkpoint(Phase.TESTING)

        # Verify checkpoint is gone
        assert manager.load_checkpoint(Phase.TESTING) is None

    def test_multiple_phase_checkpoints(self, project_with_checkpoints):
        """Test managing checkpoints for multiple phases."""
        manager = CheckpointManager(project_with_checkpoints)

        # Create checkpoints for different phases
        for phase in [Phase.STRUCTURE, Phase.TESTING, Phase.QUALITY]:
            task = Task(
                task_id=f"{phase.value}_task",
                description=f"Task for {phase.value}",
                phase=phase,
                estimated_minutes=20,
            )

            manager.save_checkpoint(phase, completed_tasks=[], pending_tasks=[task])

        # List all checkpoints
        checkpoints = manager.list_all_checkpoints()

        assert len(checkpoints) == 3
        phases = {cp["phase"] for cp in checkpoints}
        assert phases == {"structure", "testing", "quality"}

    def test_checkpoint_with_git_commit_tracking(self, project_with_checkpoints):
        """Test checkpoint tracks git commits for completed tasks."""
        manager = CheckpointManager(project_with_checkpoints)

        # Create task with git commit
        task = Task(
            task_id="refactor_module",
            description="Refactor core module",
            phase=Phase.QUALITY,
            estimated_minutes=45,
            completed=True,
            git_commit_sha="abc1234",
        )

        manager.save_checkpoint(Phase.QUALITY, completed_tasks=[task], pending_tasks=[])

        # Load and verify commit is tracked
        checkpoint = manager.load_checkpoint(Phase.QUALITY)

        assert checkpoint.completed_tasks[0].git_commit_sha == "abc1234"

    def test_checkpoint_context_preservation(self, project_with_checkpoints):
        """Test checkpoint preserves additional context."""
        manager = CheckpointManager(project_with_checkpoints)

        # Save checkpoint with context
        task = Task(
            task_id="complex_task",
            description="Complex refactoring",
            phase=Phase.STRUCTURE,
            estimated_minutes=90,
        )

        context = {
            "files_to_move": ["old/path.py", "another/file.py"],
            "backup_created": True,
            "user_approved": True,
        }

        manager.save_checkpoint(
            Phase.STRUCTURE,
            completed_tasks=[],
            pending_tasks=[task],
            context=context,
        )

        # Load and verify context
        checkpoint = manager.load_checkpoint(Phase.STRUCTURE)

        assert checkpoint.context["files_to_move"] == ["old/path.py", "another/file.py"]
        assert checkpoint.context["backup_created"] is True
        assert checkpoint.context["user_approved"] is True
