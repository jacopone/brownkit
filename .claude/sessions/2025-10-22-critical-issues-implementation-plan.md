---
status: active
created: 2025-10-22
updated: 2025-10-22
type: planning
lifecycle: ephemeral
---

# BrownKit Critical Issues - Implementation Plan

**Created**: 2025-10-22
**Priority**: CRITICAL
**Estimated Total Effort**: 12-16 hours
**Target Completion**: 2-3 days

This plan addresses the critical issues identified during the comprehensive code review on 2025-10-22.

---

## 📊 Issue Summary

| Issue | Priority | Impact | Effort | Status |
|-------|----------|--------|--------|--------|
| Task Model Inconsistency | 🔴 CRITICAL | Runtime failure in checkpoint save | 3-4h | Pending |
| Phase Validation Not Implemented | 🔴 CRITICAL | Illegal phase transitions allowed | 2-3h | Pending |
| Missing Unit Tests | 🔴 CRITICAL | No safety net for changes | 6-8h | Pending |
| State File Naming | 🟡 HIGH | Speckit compatibility | 1h | Pending |
| Remediation Phase Split | 🟡 HIGH | Workflow coherence | 2h | Pending |
| Progress Indicators | 🟡 HIGH | UX improvement | 1-2h | Pending |

---

## 🔴 CRITICAL ISSUE 1: Task Model Inconsistency

### Problem Statement

There's a schema mismatch between `checkpoint.Task` and the Task objects created by orchestrators:

**Checkpoint Model** (`src/brownfield/models/checkpoint.py`):
```python
@dataclass
class Task:
    task_id: str        # ❌ Orchestrators use .name
    description: str
    completed: bool     # ❌ Orchestrators also have .status
```

**Orchestrator Usage** (`src/brownfield/orchestrator/remediation.py`):
```python
Task(
    name="install_pytest",              # ❌ Should be task_id
    description="Install pytest framework",
    phase=Phase.TESTING,                # ❌ Not in checkpoint model
    estimated_minutes=30,               # ❌ Not in checkpoint model
    completed=True
)
```

**Impact**: Checkpoint serialization will fail with `AttributeError: 'Task' object has no attribute 'task_id'`

---

### Solution: Unify Task Model

**Step 1**: Update `src/brownfield/models/checkpoint.py`

```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum

@dataclass
class Task:
    """Unified task model for orchestrators and checkpoint persistence."""

    # Core identification
    task_id: str  # Unique identifier (e.g., "install_pytest")
    description: str  # Human-readable description

    # Execution context
    phase: Phase  # STRUCTURE, TESTING, or QUALITY
    estimated_minutes: int  # Time estimate for planning

    # Status tracking
    completed: bool = False
    status: Optional[str] = None  # "pending", "in_progress", "completed", "failed"
    error_message: Optional[str] = None  # Captured error if task failed

    # Optional metadata
    dependencies: list[str] = None  # task_ids that must complete first
    checkpoint_data: dict = None  # Phase-specific recovery data

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.checkpoint_data is None:
            self.checkpoint_data = {}

        # Auto-set status from completed if not provided
        if self.status is None:
            self.status = "completed" if self.completed else "pending"
```

**Step 2**: Update all orchestrator usages

**File**: `src/brownfield/orchestrator/remediation.py`

**Before**:
```python
tasks = [
    Task(
        name="analyze_structure",  # ❌ Wrong attribute
        description="...",
        phase=Phase.STRUCTURE,
        estimated_minutes=5
    )
]
```

**After**:
```python
tasks = [
    Task(
        task_id="analyze_structure",  # ✅ Correct attribute
        description="...",
        phase=Phase.STRUCTURE,
        estimated_minutes=5,
        status="pending"
    )
]
```

**Step 3**: Update checkpoint serialization

**File**: `src/brownfield/state/checkpoint_manager.py` (inferred location)

```python
def save_checkpoint(self, checkpoint: Checkpoint) -> Path:
    """Save checkpoint to disk."""
    checkpoint_dict = {
        "phase": checkpoint.phase.value,
        "tasks": [
            {
                "task_id": task.task_id,  # ✅ Updated
                "description": task.description,
                "phase": task.phase.value,
                "estimated_minutes": task.estimated_minutes,
                "completed": task.completed,
                "status": task.status,
                "error_message": task.error_message,
                "dependencies": task.dependencies,
                "checkpoint_data": task.checkpoint_data
            }
            for task in checkpoint.tasks
        ],
        "current_task_index": checkpoint.current_task_index,
        "created_at": checkpoint.created_at.isoformat(),
        "updated_at": checkpoint.updated_at.isoformat()
    }

    # Write atomically
    temp_path = self.checkpoint_path.with_suffix(".tmp")
    with open(temp_path, "w") as f:
        json.dump(checkpoint_dict, f, indent=2)
    temp_path.rename(self.checkpoint_path)

    return self.checkpoint_path
```

