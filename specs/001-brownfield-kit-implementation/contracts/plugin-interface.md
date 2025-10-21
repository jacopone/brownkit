# Plugin Interface Contract

**Feature**: Brownfield-Kit Implementation
**Created**: 2025-10-12
**Purpose**: Define the language handler plugin interface for extending Brownfield-Kit

## Overview

The plugin interface allows Brownfield-Kit to support multiple programming languages through a consistent API. Each language handler implements detection, structure remediation, testing, and quality gate installation specific to that ecosystem.

## Base Interface: `LanguageHandler`

All language plugins must inherit from `LanguageHandler` abstract base class and implement all required methods.

**Location**: `src/brownfield/plugins/base.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

class ConfidenceLevel(Enum):
    """Detection confidence levels."""
    HIGH = 0.9    # >90% confident
    MEDIUM = 0.7  # 70-90% confident
    LOW = 0.5     # 50-70% confident

@dataclass
class DetectionResult:
    """Language/framework detection result."""
    language: str              # Language name (lowercase: "python", "javascript", "rust", "go")
    confidence: ConfidenceLevel
    version: str | None        # Detected version (e.g., "3.9.16", "18.0.0", "1.70")
    framework: str | None      # Framework if detected (e.g., "flask", "react", "actix-web")
    evidence: dict[str, str]   # Detection evidence {"file": "reason"}

@dataclass
class StructureResult:
    """Structure remediation result."""
    directories_created: list[Path]
    files_moved: dict[Path, Path]  # {source: destination}
    imports_updated: int
    configs_created: list[Path]
    commits: list[str]  # Git commit SHAs

@dataclass
class TestSetupResult:
    """Test infrastructure setup result."""
    framework: str              # Test framework name
    dependencies_added: list[str]
    test_files_created: list[Path]
    coverage: float             # Achieved coverage (0.0-1.0)
    tests_passing: int
    tests_failing: int

@dataclass
class QualitySetupResult:
    """Quality gates installation result."""
    linter: str                 # Linter name
    formatter: str              # Formatter name
    linter_issues_found: int
    linter_issues_fixed: int
    formatter_files_changed: int
    hooks_installed: list[str]  # Pre-commit hook names
    complexity_violations: int

class LanguageHandler(ABC):
    """Abstract base class for language-specific handlers."""

    @abstractmethod
    def detect(self, project_root: Path) -> DetectionResult | None:
        """
        Detect language and framework from project files.

        Args:
            project_root: Path to project directory

        Returns:
            DetectionResult if language detected, None otherwise

        Implementation Guide:
            - Check for language-specific files (package.json, Cargo.toml, etc.)
            - Parse configuration files for version/framework info
            - Count file extensions to estimate confidence
            - Return None if not this language (allows multi-language detection)
        """
        pass

    @abstractmethod
    def get_standard_structure(self) -> dict[str, list[str]]:
        """
        Return ecosystem-standard directory structure.

        Returns:
            Dictionary mapping directory names to expected files/patterns

        Example (Python):
            {
                "src": ["__init__.py"],
                "tests": ["__init__.py", "conftest.py"],
                "docs": ["README.md"],
            }
        """
        pass

    @abstractmethod
    def bootstrap_tests(
        self,
        project_root: Path,
        core_modules: list[Path],
        coverage_target: float = 0.6
    ) -> TestSetupResult:
        """
        Add test framework and generate initial tests.

        Args:
            project_root: Path to project directory
            core_modules: Core business logic modules to test
            coverage_target: Desired coverage (0.0-1.0)

        Returns:
            TestSetupResult with setup details

        Implementation Guide:
            - Install test framework dependencies
            - Create test directory structure
            - Generate contract tests for public APIs
            - Generate smoke tests for basic functionality
            - Measure and report coverage
        """
        pass

    @abstractmethod
    def install_quality_gates(
        self,
        project_root: Path,
        complexity_threshold: int = 10
    ) -> QualitySetupResult:
        """
        Install linters, formatters, and pre-commit hooks.

        Args:
            project_root: Path to project directory
            complexity_threshold: Maximum cyclomatic complexity

        Returns:
            QualitySetupResult with installation details

        Implementation Guide:
            - Add linter/formatter dependencies
            - Create configuration files
            - Run initial linting/formatting pass
            - Install pre-commit hooks
            - Check complexity and document violations
        """
        pass

    @abstractmethod
    def verify_build(self, project_root: Path) -> bool:
        """
        Verify project builds without errors.

        Args:
            project_root: Path to project directory

        Returns:
            True if build succeeds, False otherwise

        Implementation Guide:
            - Run language-specific build/compile command
            - Check for errors (warnings acceptable)
            - Return quickly (<30 seconds)
        """
        pass

    @abstractmethod
    def measure_complexity(self, project_root: Path) -> dict[str, float]:
        """
        Measure cyclomatic complexity of codebase.

        Args:
            project_root: Path to project directory

        Returns:
            Dictionary with complexity metrics:
            {
                "average": 8.5,
                "maximum": 15,
                "violations": 3  # Functions exceeding threshold
            }
        """
        pass

    @abstractmethod
    def scan_security(self, project_root: Path) -> dict[str, int]:
        """
        Scan for security vulnerabilities.

        Args:
            project_root: Path to project directory

        Returns:
            Dictionary with vulnerability counts by severity:
            {
                "critical": 0,
                "high": 2,
                "medium": 5,
                "low": 10
            }
        """
        pass
```

