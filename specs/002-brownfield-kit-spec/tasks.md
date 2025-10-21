---
description: "Implementation tasks for Brownfield-Kit Spec-Kit Plugin"
---

# Tasks: Brownfield-Kit - Spec-Kit Plugin for Legacy Code Remediation

**Input**: Design documents from `/specs/002-brownfield-kit-spec/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not explicitly requested in spec - no test tasks generated

**Organization**: Tasks grouped by user story to enable independent implementation and MVP delivery

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US7)
- File paths follow brownfield repository structure from plan.md

## Path Conventions
- Bash scripts: `.specify/scripts/bash/brownfield-*.sh`
- Slash commands: `templates/commands/brownfield.*.md`
- Templates: `templates/brownfield-*.md`
- Python CLI: `src/brownfield/*.py`
- Config templates: `templates/brownfield-config-template.yaml`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Brownfield-Kit project structure and foundational utilities

- [X] T001 Create project directory structure (templates/, .specify/, src/, tests/)
- [X] T002 [P] Create Python package setup in `pyproject.toml` with click dependency
- [X] T003 [P] Create LICENSE file (MIT) at repository root
- [X] T004 [P] Create shared utilities in `.specify/scripts/bash/brownfield-common.sh` (next_number, parse_json, validate_speckit)
- [X] T005 [P] Create brownfield-config-template.yaml in `templates/` with quality gate defaults

**Checkpoint**: Basic project structure ready for user story implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core bash script patterns and validation that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Implement `get_next_brownfield_number()` function in brownfield-common.sh using research.md pattern
- [X] T007 Implement `render_template()` function in brownfield-common.sh for markdown generation
- [X] T008 Implement `validate_speckit_installed()` function in brownfield-common.sh to check .specify/ existence
- [X] T009 Implement `run_quality_tool()` function in brownfield-common.sh with JSON parsing via jq
- [X] T010 [P] Create brownfield-assessment-template.md in `templates/` with placeholders for metrics
- [X] T011 [P] Create brownfield-plan-template.md in `templates/` with task structure
- [X] T012 [P] Create brownfield-validation-template.md in `templates/` with quality gate results

**Checkpoint**: Foundation ready - all bash utilities and templates available for slash commands

---

## Phase 3: User Story 1 - Install Brownfield-Kit (Priority: P0) 🎯 MVP

**Goal**: Enable developers to install Brownfield-Kit into existing Spec-Kit projects without conflicts

**Independent Test**: Run `brownfield init` in Spec-Kit project, verify .specify/brownfield/ created and no file overwrites

### Implementation for User Story 1

- [X] T013 [P] [US1] Create `src/brownfield/__init__.py` with package metadata
- [X] T014 [P] [US1] Create `src/brownfield/cli.py` with click `@cli.command('init')` function
- [X] T015 [US1] Implement `src/brownfield/core/validator.py` to detect Spec-Kit installation (checks .specify/, constitution.md)
- [X] T016 [US1] Implement `src/brownfield/core/installer.py` to copy templates and create .specify/brownfield/ structure
- [X] T017 [US1] Add conflict detection in installer.py (prevents overwriting .specify/scripts/bash/ files)
- [X] T018 [US1] Copy slash commands from `templates/commands/` to `.claude/commands/` during init
- [X] T019 [US1] Create `.specify/memory/brownfield-state.json` with initial state (empty projects array)
- [X] T020 [P] [US1] Create stub slash command `templates/commands/brownfield.ingest.md` (calls brownfield-ingest.sh)
- [X] T021 [P] [US1] Create stub slash command `templates/commands/brownfield.assess.md` (calls brownfield-assess.sh)
- [X] T022 [P] [US1] Create stub slash command `templates/commands/brownfield.plan.md` (calls brownfield-plan.sh)
- [X] T023 [P] [US1] Create stub slash command `templates/commands/brownfield.remediate.md` (calls brownfield-remediate.sh)
- [X] T024 [P] [US1] Create stub slash command `templates/commands/brownfield.validate.md` (calls brownfield-validate.sh)
- [X] T025 [P] [US1] Create stub slash command `templates/commands/brownfield.graduate.md` (calls brownfield-graduate.sh)

**Checkpoint**: `brownfield init` command fully functional, installs without conflicts, creates all slash commands

---

## Phase 4: User Story 2 - Ingest and Analyze Codebase (Priority: P0) 🎯 MVP

**Goal**: Analyze existing codebase architecture and generate codebase-analysis.md with framework detection

**Independent Test**: Run `/brownfield.ingest` on Python project, verify `.specify/memory/codebase-analysis.md` generated with architectural insights

### Implementation for User Story 2

- [ ] T026 [US2] Create `.specify/scripts/bash/brownfield-ingest.sh` with main function
- [ ] T027 [US2] Add framework detection logic to brownfield-ingest.sh (check for Flask, FastAPI, Django patterns)
- [ ] T028 [US2] Add tokei/lizard execution in brownfield-ingest.sh to get codebase statistics
- [ ] T029 [US2] Implement pattern discovery in brownfield-ingest.sh (repository pattern, service layer, MVC)
- [ ] T030 [US2] Generate codebase-analysis.md from template with discovered patterns and statistics
- [ ] T031 [US2] Update `.specify/memory/constitution.md` with discovered architectural patterns (append mode)
- [ ] T032 [US2] Return JSON output: `{"ANALYSIS_FILE": "/path/to/codebase-analysis.md"}`
- [ ] T033 [US2] Complete slash command `templates/commands/brownfield.ingest.md` with workflow documentation

**Checkpoint**: `/brownfield.ingest` generates architectural analysis and updates constitution

---

## Phase 5: User Story 3 - Assess Technical Debt Hotspots (Priority: P0) 🎯 MVP

**Goal**: Identify high-complexity functions, test coverage gaps, and security vulnerabilities with concrete metrics

**Independent Test**: Run `/brownfield.assess` on Python codebase, verify `001-*/assessment.md` generated with CCN values, coverage %, and vuln counts

### Implementation for User Story 3

- [ ] T034 [US3] Create `.specify/scripts/bash/brownfield-assess.sh` with main assessment workflow
- [ ] T035 [US3] Create numbered directory using `get_next_brownfield_number()` (e.g., `.specify/brownfield/001-legacy-api-cleanup/`)
- [ ] T036 [US3] Execute Lizard analysis: `lizard src/ --json > /tmp/brownfield-complexity.json`
- [ ] T037 [US3] Parse Lizard JSON output using jq, extract avg_ccn, max_ccn, functions_over_threshold
- [ ] T038 [US3] Execute pytest coverage: `pytest --cov=src --cov-report=json > /tmp/brownfield-coverage.json`
- [ ] T039 [US3] Parse coverage JSON, extract coverage_percent
- [ ] T040 [US3] Execute Bandit security scan: `bandit -r src/ -f json > /tmp/brownfield-security.json`
- [ ] T041 [US3] Parse Bandit JSON, extract critical_vulns, high_vulns counts
- [ ] T042 [US3] Render brownfield-assessment-template.md with all metrics into `001-*/assessment.md`
- [ ] T043 [US3] Generate prioritized hotspot list (sort by CCN descending, include file:line references)
- [ ] T044 [US3] Save metrics to `.brownfield/metrics/baseline.json` using metrics.schema.json format
- [ ] T045 [US3] Update `.specify/memory/brownfield-state.json` with new project entry
- [ ] T046 [US3] Return JSON output: `{"ASSESSMENT_FILE": "...", "METRICS": {...}, "BROWNFIELD_DIR": "..."}`
- [ ] T047 [US3] Complete slash command `templates/commands/brownfield.assess.md` with result parsing and summary generation

**Checkpoint**: `/brownfield.assess` generates numbered project with comprehensive assessment report and JSON metrics

---

## Phase 6: User Story 4 - Generate Remediation Plan (Priority: P0) 🎯 MVP

**Goal**: Convert assessment metrics into actionable remediation plan with specific tasks and quality gate checklist

**Independent Test**: Run `/brownfield.plan` after assessment, verify `plan.md` generated with concrete tasks mapped to assessment issues

### Implementation for User Story 4

- [ ] T048 [US4] Create `.specify/scripts/bash/brownfield-plan.sh` with plan generation workflow
- [ ] T049 [US4] Load active project from brownfield-state.json, read assessment.md and baseline.json
- [ ] T050 [US4] Analyze complexity hotspots, generate refactoring tasks (one task per function with CCN > 10)
- [ ] T051 [US4] Analyze coverage gaps, generate test creation tasks (prioritize untested modules)
- [ ] T052 [US4] Analyze security vulnerabilities, generate fix tasks (critical first, then high severity)
- [ ] T053 [US4] Render brownfield-plan-template.md with generated tasks into `001-*/plan.md`
- [ ] T054 [US4] Create `001-*/checklists/` directory
- [ ] T055 [US4] Generate `001-*/checklists/quality-gates.md` with measurable criteria (CCN < 10, coverage > 80%, zero critical vulns)
- [ ] T056 [US4] Calculate task count and estimate completion time
- [ ] T057 [US4] Return JSON output: `{"PLAN_FILE": "...", "TASK_COUNT": 12, "CHECKLIST_FILE": "..."}`
- [ ] T058 [US4] Complete slash command `templates/commands/brownfield.plan.md` with task summary display

**Checkpoint**: `/brownfield.plan` generates actionable plan with tasks mapped 1:1 to assessment issues

---

## Phase 7: User Story 5 - Execute Remediation with Checkpoints (Priority: P1)

**Goal**: Execute remediation tasks incrementally with checkpoint validation after each task

**Independent Test**: Run `/brownfield.remediate` on planned project, verify `execution-log.md` shows incremental progress and checkpoint results

### Implementation for User Story 5

- [ ] T059 [US5] Create `.specify/scripts/bash/brownfield-remediate.sh` with checkpoint-based execution
- [ ] T060 [US5] Load active project and parse plan.md to extract task list
- [ ] T061 [US5] Implement checkpoint validation function (runs pytest, checks git status, validates no regressions)
- [ ] T062 [US5] Implement task execution loop with checkpoint after each task
- [ ] T063 [US5] Check git working tree for uncommitted changes before starting (warn if dirty)
- [ ] T064 [US5] Create `001-*/execution-log.md` with timestamp headers
- [ ] T065 [US5] Log each task execution (start time, Claude prompt, completion status)
- [ ] T066 [US5] On checkpoint failure, log error details and stop execution immediately
- [ ] T067 [US5] Support `--auto-commit` flag to create git commits at checkpoints (default: false)
- [ ] T068 [US5] Track completed/failed task counts for progress reporting
- [ ] T069 [US5] Return JSON output: `{"COMPLETED_TASKS": 8, "FAILED_TASKS": 0, "STATUS": "success"}`
- [ ] T070 [US5] Complete slash command `templates/commands/brownfield.remediate.md` with checkpoint workflow

**Checkpoint**: `/brownfield.remediate` executes tasks safely with checkpoint validation and recovery support

---

## Phase 8: User Story 6 - Validate Quality Gates (Priority: P1)

**Goal**: Verify codebase meets quality thresholds (CCN < 10, coverage > 80%, zero critical vulns) before graduation

**Independent Test**: Run `/brownfield.validate` after remediation, verify `validation.md` generated with pass/fail status for each gate

### Implementation for User Story 6

- [ ] T071 [US6] Create `.specify/scripts/bash/brownfield-validate.sh` with gate validation workflow
- [ ] T072 [US6] Load quality gate configuration from `.specify/brownfield-config.yaml` (or use defaults)
- [ ] T073 [US6] Re-run Lizard, pytest, Bandit to get current metrics (same as assessment phase)
- [ ] T074 [US6] Save current metrics to `.brownfield/metrics/current.json`
- [ ] T075 [US6] Compare current metrics against quality gate thresholds
- [ ] T076 [US6] Generate gate-by-gate comparison (baseline → current → target)
- [ ] T077 [US6] Render brownfield-validation-template.md into `001-*/validation.md` with results
- [ ] T078 [US6] For failed gates, include detailed failure info (which files/functions failed, current vs. target values)
- [ ] T079 [US6] Calculate overall pass/fail status (all required gates must pass)
- [ ] T080 [US6] Return JSON output: `{"PASSED": true, "GATE_RESULTS": {"ccn": true, "coverage": true, "security": true}, "VALIDATION_FILE": "..."}`
- [ ] T081 [US6] Complete slash command `templates/commands/brownfield.validate.md` with results display

**Checkpoint**: `/brownfield.validate` provides automated certification of quality gate compliance

---

## Phase 9: User Story 7 - Graduate to Spec-Kit Feature Development (Priority: P1)

**Goal**: Certify codebase as AI-ready, update constitution, and enable transition to Spec-Kit feature workflow

**Independent Test**: Run `/brownfield.graduate` after validation passes, verify graduation document created and constitution updated

### Implementation for User Story 7

- [ ] T082 [US7] Create `.specify/scripts/bash/brownfield-graduate.sh` with graduation workflow
- [ ] T083 [US7] Verify all quality gates pass (read validation.md, check PASSED status)
- [ ] T084 [US7] Verify checklist completion (parse checklists/quality-gates.md, ensure 100% checked)
- [ ] T085 [US7] Create graduation snapshot in `.specify/memory/brownfield-graduation.md` with final metrics
- [ ] T086 [US7] Update constitution with certification statement and graduation timestamp
- [ ] T087 [US7] Mark project as "graduated" in brownfield-state.json
- [ ] T088 [US7] Include next step guidance (run `/speckit.specify` for feature development)
- [ ] T089 [US7] Return JSON output: `{"GRADUATED": true, "NEXT_STEP": "/speckit.specify", "GRADUATION_FILE": "..."}`
- [ ] T090 [US7] Complete slash command `templates/commands/brownfield.graduate.md` with celebration message

**Checkpoint**: `/brownfield.graduate` provides formal handoff from brownfield remediation to greenfield feature development

---

## Phase 10: Polish & Documentation

**Purpose**: Complete documentation, README, and repository metadata

- [ ] T091 [P] Create comprehensive `README.md` at repository root with installation instructions (reference quickstart.md)
- [ ] T092 [P] Add usage examples to README.md for each slash command with sample outputs
- [ ] T093 [P] Document configuration options in README.md (brownfield-config.yaml format)
- [ ] T094 [P] Add troubleshooting section to README.md (common errors, tool installation)
- [ ] T095 [P] Create `CONTRIBUTING.md` with development setup and PR guidelines
- [ ] T096 [P] Add inline documentation to all bash scripts (function headers with parameters and return values)
- [ ] T097 [P] Validate all JSON schema files against sample data (run jq validation)
- [ ] T098 [P] Test installation workflow end-to-end on clean Spec-Kit project
- [ ] T099 Create `.gitignore` with /tmp/, *.pyc, __pycache__, .venv patterns
- [ ] T100 Final review: Ensure no Spec-Kit file overwrites, test all slash commands work independently

**Checkpoint**: Brownfield-Kit repository is complete, documented, and ready for release

---

## Task Summary

**Total Tasks**: 100
**MVP Scope (P0 Stories)**: T001-T058 (58 tasks covering US1-US4)
**Post-MVP (P1 Stories)**: T059-T090 (32 tasks covering US5-US7)
**Polish**: T091-T100 (10 tasks)

### Task Count by User Story

- **Setup & Foundation**: 12 tasks (T001-T012)
- **US1 - Install**: 13 tasks (T013-T025)
- **US2 - Ingest**: 8 tasks (T026-T033)
- **US3 - Assess**: 14 tasks (T034-T047)
- **US4 - Plan**: 11 tasks (T048-T058)
- **US5 - Remediate**: 12 tasks (T059-T070)
- **US6 - Validate**: 11 tasks (T071-T081)
- **US7 - Graduate**: 9 tasks (T082-T090)
- **Polish**: 10 tasks (T091-T100)

### Parallel Execution Opportunities

**Phase 1 (Setup)**: T002, T003, T004, T005 can run in parallel (4 tasks)

**Phase 2 (Foundation)**: T010, T011, T012 can run in parallel (3 tasks)

**Phase 3 (US1 - Install)**:
- T013, T014 in parallel (2 tasks)
- T020-T025 in parallel (6 tasks - all slash command stubs)

**Phase 4 (US2 - Ingest)**: No parallelization (sequential workflow)

**Phase 5 (US3 - Assess)**: No parallelization (sequential tool execution required)

**Phase 6 (US4 - Plan)**: No parallelization (sequential analysis of assessment data)

**Phase 10 (Polish)**: T091-T098 can run in parallel (8 tasks)

**Total Parallel Opportunities**: 23 tasks can be executed concurrently

---

## Dependencies

### Story Completion Order

```
Phase 1 (Setup) → Phase 2 (Foundation)
                     ↓
        Phase 3 (US1 - Install) 🎯 MVP FOUNDATION
                     ↓
        Phase 4 (US2 - Ingest) 🎯 MVP
                     ↓
        Phase 5 (US3 - Assess) 🎯 MVP
                     ↓
        Phase 6 (US4 - Plan) 🎯 MVP
                     ↓
        [Phase 7 (US5 - Remediate) (Post-MVP)]
                     ↓
        [Phase 8 (US6 - Validate) (Post-MVP)]
                     ↓
        [Phase 9 (US7 - Graduate) (Post-MVP)]
                     ↓
        Phase 10 (Polish)
