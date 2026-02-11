# Feature Specification: BrownKit Implementation

**Feature Branch**: `001-brownkit-implementation`
**Created**: 2025-10-12
**Status**: Draft
**Input**: User description: "BrownKit Implementation - AI-driven workflow for transitioning brownfield codebases to Speckit-ready state with automated assessment, structure fixes, testing infrastructure, and quality gates"

## Clarifications

### Session 2025-10-12

- Q: When automated remediation breaks the build, how should the system respond? → A: Automatically rollback the breaking change via git revert, log the failure, and continue with remaining changes
- Q: For monorepos with multiple languages (e.g., Python backend + JavaScript frontend), how should the system proceed? → A: Treat each major language as a separate subproject with its own structure, tests, and quality gates
- Q: When language tooling is missing (e.g., npm not installed for a JavaScript project), how should the system respond? → A: Detect missing tools, offer to install them via system package manager with user approval, skip phases requiring those tools if declined
- Q: For large codebases (>100,000 LOC), how should the system handle slow metric collection? → A: Offer choice: quick mode (sampling + heuristics) or full mode (complete analysis), default to quick with option to re-run full
- Q: When a user interrupts a phase (Ctrl+C, process kill), how should the system handle resumption? → A: Maintain phase checkpoint file tracking completed tasks; on restart, detect interruption and offer to resume from checkpoint or restart phase

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automated Codebase Assessment (Priority: P1)

A developer inherits a brownfield codebase with poor structure, missing tests, and no documentation. They run the assessment command to understand the current state, identify technical debt, and receive a baseline report showing test coverage, complexity metrics, security vulnerabilities, and structural issues.

**Why this priority**: Assessment is the foundation - cannot improve what you don't measure. This is the entry point for the entire workflow and provides the data needed for all subsequent phases.

**Independent Test**: Can be fully tested by running the assessment command on various brownfield projects (Python, JavaScript, Rust) and verifying that reports are generated with accurate language detection, metrics baselines, and tech debt categorization.

**Acceptance Scenarios**:

1. **Given** a Python project with no tests and disorganized structure, **When** user runs assessment command, **Then** system detects Python with high confidence, reports 0% test coverage, identifies missing tests/ directory, and flags complexity violations
2. **Given** a JavaScript project with mixed ES6/CommonJS and no package.json, **When** assessment runs, **Then** system detects JavaScript/Node, flags missing build configuration, and identifies module system inconsistency
3. **Given** a project with security vulnerabilities, **When** assessment runs, **Then** system runs appropriate security scanner (bandit, npm audit, etc.) and reports critical/high/medium vulnerabilities with counts
4. **Given** a multi-language repository, **When** assessment runs, **Then** system detects primary language by file count and reports confidence level with detected secondary languages

---

### User Story 2 - Directory Structure Remediation (Priority: P2)

A developer receives an assessment report showing structural issues. They run the structure command, which analyzes the project and generates a detailed refactoring plan with IDE-specific instructions. The developer uses their IDE's refactoring tools (PyCharm "Move Module", VSCode drag-and-drop with import updates) to safely reorganize files, then runs verification to confirm structure compliance and build integrity.

**Why this priority**: Structure is foundational infrastructure. Without proper organization, testing and quality tools cannot function correctly. This must happen before adding test frameworks or linters. **Human-in-the-loop approach ensures IDE refactoring tools handle import updates correctly**, avoiding risks of naive string replacement breaking code.

**Independent Test**: Can be tested independently by running structure command to generate plan, manually executing refactoring with IDE tools, then running verification to confirm structure matches ecosystem conventions and build passes.

**Acceptance Scenarios**:

1. **Given** a Python project with source files in root directory, **When** structure command runs with default mode, **Then** system generates detailed plan showing files to move (main.py → src/myproject/main.py), creates shell script for file operations, and provides IDE-specific instructions for PyCharm/VSCode refactoring
2. **Given** a generated refactoring plan, **When** developer uses IDE refactoring tools to move files, **Then** IDE automatically updates all import paths, handles relative imports correctly, and maintains code integrity
3. **Given** manual refactoring complete, **When** developer runs structure --verify, **Then** system checks directory structure compliance, verifies build passes, confirms import integrity, and validates no stray files in root
4. **Given** verification passes, **When** system updates state, **Then** brownfield-state.json advances to Phase.TESTING and records structure completion timestamp

---

### User Story 3 - Test Infrastructure Bootstrapping (Priority: P3)

A developer with a structured but untested codebase runs the testing command. The system adds appropriate test framework dependencies, creates test directory structure, generates example smoke tests, and implements contract tests for detected public APIs until achieving 60% coverage on core modules.

