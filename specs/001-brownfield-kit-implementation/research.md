# Research Document: Brownfield-Kit Implementation

**Feature**: Brownfield-Kit Implementation
**Created**: 2025-10-12
**Status**: Complete

## Technology Decisions

### Python 3.11+ as Foundation

**Decision**: Use Python 3.11+ as the implementation language for Brownfield-Kit.

**Rationale**:
- Native support for type hints and pattern matching improves code clarity
- Rich ecosystem of code analysis tools (lizard, radon, bandit)
- Cross-platform compatibility (Linux, macOS, Windows)
- Existing Speckit infrastructure assumes Python availability
- Easy subprocess integration for calling language-specific tools

**Alternatives Considered**:
- **Rust**: Better performance but limited ecosystem for code analysis tools; would require FFI bindings for many operations
- **Go**: Good CLI tooling but less mature static analysis libraries
- **Node.js**: Strong JavaScript ecosystem but poor support for Python/Rust analysis

**Risks**: Requires Python 3.11+ installation on user systems (mitigation: document prerequisite clearly in README)

### Click vs Argparse for CLI Framework

**Decision**: Use `click` for CLI command definitions.

**Rationale**:
- Declarative syntax with decorators improves readability (`@click.command()`)
- Automatic help text generation from docstrings
- Built-in support for nested command groups (`/brownfield.assess`, `/brownfield.structure`)
- Rich parameter validation and type conversion
- Better error messages for invalid inputs
- Industry standard for complex CLI tools (e.g., Flask, Black, Ruff)

**Alternatives Considered**:
- **argparse** (stdlib): More verbose, requires manual help text formatting, no decorator syntax
- **typer**: Newer library with type hints, but less mature ecosystem and documentation

**Implementation Pattern**:
```python
@click.group()
def brownfield():
    """Brownfield-Kit: AI-driven codebase transition workflow."""
    pass

@brownfield.command('assess')
@click.option('--quick/--full', default=True, help='Analysis mode')
@click.option('--output', type=click.Path(), help='Report output path')
def assess(quick: bool, output: str):
    """Run codebase assessment and generate baseline metrics."""
    pass
```

### GitPython for Git Operations

**Decision**: Use `gitpython` library for git repository manipulation.

**Rationale**:
- High-level Python API for git operations (commit, revert, branch management)
- Avoids subprocess parsing fragility (`subprocess.run(['git', 'commit', ...])`)
- Better error handling and exception types
- Programmatic access to repository state (current branch, dirty files, remotes)
- Widely used and maintained (>10M downloads/month)

**Alternatives Considered**:
- **subprocess + git CLI**: More fragile (output parsing varies by git version), harder to test
- **pygit2** (libgit2 bindings): C dependency complicates installation, overkill for our needs

**Implementation Pattern**:
```python
from git import Repo

def safe_commit(repo: Repo, message: str, files: list[str]):
    """Create atomic commit with automatic rollback on build failure."""
    try:
        repo.index.add(files)
        commit = repo.index.commit(message)
        if not verify_build(repo):
            repo.git.revert(commit.hexsha, no_edit=True)
            raise BuildFailureError(f"Reverted {commit.hexsha[:7]}")
        return commit
    except GitCommandError as e:
        raise GitOperationError(f"Commit failed: {e}")
```

**Trade-off**: Adds external dependency but improves reliability and testability.

## Plugin Architecture Best Practices

### Language Handler Base Class

**Decision**: Use abstract base class (`abc.ABC`) for plugin interface with mandatory methods for detection, structure, testing, and quality.

**Pattern**:
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class DetectionResult:
    language: str
    confidence: float  # 0.0-1.0
    version: str | None
    framework: str | None

class LanguageHandler(ABC):
    """Base class for language-specific brownfield operations."""

    @abstractmethod
    def detect(self, project_root: Path) -> DetectionResult | None:
        """Detect language/framework from project files."""
        pass

    @abstractmethod
    def get_standard_structure(self) -> dict[str, list[str]]:
        """Return expected directory structure."""
        pass

    @abstractmethod
    def bootstrap_tests(self, project_root: Path) -> TestSetupResult:
        """Add test framework and generate initial tests."""
        pass

    @abstractmethod
    def install_quality_gates(self, project_root: Path) -> QualitySetupResult:
        """Configure linters, formatters, and pre-commit hooks."""
        pass
```

**Benefits**:
- Enforces contract compliance at import time (missing methods cause errors)
- Type hints enable static analysis and IDE autocomplete
- Clear interface for adding new language support
- Testable via contract tests (`test_plugin_interface.py`)

### Plugin Registry Pattern

**Decision**: Use decorator-based auto-registration for plugins.

**Implementation**:
```python
# plugins/registry.py
_handlers: dict[str, type[LanguageHandler]] = {}

