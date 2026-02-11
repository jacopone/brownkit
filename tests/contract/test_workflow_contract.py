"""Contract tests for workflow public APIs."""

import dataclasses

from brownfield.models.workflow import (
    PHASE_PREREQUISITES,
    PHASE_TO_COMMAND,
    PhaseExecution,
    PhaseStatus,
    WorkflowPhase,
    WorkflowState,
)


def test_workflow_state_is_importable():
    """WorkflowState is importable and is a dataclass."""
    assert dataclasses.is_dataclass(WorkflowState)


def test_workflow_phase_is_enum():
    """WorkflowPhase is an importable enum with expected members."""
    assert hasattr(WorkflowPhase, "NOT_STARTED")
    assert hasattr(WorkflowPhase, "ASSESSMENT")
    assert hasattr(WorkflowPhase, "PLANNING")
    assert hasattr(WorkflowPhase, "REMEDIATION")
    assert hasattr(WorkflowPhase, "VALIDATION")
    assert hasattr(WorkflowPhase, "GRADUATION")
    assert hasattr(WorkflowPhase, "SPEC_KIT_READY")


def test_phase_status_is_enum():
    """PhaseStatus is an importable enum with expected members."""
    assert hasattr(PhaseStatus, "NOT_STARTED")
    assert hasattr(PhaseStatus, "IN_PROGRESS")
    assert hasattr(PhaseStatus, "COMPLETED")
    assert hasattr(PhaseStatus, "FAILED")


def test_phase_execution_is_importable():
    """PhaseExecution is importable and is a dataclass."""
    assert dataclasses.is_dataclass(PhaseExecution)


def test_phase_execution_has_mark_started():
    """PhaseExecution exposes a mark_started method."""
    assert hasattr(PhaseExecution, "mark_started")
    assert callable(PhaseExecution.mark_started)


def test_phase_execution_has_mark_completed():
    """PhaseExecution exposes a mark_completed method."""
    assert hasattr(PhaseExecution, "mark_completed")
    assert callable(PhaseExecution.mark_completed)


def test_phase_execution_has_mark_failed():
    """PhaseExecution exposes a mark_failed method."""
    assert hasattr(PhaseExecution, "mark_failed")
    assert callable(PhaseExecution.mark_failed)


def test_workflow_state_has_can_execute_phase():
    """WorkflowState exposes a can_execute_phase method."""
    assert hasattr(WorkflowState, "can_execute_phase")
    assert callable(WorkflowState.can_execute_phase)


def test_workflow_state_has_get_next_phase():
    """WorkflowState exposes a get_next_phase method."""
    assert hasattr(WorkflowState, "get_next_phase")
    assert callable(WorkflowState.get_next_phase)


def test_workflow_state_has_get_workflow_status_display():
    """WorkflowState exposes a get_workflow_status_display method."""
    assert hasattr(WorkflowState, "get_workflow_status_display")
    assert callable(WorkflowState.get_workflow_status_display)


def test_workflow_state_has_is_phase_completed():
    """WorkflowState exposes an is_phase_completed method."""
    assert hasattr(WorkflowState, "is_phase_completed")
    assert callable(WorkflowState.is_phase_completed)


def test_phase_prerequisites_constant():
    """PHASE_PREREQUISITES is an importable dict."""
    assert isinstance(PHASE_PREREQUISITES, dict)
    assert len(PHASE_PREREQUISITES) > 0


def test_phase_to_command_constant():
    """PHASE_TO_COMMAND is an importable dict."""
    assert isinstance(PHASE_TO_COMMAND, dict)
    assert len(PHASE_TO_COMMAND) > 0
