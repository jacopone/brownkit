"""Contract tests for gate public APIs."""

import dataclasses

from brownfield.models.gate import READINESS_GATES, ReadinessGate


def test_readiness_gate_is_importable():
    """ReadinessGate is importable and is a dataclass."""
    assert dataclasses.is_dataclass(ReadinessGate)


def test_readiness_gate_has_evaluate():
    """ReadinessGate exposes an evaluate instance method."""
    assert hasattr(ReadinessGate, "evaluate")
    assert callable(ReadinessGate.evaluate)


def test_readiness_gates_constant_is_list():
    """READINESS_GATES is a non-empty list of ReadinessGate instances."""
    assert isinstance(READINESS_GATES, list)
    assert len(READINESS_GATES) > 0
    for gate in READINESS_GATES:
        assert isinstance(gate, ReadinessGate)
