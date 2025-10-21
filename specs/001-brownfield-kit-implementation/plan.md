# Implementation Plan: Brownfield-Kit Implementation

**Branch**: `001-brownfield-kit-implementation` | **Date**: 2025-10-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-brownfield-kit-implementation/spec.md`

## Summary

Brownfield-Kit is an AI-driven CLI tool system that transitions poorly-maintained codebases to Speckit-ready state through automated assessment, structural remediation, test infrastructure bootstrapping, and quality gate installation. The system implements a 5-phase workflow (Assessment → Structure → Testing → Quality → Validation → Graduation) with safety mechanisms including checkpoint-based resumption, automatic build-failure rollback, and quantitative readiness gates. Upon graduation, it generates a project-specific Speckit constitution and archives all brownfield artifacts.

**Technical Approach**: Python CLI tool with plugin architecture for language-specific handlers (Python, JavaScript, Rust, Go), phase orchestrator enforcing constitution principles, git-based reversibility, and rich terminal UI for user interaction.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**:
- `click` (CLI framework), `gitpython` (git operations), `rich` (terminal UI)
- `lizard` (complexity analysis), `radon` (Python metrics), `coverage.py` (test coverage)
- `bandit` (Python security), subprocess wrappers for `npm audit`, `cargo audit`
- `pygments` (language detection), `pathlib` + `shutil` (file operations)

**Storage**:
- `.specify/memory/brownfield-state.json` (phase tracking, metrics)
- `.specify/memory/brownfield-checkpoint.json` (interruption recovery)
- `.specify/memory/assessment-report.md` (baseline analysis)
- `.specify/memory/brownfield-decisions.md` (decision log with rationale)

**Testing**: `pytest` with coverage reporting, contract tests for plugin interface, integration tests with fixture brownfield repositories

**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)

**Project Type**: Single CLI tool with modular plugin architecture

**Performance Goals**:
- Assessment: <5 min for <50K LOC, <10 min for >100K LOC (quick mode)
- Structure remediation: <30 sec per file operation
- Full workflow: <2 hours for typical projects (<10K LOC)

**Constraints**:
- Must work with/without language tooling (graceful degradation)
- All operations git-reversible (atomic commits, auto-rollback on build failure)
- Interruption-safe via checkpoints
- Monorepo support (treat each language as subproject)

**Scale/Scope**: Target 500 LOC to 100K LOC brownfield codebases in Python/JavaScript/Rust/Go

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance with Brownfield-Kit Constitution Principles

✅ **I. ASSESSMENT_DRIVEN_DEVELOPMENT**
- System implements `LanguageDetector` for evidence-based language/framework detection
- `MetricsCollector` aggregates baseline metrics before any modifications
- `TechDebtAnalyzer` categorizes issues (structural, testing, docs, security)
- Assessment results stored in `.specify/memory/assessment-report.md` with confidence levels

✅ **II. SAFETY_NET_FIRST**
- `TestingBootstrapper` module adds test framework before refactoring
- Achieves 60% coverage requirement via contract test generation for public APIs
- Pre-commit hooks installed by `QualityGatesInstaller` enforce quality gates
- All tests must pass before phase transitions

✅ **III. INCREMENTAL_REMEDIATION**
- `SafeCommit` creates atomic git commits with `[brownfield]` prefix
- Each remediation task targets single file/module/concern
- `AutoRevert` detects build failures and reverts breaking commits automatically
- Maximum change size: 10 files or 500 lines (enforced by approval prompts)

✅ **IV. TRANSPARENT_REASONING**
- `DecisionLogger` records problem, solution, confidence, alternatives, risks
- `ReportGenerator` creates structured Markdown reports
- AI self-assessment documents assumptions and analysis limitations
- Medium/Low confidence changes require human approval

✅ **V. MEASURABLE_PROGRESS**
- `StateStore` tracks baseline vs. current metrics
- Quantitative gates: coverage ≥60%, complexity <10, zero critical vulnerabilities
- `ValidationRunner` enforces all 7 readiness gates before graduation
- Progress reports show delta improvements after each phase

✅ **VI. STRUCTURE_INTEGRITY**
- Plugin system with `LanguageHandler` base class defines standard structures
- Python: `src/`, `tests/`, `pyproject.toml`
- JavaScript: `src/`, `test/`, `package.json`
- Rust: `src/`, `tests/`, `Cargo.toml`
- Go: `cmd/`, `pkg/`, `internal/`, `go.mod`

✅ **VII. REVERSIBILITY**
- All changes create git commits with descriptive messages
- `BranchGuard` prevents force pushes to main/master
- `CheckpointManager` enables interruption recovery
- Human approval required for: file deletion, >5 file renames, build config changes

### Readiness Gates Enforcement

The `ValidationRunner` checks all 7 gates before graduation:
1. **Test Coverage Gate**: ≥60% (via language-specific coverage tools)
2. **Complexity Gate**: CCN <10 (via lizard)
3. **Structure Gate**: Directory organization matches ecosystem conventions
4. **Build Gate**: CI/CD passes with zero warnings
5. **Documentation Gate**: Public APIs have docstrings/JSDoc
6. **Security Gate**: Zero critical vulnerabilities (bandit, npm audit, cargo audit)
7. **Git Hygiene Gate**: No secrets, no large binaries

## Project Structure

### Documentation (this feature)

```
specs/001-brownfield-kit-implementation/
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions and best practices
├── data-model.md        # Phase 1: Entity schemas and relationships
├── quickstart.md        # Phase 1: Developer onboarding guide
├── contracts/           # Phase 1: CLI command contracts
│   ├── cli-commands.md
│   ├── plugin-interface.md
│   └── state-schema.json
└── tasks.md             # Phase 2: Implementation tasks (generated by /speckit.tasks)
```

### Source Code (repository root)

```
/home/guyfawkes/brownfield/
├── src/
│   └── brownfield/
│       ├── cli/                     # CLI command definitions
│       │   ├── commands.py
│       │   ├── assess.py
│       │   ├── structure.py
│       │   ├── testing.py
│       │   ├── quality.py
│       │   ├── validate.py
│       │   ├── graduate.py
│       │   └── resume.py
│       │
│       ├── orchestrator/            # Phase coordination
│       │   ├── phase_machine.py
│       │   ├── gate_validator.py
│       │   ├── checkpoint_manager.py
│       │   └── approval_handler.py
│       │
│       ├── assessment/              # Phase 0: Assessment engine
│       │   ├── language_detector.py
│       │   ├── metrics_collector.py
│       │   ├── tech_debt_analyzer.py
│       │   └── report_generator.py
│       │
│       ├── remediation/             # Phases 1-4: Remediation
│       │   ├── structure.py
│       │   ├── testing.py
│       │   ├── quality.py
│       │   └── validation.py
│       │
│       ├── plugins/                 # Language-specific handlers
│       │   ├── base.py
│       │   ├── registry.py
│       │   ├── python_handler.py
│       │   ├── javascript_handler.py
│       │   ├── rust_handler.py
│       │   └── go_handler.py
│       │
│       ├── git/                     # Git operations
│       │   ├── safe_commit.py
│       │   ├── auto_revert.py
│       │   ├── history_tracker.py
│       │   └── branch_guard.py
│       │
│       ├── state/                   # State persistence
│       │   ├── state_store.py
│       │   ├── checkpoint_store.py
│       │   ├── decision_logger.py
│       │   └── report_writer.py
│       │
│       ├── models/                  # Data models
│       │   ├── assessment.py
│       │   ├── state.py
│       │   ├── metrics.py
│       │   ├── decision.py
│       │   └── gate.py
│       │
│       └── utils/                   # Shared utilities
│           ├── file_operations.py
│           ├── process_runner.py
│           ├── output_formatter.py
│           └── config.py
│
├── tests/
│   ├── contract/                    # API contract tests
│   │   ├── test_cli_commands.py
│   │   ├── test_state_schema.py
│   │   └── test_plugin_interface.py
│   │
│   ├── integration/                 # End-to-end tests
│   │   ├── test_full_workflow.py
│   │   ├── test_interruption.py
│   │   ├── test_reentry.py
│   │   └── fixtures/
│   │       ├── python_messy/
│   │       ├── javascript_legacy/
│   │       └── rust_unstructured/
│   │
│   └── unit/                        # Component unit tests
│       ├── test_language_detector.py
│       ├── test_metrics_collector.py
│       ├── test_phase_machine.py
│       └── test_git_operations.py
│
├── .specify/
│   ├── memory/
│   │   └── constitution.md          # [Exists]
│   │
│   └── templates/
│       ├── commands/                # Slash command definitions
│       │   ├── brownfield.assess.md
│       │   ├── brownfield.structure.md
│       │   ├── brownfield.testing.md
│       │   ├── brownfield.quality.md
│       │   ├── brownfield.validate.md
│       │   ├── brownfield.graduate.md
│       │   └── brownfield.resume.md
│       │
│       └── reports/
│           ├── assessment-report-template.md
│           └── graduation-report-template.md
│
├── pyproject.toml
├── requirements.txt
├── README.md
└── LICENSE
```

**Structure Decision**: Single CLI tool project with plugin architecture. Source code in `src/brownfield/` following Python ecosystem conventions. Tests organized by type (contract/integration/unit) in `tests/`. Slash command templates in `.specify/templates/commands/` for Speckit integration.

## Component Architecture

### Structure Remediation (Phase 4 - Human-in-the-Loop)

**Design Decision**: Structure remediation uses a human-in-the-loop approach rather than automated file moves and import updates. This design choice was made to avoid risks of naive string replacement breaking code.

**Architecture**:

1. **Plan Generation Mode** (default):
   - `StructurePlanGenerator` analyzes current structure
   - Generates detailed markdown refactoring plan with:
     - IDE-specific instructions (PyCharm "Move Module", VSCode drag-and-drop)
     - File move checklist with reasons and import reference counts
     - Configuration file templates
     - Package initialization code
   - Generates shell script for file moves (no import updates)
   - Outputs saved to `.specify/memory/structure-plan.md` and `structure-moves.sh`

2. **Verification Mode** (`--verify` flag):
   - `StructureVerifier` runs 4 compliance checks:
     - Directory structure compliance (required dirs exist)
     - Build integrity (language-specific build passes)
     - Import integrity (all imports resolve, no broken paths)
     - No stray files (source files not in root)
   - Generates verification report with specific remediation guidance
   - Advances phase to Testing only if all checks pass

**User Interaction Flow**:
```
1. User runs: brownfield structure
   → System generates plan with IDE instructions

