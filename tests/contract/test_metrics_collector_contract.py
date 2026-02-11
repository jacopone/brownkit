"""Contract tests for metrics_collector public APIs."""

from brownfield.assessment.metrics_collector import MetricsCollector


def test_metrics_collector_is_importable():
    """MetricsCollector is importable and is a class."""
    assert isinstance(MetricsCollector, type)


def test_metrics_collector_has_collect_method():
    """MetricsCollector exposes a collect instance method."""
    assert hasattr(MetricsCollector, "collect")
    assert callable(MetricsCollector.collect)


def test_metrics_collector_instantiable():
    """MetricsCollector can be instantiated without arguments."""
    collector = MetricsCollector()
    assert collector is not None
