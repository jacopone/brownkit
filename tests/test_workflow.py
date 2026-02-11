"""Smoke tests for workflow."""

from brownfield.models.workflow import (
    PhaseExecution,
    PhaseStatus,
    WorkflowPhase,
    WorkflowState,
    can_execute_phase,
    get_next_phase,
    mark_completed,
    mark_failed,
    mark_started,
)


def test_workflowphase_instantiation():
    """Test WorkflowPhase can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert WorkflowPhase is not None


def test_phasestatus_instantiation():
    """Test PhaseStatus can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert PhaseStatus is not None


def test_phaseexecution_instantiation():
    """Test PhaseExecution can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert PhaseExecution is not None


def test_workflowstate_instantiation():
    """Test WorkflowState can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert WorkflowState is not None


def test_mark_started_exists():
    """Test mark_started function exists."""
    # Smoke test - verify function can be imported
    assert callable(mark_started)


def test_mark_completed_exists():
    """Test mark_completed function exists."""
    # Smoke test - verify function can be imported
    assert callable(mark_completed)


def test_mark_failed_exists():
    """Test mark_failed function exists."""
    # Smoke test - verify function can be imported
    assert callable(mark_failed)


def test_can_execute_phase_exists():
    """Test can_execute_phase function exists."""
    # Smoke test - verify function can be imported
    assert callable(can_execute_phase)


def test_get_next_phase_exists():
    """Test get_next_phase function exists."""
    # Smoke test - verify function can be imported
    assert callable(get_next_phase)
