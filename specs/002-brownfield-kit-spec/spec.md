# Feature Specification: Brownfield-Kit - Spec-Kit Plugin for Legacy Code Remediation

**Feature Branch**: `002-brownfield-kit-spec`
**Created**: 2025-10-20
**Status**: Draft
**Input**: User description: "Brownfield-Kit: Spec-Kit Plugin for Legacy Code Remediation"

## Problem Statement

Brownfield projects with legacy code cannot safely adopt AI-driven feature development without first addressing technical debt. Current tools (CodeGraph MCP, CodeScene, SonarQube) measure and recommend refactoring but don't enforce a mandatory "remediate-first" workflow before feature agents run.

**The Gap**: No tool enforces quality improvement as a prerequisite gate for AI feature development in brownfield codebases.

**Solution**: Brownfield-Kit is a Spec-Kit plugin that adds upstream remediation workflow BEFORE `/speckit.specify`. It enforces quality gates and only graduates code to Spec-Kit's feature development phase after validation.

## User Scenarios & Testing

### User Story 1 - Install Brownfield-Kit in Existing Spec-Kit Project (Priority: P0) 🎯 MVP

A developer has an existing Spec-Kit project and wants to add Brownfield-Kit's remediation capabilities without breaking their current workflow. They run `brownfield init` and the tool installs cleanly alongside Spec-Kit, creating new `/brownfield.*` commands while preserving all existing `/speckit.*` commands.

**Why this priority**: Foundation for all other features. Without successful installation, no other capabilities are accessible. This is the entry point for all users.

**Independent Test**: Can be fully tested by running `brownfield init` in a Spec-Kit project and verifying directory structure creation and conflict-free coexistence. Delivers immediate value by proving compatibility.

**Acceptance Scenarios**:

1. **Given** a project with Spec-Kit already installed, **When** developer runs `brownfield init`, **Then** `.specify/brownfield/` directory is created with proper structure
2. **Given** Spec-Kit slash commands exist in `.claude/commands/`, **When** Brownfield-Kit installs, **Then** no Spec-Kit files are overwritten and 6 new `/brownfield.*` commands are added
3. **Given** Brownfield-Kit is installed, **When** developer runs `/brownfield.ingest`, **Then** command executes successfully without errors
4. **Given** both tools are installed, **When** developer runs `/speckit.specify`, **Then** Spec-Kit functionality remains unchanged

---

### User Story 2 - Ingest and Analyze Existing Codebase (Priority: P0) 🎯 MVP

A developer wants to understand their legacy codebase's architecture before starting remediation. They run `/brownfield.ingest` and receive a comprehensive analysis document showing frameworks, patterns, and architectural conventions discovered in the code.

**Why this priority**: Essential baseline for all remediation work. Cannot prioritize technical debt without understanding current state. Feeds into constitution for downstream Spec-Kit work.

**Independent Test**: Can be fully tested by running `/brownfield.ingest` on any existing Python codebase and verifying generation of `.specify/memory/codebase-analysis.md` with architectural insights. Delivers standalone value as documentation.

**Acceptance Scenarios**:

1. **Given** an existing Python codebase, **When** developer runs `/brownfield.ingest`, **Then** system analyzes code structure and generates codebase-analysis.md with framework identification
2. **Given** codebase analysis completes, **When** system updates constitution, **Then** `.specify/memory/constitution.md` contains discovered patterns (e.g., "Uses FastAPI framework", "Follows repository pattern")
3. **Given** analysis finishes, **When** command completes, **Then** structured JSON is returned with `{"ANALYSIS_FILE": "/abs/path/to/analysis.md"}`

---

### User Story 3 - Assess Technical Debt Hotspots (Priority: P0) 🎯 MVP

A developer needs to identify which parts of their codebase have the highest technical debt to prioritize remediation efforts. They run `/brownfield.assess` and receive a prioritized list of issues with specific metrics (complexity scores, test coverage gaps, security vulnerabilities).

**Why this priority**: Core value proposition. Automates the manual, time-consuming process of identifying quality issues. Enables data-driven remediation prioritization.

