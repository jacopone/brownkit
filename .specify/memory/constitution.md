<!--
SYNC IMPACT REPORT
==================
Version Change: TEMPLATE → 1.0.0
Change Type: Initial Constitution Creation
Date: 2025-10-12

New Constitution: Brownfield-Kit
Purpose: Defines governance for transitioning brownfield codebases to Speckit-ready state

Core Principles Added:
1. ASSESSMENT_DRIVEN_DEVELOPMENT - Automated analysis before changes
2. SAFETY_NET_FIRST - Testing infrastructure before features
3. INCREMENTAL_REMEDIATION - Small, verifiable improvements
4. TRANSPARENT_REASONING - AI documents decisions and confidence
5. MEASURABLE_PROGRESS - Quantitative phase transition gates
6. STRUCTURE_INTEGRITY - Directory organization per ecosystem conventions
7. REVERSIBILITY - All changes git-trackable and reviewable

New Sections Added:
- Readiness Gates (graduation criteria to Speckit)
- AI Self-Assessment Requirements
- Phase Governance (5-phase workflow)
- Re-entry Criteria (when to return to brownfield mode)

Templates Requiring Updates:
- ✅ plan-template.md: Constitution Check section compatible (uses generic gates)
- ✅ spec-template.md: No constitution-specific references, compatible as-is
- ✅ tasks-template.md: Phase structure aligns with brownfield phases
- ⚠️ PENDING: Create brownfield-specific command files in .specify/templates/commands/

Follow-up TODOs:
- Create slash command: /brownfield.assess (initial codebase scan)
- Create slash command: /brownfield.structure (fix directory organization)
- Create slash command: /brownfield.testing (add test infrastructure)
- Create slash command: /brownfield.quality (add quality gates)
- Create slash command: /brownfield.validate (check readiness for Speckit)
- Create slash command: /brownfield.graduate (generate Speckit constitution and handoff)
- Create state tracking file: .specify/memory/brownfield-state.json
- Create assessment report template: .specify/memory/assessment-report.md
-->

# Brownfield-Kit Constitution

## Purpose & Scope

Brownfield-Kit is a transition system that prepares codebases for Speckit adoption. It provides a structured workflow for AI agents to transform unstructured, under-tested, and poorly documented codebases into projects that meet the safety, quality, and structural standards required for spec-driven development.

**Relationship to Speckit**: Brownfield-Kit is a prerequisite system. Once graduation criteria are met, Brownfield-Kit generates a project-specific Speckit constitution and hands off control to Speckit workflows.

**When to Use Brownfield-Kit**:
- Codebases lacking test infrastructure (< 60% coverage on core modules)
- Projects with cyclomatic complexity > 10 (measured via lizard or equivalent)
- Disorganized directory structures violating ecosystem conventions
- Missing or outdated documentation for public APIs
- No CI/CD pipeline or failing builds with warnings
- Critical security vulnerabilities present

**When NOT to Use Brownfield-Kit**:
- Greenfield projects (new codebases) → Use Speckit directly
- Well-maintained codebases meeting readiness gates → Use Speckit directly
- Simple scripts or tools (< 500 lines, single file) → No workflow needed

## Core Principles

### I. ASSESSMENT_DRIVEN_DEVELOPMENT

**Principle**: All changes MUST be preceded by automated codebase analysis. AI agents MUST NOT make assumptions about project structure, tech stack, or architectural patterns without evidence.

**Requirements**:
- Run language/framework detection before any modifications
- Document all detected technologies with confidence levels (High/Medium/Low)
- Identify tech debt categories: structural, testing, documentation, security, performance
- Generate baseline metrics before any remediation begins
- Store assessment results in `.specify/memory/assessment-report.md`
- Re-assess after each major phase completion to track progress

**Rationale**: Brownfield codebases often have hidden complexity, legacy dependencies, and undocumented architectural decisions. Blind changes risk breaking functionality. Assessment creates a fact-based foundation for improvement.

### II. SAFETY_NET_FIRST

**Principle**: Testing infrastructure MUST be established BEFORE implementing new features or refactoring existing code. AI agents MUST prioritize test coverage and quality gates over functional enhancements.

**Requirements**:
- Add test framework appropriate to detected language (pytest, jest, cargo test, etc.)
- Achieve minimum 60% test coverage on core business logic modules
- Establish contract tests for public APIs/interfaces
- Implement integration tests for critical user journeys
- Add pre-commit hooks for linting, formatting, and complexity checks
- All tests MUST pass before proceeding to next phase

**Rationale**: Without tests, refactoring and feature work introduce regression risk. Tests provide confidence that improvements don't break existing functionality. This principle is non-negotiable.

