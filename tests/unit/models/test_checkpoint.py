"""Tests for checkpoint models."""

import pytest
from datetime import datetime

from brownfield.models.checkpoint import Task, PhaseCheckpoint
from brownfield.models.state import Phase


class TestTask:
    """Test Task model."""

    def test_task_creation_with_all_fields(self):
        """Test Task can be created with all fields."""
        task = Task(
            task_id="test_task",
            description="Test task description",
            phase=Phase.TESTING,
            estimated_minutes=30,
            completed=True,
            status="completed",
            error_message=None,
        )

        assert task.task_id == "test_task"
        assert task.description == "Test task description"
        assert task.phase == Phase.TESTING
        assert task.estimated_minutes == 30
        assert task.completed is True
        assert task.status == "completed"
        assert task.error_message is None

    def test_task_status_auto_set_from_completed(self):
        """Test status is auto-set from completed if not provided."""
        # Task marked as not completed should get "pending" status
        task_pending = Task(
            task_id="pending_task",
            description="Pending task",
            phase=Phase.TESTING,
            estimated_minutes=10,
        )
        assert task_pending.completed is False
        assert task_pending.status == "pending"

        # Task marked as completed should get "completed" status
        task_completed = Task(
            task_id="completed_task",
            description="Completed task",
            phase=Phase.TESTING,
            estimated_minutes=10,
            completed=True,
        )
        assert task_completed.status == "completed"

    def test_task_explicit_status_overrides_auto_status(self):
        """Test explicit status is preserved even if it conflicts with completed."""
        # Completed task with explicit "in_progress" status
        task = Task(
            task_id="test_task",
            description="Test",
            phase=Phase.TESTING,
            estimated_minutes=10,
            completed=False,
            status="in_progress",
        )
        assert task.status == "in_progress"
        assert task.completed is False

    def test_task_with_error_message(self):
        """Test task can capture error messages."""
        error_msg = "ImportError: Module not found"
        task = Task(
            task_id="failed_task",
            description="Install dependencies",
            phase=Phase.TESTING,
            estimated_minutes=15,
            completed=False,
            status="failed",
            error_message=error_msg,
        )

        assert task.status == "failed"
        assert task.error_message == error_msg
        assert task.completed is False

    def test_task_different_phases(self):
        """Test tasks can be created for different phases."""
        phases_to_test = [Phase.STRUCTURE, Phase.TESTING, Phase.QUALITY]

        for phase in phases_to_test:
            task = Task(
                task_id=f"task_{phase.value}",
                description=f"Task for {phase.value}",
                phase=phase,
                estimated_minutes=20,
            )
            assert task.phase == phase

    def test_task_with_git_commit(self):
        """Test task can track git commit SHA."""
        task = Task(
            task_id="committed_task",
            description="Created config file",
            phase=Phase.QUALITY,
            estimated_minutes=10,
            completed=True,
            git_commit_sha="abc123def456",
        )

        assert task.git_commit_sha == "abc123def456"

    def test_task_with_completed_at_timestamp(self):
        """Test task can track completion timestamp."""
        completed_time = datetime.utcnow()
        task = Task(
            task_id="timed_task",
            description="Timed task",
            phase=Phase.TESTING,
            estimated_minutes=30,
            completed=True,
            completed_at=completed_time,
        )

        assert task.completed_at == completed_time


