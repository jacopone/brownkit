---
status: active
created: 2025-10-21
updated: 2025-10-21
type: guide
lifecycle: persistent
---

# BrownKit Test Suite

Comprehensive test suite for BrownKit with unit, contract, and integration tests.

## Test Structure

```
tests/
├── unit/                    # Unit tests (fast, isolated)
├── contract/                # Contract tests (plugin interface)
├── integration/             # Integration tests (end-to-end)
├── fixtures/                # Test fixture projects
│   ├── python_messy/       # Python project with issues
│   ├── javascript_unstructured/  # JavaScript project
│   ├── rust_complex/       # Rust project with high complexity
│   └── go_unorganized/     # Go project needing organization
├── conftest.py             # Shared pytest fixtures
└── README.md               # This file
```

## Running Tests

### Quick Start

```bash
# Run all tests
./scripts/run_tests.sh

# Run unit tests only (fast)
./scripts/run_tests.sh unit

# Run contract tests
./scripts/run_tests.sh contract

# Run integration tests
./scripts/run_tests.sh integration

# Run with coverage
./scripts/run_tests.sh coverage
```

### Using Pytest Directly

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Contract tests only
pytest tests/contract/

# Integration tests only
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_config.py

# Run specific test
pytest tests/unit/test_config.py::TestBrownfieldConfig::test_get_project_root

# With coverage
pytest --cov=src/brownfield --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Run tests matching pattern
pytest -k "test_assess"
```

## Test Categories

### Unit Tests (`tests/unit/`)

Fast, isolated tests for individual components.

**What to test**:
- Individual functions and methods
- Class behavior in isolation
- Edge cases and error handling
- Input validation
- Data transformations

**Example**:
```python
def test_config_get_project_root():
    """Test project root retrieval."""
    config = BrownfieldConfig()
    root = config.get_project_root()
    assert isinstance(root, Path)
```

**Coverage target**: 80%+

### Contract Tests (`tests/contract/`)

Verify plugin interface compliance.

**What to test**:
- All plugins implement required methods
- Method signatures match interface
- Return types are correct
- Plugins can detect their language
- Standard structure definitions are valid

**Example**:
```python
@pytest.mark.parametrize("plugin_class", PLUGIN_CLASSES)
def test_has_detect_method(self, plugin_class):
    """Plugin must implement detect() method."""
    assert hasattr(plugin_class, "detect")
```

**Coverage target**: 100% of plugin interface

### Integration Tests (`tests/integration/`)

End-to-end workflow tests on fixture projects.

**What to test**:
- Full assessment workflow
- State transitions between phases
- Command interactions (assess → structure → testing)
- File generation (reports, plans, state files)
- Environment variable configuration
- Error handling in real scenarios

**Example**:
```python
def test_full_assessment_workflow(self, python_project):
    """Test complete assessment workflow."""
    result = cli_runner.invoke(brownfield, ["assess", "--quick"])
    assert result.exit_code == 0
    assert state_path.exists()
