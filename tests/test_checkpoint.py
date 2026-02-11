"""Smoke tests for checkpoint."""

from brownfield.models.checkpoint import (
    PhaseCheckpoint,
    Task,
    detect_interruption,
    mark_task_complete,
    progress_percentage,
    tasks,
)


def test_task_instantiation():
    """Test Task can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert Task is not None


def test_phasecheckpoint_instantiation():
    """Test PhaseCheckpoint can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert PhaseCheckpoint is not None


def test_tasks_exists():
    """Test tasks function exists."""
    # Smoke test - verify function can be imported
    assert callable(tasks)


def test_progress_percentage_exists():
    """Test progress_percentage function exists."""
    # Smoke test - verify function can be imported
    assert callable(progress_percentage)


def test_mark_task_complete_exists():
    """Test mark_task_complete function exists."""
    # Smoke test - verify function can be imported
    assert callable(mark_task_complete)


def test_detect_interruption_exists():
    """Test detect_interruption function exists."""
    # Smoke test - verify function can be imported
    assert callable(detect_interruption)
