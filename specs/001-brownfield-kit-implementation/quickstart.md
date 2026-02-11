# Quickstart Guide: BrownKit Developer Onboarding

**Feature**: BrownKit Implementation
**Created**: 2025-10-12
**Audience**: Developers contributing to BrownKit

## Prerequisites

### Required Software

1. **Python 3.11 or higher**
   ```bash
   python --version  # Should show 3.11.x or higher
   ```

2. **Git 2.30+**
   ```bash
   git --version
   ```

3. **Pip package manager**
   ```bash
   pip --version
   ```

### Recommended Tools

- **pytest** - Test framework (installed via requirements.txt)
- **black** - Code formatter (installed via requirements.txt)
- **pylint** - Linter (installed via requirements.txt)

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-org/brownkit.git
cd brownkit
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .  # Install brownfield in editable mode
```

**Core Dependencies**:
- `click` (CLI framework)
- `gitpython` (Git operations)
- `rich` (Terminal UI)
- `lizard` (Complexity analysis)
- `coverage[toml]` (Test coverage)
- `pytest` (Testing framework)

### 4. Verify Installation

```bash
brownfield --version
```

Expected output:
```
BrownKit version 0.1.0
```

## Running Your First Assessment

### Test on Sample Project

We provide fixture brownfield projects for testing:

```bash
cd tests/fixtures/python_messy/
brownfield assess --quick
```

Expected output:
```
🔍 Assessing codebase...

Language Detection:
  Primary: Python (confidence: HIGH)
  Version: 3.9
  Framework: None detected

Baseline Metrics:
  Test Coverage: 0.0%
  Avg Complexity: 15.2
  Critical Vulnerabilities: 2

Tech Debt Categories:
  - Structural (HIGH): Source files in root directory
  - Testing (CRITICAL): No test framework, 0% coverage
  - Security (HIGH): 2 critical vulnerabilities detected

Assessment complete! Report saved to:
  .specify/memory/assessment-report.md

Next steps:
  Run: brownfield structure
```

### Understanding Assessment Output

The assessment creates several artifacts:

1. **`.specify/memory/assessment-report.md`**
   - Detailed analysis in human-readable Markdown
   - Language detection evidence
   - Baseline metrics tables
   - Tech debt categorization

2. **`.specify/memory/brownfield-state.json`**
   - Machine-readable state tracking
   - Current phase: "assessment"
   - Baseline metrics stored for comparison

3. **`.specify/memory/brownfield-decisions.md`**
   - Decision log (initially empty after assessment)
   - Populated during remediation phases

### Inspect Assessment Report

```bash
cat .specify/memory/assessment-report.md
```

Key sections:
- **Language Detection**: Confidence level, detected frameworks
- **Baseline Metrics**: Coverage, complexity, security vulnerabilities
- **Tech Debt**: Prioritized issues by category
- **Assumptions**: AI assumptions about project structure
- **Limitations**: What couldn't be analyzed (missing tools, unclear code)

## Understanding the Brownfield Workflow

### The 5-Phase Process

```
┌─────────────┐
│ Assessment  │ ← You are here after first command
└──────┬──────┘
       ↓
┌──────────────┐
│  Structure   │ ← Organize directories, fix imports
└──────┬───────┘
       ↓
┌──────────────┐
│   Testing    │ ← Add test framework, generate tests
└──────┬───────┘
       ↓
┌──────────────┐
│   Quality    │ ← Add linters, formatters, pre-commit hooks
└──────┬───────┘
       ↓
┌──────────────┐
│  Validation  │ ← Check all 7 readiness gates
└──────┬───────┘
       ↓
┌──────────────┐
│  Graduation  │ ← Generate Speckit constitution, archive artifacts
└──────────────┘
```

### Phase Entry/Exit Criteria

| Phase | Entry Criteria | Exit Criteria |
|-------|----------------|---------------|
| Assessment | None (always first) | Assessment report generated |
| Structure | Assessment complete | Files organized, imports updated, build passing |
| Testing | Structure complete | 60% test coverage on core modules |
| Quality | Testing complete | Linters configured, complexity <10, pre-commit hooks installed |
| Validation | Quality complete | All 7 readiness gates pass |
| Graduation | Validation complete | Speckit constitution generated, brownfield artifacts archived |

### Key State Files

- **`.specify/memory/brownfield-state.json`**: Current phase, metrics, timestamps
- **`.specify/memory/brownfield-checkpoint.json`**: Interruption recovery (created during phases)
- **`.specify/memory/assessment-report.md`**: Initial assessment (permanent record)
- **`.specify/memory/brownfield-decisions.md`**: Decision log with rationale (append-only)

## Running the Structure Phase

After assessment, proceed to structure remediation:

```bash
brownfield structure
```

This generates a refactoring plan with:
1. List of directories to create (`src/`, `tests/`, `docs/`)
2. Files that need to be moved with reasons
3. IDE-specific refactoring instructions (PyCharm, VSCode)
4. Shell script for file moves (optional, advanced)
5. Configuration files to create

### Understanding the Plan

The generated plan (`.specify/memory/structure-plan.md`) includes:

```markdown
# Structure Refactoring Plan