## Plugin Registration

Plugins register themselves using the `@register_handler` decorator.

**Location**: `src/brownfield/plugins/registry.py`

```python
_handlers: dict[str, type[LanguageHandler]] = {}

def register_handler(name: str):
    """
    Decorator to register a language handler.

    Usage:
        @register_handler('python')
        class PythonHandler(LanguageHandler):
            ...
    """
    def decorator(cls: type[LanguageHandler]):
        _handlers[name] = cls
        return cls
    return decorator

def get_handler(language: str) -> LanguageHandler:
    """
    Get registered handler for language.

    Args:
        language: Language name (lowercase)

    Returns:
        Instantiated handler

    Raises:
        UnsupportedLanguageError: If language not registered
    """
    if language not in _handlers:
        raise UnsupportedLanguageError(f"No handler for {language}")
    return _handlers[language]()

def list_supported_languages() -> list[str]:
    """Return list of supported language names."""
    return list(_handlers.keys())
```

## Reference Implementation: Python Handler

**Location**: `src/brownfield/plugins/python_handler.py`

```python
from pathlib import Path
from brownfield.plugins.base import (
    LanguageHandler,
    DetectionResult,
    ConfidenceLevel,
    StructureResult,
    TestSetupResult,
    QualitySetupResult
)
from brownfield.plugins.registry import register_handler

@register_handler('python')
class PythonHandler(LanguageHandler):
    """Python language handler."""

    def detect(self, project_root: Path) -> DetectionResult | None:
        """Detect Python project from pyproject.toml, setup.py, or .py files."""
        evidence = {}
        confidence = ConfidenceLevel.LOW

        # Check for pyproject.toml
        pyproject = project_root / "pyproject.toml"
        if pyproject.exists():
            evidence["pyproject.toml"] = "Found Python project config"
            confidence = ConfidenceLevel.HIGH

        # Check for setup.py
        setup_py = project_root / "setup.py"
        if setup_py.exists():
            evidence["setup.py"] = "Found legacy setuptools config"
            if confidence == ConfidenceLevel.LOW:
                confidence = ConfidenceLevel.MEDIUM

        # Count .py files
        py_files = list(project_root.rglob("*.py"))
        if len(py_files) > 3:
            evidence["*.py files"] = f"Found {len(py_files)} Python files"
            if confidence == ConfidenceLevel.LOW:
                confidence = ConfidenceLevel.MEDIUM

        # If no evidence, not a Python project
        if not evidence:
            return None

        # Detect version and framework
        version = self._detect_python_version(project_root)
        framework = self._detect_framework(project_root)

        return DetectionResult(
            language="python",
            confidence=confidence,
            version=version,
            framework=framework,
            evidence=evidence
        )

    def get_standard_structure(self) -> dict[str, list[str]]:
        """Return PEP 518 standard structure."""
        return {
            "src": ["__init__.py"],
            "tests": ["__init__.py", "conftest.py"],
            "docs": ["README.md"],
        }

    def bootstrap_tests(
        self,
        project_root: Path,
        core_modules: list[Path],
        coverage_target: float = 0.6
    ) -> TestSetupResult:
        """Add pytest and generate contract tests."""
        # 1. Install pytest dependencies
        self._add_dependencies(project_root, [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "pytest-mock>=3.10"
        ])

        # 2. Create test directory structure
        tests_dir = project_root / "tests"
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "__init__.py").touch()

        # 3. Create conftest.py with fixtures
        conftest = tests_dir / "conftest.py"
        conftest.write_text(self._generate_conftest())

        # 4. Generate contract tests for core modules
        test_files = []
        for module in core_modules:
            test_file = self._generate_contract_tests(tests_dir, module)
            test_files.append(test_file)

        # 5. Run tests and measure coverage
        coverage = self._run_pytest_with_coverage(project_root, core_modules)

        return TestSetupResult(
            framework="pytest",
            dependencies_added=["pytest", "pytest-cov", "pytest-mock"],
            test_files_created=test_files,
            coverage=coverage,
            tests_passing=self._count_passing_tests(project_root),
            tests_failing=0
        )

    def install_quality_gates(
        self,
        project_root: Path,
        complexity_threshold: int = 10
    ) -> QualitySetupResult:
        """Add pylint, black, and pre-commit hooks."""
        # 1. Add linter/formatter dependencies
        self._add_dependencies(project_root, [
            "pylint>=2.15",
            "black>=23.0",
            "pre-commit>=3.0"
        ])

        # 2. Create linter config
        pylintrc = project_root / ".pylintrc"
        pylintrc.write_text(self._generate_pylintrc())

        # 3. Run black formatter
        formatter_result = self._run_black(project_root)

        # 4. Run pylint
        linter_result = self._run_pylint(project_root)

        # 5. Install pre-commit hooks
        self._install_pre_commit_hooks(project_root)

        # 6. Check complexity
        complexity = self.measure_complexity(project_root)

        return QualitySetupResult(
            linter="pylint",
            formatter="black",
            linter_issues_found=linter_result["issues"],
            linter_issues_fixed=linter_result["fixed"],
            formatter_files_changed=formatter_result["files_changed"],
            hooks_installed=["black", "pylint", "pytest"],
            complexity_violations=int(complexity["violations"])
        )

    def verify_build(self, project_root: Path) -> bool:
        """Compile all Python files to check for syntax errors."""
        import subprocess
        result = subprocess.run(
            ["python", "-m", "py_compile", *self._get_py_files(project_root)],
            cwd=project_root,
            capture_output=True
        )
        return result.returncode == 0

    def measure_complexity(self, project_root: Path) -> dict[str, float]:
        """Use lizard to measure cyclomatic complexity."""
        import subprocess
        result = subprocess.run(
            ["lizard", str(project_root), "-l", "python"],
            capture_output=True,
            text=True
        )

        # Parse lizard output
        lines = result.stdout.split("\n")
        avg_complexity = self._parse_lizard_avg(lines)
        max_complexity = self._parse_lizard_max(lines)
        violations = self._count_complexity_violations(lines, threshold=10)

        return {
            "average": avg_complexity,
            "maximum": max_complexity,
            "violations": violations
        }

    def scan_security(self, project_root: Path) -> dict[str, int]:
        """Run bandit security scanner."""
        import subprocess
        result = subprocess.run(
            ["bandit", "-r", str(project_root), "-f", "json"],
            capture_output=True,
            text=True
        )

        # Parse bandit JSON output
        import json
        data = json.loads(result.stdout)

        return {
            "critical": len([i for i in data["results"] if i["issue_severity"] == "HIGH"]),
            "high": len([i for i in data["results"] if i["issue_severity"] == "MEDIUM"]),
            "medium": len([i for i in data["results"] if i["issue_severity"] == "LOW"]),
            "low": 0
        }

    # Private helper methods...
    def _detect_python_version(self, project_root: Path) -> str | None:
        """Parse Python version from pyproject.toml or runtime."""
        pass

    def _detect_framework(self, project_root: Path) -> str | None:
        """Detect Flask, Django, FastAPI, etc."""
        pass
```