### III. INCREMENTAL_REMEDIATION

**Principle**: Improvements MUST be small, verifiable, and independently committable. AI agents MUST avoid large rewrites or multi-file refactors that cannot be reviewed atomically.

**Requirements**:
- Each remediation task targets a single concern (one file, one module, one quality issue)
- Changes are committed immediately after verification
- Git commit messages explain rationale and impact
- If a change affects > 10 files or > 500 lines, break into smaller tasks
- Each commit MUST leave the codebase in a working state (builds pass, tests pass)
- Document rollback steps for each change in commit message

**Rationale**: Large changes are difficult to review, debug, and rollback. Incremental improvements allow humans to validate progress and catch issues early. This approach reduces risk and builds trust in AI-generated changes.

### IV. TRANSPARENT_REASONING

**Principle**: AI agents MUST document all decisions, assumptions, and confidence levels. Humans MUST be able to understand why changes were made and what alternatives were considered.

**Requirements**:
- Create decision log at `.specify/memory/brownfield-decisions.md`
- For each significant change, document:
  - Problem identified (with evidence from assessment)
  - Proposed solution and rationale
  - Confidence level (High/Medium/Low) and reasoning
  - Alternative approaches considered and why rejected
  - Risks and mitigation strategies
- When confidence is Medium or Low, ASK for human review before proceeding
- Document assumptions about project purpose, architecture, and constraints
- Flag areas where analysis is incomplete (e.g., "Cannot verify database schema without credentials")

**Rationale**: AI agents make probabilistic decisions. Transparency allows humans to validate reasoning, correct misunderstandings, and learn from the AI's approach. This principle builds accountability and collaboration.

### V. MEASURABLE_PROGRESS

**Principle**: All phase transitions MUST be gated by quantitative metrics. AI agents MUST track progress against baseline and report metrics at each checkpoint.

**Requirements**:
- Establish baseline metrics during assessment phase:
  - Test coverage percentage (via coverage.py, jest --coverage, etc.)
  - Cyclomatic complexity (via lizard, radon, gocyclo, etc.)
  - Build success rate and warning count
  - Documentation coverage (public APIs with docstrings/comments)
  - Security vulnerability count (via bandit, npm audit, cargo audit, etc.)
- Track delta (improvement) after each phase
- Store metrics in `.specify/memory/brownfield-state.json`
- Generate progress report comparing current vs. baseline
- Do NOT proceed to next phase until gate metrics are met

**Readiness Gates** (see Governance section for full criteria)

**Rationale**: Subjective assessments ("code looks better") are insufficient. Quantitative metrics provide objective evidence of improvement and clear exit criteria for transitioning to Speckit.

### VI. STRUCTURE_INTEGRITY

**Principle**: Directory organization and file naming MUST follow ecosystem conventions for the detected language/framework. AI agents MUST NOT invent novel structures when standard patterns exist.

**Requirements**:
- Detect project type: single binary, library, web app (frontend + backend), mobile app, monorepo
- Apply standard structure for detected ecosystem:
  - Python: `src/`, `tests/`, `docs/`, `pyproject.toml` or `setup.py`
  - JavaScript/Node: `src/`, `test/`, `package.json`, `node_modules/` gitignored
  - Rust: `src/`, `tests/`, `Cargo.toml`, target/ gitignored
  - Go: `cmd/`, `pkg/`, `internal/`, `go.mod`
  - (Add ecosystem-specific conventions as detected)
- Move misplaced files to correct locations
- Create missing standard directories (e.g., tests/ if absent)
- Update import paths and references after moves
- Ensure build tool configurations (package.json, Cargo.toml, etc.) reflect new structure

**Rationale**: Consistent structure improves discoverability, maintainability, and tooling integration. Standard patterns reduce cognitive load for developers and enable AI agents to navigate codebases efficiently.

### VII. REVERSIBILITY

**Principle**: All automated changes MUST be git-trackable, reviewable, and revertable. AI agents MUST NOT make irreversible modifications without explicit human approval.

**Requirements**:
- Every change creates a git commit with descriptive message
- Commit message format: `[brownfield] <category>: <description>`
  - Categories: assess, structure, testing, quality, docs
  - Example: `[brownfield] structure: move src files to src/ directory`
- NEVER use `git commit --amend` or `git rebase` without explicit user request
- NEVER force push to main/master branches
- For destructive operations (file deletion, major refactor), create a backup branch first
- Ask for human approval before: deleting files, renaming > 5 files, modifying build configs

**Rationale**: AI agents can make mistakes. Git history provides an audit trail and rollback mechanism. Reversibility ensures humans maintain control over critical decisions.

