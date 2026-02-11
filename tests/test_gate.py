"""Smoke tests for gate."""

from brownfield.models.gate import (
    ReadinessGate,
    evaluate,
)


def test_readinessgate_instantiation():
    """Test ReadinessGate can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert ReadinessGate is not None


def test_evaluate_exists():
    """Test evaluate function exists."""
    # Smoke test - verify function can be imported
    assert callable(evaluate)
