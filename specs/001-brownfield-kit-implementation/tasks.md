# Tasks: BrownKit Implementation

**Input**: Design documents from `/specs/001-brownkit-implementation/`
**Prerequisites**: plan.md (✓), spec.md (✓), research.md (✓), data-model.md (✓), contracts/ (✓)

**Tests**: Tests are NOT requested in the feature specification - tasks focus on implementation only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/brownfield/`, `tests/` at repository root (Python CLI tool)
- All tasks reference absolute or repo-relative paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create Python project structure per plan.md (src/brownfield/, tests/, .specify/)
- [X] T002 [P] Initialize pyproject.toml with project metadata and dependencies (click, gitpython, rich, lizard, coverage)
- [X] T003 [P] Create requirements.txt with all runtime dependencies
- [X] T004 [P] Create requirements-dev.txt with development dependencies (pytest, black, pylint)
- [X] T005 [P] Configure pylint with .pylintrc for project-specific rules
- [X] T006 [P] Configure black formatting in pyproject.toml (line-length=100)
- [X] T007 [P] Create .gitignore for Python project (__pycache__/, .venv/, .pytest_cache/, .coverage)
- [X] T008 Create README.md with project overview and quick start guide
- [X] T009 Create LICENSE file (appropriate open source license)

**Checkpoint**: Project structure ready - core module development can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T010 [P] Create data models in src/brownfield/models/assessment.py (AssessmentReport, LanguageDetection, Metrics, TechDebtCategory from data-model.md)
- [X] T011 [P] Create data models in src/brownfield/models/state.py (BrownfieldState, Phase enum, ReEntryEvent from data-model.md)
- [X] T012 [P] Create data models in src/brownfield/models/checkpoint.py (PhaseCheckpoint, Task from data-model.md)
- [X] T013 [P] Create data models in src/brownfield/models/decision.py (DecisionEntry, Alternative, Risk, ConfidenceLevel from data-model.md)
- [X] T014 [P] Create data models in src/brownfield/models/gate.py (ReadinessGate, READINESS_GATES constant from data-model.md)
- [X] T015 [P] Create data models in src/brownfield/models/report.py (GraduationReport, StructuralChange, TestImprovement, SecurityFix from data-model.md)
- [X] T016 Create plugin base class in src/brownfield/plugins/base.py (LanguageHandler ABC, DetectionResult, StructureResult, TestSetupResult, QualitySetupResult from plugin-interface.md)
- [X] T017 Create plugin registry in src/brownfield/plugins/registry.py (@register_handler decorator, get_handler(), list_supported_languages() from research.md)
- [X] T018 Create state persistence in src/brownfield/state/state_store.py (BrownfieldState load/save with JSON serialization)
- [X] T019 [P] Create checkpoint manager in src/brownfield/state/checkpoint_store.py (PhaseCheckpoint persistence, interruption detection)
- [X] T020 [P] Create decision logger in src/brownfield/state/decision_logger.py (DecisionEntry append-only logging to brownfield-decisions.md)
- [X] T021 [P] Create report writer in src/brownfield/state/report_writer.py (Markdown generation for assessment and graduation reports)
- [X] T022 Create git safe commit in src/brownfield/git/safe_commit.py (atomic commits with [brownfield] prefix from research.md)
- [X] T023 [P] Create auto-revert in src/brownfield/git/auto_revert.py (build failure detection and automatic git revert from research.md)
- [X] T024 [P] Create history tracker in src/brownfield/git/history_tracker.py (commit tracking, rollback procedures)
- [X] T025 [P] Create branch guard in src/brownfield/git/branch_guard.py (prevent force push to main/master from constitution.md)
- [X] T026 [P] Create file operations utils in src/brownfield/utils/file_operations.py (pathlib wrappers, safe file moves)
- [X] T027 [P] Create process runner utils in src/brownfield/utils/process_runner.py (subprocess wrappers for language tools)
- [X] T028 [P] Create output formatter utils in src/brownfield/utils/output_formatter.py (Rich console formatting, progress bars)
- [X] T029 [P] Create config utils in src/brownfield/utils/config.py (load .brownfield.toml, environment variable handling)
- [X] T030 Create CLI command group in src/brownfield/cli/commands.py (@click.group() brownfield entry point from cli-commands.md)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Automated Codebase Assessment (Priority: P1) 🎯 MVP

**Goal**: Detect language, measure baseline metrics, identify tech debt, generate assessment report

**Independent Test**: Run `brownfield assess` on fixture project, verify assessment-report.md and brownfield-state.json created with accurate metrics

### Implementation for User Story 1

- [X] T031 [P] [US1] Create language detector in src/brownfield/assessment/language_detector.py (detect primary/secondary languages with confidence levels from research.md)
- [X] T032 [P] [US1] Create metrics collector in src/brownfield/assessment/metrics_collector.py (test coverage, complexity, security scanning from plan.md)
- [X] T032a [P] [US1] Implement complexity measurement in Python handler using lizard subprocess (parse JSON output, calculate average/max/violations)
- [X] T032b [P] [US1] Implement security scanning in Python handler using bandit subprocess (parse JSON output, count by severity)
- [X] T032c [P] [US1] Implement LOC counting in MetricsCollector using tokei with fallback to manual counting
- [X] T032d [P] [US1] Integrate language handler calls in MetricsCollector.collect() method (call measure_complexity, scan_security, verify_build)
- [X] T033 [P] [US1] Create tech debt analyzer in src/brownfield/assessment/tech_debt_analyzer.py (categorize issues: structural, testing, docs, security from constitution.md)
- [X] T034 [P] [US1] Create report generator in src/brownfield/assessment/report_generator.py (generate assessment-report.md with baseline metrics from data-model.md)
- [X] T035 [US1] Create Python language handler in src/brownfield/plugins/python_handler.py (@register_handler('python'), implement detect() method with confidence levels)
- [ ] T035a [US1] Implement measure_complexity() in JavaScript handler using lizard subprocess
- [ ] T035b [US1] Implement scan_security() in JavaScript handler using npm audit
- [X] T036 [US1] Create JavaScript language handler in src/brownfield/plugins/javascript_handler.py (@register_handler('javascript'), implement detect() method)
- [X] T037 [US1] Create Rust language handler in src/brownfield/plugins/rust_handler.py (@register_handler('rust'), implement detect() method)
- [X] T038 [US1] Create Go language handler in src/brownfield/plugins/go_handler.py (@register_handler('go'), implement detect() method)
- [X] T039 [US1] Create phase orchestrator in src/brownfield/orchestrator/phase_machine.py (state machine for phase transitions from plan.md)
- [X] T040 [US1] Implement `brownfield assess` command in src/brownfield/cli/assess.py (--quick/--full, --output, --force, --language options from cli-commands.md)
- [X] T041 [US1] Add CLI command imports to src/brownfield/cli/commands.py (import assess command)
- [X] T042 [US1] Create __main__.py entry point in src/brownfield/__main__.py (enable `python -m brownfield` execution)

**Checkpoint**: At this point, User Story 1 should be fully functional - `brownfield assess` works on Python projects with REAL metrics (complexity, security, LOC, git commits). JavaScript/Rust/Go handlers need metric implementation (T035a-b for JS, similar tasks for Rust/Go).

---

## Phase 4: User Story 2 - Directory Structure Remediation (Priority: P2)

**Goal**: Generate refactoring plans for reorganizing project structure (human-in-the-loop approach)

**Independent Test**: Run `brownfield structure` on disorganized project, verify plan generated with IDE instructions; manually refactor; run `brownfield structure --verify` to confirm compliance

### Implementation for User Story 2

- [X] T043 [P] [US2] Create structure plan generation logic in src/brownfield/remediation/structure.py (analyze structure, generate markdown plan with IDE instructions, create shell script for file moves only - human-in-the-loop approach from plan.md)
- [X] T043a [US2] Create structure verification module in src/brownfield/remediation/structure_verifier.py (verify directory structure, build integrity, import integrity, no stray files - validates after manual refactoring from cli-commands.md)
- [X] T044 [US2] *DEPRECATED* - Removed automated execution in favor of human-in-the-loop approach (no automated file moves or import updates to avoid string replacement risks)
- [X] T045 [US2] Implement `brownfield structure` command in src/brownfield/cli/structure.py (default: generate plan, --verify: validate after manual refactoring, --output, --format from cli-commands.md)
- [X] T046 [US2] Add CLI command imports to src/brownfield/cli/commands.py (import structure command)
- [X] T047 [US2] *DEPRECATED* - Approval handler created in Phase 1-3 but not used for structure remediation (no automated destructive operations in human-in-the-loop approach)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - projects can be assessed, structure plans generated, manual refactoring verified

---

## Phase 5: User Story 3 - Test Infrastructure Bootstrapping (Priority: P3)

**Goal**: Add test framework, generate contract tests, achieve 60% coverage on core modules

**Independent Test**: Run `brownfield testing` on zero-coverage project, verify tests/ directory created, tests pass, coverage ≥60%

### Implementation for User Story 3

- [X] T048 [P] [US3] Create testing remediation logic in src/brownfield/remediation/testing.py (bootstrap test framework, generate tests from plan.md)
- [X] T049 [US3] Implement contract test generation for public APIs (identify exported functions, generate input/output tests from spec.md)
- [X] T050 [US3] Implement smoke test generation (basic import and instantiation tests)
- [X] T051 [US3] Integrate coverage measurement (pytest-cov for Python, jest --coverage for JS, etc.)
- [X] T052 [US3] Implement `brownfield testing` command in src/brownfield/cli/testing.py (--coverage-target, --core-modules, --skip-framework-install, --test-type from cli-commands.md)
- [X] T053 [US3] Add CLI command imports to src/brownfield/cli/commands.py (import testing command)

**Checkpoint**: At this point, User Stories 1, 2 AND 3 should all work independently - projects have structure and tests

---

## Phase 6: User Story 4 - Quality Gates Installation (Priority: P4)

**Goal**: Install linters, formatters, complexity analysis, pre-commit hooks, fix security issues

**Independent Test**: Run `brownfield quality` on project, verify linter/formatter configs created, pre-commit hooks installed, complexity documented

### Implementation for User Story 4

- [X] T054 [P] [US4] Create quality remediation logic in src/brownfield/remediation/quality.py (install linters, formatters, hooks from plan.md)
- [X] T055 [US4] Implement complexity analysis integration (lizard for Python/JS/Rust/Go, document exceptions from research.md)
- [X] T056 [US4] Implement security scanning integration (bandit, npm audit, cargo audit, gosec from plugin-interface.md)
- [X] T057 [US4] Implement pre-commit hooks installation (.pre-commit-config.yaml with linter/formatter/complexity checks from cli-commands.md)
- [X] T058 [US4] Implement `brownfield quality` command in src/brownfield/cli/quality.py (--skip-linter, --skip-formatter, --skip-hooks, --complexity-threshold, --fix-auto from cli-commands.md)
- [X] T059 [US4] Add CLI command imports to src/brownfield/cli/commands.py (import quality command)

**Checkpoint**: At this point, User Stories 1-4 should all work independently - projects have structure, tests, and quality gates

---

## Phase 7: User Story 5 - Readiness Validation and Graduation (Priority: P5)

**Goal**: Check all 7 readiness gates, compare metrics, generate Speckit constitution, graduate project

**Independent Test**: Run `brownfield validate` on passing project, verify all gates pass; run `brownfield graduate`, verify constitution and graduation report created

### Implementation for User Story 5

- [ ] T060 [P] [US5] Create validation runner in src/brownfield/remediation/validation.py (evaluate all 7 readiness gates from data-model.md)
- [ ] T061 [US5] Implement gate verification commands (run coverage, complexity, security, build checks from cli-commands.md)
- [ ] T062 [US5] Create gate validator in src/brownfield/orchestrator/gate_validator.py (pass/fail logic, remediation guidance from constitution.md)
- [ ] T063 [US5] Implement `brownfield validate` command in src/brownfield/cli/validate.py (--gate, --fail-fast, --report options from cli-commands.md)
- [ ] T064 [US5] Add CLI command imports to src/brownfield/cli/commands.py (import validate command)
- [ ] T065 [P] [US5] Create Speckit constitution generator (analyze tech stack, generate tailored constitution.md from spec.md)
- [ ] T066 [US5] Create Speckit templates generator (spec-template.md, plan-template.md, tasks-template.md from plan.md)
- [ ] T067 [US5] Create graduation report generator (baseline vs final metrics, structural changes summary from data-model.md)
- [ ] T068 [US5] Create artifact archival logic (move brownfield files to .specify/memory/brownfield-archive/ from cli-commands.md)
- [ ] T069 [US5] Implement `brownfield graduate` command in src/brownfield/cli/graduate.py (--force, --archive-path options from cli-commands.md)
- [ ] T070 [US5] Add CLI command imports to src/brownfield/cli/commands.py (import graduate command)

**Checkpoint**: At this point, User Stories 1-5 should all work independently - complete brownfield → Speckit transition workflow

---

## Phase 8: User Story 6 - Re-entry for Quality Regression (Priority: P6)

**Goal**: Detect quality regressions (coverage drop, complexity increase, security breach), allow re-entry at appropriate phase

**Independent Test**: Degrade a graduated project (delete tests, add complexity), run `brownfield assess`, verify regression detection and re-entry recommendation

### Implementation for User Story 6

- [ ] T071 [P] [US6] Create regression detection in src/brownfield/state/state_store.py (compare current vs baseline metrics, detect threshold breaches from constitution.md)
- [ ] T072 [US6] Implement re-entry event logging in src/brownfield/models/state.py (ReEntryEvent tracking with trigger, baseline, current values from data-model.md)
- [ ] T073 [US6] Add regression detection to `brownfield assess` command (check for regressions after metrics collection, recommend phase from spec.md)
- [ ] T074 [US6] Create re-entry workflow in src/brownfield/orchestrator/phase_machine.py (allow phase restart for graduated projects from constitution.md)

**Checkpoint**: At this point, all user stories should work independently - full lifecycle including quality regression recovery

---

## Phase 9: Checkpoint Recovery & Utilities

**Purpose**: Interruption recovery and utility commands

- [ ] T075 [P] Create checkpoint manager in src/brownfield/orchestrator/checkpoint_manager.py (save/load checkpoints, detect interruptions from research.md)
- [ ] T076 [P] Implement `brownfield resume` command in src/brownfield/cli/resume.py (--restart option, offer checkpoint resumption from cli-commands.md)
- [ ] T077 [P] Implement `brownfield status` command in src/brownfield/cli/status.py (--json, --verbose options, show current phase and metrics from cli-commands.md)
- [ ] T078 Add CLI command imports to src/brownfield/cli/commands.py (import resume and status commands)
- [ ] T079 [P] Create signal handlers for graceful interruption (Ctrl+C saves checkpoint, exit code 130 from cli-commands.md)
- [ ] T080 [P] Add environment variable support (BROWNFIELD_PROJECT_ROOT, BROWNFIELD_VERBOSE, BROWNFIELD_AUTO_APPROVE from cli-commands.md)

**Checkpoint**: Complete CLI with all commands and interruption recovery

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T081 [P] Add shell completion support (--install-completion for bash/zsh/fish from cli-commands.md)
- [ ] T082 [P] Create .specify/templates/commands/ directory with brownfield slash command definitions from plan.md
- [ ] T083 [P] Create .specify/templates/commands/brownfield.assess.md (slash command wrapper)
- [ ] T084 [P] Create .specify/templates/commands/brownfield.structure.md (slash command wrapper)
- [ ] T085 [P] Create .specify/templates/commands/brownfield.testing.md (slash command wrapper)
- [ ] T086 [P] Create .specify/templates/commands/brownfield.quality.md (slash command wrapper)
- [ ] T087 [P] Create .specify/templates/commands/brownfield.validate.md (slash command wrapper)
- [ ] T088 [P] Create .specify/templates/commands/brownfield.graduate.md (slash command wrapper)
- [ ] T089 [P] Create .specify/templates/commands/brownfield.resume.md (slash command wrapper)
- [ ] T090 [P] Create .specify/templates/reports/assessment-report-template.md from plan.md
- [ ] T091 [P] Create .specify/templates/reports/graduation-report-template.md from plan.md
- [ ] T092 Update README.md with complete usage guide, examples, supported languages from quickstart.md
- [ ] T093 [P] Add error handling and logging throughout all modules (rich console output, log files)
- [ ] T094 [P] Add performance optimizations (caching, parallel operations where safe from research.md)
- [ ] T095 Validate against quickstart.md walkthrough (ensure developer onboarding guide matches implementation)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5 → P6)
- **Checkpoint Recovery (Phase 9)**: Can be developed in parallel with user stories
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Requires US1 (assessment) for practical use
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Requires US2 (structure) for practical use
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Requires US3 (testing) for practical use
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Requires US1-4 for practical validation
- **User Story 6 (P6)**: Can start after Foundational (Phase 2) - Requires US1 and US5 for regression detection

### Within Each User Story

- Models before services
- Services before CLI commands
- CLI commands before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a phase marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1 (Assessment)

```bash
# Launch all language handlers together:
Task: "Create Python language handler in src/brownfield/plugins/python_handler.py"
Task: "Create JavaScript language handler in src/brownfield/plugins/javascript_handler.py"
Task: "Create Rust language handler in src/brownfield/plugins/rust_handler.py"
Task: "Create Go language handler in src/brownfield/plugins/go_handler.py"

# Launch all assessment components together:
Task: "Create language detector in src/brownfield/assessment/language_detector.py"
Task: "Create metrics collector in src/brownfield/assessment/metrics_collector.py"
Task: "Create tech debt analyzer in src/brownfield/assessment/tech_debt_analyzer.py"
Task: "Create report generator in src/brownfield/assessment/report_generator.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Assessment)
4. **STOP and VALIDATE**: Test `brownfield assess` on multiple fixture projects
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Add User Story 6 → Test independently → Deploy/Demo
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Assessment)
   - Developer B: User Story 2 (Structure) - can start models/logic
   - Developer C: User Story 3 (Testing) - can start models/logic
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Tests are NOT included per feature specification - focus is on implementation only
- Follow constitution principles: incremental remediation, transparent reasoning, reversibility
