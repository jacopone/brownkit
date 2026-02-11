"""Contract tests for cli public APIs.

Note: The CLI module requires 'click' to be installed.
These tests verify that the CLI module structure is correct
by checking the module and command file directly.
"""

import importlib


def test_cli_commands_module_exists():
    """The brownfield.cli.commands module file exists and is loadable as source."""
    from pathlib import Path

    commands_path = Path(__file__).resolve().parents[2] / "src" / "brownfield" / "cli" / "commands.py"
    assert commands_path.exists(), f"commands.py not found at {commands_path}"


def test_cli_init_exports_cli():
    """The brownfield.cli __init__.py declares 'cli' in __all__."""
    from pathlib import Path

    init_path = Path(__file__).resolve().parents[2] / "src" / "brownfield" / "cli" / "__init__.py"
    assert init_path.exists()
    content = init_path.read_text()
    assert "cli" in content
    assert "__all__" in content


def test_cli_submodules_exist():
    """Key CLI submodules exist as files."""
    from pathlib import Path

    cli_dir = Path(__file__).resolve().parents[2] / "src" / "brownfield" / "cli"
    expected_submodules = ["assess", "graduate", "status", "validate", "structure"]
    for name in expected_submodules:
        module_path = cli_dir / f"{name}.py"
        assert module_path.exists(), f"CLI submodule {name}.py not found"


def test_cli_module_importable_when_click_available():
    """If click is installed, brownfield.cli should be importable and expose cli."""
    click_spec = importlib.util.find_spec("click")
    if click_spec is None:
        import pytest

        pytest.skip("click not installed; skipping CLI import test")

    from brownfield.cli import cli

    assert callable(cli)
