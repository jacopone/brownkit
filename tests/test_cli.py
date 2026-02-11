"""Smoke tests for cli."""

from brownfield.cli import (
    cli,
    init,
)


def test_cli_exists():
    """Test cli function exists."""
    # Smoke test - verify function can be imported
    assert callable(cli)


def test_init_exists():
    """Test init function exists."""
    # Smoke test - verify function can be imported
    assert callable(init)
