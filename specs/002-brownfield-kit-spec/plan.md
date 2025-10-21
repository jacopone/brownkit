# Implementation Plan: Brownfield-Kit - Spec-Kit Plugin for Legacy Code Remediation

**Branch**: `002-brownfield-kit-spec` | **Date**: 2025-10-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-brownfield-kit-spec/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Brownfield-Kit is a Spec-Kit plugin that enforces quality improvement as a mandatory prerequisite before AI-driven feature development. It provides 6 slash commands (`/brownfield.ingest`, `/brownfield.assess`, `/brownfield.plan`, `/brownfield.remediate`, `/brownfield.validate`, `/brownfield.graduate`) backed by self-contained bash scripts that analyze Python codebases using Lizard (CCN), pytest (coverage), and Bandit (security). The tool creates numbered remediation projects in `.specify/brownfield/NNN/`, enforces quality gates (CCN < 10, coverage > 80%, zero critical vulns), and graduates codebases to Spec-Kit's feature development workflow only after validation.

**Technical Approach**: Follow Spec-Kit's architectural pattern with markdown slash commands + self-contained bash scripts (no external dependencies). Bash scripts directly invoke quality tools, generate markdown reports, and return structured JSON. Total estimated code: ~520 lines of bash across 7 scripts.

## Technical Context

**Language/Version**: Bash 5.0+ (for scripts), Markdown (for slash commands/templates)
**Primary Dependencies**:
- System tools: `lizard` (CCN analysis), `pytest` + `coverage` plugin (test coverage), `bandit` (security), `jq` (JSON parsing), `git` (version control)
- Python 3.11+ (target codebase language - V1 scope)

**Storage**: Filesystem-based
- `.specify/brownfield/NNN-name/` - Numbered remediation project directories
- `.specify/memory/constitution.md` - Shared with Spec-Kit
- `.specify/memory/brownfield-state.json` - Active project tracking
- Temporary files: `/tmp/brownfield-*.json` - Tool output caching

**Testing**: bash script testing via `bats` (Bash Automated Testing System) - optional, not required for MVP
**Target Platform**: Linux/macOS (NixOS primary, any Unix-like system with bash 5.0+)
**Project Type**: CLI plugin (integrates into existing Spec-Kit projects)
**Performance Goals**:
- Analysis completes within 5 minutes for 10,000 LOC
- Quality gate validation under 3 minutes
- JSON parsing/generation under 1 second

**Constraints**:
- Must not overwrite any Spec-Kit files
- Bash scripts must be self-contained (no external script dependencies)
- Quality gate thresholds configurable via `.specify/brownfield-config.yaml`
- V1 scope: Python 3.11+ codebases only

**Scale/Scope**:
- 6 slash commands (markdown files, ~200 lines each = ~1,200 lines markdown)
- 7 bash scripts (~520 lines total)
- 3 markdown templates (~300 lines total)
- Total: ~2,000 lines (code + documentation)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Checking against Brownfield-Kit Constitution** (`.specify/memory/constitution.md`):

### I. ASSESSMENT_DRIVEN_DEVELOPMENT ✅
- **Requirement**: All changes preceded by automated analysis
- **Compliance**: `/brownfield.ingest` and `/brownfield.assess` run Lizard, pytest, Bandit before any remediation
- **Status**: PASS

### II. SAFETY_NET_FIRST ✅
- **Requirement**: Testing infrastructure before features
- **Compliance**: `/brownfield.validate` enforces 80% coverage threshold before graduation
- **Status**: PASS

### III. INCREMENTAL_REMEDIATION ✅
- **Requirement**: Small, verifiable changes
- **Compliance**: `/brownfield.remediate` executes tasks with checkpoint validation after each
- **Status**: PASS

### IV. TRANSPARENT_REASONING ✅
- **Requirement**: AI documents decisions with confidence levels
- **Compliance**: Assessment reports include metrics with thresholds, plan tasks mapped 1:1 to issues
- **Status**: PASS

### V. MEASURABLE_PROGRESS ✅
- **Requirement**: Quantitative phase transition gates
- **Compliance**: Quality gates (CCN < 10, coverage > 80%, zero critical vulns) are measurable and enforced
- **Status**: PASS

### VI. STRUCTURE_INTEGRITY ✅
- **Requirement**: Directory organization per ecosystem conventions
- **Compliance**: Mirrors Spec-Kit structure (`.specify/brownfield/NNN/`, parallel to `.specify/specs/`)
- **Status**: PASS

### VII. REVERSIBILITY ✅
- **Requirement**: All changes git-trackable
- **Compliance**: Checkpoint-based remediation with git status validation, rollback capability mentioned
- **Status**: PASS

**Gate Result**: ✅ **PASS** - All constitutional principles satisfied

## Project Structure

### Documentation (this feature)