---

### Testing Requirements

**File**: `tests/unit/models/test_checkpoint.py` (NEW)

```python
import pytest
from brownfield.models.checkpoint import Task, Checkpoint
from brownfield.models.state import Phase
from datetime import datetime

def test_task_creation_with_all_fields():
    """Test Task can be created with all fields."""
    task = Task(
        task_id="test_task",
        description="Test task description",
        phase=Phase.TESTING,
        estimated_minutes=30,
        completed=True,
        status="completed",
        error_message=None,
        dependencies=["dependency_task"],
        checkpoint_data={"key": "value"}
    )

    assert task.task_id == "test_task"
    assert task.completed is True
    assert task.status == "completed"
    assert len(task.dependencies) == 1

def test_task_status_auto_set_from_completed():
    """Test status is auto-set from completed if not provided."""
    task_pending = Task(
        task_id="pending_task",
        description="...",
        phase=Phase.TESTING,
        estimated_minutes=10
    )
    assert task_pending.status == "pending"

    task_completed = Task(
        task_id="completed_task",
        description="...",
        phase=Phase.TESTING,
        estimated_minutes=10,
        completed=True
    )
    assert task_completed.status == "completed"

def test_checkpoint_serialization():
    """Test checkpoint can be serialized and deserialized."""
    tasks = [
        Task(
            task_id=f"task_{i}",
            description=f"Task {i}",
            phase=Phase.TESTING,
            estimated_minutes=10 * i
        )
        for i in range(3)
    ]

    checkpoint = Checkpoint(
        phase=Phase.TESTING,
        tasks=tasks,
        current_task_index=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    # Test serialization (would need checkpoint_manager.save)
    # This validates the structure is correct
    checkpoint_dict = {
        "phase": checkpoint.phase.value,
        "tasks": [
            {
                "task_id": task.task_id,
                "description": task.description,
                "phase": task.phase.value,
                "estimated_minutes": task.estimated_minutes,
                "completed": task.completed,
                "status": task.status
            }
            for task in checkpoint.tasks
        ]
    }

    assert len(checkpoint_dict["tasks"]) == 3
    assert checkpoint_dict["tasks"][0]["task_id"] == "task_0"
```

---

### Migration Strategy

1. **Update model first**: Modify `checkpoint.py` with new unified Task model
2. **Search and replace**: Find all Task() instantiations
   ```bash
   rg "Task\(" src/brownfield/orchestrator/
   ```
3. **Update each file**: Change `name=` to `task_id=`
4. **Update serialization**: Modify checkpoint_manager.py
5. **Run tests**: Ensure no AttributeError exceptions
6. **Commit atomically**: Single commit with all changes

**Estimated Effort**: 3-4 hours

---

## 🔴 CRITICAL ISSUE 2: Phase Validation Not Implemented

### Problem Statement

**Current Code** (`src/brownfield/orchestrator/phase_machine.py:12`):
```python
def can_advance_to(self, next_phase: Phase) -> bool:
    """Check if can advance to next phase."""
    # TODO: Implement phase transition validation
    return True  # ❌ ALWAYS RETURNS TRUE - NO VALIDATION!
```

**Impact**: Could transition STRUCTURE → VALIDATION illegally, skipping TESTING and QUALITY phases.

---

### Solution: Implement Phase Transition Validation

**Step 1**: Define phase transition rules

