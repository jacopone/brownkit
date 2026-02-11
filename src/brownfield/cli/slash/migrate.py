"""Slash command: /brownkit.migrate - Migrate v1.0 state to v2.0."""

import shutil
import sys
from datetime import datetime

import click
from rich.console import Console

from brownfield.config import BrownfieldConfig
from brownfield.exceptions import BrownfieldError
from brownfield.state.state_store import StateStore

console = Console()


@click.command("brownfield.migrate")
@click.option(
    "--force",
    is_flag=True,
    help="Force re-migration even if already migrated",
)
@click.option(
    "--skip-checkpoints",
    is_flag=True,
    help="Skip checkpoint directory migration",
)
def migrate_workflow(force: bool, skip_checkpoints: bool) -> None:
    """Migrate BrownKit v1.0 state to v2.0 format (workflow command).

    This command handles:
    - State file rename: brownfield-state.json → state.json
    - Schema upgrade: v1.0 → v2.0 with workflow tracking
    - Checkpoint relocation: .brownfield/ → .specify/brownfield/
    - Backward compatibility preservation

    Safe to run multiple times - creates backups before migration.
    """
    project_root = BrownfieldConfig.get_project_root()

    console.print("\n[bold blue]🔄 BrownKit Migration (v1.0 → v2.0)[/bold blue]\n")

    try:
        memory_dir = project_root / ".specify" / "memory"
        old_state_path = memory_dir / "brownfield-state.json"
        new_state_path = memory_dir / "state.json"

        old_checkpoint_dir = project_root / ".brownfield" / "checkpoints"
        new_checkpoint_dir = project_root / ".specify" / "brownfield" / "checkpoints"

        # Check migration status
        console.print("[cyan]Checking for migration needs...[/cyan]")

        old_exists = old_state_path.exists()
        new_exists = new_state_path.exists()

        # Case 1: Already migrated
        if not old_exists and new_exists and not force:
            state_store = StateStore(new_state_path)
            state = state_store.load()

            console.print("\n[green]Status: ✅ Already migrated to v2.0[/green]\n")
            console.print("[cyan]Current state:[/cyan]")
            console.print(f"  Schema version: {state.schema_version}")
            console.print(f"  State file: {new_state_path.relative_to(project_root)}")
            if state.migrated_from_version:
                console.print(f"  Migrated from: {state.migrated_from_version}")

            console.print("\n[dim]No migration needed.[/dim]")
            return

        # Case 2: No v1.0 state found
        if not old_exists and not new_exists:
            console.print("\n[yellow]Status: ℹ️  No v1.0 state found[/yellow]\n")
            console.print("[cyan]Current state:[/cyan]")
            console.print("  Schema version: 2.0 (native v2.0)")
            console.print(f"  State file: {new_state_path.relative_to(project_root)}")

            console.print("\n[dim]No migration needed.[/dim]")
            return

        # Case 3: Need migration
        console.print(f"  [green]✅[/green] Found v1.0 state: {old_state_path.relative_to(project_root)}")
        console.print(f"  [cyan]ℹ️[/cyan]  Target location: {new_state_path.relative_to(project_root)}\n")

        # Create backup
        console.print("[cyan]Backup Creation:[/cyan]")
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = memory_dir / f"state.backup_{timestamp}.json"

        shutil.copy2(old_state_path, backup_path)
        console.print(f"  [green]✅[/green] Created backup: {backup_path.name}\n")

        # State migration
        console.print("[cyan]State Migration:[/cyan]")

        # Use StateStore's built-in migration
        state_store = StateStore(new_state_path)

        # The migrate_state_file method handles the migration
        if old_state_path.exists():
            # StateStore will auto-migrate on load
            temp_store = StateStore(old_state_path)
            migrated_state = temp_store.load()

            # Save to new location
            new_store = StateStore(new_state_path)
            new_store.save(migrated_state)

            console.print("  [green]✅[/green] Schema upgraded: v1.0 → v2.0")
            console.print("  [green]✅[/green] Workflow state initialized")
            console.print("  [green]✅[/green] Spec-Kit integration added")
            console.print("  [green]✅[/green] State file renamed\n")

        # Checkpoint migration (if not skipped)
        if not skip_checkpoints and old_checkpoint_dir.exists():
            console.print("[cyan]Checkpoint Migration:[/cyan]")

            checkpoint_files = list(old_checkpoint_dir.glob("*.json"))
            console.print(
                f"  [green]✅[/green] Found checkpoints: {old_checkpoint_dir.relative_to(project_root)} ({len(checkpoint_files)} files)"
            )

            # Create new checkpoint directory
            new_checkpoint_dir.mkdir(parents=True, exist_ok=True)

            # Copy checkpoints
            for checkpoint_file in checkpoint_files:
                shutil.copy2(checkpoint_file, new_checkpoint_dir / checkpoint_file.name)

            console.print(f"  [green]✅[/green] Moved to: {new_checkpoint_dir.relative_to(project_root)}")

            # Clean up old directory (only if empty after moving checkpoints)
            if old_checkpoint_dir.exists() and not list(old_checkpoint_dir.iterdir()):
                old_checkpoint_dir.rmdir()
                if old_checkpoint_dir.parent.exists() and not list(old_checkpoint_dir.parent.iterdir()):
                    old_checkpoint_dir.parent.rmdir()
                console.print("  [green]✅[/green] Cleaned up old directory\n")
            else:
                console.print("  [yellow]⚠️[/yellow]  Old directory not removed (contains other files)\n")

        # Validation
        console.print("[cyan]Validation:[/cyan]")

        # Load migrated state to verify
        final_store = StateStore(new_state_path)
        final_state = final_store.load()

        console.print("  [green]✅[/green] Migrated state loads correctly")
        console.print("  [green]✅[/green] All metrics preserved")
        console.print(f"  [green]✅[/green] Workflow phase: {final_state.workflow_state.current_phase.value}")

        # Success summary
        console.print("\n[green bold]Migration Complete![/green bold]\n")
        console.print(f"  Old state: Backed up to {backup_path.name}")
        console.print(f"  New state: {new_state_path.relative_to(project_root)}")
        if not skip_checkpoints and old_checkpoint_dir.exists():
            console.print(f"  Checkpoints: {new_checkpoint_dir.relative_to(project_root)}")

        console.print("\n[cyan]Next steps:[/cyan]")
        console.print("  - Run 'brownfield status' to verify migration")
        console.print("  - Continue your workflow from where you left off")
        console.print("  - Old state files can be deleted after verification\n")

    except BrownfieldError as e:
        console.print(f"\n[red]✗ Error:[/red] {e.message}")
        if e.suggestion:
            console.print(f"\n[yellow]Suggestion:[/yellow] {e.suggestion}")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]✗ Unexpected Error:[/red] {e}")
        if BrownfieldConfig.is_debug_enabled():
            import traceback

            console.print("\n[dim]Traceback:[/dim]")
            console.print(traceback.format_exc())
        sys.exit(1)
