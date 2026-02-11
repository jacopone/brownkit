"""Brownfield state tracking models."""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

from brownfield.models.assessment import Metrics
from brownfield.models.workflow import PhaseExecution, PhaseStatus, WorkflowPhase, WorkflowState


class Phase(Enum):
    """Brownfield workflow phases."""

    ASSESSMENT = "assessment"
    STRUCTURE = "structure"
    TESTING = "testing"
    QUALITY = "quality"
    VALIDATION = "validation"
    GRADUATED = "graduated"


@dataclass
class ReEntryEvent:
    """Records regression that triggered workflow re-entry."""

    detected_at: datetime
    trigger: str
    baseline_value: float
    current_value: float
    threshold_breached: float
    re_entry_phase: Phase
    resolved: bool = False
    resolved_at: datetime | None = None


@dataclass
class SpecKitIntegration:
    """Spec-Kit integration metadata and state."""

    version: str | None = None
    installed: bool = False
    initialized: bool = False
    warned_missing: bool = False
    constitution_generated: bool = False
    constitution_path: Path | None = None
    last_monitor_check: datetime | None = None


@dataclass
class BrownfieldState:
    """Current state of brownfield transition workflow."""

    # Speckit compatibility fields
    workflow: str = "brownfield"  # Workflow type discriminator
    schema_version: str = "2.0"  # State schema version (bumped for workflow system)

    # Core workflow fields
    project_root: Path = None
    current_phase: Phase = Phase.ASSESSMENT  # Legacy phase tracking (kept for backward compat)
    baseline_metrics: Metrics | None = None
    current_metrics: Metrics | None = None
    phase_timestamps: dict[str, datetime] = field(default_factory=dict)
    re_entry_events: list[ReEntryEvent] = field(default_factory=list)
    graduation_timestamp: datetime | None = None
    graduated: bool = False
    ai_agent_version: str = "0.1.0"

    # NEW: Workflow enforcement system (v2.0)
    workflow_state: WorkflowState = field(default_factory=WorkflowState)

    # NEW: Spec-Kit integration (v2.0)
    speckit: SpecKitIntegration = field(default_factory=SpecKitIntegration)

    # NEW: Migration tracking (v2.0)
    migrated_from_version: str | None = None
    checkpoint_path_migrated: bool = False

    def update_metrics(self, new_metrics: Metrics) -> None:
        """Update current metrics and record timestamp."""
        self.current_metrics = new_metrics
        timestamp_key = f"{self.current_phase.value}_metrics_updated"
        self.phase_timestamps[timestamp_key] = datetime.utcnow()

    def advance_phase(self, next_phase: Phase) -> None:
        """Transition to next phase and record timestamp."""
        complete_key = f"{self.current_phase.value}_complete"
        self.phase_timestamps[complete_key] = datetime.utcnow()
        self.current_phase = next_phase
        start_key = f"{next_phase.value}_start"
        self.phase_timestamps[start_key] = datetime.utcnow()

    def detect_regression(self) -> ReEntryEvent | None:
        """Check if metrics have regressed below thresholds."""
        # Coverage drop check
        if self.current_metrics.test_coverage < 0.5 and self.baseline_metrics.test_coverage >= 0.6:
            return ReEntryEvent(
                detected_at=datetime.utcnow(),
                trigger="coverage_drop",
                baseline_value=self.baseline_metrics.test_coverage,
                current_value=self.current_metrics.test_coverage,
                threshold_breached=0.5,
                re_entry_phase=Phase.TESTING,
            )

        # Complexity increase check
        if self.current_metrics.complexity_avg > 12 and self.baseline_metrics.complexity_avg <= 10:
            return ReEntryEvent(
                detected_at=datetime.utcnow(),
                trigger="complexity_increase",
                baseline_value=self.baseline_metrics.complexity_avg,
                current_value=self.current_metrics.complexity_avg,
                threshold_breached=12.0,
                re_entry_phase=Phase.QUALITY,
            )

        # Security breach check
        if self.current_metrics.critical_vulnerabilities > 0 and self.baseline_metrics.critical_vulnerabilities == 0:
            return ReEntryEvent(
                detected_at=datetime.utcnow(),
                trigger="security_breach",
                baseline_value=float(self.baseline_metrics.critical_vulnerabilities),
                current_value=float(self.current_metrics.critical_vulnerabilities),
                threshold_breached=0.0,
                re_entry_phase=Phase.QUALITY,
            )

        return None

    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = asdict(self)
        # Convert Path objects to strings
        data["project_root"] = str(self.project_root) if self.project_root else None

        # Convert Phase enum to string (handle both enum and string)
        data["current_phase"] = (
            self.current_phase.value if isinstance(self.current_phase, Phase) else self.current_phase
        )

        # Convert datetime objects to ISO format
        for key, value in data["phase_timestamps"].items():
            if isinstance(value, datetime):
                data["phase_timestamps"][key] = value.isoformat()
        if data["graduation_timestamp"]:
            data["graduation_timestamp"] = data["graduation_timestamp"].isoformat()

        # Convert re_entry_events
        for event in data["re_entry_events"]:
            event["detected_at"] = event["detected_at"].isoformat()
            if event["resolved_at"]:
                event["resolved_at"] = event["resolved_at"].isoformat()
            event["re_entry_phase"] = event["re_entry_phase"].value

        # NEW: Convert workflow_state
        workflow_data = data["workflow_state"]
        workflow_data["current_phase"] = workflow_data["current_phase"].value

        # Convert phase_executions dict
        phase_execs = {}
        for phase_enum, execution_data in workflow_data["phase_executions"].items():
            # Convert WorkflowPhase enum to string
            phase_value = phase_enum.value
            execution_data["phase"] = execution_data["phase"].value
            execution_data["status"] = execution_data["status"].value
            if execution_data.get("started_at"):
                execution_data["started_at"] = execution_data["started_at"].isoformat()
            if execution_data.get("completed_at"):
                execution_data["completed_at"] = execution_data["completed_at"].isoformat()
            phase_execs[phase_value] = execution_data
        workflow_data["phase_executions"] = phase_execs

        # NEW: Convert speckit fields
        speckit_data = data["speckit"]
        if speckit_data.get("constitution_path"):
            speckit_data["constitution_path"] = str(speckit_data["constitution_path"])
        if speckit_data.get("last_monitor_check"):
            speckit_data["last_monitor_check"] = speckit_data["last_monitor_check"].isoformat()

        return json.dumps(data, indent=2)

    @classmethod
    def load(cls, path: Path) -> "BrownfieldState":
        """Load state from JSON file with backward compatibility."""
        if not path.exists():
            raise FileNotFoundError(f"State file not found: {path}")

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        # Convert strings back to appropriate types
        if data.get("project_root"):
            data["project_root"] = Path(data["project_root"])

        # Convert current_phase to Phase enum if it's a string (both v1.0 and v2.0)
        if "current_phase" in data and isinstance(data["current_phase"], str):
            data["current_phase"] = Phase(data["current_phase"])

        # Convert ISO datetime strings back to datetime objects
        if "phase_timestamps" in data:
            phase_timestamps = {}
            for key, value in data["phase_timestamps"].items():
                phase_timestamps[key] = datetime.fromisoformat(value)
            data["phase_timestamps"] = phase_timestamps
        else:
            # v1.0 compatibility - create empty phase_timestamps
            data["phase_timestamps"] = {}

        if data.get("graduation_timestamp"):
            data["graduation_timestamp"] = datetime.fromisoformat(data["graduation_timestamp"])

        # Convert re_entry_events
        re_entry_events = []
        for event_data in data.get("re_entry_events", []):
            event_data["detected_at"] = datetime.fromisoformat(event_data["detected_at"])
            if event_data.get("resolved_at"):
                event_data["resolved_at"] = datetime.fromisoformat(event_data["resolved_at"])
            event_data["re_entry_phase"] = Phase(event_data["re_entry_phase"])
            re_entry_events.append(ReEntryEvent(**event_data))
        data["re_entry_events"] = re_entry_events

        # Convert metrics dicts to Metrics objects (handle None values)
        if data.get("baseline_metrics"):
            data["baseline_metrics"] = Metrics(**data["baseline_metrics"])
        else:
            data["baseline_metrics"] = None

        if data.get("current_metrics"):
            data["current_metrics"] = Metrics(**data["current_metrics"])
        else:
            data["current_metrics"] = None

        # Set defaults for backward compatibility (v1.0 → v2.0 migration)
        data.setdefault("workflow", "brownfield")
        schema_version = data.get("schema_version", "1.0")

        # NEW: Handle workflow_state (v2.0)
        if "workflow_state" in data:
            workflow_data = data["workflow_state"]
            workflow_data["current_phase"] = WorkflowPhase(workflow_data["current_phase"])

            # Convert phase_executions
            phase_execs = {}
            for phase_str, exec_data in workflow_data.get("phase_executions", {}).items():
                phase = WorkflowPhase(phase_str)
                exec_data["phase"] = WorkflowPhase(exec_data["phase"])
                exec_data["status"] = PhaseStatus(exec_data["status"])
                if exec_data.get("started_at"):
                    exec_data["started_at"] = datetime.fromisoformat(exec_data["started_at"])
                if exec_data.get("completed_at"):
                    exec_data["completed_at"] = datetime.fromisoformat(exec_data["completed_at"])
                phase_execs[phase] = PhaseExecution(**exec_data)
            workflow_data["phase_executions"] = phase_execs

            data["workflow_state"] = WorkflowState(**workflow_data)
        else:
            # Migrating from v1.0 - create default workflow state
            data["workflow_state"] = WorkflowState()
            data["migrated_from_version"] = schema_version

        # NEW: Handle speckit (v2.0)
        if "speckit" in data:
            speckit_data = data["speckit"]
            if speckit_data.get("constitution_path"):
                speckit_data["constitution_path"] = Path(speckit_data["constitution_path"])
            if speckit_data.get("last_monitor_check"):
                speckit_data["last_monitor_check"] = datetime.fromisoformat(speckit_data["last_monitor_check"])
            data["speckit"] = SpecKitIntegration(**speckit_data)
        else:
            # Migrating from v1.0 - create default speckit integration
            data["speckit"] = SpecKitIntegration()

        # NEW: Migration tracking defaults
        data.setdefault("migrated_from_version", None)
        data.setdefault("checkpoint_path_migrated", False)

        # Always set schema_version to current
        data["schema_version"] = "2.0"

        return cls(**data)

    def save(self, path: Path) -> None:
        """Save state to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())