```

**Coverage target**: 60%+ (slower tests)

## Test Fixtures

### Fixture Projects

Located in `tests/fixtures/`, these are sample brownfield projects with intentional issues:

#### `python_messy/`
- **Issues**: High complexity, hardcoded secrets, no tests, poor structure
- **Complexity**: Functions with CCN > 10
- **Security**: Plain text passwords, API keys in code
- **Structure**: Files in root directory
- **Coverage**: 0%

#### `javascript_unstructured/`
- **Issues**: No structure, high complexity, security issues
- **Framework**: Node.js with Express
- **Structure**: All code in single `app.js` file
- **Coverage**: 0%

#### `rust_complex/`
- **Issues**: High complexity, no tests, security issues
- **Complexity**: Nested conditionals (CCN > 10)
- **Security**: Plain text passwords
- **Structure**: Files in root

#### `go_unorganized/`
- **Issues**: Poor structure, hardcoded credentials, high complexity
- **Structure**: No package organization
- **Security**: API keys in source
- **Coverage**: 0%

### Using Fixtures in Tests

```python
@pytest.fixture
def python_project(tmp_path):
    """Create temporary copy of Python fixture."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "python_messy"
    project_path = tmp_path / "python_project"
    shutil.copytree(fixture_path, project_path)
    return project_path

def test_assess_python(python_project):
    """Test assessment on Python fixture."""
    result = assess_project(python_project)
    assert result.language == "python"
```

## Pytest Configuration

### Markers

Tests are automatically marked based on directory:

- `@pytest.mark.unit` - Unit tests (auto-applied to `tests/unit/`)
- `@pytest.mark.contract` - Contract tests (auto-applied to `tests/contract/`)
- `@pytest.mark.integration` - Integration tests (auto-applied to `tests/integration/`)
- `@pytest.mark.slow` - Slow tests (auto-applied to integration tests)
- `@pytest.mark.requires_fixture` - Tests requiring fixture projects

### Running Specific Markers

```bash
# Run only unit tests
pytest -m unit

# Run only contract tests
pytest -m contract

# Run only integration tests
pytest -m integration

# Run fast tests (exclude slow)
pytest -m "not slow"

# Run tests requiring fixtures
pytest -m requires_fixture
```

## Coverage Reports

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=src/brownfield --cov-report=term

# HTML report
pytest --cov=src/brownfield --cov-report=html

# Both
pytest --cov=src/brownfield --cov-report=term --cov-report=html

# Open HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Configuration

Coverage settings in `pytest.ini`:
- **Source**: `src/brownfield`
- **Omit**: `*/tests/*`, `*/__pycache__/*`
- **Precision**: 2 decimal places
- **Show missing**: True

### Coverage Targets

| Test Type | Target | Current |
|-----------|--------|---------|
| Unit | 80% | TBD |
| Contract | 100% | TBD |
| Integration | 60% | TBD |
| Overall | 70% | TBD |

## Writing New Tests

### Unit Test Template

```python
"""Unit tests for <module_name>."""

import pytest
from brownfield.<module> import <Class>


class Test<ClassName>:
    """Test <ClassName> functionality."""

    def test_basic_functionality(self):
        """Test basic use case."""
        instance = <Class>()
        result = instance.method()
        assert result == expected

    def test_edge_case(self):
        """Test edge case handling."""
        instance = <Class>()
        with pytest.raises(ValueError):
            instance.method(invalid_input)

    @pytest.mark.parametrize("input,expected", [
        ("input1", "output1"),
        ("input2", "output2"),
    ])
    def test_multiple_cases(self, input, expected):
        """Test multiple input cases."""
        result = function(input)
        assert result == expected
```

### Integration Test Template

```python
"""Integration tests for <workflow_name>."""

import shutil
from pathlib import Path
import pytest
from click.testing import CliRunner

from brownfield.cli.commands import brownfield


@pytest.fixture
def test_project(tmp_path):
    """Create test project."""
    fixture = Path(__file__).parent.parent / "fixtures" / "python_messy"
    project = tmp_path / "test"
    shutil.copytree(fixture, project)
    return project


class Test<WorkflowName>:
    """Test <workflow> workflow."""

    def test_workflow(self, test_project, monkeypatch):
        """Test complete workflow."""
        monkeypatch.setenv("BROWNFIELD_PROJECT_ROOT", str(test_project))

        cli_runner = CliRunner()
        result = cli_runner.invoke(brownfield, ["command"])

        assert result.exit_code == 0
        assert "expected output" in result.output
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
          pip install -e .

      - name: Run fast tests
        run: ./scripts/run_tests.sh fast

      - name: Run integration tests
        run: ./scripts/run_tests.sh integration

      - name: Generate coverage
        run: ./scripts/run_tests.sh coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'brownfield'`

**Solution**:
```bash
# Install in editable mode
pip install -e .

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Fixture Not Found

**Problem**: `pytest.skip("Python fixture not found")`

**Solution**:
```bash
# Ensure fixtures exist
ls tests/fixtures/

# Fixtures should have git repos
ls tests/fixtures/python_messy/.git
```

### Permission Errors

**Problem**: `PermissionError: [Errno 13] Permission denied`

**Solution**:
```bash
# Make test runner executable
chmod +x scripts/run_tests.sh

# Check file permissions
ls -la tests/fixtures/
```

### Slow Tests

**Problem**: Integration tests take too long

**Solution**:
```bash
# Run only fast tests during development
./scripts/run_tests.sh fast

# Run integration tests before commit
./scripts/run_tests.sh integration

# Use pytest-xdist for parallel execution
pip install pytest-xdist
pytest -n auto  # Use all CPU cores
```

## Best Practices

### 1. Test Isolation

Each test should be independent:
```python
# ✅ GOOD - Uses fixture for clean state
def test_function(tmp_path):
    project = tmp_path / "test"
    project.mkdir()
    # Test uses isolated directory

# ❌ BAD - Modifies shared state
def test_function():
    project = Path("/shared/location")
    # Tests can interfere with each other
```

### 2. Descriptive Names

Use clear, descriptive test names:
```python
# ✅ GOOD
def test_assess_detects_python_project_from_requirements_txt():
    pass

# ❌ BAD
def test_assess():
    pass
```

### 3. Arrange-Act-Assert

Structure tests clearly:
```python
def test_config_default_analysis_mode():
    # Arrange - Set up test data
    config = BrownfieldConfig()

    # Act - Execute function under test
    mode = config.get_default_analysis_mode()

    # Assert - Verify expected outcome
    assert mode == "quick"
```

### 4. Mock External Dependencies

Don't rely on external services:
```python
# ✅ GOOD - Mocks external call
def test_api_call(monkeypatch):
    def mock_request(url):
        return {"status": "ok"}

    monkeypatch.setattr("requests.get", mock_request)
    result = call_api()
    assert result["status"] == "ok"
```

### 5. Parametrize Similar Tests

Use `@pytest.mark.parametrize` for multiple cases:
```python
@pytest.mark.parametrize("language,expected", [
    ("python", ".py"),
    ("javascript", ".js"),
    ("rust", ".rs"),
    ("go", ".go"),
])
def test_language_extensions(language, expected):
    ext = get_extension(language)
    assert ext == expected
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [BrownKit Contributing Guide](../CONTRIBUTING.md)

---

**Last Updated**: 2025-10-21
**Maintainer**: BrownKit Team
