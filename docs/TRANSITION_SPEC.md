# BrownKit: Spec-Kit Plugin for Legacy Code Remediation

## Problem Statement

Brownfield projects with legacy code cannot safely adopt AI-driven feature development without first addressing technical debt. Current tools (CodeGraph MCP, CodeScene, SonarQube) measure and recommend refactoring but don't enforce a mandatory "remediate-first" workflow before feature agents run.

**The Gap**: No tool enforces quality improvement as a prerequisite gate for AI feature development in brownfield codebases.

## Solution Overview

BrownKit is a Spec-Kit plugin that adds upstream remediation workflow BEFORE `/speckit.specify`. It enforces quality gates (CCN < 10, coverage > 80%, zero critical vulns) and only graduates code to Spec-Kit's feature development phase after validation.

**Relationship to Spec-Kit**: BrownKit is to Spec-Kit as BP-Kit is to Spec-Kit:
- **BP-Kit**: Business plan → Constitutional principles (upstream preparation)
- **BrownKit**: Legacy code → Quality baseline (upstream remediation)
- **Spec-Kit**: Specifications → Working code (downstream implementation)

## User Stories

### User Story 1 - Install BrownKit in Existing Spec-Kit Project (Priority: P0) 🎯 MVP

**As a** developer with a legacy codebase
**I want to** install BrownKit into my existing Spec-Kit project
**So that** I can remediate technical debt before using Spec-Kit for features

**Acceptance Criteria**:
- ✅ `brownfield init` creates `.specify/brownfield/` directory structure
- ✅ Installs 6 slash commands in `templates/commands/brownfield.*.md`
- ✅ Creates bash wrapper scripts in `.specify/scripts/bash/brownfield-*.sh`
- ✅ Shares `.specify/memory/constitution.md` with Spec-Kit
- ✅ Detects conflicts with existing Spec-Kit installation (no overwrites)
- ✅ Validation: Running `/brownfield.ingest` succeeds after installation

### User Story 2 - Ingest Existing Codebase (Priority: P0) 🎯 MVP

**As a** developer
**I want to** analyze my existing codebase architecture
**So that** I understand current patterns before remediation

**Acceptance Criteria**:
- ✅ `/brownfield.ingest` wraps `ai-project-orchestration/assess-codebase.sh`
- ✅ Generates `.specify/memory/codebase-analysis.md` with architecture overview
- ✅ Updates constitution with discovered patterns (frameworks, conventions)
- ✅ Returns structured JSON output: `{"ANALYSIS_FILE": "/path/to/analysis.md"}`
- ✅ Validation: Constitution contains patterns from analyzed codebase

### User Story 3 - Assess Technical Debt (Priority: P0) 🎯 MVP

**As a** developer
**I want to** identify technical debt hotspots
**So that** I can prioritize remediation work

**Acceptance Criteria**:
- ✅ `/brownfield.assess` wraps `ai-project-orchestration/quality-check.sh`
- ✅ Runs Lizard (CCN), pytest (coverage), Bandit (security)
- ✅ Creates numbered directory: `.specify/brownfield/001-legacy-api-cleanup/`
- ✅ Generates `assessment.md` with metrics and prioritized issues
- ✅ Returns JSON: `{"METRICS": {"coverage": 15, "complexity": 22, "vulns": 3}}`
- ✅ Validation: Assessment identifies files with CCN > 10

### User Story 4 - Generate Remediation Plan (Priority: P0) 🎯 MVP

**As a** developer
**I want to** create a remediation plan from assessment results
**So that** I have actionable steps to improve code quality

**Acceptance Criteria**:
- ✅ `/brownfield.plan` wraps `generate-remediation-plan.sh`
- ✅ Generates `.specify/brownfield/001-legacy-api-cleanup/plan.md`
- ✅ Creates `checklists/quality-gates.md` with passing criteria
- ✅ Plan includes: refactoring tasks, test additions, security fixes
- ✅ Returns JSON: `{"PLAN_FILE": "/path/to/plan.md", "TASK_COUNT": 12}`
- ✅ Validation: Plan tasks map 1:1 to assessment issues

### User Story 5 - Execute Remediation (Priority: P1)

**As a** developer
**I want to** execute the remediation plan with checkpoints
**So that** I can safely improve code quality incrementally