```

### Critical Path

1. Setup (T001-T005) → Foundation (T006-T012)
2. Install CLI (T013-T019) → Slash commands (T020-T025)
3. Ingest script (T026-T032) → Complete ingest command (T033)
4. Assess script (T034-T046) → Complete assess command (T047)
5. Plan script (T048-T057) → Complete plan command (T058)

**MVP Completion Point**: After T058, users can install, analyze, assess, and plan remediation

### Post-MVP Path

6. Remediate script (T059-T069) → Complete remediate command (T070)
7. Validate script (T071-T080) → Complete validate command (T081)
8. Graduate script (T082-T089) → Complete graduate command (T090)
9. Documentation polish (T091-T100)

---

## Implementation Strategy

### MVP-First Approach (Recommended)

**Week 1-2: MVP Foundation**
- Complete Phase 1 (Setup) and Phase 2 (Foundation): T001-T012
- Deliverable: Bash utilities and templates ready

**Week 2-3: MVP User Stories**
- Complete US1 (Install): T013-T025
- Complete US2 (Ingest): T026-T033
- Complete US3 (Assess): T034-T047
- Complete US4 (Plan): T048-T058
- Deliverable: Working `brownfield init`, `/brownfield.ingest`, `/brownfield.assess`, `/brownfield.plan`

**Week 4: MVP Testing & Polish**
- Test MVP on real brownfield project
- Fix bugs, improve error handling
- Write basic README
- **Deliverable: Usable tool for manual remediation with generated plans**

### Post-MVP Iterations

**Iteration 1: Automation** (US5 - Remediate)
- T059-T070
- Deliverable: `/brownfield.remediate` for automated execution

**Iteration 2: Validation** (US6-US7)
- T071-T090
- Deliverable: `/brownfield.validate` and `/brownfield.graduate`

**Iteration 3: Documentation**
- T091-T100
- Deliverable: Production-ready documentation

---

## Validation Checklist

After completing MVP (T001-T058), verify:
- [ ] `brownfield init` runs without errors in Spec-Kit project
- [ ] No Spec-Kit files overwritten during installation
- [ ] All 6 slash commands appear in `.claude/commands/`
- [ ] `/brownfield.ingest` generates codebase-analysis.md
- [ ] `/brownfield.assess` creates numbered project directory with assessment.md
- [ ] Assessment.md contains concrete metrics (CCN values, coverage %, vuln counts)
- [ ] `/brownfield.plan` generates actionable plan with specific file:line references
- [ ] Plan.md tasks map 1:1 to assessment issues
- [ ] Checklist file contains measurable quality gate criteria
- [ ] All bash scripts return valid JSON output
- [ ] Constitution.md updated without data loss
- [ ] Multiple brownfield projects can coexist (001-, 002-, etc.)

After completing full implementation (T001-T100), verify:
- [ ] `/brownfield.remediate` executes tasks with checkpoints
- [ ] Checkpoint failures stop execution and log details
- [ ] `/brownfield.validate` re-runs quality tools and compares results
- [ ] Validation.md shows pass/fail status for each gate
- [ ] `/brownfield.graduate` requires 100% checklist completion
- [ ] Graduation updates constitution with certification
- [ ] README.md provides clear installation and usage instructions
- [ ] All JSON schemas validate against sample data
- [ ] Tool works on Python 3.11+ codebases
- [ ] Integration with Spec-Kit workflow confirmed (graduated projects work with `/speckit.specify`)
