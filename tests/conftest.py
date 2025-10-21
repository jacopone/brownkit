"""Pytest configuration and shared fixtures.

This file provides common fixtures and configuration for all tests.
"""

import os
import sys
from pathlib import Path

import pytest


# Add src directory to Python path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    """Reset environment variables before each test."""
    # Clear brownfield environment variables
    env_vars = [
        "BROWNFIELD_PROJECT_ROOT",
        "BROWNFIELD_STATE_DIR",
        "BROWNFIELD_REPORTS_DIR",
        "BROWNFIELD_TEMPLATES_DIR",
        "BROWNFIELD_DEBUG",
        "BROWNFIELD_ANALYSIS_MODE",
        "BROWNFIELD_FORCE_LANGUAGE",
    ]

    for var in env_vars:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory with git repo."""
    project = tmp_path / "test_project"
    project.mkdir()

    # Initialize git repo
    git_dir = project / ".git"
    git_dir.mkdir()

    return project


@pytest.fixture
def mock_git_repo(tmp_path):
    """Create a mock git repository structure."""
    repo = tmp_path / "mock_repo"
    repo.mkdir()

    # Create .git directory
    (repo / ".git").mkdir()
    (repo / ".git" / "config").write_text("[core]\n\trepositoryformatversion = 0\n")

    return repo


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "contract: mark test as a contract test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_fixture: mark test as requiring fixture projects"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test items during collection.

    Automatically marks tests based on their location:
    - tests/unit/* → unit marker
    - tests/contract/* → contract marker
    - tests/integration/* → integration marker
    """
    for item in items:
        # Get test file path relative to tests directory
        test_path = Path(item.fspath).relative_to(Path(__file__).parent)

        # Auto-mark based on directory
        if test_path.parts[0] == "unit":
            item.add_marker(pytest.mark.unit)
        elif test_path.parts[0] == "contract":
            item.add_marker(pytest.mark.contract)
        elif test_path.parts[0] == "integration":
            item.add_marker(pytest.mark.integration)
            # Integration tests are typically slower
            item.add_marker(pytest.mark.slow)
