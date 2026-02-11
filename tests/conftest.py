"""Pytest configuration."""

import pytest


@pytest.fixture
def project_root():
    """Return project root directory."""
    from pathlib import Path

    return Path(__file__).parent.parent