def register_handler(name: str):
    def decorator(cls: type[LanguageHandler]):
        _handlers[name] = cls
        return cls
    return decorator

def get_handler(language: str) -> LanguageHandler:
    if language not in _handlers:
        raise UnsupportedLanguageError(f"No handler for {language}")
    return _handlers[language]()

# plugins/python_handler.py
@register_handler('python')
class PythonHandler(LanguageHandler):
    def detect(self, project_root: Path) -> DetectionResult | None:
        if (project_root / 'pyproject.toml').exists():
            return DetectionResult('python', 0.95, None, None)
        # ... more detection logic
```

**Benefits**:
- No manual registration required (import plugins package auto-registers)
- Centralized handler lookup with clear error messages
- Easy to add new languages (just implement interface and add decorator)

### Tool Availability Detection

**Decision**: Detect missing tools during assessment phase and offer installation with user approval.

**Implementation Strategy**:
```python
from shutil import which

class ToolChecker:
    REQUIRED_TOOLS = {
        'python': ['pytest', 'black', 'pylint', 'bandit'],
        'javascript': ['npm', 'jest', 'eslint', 'prettier'],
        'rust': ['cargo', 'rustfmt', 'clippy'],
    }

    def check_tools(self, language: str) -> ToolCheckResult:
        missing = [tool for tool in self.REQUIRED_TOOLS[language]
                   if which(tool) is None]
        return ToolCheckResult(available=..., missing=missing)

    def offer_installation(self, missing: list[str]) -> bool:
        """Prompt user to install missing tools via package manager."""
        if not missing:
            return True

        console.print(f"[yellow]Missing tools: {', '.join(missing)}[/yellow]")
        if click.confirm("Install via system package manager?"):
            # Detect package manager (apt, brew, pacman, choco)
            # Attempt installation with subprocess
            return True
        return False
```

**Graceful Degradation**: If user declines tool installation, skip phases requiring those tools and document limitations in assessment report.

## Git Safety Patterns

### Atomic Commits with Descriptive Messages

**Pattern**: Each structural change creates one commit with standardized message format.

**Message Format**:
```
[brownfield] <category>: <description>

<optional body explaining rationale>

Phase: <phase-name>
Automated: yes
```

**Categories**:
- `structure`: File moves, directory creation
- `testing`: Test framework setup, test file generation
- `quality`: Linter/formatter config, pre-commit hooks
- `docs`: README, docstring additions
- `config`: Build configuration changes

**Example**:
```
[brownfield] structure: Move source files to src/ directory

Moved 12 Python modules from project root to src/myproject/
to follow PEP 518 package structure conventions.

Phase: Structure Remediation
Automated: yes
```

### Auto-Revert on Build Failure

**Decision**: After each structural change, verify build succeeds; if failed, automatically revert commit.

**Implementation**:
```python
class AutoRevert:
    def __init__(self, repo: Repo):
        self.repo = repo

    def commit_with_verification(
        self,
        message: str,
        files: list[Path],
        verify_cmd: list[str]
    ) -> Commit | None:
        """Create commit and revert if verification fails."""
        commit = self.repo.index.commit(message)

        result = subprocess.run(
            verify_cmd,
            capture_output=True,
            timeout=300
        )

        if result.returncode != 0:
            self.repo.git.revert(commit.hexsha, no_edit=True)
            self._log_failure(commit, result.stderr)
            return None

        return commit

    def _log_failure(self, commit: Commit, error: str):
        """Record failure in brownfield-decisions.md."""
        with open('.specify/memory/brownfield-decisions.md', 'a') as f:
            f.write(f"\n## Build Failure - {commit.hexsha[:7]}\n")
            f.write(f"**Change**: {commit.message}\n")
            f.write(f"**Error**: {error}\n")
            f.write(f"**Action**: Reverted automatically\n\n")
```

**Build Verification Commands**:
- **Python**: `python -m py_compile <changed_files>` or `pytest --collect-only`
- **JavaScript**: `npm run build` or `node --check <changed_files>`
- **Rust**: `cargo check`
- **Go**: `go build ./...`

### Checkpoint-Based Interruption Recovery

**Decision**: Maintain checkpoint file tracking completed tasks; on restart, offer resumption.

**Checkpoint Schema**:
```json
{
  "phase": "Structure",
  "started_at": "2025-10-12T14:30:00Z",
  "last_checkpoint": "2025-10-12T14:45:00Z",
  "completed_tasks": [
    "move_src_files",
    "update_imports_module_a",
    "update_imports_module_b"
  ],
  "total_tasks": 15,
  "interrupted": true
}
```

**Recovery Logic**:
```python
class CheckpointManager:
    def load_checkpoint(self) -> Checkpoint | None:
        path = Path('.specify/memory/brownfield-checkpoint.json')
        if not path.exists():
            return None

        checkpoint = Checkpoint.from_json(path.read_text())
        if checkpoint.interrupted:
            return checkpoint
        return None

    def offer_resumption(self, checkpoint: Checkpoint) -> bool:
        """Ask user whether to resume or restart phase."""
        console.print(f"[yellow]Interrupted {checkpoint.phase} detected[/yellow]")
        console.print(f"Progress: {len(checkpoint.completed_tasks)}/{checkpoint.total_tasks} tasks")

        return click.confirm("Resume from checkpoint?", default=True)
