# Brownfield-Kit

AI-driven workflow for transitioning brownfield codebases to Speckit-ready state with automated assessment, structure fixes, testing infrastructure, and quality gates.

## Overview

Brownfield-Kit is a Python CLI tool that helps transform poorly-maintained codebases into high-quality, well-tested projects ready for spec-driven development with Speckit.

### Key Features

- **Automated Assessment**: Detect language/framework, measure baseline metrics, identify tech debt
- **Structure Remediation**: Organize directories to ecosystem conventions, update import paths
- **Test Infrastructure**: Bootstrap test frameworks, generate contract tests, achieve 60% coverage
- **Quality Gates**: Install linters, formatters, pre-commit hooks, enforce complexity < 10
- **Validation & Graduation**: Check 7 readiness gates, generate Speckit constitution
- **Re-entry Support**: Detect quality regressions, allow workflow re-entry

## Prerequisites

- Python 3.11 or higher
- Git 2.30+
- Language-specific tools for your project (pytest, npm, cargo, etc.)

## Installation

### From Source

```bash
git clone https://github.com/brownfield-kit/brownfield-kit.git
cd brownfield-kit
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
pip install -e .
```

### Verify Installation

```bash
brownfield --version
```

## Quick Start

### 1. Assess Your Codebase

```bash
cd /path/to/your/project
brownfield assess --quick
```

This generates:
- `.specify/memory/assessment-report.md` - Detailed analysis
- `.specify/memory/brownfield-state.json` - Machine-readable state
- Baseline metrics for tracking progress

### 2. Fix Directory Structure

```bash
brownfield structure
```

This will:
- Move files to standard directories (src/, tests/, docs/)
- Update import paths automatically
- Create separate git commits for each change
- Auto-revert on build failures

### 3. Add Test Infrastructure

```bash
brownfield testing --coverage-target=0.6
```

This adds:
- Test framework (pytest, jest, cargo test, etc.)
- Contract tests for public APIs
- Smoke tests for basic functionality
- Achieves 60% coverage on core modules

### 4. Install Quality Gates

```bash
brownfield quality
```

This configures:
- Linters (pylint, eslint, clippy, golangci-lint)
- Formatters (black, prettier, rustfmt, gofmt)
- Pre-commit hooks
- Complexity analysis and security scanning

### 5. Validate & Graduate

```bash
brownfield validate
brownfield graduate
```

This checks all 7 readiness gates and generates:
- Speckit constitution tailored to your project
- Graduation report with before/after metrics
- Archived brownfield artifacts

## The 6-Phase Workflow

```
Assessment → Structure → Testing → Quality → Validation → Graduation
```

Each phase has clear entry/exit criteria and creates atomic git commits for reversibility.

### Re-entry & Resumption

Brownfield-Kit supports two types of workflow interruption handling:

**Quality Regression Re-entry**: If metrics degrade after graduation, the tool automatically detects regression and re-enters the appropriate phase:

```bash
brownfield assess  # After graduation
# Detects: Test coverage dropped from 60% to 45%
# Automatically re-enters: TESTING phase
# Recommendation: Run `brownfield testing` to restore coverage
```

**Checkpoint-based Resumption**: If a command is interrupted (Ctrl+C, crash, connection loss), resume from the last checkpoint:

```bash
brownfield testing
# ... gets interrupted at 40% progress ...

brownfield resume
# Shows checkpoints:
# ✓ framework_installed (completed)
# • test_generation (in_progress) - 12/30 modules
# [ ] coverage_verification (pending)

# Press Enter to resume from test_generation
```

## Supported Languages

- **Python** (3.9+): pytest, black, pylint, bandit
- **JavaScript/Node**: jest, prettier, eslint, npm audit
- **Rust**: cargo test, rustfmt, clippy, cargo audit
- **Go**: go test, gofmt, golangci-lint, gosec

## CLI Commands

### Core Workflow Commands

- `brownfield assess` - Run codebase analysis and baseline metrics collection
- `brownfield structure` - Generate refactoring plan or verify structure compliance
- `brownfield testing` - Bootstrap test framework and achieve target coverage
- `brownfield quality` - Install linters, formatters, and quality gates
- `brownfield validate` - Check all 7 readiness gates before graduation
- `brownfield graduate` - Generate Speckit constitution and archive artifacts

### Utility Commands

- `brownfield resume` - Resume interrupted workflow from checkpoint
- `brownfield status` - Show current phase, metrics, and progress
- `brownfield install-completion` - Install shell completion (bash/zsh/fish)

### Command Options

```bash
brownfield assess --quick              # Fast analysis (default)
brownfield assess --full               # Comprehensive analysis
brownfield assess --force              # Force re-assessment
brownfield assess --language python    # Override language detection

brownfield structure                   # Generate refactoring plan
brownfield structure --verify          # Verify structure after manual refactoring

brownfield testing --coverage-target 0.6  # Set coverage target

brownfield status                      # Human-readable output
brownfield status --json               # JSON output for CI/CD
brownfield status --verbose            # Show phase timeline

brownfield resume                      # List checkpoints and resume
brownfield resume --restart            # Clear checkpoint and restart phase

brownfield install-completion --shell bash   # Install bash completion
brownfield install-completion --shell zsh    # Install zsh completion
brownfield install-completion --shell fish   # Install fish completion
```