2. User manually refactors using IDE tools
   → IDE AST parsing handles import updates correctly

3. User runs: brownfield structure --verify
   → System validates compliance and build integrity

4. If passed → Advance to Phase.TESTING
   If failed → Show specific issues and remediation steps
```

**Benefits**:
- **Safety**: IDE AST parsing > naive string replacement
- **Correctness**: Leverages existing refactoring tools developers trust
- **Learning**: Manual process helps developers understand structure
- **Constitution Alignment**: Transparent reasoning, human approval, reversibility

**Rationale**:
- LLMs are error-prone with text manipulation ("cut and paste")
- Import path updates require proper AST parsing to handle:
  - Relative imports (Python `from ..module import`)
  - Barrel exports (JavaScript `export * from`)
  - Module path calculations across nested directories
- IDEs already have battle-tested refactoring engines
- Human-in-the-loop maintains trust and control

**File Structure**:
- `src/brownfield/remediation/structure.py` - `StructurePlanGenerator` class
- `src/brownfield/remediation/structure_verifier.py` - `StructureVerifier` class
- `src/brownfield/cli/structure.py` - CLI command with `--verify` flag

## Complexity Tracking

*No constitution violations requiring justification.*

The architecture follows all constitution principles without compromise:
- Single project structure (not multiple projects)
- Plugin pattern for extensibility (simpler than inheritance hierarchies)
- JSON storage (simpler than database dependency)
- Subprocess execution for external tools (simpler than native bindings)
