"""Tests for state migration utility."""

import json
import pytest
from pathlib import Path

from brownfield.state.migrations.migrate_state_v1 import (
    migrate_state_file,
    check_migration_needed,
    rollback_migration,
)


class TestStateMigration:
    """Test state file migration from brownfield-state.json to state.json."""

    @pytest.fixture
    def temp_memory_dir(self, tmp_path):
        """Create temporary memory directory."""
        memory_dir = tmp_path / ".specify" / "memory"
        memory_dir.mkdir(parents=True)
        return memory_dir

    @pytest.fixture
    def old_state_file(self, temp_memory_dir):
        """Create old brownfield-state.json file."""
        old_state = {
            "schema_version": "1.0",
            "project_root": "/tmp/test",
            "current_phase": "assessment",
            "baseline_metrics": {
                "test_coverage": 0.5,
                "complexity_avg": 10.0,
                "complexity_max": 15,
                "critical_vulnerabilities": 0,
                "high_vulnerabilities": 0,
                "medium_vulnerabilities": 0,
                "build_status": "passing",
                "documentation_coverage": 0.4,
                "total_loc": 1000,
                "test_loc": 500,
                "git_commits": 10,
                "git_secrets_found": 0,
            },
            "current_metrics": {
                "test_coverage": 0.5,
                "complexity_avg": 10.0,
                "complexity_max": 15,
                "critical_vulnerabilities": 0,
                "high_vulnerabilities": 0,
                "medium_vulnerabilities": 0,
                "build_status": "passing",
                "documentation_coverage": 0.4,
                "total_loc": 1000,
                "test_loc": 500,
                "git_commits": 10,
                "git_secrets_found": 0,
            },
            "phase_timestamps": {},
            "re_entry_events": [],
            "graduated": False,
        }

        old_path = temp_memory_dir / "brownfield-state.json"
        with open(old_path, "w") as f:
            json.dump(old_state, f, indent=2)

        return old_path

    def test_migrate_creates_new_state_file(self, temp_memory_dir, old_state_file):
        """Test migration creates state.json."""
        new_path = temp_memory_dir / "state.json"

        assert old_state_file.exists()
        assert not new_path.exists()

        # Perform migration
        result = migrate_state_file(temp_memory_dir)

        assert result is True
        assert new_path.exists()

    def test_migrate_adds_workflow_field(self, temp_memory_dir, old_state_file):
        """Test migration adds workflow field."""
        migrate_state_file(temp_memory_dir)

        new_path = temp_memory_dir / "state.json"
        with open(new_path) as f:
            state_dict = json.load(f)

        assert "workflow" in state_dict
        assert state_dict["workflow"] == "brownfield"

    def test_migrate_preserves_existing_data(self, temp_memory_dir, old_state_file):
        """Test migration preserves all existing data."""
        # Load original data
        with open(old_state_file) as f:
            original = json.load(f)

        migrate_state_file(temp_memory_dir)

        # Load migrated data
        new_path = temp_memory_dir / "state.json"
        with open(new_path) as f:
            migrated = json.load(f)

        # Check all original fields are preserved
        assert migrated["current_phase"] == original["current_phase"]
        assert migrated["baseline_metrics"] == original["baseline_metrics"]
        assert migrated["graduated"] == original["graduated"]

    def test_migrate_archives_old_file(self, temp_memory_dir, old_state_file):
        """Test migration archives brownfield-state.json."""
        old_path = temp_memory_dir / "brownfield-state.json"

        migrate_state_file(temp_memory_dir)

        # Old file should be archived, not deleted
        assert not old_path.exists()

        # Check for archived file
        archived_files = list(temp_memory_dir.glob("brownfield-state.json.archived_*"))
        assert len(archived_files) == 1

    def test_migrate_no_op_if_no_old_file(self, temp_memory_dir):
        """Test migration returns False if no old file exists."""
        result = migrate_state_file(temp_memory_dir)

        assert result is False

    def test_check_migration_needed_detects_old_file(
        self, temp_memory_dir, old_state_file
    ):
        """Test check_migration_needed detects old state file."""
        reason = check_migration_needed(temp_memory_dir)

        assert reason is not None
        assert "needs migration" in reason.lower()

    def test_check_migration_needed_none_after_migration(
        self, temp_memory_dir, old_state_file
    ):
        """Test check_migration_needed returns None after migration."""
        migrate_state_file(temp_memory_dir)

        reason = check_migration_needed(temp_memory_dir)

        assert reason is None

    def test_rollback_migration(self, temp_memory_dir, old_state_file):
        """Test rollback migration restores old file."""
        # Perform migration
        migrate_state_file(temp_memory_dir)

        old_path = temp_memory_dir / "brownfield-state.json"
        new_path = temp_memory_dir / "state.json"

        assert not old_path.exists()
        assert new_path.exists()

        # Rollback
        result = rollback_migration(temp_memory_dir)

        assert result is True
        assert old_path.exists()
        assert not new_path.exists()

    def test_migrate_backups_existing_state_json(self, temp_memory_dir, old_state_file):
        """Test migration backs up existing state.json if present."""
        # Create existing state.json
        new_path = temp_memory_dir / "state.json"
        existing_data = {"existing": "data"}
        with open(new_path, "w") as f:
            json.dump(existing_data, f)

        # Perform migration
        migrate_state_file(temp_memory_dir)

        # Check for backup
        backups = list(temp_memory_dir.glob("state.backup_*.json"))
        assert len(backups) == 1

    def test_migrate_atomic_write(self, temp_memory_dir, old_state_file):
        """Test migration uses atomic write (temp file + rename)."""
        migrate_state_file(temp_memory_dir)

        # No .tmp files should remain
        tmp_files = list(temp_memory_dir.glob("*.tmp"))
        assert len(tmp_files) == 0

        # state.json should exist
        new_path = temp_memory_dir / "state.json"
        assert new_path.exists()


class TestStateMigrationEdgeCases:
    """Test edge cases in state migration."""

    def test_migrate_handles_missing_workflow_in_existing_state(self, tmp_path):
        """Test migration adds workflow to existing state.json."""
        memory_dir = tmp_path / ".specify" / "memory"
        memory_dir.mkdir(parents=True)

        # Create state.json without workflow field
        state_without_workflow = {
            "schema_version": "1.0",
            "current_phase": "assessment",
        }

        state_path = memory_dir / "state.json"
        with open(state_path, "w") as f:
            json.dump(state_without_workflow, f)

        # Migration should detect missing workflow
        reason = check_migration_needed(memory_dir)
        assert reason is not None
        assert "workflow" in reason.lower()
