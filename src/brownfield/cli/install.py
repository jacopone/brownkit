"""Install command for setting up BrownKit in current project."""

import shutil
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.command("install")
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing slash commands",
)
def install(force: bool):
    """
    Install BrownKit slash commands in current project.

    Creates .claude/commands/ directory and copies all BrownKit slash commands,
    making them available in Claude Code sessions for this project.

    This is the brownfield equivalent of 'specify init' - designed for existing
    projects that need to transition to spec-driven development.
    """
    # Get current directory from environment or cwd
    import os
    current_dir = Path(os.environ.get("PWD", Path.cwd()))

    console.print("\n[bold cyan]🏗️  Installing BrownKit in current project[/bold cyan]\n")
    console.print(f"[dim]Target directory: {current_dir}[/dim]\n")

    # Check if this looks like a valid project (has git or some source files)
    has_git = (current_dir / ".git").exists()
    has_source = any((current_dir / ext).exists() for ext in ["src", "lib", "*.py", "*.js", "*.rs", "*.go"])

    if not has_git and not has_source:
        console.print("[yellow]⚠ Warning:[/yellow] Current directory doesn't look like a project.")
        console.print("  (No .git directory or source files found)")
        if not click.confirm("Continue anyway?", default=False):
            console.print("\n[red]Installation cancelled.[/red]")
            sys.exit(1)

    # Find brownkit installation directory
    # The slash commands are in the package's .claude/commands/ directory
    brownkit_module = Path(__file__).parent.parent.parent.parent
    source_commands = brownkit_module / ".claude" / "commands"

    if not source_commands.exists():
        console.print(f"[red]✗ Error:[/red] BrownKit commands not found at {source_commands}")
        console.print("\n  Expected location: <brownkit-installation>/.claude/commands/")
        sys.exit(1)

    # Prevent installing into brownkit's own directory
    if current_dir.resolve() == brownkit_module.resolve():
        console.print("[red]✗ Error:[/red] Cannot install BrownKit into its own directory")
        console.print(f"\n  Current directory: {current_dir}")
        console.print(f"  BrownKit directory: {brownkit_module}")
        console.print("\n  Navigate to your project directory first, then run 'brownfield install'")
        sys.exit(1)

    # Create target directory
    target_dir = current_dir / ".claude" / "commands"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy brownkit slash commands
    brownkit_commands = list(source_commands.glob("brownkit.*.md"))

    if not brownkit_commands:
        console.print(f"[red]✗ Error:[/red] No brownkit commands found in {source_commands}")
        sys.exit(1)

    installed = []
    skipped = []

    for cmd_file in brownkit_commands:
        target_file = target_dir / cmd_file.name

        if target_file.exists() and not force:
            skipped.append(cmd_file.name)
        else:
            shutil.copy2(cmd_file, target_file)
            installed.append(cmd_file.name)

    # Report results
    if installed:
        console.print(f"[green]✓[/green] Installed {len(installed)} BrownKit slash commands:\n")
        for cmd in sorted(installed):
            cmd_name = cmd.replace(".md", "").replace("brownkit.", "/brownkit.")
            console.print(f"  • {cmd_name}")

    if skipped:
        console.print(f"\n[yellow]⚠[/yellow] Skipped {len(skipped)} existing commands (use --force to overwrite):\n")
        for cmd in sorted(skipped):
            cmd_name = cmd.replace(".md", "").replace("brownkit.", "/brownkit.")
            console.print(f"  • {cmd_name}")

    # Show next steps
    console.print()
    console.print(Panel(
        "[bold]Next Steps:[/bold]\n\n"
        "1. Start a new Claude Code session in this project\n"
        "2. Type [cyan]/brownkit.[/cyan] to see available commands\n"
        "3. Run [cyan]/brownkit.assess[/cyan] to begin brownfield transformation\n\n"
        "[dim]BrownKit Workflow:[/dim]\n"
        "  [cyan]/brownkit.assess[/cyan]     → Analyze codebase\n"
        "  [cyan]/brownkit.plan[/cyan]       → Generate remediation plan\n"
        "  [cyan]/brownkit.remediate[/cyan]  → Execute improvements\n"
        "  [cyan]/brownkit.validate[/cyan]   → Check readiness gates\n"
        "  [cyan]/brownkit.graduate[/cyan]   → Generate Spec-Kit constitution\n\n"
        "[green]Installation complete![/green] BrownKit is ready to use.",
        title="🎉 Success",
        border_style="green",
    ))

    console.print()