**Why this priority**: Tests are the safety net required before refactoring or adding features. This builds on the structured foundation from User Story 2 and enables confident code changes.

**Independent Test**: Can be tested by running testing command on a zero-coverage codebase and verifying that test framework is installed, tests pass, and coverage reports show 60%+ on core business logic.

**Acceptance Scenarios**:

1. **Given** a Python project with 0% coverage, **When** testing command runs, **Then** system adds pytest to dependencies, creates tests/ directory with conftest.py, generates smoke test that passes, and creates coverage report
2. **Given** a project with public API functions, **When** testing command runs, **Then** system identifies exported functions, generates contract tests verifying input/output types and error handling, and places tests in tests/contract/
3. **Given** a codebase with unclear business logic, **When** testing command runs, **Then** system asks user which modules are core business logic before generating tests
4. **Given** core modules after test generation, **When** coverage is measured, **Then** system reports at least 60% line coverage on identified core modules

---

### User Story 4 - Quality Gates Installation (Priority: P4)

A developer with tests in place runs the quality command to add linting, formatting, complexity analysis, and security scanning. The system configures appropriate tools (eslint, pylint, black, prettier, lizard), adds pre-commit hooks, fixes critical security issues, and ensures complexity stays below 10.

**Why this priority**: Quality gates prevent regression and enforce standards. This builds on testing infrastructure and provides continuous guardrails for future development.

**Independent Test**: Can be tested by running quality command and verifying that linters are configured, pre-commit hooks block bad commits, and complexity/security reports pass thresholds.

**Acceptance Scenarios**:

1. **Given** a Python project with tests, **When** quality command runs, **Then** system adds pylint and black to dev dependencies, creates .pylintrc and pyproject.toml configs, and configures pre-commit hooks
2. **Given** a codebase with functions having cyclomatic complexity > 10, **When** quality command runs, **Then** system identifies complex functions, suggests refactoring, and documents justified complexity in complexity-justification.md
3. **Given** a project with critical security vulnerabilities, **When** quality command runs, **Then** system runs security scanner, attempts automated fixes for common issues (dependency updates), and reports remaining vulnerabilities requiring manual review
4. **Given** quality tools configured, **When** developer attempts to commit code with linting errors, **Then** pre-commit hook blocks the commit and displays specific errors to fix

---

### User Story 5 - Readiness Validation and Graduation (Priority: P5)

A developer who has completed assessment, structure, testing, and quality phases runs the validation command. The system re-runs all metrics, compares against baseline, checks all 7 readiness gates, and if passing, generates a project-specific Speckit constitution and graduation report for transitioning to spec-driven development.

**Why this priority**: Validation ensures quality standards are met before graduation. This is the final gate and handoff to Speckit workflow, completing the brownfield transition.

**Independent Test**: Can be tested by running validation on a codebase that meets all gates and verifying that graduation artifacts are generated (Speckit constitution, templates, graduation report).

**Acceptance Scenarios**:

1. **Given** a codebase meeting all 7 readiness gates, **When** validation command runs, **Then** system confirms all gates pass, generates progress report showing baseline vs. current metrics, and prompts user for graduation
2. **Given** a codebase failing test coverage gate (50% instead of 60%), **When** validation command runs, **Then** system identifies coverage gap, reports which modules need tests, and suggests returning to testing phase
3. **Given** user approves graduation, **When** graduation proceeds, **Then** system generates Speckit constitution tailored to detected tech stack, creates spec/plan/tasks templates with project structure, and archives brownfield assessment data
4. **Given** graduation complete, **When** user checks repository, **Then** brownfield-graduation-report.md exists summarizing all changes made, brownfield-state.json shows graduation timestamp, and user can run /speckit.specify

---

### User Story 6 - Re-entry for Quality Regression (Priority: P6)

A developer working in Speckit mode notices test coverage has dropped to 45% and build warnings have increased. They run the brownfield assessment again, which detects regression, documents what degraded, and allows re-entering brownfield workflow at the appropriate phase (testing or quality) to restore standards.

**Why this priority**: Quality can degrade over time. Re-entry criteria ensure projects can recover when standards slip without starting from scratch.

**Independent Test**: Can be tested by degrading a graduated project (delete tests, add complexity) and verifying that re-entry assessment correctly identifies regressions and recommends appropriate phase.

**Acceptance Scenarios**:

1. **Given** a graduated project with test coverage dropped from 65% to 45%, **When** brownfield assessment runs, **Then** system detects 20-point coverage regression, flags re-entry criteria breach, and recommends Phase 2 (Testing)
2. **Given** a project with new critical security vulnerability, **When** assessment runs, **Then** system detects vulnerability, flags security gate failure, and recommends Phase 3 (Quality) to address
3. **Given** regression detected, **When** user confirms re-entry, **Then** system documents regression cause in brownfield-decisions.md, updates brownfield-state.json with re-entry timestamp, and starts at recommended phase
4. **Given** re-entry phase completed, **When** validation runs again, **Then** system compares new metrics against original graduation metrics and confirms standards are restored

