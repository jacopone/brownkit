# Data Model: BrownKit Implementation

**Feature**: BrownKit Implementation
**Created**: 2025-10-12
**Status**: Complete

## Entity Relationship Overview

```
AssessmentReport
    ├── language_detection: LanguageDetection
    ├── baseline_metrics: Metrics
    ├── tech_debt: TechDebtAnalysis
    └── limitations: list[str]

BrownfieldState
    ├── current_phase: Phase
    ├── baseline_metrics: Metrics
    ├── current_metrics: Metrics
    ├── phase_checkpoints: list[PhaseCheckpoint]
    └── re_entry_events: list[ReEntryEvent]

PhaseCheckpoint
    ├── phase: Phase
    ├── completed_tasks: list[str]
    ├── total_tasks: int
    └── interrupted: bool

DecisionEntry
    ├── problem: str
    ├── solution: str
    ├── confidence: ConfidenceLevel
    ├── alternatives: list[Alternative]
    └── risks: list[Risk]

ReadinessGate
    ├── name: str
    ├── threshold: float
    ├── current_value: float
    ├── passed: bool
    └── verification_command: str

GraduationReport
    ├── baseline_metrics: Metrics
    ├── final_metrics: Metrics
    ├── structural_changes: list[StructuralChange]
    ├── test_improvements: list[TestImprovement]
    └── archived_artifacts: list[Path]
```

## Core Entities

### 1. AssessmentReport

**Purpose**: Captures initial codebase analysis including language detection, baseline metrics, tech debt categorization, and analysis limitations.

**Storage**: `.specify/memory/assessment-report.md` (Markdown format for human readability)

**Python Dataclass**:

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

class ConfidenceLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class LanguageDetection:
    """Language and framework detection results."""
    language: str
    confidence: ConfidenceLevel
    version: str | None
    framework: str | None
    secondary_languages: list[tuple[str, float]] = field(default_factory=list)
    detection_evidence: dict[str, str] = field(default_factory=dict)
    # Example evidence: {"pyproject.toml": "found", "setup.py": "found"}

@dataclass
class Metrics:
    """Quantitative codebase metrics."""
    test_coverage: float  # 0.0-1.0
    complexity_avg: float  # Cyclomatic complexity average
    complexity_max: int  # Maximum complexity in codebase
    critical_vulnerabilities: int
    high_vulnerabilities: int
    medium_vulnerabilities: int
    build_status: str  # "passing" | "failing" | "unknown"
    documentation_coverage: float  # Percentage of public APIs with docs
    total_loc: int  # Lines of code
    test_loc: int  # Lines of test code
    git_commits: int  # Total commits
    git_secrets_found: int  # Secrets detected by scanner

@dataclass
class TechDebtCategory:
    """Tech debt in a specific category."""
    category: str  # "structural" | "testing" | "documentation" | "security"
    severity: str  # "critical" | "high" | "medium" | "low"
    issues: list[str]
    estimated_remediation_time: str  # Human-readable estimate

@dataclass
class AssessmentReport:
    """Complete codebase assessment report."""
    project_name: str
    project_root: Path
    assessed_at: datetime
    agent_version: str

    language_detection: LanguageDetection
    baseline_metrics: Metrics
    tech_debt: list[TechDebtCategory]

    assumptions: list[str]  # AI assumptions about project purpose
    limitations: list[str]  # Analysis limitations (missing tools, unclear code)
    risk_assessment: str  # Overall risk level for automated remediation

    analysis_mode: str  # "quick" | "full"
    analysis_duration_seconds: int

    def to_markdown(self) -> str:
        """Generate Markdown report for human consumption."""
        # Implementation generates formatted report
        pass

    @classmethod
    def from_markdown(cls, path: Path) -> 'AssessmentReport':
        """Parse existing assessment report."""
        # Implementation parses structured Markdown
        pass
```

**Key Attributes**:
- `language_detection.confidence`: Determines whether to prompt user for confirmation
- `baseline_metrics`: Stored for comparison during validation phase
- `tech_debt`: Prioritized list driving remediation phases
- `limitations`: Documents what AI couldn't analyze (missing tools, obfuscated code)

**Usage Example**:
```python
report = AssessmentReport(
    project_name="legacy-api",
    language_detection=LanguageDetection(
        language="python",
        confidence=ConfidenceLevel.HIGH,
        version="3.9",
        framework="flask",
        detection_evidence={
            "pyproject.toml": "found with flask dependency",
            "app.py": "contains Flask() instantiation"
        }
    ),
    baseline_metrics=Metrics(
        test_coverage=0.0,
        complexity_avg=15.2,
        critical_vulnerabilities=2
    ),
    tech_debt=[
        TechDebtCategory(
            category="structural",
            severity="high",
            issues=["Source files in root directory", "No tests/ directory"],
            estimated_remediation_time="30 minutes"
        )
    ]
)
```

---

### 2. BrownfieldState

**Purpose**: Tracks workflow progression, metrics evolution, and phase transitions throughout brownfield process.

**Storage**: `.specify/memory/brownfield-state.json` (JSON for programmatic access)

**Python Dataclass**:

```python
@dataclass
class Phase(Enum):
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
    trigger: str  # "coverage_drop" | "complexity_increase" | "security_breach"
    baseline_value: float
    current_value: float
    threshold_breached: float
    re_entry_phase: Phase

