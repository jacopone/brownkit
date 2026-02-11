"""Contract tests for state public APIs."""

import dataclasses

from brownfield.models.state import (
    BrownfieldState,
    Metrics,
    Phase,
    ReEntryEvent,
    SpecKitIntegration,
)


def test_brownfield_state_is_importable():
    """BrownfieldState is importable and is a dataclass."""
    assert dataclasses.is_dataclass(BrownfieldState)


def test_phase_is_enum():
    """Phase is an importable enum with expected members."""
    assert hasattr(Phase, "ASSESSMENT")
    assert hasattr(Phase, "STRUCTURE")
    assert hasattr(Phase, "TESTING")
    assert hasattr(Phase, "QUALITY")
    assert hasattr(Phase, "VALIDATION")
    assert hasattr(Phase, "GRADUATED")


def test_brownfield_state_has_update_metrics():
    """BrownfieldState exposes an update_metrics method."""
    assert hasattr(BrownfieldState, "update_metrics")
    assert callable(BrownfieldState.update_metrics)


def test_brownfield_state_has_advance_phase():
    """BrownfieldState exposes an advance_phase method."""
    assert hasattr(BrownfieldState, "advance_phase")
    assert callable(BrownfieldState.advance_phase)


def test_brownfield_state_has_detect_regression():
    """BrownfieldState exposes a detect_regression method."""
    assert hasattr(BrownfieldState, "detect_regression")
    assert callable(BrownfieldState.detect_regression)


def test_brownfield_state_has_to_json():
    """BrownfieldState exposes a to_json method."""
    assert hasattr(BrownfieldState, "to_json")
    assert callable(BrownfieldState.to_json)


def test_brownfield_state_has_load():
    """BrownfieldState exposes a load classmethod."""
    assert hasattr(BrownfieldState, "load")
    assert callable(BrownfieldState.load)


def test_brownfield_state_has_save():
    """BrownfieldState exposes a save method."""
    assert hasattr(BrownfieldState, "save")
    assert callable(BrownfieldState.save)


def test_re_entry_event_is_importable():
    """ReEntryEvent is importable and is a dataclass."""
    assert dataclasses.is_dataclass(ReEntryEvent)


def test_speckit_integration_is_importable():
    """SpecKitIntegration is importable and is a dataclass."""
    assert dataclasses.is_dataclass(SpecKitIntegration)


def test_metrics_re_exported():
    """Metrics is re-exported from brownfield.models.state."""
    assert dataclasses.is_dataclass(Metrics)