---

### Edge Cases

- For mixed-language monorepos, system treats each major language (with significant LOC presence) as a separate subproject with independent directory structure, test framework, and quality gates; reports all detected languages with their respective metrics
- How does the system handle codebases with no git repository initialized?
- When required language tools are missing, system detects them during assessment, offers to install via system package manager (apt, brew, pacman) with user approval, and skips phases requiring declined tools while documenting limitations in assessment report
- How does the system handle codebases with proprietary or custom build systems not matching standard patterns?
- When automated fixes (structure moves, import updates) break the build, system automatically reverts the breaking change via git revert, logs the failure with error details to brownfield-decisions.md, and continues processing remaining changes
- For large codebases (>100,000 LOC), system offers analysis mode choice: quick mode (samples representative modules, uses heuristics for estimates, completes in <10 minutes) or full mode (analyzes entire codebase thoroughly); defaults to quick mode with option to re-run full analysis later
- When user interrupts phase execution (Ctrl+C, process kill), system maintains checkpoint file (.specify/memory/brownfield-checkpoint.json) tracking completed tasks; on next run, system detects interruption and offers to resume from last checkpoint or restart phase from beginning
- How does the system handle projects with external dependencies (databases, APIs) that cannot be verified without credentials?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect all programming languages by analyzing file extensions, import statements, and configuration files, reporting confidence level (High/Medium/Low) for each; for monorepos with multiple major languages, system MUST treat each as a separate subproject with independent workflows
- **FR-002**: System MUST generate baseline metrics including test coverage percentage, cyclomatic complexity scores, build status, documentation coverage, and security vulnerability counts; system MUST detect missing language tooling and offer installation via system package manager with user approval
- **FR-002a**: System MUST skip phases requiring tools that user declined to install and document these limitations in assessment report
- **FR-002b**: For codebases exceeding 100,000 LOC, system MUST offer analysis mode selection: quick mode (sampling-based, <10 minute target) or full mode (comprehensive); system MUST default to quick mode and allow re-running full analysis later
- **FR-003**: System MUST store assessment results in .specify/memory/assessment-report.md with timestamp and AI agent version
- **FR-004**: System MUST create separate git commits for each structural change with descriptive messages following format: [brownfield] <category>: <description>
- **FR-004a**: System MUST maintain phase checkpoint file (.specify/memory/brownfield-checkpoint.json) recording completed tasks; on restart after interruption, system MUST detect incomplete phase and offer resumption from checkpoint or full phase restart
- **FR-005**: System MUST ask for user approval before destructive operations including deleting files, renaming more than 5 files, or modifying build configurations
- **FR-006**: System MUST analyze current structure and generate detailed refactoring plan showing files to move to ecosystem-standard directories (Python: src/, tests/, docs/; JavaScript: src/, test/; Rust: src/, tests/; Go: cmd/, pkg/, internal/), including shell script for file moves and IDE-specific refactoring instructions
- **FR-006a**: System MUST provide --verify mode that checks directory structure compliance, runs build verification, validates import integrity, and confirms no misplaced files remain
- **FR-007**: System SHOULD NOT attempt automated import path updates via string replacement; instead, system MUST guide users to use IDE refactoring tools (PyCharm "Move Module", VSCode with import updates) that handle imports correctly via AST parsing
- **FR-008**: System MUST add test framework appropriate to detected language (pytest for Python, jest for JavaScript, cargo test for Rust)
- **FR-009**: System MUST generate contract tests for detected public APIs verifying input/output types and error handling
- **FR-010**: System MUST achieve minimum 60% test coverage on core business logic modules before exiting testing phase
- **FR-011**: System MUST add linter configuration appropriate to detected language (pylint, eslint, clippy, etc.)
- **FR-012**: System MUST add formatter configuration appropriate to detected language (black, prettier, rustfmt, etc.)
- **FR-013**: System MUST configure pre-commit hooks that block commits with linting errors, formatting violations, or complexity exceeding 10
- **FR-014**: System MUST run security scanner appropriate to detected ecosystem (bandit, npm audit, cargo audit) and report vulnerability counts by severity
- **FR-015**: System MUST validate all 7 readiness gates (test coverage ≥60%, complexity <10, structure follows conventions, build passes cleanly, APIs documented, zero critical vulnerabilities, git hygiene)
- **FR-016**: System MUST generate project-specific Speckit constitution upon graduation based on detected tech stack and architectural patterns
- **FR-017**: System MUST create brownfield-state.json tracking current phase, metrics, and timestamps for assessment, phase completions, and graduation
- **FR-018**: System MUST document all decisions with problem, solution, confidence level, alternatives considered, and risks in .specify/memory/brownfield-decisions.md
- **FR-019**: System MUST detect quality regression when test coverage drops below 50%, complexity exceeds 12, critical vulnerabilities are introduced, or build produces >10 warnings
- **FR-020**: System MUST allow re-entry at appropriate phase (testing or quality) when regression is detected without requiring full workflow restart