## Configuration

Create `.brownfield.toml` in your project root:

```toml
[brownfield]
analysis_mode = "quick"  # or "full"
coverage_target = 0.6
complexity_threshold = 10

[brownfield.ignore]
paths = ["vendor/", "third_party/"]
```

## Environment Variables

Brownfield-Kit supports environment variables for flexible configuration:

### Path Configuration

- `BROWNFIELD_PROJECT_ROOT` - Override project root directory
  ```bash
  export BROWNFIELD_PROJECT_ROOT=/path/to/project
  brownfield assess  # Runs on /path/to/project
  ```

- `BROWNFIELD_STATE_DIR` - Override state directory (default: `.specify/memory`)
  ```bash
  export BROWNFIELD_STATE_DIR=/custom/state/dir
  ```

- `BROWNFIELD_REPORTS_DIR` - Override reports directory (default: `.specify/memory`)
  ```bash
  export BROWNFIELD_REPORTS_DIR=/custom/reports/dir
  ```

- `BROWNFIELD_TEMPLATES_DIR` - Custom templates directory
  ```bash
  export BROWNFIELD_TEMPLATES_DIR=/custom/templates
  ```

### Behavior Configuration

- `BROWNFIELD_DEBUG` - Enable debug logging (`true`/`1`/`yes`)
  ```bash
  export BROWNFIELD_DEBUG=true
  brownfield assess  # Shows debug output
  ```

- `BROWNFIELD_ANALYSIS_MODE` - Default analysis mode (`quick`/`full`)
  ```bash
  export BROWNFIELD_ANALYSIS_MODE=full
  brownfield assess  # Uses full analysis by default
  ```

- `BROWNFIELD_FORCE_LANGUAGE` - Force language detection (`python`/`javascript`/`rust`/`go`)
  ```bash
  export BROWNFIELD_FORCE_LANGUAGE=python
  brownfield assess  # Skips language detection
  ```

See [docs/environment-variables.md](docs/environment-variables.md) for detailed documentation and CI/CD examples.

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Brownfield Quality Check

on:
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install brownfield
        run: pip install brownfield-kit

      - name: Check brownfield status
        run: |
          STATUS=$(brownfield status --json | jq -r '.current_phase')
          echo "Current phase: $STATUS"

          if [ "$STATUS" != "graduated" ]; then
            echo "Project has not graduated from brownfield workflow"
            exit 1
          fi

      - name: Validate readiness gates
        run: brownfield validate --json > validation.json

      - name: Upload validation report
        uses: actions/upload-artifact@v3
        with:
          name: brownfield-validation
          path: validation.json
```

### Pre-commit Hook Example

```bash
# .git/hooks/pre-commit
#!/bin/bash
# Check brownfield status before allowing commits

STATUS=$(brownfield status --json 2>/dev/null | jq -r '.current_phase // "unknown"')

if [ "$STATUS" = "unknown" ]; then
  echo "Warning: Brownfield state not found. Run 'brownfield assess' first."
  exit 1
fi

if [ "$STATUS" != "graduated" ] && [ "$STATUS" != "validation" ]; then
  echo "Warning: Project is in $STATUS phase (not yet graduated)"
  echo "Consider running: brownfield $STATUS"
fi

# Allow commit but warn user
exit 0
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/brownfield-kit/brownfield-kit.git
cd brownfield-kit
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
```

### Run Tests

```bash
pytest                              # All tests
pytest tests/unit/                  # Unit tests only
pytest tests/contract/              # Contract tests
pytest tests/integration/           # Integration tests
pytest --cov=src/brownfield         # With coverage
```

### Code Quality

```bash
black src/brownfield/               # Format code
pylint src/brownfield/              # Lint code
lizard -C 10 src/brownfield/        # Check complexity
```

## Architecture

Brownfield-Kit uses a plugin architecture:

- **CLI Layer**: Click-based commands
- **Orchestrator**: Phase state machine
- **Assessment Engine**: Language detection, metrics collection
- **Remediation**: Structure, testing, quality modules
- **Plugins**: Language-specific handlers (Python, JS, Rust, Go)
- **Git Layer**: Safe commits, auto-revert, history tracking
- **State Layer**: JSON persistence, checkpoints, decision logs

## Constitution Principles

1. **Assessment-Driven Development**: All changes preceded by automated analysis
2. **Safety-Net First**: Testing infrastructure before refactoring
3. **Incremental Remediation**: Small, verifiable, committable changes
4. **Transparent Reasoning**: AI documents decisions with confidence levels
5. **Measurable Progress**: Quantitative gates for phase transitions
6. **Structure Integrity**: Follow ecosystem conventions
7. **Reversibility**: All changes git-trackable and revertable

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- [Documentation](https://brownfield-kit.readthedocs.io)
- [Issue Tracker](https://github.com/brownfield-kit/brownfield-kit/issues)
- [Speckit](https://github.com/specify/speckit)

## Support

- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share ideas
- Slack: #brownfield-kit channel
