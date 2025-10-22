"""Main CLI entry point."""

import click

from brownfield.cli.assess import assess
from brownfield.cli.graduate import graduate
from brownfield.cli.quality import quality
from brownfield.cli.resume import resume
from brownfield.cli.slash.assess import assess_workflow
from brownfield.cli.slash.graduate import graduate_workflow
from brownfield.cli.slash.plan import plan_workflow
from brownfield.cli.slash.remediate import remediate_workflow
from brownfield.cli.slash.validate import validate_workflow
from brownfield.cli.status import status
from brownfield.cli.structure import structure
from brownfield.cli.testing import testing
from brownfield.cli.validate import validate


@click.group()
@click.version_option(version="0.1.0", prog_name="brownkit")
def brownfield():
    """BrownKit: AI-driven workflow for transitioning brownfield codebases to Speckit-ready state."""
    pass


@brownfield.command()
@click.option(
    "--shell",
    type=click.Choice(["bash", "zsh", "fish"], case_sensitive=False),
    required=True,
    help="Shell type for completion script",
)
def install_completion(shell: str):
    """Install shell completion for brownfield command."""
    import sys

    shell_lower = shell.lower()

    click.echo(f"Installing {shell_lower} completion for brownfield...")

    try:
        # Generate completion script using click's built-in support
        if shell_lower == "bash":
            install_cmd = "eval \"$(_BROWNFIELD_COMPLETE=bash_source brownfield)\""
            config_file = "~/.bashrc"
        elif shell_lower == "zsh":
            install_cmd = "eval \"$(_BROWNFIELD_COMPLETE=zsh_source brownfield)\""
            config_file = "~/.zshrc"
        elif shell_lower == "fish":
            install_cmd = "eval (env _BROWNFIELD_COMPLETE=fish_source brownfield)"
            config_file = "~/.config/fish/config.fish"
        else:
            click.echo(f"Unsupported shell: {shell}", err=True)
            sys.exit(1)

        click.echo("\nAdd the following line to your shell configuration file:")
        click.echo(f"  File: {config_file}")
        click.echo(f"  Line: {install_cmd}")
        click.echo("\nThen reload your shell or run:")
        click.echo(f"  source {config_file}")

        sys.exit(0)

    except Exception as e:
        click.echo(f"Error installing completion: {e}", err=True)
        sys.exit(1)


# Register granular commands (phase-specific)
brownfield.add_command(assess)
brownfield.add_command(structure)
brownfield.add_command(testing)
brownfield.add_command(quality)
brownfield.add_command(validate)
brownfield.add_command(graduate)
brownfield.add_command(resume)
brownfield.add_command(status)

# Register workflow commands (slash commands - orchestrator-based)
brownfield.add_command(assess_workflow)
brownfield.add_command(plan_workflow)
brownfield.add_command(remediate_workflow)
brownfield.add_command(validate_workflow)
brownfield.add_command(graduate_workflow)


if __name__ == "__main__":
    brownfield()
