"""Integration tests for complete migration workflow (v1.0 → v2.0).

Tests full migration including state schema upgrade and checkpoint relocation.
"""

import json
import shutil
from datetime import datetime

import pytest

from brownfield.models.state import Phase
from brownfield.orchestrator.checkpoint_manager import CheckpointManager
from brownfield.state.migrations.migrate_state_v1 import (
    check_migration_needed,
    migrate_state_file,
    rollback_migration,
)
from brownfield.state.state_store import StateStore


class TestFullMigrationWorkflow:
    """Test complete v1.0 → v2.0 migration workflow."""

    @pytest.fixture
    def v1_project(self, tmp_path):
        """Create project with v1.0 state and old checkpoint structure."""
        project_root = tmp_path / "v1_project"
        project_root.mkdir()

        # Create old directory structure
        old_memory_dir = project_root / ".specify" / "memory"
        old_memory_dir.mkdir(parents=True)

        old_checkpoint_dir = project_root / ".brownfield" / "checkpoints"
        old_checkpoint_dir.mkdir(parents=True)

        # Create v1.0 state file (brownfield-state.json)
        old_state = {
            "schema_version": "1.0",
            "project_root": str(project_root),
            "current_phase": "testing",
            "baseline_metrics": {
                "test_coverage": 0.5,
                "complexity_avg": 10.0,
                "complexity_max": 15,
                "critical_vulnerabilities": 0,
                "high_vulnerabilities": 1,
                "medium_vulnerabilities": 3,
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
                "high_vulnerabilities": 1,
                "medium_vulnerabilities": 3,
                "build_status": "passing",
                "documentation_coverage": 0.4,
                "total_loc": 1000,
                "test_loc": 500,
                "git_commits": 10,
                "git_secrets_found": 0,
            },
            "phase_timestamps": {
                "assessment": datetime.utcnow().isoformat(),
                "structure_complete": datetime.utcnow().isoformat(),
            },
            "re_entry_events": [],
            "graduated": False,
        }

        old_state_path = old_memory_dir / "brownfield-state.json"
        with open(old_state_path, "w") as f:
            json.dump(old_state, f, indent=2)

        # Create old checkpoint files
        checkpoint_data = {
            "phase": "testing",
            "completed_tasks": [
                {
                    "id": "install_pytest",
                    "description": "Install pytest",
                    "phase": "testing",
                    "estimated_minutes": 10,
                    "completed": True,
                    "status": "completed",
                    "error_message": None,
                }
            ],
            "pending_tasks": [
                {
                    "id": "write_tests",
                    "description": "Write unit tests",
                    "phase": "testing",
                    "estimated_minutes": 60,
                    "completed": False,
                    "status": "pending",
                    "error_message": None,
                }
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "interrupted": False,
            "context": {},
        }

        checkpoint_path = old_checkpoint_dir / "testing-checkpoint.json"
        with open(checkpoint_path, "w") as f:
            json.dump(checkpoint_data, f, indent=2)

        return project_root

    def test_complete_migration_from_v1_to_v2(self, v1_project):
        """Test complete migration workflow from v1.0 to v2.0."""
        memory_dir = v1_project / ".specify" / "memory"

        # Verify v1.0 state exists
        old_state_path = memory_dir / "brownfield-state.json"
        assert old_state_path.exists()

        # Check migration is needed
        migration_reason = check_migration_needed(memory_dir)
        assert migration_reason is not None
        assert "needs migration" in migration_reason.lower()

        # Perform migration
        success = migrate_state_file(memory_dir)
        assert success is True

        # Verify new state file exists
        new_state_path = memory_dir / "state.json"
        assert new_state_path.exists()

        # Verify old state file was archived
        archived_files = list(memory_dir.glob("brownfield-state.json.archived_*"))
        assert len(archived_files) == 1

        # Load migrated state
        state_store = StateStore(new_state_path)
        state = state_store.load()

        # Verify workflow field was added
        assert state.workflow == "brownfield"

        # Verify schema version updated
        assert state.schema_version == "2.0"

        # Verify all original data preserved
        assert state.current_phase == Phase.TESTING
        assert state.baseline_metrics.test_coverage == 0.5

    def test_checkpoint_migration_to_new_location(self, v1_project):
        """Test checkpoint files migrated to new location."""
        old_checkpoint_dir = v1_project / ".brownfield" / "checkpoints"
        new_checkpoint_dir = v1_project / ".specify" / "brownfield" / "checkpoints"

        # Verify old checkpoints exist
        old_checkpoint_files = list(old_checkpoint_dir.glob("*.json"))
        assert len(old_checkpoint_files) > 0

        # Migrate checkpoints manually (simulating CLI command)
        new_checkpoint_dir.mkdir(parents=True, exist_ok=True)
        for old_file in old_checkpoint_files:
            shutil.copy2(old_file, new_checkpoint_dir / old_file.name)

        # Verify new location has checkpoints
        new_checkpoint_files = list(new_checkpoint_dir.glob("*.json"))
        assert len(new_checkpoint_files) == len(old_checkpoint_files)

        # Verify checkpoint can be loaded from new location
        manager = CheckpointManager(v1_project)
        checkpoint = manager.load_checkpoint(Phase.TESTING)

        assert checkpoint is not None
        assert len(checkpoint.completed_tasks) == 1
        assert len(checkpoint.pending_tasks) == 1

    def test_migration_preserves_all_fields(self, v1_project):
        """Test migration preserves all state fields."""
        memory_dir = v1_project / ".specify" / "memory"

        # Load original state
        old_state_path = memory_dir / "brownfield-state.json"
        with open(old_state_path) as f:
            original_data = json.load(f)

        # Perform migration
        migrate_state_file(memory_dir)

        # Load migrated state
        new_state_path = memory_dir / "state.json"
        state_store = StateStore(new_state_path)
        state = state_store.load()

        # Verify all fields preserved
        assert state.baseline_metrics.test_coverage == original_data["baseline_metrics"]["test_coverage"]
        assert state.current_metrics.complexity_avg == original_data["current_metrics"]["complexity_avg"]
        assert len(state.phase_timestamps) == len(original_data["phase_timestamps"])
        assert state.graduated == original_data["graduated"]

    def test_migration_rollback(self, v1_project):
        """Test migration can be rolled back."""
        memory_dir = v1_project / ".specify" / "memory"

        # Perform migration
        migrate_state_file(memory_dir)

        # Verify migration occurred
        new_state_path = memory_dir / "state.json"
        assert new_state_path.exists()

        old_state_path = memory_dir / "brownfield-state.json"
        assert not old_state_path.exists()

        # Rollback migration
        success = rollback_migration(memory_dir)
        assert success is True

        # Verify old state restored
        assert old_state_path.exists()
        assert not new_state_path.exists()

        # Verify data integrity
        with open(old_state_path) as f:
            restored_data = json.load(f)

        assert restored_data["current_phase"] == "testing"
        assert restored_data["baseline_metrics"]["test_coverage"] == 0.5

    def test_migration_backup_creation(self, v1_project):
        """Test migration creates backup of existing state.json."""
        memory_dir = v1_project / ".specify" / "memory"

        # Create existing state.json (to test backup)
        existing_state_path = memory_dir / "state.json"
        existing_data = {"existing": "data"}
        with open(existing_state_path, "w") as f:
            json.dump(existing_data, f)

        # Perform migration
        migrate_state_file(memory_dir)

        # Verify backup was created
        backups = list(memory_dir.glob("state.backup_*.json"))
        assert len(backups) == 1

        # Verify backup contains original data
        with open(backups[0]) as f:
            backup_data = json.load(f)

        assert backup_data == existing_data

    def test_migration_atomic_write(self, v1_project):
        """Test migration uses atomic write (no corrupt state)."""
        memory_dir = v1_project / ".specify" / "memory"

        # Perform migration
        migrate_state_file(memory_dir)

        # Verify no temporary files remain
        tmp_files = list(memory_dir.glob("*.tmp"))
        assert len(tmp_files) == 0

        # Verify state.json is valid
        new_state_path = memory_dir / "state.json"
        state_store = StateStore(new_state_path)
        state = state_store.load()

        assert state.workflow == "brownfield"

    def test_migration_workflow_state_initialization(self, v1_project):
        """Test migration initializes workflow_state for v1.0 projects."""
        memory_dir = v1_project / ".specify" / "memory"

        # Perform migration
        migrate_state_file(memory_dir)

        # Load migrated state
        new_state_path = memory_dir / "state.json"
        state_store = StateStore(new_state_path)
        state = state_store.load()

        # Verify workflow_state was initialized
        assert state.workflow_state is not None
        assert state.workflow_state.current_phase is not None

    def test_migration_handles_missing_fields(self, v1_project):
        """Test migration handles v1.0 states with missing optional fields."""
        memory_dir = v1_project / ".specify" / "memory"

        # Modify old state to remove optional fields
        old_state_path = memory_dir / "brownfield-state.json"
        with open(old_state_path) as f:
            old_data = json.load(f)

        # Remove optional fields
        old_data.pop("re_entry_events", None)
        old_data.pop("graduated", None)

        with open(old_state_path, "w") as f:
            json.dump(old_data, f, indent=2)

        # Perform migration
        success = migrate_state_file(memory_dir)
        assert success is True

        # Load migrated state
        new_state_path = memory_dir / "state.json"
        state_store = StateStore(new_state_path)
        state = state_store.load()

        # Verify defaults were applied
        assert state.re_entry_events == []
        assert state.graduated is False

    def test_no_migration_needed_for_v2_projects(self, tmp_path):
        """Test migration skipped for projects already on v2.0."""
        project_root = tmp_path / "v2_project"
        project_root.mkdir()

        memory_dir = project_root / ".specify" / "memory"
        memory_dir.mkdir(parents=True)

        # Create v2.0 state directly
        from brownfield.models.assessment import Metrics
        from brownfield.models.state import BrownfieldState

        metrics = Metrics(
            test_coverage=0.6,
            complexity_avg=8.0,
            complexity_max=12,
            critical_vulnerabilities=0,
            high_vulnerabilities=0,
            medium_vulnerabilities=0,
            build_status="passing",
            documentation_coverage=0.5,
            total_loc=1000,
            test_loc=600,
            git_commits=15,
            git_secrets_found=0,
        )

        state = BrownfieldState(
            workflow="brownfield",
            schema_version="2.0",
            project_root=project_root,
            current_phase=Phase.QUALITY,
            baseline_metrics=metrics,
            current_metrics=metrics,
        )

        state_store = StateStore(memory_dir / "state.json")
        state_store.save(state)

        # Check migration needed
        migration_reason = check_migration_needed(memory_dir)
        assert migration_reason is None  # No migration needed

        # Attempt migration (should be no-op)
        success = migrate_state_file(memory_dir)
        assert success is False  # Returns False for no-op