## Step 1: Create Directories
- [ ] mkdir -p src tests docs

## Step 2: Move Files (Use IDE!)
⚠️ IMPORTANT: Use IDE refactoring tools!

**PyCharm Users:**
1. Right-click file → Refactor → Move Module
2. Select destination directory
3. Enable "Search for references" (updates imports automatically)

**VSCode Users:**
1. Drag file to destination in Explorer
2. Click "Update imports" when prompted

### Files to Move:
- [ ] main.py → src/myproject/main.py (3 import references)
- [ ] utils.py → src/myproject/utils.py (5 import references)
```

### Manual Refactoring with IDE

**Why manual?** IDE refactoring tools use AST parsing to update imports correctly, avoiding risks of naive string replacement that can break code.

1. **Read the plan**: `cat .specify/memory/structure-plan.md`
2. **Use IDE refactoring**: Follow IDE-specific instructions in the plan
3. **Verify**: Run `brownfield structure --verify`

### Verification After Refactoring

After completing manual refactoring:

```bash
brownfield structure --verify
```

This checks:
- ✓ Directory structure compliant
- ✓ Build integrity (no syntax errors)
- ✓ Import integrity (all imports resolve)
- ✓ No stray files in root

If verification passes:
```
✅ Structure verification PASSED!
   All checks passed.

Next steps:
  Run: brownfield testing
```

If verification fails:
```
❌ Structure verification FAILED
   Issues found:
   - Missing directory: docs/
   - Broken import in src/main.py

See full report: .specify/memory/structure-verification.md
```

## Testing the CLI

### Running Unit Tests

```bash
pytest tests/unit/
```

### Running Contract Tests

Contract tests verify plugin interface compliance:

```bash
pytest tests/contract/
```

### Running Integration Tests

Integration tests use fixture brownfield projects:

```bash
pytest tests/integration/
```

### Test Coverage Report

```bash
pytest --cov=src/brownfield --cov-report=html
open htmlcov/index.html
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/add-go-language-support
```

### 2. Implement Changes

Edit relevant files in `src/brownfield/`:

- **New language plugin**: `src/brownfield/plugins/go_handler.py`
- **Register plugin**: Add `@register_handler('go')` decorator
- **Implement interface**: Inherit from `LanguageHandler` base class

### 3. Write Tests

```bash
# Unit test for new plugin
tests/unit/test_go_handler.py

# Integration test with Go fixture project
tests/integration/fixtures/go_unstructured/
```

### 4. Run Quality Checks

```bash
# Format code
black src/brownfield/

# Run linter
pylint src/brownfield/

# Check complexity
lizard -C 10 src/brownfield/