## Contract Tests

All plugins must pass these contract tests.

**Location**: `tests/contract/test_plugin_interface.py`

```python
import pytest
from pathlib import Path
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

    # Check all abstract methods implemented
    assert callable(handler.detect)
    assert callable(handler.get_standard_structure)
    assert callable(handler.bootstrap_tests)
    assert callable(handler.install_quality_gates)
    assert callable(handler.verify_build)
    assert callable(handler.measure_complexity)
    assert callable(handler.scan_security)

@pytest.mark.parametrize('language', REQUIRED_HANDLERS)
def test_detection_returns_valid_result(language: str, tmp_path: Path):
    """Detection must return DetectionResult or None."""
    handler = registry.get_handler(language)
    result = handler.detect(tmp_path)

    if result is not None:
        assert isinstance(result, base.DetectionResult)
        assert result.language == language
        assert isinstance(result.confidence, base.ConfidenceLevel)
        assert 0.0 <= result.confidence.value <= 1.0
        assert isinstance(result.evidence, dict)
        assert len(result.evidence) > 0

@pytest.mark.parametrize('language', REQUIRED_HANDLERS)
def test_standard_structure_format(language: str):
    """Standard structure must be valid dictionary."""
    handler = registry.get_handler(language)
    structure = handler.get_standard_structure()

    assert isinstance(structure, dict)
    assert len(structure) > 0
    for directory, files in structure.items():
        assert isinstance(directory, str)
        assert isinstance(files, list)
        assert all(isinstance(f, str) for f in files)

@pytest.mark.parametrize('language', REQUIRED_HANDLERS)
def test_complexity_measurement_format(language: str, tmp_path: Path):
    """Complexity measurement must return valid metrics."""
    handler = registry.get_handler(language)
    complexity = handler.measure_complexity(tmp_path)

    assert isinstance(complexity, dict)
    assert "average" in complexity
    assert "maximum" in complexity
    assert "violations" in complexity
    assert isinstance(complexity["average"], (int, float))
    assert isinstance(complexity["maximum"], (int, float))
    assert isinstance(complexity["violations"], int)

@pytest.mark.parametrize('language', REQUIRED_HANDLERS)
def test_security_scan_format(language: str, tmp_path: Path):
    """Security scan must return valid severity counts."""
    handler = registry.get_handler(language)
    vulnerabilities = handler.scan_security(tmp_path)

    assert isinstance(vulnerabilities, dict)
    assert "critical" in vulnerabilities
    assert "high" in vulnerabilities
    assert "medium" in vulnerabilities
    assert "low" in vulnerabilities
    assert all(isinstance(v, int) for v in vulnerabilities.values())
    assert all(v >= 0 for v in vulnerabilities.values())
```

