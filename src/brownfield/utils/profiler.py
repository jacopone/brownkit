"""Performance profiling utilities.

Provides tools for measuring and optimizing command performance.
"""

import time
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Optional

from rich.console import Console

from brownfield.config import BrownfieldConfig

console = Console()


class PerformanceTracker:
    """Track performance metrics for operations."""

    def __init__(self):
        """Initialize performance tracker."""
        self.timings: dict[str, list[float]] = {}
        self.enabled = BrownfieldConfig.is_debug_enabled()

    def record(self, operation: str, duration: float) -> None:
        """Record timing for an operation.

        Args:
            operation: Operation name
            duration: Duration in seconds
        """
        if not self.enabled:
            return

        if operation not in self.timings:
            self.timings[operation] = []
        self.timings[operation].append(duration)

    def get_stats(self, operation: str) -> dict[str, float]:
        """Get statistics for an operation.

        Args:
            operation: Operation name

        Returns:
            Dictionary with min, max, avg, total times
        """
        if operation not in self.timings or not self.timings[operation]:
            return {"min": 0.0, "max": 0.0, "avg": 0.0, "total": 0.0, "count": 0}

        timings = self.timings[operation]
        return {
            "min": min(timings),
            "max": max(timings),
            "avg": sum(timings) / len(timings),
            "total": sum(timings),
            "count": len(timings),
        }

    def print_summary(self) -> None:
        """Print performance summary to console."""
        if not self.enabled or not self.timings:
            return

        console.print("\n[bold]Performance Summary:[/bold]")
        console.print("=" * 60)

        for operation, timings in sorted(self.timings.items()):
            stats = self.get_stats(operation)
            console.print(f"\n[cyan]{operation}[/cyan]:")
            console.print(f"  Count: {stats['count']}")
            console.print(f"  Total: {stats['total']:.2f}s")
            console.print(f"  Avg:   {stats['avg']:.2f}s")
            console.print(f"  Min:   {stats['min']:.2f}s")
            console.print(f"  Max:   {stats['max']:.2f}s")

        console.print("\n" + "=" * 60)

    def clear(self) -> None:
        """Clear all recorded timings."""
        self.timings.clear()


# Global performance tracker
_perf_tracker = PerformanceTracker()


@contextmanager
def measure_time(operation: str, print_result: bool = False):
    """Context manager to measure execution time.

    Args:
        operation: Operation name for tracking
        print_result: Whether to print timing immediately

    Usage:
        with measure_time("expensive_operation"):
            # ... code to measure ...
            pass
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - start
        _perf_tracker.record(operation, duration)

        if print_result or BrownfieldConfig.is_debug_enabled():
            console.print(f"[dim]{operation}: {duration:.2f}s[/dim]")


def timed(operation: Optional[str] = None):
    """Decorator to measure function execution time.

    Args:
        operation: Optional operation name (defaults to function name)

    Usage:
        @timed()
        def expensive_function():
            # ... code ...
            pass

        @timed("custom_operation_name")
        def another_function():
            # ... code ...
            pass
    """

    def decorator(func: Callable) -> Callable:
        op_name = operation or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            with measure_time(op_name):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def get_performance_stats() -> dict[str, dict[str, float]]:
    """Get all performance statistics.

    Returns:
        Dictionary mapping operation names to their statistics
    """
    return {op: _perf_tracker.get_stats(op) for op in _perf_tracker.timings.keys()}


def print_performance_summary() -> None:
    """Print performance summary to console."""
    _perf_tracker.print_summary()


def clear_performance_data() -> None:
    """Clear all performance tracking data."""
    _perf_tracker.clear()


@contextmanager
def batch_operations(min_batch_size: int = 10):
    """Context manager for batching operations.

    Useful for collecting items to process in bulk instead of one-by-one.

    Args:
        min_batch_size: Minimum batch size before processing

    Usage:
        with batch_operations() as batch:
            for item in items:
                batch.append(item)
                if len(batch) >= min_batch_size:
                    process_batch(batch)
                    batch.clear()
            # Process remaining items
            if batch:
                process_batch(batch)
    """
    batch = []
    try:
        yield batch
    finally:
        pass  # Batch processing handled in user code


class ProgressEstimator:
    """Estimate remaining time for long operations."""

    def __init__(self, total_items: int):
        """Initialize progress estimator.

        Args:
            total_items: Total number of items to process
        """
        self.total_items = total_items
        self.completed_items = 0
        self.start_time = time.perf_counter()

    def update(self, completed: int = 1) -> None:
        """Update progress.

        Args:
            completed: Number of items completed since last update
        """
        self.completed_items += completed

    def estimate_remaining_seconds(self) -> float:
        """Estimate remaining time in seconds.

        Returns:
            Estimated seconds remaining (or 0 if no progress yet)
        """
        if self.completed_items == 0:
            return 0.0

        elapsed = time.perf_counter() - self.start_time
        rate = self.completed_items / elapsed  # items per second
        remaining_items = self.total_items - self.completed_items

        return remaining_items / rate if rate > 0 else 0.0

    def get_progress_percentage(self) -> float:
        """Get progress percentage.

        Returns:
            Progress as percentage (0.0 to 100.0)
        """
        return (self.completed_items / self.total_items * 100.0) if self.total_items > 0 else 0.0

    def format_eta(self) -> str:
        """Format estimated time to completion.

        Returns:
            Human-readable ETA string
        """
        remaining = self.estimate_remaining_seconds()

        if remaining < 60:
            return f"{remaining:.0f}s"
        elif remaining < 3600:
            minutes = remaining / 60
            return f"{minutes:.1f}m"
        else:
            hours = remaining / 3600
            return f"{hours:.1f}h"
