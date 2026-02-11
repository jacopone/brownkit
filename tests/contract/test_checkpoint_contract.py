"""Contract tests for checkpoint public APIs."""

import dataclasses

from brownfield.models.checkpoint import PhaseCheckpoint, Task


def test_phase_checkpoint_is_importable():
    """PhaseCheckpoint is importable and is a dataclass."""
    assert dataclasses.is_dataclass(PhaseCheckpoint)


def test_task_is_importable():
    """Task is importable and is a dataclass."""
    assert dataclasses.is_dataclass(Task)


def test_phase_checkpoint_has_tasks_property():
    """PhaseCheckpoint exposes a tasks property."""
    assert isinstance(
        getattr(PhaseCheckpoint, "tasks", None),
        property,
    )


def test_phase_checkpoint_has_progress_percentage_property():
    """PhaseCheckpoint exposes a progress_percentage property."""
    assert isinstance(
        getattr(PhaseCheckpoint, "progress_percentage", None),
        property,
    )


def test_phase_checkpoint_has_mark_task_complete():
    """PhaseCheckpoint exposes a mark_task_complete method."""
    assert hasattr(PhaseCheckpoint, "mark_task_complete")
    assert callable(PhaseCheckpoint.mark_task_complete)


def test_phase_checkpoint_has_detect_interruption():
    """PhaseCheckpoint exposes a detect_interruption method."""
    assert hasattr(PhaseCheckpoint, "detect_interruption")
    assert callable(PhaseCheckpoint.detect_interruption)