**Independent Test**: Can be fully tested by running `/brownfield.assess` on a codebase and verifying assessment.md generation with concrete metrics (CCN values, coverage percentages, vulnerability counts). Delivers actionable insights immediately.

**Acceptance Scenarios**:

1. **Given** a Python codebase, **When** developer runs `/brownfield.assess`, **Then** system executes Lizard (CCN), pytest (coverage), and Bandit (security) analysis
2. **Given** analysis completes, **When** system generates assessment, **Then** numbered directory `.specify/brownfield/001-legacy-api-cleanup/` is created with assessment.md
3. **Given** assessment completes, **When** results are compiled, **Then** JSON output includes metrics: `{"METRICS": {"coverage": 15, "complexity": 22, "vulns": 3}}`
4. **Given** high-complexity functions exist, **When** assessment runs, **Then** all functions with CCN > 10 are identified and listed with file paths and line numbers

---

### User Story 4 - Generate Remediation Plan (Priority: P0) 🎯 MVP

A developer has an assessment report showing technical debt hotspots. They run `/brownfield.plan` and receive an actionable remediation plan with specific tasks (refactor function X to reduce CCN, add tests for module Y, fix security issue Z) and a quality gates checklist.

**Why this priority**: Converts assessment data into actionable work. Without a plan, assessment insights remain theoretical. Checklist provides clear definition of "done".

**Independent Test**: Can be fully tested by running `/brownfield.plan` after assessment and verifying plan.md generation with task breakdown and checklists/quality-gates.md with measurable criteria. Delivers clear roadmap.

**Acceptance Scenarios**:

1. **Given** an assessment report exists, **When** developer runs `/brownfield.plan`, **Then** system generates plan.md with specific remediation tasks mapped 1:1 to assessment issues
2. **Given** plan generation, **When** system creates artifacts, **Then** `checklists/quality-gates.md` is generated with passing criteria (CCN < 10, coverage > 80%, zero critical vulns)
3. **Given** plan completes, **When** command finishes, **Then** JSON output includes `{"PLAN_FILE": "/path/to/plan.md", "TASK_COUNT": 12}`
4. **Given** plan contains tasks, **When** developer reviews plan.md, **Then** each task includes: specific file/function, current metric, target metric, and recommended action

---

### User Story 5 - Execute Remediation with Checkpoints (Priority: P1)

A developer has a remediation plan and wants to execute it safely with validation checkpoints to prevent breaking the codebase. They run `/brownfield.remediate` and the system executes tasks incrementally, running tests after each change and stopping if quality gates fail.

**Why this priority**: Automates the risky manual refactoring process. Post-MVP priority because manual remediation is possible with the plan from P0 stories. Provides safety through checkpointing.

**Independent Test**: Can be fully tested by running `/brownfield.remediate` on a planned feature and verifying execution-log.md shows incremental progress with checkpoint validations. Delivers safe automation.

**Acceptance Scenarios**:

1. **Given** a remediation plan exists, **When** developer runs `/brownfield.remediate`, **Then** system executes tasks sequentially with checkpoint validation after each
2. **Given** remediation is running, **When** a checkpoint fails (tests break), **Then** system stops execution and logs failure in execution-log.md
3. **Given** remediation completes successfully, **When** all tasks finish, **Then** JSON output shows `{"COMPLETED_TASKS": 8, "FAILED_TASKS": 0, "STATUS": "success"}`
4. **Given** remediation finishes, **When** validation runs, **Then** all tests pass and no regressions are introduced

---

### User Story 6 - Validate Quality Gates (Priority: P1)

A developer has completed remediation (manually or via `/brownfield.remediate`) and wants to verify the codebase meets quality thresholds before proceeding to feature development. They run `/brownfield.validate` and receive a pass/fail report for each quality gate.

**Why this priority**: Safety check before transitioning to AI-driven feature work. Post-MVP because manual verification is possible. Provides automated certification that codebase is ready.

**Independent Test**: Can be fully tested by running `/brownfield.validate` on a remediated codebase and verifying validation.md with gate results. Delivers confidence certification.

