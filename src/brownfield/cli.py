"""
BrownKit CLI - Main command-line interface.

This module provides the `brownfield init` command for installing
BrownKit into existing Spec-Kit projects.
"""

import click
import sys

from brownfield.core.validator import validate_speckit_installation
from brownfield.core.installer import install_brownfield_kit


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """BrownKit: Spec-Kit plugin for legacy code remediation.

    Install BrownKit into your Spec-Kit project to add quality
    assessment and remediation workflows before AI-driven feature development.
    """
    pass


@cli.command("init")
@click.option(
    "--force",
    is_flag=True,
    help="Force installation even if conflicts detected"
)
def init(force: bool):
    """Initialize BrownKit in the current Spec-Kit project.

    This command installs BrownKit slash commands, templates, and
    bash scripts into your existing Spec-Kit project structure without
    overwriting any Spec-Kit files.

    \b
    Directory structure created:
    - .specify/brownfield/       # Brownfield project storage
    - .specify/scripts/bash/     # Bash utility scripts
    - .claude/commands/          # Slash commands for Claude
    - templates/                 # Markdown templates

    Requirements:
    - Spec-Kit must be installed (.specify/ directory exists)
    - Project must be in a git repository
    """
    click.echo("=== BrownKit Installation ===\n")

    # Validate Spec-Kit installation
    validation_result = validate_speckit_installation()

    if not validation_result["valid"]:
        click.echo(click.style("✗ Validation Failed", fg="red", bold=True))
        for error in validation_result["errors"]:
            click.echo(f"  - {error}")

        if not force:
            click.echo("\nRun with --force to bypass validation checks.")
            sys.exit(1)
        else:
            click.echo(click.style("\n⚠ Proceeding with --force", fg="yellow"))

    # Show validation warnings (non-blocking)
    if validation_result.get("warnings"):
        click.echo(click.style("⚠ Warnings:", fg="yellow"))
        for warning in validation_result["warnings"]:
            click.echo(f"  - {warning}")
        click.echo()

    # Perform installation
    click.echo("Installing BrownKit components...")

    try:
        install_result = install_brownfield_kit(force=force)

        if install_result["success"]:
            click.echo(click.style("\n✓ Installation Complete!", fg="green", bold=True))

            # Show what was installed
            click.echo("\nInstalled components:")
            for component in install_result["installed"]:
                click.echo(f"  ✓ {component}")

            # Show any skipped components
            if install_result.get("skipped"):
                click.echo("\nSkipped (already exists):")
                for component in install_result["skipped"]:
                    click.echo(f"  - {component}")

            # Show next steps
            click.echo("\n" + "=" * 50)
            click.echo("Next steps:")
            click.echo("  1. Run /brownfield.ingest to analyze your codebase")
            click.echo("  2. Run /brownfield.assess to identify technical debt")
            click.echo("  3. Run /brownfield.plan to generate remediation plan")
            click.echo("\nFor help: brownfield --help")

        else:
            click.echo(click.style("\n✗ Installation Failed", fg="red", bold=True))
            for error in install_result["errors"]:
                click.echo(f"  - {error}")
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f"\n✗ Installation Error: {e}", fg="red", bold=True))
        sys.exit(1)


if __name__ == "__main__":
    cli()
