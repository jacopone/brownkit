# 🏗️ BrownKit

**The official brownfield companion to [Spec-Kit](https://github.com/specify/speckit)** - Transform legacy codebases into spec-ready, production-grade projects with AI-driven automation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Spec-Kit Compatible](https://img.shields.io/badge/Spec--Kit-Compatible-brightgreen.svg)](https://github.com/specify/speckit)
[![Tests](https://img.shields.io/badge/tests-77%20passing-success.svg)](./tests)

---

## 🎯 What is BrownKit?

**BrownKit is the missing bridge between messy legacy code and spec-driven development.**

Before you can leverage Spec-Kit's powerful spec-driven workflow, your codebase needs to meet basic quality standards. BrownKit automates the entire transition journey - from chaotic brownfield to clean, testable, spec-ready code.

```
Messy Legacy Code → 🏗️ BrownKit → Clean, Tested Codebase → 📋 Spec-Kit → Production Excellence
```

### Why BrownKit?

**The Problem**: You want to adopt spec-driven development with Spec-Kit, but your codebase is:
- ❌ Poorly organized with files scattered everywhere
- ❌ Missing tests or has <30% coverage
- ❌ No linting, formatting, or quality gates
- ❌ High complexity and technical debt
- ❌ Not ready for AI-assisted development

**The Solution**: BrownKit automates the entire cleanup process:
- ✅ **Automated Assessment** - Detect language, measure metrics, identify debt
- ✅ **Structure Remediation** - Reorganize to ecosystem standards
- ✅ **Test Infrastructure** - Bootstrap frameworks, generate tests, achieve 60%+ coverage
- ✅ **Quality Gates** - Install linters, formatters, pre-commit hooks
- ✅ **Spec-Kit Graduation** - Generate constitution, achieve readiness
- ✅ **Safety First** - Every change is atomic, committed, and revertable

**Result**: A production-ready codebase that seamlessly integrates with Spec-Kit's workflow.

---

## 🚀 The BrownKit → Spec-Kit Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                      BROWNFIELD STATE                            │
│  • Scattered files, no structure                                │
│  • Missing or inadequate tests                                  │
│  • No quality enforcement                                       │
│  • High technical debt                                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   🏗️  BROWNKIT WORKFLOW                          │
│                                                                  │
│  Phase 1: ASSESSMENT                                            │
│    └─→ Detect language, baseline metrics, identify gaps        │
│                                                                  │
│  Phase 2: STRUCTURE                                             │
│    └─→ Reorganize to src/, tests/, docs/ conventions           │
│                                                                  │
│  Phase 3: TESTING                                               │
│    └─→ Bootstrap framework, generate tests, 60%+ coverage      │
│                                                                  │
│  Phase 4: QUALITY                                               │
│    └─→ Install linters, formatters, hooks, enforce <10 CCN    │
│                                                                  │
│  Phase 5: VALIDATION                                            │
│    └─→ Check 7 readiness gates for graduation                 │
│                                                                  │
│  Phase 6: GRADUATION                                            │
│    └─→ Generate Spec-Kit constitution, archive artifacts       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    SPEC-READY STATE                              │
│  ✓ Organized structure (src/, tests/, docs/)                   │
│  ✓ 60%+ test coverage with framework                           │
│  ✓ Quality gates enforced (linters, formatters)                │
│  ✓ Complexity <10, security scanned                            │
│  ✓ Spec-Kit constitution generated                             │
│  ✓ Ready for spec-driven development                           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   📋  SPEC-KIT WORKFLOW                          │
│  • Write feature specs                                          │
│  • AI-assisted implementation                                   │
│  • Continuous quality enforcement                               │
│  • Production-ready delivery                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start

### Installation

**Option 1: Using devenv (Recommended for NixOS)**

```bash
git clone https://github.com/jacopone/brownkit.git
cd brownkit
direnv allow  # Auto-activates environment
```

**Option 2: Standard Python**

```bash
git clone https://github.com/jacopone/brownkit.git
cd brownkit
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Transform Your Codebase in 5 Commands

```bash
# 1. Assess your codebase
cd /path/to/your/messy/project
brownfield assess

# 2. Fix structure
brownfield structure

# 3. Add tests
brownfield testing

# 4. Enforce quality
brownfield quality

# 5. Graduate to Spec-Kit
brownfield graduate
```

**That's it!** Your codebase is now ready for spec-driven development with Spec-Kit.

---

## 🎓 Spec-Kit Integration

BrownKit is designed to prepare codebases for Spec-Kit's workflow:

### 1. **Generates Spec-Kit Constitution**

Upon graduation, BrownKit creates `.specify/memory/constitution.md` with project-specific principles:

```markdown
# Project Constitution

## Structure Principles
1. All source code in src/ following Python package structure
2. All tests in tests/ mirroring src/ organization

## Testing Principles
3. Maintain 60%+ test coverage on core modules
4. Contract tests required for all public APIs

## Quality Principles
5. Cyclomatic complexity <10 enforced by pre-commit
6. Ruff linter + Black formatter required
7. No critical/high vulnerabilities in dependencies
```

### 2. **Compatible State Management**

BrownKit uses `.specify/memory/state.json` with `workflow` field for Spec-Kit interoperability:

```json
{
  "workflow": "brownfield",
  "schema_version": "1.0",
  "current_phase": "graduated",
  "graduation_timestamp": "2025-10-23T10:30:00Z"
}
```

Spec-Kit can detect graduated projects and apply appropriate workflows.

### 3. **Enforces Spec-Kit Prerequisites**

BrownKit validates **7 readiness gates** before graduation:

| Gate | Requirement | Why It Matters for Spec-Kit |
|------|-------------|----------------------------|
| **Structure** | src/, tests/, docs/ organization | Spec-Kit assumes conventional layout |
| **Test Coverage** | ≥60% on core modules | Spec-Kit workflows rely on test safety net |
| **Build Status** | Passing builds | Spec-Kit can't work with broken projects |
| **Linting** | Configured + passing | Spec-Kit assumes code quality baseline |
| **Complexity** | CCN <10 average | Spec-Kit specs require maintainable code |
| **Security** | No critical vulnerabilities | Spec-Kit workflows shouldn't introduce risk |
| **Documentation** | Basic README, architecture docs | Spec-Kit needs context for AI assistance |

### 4. **Atomic Git History**

Every BrownKit change is a separate commit:

```
a47b8b6 feat: Add workflow orchestrators and critical fixes
c06c277 refactor: Rename project from brownfield-kit to brownkit
3cf3e33 feat: Complete Brownfield-Kit v0.1.0 MVP+ implementation
```

Spec-Kit can trace provenance and understand project evolution.

---

## 📊 Real-World Impact

### Before BrownKit
```
├── random_files_everywhere.py
├── old_stuff/
│   ├── legacy_code.py
│   └── tests.py (12% coverage)
├── utils.py (CCN: 45)
└── README.md (outdated)
```

**Metrics**: 12% test coverage, CCN avg 28, no linting, 15 high vulnerabilities

### After BrownKit
```
├── src/
│   └── myproject/
│       ├── __init__.py
│       ├── core.py (CCN: 8)
│       └── utils.py (CCN: 6)
├── tests/
│   ├── test_core.py
│   └── test_utils.py (68% coverage)
├── docs/
│   └── architecture.md
├── .specify/
│   └── memory/
│       ├── constitution.md
│       └── state.json (graduated)
└── README.md (complete)
```

**Metrics**: 68% test coverage, CCN avg 7, ruff + black configured, 0 vulnerabilities

**Ready for Spec-Kit**: ✅ Constitution generated, quality gates enforced

---

## 🛠️ Core Features

### Automated Assessment
- **Language Detection**: Python, JavaScript, Rust, Go
- **Baseline Metrics**: Coverage, complexity, vulnerabilities, build status
- **Tech Debt Analysis**: Identify high-priority issues
- **Report Generation**: `.specify/memory/assessment-report.md`

### Structure Remediation
- **Ecosystem Conventions**: src/, tests/, docs/ organization
- **Import Path Updates**: Automatic refactoring after moves
- **Atomic Commits**: Each restructure is a separate, revertable commit
- **Build Verification**: Auto-revert if tests fail after structure changes

### Test Infrastructure
- **Framework Bootstrap**: pytest, jest, cargo test, go test
- **Contract Test Generation**: Public API coverage
- **Smoke Test Creation**: Basic functionality verification
- **Coverage Tracking**: Achieve and maintain 60%+ coverage

### Quality Gates
- **Linter Installation**: pylint, eslint, clippy, golangci-lint
- **Formatter Setup**: black, prettier, rustfmt, gofmt
- **Pre-commit Hooks**: Enforce quality on every commit
- **Complexity Analysis**: CCN <10 enforced with lizard
- **Security Scanning**: Detect vulnerabilities with bandit, npm audit, cargo audit

### Workflow Orchestration (v0.2.0)
- **Dual CLI Interface**: Granular commands + workflow orchestrators
- **Phase Validation**: Strict transition rules prevent phase skipping
- **Checkpoint Recovery**: Resume interrupted operations
- **Progress Tracking**: Rich console displays with tables and trees
- **State Persistence**: Atomic writes, auto-migration from v0.1.0

---

## 📚 Documentation

- **[Installation Guide](docs/installation.md)** - Detailed setup for all platforms
- **[Workflow Guide](docs/workflow.md)** - Complete 6-phase walkthrough
- **[CLI Reference](docs/cli-reference.md)** - All commands and options
- **[Environment Variables](docs/environment-variables.md)** - Configuration options
- **[GitHub Actions Integration](docs/github-actions.md)** - CI/CD examples
- **[Spec-Kit Integration](docs/speckit-integration.md)** - How BrownKit prepares for Spec-Kit
- **[Testing Guide](docs/testing-guide.md)** - Test suite, fixtures, and coverage

---

## 🧪 Supported Languages

| Language | Test Framework | Linter | Formatter | Security Scanner |
|----------|----------------|--------|-----------|------------------|
| **Python** | pytest | ruff/pylint | black | bandit |
| **JavaScript** | jest | eslint | prettier | npm audit |
| **Rust** | cargo test | clippy | rustfmt | cargo audit |
| **Go** | go test | golangci-lint | gofmt | gosec |

---

## 🎮 CLI Commands

### Workflow Orchestrators (v0.2.0)

High-level commands for complete workflow phases:

```bash
brownfield.assess     # Full assessment + baseline metrics
brownfield.plan       # Generate unified remediation plan
brownfield.remediate  # Execute structure + testing + quality
brownfield.validate   # Check all 7 readiness gates
brownfield.graduate   # Generate constitution + archive
```

### Granular Commands

Fine-grained control for power users:

```bash
brownfield assess           # Run codebase analysis
brownfield structure        # Fix directory organization
brownfield testing          # Add test infrastructure
brownfield quality          # Install quality gates
brownfield validate         # Check readiness gates
brownfield graduate         # Generate Spec-Kit constitution
brownfield resume           # Resume interrupted workflow
brownfield status           # Show current state
```

### Options & Flags

```bash
# Assessment
brownfield assess --quick              # Fast analysis (default)
brownfield assess --full               # Comprehensive analysis
brownfield assess --force              # Force re-assessment

# Structure
brownfield structure                   # Generate refactoring plan
brownfield structure --verify          # Verify manual changes

# Testing
brownfield testing --coverage-target 0.7  # Set coverage goal

# Status
brownfield status                      # Human-readable output
brownfield status --json               # JSON for CI/CD
brownfield status --verbose            # Show timeline

# Resume
brownfield resume                      # Interactive checkpoint selection
brownfield resume --restart            # Clear and restart phase
```

---

## 🔧 Configuration

### Project Configuration (`.brownfield.toml`)

```toml
[brownfield]
analysis_mode = "quick"         # or "full"
coverage_target = 0.6           # 60% minimum coverage
complexity_threshold = 10       # CCN limit

[brownfield.ignore]
paths = ["vendor/", "third_party/", "generated/"]

[brownfield.speckit]
constitution_path = ".specify/memory/constitution.md"
generate_templates = true       # Generate Spec-Kit slash command templates
```

### Environment Variables

```bash
# Path overrides
export BROWNFIELD_PROJECT_ROOT=/path/to/project
export BROWNFIELD_STATE_DIR=.specify/memory

# Behavior
export BROWNFIELD_DEBUG=true
export BROWNFIELD_ANALYSIS_MODE=full

# Language override
export BROWNFIELD_FORCE_LANGUAGE=python
```

See [docs/environment-variables.md](docs/environment-variables.md) for complete reference.

---

## 🏭 CI/CD Integration

### GitHub Actions Example

```yaml
name: Validate Spec-Kit Readiness

on:
  pull_request:
    branches: [main]

jobs:
  brownfield-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install BrownKit
        run: pip install brownkit

      - name: Validate graduation status
        run: |
          STATUS=$(brownfield status --json | jq -r '.current_phase')

          if [ "$STATUS" != "graduated" ]; then
            echo "❌ Project not ready for Spec-Kit workflow"
            echo "Current phase: $STATUS"
            brownfield status --verbose
            exit 1
          fi

          echo "✅ Project graduated - ready for Spec-Kit"

      - name: Validate readiness gates
        run: brownfield validate --json > validation.json

      - name: Upload validation report
        uses: actions/upload-artifact@v3
        with:
          name: brownfield-validation
          path: validation.json
```

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Layer (Click)                     │
│  • Workflow orchestrators (assess, plan, remediate)     │
│  • Granular commands (structure, testing, quality)      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Orchestrator Layer (Phase Machine)          │
│  • State transitions with validation                    │
│  • Checkpoint management                                │
│  • Progress tracking                                    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  Assessment Engine                       │
│  • Language detection (AST-based)                       │
│  • Metrics collection (coverage, CCN, vulns)           │
│  • Tech debt identification                             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│             Remediation Layer (Plugins)                  │
│  • Python: pytest, black, ruff, bandit                  │
│  • JavaScript: jest, prettier, eslint, npm audit        │
│  • Rust: cargo test, rustfmt, clippy, cargo audit      │
│  • Go: go test, gofmt, golangci-lint, gosec            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         Git Layer (Atomic Commits + Safety)              │
│  • Separate commits per change                         │
│  • Auto-revert on build failures                       │
│  • History tracking for audit trail                    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│    State Layer (Spec-Kit Compatible Persistence)        │
│  • JSON state in .specify/memory/state.json            │
│  • Workflow discriminator field                        │
│  • Checkpoint persistence                              │
│  • Auto-migration from v0.1.0                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🎓 Constitution Principles

These principles guide BrownKit's automation and are embedded in the generated Spec-Kit constitution:

1. **Assessment-Driven Development** - All changes preceded by automated analysis
2. **Safety-Net First** - Testing infrastructure before refactoring
3. **Incremental Remediation** - Small, verifiable, committable changes
4. **Transparent Reasoning** - AI documents decisions with confidence levels
5. **Measurable Progress** - Quantitative gates for phase transitions
6. **Structure Integrity** - Follow ecosystem conventions (src/, tests/, docs/)
7. **Reversibility** - All changes git-trackable and revertable

---

## 🧪 Testing & Quality

**BrownKit v0.2.0** achieves production-ready quality standards:

- ✅ **77 passing tests** (100% pass rate)
- ✅ **19 unit tests** for checkpoint and task models
- ✅ **41 unit tests** for phase validation and transitions
- ✅ **11 unit tests** for state migration
- ✅ **4 integration tests** for end-to-end workflow
- ✅ **2 remediation tests** for orchestrator models
- ✅ **All ruff checks passing** (no linting errors)
- ✅ **Complexity <10** (enforced with lizard)

Run the test suite:

```bash
# Using devenv
test                    # Run all tests
test-cov                # With coverage report
test-integration        # Integration tests only

# Using pytest directly
pytest                  # All tests
pytest tests/unit/      # Unit tests
pytest tests/integration/  # Integration tests
pytest --cov=src/brownfield  # With coverage
```

See [docs/testing-guide.md](docs/testing-guide.md) for comprehensive testing documentation.

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **[BrownKit Documentation](https://brownkit.readthedocs.io)** - Complete guides and references
- **[Spec-Kit](https://github.com/specify/speckit)** - The spec-driven development workflow
- **[Issue Tracker](https://github.com/jacopone/brownkit/issues)** - Report bugs and request features
- **[Discussions](https://github.com/jacopone/brownkit/discussions)** - Ask questions and share ideas
- **[Changelog](CHANGELOG.md)** - Release history and migration guides

---

## 💬 Support

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share ideas
- **Documentation**: Comprehensive guides at [brownkit.readthedocs.io](https://brownkit.readthedocs.io)

---

<div align="center">

**BrownKit** + **Spec-Kit** = **Production Excellence**

Transform legacy code → Enforce quality → Ship with confidence

Made with 🏗️ by the Spec-Kit community

</div>