```
specs/002-brownfield-kit-spec/
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0 output (tool research, bash patterns)
├── data-model.md        # Phase 1 output (state structures, config schema)
├── quickstart.md        # Phase 1 output (installation guide)
├── contracts/           # Phase 1 output (JSON schemas for script outputs)
│   ├── brownfield-assess-output.json
│   ├── brownfield-plan-output.json
│   └── brownfield-validate-output.json
├── checklists/
│   └── requirements.md  # Spec quality checklist (completed)
└── spec.md              # Feature specification (completed)
```

### Source Code (repository root)

```
brownfield/
├── templates/
│   ├── commands/                          # Slash commands (Spec-Kit pattern)
│   │   ├── brownfield.ingest.md          # ~200 lines: Workflow for codebase ingestion
│   │   ├── brownfield.assess.md          # ~200 lines: Workflow for quality assessment
│   │   ├── brownfield.plan.md            # ~200 lines: Workflow for remediation planning
│   │   ├── brownfield.remediate.md       # ~200 lines: Workflow for executing fixes
│   │   ├── brownfield.validate.md        # ~200 lines: Workflow for quality gate validation
│   │   └── brownfield.graduate.md        # ~200 lines: Workflow for certification
│   │
│   ├── brownfield-assessment-template.md  # ~100 lines: Assessment report template
│   ├── brownfield-plan-template.md        # ~100 lines: Remediation plan template
│   ├── brownfield-validation-template.md  # ~100 lines: Validation report template
│   └── brownfield-config-template.yaml    # ~30 lines: Quality gate configuration
│
├── .specify/
│   ├── memory/
│   │   └── constitution.md                # Shared with Spec-Kit (already exists)
│   │
│   ├── scripts/bash/                      # Self-contained bash scripts
│   │   ├── brownfield-ingest.sh          # ~80 lines: Run tokei, lizard, generate codebase-analysis.md
│   │   ├── brownfield-assess.sh          # ~60 lines: Run quality checks, create assessment.md
│   │   ├── brownfield-plan.sh            # ~100 lines: Analyze metrics, generate plan.md
│   │   ├── brownfield-remediate.sh       # ~120 lines: Execute tasks with checkpoints
│   │   ├── brownfield-validate.sh        # ~70 lines: Check quality gates
│   │   ├── brownfield-graduate.sh        # ~50 lines: Certify AI-ready, update constitution
│   │   └── brownfield-common.sh          # ~40 lines: Shared utilities (next_number, parse_json, etc.)
│   │
│   ├── templates/                         # Copied from templates/ on init
│   │   └── [templates mirror for installed instances]
│   │
│   └── brownfield/                        # Created on first /brownfield.assess
│       └── 001-{project-name}/
│           ├── codebase-analysis.md
│           ├── assessment.md
│           ├── plan.md
│           ├── execution-log.md
│           ├── validation.md
│           └── checklists/quality-gates.md
│
├── src/brownfield/                        # Python CLI (installation only)
│   ├── __init__.py
│   ├── cli.py                            # `brownfield init` command
│   ├── core/
│   │   ├── __init__.py
│   │   ├── installer.py                  # Copy templates, detect conflicts
│   │   └── validator.py                  # Check Spec-Kit presence
│   └── templates/                        # Embedded templates
│
├── tests/                                 # Unit tests for Python CLI
│   ├── test_installer.py
│   └── test_validator.py
│
├── pyproject.toml                         # Python package config
├── README.md                              # Installation + quick start
└── LICENSE                                # MIT License
```

**Structure Decision**: Single project with clear separation between:
1. **Templates** (to be copied into user projects)
2. **Python CLI** (installation tooling only, minimal)
3. **Documentation** (in specs/ following Spec-Kit conventions)

This structure mirrors BP-Kit's architecture (Python CLI for init, markdown templates for workflows).

## Complexity Tracking

*No constitution violations requiring justification.*

All design decisions align with constitutional principles:
- Self-contained bash scripts keep complexity low
- No external dependencies (follows STRUCTURE_INTEGRITY)
- Incremental execution with checkpoints (follows INCREMENTAL_REMEDIATION)
- Measurable quality gates (follows MEASURABLE_PROGRESS)

---

## Phase 0: Research & Unknown Resolution

**Status**: NEEDS EXECUTION

### Research Tasks

1. **Bash Script Patterns for JSON Generation**
   - **Question**: How to reliably generate structured JSON from bash without external tools besides `jq`?
   - **Research needed**: Best practices for heredoc JSON templates, escaping quotes, handling dynamic values
   - **Output**: Reusable pattern for all 7 bash scripts

2. **Quality Tool Integration**
   - **Question**: What are the exact command-line flags for Lizard, pytest, and Bandit to get JSON output?
   - **Research needed**: Tool documentation for:
     - `lizard --json` format and fields
     - `pytest --cov --cov-report=json` output structure
     - `bandit -f json` schema
   - **Output**: Example commands + JSON schema documentation

3. **Numbered Directory Management**
   - **Question**: How to reliably get next brownfield project number in bash?
   - **Research needed**: Edge cases (gaps in numbering, concurrent creation, zero-padding)
   - **Output**: Bash function `get_next_brownfield_number()`