**Acceptance Scenarios**:

1. **Given** remediation is complete, **When** developer runs `/brownfield.validate`, **Then** system checks CCN < 10, coverage > 80%, zero critical vulnerabilities
2. **Given** validation runs, **When** results are compiled, **Then** validation.md is generated with pass/fail status for each gate
3. **Given** all gates pass, **When** command completes, **Then** JSON output shows `{"PASSED": true, "GATE_RESULTS": {"ccn": true, "coverage": true, "security": true}}`
4. **Given** a gate fails, **When** validation completes, **Then** detailed failure information is provided (which files/functions failed, current vs. target metrics)

---

### User Story 7 - Graduate to Spec-Kit Feature Development (Priority: P1)

A developer has validated their codebase meets quality gates and wants to officially transition from remediation mode to feature development mode. They run `/brownfield.graduate` and the system certifies the codebase as AI-ready, updates the constitution with validated patterns, and confirms readiness for `/speckit.specify`.

**Why this priority**: Formal handoff ceremony between brownfield remediation and greenfield feature work. Post-MVP because manual transition is possible. Provides clear "graduation" milestone.

**Independent Test**: Can be fully tested by running `/brownfield.graduate` after validation and verifying constitution update and graduation document creation. Delivers clear transition point.

**Acceptance Scenarios**:

1. **Given** all quality gates pass, **When** developer runs `/brownfield.graduate`, **Then** system requires 100% checklist completion before proceeding
2. **Given** checklists are complete, **When** graduation runs, **Then** constitution is updated with validated patterns and handoff document `.specify/memory/brownfield-graduation.md` is created
3. **Given** graduation completes, **When** command finishes, **Then** JSON output shows `{"GRADUATED": true, "NEXT_STEP": "/speckit.specify"}`
4. **Given** codebase is graduated, **When** developer runs `/speckit.specify`, **Then** Spec-Kit reads patterns from constitution and applies them to feature planning

---

### Edge Cases

- What happens when `/brownfield.assess` is run on a codebase with no tests?
  - Assessment should report 0% coverage and flag this as critical gap
  - Plan should prioritize test creation before refactoring

- How does system handle projects mixing Python with other languages?
  - V1 scope: Python only. Non-Python files are analyzed for structure but metrics (CCN, coverage) only run on Python files
  - Assessment report clearly indicates which files were analyzed vs. skipped

- What if `/brownfield.remediate` checkpoint fails midway through execution?
  - System stops immediately, logs failure point in execution-log.md
  - Developer can review failure, fix manually, then resume or restart

- How does system handle conflicts if developer manually modifies files during remediation?
  - Checkpoints detect git working tree changes
  - System warns if uncommitted changes exist and asks developer to commit or stash before proceeding

- What if quality gate thresholds are too strict for a specific project?
  - V1: Thresholds are hardcoded (CCN < 10, coverage > 80%)
  - Future: `.specify/brownfield-config.yaml` allows threshold customization

- How does Brownfield-Kit detect existing Spec-Kit installation?
  - Checks for `.specify/` directory existence
  - Validates presence of `.specify/memory/constitution.md`
  - If not found, prompts to install Spec-Kit first

## Technical Architecture

### Spec-Kit Compatibility Pattern

Brownfield-Kit follows the **exact same architecture** as Spec-Kit to ensure seamless integration:

**Architecture Components**:
1. **Markdown Slash Commands** (`.claude/commands/brownfield.*.md`)
   - Contain workflow documentation and invocation instructions
   - Call bash scripts and orchestrate Claude's analysis
   - Format: Same as Spec-Kit's `/speckit.*` commands

2. **Self-Contained Bash Scripts** (`.specify/scripts/bash/brownfield-*.sh`)
   - Directly invoke quality tools (no external dependencies)
   - Create Spec-Kit directory structures
   - Generate markdown artifacts
   - Return structured JSON output
   - Pattern: Same as Spec-Kit's `create-new-feature.sh`

3. **Markdown Templates** (`templates/brownfield-*.md`)
   - Assessment report template
   - Remediation plan template
   - Validation report template