@dataclass
class BrownfieldState:
    """Current state of brownfield transition workflow."""
    schema_version: str = "1.0"
    project_root: Path
    current_phase: Phase

    baseline_metrics: Metrics
    current_metrics: Metrics

    phase_timestamps: dict[str, datetime] = field(default_factory=dict)
    # Keys: "assessment", "structure_start", "structure_complete", etc.

    phase_checkpoints: list['PhaseCheckpoint'] = field(default_factory=list)
    re_entry_events: list[ReEntryEvent] = field(default_factory=list)

    graduation_timestamp: datetime | None = None
    graduated: bool = False

    def update_metrics(self, new_metrics: Metrics):
        """Update current metrics and record timestamp."""
        self.current_metrics = new_metrics
        self.phase_timestamps[f"{self.current_phase.value}_metrics_updated"] = datetime.utcnow()

    def advance_phase(self, next_phase: Phase):
        """Transition to next phase and record timestamp."""
        self.phase_timestamps[f"{self.current_phase.value}_complete"] = datetime.utcnow()
        self.current_phase = next_phase
        self.phase_timestamps[f"{next_phase.value}_start"] = datetime.utcnow()

    def detect_regression(self) -> ReEntryEvent | None:
        """Check if metrics have regressed below thresholds."""
        if self.current_metrics.test_coverage < 0.5 and self.baseline_metrics.test_coverage >= 0.6:
            return ReEntryEvent(
                detected_at=datetime.utcnow(),
                trigger="coverage_drop",
                baseline_value=self.baseline_metrics.test_coverage,
                current_value=self.current_metrics.test_coverage,
                threshold_breached=0.5,
                re_entry_phase=Phase.TESTING
            )
        # ... check other metrics
        return None

    def to_json(self) -> str:
        """Serialize to JSON string."""
        # Custom serialization handling Path and datetime
        pass

    @classmethod
    def load(cls, path: Path) -> 'BrownfieldState':
        """Load state from JSON file."""
        # Handle missing file, schema migration
        pass
```

**Key Attributes**:
- `current_phase`: Determines which commands are available
- `phase_timestamps`: Tracks time spent in each phase for reporting
- `re_entry_events`: History of quality regressions and recoveries

**State Transitions**:
```
ASSESSMENT → STRUCTURE → TESTING → QUALITY → VALIDATION → GRADUATED
     ↑           ↑          ↑          ↑
     └───────────┴──────────┴──────────┘
        (re-entry on regression detection)
```

---

### 3. PhaseCheckpoint

**Purpose**: Enables interruption recovery by tracking completed tasks within a phase.

**Storage**: `.specify/memory/brownfield-checkpoint.json`

**Python Dataclass**:

```python
@dataclass
class Task:
    """Individual task within a phase."""
    task_id: str
    description: str
    completed: bool
    completed_at: datetime | None
    git_commit_sha: str | None  # Commit created by this task

@dataclass
class PhaseCheckpoint:
    """Checkpoint for interruption recovery."""
    phase: Phase
    started_at: datetime
    last_checkpoint_at: datetime

    tasks: list[Task] = field(default_factory=list)
    interrupted: bool = False

    @property
    def completed_tasks(self) -> list[Task]:
        return [t for t in self.tasks if t.completed]

    @property
    def pending_tasks(self) -> list[Task]:
        return [t for t in self.tasks if not t.completed]

    @property
    def progress_percentage(self) -> float:
        if not self.tasks:
            return 0.0
        return len(self.completed_tasks) / len(self.tasks) * 100

    def mark_task_complete(self, task_id: str, commit_sha: str | None = None):
        """Mark task as completed and update checkpoint timestamp."""
        for task in self.tasks:
            if task.task_id == task_id:
                task.completed = True
                task.completed_at = datetime.utcnow()
                task.git_commit_sha = commit_sha
                break
        self.last_checkpoint_at = datetime.utcnow()

    def detect_interruption(self) -> bool:
        """Check if process was interrupted (incomplete tasks + old timestamp)."""
        if not self.interrupted:
            return False

        # Consider interrupted if last checkpoint > 5 minutes ago and incomplete
        time_since_checkpoint = datetime.utcnow() - self.last_checkpoint_at
        return time_since_checkpoint.total_seconds() > 300 and len(self.pending_tasks) > 0