**Acceptance Criteria**:
- ✅ `/brownfield.remediate` wraps `autonomous-remediation-session.sh`
- ✅ Executes plan tasks with checkpoint validation after each
- ✅ Generates `.specify/brownfield/001-legacy-api-cleanup/execution-log.md`
- ✅ Stops if quality gates fail (tests break, complexity increases)
- ✅ Returns JSON: `{"COMPLETED_TASKS": 8, "FAILED_TASKS": 0, "STATUS": "success"}`
- ✅ Validation: All tests pass after remediation

### User Story 6 - Validate Quality Gates (Priority: P1)

**As a** developer
**I want to** verify code meets quality thresholds
**So that** I know it's safe for AI feature development

**Acceptance Criteria**:
- ✅ `/brownfield.validate` wraps `certify-feature-ready.sh`
- ✅ Checks: CCN < 10, coverage > 80%, zero critical vulnerabilities
- ✅ Generates `.specify/brownfield/001-legacy-api-cleanup/validation.md`
- ✅ Creates checklist: `checklists/quality-gates.md` (100% completion required)
- ✅ Returns JSON: `{"PASSED": true, "GATE_RESULTS": {"ccn": true, "coverage": true}}`
- ✅ Validation: All quality gates pass

### User Story 7 - Graduate to Spec-Kit (Priority: P1)

**As a** developer
**I want to** certify code as AI-ready and transition to feature development
**So that** I can safely use `/speckit.specify` for new features

**Acceptance Criteria**:
- ✅ `/brownfield.graduate` requires 100% checklist completion
- ✅ Updates constitution with validated patterns
- ✅ Creates handoff document: `.specify/memory/brownfield-graduation.md`
- ✅ Returns JSON: `{"GRADUATED": true, "NEXT_STEP": "/speckit.specify"}`
- ✅ Validation: Running `/speckit.specify` uses patterns from constitution

## Architecture & Integration

### Plugin Architecture (Following BP-Kit Pattern)

```
brownfield/
├── templates/
│   ├── commands/                      # Slash commands (NO collision with Spec-Kit)
│   │   ├── brownfield.ingest.md      # Analyze existing codebase
│   │   ├── brownfield.assess.md      # Identify technical debt
│   │   ├── brownfield.plan.md        # Generate remediation plan
│   │   ├── brownfield.remediate.md   # Execute fixes
│   │   ├── brownfield.validate.md    # Check quality gates
│   │   └── brownfield.graduate.md    # Certify AI-ready
│   │
│   ├── brownfield-assessment-template.md
│   ├── brownfield-plan-template.md
│   └── brownfield-validation-template.md
│
├── .specify/
│   ├── memory/
│   │   └── constitution.md           # SHARED with Spec-Kit
│   │
│   ├── scripts/bash/                 # Bash wrappers (Spec-Kit pattern)
│   │   ├── brownfield-ingest.sh     # Wraps ai-orchestration scripts
│   │   ├── brownfield-assess.sh
│   │   ├── brownfield-plan.sh
│   │   ├── brownfield-remediate.sh
│   │   ├── brownfield-validate.sh
│   │   ├── brownfield-graduate.sh
│   │   └── brownfield-common.sh
│   │
│   ├── brownfield/                   # Parallel to specs/ (brownfield artifacts)
│   │   └── 001-legacy-api-cleanup/
│   │       ├── codebase-analysis.md
│   │       ├── assessment.md
│   │       ├── plan.md
│   │       ├── execution-log.md
│   │       ├── validation.md
│   │       └── checklists/quality-gates.md
│   │
│   └── specs/                        # Spec-Kit features (UNCHANGED)
│       └── 002-new-feature/
│
├── src/brownfield/                   # Python CLI for installation only
│   └── cli.py                        # `brownfield init` command
│
└── pyproject.toml                    # Same deps as BP-Kit (typer, rich)
```

### Workflow Integration

```
PHASE 0: Brownfield Remediation (Upstream)
├─ /brownfield.ingest
│  └─ Analyzes existing code
│  └─ Updates constitution with patterns
│
├─ /brownfield.assess
│  └─ Identifies tech debt hotspots
│  └─ Generates .specify/brownfield/001-*/assessment.md
│
├─ /brownfield.plan
│  └─ Creates remediation plan
│  └─ Generates checklists/quality-gates.md
│
├─ /brownfield.remediate
│  └─ Executes fixes with checkpoints
│
├─ /brownfield.validate
│  └─ Checks quality gates (CCN, coverage, security)
│
└─ /brownfield.graduate
   └─ Certifies AI-ready
   └─ Hands off to Spec-Kit ────────┐
                                      │
                                      ▼
PHASE 1: Spec-Kit Feature Development (Downstream)
├─ /speckit.specify  ◄─────────── (Uses patterns from constitution)
├─ /speckit.plan
├─ /speckit.tasks
└─ /speckit.implement
```