**Key Architectural Decisions**:

**Self-Contained Scripts** (No External Dependencies):
- Bash scripts directly call `lizard`, `pytest`, `bandit` (not wrappers)
- All logic is self-contained within brownfield repository
- No dependency on external script repositories
- Tools assumed available: lizard, pytest, bandit, jq, git

**Spec-Kit Pattern Alignment**:
```bash
# Spec-Kit pattern (create-new-feature.sh):
.specify/scripts/bash/create-new-feature.sh --json "feature-name"
# Returns: {"BRANCH_NAME": "...", "SPEC_FILE": "..."}

# Brownfield-Kit pattern (brownfield-assess.sh):
.specify/scripts/bash/brownfield-assess.sh --json
# Returns: {"ASSESSMENT_FILE": "...", "METRICS": {...}}
```

**Data Flow**:
```
User runs /brownfield.assess
    ↓
Slash command (MD) invokes brownfield-assess.sh
    ↓
Bash script:
  1. Runs lizard src/ --json → /tmp/complexity.json
  2. Runs pytest --cov --json → /tmp/coverage.json
  3. Runs bandit -r src/ -f json → /tmp/security.json
  4. Creates .specify/brownfield/001-project/
  5. Generates assessment.md from template + metrics
  6. Returns JSON: {"ASSESSMENT_FILE": "...", "METRICS": {...}}
    ↓
Slash command parses JSON
    ↓
Claude analyzes assessment.md, generates summary
    ↓
User receives: "Assessment complete. Found 12 complexity hotspots..."
```

**Directory Structure** (Mirrors Spec-Kit):
```
brownfield/
├── templates/
│   ├── commands/                      # Slash commands (like Spec-Kit)
│   │   ├── brownfield.ingest.md
│   │   ├── brownfield.assess.md
│   │   ├── brownfield.plan.md
│   │   ├── brownfield.remediate.md
│   │   ├── brownfield.validate.md
│   │   └── brownfield.graduate.md
│   │
│   ├── brownfield-assessment-template.md
│   ├── brownfield-plan-template.md
│   └── brownfield-validation-template.md
│
├── .specify/
│   ├── memory/
│   │   └── constitution.md           # SHARED with Spec-Kit
│   │
│   ├── scripts/bash/                 # Self-contained scripts (like Spec-Kit)
│   │   ├── brownfield-ingest.sh     # ~80 lines: tokei, lizard, generate analysis
│   │   ├── brownfield-assess.sh     # ~60 lines: quality checks, create assessment
│   │   ├── brownfield-plan.sh       # ~100 lines: analyze metrics, generate plan
│   │   ├── brownfield-remediate.sh  # ~120 lines: execute tasks with checkpoints
│   │   ├── brownfield-validate.sh   # ~70 lines: check quality gates
│   │   ├── brownfield-graduate.sh   # ~50 lines: certify and snapshot
│   │   └── brownfield-common.sh     # ~40 lines: shared utilities
│   │
│   ├── brownfield/                   # Parallel to specs/
│   │   └── 001-legacy-api-cleanup/
│   │       ├── codebase-analysis.md  # From /brownfield.ingest
│   │       ├── assessment.md         # From /brownfield.assess
│   │       ├── plan.md               # From /brownfield.plan
│   │       ├── execution-log.md      # From /brownfield.remediate
│   │       ├── validation.md         # From /brownfield.validate
│   │       └── checklists/quality-gates.md
│   │
│   └── specs/                        # Spec-Kit features (UNCHANGED)
│       └── 002-new-feature/
│
└── src/brownfield/                   # Python CLI for init only
    └── cli.py                        # `brownfield init` command
```

**Bash Script Responsibilities**:
- ✅ Run quality analysis tools directly
- ✅ Parse JSON output (using `jq`)
- ✅ Create `.specify/brownfield/NNN/` directories
- ✅ Generate markdown from templates
- ✅ Manage state files (brownfield-state.json)
- ✅ Return structured JSON for slash commands
- ✅ Handle errors gracefully