```python
# src/brownfield/orchestrator/phase_machine.py

from enum import Enum
from typing import Dict, List, Optional
from brownfield.models.state import Phase, BrownfieldState

class PhaseOrchestrator:
    """Manages phase transitions and validation."""

    # Define allowed transitions as adjacency list
    PHASE_TRANSITIONS: Dict[Phase, List[Phase]] = {
        Phase.ASSESSMENT: [Phase.STRUCTURE],
        Phase.STRUCTURE: [Phase.TESTING],
        Phase.TESTING: [Phase.QUALITY],
        Phase.QUALITY: [Phase.VALIDATION],
        Phase.VALIDATION: [Phase.GRADUATED],
        Phase.GRADUATED: [Phase.STRUCTURE, Phase.TESTING, Phase.QUALITY]  # Re-entry
    }

    # Define requirements for each phase (gates that must pass)
    PHASE_REQUIREMENTS: Dict[Phase, List[str]] = {
        Phase.STRUCTURE: ["language_detected", "baseline_metrics_captured"],
        Phase.TESTING: ["structure_compliant"],
        Phase.QUALITY: ["test_coverage_min_60"],
        Phase.VALIDATION: ["linters_installed", "formatters_configured"],
        Phase.GRADUATED: ["all_gates_passed"]
    }

    def __init__(self, state_store: StateStore):
        self.state_store = state_store
        self.state = state_store.load() if state_store.exists() else None

    def can_advance_to(self, next_phase: Phase) -> tuple[bool, Optional[str]]:
        """Check if can advance to next phase.

        Returns:
            (can_advance, reason): Tuple of boolean and optional reason string
        """
        if self.state is None:
            return False, "No brownfield state found. Run 'brownfield assess' first."

        current_phase = self.state.current_phase

        # Check if transition is allowed
        allowed_transitions = self.PHASE_TRANSITIONS.get(current_phase, [])
        if next_phase not in allowed_transitions:
            return False, (
                f"Cannot transition from {current_phase.value} to {next_phase.value}. "
                f"Allowed transitions: {', '.join(p.value for p in allowed_transitions)}"
            )

        # Check if requirements are met
        requirements = self.PHASE_REQUIREMENTS.get(next_phase, [])
        unmet_requirements = self._check_requirements(requirements)

        if unmet_requirements:
            return False, (
                f"Cannot advance to {next_phase.value}. "
                f"Unmet requirements: {', '.join(unmet_requirements)}"
            )

        return True, None

    def _check_requirements(self, requirements: List[str]) -> List[str]:
        """Check which requirements are not met.

        Returns:
            List of unmet requirement names
        """
        unmet = []

        for req in requirements:
            if req == "language_detected":
                if not self.state.language:
                    unmet.append(req)

            elif req == "baseline_metrics_captured":
                if not self.state.baseline_metrics:
                    unmet.append(req)

            elif req == "structure_compliant":
                # Check if structure phase completed successfully
                phase_history = getattr(self.state, 'phase_history', [])
                if not any(p.phase == Phase.STRUCTURE and p.completed for p in phase_history):
                    unmet.append(req)

            elif req == "test_coverage_min_60":
                metrics = self.state.current_metrics or self.state.baseline_metrics
                if not metrics or metrics.test_coverage < 0.6:
                    unmet.append(req)

            elif req == "linters_installed":
                # Check if quality phase installed linters
                # This would need implementation-specific logic
                pass  # Placeholder

            elif req == "all_gates_passed":
                # Check if all 7 gates passed in validation
                if not hasattr(self.state, 'validation_gates'):
                    unmet.append(req)
                elif not all(gate.passed for gate in self.state.validation_gates):
                    unmet.append(req)

        return unmet

    def advance_to(self, next_phase: Phase) -> BrownfieldState:
        """Advance to next phase (with validation).

        Raises:
            ValueError: If transition is not allowed
        """
        can_advance, reason = self.can_advance_to(next_phase)

        if not can_advance:
            raise ValueError(reason)

        # Update state
        self.state.current_phase = next_phase
        self.state_store.save(self.state)

        return self.state
```

**Step 2**: Update orchestrators to use validated transitions

**File**: `src/brownfield/orchestrator/remediation.py`

**Before**:
```python
def execute(phase: Phase) -> RemediationResult:
    # No validation, just execute
    if phase == Phase.STRUCTURE:
        _remediate_structure()
```

**After**:
```python
def execute(phase: Phase) -> RemediationResult:
    # Validate transition first
    phase_orchestrator = PhaseOrchestrator(state_store)
    can_advance, reason = phase_orchestrator.can_advance_to(phase)

    if not can_advance:
        raise ValueError(f"Cannot execute {phase.value} phase: {reason}")

    # Now safe to execute
    if phase == Phase.STRUCTURE:
        _remediate_structure()
```

---

### Testing Requirements

**File**: `tests/unit/orchestrator/test_phase_machine.py` (NEW)