```

**Update Strategy**: Write checkpoint after each task completes (every 30-60 seconds of work).

## Testing Strategies

### Pytest Fixtures for Brownfield Repositories

**Decision**: Use pytest fixtures to create temporary brownfield project structures for integration tests.

**Implementation**:
```python
# tests/conftest.py
import pytest
from pathlib import Path
from git import Repo

@pytest.fixture
def messy_python_project(tmp_path: Path) -> Path:
    """Create a disorganized Python project for testing."""
    project = tmp_path / "test_project"
    project.mkdir()

    # Create messy structure (files in root, no tests/)
    (project / "main.py").write_text("def main(): pass")
    (project / "utils.py").write_text("def helper(): pass")
    (project / "config.py").write_text("DEBUG = True")

    # Initialize git
    repo = Repo.init(project)
    repo.index.add(['main.py', 'utils.py', 'config.py'])
    repo.index.commit("Initial messy commit")

    return project

@pytest.fixture
def javascript_legacy_project(tmp_path: Path) -> Path:
    """Create legacy JavaScript project (no package.json, mixed modules)."""
    project = tmp_path / "js_project"
    project.mkdir()

    (project / "index.js").write_text("const util = require('./util');")
    (project / "util.js").write_text("module.exports = {};")
    (project / "modern.js").write_text("import { x } from './util';")

    repo = Repo.init(project)
    repo.index.add(['index.js', 'util.js', 'modern.js'])
    repo.index.commit("Legacy JS project")

    return project
```

**Usage in Tests**:
```python
def test_structure_remediation(messy_python_project: Path):
    """Test that structure phase moves files to src/ and updates imports."""
    from brownfield.cli import assess, structure

    # Run assessment first
    assess(project_root=messy_python_project, quick=True)

    # Run structure remediation
    structure(project_root=messy_python_project, auto_approve=True)

    # Verify files moved
    assert (messy_python_project / "src" / "main.py").exists()
    assert not (messy_python_project / "main.py").exists()

    # Verify imports updated
    content = (messy_python_project / "src" / "main.py").read_text()
    assert "from .utils import helper" in content
```

### Contract Tests for Plugin Interface

**Decision**: Test that all language handlers implement required interface correctly.

**Implementation**:
```python
# tests/contract/test_plugin_interface.py
import pytest
from brownfield.plugins import registry, base

REQUIRED_HANDLERS = ['python', 'javascript', 'rust', 'go']

@pytest.mark.parametrize('language', REQUIRED_HANDLERS)
def test_handler_registration(language: str):
    """All required handlers must be registered."""
    handler = registry.get_handler(language)
    assert handler is not None
    assert isinstance(handler, base.LanguageHandler)

@pytest.mark.parametrize('language', REQUIRED_HANDLERS)
def test_handler_implements_interface(language: str):
    """All handlers must implement required methods."""
    handler = registry.get_handler(language)

    # Check required methods exist and are callable
    assert callable(handler.detect)
    assert callable(handler.get_standard_structure)
    assert callable(handler.bootstrap_tests)
    assert callable(handler.install_quality_gates)

@pytest.mark.parametrize('language', REQUIRED_HANDLERS)
def test_detection_returns_valid_result(language: str, tmp_path: Path):
    """Detection must return DetectionResult or None."""
    handler = registry.get_handler(language)
    result = handler.detect(tmp_path)

    if result is not None:
        assert isinstance(result, base.DetectionResult)
        assert 0.0 <= result.confidence <= 1.0
        assert result.language == language
```

### Integration Tests for Full Workflow

**Strategy**: Test complete assessment → graduation flow with fixture projects.

**Test Structure**:
```python
# tests/integration/test_full_workflow.py
def test_python_project_graduation(messy_python_project: Path):
    """Test full brownfield workflow on Python project."""
    from brownfield.orchestrator import WorkflowRunner

    runner = WorkflowRunner(project_root=messy_python_project)

    # Phase 0: Assessment
    assessment = runner.run_assessment(quick=True)
    assert assessment.language == 'python'
    assert assessment.test_coverage == 0.0

    # Phase 1: Structure
    runner.run_structure(auto_approve=True)
    assert (messy_python_project / "src").exists()
    assert (messy_python_project / "tests").exists()

    # Phase 2: Testing
    runner.run_testing(coverage_target=0.6)
    state = runner.get_state()
    assert state.current_metrics.test_coverage >= 0.6

    # Phase 3: Quality
    runner.run_quality()
    assert (messy_python_project / ".pre-commit-config.yaml").exists()

    # Phase 4: Validation
    validation = runner.run_validation()
    assert all(gate.passed for gate in validation.gates)

    # Phase 5: Graduation
    runner.graduate()
    assert (messy_python_project / ".specify" / "memory" / "constitution.md").exists()
    assert (messy_python_project / "brownfield-graduation-report.md").exists()