### Conflict Prevention (Following BP-Kit Pattern)

**Namespace Separation**:
- Brownfield commands: `/brownfield.*`
- Spec-Kit commands: `/speckit.*`
- NO file overwrites

**Validation Logic**:
```python
def check_speckit_conflicts(project_dir: Path) -> List[str]:
    """Ensure BrownKit won't overwrite Spec-Kit files."""
    speckit_commands = [
        ".claude/commands/speckit.constitution.md",
        ".claude/commands/speckit.specify.md",
        ".claude/commands/speckit.plan.md",
        ".claude/commands/speckit.tasks.md",
        ".claude/commands/speckit.implement.md",
    ]
    # Brownfield NEVER overwrites these
```

### Bash Script Pattern (Critical for Spec-Kit Compatibility)

**Example: brownfield-assess.sh**
```bash
#!/bin/bash
# Wraps ai-project-orchestration/quality-check.sh
# Returns JSON output for slash command parsing

brownfield-assess.sh --json

# Internally calls:
# ~/ai-project-orchestration/scripts/assess-codebase.sh
# Parses output, formats as JSON

# Returns:
# {
#   "ASSESSMENT_FILE": "/abs/path/.specify/brownfield/001-legacy/assessment.md",
#   "METRICS": {"coverage": 15, "complexity": 22, "vulns": 3},
#   "REMEDIATION_DIR": "/abs/path/.specify/brownfield/001-legacy"
# }
```

## Technical Requirements

### Dependencies
- `typer>=0.9.0` - CLI framework (same as Spec-Kit/BP-Kit)
- `rich>=13.0.0` - Console UI (same as Spec-Kit/BP-Kit)
- `platformdirs>=3.0.0` - Config management
- Wraps existing: `ai-project-orchestration` scripts (32 bash scripts)
- Uses system tools: `lizard` (CCN), `pytest` (coverage), `bandit` (security)

### Quality Gates
- **Cyclomatic Complexity**: CCN < 10 for all functions
- **Test Coverage**: > 80% line coverage
- **Security**: Zero critical vulnerabilities (Bandit)
- **Type Safety**: mypy strict mode passes
- **Linting**: ruff check passes

### Integration Points
1. **Shared Constitution**: `.specify/memory/constitution.md`
2. **Parallel Artifacts**: `.specify/brownfield/` alongside `.specify/specs/`
3. **Sequential Workflow**: Brownfield first, then Spec-Kit
4. **Pattern Reuse**: Bash scripts with `--json`, checklists, templates

## Success Criteria

### MVP Success (User Stories 1-4)
- ✅ Install BrownKit into existing Spec-Kit project without conflicts
- ✅ Run `/brownfield.ingest` → `/brownfield.assess` → `/brownfield.plan` workflow
- ✅ Generated artifacts follow Spec-Kit patterns (numbered dirs, templates, checklists)
- ✅ Constitution updated with codebase patterns

### Full Success (User Stories 5-7)
- ✅ Complete remediation workflow: ingest → graduate
- ✅ All quality gates pass (CCN < 10, coverage > 80%, zero vulns)
- ✅ Smooth handoff to `/speckit.specify` (constitution contains validated patterns)
- ✅ Documentation shows Brownfield → Spec-Kit integration

## Out of Scope (V1)
- ❌ Automatic remediation without human review (checkpoints required)
- ❌ Support for non-Python languages (MVP: Python only)
- ❌ GUI/web interface (CLI only)
- ❌ Git workflow automation (manual commits)

## Open Questions
1. Should `/brownfield.remediate` support auto-commit at checkpoints?
2. Quality gate thresholds configurable or hardcoded? (Suggest: `.specify/brownfield-config.yaml`)
3. Support multiple brownfield projects in parallel? (e.g., `001-api`, `002-database`)

## References
- BP-Kit architecture: `~/bpkit/` (plugin pattern to follow)
- Spec-Kit: `github.com/github/spec-kit`
- ai-project-orchestration: `~/ai-project-orchestration/scripts/`
- Discussion #331: "Recommended approach for brownfield development" (gap to fill)
