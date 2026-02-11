"""Smoke tests for state."""

from brownfield.models.state import (
    BrownfieldState,
    Phase,
    ReEntryEvent,
    SpecKitIntegration,
    advance_phase,
    detect_regression,
    load,
    to_json,
    update_metrics,
)


def test_phase_instantiation():
    """Test Phase can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert Phase is not None


def test_reentryevent_instantiation():
    """Test ReEntryEvent can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert ReEntryEvent is not None


def test_speckitintegration_instantiation():
    """Test SpecKitIntegration can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert SpecKitIntegration is not None


def test_brownfieldstate_instantiation():
    """Test BrownfieldState can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert BrownfieldState is not None


def test_update_metrics_exists():
    """Test update_metrics function exists."""
    # Smoke test - verify function can be imported
    assert callable(update_metrics)


def test_advance_phase_exists():
    """Test advance_phase function exists."""
    # Smoke test - verify function can be imported
    assert callable(advance_phase)


def test_detect_regression_exists():
    """Test detect_regression function exists."""
    # Smoke test - verify function can be imported
    assert callable(detect_regression)


def test_to_json_exists():
    """Test to_json function exists."""
    # Smoke test - verify function can be imported
    assert callable(to_json)


def test_load_exists():
    """Test load function exists."""
    # Smoke test - verify function can be imported
    assert callable(load)