```

## State Management Patterns

### JSON vs Database Tradeoff

**Decision**: Use JSON files for state persistence instead of embedded database (SQLite).

**Rationale**:
- **Simplicity**: No schema migrations, no query language, direct serialization
- **Human-readable**: Users can inspect state with text editor
- **Git-friendly**: Text format enables version control and diffing
- **Portability**: No binary files, works across platforms without compilation
- **Dependency-free**: No need for SQLite driver or ORM

**Trade-offs**:
- **Performance**: Slower for large datasets (mitigated: state files are small, <100KB)
- **Concurrency**: No built-in locking (mitigated: single-process tool, not multi-user)
- **Querying**: No SQL queries (mitigated: load entire state into memory, filter with Python)

**Implementation Pattern**:
```python
from dataclasses import dataclass, asdict
from pathlib import Path
import json

@dataclass
class BrownfieldState:
    current_phase: str
    baseline_metrics: dict[str, float]
    current_metrics: dict[str, float]
    phase_timestamps: dict[str, str]

    @classmethod
    def load(cls, path: Path) -> 'BrownfieldState':
        """Load state from JSON file."""
        if not path.exists():
            return cls.default()

        data = json.loads(path.read_text())
        return cls(**data)

    def save(self, path: Path):
        """Save state to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2))
```

### State Versioning Strategy

**Decision**: Include schema version in state files for future compatibility.

**Schema**:
```json
{
  "schema_version": "1.0",
  "current_phase": "Testing",
  "baseline_metrics": {
    "test_coverage": 0.0,
    "complexity_avg": 12.5,
    "critical_vulnerabilities": 3
  },
  "current_metrics": {
    "test_coverage": 0.45,
    "complexity_avg": 8.2,
    "critical_vulnerabilities": 1
  },
  "phase_timestamps": {
    "assessment": "2025-10-12T14:00:00Z",
    "structure": "2025-10-12T14:30:00Z",
    "testing_started": "2025-10-12T15:00:00Z"
  }
}
```

**Migration Strategy**: Check `schema_version` on load; apply migrations if needed.

```python
def migrate_state(data: dict) -> dict:
    """Apply schema migrations based on version."""
    version = data.get('schema_version', '0.0')

    if version == '0.0':
        # Migrate from legacy format
        data['schema_version'] = '1.0'
        data['phase_timestamps'] = data.pop('timestamps', {})

    return data
```

## Performance Considerations

### Quick vs Full Analysis Mode

**Decision**: Implement sampling-based quick mode for large codebases (>100K LOC).

**Quick Mode Strategy**:
1. Sample 10% of files from each major directory
2. Use heuristics for metric estimation (extrapolate from sample)
3. Skip expensive operations (full complexity analysis, deep dependency graph)
4. Target: <10 minutes for 500K LOC project

**Full Mode Strategy**:
1. Analyze every file comprehensively
2. Build complete dependency graph
3. Run all security scanners with deep scan flags
4. Target: <30 minutes for 100K LOC project

**Implementation**:
```python
class MetricsCollector:
    def collect(self, project_root: Path, mode: str = 'quick') -> Metrics:
        if mode == 'quick':
            return self._quick_analysis(project_root)
        return self._full_analysis(project_root)

    def _quick_analysis(self, root: Path) -> Metrics:
        """Sample-based analysis for large codebases."""
        all_files = list(root.rglob('*.py'))
        sample_size = max(len(all_files) // 10, 20)
        sample = random.sample(all_files, min(sample_size, len(all_files)))

        # Analyze sample
        coverage = self._estimate_coverage(sample)
        complexity = self._estimate_complexity(sample)

        return Metrics(
            test_coverage=coverage,
            complexity_avg=complexity,
            confidence='medium'  # Mark as estimate
        )
```

## References

- [Click Documentation](https://click.palletsprojects.com/)
- [GitPython Documentation](https://gitpython.readthedocs.io/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [Python ABC Pattern](https://docs.python.org/3/library/abc.html)
- [Lizard Complexity Tool](https://github.com/terryyin/lizard)
- [Pre-commit Framework](https://pre-commit.com/)
