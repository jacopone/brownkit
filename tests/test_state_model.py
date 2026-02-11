"""Unit tests for state model updates (Phase 1)."""

import json
from datetime import datetime
from pathlib import Path

from brownfield.models.state import BrownfieldState, Phase, SpecKitIntegration
from brownfield.models.workflow import PhaseExecution, PhaseStatus, WorkflowPhase, WorkflowState


class TestSpecKitIntegration:
    """Test SpecKitIntegration dataclass."""

    def test_creation_defaults(self):
        """Test creating SpecKitIntegration with defaults."""
        speckit = SpecKitIntegration()

        assert speckit.version is None
        assert speckit.installed is False
        assert speckit.initialized is False
        assert speckit.warned_missing is False
        assert speckit.constitution_generated is False
        assert speckit.constitution_path is None
        assert speckit.last_monitor_check is None

    def test_creation_with_values(self):
        """Test creating SpecKitIntegration with custom values."""
        now = datetime.utcnow()
        const_path = Path("/home/user/.specify/memory/constitution.md")

        speckit = SpecKitIntegration(
            version="1.0.0",
            installed=True,
            initialized=True,
            warned_missing=False,
            constitution_generated=True,
            constitution_path=const_path,
            last_monitor_check=now,
        )

        assert speckit.version == "1.0.0"
        assert speckit.installed is True
        assert speckit.initialized is True
        assert speckit.warned_missing is False
        assert speckit.constitution_generated is True
        assert speckit.constitution_path == const_path
        assert speckit.last_monitor_check == now


class TestBrownfieldStateEnhancements:
    """Test BrownfieldState enhancements for Phase 1."""

    def test_schema_version_2_0(self):
        """Test state has schema version 2.0."""
        state = BrownfieldState()
        assert state.schema_version == "2.0"

    def test_default_workflow_state(self):
        """Test state has default WorkflowState."""
        state = BrownfieldState()

        assert isinstance(state.workflow_state, WorkflowState)
        assert state.workflow_state.current_phase == WorkflowPhase.NOT_STARTED
        assert state.workflow_state.phase_executions == {}
        assert state.workflow_state.can_skip_phases is False

    def test_default_speckit_integration(self):
        """Test state has default SpecKitIntegration."""
        state = BrownfieldState()

        assert isinstance(state.speckit, SpecKitIntegration)
        assert state.speckit.installed is False
        assert state.speckit.initialized is False

    def test_migration_tracking_fields(self):
        """Test migration tracking fields."""
        state = BrownfieldState()

        assert state.migrated_from_version is None
        assert state.checkpoint_path_migrated is False

    def test_workflow_state_progression(self):
        """Test workflow state can be modified and tracked."""
        state = BrownfieldState()

        # Mark assessment as completed
        assessment_exec = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.COMPLETED)
        state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment_exec
        state.workflow_state.current_phase = WorkflowPhase.PLANNING

        assert state.workflow_state.current_phase == WorkflowPhase.PLANNING
        assert len(state.workflow_state.phase_executions) == 1
        assert state.workflow_state.is_phase_completed(WorkflowPhase.ASSESSMENT)


class TestStateSerialization:
    """Test state serialization with new fields."""

    def test_serialize_with_workflow_state(self):
        """Test serialization includes workflow_state."""
        state = BrownfieldState()

        # Add some workflow progression
        assessment = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.COMPLETED)
        state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment
        state.workflow_state.current_phase = WorkflowPhase.PLANNING

        # Serialize to JSON
        json_data = state.to_json()
        data = json.loads(json_data)

        # Verify workflow_state is serialized
        assert "workflow_state" in data
        assert data["workflow_state"]["current_phase"] == "planning"
        assert "phase_executions" in data["workflow_state"]

    def test_serialize_with_speckit_integration(self):
        """Test serialization includes speckit fields."""
        state = BrownfieldState()
        state.speckit.version = "1.0.0"
        state.speckit.installed = True
        state.speckit.constitution_generated = True

        # Serialize to JSON
        json_data = state.to_json()
        data = json.loads(json_data)

        # Verify speckit is serialized
        assert "speckit" in data
        assert data["speckit"]["version"] == "1.0.0"
        assert data["speckit"]["installed"] is True
        assert data["speckit"]["constitution_generated"] is True

    def test_serialize_phase_execution_fields(self):
        """Test PhaseExecution serialization includes all fields."""
        state = BrownfieldState()

        # Create phase execution with all fields
        assessment = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.COMPLETED)
        assessment.mark_started()
        assessment.mark_completed()

        state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment

        # Serialize
        json_data = state.to_json()
        data = json.loads(json_data)

        # Verify phase execution fields
        phase_data = data["workflow_state"]["phase_executions"]["assessment"]
        assert phase_data["phase"] == "assessment"
        assert phase_data["status"] == "completed"
        assert "started_at" in phase_data
        assert "completed_at" in phase_data
        assert phase_data["attempts"] == 1


