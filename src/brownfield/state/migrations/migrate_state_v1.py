"""Migration utility for brownfield-state.json → state.json.

This migration:
1. Renames brownfield-state.json to state.json
2. Adds 'workflow' field with value 'brownfield'
3. Archives old state file with timestamp
"""

import json
import shutil
from datetime import datetime
from pathlib import Path


def migrate_state_file(memory_dir: Path) -> bool:
    """Migrate old brownfield-state.json to Speckit-compatible state.json.

    Args:
        memory_dir: Path to .specify/memory directory

    Returns:
        True if migration was performed, False if no migration needed
    """
    old_path = memory_dir / "brownfield-state.json"
    new_path = memory_dir / "state.json"

    # Check if migration is needed
    if not old_path.exists():
        return False  # Nothing to migrate

    if new_path.exists():
        # Backup existing state.json before migration
        backup_path = new_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        shutil.copy(new_path, backup_path)

    # Load old state
    with open(old_path, encoding="utf-8") as f:
        state_dict = json.load(f)

    # Add workflow field if not present
    if "workflow" not in state_dict:
        state_dict["workflow"] = "brownfield"

    # Ensure schema_version exists
    if "schema_version" not in state_dict:
        state_dict["schema_version"] = "1.0"

    # Write to new location atomically
    temp_path = new_path.with_suffix(".tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(state_dict, f, indent=2)

    temp_path.rename(new_path)

    # Archive old file (don't delete, keep for rollback)
    archive_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = memory_dir / f"brownfield-state.json.archived_{archive_timestamp}"
    shutil.move(old_path, archive_path)

    return True


def check_migration_needed(memory_dir: Path) -> str | None:
    """Check if migration is needed and return reason.

    Args:
        memory_dir: Path to .specify/memory directory

    Returns:
        Reason string if migration needed, None if not needed
    """
    old_path = memory_dir / "brownfield-state.json"
    new_path = memory_dir / "state.json"

    if old_path.exists() and not new_path.exists():
        return "Old state file exists, needs migration to state.json"

    if old_path.exists() and new_path.exists():
        return "Both old and new state files exist, migration incomplete"

    # Check if new state has workflow field
    if new_path.exists():
        try:
            with open(new_path, encoding="utf-8") as f:
                state_dict = json.load(f)

            if "workflow" not in state_dict:
                return "state.json missing workflow field"
        except (OSError, json.JSONDecodeError):
            pass

    return None


def rollback_migration(memory_dir: Path) -> bool:
    """Rollback migration by restoring archived state file.

    Args:
        memory_dir: Path to .specify/memory directory

    Returns:
        True if rollback successful, False if no archive found
    """
    import glob

    # Find most recent archive
    archives = sorted(glob.glob(str(memory_dir / "brownfield-state.json.archived_*")))

    if not archives:
        return False

    most_recent_archive = Path(archives[-1])
    old_path = memory_dir / "brownfield-state.json"

    # Restore archive
    shutil.copy(most_recent_archive, old_path)

    # Remove state.json (created during migration)
    new_path = memory_dir / "state.json"
    if new_path.exists():
        new_path.unlink()

    return True