## Readiness Gates (Graduation to Speckit)

**Brownfield-Kit → Speckit Transition Criteria**:

Graduation occurs when ALL of the following gates are met:

1. **Test Coverage Gate**: ≥ 60% test coverage on core business logic modules
   - Verification: Run coverage tool appropriate to language
   - Exception: If codebase is < 500 lines total, this gate is waived

2. **Complexity Gate**: Cyclomatic complexity (CCN) < 10 for all functions/methods
   - Verification: Run `lizard` or equivalent complexity analyzer
   - Exception: Document any functions with CCN ≥ 10 in complexity-justification.md

3. **Structure Gate**: Directory organization follows ecosystem conventions
   - Verification: Manual review of directory tree against standard patterns
   - All source files in appropriate directories (src/, lib/, pkg/, etc.)
   - All test files in test directories (tests/, test/, __tests__/, etc.)

4. **Build Gate**: CI/CD pipeline passes without errors or warnings
   - Verification: Run build command (npm run build, cargo build, make, etc.)
   - Zero warnings, zero errors
   - If no CI/CD exists, local build must succeed cleanly

5. **Documentation Gate**: Public APIs have documentation
   - Verification: Check for docstrings/JSDoc/comments on exported functions/classes
   - Minimum: Each public function has purpose description and parameter types
   - README.md exists with basic setup instructions

6. **Security Gate**: No critical vulnerabilities
   - Verification: Run security scanner (npm audit, cargo audit, bandit, etc.)
   - Zero critical or high-severity vulnerabilities
   - Medium/low vulnerabilities documented in known-issues.md

7. **Git Hygiene Gate**: Repository clean
   - Verification: No large binaries (> 1MB) in git history
   - No secrets, credentials, or API keys in codebase (use .env, secrets management)
   - .gitignore properly configured for ecosystem

**Upon Graduation**:
- Brownfield-Kit generates initial Speckit constitution tailored to project
- Assessment report and decision log archived in `.specify/memory/brownfield-archive/`
- State file updated with graduation timestamp
- Handoff summary created: `brownfield-graduation-report.md`

## AI Self-Assessment Requirements

AI agents operating in Brownfield-Kit mode MUST document the following in the initial assessment phase:

1. **Language/Framework Detection**:
   - Primary language (with confidence: High/Medium/Low)
   - Framework/runtime (with confidence)
   - Evidence for detection (file extensions, imports, config files)
   - Uncertainty areas (e.g., "Detected both Flask and Django imports - unclear which is primary")

2. **Tech Debt Categories Identified**:
   - Structural issues (misplaced files, missing directories)
   - Testing gaps (missing tests, low coverage areas)
   - Documentation deficiencies (undocumented APIs, missing README)
   - Security vulnerabilities (with severity levels)
   - Build/tooling issues (missing configs, broken builds)
   - Performance concerns (if detectable via profiling or obvious anti-patterns)

3. **Assumptions About Project**:
   - Inferred purpose (e.g., "appears to be a REST API for user management")
   - Inferred architecture (e.g., "monolithic web app with MVC pattern")
   - Confidence in assumptions (High/Medium/Low)
   - Areas where purpose/architecture is unclear

4. **Analysis Limitations**:
   - External dependencies that cannot be verified (databases, APIs, services)
   - Incomplete information (e.g., "no test coverage data available without running tests")
   - Tools not available (e.g., "cannot run security audit without npm/pip installed")
   - Human expertise required (e.g., "domain logic in `billing.py` requires business knowledge to validate")

5. **Risk Assessment**:
   - High-risk areas where automated fixes may break functionality
   - Recommended manual review points
   - Rollback procedures if issues arise

**Output**: All self-assessment results stored in `.specify/memory/assessment-report.md` with timestamp and AI agent version/model.

## Phase Governance

Brownfield-Kit operates in 5 sequential phases. Each phase has entry criteria, activities, and exit gates.

### Phase 0: Assessment (ENTRY POINT)

**Entry Criteria**: None (always starts here)

**Activities**:
1. Run AI self-assessment (see Self-Assessment Requirements section)
2. Detect language, framework, project type
3. Run metrics baseline: test coverage, complexity, build status, security scan
4. Generate assessment report
5. Create brownfield-state.json with baseline metrics

**Exit Gate**: Assessment report complete, baseline metrics captured

**Human Review Point**: Present assessment report to user, ask for corrections/clarifications

### Phase 1: Structure (FOUNDATION)

**Entry Criteria**: Phase 0 complete