4. **Template Rendering in Bash**
   - **Question**: How to fill markdown templates with dynamic values in bash?
   - **Research needed**: `envsubst` usage, sed patterns, or custom function
   - **Output**: Reusable template rendering function

5. **Checkpoint Validation Pattern**
   - **Question**: How should `/brownfield.remediate` implement checkpoints?
   - **Research needed**: Git status checks, test execution, rollback mechanisms
   - **Output**: Checkpoint workflow design

**Output Location**: `specs/002-brownfield-kit-spec/research.md`

---

## Phase 1: Design & Contracts

**Status**: PENDING (blocked on Phase 0)

**Prerequisites**: `research.md` complete with all patterns documented

### 1. Data Model (`data-model.md`)

**Entities**:

**BrownfieldProject**:
- `number`: Integer (001, 002, etc.)
- `name`: String (e.g., "legacy-api-cleanup")
- `directory`: Path (`.specify/brownfield/001-legacy-api-cleanup/`)
- `status`: Enum (`assessing`, `planning`, `remediating`, `validating`, `graduated`)
- `created_at`: Timestamp
- `metrics`: Metrics object

**Metrics**:
- `avg_ccn`: Float (average cyclomatic complexity)
- `max_ccn`: Float (maximum CCN in any function)
- `coverage_percent`: Float (test coverage percentage)
- `critical_vulns`: Integer (count of critical security vulnerabilities)
- `high_vulns`: Integer (count of high severity vulnerabilities)

**QualityGate**:
- `name`: String (e.g., "Cyclomatic Complexity")
- `threshold`: Float or Integer
- `operator`: Enum (`lt`, `gt`, `eq`)
- `current_value`: Float or Integer
- `passed`: Boolean

**BrownfieldState** (stored in `.specify/memory/brownfield-state.json`):
- `active_project`: String (e.g., "001-legacy-api-cleanup")
- `projects`: Array of BrownfieldProject objects
- `version`: String ("1.0.0")

**QualityGateConfig** (stored in `.specify/brownfield-config.yaml`):
```yaml
quality_gates:
  cyclomatic_complexity:
    threshold: 10
    enabled: true
  test_coverage:
    threshold: 80
    enabled: true
  security:
    block_on_critical: true
    block_on_high: false
```

### 2. API Contracts (`contracts/`)

**brownfield-assess-output.json** (JSON Schema):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["ASSESSMENT_FILE", "METRICS", "BROWNFIELD_DIR"],
  "properties": {
    "ASSESSMENT_FILE": {
      "type": "string",
      "description": "Absolute path to assessment.md"
    },
    "METRICS": {
      "type": "object",
      "required": ["avg_ccn", "coverage", "vulns"],
      "properties": {
        "avg_ccn": {"type": "number"},
        "max_ccn": {"type": "number"},
        "coverage": {"type": "number"},
        "critical_vulns": {"type": "integer"},
        "high_vulns": {"type": "integer"}
      }
    },
    "BROWNFIELD_DIR": {
      "type": "string",
      "description": "Absolute path to .specify/brownfield/NNN-name/"
    }
  }
}
```

**brownfield-plan-output.json** (JSON Schema):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["PLAN_FILE", "TASK_COUNT", "CHECKLIST_FILE"],
  "properties": {
    "PLAN_FILE": {"type": "string"},
    "TASK_COUNT": {"type": "integer"},
    "CHECKLIST_FILE": {"type": "string"}
  }
}
```

**brownfield-validate-output.json** (JSON Schema):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["PASSED", "GATE_RESULTS", "VALIDATION_FILE"],
  "properties": {
    "PASSED": {"type": "boolean"},
    "GATE_RESULTS": {
      "type": "object",
      "properties": {
        "ccn": {"type": "boolean"},
        "coverage": {"type": "boolean"},
        "security": {"type": "boolean"}
      }
    },
    "VALIDATION_FILE": {"type": "string"}
  }
}
```

### 3. Quick Start Guide (`quickstart.md`)

See Phase 1 output (to be generated).

---

## Next Steps After Phase 1

1. **Agent Context Update**: Run `.specify/scripts/bash/update-agent-context.sh claude` to add Brownfield-Kit technologies to Claude's context
2. **Generate Tasks**: Run `/speckit.tasks` to break down implementation into concrete tasks
3. **Implementation**: Execute tasks to build bash scripts, slash commands, and templates
4. **Testing**: Validate on sample brownfield project (this brownfield repository itself!)

---

**Phase Status Summary**:
- ✅ Phase -1: Specification complete (spec.md)
- ✅ Phase 0: Planning complete (this file)
- 🔄 Phase 0 (next): Research execution (create research.md)
- ⏳ Phase 1: Design pending (create data-model.md, contracts/, quickstart.md)
- ⏳ Phase 2: Tasks pending (run /speckit.tasks)