class TestPhaseCheckpoint:
    """Test PhaseCheckpoint model."""

    @pytest.fixture
    def sample_tasks(self):
        """Create sample tasks for testing."""
        return [
            Task(
                task_id="task_1",
                description="First task",
                phase=Phase.TESTING,
                estimated_minutes=10,
                completed=True,
            ),
            Task(
                task_id="task_2",
                description="Second task",
                phase=Phase.TESTING,
                estimated_minutes=15,
                completed=True,
            ),
            Task(
                task_id="task_3",
                description="Third task",
                phase=Phase.TESTING,
                estimated_minutes=20,
                completed=False,
            ),
        ]

    def test_checkpoint_creation(self, sample_tasks):
        """Test checkpoint can be created with tasks."""
        now = datetime.utcnow()
        checkpoint = PhaseCheckpoint(
            phase=Phase.TESTING,
            started_at=now,
            last_checkpoint_at=now,
            tasks=sample_tasks,
        )

        assert checkpoint.phase == Phase.TESTING
        assert len(checkpoint.tasks) == 3
        assert checkpoint.interrupted is False

    def test_checkpoint_completed_tasks_property(self, sample_tasks):
        """Test completed_tasks property returns only completed tasks."""
        checkpoint = PhaseCheckpoint(
            phase=Phase.TESTING,
            started_at=datetime.utcnow(),
            last_checkpoint_at=datetime.utcnow(),
            tasks=sample_tasks,
        )

        completed = checkpoint.completed_tasks
        assert len(completed) == 2
        assert all(task.completed for task in completed)
        assert completed[0].task_id == "task_1"
        assert completed[1].task_id == "task_2"

    def test_checkpoint_pending_tasks_property(self, sample_tasks):
        """Test pending_tasks property returns only incomplete tasks."""
        checkpoint = PhaseCheckpoint(
            phase=Phase.TESTING,
            started_at=datetime.utcnow(),
            last_checkpoint_at=datetime.utcnow(),
            tasks=sample_tasks,
        )

        pending = checkpoint.pending_tasks
        assert len(pending) == 1
        assert not pending[0].completed
        assert pending[0].task_id == "task_3"

    def test_checkpoint_progress_percentage(self, sample_tasks):
        """Test progress_percentage calculation."""
        checkpoint = PhaseCheckpoint(
            phase=Phase.TESTING,
            started_at=datetime.utcnow(),
            last_checkpoint_at=datetime.utcnow(),
            tasks=sample_tasks,
        )

        # 2 out of 3 tasks completed = 66.67%
        progress = checkpoint.progress_percentage
        assert abs(progress - 66.67) < 0.1

    def test_checkpoint_progress_percentage_no_tasks(self):
        """Test progress_percentage returns 0 when no tasks."""
        checkpoint = PhaseCheckpoint(
            phase=Phase.TESTING,
            started_at=datetime.utcnow(),
            last_checkpoint_at=datetime.utcnow(),
            tasks=[],
        )

        assert checkpoint.progress_percentage == 0.0

    def test_checkpoint_progress_percentage_all_completed(self):
        """Test progress_percentage returns 100 when all completed."""
        tasks = [
            Task(
                task_id="task_1",
                description="Task 1",
                phase=Phase.TESTING,
                estimated_minutes=10,
                completed=True,
            ),
            Task(
                task_id="task_2",
                description="Task 2",
                phase=Phase.TESTING,
                estimated_minutes=10,
                completed=True,
            ),
        ]

        checkpoint = PhaseCheckpoint(
            phase=Phase.TESTING,
            started_at=datetime.utcnow(),
            last_checkpoint_at=datetime.utcnow(),
            tasks=tasks,
        )

        assert checkpoint.progress_percentage == 100.0

    def test_mark_task_complete(self, sample_tasks):
        """Test marking a task as complete."""
        checkpoint = PhaseCheckpoint(
            phase=Phase.TESTING,
            started_at=datetime.utcnow(),
            last_checkpoint_at=datetime.utcnow(),
            tasks=sample_tasks,
        )

        # Mark task_3 as complete
        commit_sha = "abc123"
        checkpoint.mark_task_complete("task_3", commit_sha=commit_sha)

        # Verify task is marked complete
        task_3 = next(t for t in checkpoint.tasks if t.task_id == "task_3")
        assert task_3.completed is True
        assert task_3.git_commit_sha == commit_sha
        assert task_3.completed_at is not None

    def test_mark_task_complete_updates_checkpoint_time(self, sample_tasks):
        """Test marking task complete updates checkpoint timestamp."""
        now = datetime.utcnow()
        checkpoint = PhaseCheckpoint(
            phase=Phase.TESTING,
            started_at=now,
            last_checkpoint_at=now,
            tasks=sample_tasks,
        )

        original_time = checkpoint.last_checkpoint_at

        # Wait a moment and mark task complete
        import time

        time.sleep(0.1)
        checkpoint.mark_task_complete("task_3")

        # Checkpoint time should be updated
        assert checkpoint.last_checkpoint_at > original_time

    def test_detect_interruption_not_interrupted(self, sample_tasks):
        """Test detect_interruption returns False when not interrupted."""
        checkpoint = PhaseCheckpoint(
            phase=Phase.TESTING,
            started_at=datetime.utcnow(),
            last_checkpoint_at=datetime.utcnow(),
            tasks=sample_tasks,
            interrupted=False,
        )

        assert checkpoint.detect_interruption() is False

    def test_detect_interruption_no_pending_tasks(self):
        """Test detect_interruption returns False when all tasks completed."""
        tasks = [
            Task(
                task_id="task_1",
                description="Task 1",
                phase=Phase.TESTING,
                estimated_minutes=10,
                completed=True,
            ),
        ]

        checkpoint = PhaseCheckpoint(
            phase=Phase.TESTING,
            started_at=datetime.utcnow(),
            last_checkpoint_at=datetime.utcnow(),
            tasks=tasks,
            interrupted=True,
        )

        assert checkpoint.detect_interruption() is False


class TestTaskSerialization:
    """Test Task serialization for checkpoint persistence."""

    def test_task_can_be_serialized(self):
        """Test Task attributes can be serialized to dict."""
        task = Task(
            task_id="serialize_test",
            description="Test serialization",
            phase=Phase.QUALITY,
            estimated_minutes=25,
            completed=False,
            status="pending",
            error_message="Test error",
        )

        # Simulate serialization
        task_dict = {
            "id": task.task_id,
            "description": task.description,
            "phase": task.phase.value,
            "estimated_minutes": task.estimated_minutes,
            "completed": task.completed,
            "status": task.status,
            "error_message": task.error_message,
        }

        assert task_dict["id"] == "serialize_test"
        assert task_dict["phase"] == "quality"
        assert task_dict["estimated_minutes"] == 25

    def test_task_can_be_deserialized(self):
        """Test Task can be reconstructed from dict."""
        task_dict = {
            "id": "deserialize_test",
            "description": "Test deserialization",
            "phase": "testing",
            "estimated_minutes": 30,
            "completed": True,
            "status": "completed",
            "error_message": None,
        }

        # Simulate deserialization
        task = Task(
            task_id=task_dict["id"],
            description=task_dict["description"],
            phase=Phase(task_dict["phase"]),
            estimated_minutes=task_dict["estimated_minutes"],
            completed=task_dict["completed"],
            status=task_dict["status"],
            error_message=task_dict.get("error_message"),
        )

        assert task.task_id == "deserialize_test"
        assert task.phase == Phase.TESTING
        assert task.completed is True