class TestBackwardCompatibility:
    """Test backward compatibility with v1.0 state files."""

    def test_load_v1_state_auto_migrates(self, tmp_path):
        """Test loading v1.0 state auto-creates v2.0 fields."""
        # Create v1.0 state JSON (no workflow_state or speckit)
        v1_state = {
            "schema_version": "1.0",
            "project_root": "/home/user/project",
            "current_phase": "assessment",
            "graduated": False,
            "ai_agent_version": "0.1.0",
            "baseline_metrics": None,
            "current_metrics": None,
            "re_entry_events": [],
        }

        # Write v1.0 state file
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps(v1_state, indent=2))

        # Load state (should auto-migrate)
        loaded_state = BrownfieldState.load(state_file)

        # Verify v2.0 fields were added with defaults
        assert loaded_state.schema_version == "2.0"
        assert isinstance(loaded_state.workflow_state, WorkflowState)
        assert loaded_state.workflow_state.current_phase == WorkflowPhase.NOT_STARTED
        assert isinstance(loaded_state.speckit, SpecKitIntegration)
        assert loaded_state.speckit.installed is False

        # Verify migration tracking
        assert loaded_state.migrated_from_version == "1.0"

    def test_load_v2_state_preserves_fields(self, tmp_path):
        """Test loading v2.0 state preserves all fields."""
        # Create v2.0 state
        state = BrownfieldState()
        state.project_root = Path("/home/user/project")
        state.workflow_state.current_phase = WorkflowPhase.PLANNING
        state.speckit.version = "1.0.0"
        state.speckit.installed = True

        # Save and reload
        state_file = tmp_path / "state.json"
        state_file.write_text(state.to_json())

        loaded_state = BrownfieldState.load(state_file)

        # Verify all fields preserved
        assert loaded_state.schema_version == "2.0"
        assert loaded_state.workflow_state.current_phase == WorkflowPhase.PLANNING
        assert loaded_state.speckit.version == "1.0.0"
        assert loaded_state.speckit.installed is True
        assert loaded_state.migrated_from_version is None  # Not a migration

    def test_migration_preserves_existing_data(self, tmp_path):
        """Test migration preserves all v1.0 data."""
        # Create v1.0 state with existing data
        v1_state = {
            "schema_version": "1.0",
            "project_root": "/home/user/project",
            "current_phase": "structure",
            "graduated": False,
            "ai_agent_version": "0.1.0",
            "baseline_metrics": {
                "test_coverage": 0.65,
                "complexity_avg": 12.5,
                "complexity_max": 45,
                "critical_vulnerabilities": 0,
                "high_vulnerabilities": 2,
                "medium_vulnerabilities": 5,
                "build_status": "passing",
                "documentation_coverage": 0.45,
                "total_loc": 15000,
                "test_loc": 3500,
                "git_commits": 125,
                "git_secrets_found": 0,
                "complexity_violations": [],
            },
            "current_metrics": None,
            "re_entry_events": [],
        }

        # Write and load
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps(v1_state, indent=2))
        loaded_state = BrownfieldState.load(state_file)

        # Verify existing data preserved
        assert loaded_state.current_phase == Phase.STRUCTURE
        assert loaded_state.graduated is False
        assert loaded_state.baseline_metrics.test_coverage == 0.65
        assert loaded_state.baseline_metrics.complexity_avg == 12.5
        assert loaded_state.baseline_metrics.total_loc == 15000

        # Verify new fields added
        assert isinstance(loaded_state.workflow_state, WorkflowState)
        assert isinstance(loaded_state.speckit, SpecKitIntegration)


class TestStateIntegration:
    """Integration tests for state model with workflow."""

    def test_full_workflow_progression_in_state(self):
        """Test complete workflow progression tracked in state."""
        state = BrownfieldState()
        state.project_root = Path("/home/user/project")
        state.language = "python"

        # Phase 1: Assessment
        assessment = PhaseExecution(phase=WorkflowPhase.ASSESSMENT, status=PhaseStatus.NOT_STARTED)
        assessment.mark_started()
        assessment.mark_completed()
        state.workflow_state.phase_executions[WorkflowPhase.ASSESSMENT] = assessment
        state.workflow_state.current_phase = WorkflowPhase.PLANNING

        # Phase 2: Planning
        planning = PhaseExecution(phase=WorkflowPhase.PLANNING, status=PhaseStatus.NOT_STARTED)
        planning.mark_started()
        planning.mark_completed()
        state.workflow_state.phase_executions[WorkflowPhase.PLANNING] = planning
        state.workflow_state.current_phase = WorkflowPhase.REMEDIATION

        # Verify state tracks progression
        assert state.workflow_state.is_phase_completed(WorkflowPhase.ASSESSMENT)
        assert state.workflow_state.is_phase_completed(WorkflowPhase.PLANNING)
        assert state.workflow_state.current_phase == WorkflowPhase.REMEDIATION

        # Verify can execute next phase
        can_exec, _ = state.workflow_state.can_execute_phase(WorkflowPhase.REMEDIATION)
        assert can_exec is True

    def test_state_with_speckit_integration_workflow(self):
        """Test state tracks Spec-Kit integration alongside workflow."""
        state = BrownfieldState()

        # Complete graduation
        for phase in [
            WorkflowPhase.ASSESSMENT,
            WorkflowPhase.PLANNING,
            WorkflowPhase.REMEDIATION,
            WorkflowPhase.VALIDATION,
            WorkflowPhase.GRADUATION,
        ]:
            exec = PhaseExecution(phase=phase, status=PhaseStatus.COMPLETED)
            state.workflow_state.phase_executions[phase] = exec

        # Mark Spec-Kit initialized
        state.speckit.version = "1.0.0"
        state.speckit.installed = True
        state.speckit.initialized = True
        state.speckit.constitution_generated = True
        state.speckit.constitution_path = Path("/home/user/.specify/memory/constitution.md")

        # Verify both systems tracked
        assert state.workflow_state.is_phase_completed(WorkflowPhase.GRADUATION)
        assert state.speckit.initialized is True
        assert state.speckit.constitution_path.name == "constitution.md"