```

**Checkpoint Update Frequency**: After each task completion (typically every 30-60 seconds of work).

**Recovery Logic**:
```python
def resume_from_checkpoint(checkpoint: PhaseCheckpoint) -> bool:
    """Offer user choice to resume or restart phase."""
    if not checkpoint.detect_interruption():
        return False

    console.print(f"[yellow]Interrupted {checkpoint.phase.value} detected[/yellow]")
    console.print(f"Progress: {checkpoint.progress_percentage:.1f}%")
    console.print(f"Completed: {len(checkpoint.completed_tasks)}/{len(checkpoint.tasks)} tasks")

    return click.confirm("Resume from checkpoint?", default=True)
```

---

### 4. DecisionEntry

**Purpose**: Documents AI reasoning for significant changes with problem analysis, solution rationale, alternatives considered, and risks.

**Storage**: `.specify/memory/brownfield-decisions.md` (append-only Markdown log)

**Python Dataclass**:

```python
@dataclass
class Alternative:
    """Alternative solution that was considered."""
    description: str
    pros: list[str]
    cons: list[str]
    rejected_reason: str

@dataclass
class Risk:
    """Identified risk with mitigation strategy."""
    description: str
    likelihood: str  # "high" | "medium" | "low"
    impact: str  # "critical" | "high" | "medium" | "low"
    mitigation: str
    rollback_procedure: str | None

@dataclass
class DecisionEntry:
    """Documented decision with rationale."""
    timestamp: datetime
    phase: Phase
    decision_id: str  # Unique identifier

    problem: str  # Problem being solved
    evidence: list[str]  # Evidence supporting problem identification
    solution: str  # Chosen solution
    rationale: str  # Why this solution was chosen
    confidence: ConfidenceLevel

    alternatives: list[Alternative] = field(default_factory=list)
    risks: list[Risk] = field(default_factory=list)

    requires_human_approval: bool = False
    approved: bool = False
    approved_by: str | None = None

    def to_markdown(self) -> str:
        """Format decision as Markdown section."""
        md = f"## Decision {self.decision_id} - {self.phase.value}\n\n"
        md += f"**Timestamp**: {self.timestamp.isoformat()}\n"
        md += f"**Confidence**: {self.confidence.value}\n\n"
        md += f"### Problem\n{self.problem}\n\n"
        md += f"**Evidence**:\n" + "\n".join(f"- {e}" for e in self.evidence) + "\n\n"
        md += f"### Solution\n{self.solution}\n\n"
        md += f"**Rationale**: {self.rationale}\n\n"

        if self.alternatives:
            md += "### Alternatives Considered\n"
            for alt in self.alternatives:
                md += f"- **{alt.description}**: {alt.rejected_reason}\n"

        if self.risks:
            md += "\n### Risks\n"
            for risk in self.risks:
                md += f"- **{risk.description}** ({risk.likelihood} likelihood, {risk.impact} impact)\n"
                md += f"  - Mitigation: {risk.mitigation}\n"

        return md
```

**Decision Approval Workflow**:
- High confidence decisions: Auto-approved, logged for transparency
- Medium confidence: Prompt user for approval before execution
- Low confidence: Require user approval and document user choice

**Usage Example**:
```python
decision = DecisionEntry(
    timestamp=datetime.utcnow(),
    phase=Phase.STRUCTURE,
    decision_id="STRUCT-001",
    problem="Source files scattered in root directory violate PEP 518",
    evidence=[
        "Found 12 .py files in project root",
        "No src/ directory exists",
        "pyproject.toml present (modern Python project)"
    ],
    solution="Create src/myproject/ and move all modules there",
    rationale="PEP 518 standardizes Python package structure; enables proper imports",
    confidence=ConfidenceLevel.HIGH,
    alternatives=[
        Alternative(
            description="Keep flat structure, only create tests/ directory",
            pros=["Less disruptive", "Simpler imports"],
            cons=["Doesn't follow modern conventions", "Harder to package"],
            rejected_reason="Modern Python projects should follow PEP 518"
        )
    ],
    risks=[
        Risk(
            description="Moving files may break import paths",
            likelihood="medium",
            impact="high",
            mitigation="Update imports automatically, verify build after each commit",
            rollback_procedure="git revert <commit-sha>"
        )
    ]
)
```

---

### 5. ReadinessGate

**Purpose**: Represents quantitative validation criterion that must pass before graduation.

**Storage**: Part of validation results (ephemeral, recalculated on each validation run)

**Python Dataclass**:

```python
@dataclass
class ReadinessGate:
    """Quantitative validation gate."""
    name: str
    description: str
    threshold: float
    current_value: float
    passed: bool

    verification_command: str  # Command to verify this gate
    remediation_guidance: str  # What to do if gate fails

    exception_conditions: list[str] = field(default_factory=list)
    # Conditions under which gate can be waived

    justification_required: bool = False
    justification: str | None = None

    def evaluate(self) -> bool:
        """Check if gate passes based on threshold."""
        self.passed = self.current_value >= self.threshold
        return self.passed