```python
import pytest
from brownfield.orchestrator.phase_machine import PhaseOrchestrator
from brownfield.models.state import Phase, BrownfieldState, Metrics
from brownfield.state.state_store import StateStore
from pathlib import Path

@pytest.fixture
def state_store(tmp_path):
    """Create temporary state store."""
    return StateStore(tmp_path)

@pytest.fixture
def assessment_state(state_store):
    """Create state in ASSESSMENT phase."""
    state = BrownfieldState(
        project_root=Path("/tmp/test"),
        current_phase=Phase.ASSESSMENT,
        language="python",
        baseline_metrics=Metrics(
            test_coverage=0.0,
            complexity_avg=15.0,
            # ... other metrics
        )
    )
    state_store.save(state)
    return state

def test_can_advance_from_assessment_to_structure(state_store, assessment_state):
    """Test valid transition: ASSESSMENT → STRUCTURE."""
    orchestrator = PhaseOrchestrator(state_store)
    can_advance, reason = orchestrator.can_advance_to(Phase.STRUCTURE)

    assert can_advance is True
    assert reason is None

def test_cannot_advance_from_assessment_to_quality(state_store, assessment_state):
    """Test invalid transition: ASSESSMENT → QUALITY (skip phases)."""
    orchestrator = PhaseOrchestrator(state_store)
    can_advance, reason = orchestrator.can_advance_to(Phase.QUALITY)

    assert can_advance is False
    assert "Cannot transition" in reason
    assert "QUALITY" in reason

def test_cannot_advance_without_requirements(state_store):
    """Test transition blocked by unmet requirements."""
    # State with no language detection
    state = BrownfieldState(
        project_root=Path("/tmp/test"),
        current_phase=Phase.ASSESSMENT,
        language=None,  # ❌ Missing requirement
        baseline_metrics=None
    )
    state_store.save(state)

    orchestrator = PhaseOrchestrator(state_store)
    can_advance, reason = orchestrator.can_advance_to(Phase.STRUCTURE)

    assert can_advance is False
    assert "Unmet requirements" in reason
    assert "language_detected" in reason

def test_graduated_can_reenter_any_phase(state_store):
    """Test graduated projects can re-enter any remediation phase."""
    state = BrownfieldState(
        project_root=Path("/tmp/test"),
        current_phase=Phase.GRADUATED,
        language="python",
        baseline_metrics=Metrics(test_coverage=0.7, complexity_avg=8.0)
    )
    state_store.save(state)

    orchestrator = PhaseOrchestrator(state_store)

    # Should allow re-entry to STRUCTURE, TESTING, or QUALITY
    for phase in [Phase.STRUCTURE, Phase.TESTING, Phase.QUALITY]:
        can_advance, _ = orchestrator.can_advance_to(phase)
        assert can_advance is True, f"Should allow re-entry to {phase.value}"

def test_advance_to_raises_on_invalid_transition(state_store, assessment_state):
    """Test advance_to() raises ValueError on invalid transition."""
    orchestrator = PhaseOrchestrator(state_store)

    with pytest.raises(ValueError, match="Cannot transition"):
        orchestrator.advance_to(Phase.GRADUATED)  # Skip all phases
```

---

### Migration Strategy

1. **Implement phase_machine.py**: Add full validation logic
2. **Update all orchestrators**: Add validation checks before execute()
3. **Update CLI commands**: Show helpful error messages on invalid transitions
4. **Test extensively**: Ensure all transitions work correctly
5. **Document transitions**: Add phase transition diagram to docs

**Estimated Effort**: 2-3 hours

---

## 🔴 CRITICAL ISSUE 3: Missing Unit Tests

### Problem Statement

**Current State**: Zero unit tests for orchestrators
**Impact**: No safety net for refactoring, high risk of regressions

---

### Solution: Comprehensive Test Suite

**Test Coverage Goals**:
- ✅ All 5 orchestrators (assessment, plan, remediation, validation, graduation)
- ✅ Phase transition validation
- ✅ Checkpoint save/load
- ✅ State persistence
- ✅ Display utilities

**Directory Structure**:
```
tests/
├── unit/
│   ├── orchestrator/
│   │   ├── test_assessment.py         (NEW - 150 lines)
│   │   ├── test_plan.py                (NEW - 200 lines)
│   │   ├── test_remediation.py         (NEW - 250 lines)
│   │   ├── test_validation.py          (NEW - 200 lines)
│   │   ├── test_graduation.py          (NEW - 150 lines)
│   │   └── test_phase_machine.py       (NEW - 150 lines)
│   ├── models/
│   │   ├── test_checkpoint.py          (NEW - 100 lines)
│   │   └── test_orchestrator_models.py (NEW - 100 lines)
│   ├── state/
│   │   └── test_state_store.py         (NEW - 150 lines)
│   └── cli/
│       └── test_slash_commands.py      (NEW - 200 lines)
└── integration/
    ├── test_workflow_full.py           (NEW - 300 lines)
    └── test_checkpoint_recovery.py     (NEW - 200 lines)
```

