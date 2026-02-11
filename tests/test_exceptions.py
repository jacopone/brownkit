"""Smoke tests for exceptions."""

from brownfield.exceptions import (
    BrownfieldError,
    InvalidStateError,
    PhaseError,
    StateError,
    StateNotFoundError,
)


def test_brownfielderror_instantiation():
    """Test BrownfieldError can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert BrownfieldError is not None


def test_stateerror_instantiation():
    """Test StateError can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert StateError is not None


def test_statenotfounderror_instantiation():
    """Test StateNotFoundError can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert StateNotFoundError is not None


def test_invalidstateerror_instantiation():
    """Test InvalidStateError can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert InvalidStateError is not None


def test_phaseerror_instantiation():
    """Test PhaseError can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert PhaseError is not None