# Predefined gates
READINESS_GATES = [
    ReadinessGate(
        name="Test Coverage",
        description="Minimum test coverage on core business logic",
        threshold=0.6,
        current_value=0.0,  # Updated during validation
        passed=False,
        verification_command="pytest --cov=src --cov-report=json",
        remediation_guidance="Run /brownfield.testing to generate more tests",
        exception_conditions=["Project is pure library with no business logic"]
    ),
    ReadinessGate(
        name="Complexity",
        description="Maximum cyclomatic complexity",
        threshold=10.0,
        current_value=0.0,
        passed=False,
        verification_command="lizard -C 10 src/",
        remediation_guidance="Refactor complex functions or document justification",
        exception_conditions=["Complexity justified in complexity-justification.md"]
    ),
    # ... 5 more gates
]
```

**Gate Evaluation During Validation**:
```python
class ValidationRunner:
    def evaluate_gates(self, project_root: Path) -> list[ReadinessGate]:
        """Run all gates and return results."""
        gates = []

        for gate_template in READINESS_GATES:
            gate = copy.deepcopy(gate_template)

            # Run verification command
            result = subprocess.run(
                gate.verification_command.split(),
                cwd=project_root,
                capture_output=True
            )

            # Parse result and update current_value
            gate.current_value = self._parse_verification_result(gate.name, result)
            gate.evaluate()

            gates.append(gate)

        return gates
```

**7 Mandatory Gates**:
1. Test Coverage ≥60%
2. Cyclomatic Complexity <10
3. Structure follows ecosystem conventions
4. Build passes cleanly (zero errors, <10 warnings)
5. Public APIs documented
6. Zero critical security vulnerabilities
7. Git hygiene (no secrets, no large binaries)

---

### 6. GraduationReport

**Purpose**: Summarizes entire brownfield transition journey including before/after metrics, changes made, and archived artifacts.

**Storage**: `brownfield-graduation-report.md` (project root)

**Python Dataclass**:

```python
@dataclass
class StructuralChange:
    """Documents a structural modification."""
    category: str  # "file_move" | "directory_create" | "config_add"
    description: str
    files_affected: list[Path]
    git_commit_sha: str
    timestamp: datetime

@dataclass
class TestImprovement:
    """Documents test infrastructure improvement."""
    module: str
    baseline_coverage: float
    final_coverage: float
    tests_added: int
    framework: str  # "pytest" | "jest" | "cargo test"

@dataclass
class SecurityFix:
    """Documents security vulnerability remediation."""
    vulnerability_id: str
    severity: str
    description: str
    fix_applied: str
    verification: str