---

### Example Test: Assessment Orchestrator

**File**: `tests/unit/orchestrator/test_assessment.py` (NEW)

```python
import pytest
from pathlib import Path
from brownfield.orchestrator.assessment import AssessmentOrchestrator
from brownfield.models.state import Phase, BrownfieldState
from brownfield.state.state_store import StateStore

@pytest.fixture
def python_project(tmp_path):
    """Create a minimal Python project for testing."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()

    # Create Python files
    (project_root / "main.py").write_text("print('Hello')")
    (project_root / "requirements.txt").write_text("click>=8.0")

    return project_root

@pytest.fixture
def state_store(tmp_path):
    """Create state store in temp directory."""
    memory_dir = tmp_path / ".specify" / "memory"
    memory_dir.mkdir(parents=True)
    return StateStore(memory_dir)

def test_assessment_detects_python_language(python_project, state_store):
    """Test language detection works correctly."""
    orchestrator = AssessmentOrchestrator(
        project_root=python_project,
        language_override=None,
        quick_mode=True
    )

    result = orchestrator.execute()

    assert result.language_detection.detected_language == "python"
    assert result.language_detection.confidence > 0.8

def test_assessment_creates_initial_state(python_project, state_store):
    """Test initial state is created correctly."""
    orchestrator = AssessmentOrchestrator(
        project_root=python_project,
        language_override=None,
        quick_mode=True
    )

    result = orchestrator.execute()

    # Load state and verify
    state = state_store.load()
    assert state.current_phase == Phase.ASSESSMENT
    assert state.language == "python"
    assert state.baseline_metrics is not None

def test_assessment_detects_regression(python_project, state_store):
    """Test regression detection for graduated projects."""
    # Create graduated state with good metrics
    graduated_state = BrownfieldState(
        project_root=python_project,
        current_phase=Phase.GRADUATED,
        language="python",
        baseline_metrics=Metrics(test_coverage=0.7, complexity_avg=8.0)
    )
    state_store.save(graduated_state)

    # Simulate degraded metrics (coverage dropped)
    # In real scenario, this would be detected from actual codebase
    # For test, we'd mock the metrics collection

    orchestrator = AssessmentOrchestrator(
        project_root=python_project,
        language_override=None,
        quick_mode=True
    )

    # Mock metrics to show regression
    with patch.object(orchestrator, '_collect_metrics') as mock_metrics:
        mock_metrics.return_value = Metrics(
            test_coverage=0.45,  # ❌ Below 0.6 threshold
            complexity_avg=8.0
        )

        result = orchestrator.execute()

    assert result.regression is not None
    assert result.regression.regression_type == "test_coverage"
    assert result.regression.re_entry_phase == Phase.TESTING

def test_assessment_report_created(python_project, state_store):
    """Test assessment report is written to disk."""
    orchestrator = AssessmentOrchestrator(
        project_root=python_project,
        language_override=None,
        quick_mode=True
    )

    result = orchestrator.execute()

    assert result.report_path.exists()
    content = result.report_path.read_text()
    assert "Assessment Report" in content
    assert "python" in content.lower()

@pytest.mark.parametrize("language,expected_files", [
    ("python", ["setup.py", "requirements.txt", "pyproject.toml"]),
    ("javascript", ["package.json", "package-lock.json"]),
    ("rust", ["Cargo.toml", "Cargo.lock"]),
    ("go", ["go.mod", "go.sum"])
])
def test_language_detection_heuristics(tmp_path, language, expected_files):
    """Test language detection uses correct file heuristics."""
    project_root = tmp_path / f"{language}_project"
    project_root.mkdir()

    # Create language-specific files
    for filename in expected_files[:1]:  # Create at least one
        (project_root / filename).write_text("# Test content")

    orchestrator = AssessmentOrchestrator(
        project_root=project_root,
        language_override=None,
        quick_mode=True
    )

    result = orchestrator.execute()
    assert result.language_detection.detected_language == language
```

---

### Example Test: Remediation Orchestrator

**File**: `tests/unit/orchestrator/test_remediation.py` (NEW)