**Slash Command Responsibilities**:
- ✅ Invoke bash scripts with correct arguments
- ✅ Parse JSON responses
- ✅ Generate AI-enhanced summaries
- ✅ Guide user through workflow
- ✅ Update constitution when needed

**Integration with Spec-Kit**:
- Shared `.specify/memory/constitution.md`
- Parallel directory structure (`.specify/brownfield/` alongside `.specify/specs/`)
- Same slash command pattern (`/brownfield.*` vs `/speckit.*`)
- Same bash script pattern (self-contained, JSON output)
- Brownfield graduates → Spec-Kit takes over

## Requirements

### Functional Requirements

- **FR-001**: System MUST install Brownfield-Kit into existing Spec-Kit projects without overwriting any Spec-Kit files or configurations
- **FR-002**: System MUST create 6 slash commands (`/brownfield.ingest`, `/brownfield.assess`, `/brownfield.plan`, `/brownfield.remediate`, `/brownfield.validate`, `/brownfield.graduate`) in `templates/commands/`
- **FR-003**: System MUST create self-contained bash scripts in `.specify/scripts/bash/` that directly invoke quality analysis tools (Lizard, pytest, Bandit) following Spec-Kit architectural patterns
- **FR-004**: System MUST return structured JSON output from all bash scripts for programmatic parsing
- **FR-005**: System MUST analyze Python codebases for cyclomatic complexity using Lizard tool
- **FR-006**: System MUST measure test coverage using pytest with coverage plugin
- **FR-007**: System MUST scan for security vulnerabilities using Bandit tool
- **FR-008**: System MUST generate numbered directories for brownfield projects (e.g., `.specify/brownfield/001-legacy-api-cleanup/`)
- **FR-009**: System MUST create assessment reports in markdown format with metrics and prioritized issues
- **FR-010**: System MUST generate remediation plans with tasks mapped 1:1 to assessment issues
- **FR-011**: System MUST create checklists with quality gate criteria (CCN < 10, coverage > 80%, zero critical vulns)
- **FR-012**: System MUST execute remediation tasks with checkpoint validation after each task
- **FR-013**: System MUST stop remediation execution if any checkpoint fails (tests break, complexity increases)
- **FR-014**: System MUST validate quality gates pass before allowing graduation
- **FR-015**: System MUST update `.specify/memory/constitution.md` with discovered patterns from codebase analysis
- **FR-016**: System MUST share constitution file between Brownfield-Kit and Spec-Kit (no duplication)
- **FR-017**: System MUST detect conflicts with Spec-Kit installation and prevent overwrites
- **FR-018**: System MUST support Python 3.11+ codebases (V1 scope: Python only)

### Key Entities

- **Brownfield Project**: Represents a legacy codebase undergoing remediation, stored in `.specify/brownfield/NNN-name/` with assessment, plan, execution log, validation report, and checklists
- **Assessment Report**: Markdown document containing metrics (CCN, coverage, vulnerabilities) and prioritized list of technical debt hotspots with file paths and line numbers
- **Remediation Plan**: Markdown document with actionable tasks, each mapped to an assessment issue, including current/target metrics and recommended actions
- **Quality Gate**: Validation criterion with threshold (e.g., "CCN < 10", "coverage > 80%") and pass/fail status
- **Checklist**: Markdown document tracking completion status of quality gates and remediation tasks
- **Constitution**: Shared YAML/markdown file in `.specify/memory/constitution.md` containing project principles, patterns, and architectural conventions
- **Execution Log**: Chronological record of remediation tasks executed, checkpoint results, and any failures encountered

## Success Criteria

### Measurable Outcomes

