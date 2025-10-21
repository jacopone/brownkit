"""Brownfield state tracking models."""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from brownfield.models.assessment import Metrics


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
    resolved_at: Optional[datetime] = None


@dataclass
class BrownfieldState:
    """Current state of brownfield transition workflow."""

    schema_version: str
    project_root: Path
    current_phase: Phase
    baseline_metrics: Metrics
    current_metrics: Metrics
    phase_timestamps: dict[str, datetime] = field(default_factory=dict)
    re_entry_events: list[ReEntryEvent] = field(default_factory=list)
    graduation_timestamp: Optional[datetime] = None
    graduated: bool = False
    ai_agent_version: str = "0.1.0"

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

    def detect_regression(self) -> Optional[ReEntryEvent]:
        """Check if metrics have regressed below thresholds."""
        # Coverage drop check
        if (
            self.current_metrics.test_coverage < 0.5
            and self.baseline_metrics.test_coverage >= 0.6
        ):
            return ReEntryEvent(
                detected_at=datetime.utcnow(),
                trigger="coverage_drop",
                baseline_value=self.baseline_metrics.test_coverage,
                current_value=self.current_metrics.test_coverage,
                threshold_breached=0.5,
                re_entry_phase=Phase.TESTING,
            )

        # Complexity increase check
        if (
            self.current_metrics.complexity_avg > 12
            and self.baseline_metrics.complexity_avg <= 10
        ):
            return ReEntryEvent(
                detected_at=datetime.utcnow(),
                trigger="complexity_increase",
                baseline_value=self.baseline_metrics.complexity_avg,
                current_value=self.current_metrics.complexity_avg,
                threshold_breached=12.0,
                re_entry_phase=Phase.QUALITY,
            )

        # Security breach check
        if (
            self.current_metrics.critical_vulnerabilities > 0
            and self.baseline_metrics.critical_vulnerabilities == 0
        ):
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
        data["project_root"] = str(self.project_root)
        # Convert Phase enum to string
        data["current_phase"] = self.current_phase.value
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
        return json.dumps(data, indent=2)

    @classmethod
    def load(cls, path: Path) -> "BrownfieldState":
        """Load state from JSON file."""
        if not path.exists():
            raise FileNotFoundError(f"State file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convert strings back to appropriate types
        data["project_root"] = Path(data["project_root"])
        data["current_phase"] = Phase(data["current_phase"])

        # Convert ISO datetime strings back to datetime objects
        phase_timestamps = {}
        for key, value in data["phase_timestamps"].items():
            phase_timestamps[key] = datetime.fromisoformat(value)
        data["phase_timestamps"] = phase_timestamps

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

        # Convert metrics dicts to Metrics objects
        data["baseline_metrics"] = Metrics(**data["baseline_metrics"])
        data["current_metrics"] = Metrics(**data["current_metrics"])

        return cls(**data)

    def save(self, path: Path) -> None:
        """Save state to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())