```python
import pytest
from brownfield.orchestrator.remediation import RemediationOrchestrator
from brownfield.models.state import Phase
from brownfield.models.checkpoint import Checkpoint

@pytest.fixture
def remediation_orchestrator(tmp_path, state_store):
    """Create remediation orchestrator with test state."""
    # Setup state in STRUCTURE phase
    state = BrownfieldState(
        project_root=tmp_path,
        current_phase=Phase.STRUCTURE,
        language="python"
    )
    state_store.save(state)

    return RemediationOrchestrator(
        project_root=tmp_path,
        phase=Phase.TESTING,
        auto_commit=False
    )

def test_remediation_creates_tasks(remediation_orchestrator):
    """Test remediation generates appropriate tasks."""
    result = remediation_orchestrator.execute()

    assert len(result.tasks) > 0
    assert all(isinstance(task, Task) for task in result.tasks)

    # Check task structure
    first_task = result.tasks[0]
    assert first_task.task_id
    assert first_task.description
    assert first_task.phase == Phase.TESTING

def test_remediation_saves_checkpoint(remediation_orchestrator):
    """Test checkpoint is saved during execution."""
    result = remediation_orchestrator.execute()

    assert result.checkpoint_path is not None
    assert result.checkpoint_path.exists()

    # Verify checkpoint can be loaded
    # (would need checkpoint manager)

def test_remediation_handles_task_failure(remediation_orchestrator):
    """Test failed tasks are tracked correctly."""
    # Mock a task that fails
    with patch.object(remediation_orchestrator, '_execute_task') as mock_exec:
        mock_exec.side_effect = Exception("Task failed")

        result = remediation_orchestrator.execute()

    assert len(result.failed_tasks) > 0
    failed_task = result.failed_tasks[0]
    assert failed_task.error_message is not None

def test_remediation_creates_commits_when_enabled(remediation_orchestrator):
    """Test git commits are created when auto_commit=True."""
    orchestrator = RemediationOrchestrator(
        project_root=remediation_orchestrator.project_root,
        phase=Phase.TESTING,
        auto_commit=True  # ✅ Enable commits
    )

    result = orchestrator.execute()

    # Verify commits were created
    assert len(result.commits) > 0
    # Would need git repo fixture to verify actual commits

@pytest.mark.parametrize("phase,expected_task_types", [
    (Phase.STRUCTURE, ["analyze_structure", "organize_directories"]),
    (Phase.TESTING, ["install_framework", "generate_tests"]),
    (Phase.QUALITY, ["install_linters", "configure_formatters"])
])
def test_remediation_phase_specific_tasks(phase, expected_task_types):
    """Test each phase generates appropriate tasks."""
    # Test that each phase has correct task types
    pass  # Would need full implementation
```

---

### Testing Strategy

**Phase 1: Core Models (2 hours)**
- Task model tests
- Checkpoint serialization tests
- State model tests

**Phase 2: Orchestrators (4 hours)**
- Assessment orchestrator (language detection, metrics, regression)
- Plan orchestrator (plan generation, estimates)
- Remediation orchestrator (task execution, checkpoints, commits)
- Validation orchestrator (gate checking)
- Graduation orchestrator (constitution generation)

**Phase 3: State Management (1 hour)**
- State store (save, load, atomic writes)
- Phase machine (transitions, requirements)

**Phase 4: Integration Tests (2 hours)**
- Full workflow: assess → plan → remediate → validate → graduate
- Checkpoint recovery (interrupt and resume)
- Regression re-entry

**Total Estimated Effort**: 6-8 hours

---

## 🟡 HIGH-PRIORITY ISSUE 4: State File Naming

### Problem Statement

**Current**: `brownfield-state.json`
**Speckit Standard**: `state.json` with workflow discriminator

**Impact**: Moderate - state files discoverable but not Speckit-compatible

---

### Solution: Rename to `state.json` with Workflow Field

**Step 1**: Update state model

```python
# src/brownfield/models/state.py

@dataclass
class BrownfieldState:
    """Project state for brownfield workflow."""

    # Speckit compatibility
    workflow: str = "brownfield"  # ✅ NEW - Workflow discriminator
    version: str = "1.0"          # ✅ NEW - Schema version

    # Existing fields...
    project_root: Path
    current_phase: Phase
    language: Optional[str] = None
    # ...
```

**Step 2**: Update state store paths

