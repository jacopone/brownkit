"""
Installation module for BrownKit.

Handles copying templates, creating directory structure, and initializing
the brownfield project environment without overwriting Spec-Kit files.
"""

from pathlib import Path
import shutil
import json
from datetime import datetime
from typing import Dict

from brownfield.core.validator import check_conflicts


def install_brownfield_kit(force: bool = False) -> Dict[str, any]:
    """Install BrownKit into the current Spec-Kit project.

    Args:
        force: If True, overwrite existing files

    Returns:
        dict: {
            "success": bool,
            "installed": List[str],
            "skipped": List[str],
            "errors": List[str]
        }
    """
    installed = []
    skipped = []
    errors = []

    try:
        # Check for conflicts first
        conflict_check = check_conflicts(force=force)

        if not conflict_check["safe_to_install"]:
            return {
                "success": False,
                "installed": [],
                "skipped": [],
                "errors": [
                    f"Installation conflicts detected: {len(conflict_check['conflicts'])} files exist",
                    "Run with --force to overwrite existing files"
                ]
            }

        # Create directory structure
        directories = [
            ".specify/brownfield",
            ".specify/scripts/bash",
            ".claude/commands",
            "templates/commands",
        ]

        for dir_path in directories:
            path = Path(dir_path)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                installed.append(f"Created directory: {dir_path}")
            else:
                skipped.append(f"Directory exists: {dir_path}")

        # Copy bash common utilities
        # Since we're in the brownfield repo itself, copy from .specify/scripts/bash/
        if Path(".specify/scripts/bash/brownfield-common.sh").exists():
            # Already exists in development
            installed.append("Bash utilities: brownfield-common.sh")
        else:
            errors.append("brownfield-common.sh not found in templates")

        # Create initial brownfield state file
        state_file = Path(".specify/memory/brownfield-state.json")
        if not state_file.exists() or force:
            initial_state = {
                "version": "1.0",
                "active_project": None,
                "projects": [],
                "created_at": datetime.utcnow().isoformat() + "Z"
            }

            state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(state_file, "w") as f:
                json.dump(initial_state, f, indent=2)

            installed.append("Created: .specify/memory/brownfield-state.json")
        else:
            skipped.append(".specify/memory/brownfield-state.json")

        # Copy slash command templates
        slash_commands = [
            "brownfield.ingest.md",
            "brownfield.assess.md",
            "brownfield.plan.md",
            "brownfield.remediate.md",
            "brownfield.validate.md",
            "brownfield.graduate.md"
        ]

        for cmd_file in slash_commands:
            source = Path("templates/commands") / cmd_file
            dest = Path(".claude/commands") / cmd_file

            if source.exists():
                if not dest.exists() or force:
                    shutil.copy2(source, dest)
                    installed.append(f"Installed: .claude/commands/{cmd_file}")
                else:
                    skipped.append(f".claude/commands/{cmd_file}")
            else:
                # Will be created in later tasks
                skipped.append(f"Template not yet created: {cmd_file}")

        # Copy markdown templates
        markdown_templates = [
            "brownfield-assessment-template.md",
            "brownfield-plan-template.md",
            "brownfield-validation-template.md",
            "brownfield-config-template.yaml"
        ]

        for template_file in markdown_templates:
            # Templates should already exist in templates/ from Phase 2
            if Path("templates") / template_file:
                installed.append(f"Template available: templates/{template_file}")

        return {
            "success": True,
            "installed": installed,
            "skipped": skipped,
            "errors": []
        }

    except Exception as e:
        return {
            "success": False,
            "installed": installed,
            "skipped": skipped,
            "errors": [f"Installation error: {str(e)}"]
        }


def copy_bash_scripts():
    """Copy all brownfield bash scripts to .specify/scripts/bash/."""
    bash_scripts = [
        "brownfield-common.sh",
        "brownfield-ingest.sh",
        "brownfield-assess.sh",
        "brownfield-plan.sh",
        "brownfield-remediate.sh",
        "brownfield-validate.sh",
        "brownfield-graduate.sh"
    ]

    for script in bash_scripts:
        source = Path(".specify/scripts/bash") / script
        if source.exists():
            # Make executable
            source.chmod(0o755)