@dataclass
class GraduationReport:
    """Complete brownfield transition summary."""
    project_name: str
    graduated_at: datetime

    baseline_metrics: Metrics
    final_metrics: Metrics

    structural_changes: list[StructuralChange]
    test_improvements: list[TestImprovement]
    security_fixes: list[SecurityFix]

    time_spent: dict[Phase, int]  # Seconds spent in each phase
    total_commits: int

    archived_artifacts: list[Path]  # Brownfield artifacts archived
    speckit_constitution: Path  # Generated constitution location

    readiness_gates: list[ReadinessGate]

    def to_markdown(self) -> str:
        """Generate comprehensive graduation report."""
        md = f"# Brownfield Graduation Report: {self.project_name}\n\n"
        md += f"**Graduated**: {self.graduated_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        md += "## Metrics Improvement\n\n"
        md += "| Metric | Baseline | Final | Delta |\n"
        md += "|--------|----------|-------|-------|\n"
        md += f"| Test Coverage | {self.baseline_metrics.test_coverage:.1%} | {self.final_metrics.test_coverage:.1%} | +{(self.final_metrics.test_coverage - self.baseline_metrics.test_coverage):.1%} |\n"
        md += f"| Avg Complexity | {self.baseline_metrics.complexity_avg:.1f} | {self.final_metrics.complexity_avg:.1f} | {self.final_metrics.complexity_avg - self.baseline_metrics.complexity_avg:+.1f} |\n"
        # ... more metrics

        md += "\n## Structural Changes\n\n"
        for change in self.structural_changes:
            md += f"- **{change.category}**: {change.description} ({change.git_commit_sha[:7]})\n"

        md += "\n## Test Infrastructure\n\n"
        for improvement in self.test_improvements:
            md += f"- **{improvement.module}**: {improvement.baseline_coverage:.1%} → {improvement.final_coverage:.1%} (+{improvement.tests_added} tests)\n"

        md += "\n## Readiness Gates\n\n"
        for gate in self.readiness_gates:
            status = "✅" if gate.passed else "❌"
            md += f"- {status} **{gate.name}**: {gate.current_value:.2f} (threshold: {gate.threshold:.2f})\n"

        md += f"\n## Next Steps\n\n"
        md += f"Your project has graduated from BrownKit and is now Speckit-ready!\n\n"
        md += f"1. Review generated Speckit constitution: `{self.speckit_constitution}`\n"
        md += f"2. Start spec-driven development: `/speckit.specify \"your feature description\"`\n"
        md += f"3. Archived brownfield artifacts: `.specify/memory/brownfield-archive/`\n"

        return md
```

**Graduation Artifacts Created**:
- `brownfield-graduation-report.md` (root directory)
- `.specify/memory/constitution.md` (Speckit constitution)
- `.specify/memory/brownfield-archive/` (archived assessment, decisions, checkpoints)
- `.specify/templates/` (spec, plan, tasks templates based on detected tech stack)

---

## Relationships and Workflows

### Assessment → State Initialization

```python
def initialize_state_from_assessment(report: AssessmentReport) -> BrownfieldState:
    """Create initial brownfield state from assessment results."""
    return BrownfieldState(
        project_root=report.project_root,
        current_phase=Phase.STRUCTURE,
        baseline_metrics=report.baseline_metrics,
        current_metrics=report.baseline_metrics,
        phase_timestamps={"assessment": report.assessed_at}
    )
```

### Checkpoint → State Recovery

```python
def recover_from_checkpoint(checkpoint: PhaseCheckpoint, state: BrownfieldState) -> BrownfieldState:
    """Resume workflow from checkpoint after interruption."""
    state.current_phase = checkpoint.phase
    return state
```

### State → Validation → Graduation

```python
def validate_and_graduate(state: BrownfieldState) -> GraduationReport:
    """Validate readiness gates and generate graduation report."""
    gates = evaluate_all_gates(state.current_metrics)

    if not all(gate.passed for gate in gates):
        raise ValidationFailedError("Not all gates passed")

    return GraduationReport(
        baseline_metrics=state.baseline_metrics,
        final_metrics=state.current_metrics,
        readiness_gates=gates,
        # ... populate other fields
    )
```

## JSON Schema Examples

### brownfield-state.json

```json
{
  "schema_version": "1.0",
  "project_root": "/home/user/project",
  "current_phase": "testing",
  "baseline_metrics": {
    "test_coverage": 0.0,
    "complexity_avg": 15.2,
    "critical_vulnerabilities": 2
  },
  "current_metrics": {
    "test_coverage": 0.45,
    "complexity_avg": 12.1,
    "critical_vulnerabilities": 1
  },
  "phase_timestamps": {
    "assessment": "2025-10-12T14:00:00Z",
    "structure_start": "2025-10-12T14:30:00Z",
    "structure_complete": "2025-10-12T15:00:00Z",
    "testing_start": "2025-10-12T15:15:00Z"
  },
  "re_entry_events": [],
  "graduated": false
}
```

### brownfield-checkpoint.json

```json
{
  "phase": "structure",
  "started_at": "2025-10-12T14:30:00Z",
  "last_checkpoint_at": "2025-10-12T14:45:00Z",
  "interrupted": false,
  "tasks": [
    {
      "task_id": "create_src_dir",
      "description": "Create src/ directory",
      "completed": true,
      "completed_at": "2025-10-12T14:32:00Z",
      "git_commit_sha": "abc123def"
    },
    {
      "task_id": "move_main_py",
      "description": "Move main.py to src/",
      "completed": true,
      "completed_at": "2025-10-12T14:35:00Z",
      "git_commit_sha": "def456ghi"
    },
    {
      "task_id": "update_imports",
      "description": "Update import paths",
      "completed": false,
      "completed_at": null,
      "git_commit_sha": null
    }
  ]
}
```