## Language-Specific Handler Requirements

### Python Handler

**Detection**:
- `pyproject.toml` → HIGH confidence
- `setup.py` → MEDIUM confidence
- `*.py` files (>3) → MEDIUM confidence

**Standard Structure**:
```
src/<package>/
tests/
docs/
```

**Testing**:
- Framework: pytest
- Coverage tool: pytest-cov
- Fixtures: conftest.py

**Quality**:
- Linter: pylint
- Formatter: black
- Complexity: lizard
- Security: bandit

---

### JavaScript Handler

**Detection**:
- `package.json` → HIGH confidence
- `node_modules/` → MEDIUM confidence
- `*.js` files (>3) → MEDIUM confidence

**Standard Structure**:
```
src/
test/
dist/
```

**Testing**:
- Framework: jest
- Coverage tool: jest --coverage

**Quality**:
- Linter: eslint
- Formatter: prettier
- Complexity: lizard
- Security: npm audit

---

### Rust Handler

**Detection**:
- `Cargo.toml` → HIGH confidence
- `*.rs` files → MEDIUM confidence

**Standard Structure**:
```
src/
tests/
benches/
```

**Testing**:
- Framework: cargo test
- Coverage tool: cargo-tarpaulin

**Quality**:
- Linter: clippy
- Formatter: rustfmt
- Complexity: lizard
- Security: cargo audit

---

### Go Handler

**Detection**:
- `go.mod` → HIGH confidence
- `*.go` files → MEDIUM confidence

**Standard Structure**:
```
cmd/
pkg/
internal/
```

**Testing**:
- Framework: go test
- Coverage tool: go test -cover

**Quality**:
- Linter: golangci-lint
- Formatter: gofmt
- Complexity: gocyclo
- Security: gosec

## Plugin Development Checklist

When implementing a new language handler:

- [ ] Create `src/brownfield/plugins/<language>_handler.py`
- [ ] Inherit from `LanguageHandler` base class
- [ ] Add `@register_handler('<language>')` decorator
- [ ] Implement `detect()` with evidence-based detection
- [ ] Implement `get_standard_structure()` with ecosystem conventions
- [ ] Implement `bootstrap_tests()` with framework installation
- [ ] Implement `install_quality_gates()` with linter/formatter setup
- [ ] Implement `verify_build()` with fast build check
- [ ] Implement `measure_complexity()` with tool integration
- [ ] Implement `scan_security()` with vulnerability scanner
- [ ] Add integration test fixture in `tests/integration/fixtures/<language>_unstructured/`
- [ ] Verify contract tests pass: `pytest tests/contract/`
- [ ] Document in `README.md` under "Supported Languages"

## Error Handling

All plugin methods should handle errors gracefully:

```python
def detect(self, project_root: Path) -> DetectionResult | None:
    try:
        # Detection logic
        pass
    except FileNotFoundError:
        # File not found is expected (not this language)
        return None
    except PermissionError:
        # Log warning but don't crash
        logger.warning(f"Permission denied reading {project_root}")
        return None
    except Exception as e:
        # Unexpected errors logged but not raised
        logger.error(f"Unexpected error in Python detection: {e}")
        return None
```

## Performance Guidelines

- **Detection**: <1 second per language
- **Structure remediation**: <30 seconds per file operation
- **Test generation**: <2 minutes per module
- **Quality gate installation**: <5 minutes total

Optimize by:
- Caching file system operations
- Avoiding repeated subprocess calls
- Using streaming parsers for large files
- Running independent operations in parallel