```python
# src/brownfield/state/state_store.py

class StateStore:
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        # OLD: self.state_path = memory_dir / "brownfield-state.json"
        self.state_path = memory_dir / "state.json"  # ✅ NEW
```

**Step 3**: Migration utility

```python
# src/brownfield/state/migrate.py (NEW)

def migrate_state_file(memory_dir: Path) -> bool:
    """Migrate old brownfield-state.json to state.json."""
    old_path = memory_dir / "brownfield-state.json"
    new_path = memory_dir / "state.json"

    if not old_path.exists():
        return False  # Nothing to migrate

    if new_path.exists():
        # Backup new file
        shutil.copy(new_path, new_path.with_suffix(".bak"))

    # Load old state
    with open(old_path) as f:
        state_dict = json.load(f)

    # Add workflow field
    state_dict["workflow"] = "brownfield"
    state_dict["version"] = "1.0"

    # Write to new location
    with open(new_path, "w") as f:
        json.dump(state_dict, f, indent=2)

    # Archive old file
    archive_path = memory_dir / f"brownfield-state.json.archived_{datetime.now().isoformat()}"
    shutil.move(old_path, archive_path)

    return True
```

**Step 4**: Auto-migrate on first run

```python
# In state_store.py __init__

def __init__(self, memory_dir: Path):
    self.memory_dir = memory_dir
    self.state_path = memory_dir / "state.json"

    # Auto-migrate if needed
    from brownfield.state.migrate import migrate_state_file
    migrate_state_file(memory_dir)
```

**Estimated Effort**: 1 hour

---

## 🟡 HIGH-PRIORITY ISSUE 5: Split Remediation Phase

### Problem Statement

**Current Workflow**:
```
assess → plan → remediate (combines tasks + implement) → validate → graduate
```

**Speckit Workflow**:
```
specify → plan → tasks → implement
```

**Issue**: `remediate` combines task generation and implementation, reducing granularity

---

### Solution: Split into `tasks` and `remediate` Commands

**New Workflow**:
```
assess → plan → tasks → remediate → validate → graduate
```

**Step 1**: Create new `tasks` command

```python
# src/brownfield/cli/slash/tasks.py (NEW)

@click.command("brownfield.tasks")
@click.option("--phase", type=click.Choice(["structure", "testing", "quality"]))
@click.option("--json", "output_json", is_flag=True)
def tasks_workflow(phase: str, output_json: bool):
    """Generate actionable task list for remediation phase.

    Equivalent to Speckit's task breakdown phase.
    """
    project_root = Path.cwd()

    # Load state
    state_store = StateStore(project_root / ".specify" / "memory")
    if not state_store.exists():
        console.print("[red]No brownfield state found. Run 'brownfield brownfield.assess' first.")
        sys.exit(1)

    # Generate tasks without executing
    orchestrator = TasksOrchestrator(
        project_root=project_root,
        phase=Phase[phase.upper()],
        generate_only=True  # ✅ Don't execute, just plan
    )

    result = orchestrator.execute()

    if output_json:
        console.print(json.dumps({
            "phase": phase,
            "tasks": [
                {
                    "task_id": task.task_id,
                    "description": task.description,
                    "estimated_minutes": task.estimated_minutes,
                    "dependencies": task.dependencies
                }
                for task in result.tasks
            ],
            "total_estimated_hours": sum(t.estimated_minutes for t in result.tasks) / 60
        }, indent=2))
    else:
        display_tasks(result.tasks, phase)
```

**Step 2**: Update `remediate` to execute tasks

```python
# src/brownfield/cli/slash/remediate.py (UPDATE)

@click.command("brownfield.remediate")
@click.option("--phase", type=click.Choice(["structure", "testing", "quality"]))
@click.option("--no-commit", is_flag=True)
def remediate_workflow(phase: str, no_commit: bool):
    """Execute remediation tasks for specified phase.

    Runs tasks generated by 'brownfield.tasks' command.
    """
    # Load existing tasks (generated by tasks command)
    tasks_path = project_root / ".specify" / "memory" / f"{phase}-tasks.json"

    if not tasks_path.exists():
        console.print(f"[yellow]No tasks found for {phase} phase.")
        console.print(f"[yellow]Run 'brownfield brownfield.tasks --phase {phase}' first.")
        sys.exit(1)

    # Execute tasks
    orchestrator = RemediationOrchestrator(
        project_root=project_root,
        phase=Phase[phase.upper()],
        auto_commit=not no_commit,
        task_file=tasks_path  # ✅ Load pre-generated tasks
    )

    result = orchestrator.execute()
    display_remediation_results(result)
```

