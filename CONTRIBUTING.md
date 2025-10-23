# Contributing to BrownKit

Thank you for your interest in contributing to BrownKit! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing Requirements](#testing-requirements)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Review Process](#review-process)
- [Community](#community)

---

## Code of Conduct

This project adheres to the Contributor Covenant [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to conduct@brownkit.dev.

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git 2.30+
- (Optional) Nix with direnv for reproducible development environment

### Quick Setup

**Option 1: Using devenv (Recommended for NixOS users)**

```bash
# Clone the repository
git clone https://github.com/jacopone/brownkit.git
cd brownkit

# Activate environment (auto-activates with direnv)
direnv allow

# The environment automatically:
# - Installs Python 3.11
# - Creates virtual environment
# - Installs dependencies
# - Configures pre-commit hooks
```

**Option 2: Traditional Python venv**

```bash
# Clone the repository
git clone https://github.com/jacopone/brownkit.git
cd brownkit

# Create and activate virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows

# Install in editable mode with dev dependencies
pip install -e .[dev]

# Install pre-commit hooks (if not using devenv)
pip install pre-commit
pre-commit install
```

### Verify Installation

```bash
# Run the test suite
pytest

# Check code quality
ruff check src/ tests/
ruff format --check src/ tests/

# Run all quality checks
./scripts/run_tests.sh all
```

---

## Development Setup

### Project Structure

```
brownkit/
├── src/brownfield/     # Source code
│   ├── cli/           # CLI commands
│   ├── orchestrator/  # Workflow orchestration
│   ├── plugins/       # Language handlers
│   └── ...
├── tests/             # Test suite
│   ├── unit/         # Fast, isolated tests
│   ├── contract/     # Plugin interface tests
│   ├── integration/  # End-to-end tests
│   └── fixtures/     # Test projects
├── docs/              # Documentation
└── examples/          # Usage examples
```

### Available Commands (with devenv)

```bash
test              # Run test suite
test-cov          # Run tests with coverage report
lint              # Check code with ruff
lint-fix          # Auto-fix linting issues
format            # Format code with ruff format
typecheck         # Run mypy type checking
complexity        # Analyze code complexity (CCN < 10)
check-all         # Run all quality checks
```

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/description
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes**
   - Write code following project conventions
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**
   ```bash
   check-all  # Or ./scripts/run_tests.sh all
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/description
   # Create PR on GitHub
   ```

---

## Making Changes

### Types of Contributions

We welcome several types of contributions:

- **Bug fixes** - Fix issues in existing code
- **Features** - Add new functionality
- **Documentation** - Improve or add documentation
- **Tests** - Add or improve test coverage
- **Refactoring** - Improve code quality without changing behavior
- **Performance** - Optimize code performance

### Finding Work

- Check [GitHub Issues](https://github.com/jacopone/brownkit/issues) for open issues
- Look for issues labeled `good first issue` or `help wanted`
- Ask in [Discussions](https://github.com/jacopone/brownkit/discussions) if you need guidance

---

## Testing Requirements

### All Pull Requests Must Include Tests

**New Features:**
- Add unit tests for new functions/classes
- Add integration tests if feature spans multiple modules
- Aim for 80%+ coverage on new code

**Bug Fixes:**
- Add regression test that fails without the fix
- Ensure test passes with the fix

**Refactoring:**
- Ensure existing tests still pass
- Add tests for any new abstractions

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit              # Fast unit tests
pytest -m contract          # Plugin interface tests
pytest -m integration       # End-to-end tests

# Run tests with coverage
pytest --cov=src/brownfield --cov-report=html
# View report: open htmlcov/index.html

# Run tests in watch mode
ptw -- tests/              # Requires pytest-watch
```

### Test Organization

- **Unit tests** (`tests/unit/`) - Fast, isolated tests for single functions/classes
- **Contract tests** (`tests/contract/`) - Verify plugin interface compliance
- **Integration tests** (`tests/integration/`) - End-to-end workflow tests
- **Fixtures** (`tests/fixtures/`) - Sample brownfield projects for testing

### Writing Good Tests

- Use descriptive test names: `test_detect_python_project_with_pyproject_toml`
- Follow AAA pattern: Arrange, Act, Assert
- Keep tests isolated (no shared state)
- Use fixtures for common setup
- Test edge cases and error conditions

Example:
```python
def test_bootstrap_tests_creates_pytest_framework(temp_project):
    """Test that bootstrap_tests installs pytest framework."""
    # Arrange
    handler = PythonHandler()
    project_root = temp_project

    # Act
    result = handler.bootstrap_tests(project_root, [])

    # Assert
    assert result.framework == "pytest"
    assert (project_root / "tests").exists()
    assert (project_root / "tests" / "conftest.py").exists()
```

---

## Code Style

### Python Style Guide

We follow PEP 8 with these specifics:

**Line Length**: 100 characters (not 79)

**Formatting**: Use `ruff format` (not black)
```bash
ruff format src/ tests/
```

**Linting**: Use `ruff` for linting
```bash
ruff check src/ tests/
ruff check --fix src/ tests/  # Auto-fix
```

**Type Hints**: Required on all public functions
```python
def bootstrap_tests(
    self,
    project_root: Path,
    core_modules: list[Path],
    coverage_target: float = 0.6
) -> TestSetupResult:
    """Bootstrap test framework."""
```

**Docstrings**: Required on all public functions, classes, and modules
- Use Google style
- Include Args, Returns, Raises sections
- Add examples for complex functions

```python
def detect_language(project_root: Path) -> Optional[DetectionResult]:
    """Detect project language and framework.

    Args:
        project_root: Path to project directory

    Returns:
        DetectionResult if language detected, None otherwise

    Raises:
        FileNotFoundError: If project_root doesn't exist
        PermissionError: If project_root not readable

    Example:
        >>> detector = LanguageDetector()
        >>> result = detector.detect(Path("/path/to/project"))
        >>> print(result.language)
        'python'
    """
```

**Complexity**: Keep cyclomatic complexity (CCN) < 10
```bash
lizard src/brownfield -l python --CCN 10
```

### Naming Conventions

- **Functions/methods**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: Prefix with single underscore `_private_method`

### Import Order

Follow isort/ruff ordering:
1. Standard library imports
2. Third-party imports
3. Local application imports

```python
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from brownfield.models.state import Phase
from brownfield.orchestrator.phase_machine import PhaseOrchestrator
```

---

## Pull Request Process

### Before Submitting

1. **Run all quality checks**
   ```bash
   check-all
   ```

2. **Update documentation**
   - Update README.md if adding features
   - Update CHANGELOG.md (Unreleased section)
   - Add docstrings to new functions/classes

3. **Write descriptive commit messages**
   - Follow [Conventional Commits](https://www.conventionalcommits.org/)
   - Format: `type(scope): description`
   - Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`

   Examples:
   ```
   feat(plugins): add TypeScript language plugin
   fix(orchestrator): prevent phase skipping in state machine
   docs(readme): add examples for CI/CD integration
   test(contract): add plugin interface compliance tests
   refactor(cli): extract command validation logic
   ```

4. **Squash WIP commits** (optional but preferred)
   ```bash
   git rebase -i HEAD~n  # Squash n commits
   ```

### Creating the Pull Request

1. **Push your branch**
   ```bash
   git push origin feature/description
   ```

2. **Create PR on GitHub**
   - Use descriptive title: `feat(plugins): add TypeScript support`
   - Fill out PR template (if available)
   - Reference related issues: `Fixes #123` or `Closes #456`

3. **PR Description Should Include:**
   - **Summary**: What does this PR do?
   - **Motivation**: Why is this change needed?
   - **Changes**: What changed?
   - **Testing**: How was this tested?
   - **Screenshots**: If UI changes
   - **Checklist**:
     - [ ] Tests added/updated
     - [ ] Documentation updated
     - [ ] CHANGELOG.md updated
     - [ ] All checks passing

### Example PR Description

```markdown
## Summary
Adds TypeScript language plugin with jest, prettier, eslint integration.

## Motivation
TypeScript is a popular language in the JavaScript ecosystem and many projects need brownfield transformation.

## Changes
- Created `TypeScriptHandler` class implementing `LanguageHandler`
- Added detection logic for tsconfig.json
- Integrated jest for testing, prettier for formatting, eslint for linting
- Added contract tests for TypeScript plugin

## Testing
- Added 15 contract tests for TypeScript plugin
- Tested against real TypeScript project in `tests/fixtures/typescript_messy/`
- All tests passing

## Checklist
- [x] Tests added
- [x] Documentation updated (README.md)
- [x] CHANGELOG.md updated
- [x] All checks passing
```

---

## Review Process

### What Reviewers Look For

1. **Correctness**: Does the code work as intended?
2. **Tests**: Are there tests? Do they cover edge cases?
3. **Code Quality**: Is the code readable and maintainable?
4. **Documentation**: Are new features documented?
5. **Performance**: Any performance implications?
6. **Security**: Any security concerns?

### Review Timeline

- **Initial response**: Within 2 business days
- **Full review**: Within 1 week
- **Iterative feedback**: Ongoing until approved

### Addressing Feedback

1. **Make requested changes**
2. **Push new commits** (don't force push during review)
3. **Reply to comments** when addressed
4. **Request re-review** when ready

### Merge Requirements

Before merging, your PR must:
- ✅ Pass all CI checks
- ✅ Have at least 1 approving review
- ✅ Have no unresolved conversations
- ✅ Be up to date with main branch
- ✅ Follow conventional commit format

We use **squash and merge** to keep commit history clean.

---

## Community

### Getting Help

- **GitHub Discussions**: Ask questions, share ideas
- **GitHub Issues**: Report bugs, request features
- **Email**: support@brownkit.dev

### Staying Updated

- Watch the repository for notifications
- Follow releases for version updates
- Check CHANGELOG.md for recent changes

### Recognition

Contributors are recognized in:
- CHANGELOG.md (for each release)
- GitHub contributors graph
- Release notes

---

## Additional Resources

- [README.md](README.md) - Project overview and usage
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [docs/](docs/) - Additional documentation
- [tests/README.md](tests/README.md) - Testing guide
- [GitHub Workflow Guide](docs/GITHUB_WORKFLOW.md) - Detailed Git workflow

---

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

Thank you for contributing to BrownKit! 🏗️