# Run tests
pytest
```

### 5. Commit and Push

```bash
git add .
git commit -m "[brownfield] Add Go language plugin support"
git push origin feature/add-go-language-support
```

## Common Development Tasks

### Adding a New Language Plugin

1. **Create handler file**: `src/brownfield/plugins/<language>_handler.py`
2. **Implement interface**:
   ```python
   from brownfield.plugins.base import LanguageHandler
   from brownfield.plugins.registry import register_handler

   @register_handler('rust')
   class RustHandler(LanguageHandler):
       def detect(self, project_root: Path) -> DetectionResult | None:
           if (project_root / 'Cargo.toml').exists():
               return DetectionResult('rust', ConfidenceLevel.HIGH, None, None)
           return None

       def get_standard_structure(self) -> dict[str, list[str]]:
           return {
               'src': ['lib.rs', 'main.rs'],
               'tests': ['integration_test.rs'],
               'benches': ['benchmark.rs']
           }

       def bootstrap_tests(self, project_root: Path) -> TestSetupResult:
           # Add cargo test setup
           pass

       def install_quality_gates(self, project_root: Path) -> QualitySetupResult:
           # Add clippy, rustfmt
           pass
   ```

3. **Write contract test**: Ensure `tests/contract/test_plugin_interface.py` includes new language
4. **Create integration fixture**: `tests/integration/fixtures/rust_unstructured/`

### Adding a New CLI Command

1. **Create command file**: `src/brownfield/cli/<command>.py`
2. **Define click command**:
   ```python
   import click
   from brownfield.cli.commands import brownfield

   @brownfield.command('mycommand')
   @click.option('--flag', is_flag=True, help='Optional flag')
   def my_command(flag: bool):
       """Brief description of command."""
       click.echo("Executing my command...")
   ```

3. **Import in** `src/brownfield/cli/commands.py`:
   ```python
   from brownfield.cli.mycommand import my_command
   ```

### Adding a New Readiness Gate

1. **Edit** `src/brownfield/models/gate.py`:
   ```python
   READINESS_GATES.append(
       ReadinessGate(
           name="API Documentation",
           description="Percentage of public APIs with docstrings",
           threshold=0.8,
           verification_command="pydocstyle --count src/",
           remediation_guidance="Add docstrings to public functions/classes"
       )
   )
   ```

2. **Update validation logic** in `src/brownfield/remediation/validation.py`

## Troubleshooting

### Issue: `brownfield: command not found`

**Solution**: Ensure virtual environment is activated and package installed in editable mode:
```bash
source .venv/bin/activate
pip install -e .
```

### Issue: Import errors when running tests

**Solution**: Install test dependencies:
```bash
pip install -r requirements-dev.txt
```

### Issue: Git operations fail with "Not a git repository"

**Solution**: BrownKit requires projects to be git repositories:
```bash
cd /path/to/your/project
git init
git add .
git commit -m "Initial commit"
```

### Issue: Assessment reports "missing tools"

**Solution**: Install language-specific tools for your project:

- **Python**: `pip install pytest black pylint bandit`
- **JavaScript**: `npm install -g jest eslint prettier`
- **Rust**: `rustup component add clippy rustfmt`

## Next Steps

### Learn More About Architecture

- **[data-model.md](./data-model.md)**: Entity schemas and relationships
- **[research.md](./research.md)**: Technology decisions and patterns
- **[contracts/](./contracts/)**: CLI command contracts and plugin interface

### Explore Codebase

Key modules to understand:

1. **`src/brownfield/orchestrator/phase_machine.py`**: Phase transition logic
2. **`src/brownfield/assessment/language_detector.py`**: Language detection engine
3. **`src/brownfield/git/safe_commit.py`**: Git safety patterns
4. **`src/brownfield/plugins/base.py`**: Plugin interface definition

### Run Full Workflow

Test the complete workflow on a fixture project:

```bash
cd tests/fixtures/python_messy/
brownfield assess --quick
brownfield structure                   # Generates plan
# [Manually refactor with IDE tools]
brownfield structure --verify         # Verify refactoring
brownfield testing --coverage-target=0.6
brownfield quality
brownfield validate
brownfield graduate
```

Check the generated artifacts:
- `brownfield-graduation-report.md`
- `.specify/memory/constitution.md`
- `.specify/memory/brownfield-archive/`

## Contributing Guidelines

### Code Style

- **Formatting**: Use `black` with default settings
- **Line length**: 100 characters (configured in `pyproject.toml`)
- **Type hints**: Required for all public functions
- **Docstrings**: Required for public classes/functions (Google style)

### Git Commit Messages

Follow conventional commits format:

```
[brownfield] <category>: <summary>

<optional body>

Phase: <phase-name>
```

**Categories**: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

### Pull Request Process

1. Create feature branch from `main`
2. Implement changes with tests
3. Ensure all tests pass: `pytest`
4. Ensure code quality: `black . && pylint src/`
5. Push and create PR
6. Address review feedback
7. Squash commits before merge

## Additional Resources

- **Speckit Documentation**: https://github.com/specify/speckit
- **Click Documentation**: https://click.palletsprojects.com/
- **GitPython Documentation**: https://gitpython.readthedocs.io/
- **Pytest Documentation**: https://docs.pytest.org/

## Getting Help

- **Issues**: https://github.com/your-org/brownkit/issues
- **Discussions**: https://github.com/your-org/brownkit/discussions
- **Slack**: #brownkit channel

---

**Welcome to BrownKit development!** Start by running the assessment on fixture projects, explore the codebase modules, and contribute new language plugins or CLI commands.