**Activities**:
1. Create standard directory structure for detected ecosystem
2. Move misplaced files to correct locations
3. Update import paths and references
4. Create missing standard files (README.md, .gitignore, etc.)
5. Configure build tool if missing (package.json, Cargo.toml, pyproject.toml, etc.)
6. Commit each structural change separately

**Exit Gate**: Directory structure matches ecosystem conventions, build succeeds

**Human Review Point**: If > 10 files will be moved or deleted, ask for approval

### Phase 2: Testing (SAFETY NET)

**Entry Criteria**: Phase 1 complete

**Activities**:
1. Add test framework dependencies
2. Create test directory structure (tests/, test/, etc.)
3. Add example/smoke test to verify framework works
4. Implement contract tests for public APIs
5. Implement integration tests for critical user journeys
6. Achieve 60% test coverage on core modules
7. Configure coverage reporting

**Exit Gate**: Test coverage ≥ 60%, all tests pass

**Human Review Point**: If core business logic is unclear, ask for guidance on what to test

### Phase 3: Quality (GATES)

**Entry Criteria**: Phase 2 complete

**Activities**:
1. Add linter configuration (eslint, pylint, clippy, etc.)
2. Add formatter configuration (prettier, black, rustfmt, etc.)
3. Add complexity analyzer (lizard, radon, etc.)
4. Run security scanner (npm audit, bandit, cargo audit, etc.)
5. Fix critical and high-severity issues
6. Add pre-commit hooks for linting/formatting/complexity
7. Configure CI/CD pipeline (if absent)

**Exit Gate**: Complexity < 10, zero critical vulnerabilities, build passes with zero warnings

**Human Review Point**: If security fixes require architectural changes, ask for approval

### Phase 4: Validation (READINESS CHECK)

**Entry Criteria**: Phase 3 complete

**Activities**:
1. Re-run all metrics (coverage, complexity, security, build)
2. Compare current vs. baseline
3. Generate progress report
4. Check all readiness gates (see Readiness Gates section)
5. If any gate fails, return to appropriate phase

**Exit Gate**: All 7 readiness gates pass

**Human Review Point**: Present readiness report, ask if ready to graduate to Speckit

### Phase 5: Graduation (HANDOFF TO SPECKIT)

**Entry Criteria**: Phase 4 complete, all gates passed, user approval

**Activities**:
1. Generate project-specific Speckit constitution based on:
   - Detected tech stack
   - Architectural patterns observed
   - Team preferences (ask user for input)
2. Create initial spec-template.md tailored to project
3. Create initial plan-template.md with project structure
4. Archive brownfield assessment and decision log
5. Create graduation report summarizing all changes made
6. Update brownfield-state.json with graduation timestamp

**Exit Gate**: Speckit constitution created, graduation report delivered

**Output**: User can now run `/speckit.specify` to start spec-driven development

## Re-Entry Criteria (Brownfield → Speckit → Brownfield)

If a project has graduated to Speckit but later degrades below quality standards, re-enter Brownfield mode when ANY of:

- Test coverage drops below 50% (10% buffer from original gate)
- Cyclomatic complexity exceeds 12 (2-point buffer)
- Critical security vulnerabilities introduced
- Build fails or produces > 10 warnings
- Directory structure becomes disorganized (subjective, requires human judgment)

**Re-entry Procedure**:
1. Run brownfield assessment to identify regressions
2. Document what degraded and why
3. Return to appropriate phase (usually Phase 2 or 3, structure rarely regresses)
4. Re-validate and graduate again once gates are met

## Governance

### Amendment Procedure

1. Proposed changes to this constitution MUST be documented in a PR or issue
2. Changes require human approval (AI agents cannot amend the constitution autonomously)
3. Version bump follows semantic versioning:
   - MAJOR: Backward-incompatible changes (removing principles, changing gates drastically)
   - MINOR: Adding principles, adding phases, expanding requirements
   - PATCH: Clarifications, typos, non-semantic refinements
4. After amendment, update sync impact report at top of file

### Versioning Policy

- Version format: MAJOR.MINOR.PATCH
- All templates referencing the constitution MUST be reviewed and updated when MAJOR or MINOR version changes
- PATCH version changes do not require template updates

### Compliance Review

- After each phase completion, verify adherence to principles
- Document any principle violations in decision log with justification
- If violations cannot be justified, rollback changes and revise approach

### Rollback Procedure

If changes cause issues:
1. Identify problematic commit via git log
2. Run `git revert <commit-hash>` (do NOT use git reset)
3. Document what went wrong in decision log
4. Revise approach and try again
5. If multiple commits need rollback, ask human for guidance

**Version**: 1.0.0 | **Ratified**: 2025-10-12 | **Last Amended**: 2025-10-12
