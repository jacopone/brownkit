# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Unit tests for individual modules (target: 80% coverage)
- Additional language plugins (TypeScript, Java, C++, PHP)
- GUI/TUI mode for interactive workflow
- Performance benchmarks and regression tracking
- Property-based tests with hypothesis
- PyPI package distribution

---

## [0.1.0] - 2025-10-21

### 🎉 Initial Release - MVP+

First production-ready release of BrownKit with comprehensive features for transforming brownfield codebases into Speckit-ready projects.

### Added

#### Core Features
- **CLI Commands** (9 total):
  - `brownfield assess` - Codebase analysis with baseline metrics collection
  - `brownfield structure` - Refactoring plan generation and structure verification
  - `brownfield testing` - Test framework bootstrapping with coverage targets
  - `brownfield quality` - Linter, formatter, and quality gate installation
  - `brownfield validate` - Readiness gate validation before graduation
  - `brownfield graduate` - Speckit constitution generation and artifact archival
  - `brownfield resume` - Checkpoint-based workflow resumption
  - `brownfield status` - Current phase and metrics display (human + JSON output)
  - `brownfield install-completion` - Shell completion for bash/zsh/fish

#### Language Support
- **Python Plugin** - pytest, black, pylint, bandit integration
- **JavaScript Plugin** - jest, prettier, eslint, npm audit integration
- **Rust Plugin** - cargo test, rustfmt, clippy, cargo audit integration
- **Go Plugin** - go test, gofmt, golangci-lint, gosec integration
- Plugin architecture with `LanguageHandler` base class
- Plugin registry for automatic handler discovery

#### Workflow Management
- **6-Phase Workflow**: Assessment → Structure → Testing → Quality → Validation → Graduation
- **Phase State Machine** with transition validation
- **7 Readiness Gates** for graduation criteria
- **Re-entry Support** for quality regression detection
- **Checkpoint System** for interruption recovery
- **Decision Logging** with rationale and confidence levels

#### Assessment Engine
- Automatic language and framework detection
- Baseline metrics collection (coverage, complexity, vulnerabilities)
- Tech debt categorization by severity
- Assessment report generation (Markdown format)
- Support for quick and full analysis modes

#### Remediation Features
- **Structure Remediation**:
  - Human-in-the-loop refactoring approach
  - IDE-specific instructions (PyCharm, VSCode)
  - Structure verification with build integrity checks
  - Shell script generation for file moves
- **Test Infrastructure**:
  - Framework detection and installation
  - Smoke test and contract test generation
  - Iterative coverage improvement to 60%
- **Quality Gates**:
  - Linter and formatter installation
  - Pre-commit hook configuration
  - Complexity analysis (CCN < 10)
  - Security scanning integration

#### Graduation Features
- Speckit constitution generation tailored to project
- Spec/plan/tasks template generation
- Graduation report with before/after metrics
- Brownfield artifact archival
- Structural changes documentation
- Security fixes tracking

#### State Management
- JSON-based state persistence (`.specify/memory/brownfield-state.json`)
- Checkpoint-based resumption (`.specify/memory/checkpoints/`)
- Assessment report storage (`.specify/memory/assessment-report.md`)
- Decision log (`.specify/memory/brownfield-decisions.md`)
- Phase transition tracking with timestamps

### Enhanced Features

#### Environment Variable Configuration (7 variables)
- `BROWNFIELD_PROJECT_ROOT` - Override project root directory
- `BROWNFIELD_STATE_DIR` - Custom state directory
- `BROWNFIELD_REPORTS_DIR` - Custom reports directory
- `BROWNFIELD_TEMPLATES_DIR` - Custom templates directory
- `BROWNFIELD_DEBUG` - Enable debug logging
- `BROWNFIELD_ANALYSIS_MODE` - Default analysis mode (quick/full)
- `BROWNFIELD_FORCE_LANGUAGE` - Force language detection override

#### Error Handling (20+ custom exceptions)
- **State Errors**: `StateNotFoundError`, `InvalidStateError`
- **Phase Errors**: `PhaseTransitionError`, `PhasePreconditionError`
- **Validation Errors**: `GateValidationError`, `StructureValidationError`
- **Tool Errors**: `ToolNotFoundError`, `LanguageDetectionError`
- **Git Errors**: `GitNotFoundError`, `GitDirtyWorkingTreeError`
- **Checkpoint Errors**: `CheckpointNotFoundError`, `CheckpointCorruptedError`
- **File System Errors**: `PermissionError`, `DiskSpaceError`
- All exceptions include actionable suggestions

#### Performance Optimizations
- **In-Memory Cache** with TTL support (5-minute default)
- **Disk Cache** for persistent storage with expiry
- **Cache Decorators**: `@cache_result`, `@disk_cache_result`
- **File Hash Memoization** for change detection
- **Performance Tracker** with min/max/avg timing statistics
- **Progress Estimator** with ETA calculation
- **Time Measurement**: `@timed` decorator, `measure_time()` context manager

#### Utilities
- **Error Handler Module**: `@handle_errors` decorator, validation helpers
- **Cache Module**: In-memory and disk caching with decorators
- **Profiler Module**: Performance tracking and progress estimation
- **Output Formatter**: Consistent CLI output formatting

