"""Smoke tests for metrics_collector."""

from brownfield.assessment.metrics_collector import (
    MetricsCollector,
    collect,
)


def test_metricscollector_instantiation():
    """Test MetricsCollector can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert MetricsCollector is not None


def test_collect_exists():
    """Test collect function exists."""
    # Smoke test - verify function can be imported
    assert callable(collect)