- **SC-001**: Developers can install Brownfield-Kit into existing Spec-Kit project in under 2 minutes without any file conflicts
- **SC-002**: Codebase analysis completes within 5 minutes for projects up to 10,000 lines of code
- **SC-003**: Assessment accurately identifies 100% of functions with CCN > 10 when compared to manual Lizard execution
- **SC-004**: Remediation plans contain specific, actionable tasks with zero "TODO" or "TBD" placeholders
- **SC-005**: Checkpoint validation detects test failures within 30 seconds of introducing breaking changes
- **SC-006**: Quality gate validation completes in under 3 minutes for codebases up to 10,000 lines
- **SC-007**: Constitution updates preserve existing Spec-Kit patterns (no data loss during Brownfield-Kit installation)
- **SC-008**: 90% of developers successfully complete ingest → assess → plan workflow on first attempt without errors
- **SC-009**: Graduated codebases pass all quality gates (CCN < 10, coverage > 80%, zero critical vulnerabilities)
- **SC-010**: Brownfield-Kit slash commands coexist with Spec-Kit commands with zero namespace collisions

## Assumptions

- Developers have Python 3.11+ installed on their system
- Developers have pytest, Lizard, and Bandit tools available (system-level or via virtualenv)
- Spec-Kit is already installed and properly configured before Brownfield-Kit installation
- Projects use git for version control (checkpoint validation relies on git status)
- Test suites exist and can be executed via `pytest` command (remediation checkpoint assumes tests are runnable)
- Developers understand technical debt concepts (CCN, test coverage, security vulnerabilities)
- Quality gate thresholds (CCN < 10, coverage > 80%) are reasonable defaults for most Python projects

## Out of Scope (V1)

- Automatic remediation without human review (checkpoints require developer to review and approve)
- Support for non-Python languages (MVP targets Python 3.11+ only)
- GUI or web interface (CLI-only tool)
- Git workflow automation (no automatic commits, branches, or PRs)
- IDE integrations or editor plugins
- Real-time monitoring or continuous quality tracking
- Custom quality gate threshold configuration (hardcoded values in V1)
- Multi-language project support (future: JavaScript, TypeScript, Go, etc.)
- Cloud deployment or SaaS offering
- Team collaboration features (shared dashboards, notifications)

## Design Decisions

**Decision 1: Auto-commit at checkpoints → Configurable flag (defaults to false)**

**Rationale**: Respects user's git control preferences while enabling automation for power users. Aligns with documented policy against forced git operations. Default behavior leaves commits to developer (manual control), but `--auto-commit` flag enables automation when needed.

**Implementation**: `/brownfield.remediate --auto-commit` creates commits with descriptive messages (e.g., "Refactor: Reduce CCN in user_service.py from 15 to 8"). Without flag, checkpoints validate but don't commit.

---

**Decision 2: Quality gate thresholds → Configurable via `.specify/brownfield-config.yaml`**

**Rationale**: Real-world legacy systems vary widely in current quality baseline. Teams need flexibility to set achievable incremental targets (e.g., reduce CCN from 30 to 20 before targeting 10). Different domains have different requirements (financial systems may need 90% coverage, prototypes 60%).

**Default configuration**:
```yaml
# .specify/brownfield-config.yaml
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

**Implementation**: Generate default config on `brownfield init`, allow per-project customization.

---

**Decision 3: Multiple brownfield projects in parallel → Yes, support multiple numbered projects**

**Rationale**: Matches Spec-Kit's architectural pattern (multiple numbered specs). Enables team scalability where different developers remediate different subsystems simultaneously. Large codebases have multiple independent areas (API, database, UI) that benefit from parallel work.

**Implementation**: Each brownfield project gets numbered directory (`.specify/brownfield/001-api/`, `.specify/brownfield/002-database/`). Commands accept optional `--project 001` flag. Active project tracked in `.specify/memory/brownfield-state.json`. Example: `/brownfield.assess --project 002` runs assessment on project 002.

## References

- **Spec-Kit**: `github.com/github/spec-kit` (architectural pattern to follow)
- **BP-Kit**: `~/bpkit/` (plugin integration pattern reference)
- **Spec-Kit Discussion #331**: "Recommended approach for brownfield development" (community gap this tool addresses)
- **Quality Tools**:
  - Lizard: Code complexity analyzer (CCN metrics)
  - pytest + coverage: Test coverage measurement
  - Bandit: Python security vulnerability scanner
- **Competitive Analysis**: CodeGraph MCP, CodeScene, SonarQube (existing solutions that measure but don't enforce remediation-first workflow)