**Step 3**: Register new command

```python
# src/brownfield/cli/commands.py

from brownfield.cli.slash.tasks import tasks_workflow

# Add to CLI group
cli.add_command(tasks_workflow)
```

**Estimated Effort**: 2 hours

---

## 🟡 HIGH-PRIORITY ISSUE 6: Add Progress Indicators

### Problem Statement

Long-running operations (assessment, remediation) provide no progress feedback.

**Impact**: Poor UX, users don't know if tool is working

---

### Solution: Rich Progress Bars

**Step 1**: Add progress tracking to orchestrators

```python
# src/brownfield/orchestrator/remediation.py

from rich.progress import Progress, TaskID

def execute(self) -> RemediationResult:
    """Execute remediation with progress tracking."""

    tasks = self._generate_tasks()

    with Progress() as progress:
        main_task = progress.add_task(
            f"[cyan]Remediating {self.phase.value}...",
            total=len(tasks)
        )

        for task in tasks:
            progress.update(main_task, description=f"[cyan]{task.description}")

            try:
                self._execute_task(task)
                task.completed = True
            except Exception as e:
                task.error_message = str(e)

            progress.advance(main_task)

    return RemediationResult(...)
```

**Step 2**: Add subtask progress

```python
def _execute_task(self, task: Task, progress: Progress, parent_task: TaskID):
    """Execute single task with sub-progress."""

    subtask = progress.add_task(
        f"  [dim]{task.description}[/dim]",
        total=100
    )

    # Update progress as task executes
    progress.update(subtask, advance=25)  # Started
    # ... do work ...
    progress.update(subtask, advance=50)  # Halfway
    # ... more work ...
    progress.update(subtask, completed=100)  # Done
```

**Estimated Effort**: 1-2 hours

---

## 📋 Implementation Timeline

### Day 1 (6-8 hours)

**Morning (3-4h)**:
- ✅ Fix Task model inconsistency
- ✅ Update all orchestrator usages
- ✅ Update checkpoint serialization
- ✅ Write Task model tests

**Afternoon (3-4h)**:
- ✅ Implement phase validation logic
- ✅ Write phase transition tests
- ✅ Update orchestrators to use validation

### Day 2 (6-8 hours)

**Morning (3-4h)**:
- ✅ Write assessment orchestrator tests
- ✅ Write remediation orchestrator tests
- ✅ Write validation orchestrator tests

**Afternoon (3-4h)**:
- ✅ Rename state file + migration utility
- ✅ Split remediation into tasks + remediate
- ✅ Add progress indicators

### Day 3 (Optional - polish)

- ✅ Integration tests (full workflow)
- ✅ Checkpoint recovery tests
- ✅ Documentation updates
- ✅ Final validation run

---

## ✅ Validation Checklist

Before considering issues resolved:

- [ ] All tests pass (`pytest tests/ --cov=src/brownfield`)
- [ ] Coverage >= 70% for orchestrator layer
- [ ] No AttributeError exceptions in checkpoint save/load
- [ ] Phase transitions validated (no illegal jumps)
- [ ] State file migrated to `state.json` format
- [ ] `brownfield.tasks` command works
- [ ] Progress indicators show for long operations
- [ ] Integration test: full workflow assess → graduate
- [ ] Documentation updated with new commands
- [ ] Devenv `check-all` passes

---

## 🚀 Post-Implementation

After all critical issues resolved:

1. **Run self-assessment**:
   ```bash
   brownfield brownfield.assess
   ```

2. **Validate quality gates**:
   ```bash
   brownfield brownfield.validate
   ```

3. **Create release candidate**:
   ```bash
   git tag -a v0.2.0-rc1 -m "Critical fixes + test coverage"
   ```

4. **Test with fixture projects**:
   ```bash
   ./tests/fixtures/run_all_fixtures.sh
   ```

5. **Update CHANGELOG.md**:
   - Document breaking changes (state file renamed)
   - Document new commands (brownfield.tasks)
   - Document fixed bugs

---

## 📞 Support

**Questions or blockers?**
- Refer to `.claude/sessions/2025-10-22-dual-interface-implementation.md` for architecture context
- Check `docs/testing-guide.md` for test patterns
- Review `src/brownfield/models/` for data contracts

**Next Session**:
- Continue from this plan
- Update TODO list as issues are resolved
- Document any new issues discovered during implementation