### Key Entities

- **Assessment Report**: Contains language detection results with confidence levels, baseline metrics (coverage, complexity, security, build), tech debt categories (structural, testing, documentation, security), assumptions about project purpose, analysis limitations, and risk assessment
- **Brownfield State**: Tracks current phase (Assessment, Structure, Testing, Quality, Validation, Graduation), baseline metrics, current metrics, phase completion timestamps, re-entry events, and graduation timestamp
- **Phase Checkpoint**: Records completed tasks within current phase, interruption detection flag, timestamp of last checkpoint update, and resumption options for interrupted phases
- **Decision Log**: Records significant changes with problem identified (with evidence), proposed solution and rationale, confidence level (High/Medium/Low), alternatives considered, risks and mitigation strategies, and rollback procedures
- **Readiness Gate**: Represents one of 7 validation criteria with name, metric threshold, verification command, current status (pass/fail), and exception conditions
- **Phase**: Represents one of 5 workflow stages with entry criteria, activities list, exit gate definition, human review points, and next phase transition rules
- **Graduation Report**: Summarizes baseline vs. final metrics, all structural changes made, test coverage improvements, security issues resolved, archived brownfield artifacts location, and generated Speckit constitution location

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can run assessment command on any brownfield codebase and receive a complete report within 5 minutes for projects <50,000 LOC, or within 10 minutes using quick mode for projects >100,000 LOC
- **SC-002**: System correctly detects primary language with high confidence in 90% of standard project structures (Python, JavaScript, Rust, Go)
- **SC-003**: Structure command generates actionable refactoring plans with IDE instructions in 100% of supported languages; verification correctly identifies structure compliance and import integrity in 98% of cases after manual refactoring
- **SC-004**: Test infrastructure setup achieves 60% coverage on core modules within one automated pass for simple projects (<5,000 LOC)
- **SC-005**: Quality gates installation reduces cyclomatic complexity violations by 80% compared to baseline
- **SC-006**: Validation correctly identifies all 7 readiness gate failures with specific remediation guidance
- **SC-007**: Graduation generates a working Speckit constitution that allows immediate use of /speckit.specify without errors
- **SC-008**: Re-entry detection identifies quality regressions within one assessment run with 95% accuracy
- **SC-009**: All automated changes are reversible via git revert without requiring manual conflict resolution in 98% of cases
- **SC-010**: Complete brownfield workflow (assessment through graduation) completes in under 2 hours for typical projects (<10,000 LOC, <5 core modules)

## Assumptions

- Users have git installed and codebases are either already git repositories or can be initialized
- System has access to a package manager (apt, brew, pacman, or equivalent) for installing missing language tooling when needed
- Codebases follow reasonably standard structures (not exotic custom build systems)
- Core business logic can be identified through heuristics (files in src/, lib/, or similar, excluding config/scripts)
- Users can provide domain knowledge when AI cannot determine what to test
- Standard ecosystem conventions exist for detected languages (Python: src/tests, JavaScript: src/test, etc.)
- Security scanners (bandit, npm audit, cargo audit) are available for detected languages
- For multi-language monorepos, each language with >1000 LOC is treated as a major subproject requiring full workflow

## Dependencies

- Existing Speckit installation and templates (constitution.md, spec-template.md, plan-template.md, tasks-template.md)
- Git version control system
- Language-specific tooling: python/pip, node/npm, rust/cargo, go toolchain
- Code analysis tools: lizard (complexity), coverage.py/jest/cargo-tarpaulin (coverage)
- Security scanners: bandit, npm audit, cargo audit
- Linters and formatters: pylint/black, eslint/prettier, clippy/rustfmt

## Out of Scope

- Supporting languages without standard ecosystem conventions (proprietary languages, legacy systems)
- Migrating codebases between languages (e.g., Python to Rust)
- Refactoring business logic to improve complexity (only identifies violations, doesn't auto-fix)
- Fixing all security vulnerabilities automatically (only critical/high with known patches, rest require manual review)
- Providing domain-specific test generation (requires human input for business logic validation)
- Managing external dependencies like databases, message queues, or third-party APIs
- Converting non-git version control systems to git
- Generating comprehensive documentation beyond baseline API docs and README