### Test Infrastructure

#### Test Fixtures (4 projects)
- **python_messy** - High complexity, hardcoded secrets, poor structure
- **javascript_unstructured** - Nested conditionals, security issues
- **rust_complex** - High CCN, plain text passwords
- **go_unorganized** - Hardcoded credentials, no package organization
- All fixtures initialized as git repositories

#### Test Suites
- **Contract Tests** (15+ tests) - Plugin interface compliance verification
- **Integration Tests** (20+ tests) - End-to-end workflow validation
- **Test Configuration** - pytest.ini with markers and coverage settings
- **Shared Fixtures** - conftest.py with auto-marking

#### Test Tooling
- **Test Runner Script** (`scripts/run_tests.sh`) - 8 execution modes
- **Pytest Configuration** - Markers, coverage, output options
- **Coverage Reports** - HTML and terminal output

### Documentation

#### User Documentation
- **README.md** - Comprehensive guide with examples
  - Quick start guide
  - CLI command reference with options
  - 6-phase workflow explanation
  - Re-entry and resumption workflows
  - Environment variable configuration
  - CI/CD integration examples (GitHub Actions, pre-commit hooks)
  - Supported languages and versions

- **Environment Variables Guide** (`docs/environment-variables.md`)
  - Detailed documentation for all 7 variables
  - Use case examples
  - CI/CD integration patterns
  - Docker integration example
  - Troubleshooting guide

#### Developer Documentation
- **Testing Guide** (`tests/README.md`) - 450+ line comprehensive guide
  - Test structure and categories
  - Running tests (quick start + advanced)
  - Test fixtures documentation
  - Writing new tests (templates and patterns)
  - Best practices (AAA pattern, isolation, mocking)
  - CI/CD integration examples
  - Troubleshooting section

- **Implementation Validation** (`docs/implementation-validation.md`)
  - 100% requirement compliance verification
  - Architecture validation
  - Known gaps and recommendations
  - Feature matrix with status

- **Project Status** (`PROJECT_STATUS.md`)
  - Feature completion matrix
  - Architecture overview
  - Quality metrics
  - Deployment readiness checklist
  - Development workflow guide
  - Release checklist

#### Templates
- 7 Slash Command Wrappers (`templates/slash-commands/`)
  - brownfield.assess.md
  - brownfield.structure.md
  - brownfield.testing.md
  - brownfield.quality.md
  - brownfield.validate.md
  - brownfield.graduate.md
  - brownfield.resume.md

### Configuration

#### Project Configuration
- `pyproject.toml` - Python 3.11+ requirement, project metadata
- `pytest.ini` - Test markers, coverage settings, output options
- `.gitignore` - Standard Python patterns, brownfield-specific exclusions
- `.pylintrc` - Linting configuration
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies

### Dependencies

#### Production Dependencies
- `click` (^8.1.0) - CLI framework
- `rich` (^13.0.0) - Terminal UI
- `gitpython` (^3.1.0) - Git operations
- `lizard` (^1.17.0) - Complexity analysis

#### Development Dependencies
- `pytest` (^7.4.0) - Testing framework
- `pytest-cov` (^4.1.0) - Coverage reports
- `black` (^23.0.0) - Code formatting
- `pylint` (^2.17.0) - Linting
- `mypy` (^1.5.0) - Type checking

### Known Limitations

#### By Design
- Manual structure refactoring (human-in-the-loop prevents destructive automation)
- Language-specific tools required (pytest, npm, cargo, go)
- Git repository required (ensures reversibility)

#### Future Enhancements
- Additional language plugins (TypeScript, Java, C++, PHP)
- GUI/TUI mode with real-time progress
- Unit tests for individual modules
- Performance benchmarks
- Property-based tests

### Security

- Custom exception handling prevents information leakage
- No automated credential storage
- Git operations use safe patterns (no force push to main)
- Security scanning integration (bandit, npm audit, cargo audit, gosec)

### Performance

- In-memory caching for fast re-runs (5-minute TTL)
- Disk caching for persistent storage
- File hash memoization for change detection
- Optimized file system operations

---

## Version History

### Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version (X.0.0) - Incompatible API changes
- **MINOR** version (0.X.0) - New functionality (backwards-compatible)
- **PATCH** version (0.0.X) - Bug fixes (backwards-compatible)

### Release Types

- **🎉 Major Release** - Breaking changes, new architecture
- **✨ Minor Release** - New features, enhancements
- **🐛 Patch Release** - Bug fixes, documentation updates
- **🚀 Pre-release** - Alpha, beta, release candidate

### Upgrade Notes

#### From 0.0.x to 0.1.0
- N/A (initial release)

---

## Links

- **Repository**: https://github.com/brownkit/brownkit
- **Documentation**: https://brownkit.readthedocs.io
- **Issue Tracker**: https://github.com/brownkit/brownkit/issues
- **Speckit**: https://github.com/specify/speckit

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

[Unreleased]: https://github.com/brownkit/brownkit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/brownkit/brownkit/releases/tag/v0.1.0
