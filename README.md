# BrownKit

Brownfield companion to [Spec-Kit](https://github.com/specify/speckit). Automates the transition from legacy codebases to spec-ready, tested, quality-gated projects.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Spec-Kit Compatible](https://img.shields.io/badge/Spec--Kit-Compatible-brightgreen.svg)](https://github.com/specify/speckit)
[![Tests](https://img.shields.io/badge/tests-54%20passing-success.svg)](./tests)

```
Messy Legacy Code -> BrownKit -> Clean, Tested Codebase -> Spec-Kit -> Production
```

## What It Does

BrownKit takes a disorganized codebase and prepares it for spec-driven development:

1. **Assess** -- Detect language, collect baseline metrics, identify tech debt
2. **Structure** -- Reorganize files to src/, tests/, docs/ conventions
3. **Test** -- Bootstrap test frameworks, generate tests, reach 60%+ coverage
4. **Quality** -- Install linters, formatters, pre-commit hooks; enforce complexity < 10
5. **Validate** -- Check 7 readiness gates before graduation
6. **Graduate** -- Generate a Spec-Kit constitution and archive artifacts

Every change is an atomic git commit. Failed builds auto-revert.

## Quick Start

### Installation

**Option 1: devenv (recommended for NixOS)**

```bash
git clone https://github.com/jacopone/brownkit.git
cd brownkit
direnv allow
```

**Option 2: Standard Python**

```bash
git clone https://github.com/jacopone/brownkit.git
cd brownkit
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Usage

```bash
cd /path/to/your/project

brownfield assess       # Analyze codebase
brownfield structure    # Fix directory layout
brownfield testing      # Add test infrastructure
brownfield quality      # Install quality gates
brownfield graduate     # Generate Spec-Kit constitution
```

## Supported Languages

| Language | Tests | Linter | Formatter | Security |
|----------|-------|--------|-----------|----------|
| Python | pytest | ruff/pylint | black | bandit |
| JavaScript | jest | eslint | prettier | npm audit |
| Rust | cargo test | clippy | rustfmt | cargo audit |
| Go | go test | golangci-lint | gofmt | gosec |

## Readiness Gates

BrownKit validates 7 gates before graduation to Spec-Kit:

| Gate | Requirement |
|------|-------------|
| Structure | src/, tests/, docs/ layout |
| Test Coverage | 60%+ on core modules |
| Build Status | Passing |
| Linting | Configured and passing |
| Complexity | CCN < 10 average |
| Security | No critical vulnerabilities |
| Documentation | README and architecture docs present |

## Configuration

Configure via `.brownfield.toml`:

```toml
[brownfield]
analysis_mode = "quick"
coverage_target = 0.6
complexity_threshold = 10

[brownfield.ignore]
paths = ["vendor/", "third_party/", "generated/"]
```

## Testing

54 tests covering assessment workflows, checkpoint recovery, constitution generation, state migration, phase transitions, and end-to-end scenarios.

```bash
pytest                          # All tests
pytest tests/unit/              # Unit tests
pytest tests/integration/       # Integration tests
pytest --cov=src/brownfield     # With coverage
```

## Documentation

- [Installation Guide](docs/installation.md)
- [Workflow Guide](docs/workflow.md)
- [CLI Reference](docs/cli-reference.md)
- [Environment Variables](docs/environment-variables.md)
- [Spec-Kit Integration](docs/speckit-integration.md)
- [Testing Guide](docs/testing-guide.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT -- see [LICENSE](LICENSE).
