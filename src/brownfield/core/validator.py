"""
Validation module for Brownfield-Kit installation.

Checks that Spec-Kit is properly installed and the project environment
is ready for Brownfield-Kit installation.
"""

from pathlib import Path
from typing import Dict


def validate_speckit_installation() -> Dict[str, any]:
    """Validate that Spec-Kit is installed in the current project.

    Returns:
        dict: {
            "valid": bool,
            "errors": List[str],
            "warnings": List[str]
        }
    """
    errors = []
    warnings = []

    # Check .specify/ directory exists
    specify_dir = Path(".specify")
    if not specify_dir.exists():
        errors.append(".specify/ directory not found - Spec-Kit may not be installed")

    # Check .specify/memory/ exists
    memory_dir = specify_dir / "memory"
    if not memory_dir.exists():
        errors.append(".specify/memory/ directory not found")

    # Check constitution.md exists
    constitution_file = memory_dir / "constitution.md"
    if not constitution_file.exists():
        errors.append(".specify/memory/constitution.md not found")

    # Check if git repository
    if not Path(".git").exists():
        warnings.append("Not a git repository - version control recommended")

    # Check if .claude/commands/ exists (for slash commands)
    claude_commands_dir = Path(".claude/commands")
    if not claude_commands_dir.exists():
        warnings.append(".claude/commands/ not found - slash commands may not work")

    # Check if .specify/scripts/bash/ exists
    scripts_dir = specify_dir / "scripts" / "bash"
    if not scripts_dir.exists():
        warnings.append(".specify/scripts/bash/ not found - will be created")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def check_conflicts(force: bool = False) -> Dict[str, any]:
    """Check for potential file conflicts before installation.

    Args:
        force: If True, report conflicts but don't block installation

    Returns:
        dict: {
            "conflicts": List[str],
            "safe_to_install": bool
        }
    """
    conflicts = []

    # Check if brownfield-specific files already exist
    brownfield_files = [
        ".specify/scripts/bash/brownfield-common.sh",
        ".specify/scripts/bash/brownfield-ingest.sh",
        ".specify/scripts/bash/brownfield-assess.sh",
        ".specify/scripts/bash/brownfield-plan.sh",
        ".specify/memory/brownfield-state.json",
    ]

    for file_path in brownfield_files:
        if Path(file_path).exists():
            conflicts.append(file_path)

    # Check slash commands
    slash_commands = [
        ".claude/commands/brownfield.ingest.md",
        ".claude/commands/brownfield.assess.md",
        ".claude/commands/brownfield.plan.md",
        ".claude/commands/brownfield.remediate.md",
        ".claude/commands/brownfield.validate.md",
        ".claude/commands/brownfield.graduate.md",
    ]

    for cmd_path in slash_commands:
        if Path(cmd_path).exists():
            conflicts.append(cmd_path)

    return {
        "conflicts": conflicts,
        "safe_to_install": len(conflicts) == 0 or force
    }
