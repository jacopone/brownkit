# CLI Commands Contract

**Feature**: BrownKit Implementation
**Created**: 2025-10-12
**Purpose**: Define input/output contracts for all BrownKit CLI commands

## Command Overview

| Command | Phase | Description |
|---------|-------|-------------|
| `brownfield assess` | Assessment | Run codebase analysis and generate baseline metrics |
| `brownfield structure` | Structure | Fix directory organization and import paths |
| `brownfield testing` | Testing | Bootstrap test framework and generate tests |
| `brownfield quality` | Quality | Install linters, formatters, and pre-commit hooks |
| `brownfield validate` | Validation | Check all 7 readiness gates |
| `brownfield graduate` | Graduation | Generate Speckit constitution and archive artifacts |
| `brownfield resume` | Any | Resume interrupted phase from checkpoint |
| `brownfield status` | Any | Show current workflow state and progress |

## Global Options

All commands support these global options:

```bash
--project-root PATH    # Override project root directory (default: current directory)
--verbose             # Enable verbose logging
--quiet               # Suppress non-critical output
--help                # Show command help
```

## Command Specifications

---

### `brownfield assess`

**Purpose**: Analyze codebase to detect language, measure baseline metrics, and identify tech debt.

**Usage**:
```bash
brownfield assess [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--quick` / `--full` | Flag | `--quick` | Analysis mode (quick: sampling, full: comprehensive) |
| `--output PATH` | Path | `.specify/memory/assessment-report.md` | Output path for assessment report |
| `--force` | Flag | False | Force re-assessment even if report exists |
| `--language LANG` | Choice | Auto-detect | Override language detection (python, javascript, rust, go) |

**Inputs**:
- Current working directory must be project root
- Project should be git repository (warning if not)
- Optional: Configuration file `.brownfield.toml` for custom settings

**Outputs**:

**Success (Exit Code 0)**:
```
🔍 Assessing codebase...

Language Detection:
  Primary: Python (confidence: HIGH)
  Version: 3.9.16
  Framework: Flask 2.3.0

Baseline Metrics:
  Test Coverage: 0.0%
  Avg Complexity: 15.2
  Max Complexity: 34 (in utils/parser.py:process_data)
  Critical Vulnerabilities: 2
  High Vulnerabilities: 5
  Total LOC: 8,543
  Test LOC: 0

Tech Debt Categories:
  🔴 CRITICAL - Testing: No test framework, 0% coverage
  🟠 HIGH - Structural: Source files in root directory
  🟠 HIGH - Security: 2 critical vulnerabilities (CVE-2023-1234, CVE-2023-5678)
  🟡 MEDIUM - Documentation: 45% of public APIs lack docstrings

Analysis Mode: quick (completed in 2m 15s)
Confidence: HIGH

Assessment complete! Report saved to:
  .specify/memory/assessment-report.md

Next steps:
  Run: brownfield structure
```

**Files Created**:
- `.specify/memory/assessment-report.md` (detailed Markdown report)
- `.specify/memory/brownfield-state.json` (machine-readable state)
- `.specify/memory/brownfield-decisions.md` (decision log, initially empty)

**Error Cases**:

| Exit Code | Scenario | Output |
|-----------|----------|--------|
| 1 | Not a directory | `Error: /path/to/project is not a directory` |
| 2 | Language detection failed | `Error: Could not detect primary language. Use --language to specify.` |
| 3 | Missing required tools | `Warning: Missing tools (pytest, black). Some metrics unavailable. Run 'brownfield install-tools' to fix.` (non-fatal) |
| 4 | Analysis timeout | `Error: Analysis timed out after 10 minutes. Try --quick mode.` |

**Preconditions**:
- None (always first command)

**Postconditions**:
- `brownfield-state.json` created with `current_phase: "structure"`
- Assessment report available for inspection
- Baseline metrics stored for later comparison

---

### `brownfield structure`

**Purpose**: Generate refactoring plan for reorganizing project directories to follow ecosystem conventions. **Default mode generates plan for manual execution with IDE tools; use --verify to validate after manual refactoring.**

**Usage**:
```bash
brownfield structure [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--verify` | Flag | False | Verify structure after manual refactoring (instead of generating plan) |
| `--output PATH` | Path | `.specify/memory/structure-plan.md` | Output path for refactoring plan |
| `--shell-script` | Flag | True | Generate shell script for file moves |
| `--format FORMAT` | Choice | markdown | Plan output format (markdown, json) |

**Inputs**:
- Assessment must be complete (checks `brownfield-state.json`)
- For --verify mode: Manual refactoring should be complete

**Outputs**:

**Default Mode - Plan Generation (Exit Code 0)**:
```
🏗️  Analyzing project structure...

Language Detection:
  Primary: Python (confidence: HIGH)
  Standard: src/, tests/, docs/ with PEP 518 conventions

Current Structure Issues:
  ❌ 12 source files in root directory
  ❌ Missing src/ package directory
  ❌ Missing tests/ directory
  ⚠️  No pyproject.toml configuration

Generated Refactoring Plan:
  📄 Detailed plan: .specify/memory/structure-plan.md
  🔧 Shell script: .specify/memory/structure-moves.sh
  📋 12 files to reorganize

═══════════════════════════════════════════════════════════════
⚠️  IMPORTANT: Use IDE Refactoring Tools for Import Updates! ⚠️
═══════════════════════════════════════════════════════════════

BrownKit generates a plan but does NOT move files automatically
to avoid risks of breaking imports with naive string replacement.

Recommended Workflow:
  1. Review plan: cat .specify/memory/structure-plan.md
  2. Use IDE refactoring (PyCharm "Move Module", VSCode drag+drop)
  3. IDE will automatically update all imports correctly
  4. Verify: brownfield structure --verify

Alternative (Advanced):
  - Run shell script: bash .specify/memory/structure-moves.sh
  - Manually fix imports (or use find-replace carefully)
  - Verify: brownfield structure --verify

Plan saved to: .specify/memory/structure-plan.md

Next steps:
  1. Open .specify/memory/structure-plan.md for detailed instructions
  2. Use IDE refactoring tools to move files
  3. Run: brownfield structure --verify
```

**Generated Plan File (.specify/memory/structure-plan.md)**:
```markdown
# Structure Refactoring Plan

Generated: 2025-10-12 19:30:00
Language: Python
Project: myproject

## Overview
Moving 12 Python files from root to standard src/myproject/ structure.

## Step 1: Create Directories
- [ ] Create `src/myproject/`
- [ ] Create `tests/`
- [ ] Create `docs/`

## Step 2: Move Files (Use IDE Refactoring!)

### ⚠️ IMPORTANT: Use IDE Refactoring for Correct Import Updates

**PyCharm Users:**
1. Right-click file → Refactor → Move File
2. Destination: `src/myproject/`
3. ✓ Enable "Search for references"
4. Review and apply changes

**VSCode Users:**
1. Install "Python Refactor" extension if needed
2. Drag file to `src/myproject/` in explorer
3. Confirm "Update imports" prompt
4. Review changes

**Vim/Emacs/Manual:**
- Use shell script below for moves
- Update imports using find-replace or LSP tools

### Files to Move:
- [ ] main.py → src/myproject/main.py (imported in 3 files)
- [ ] utils.py → src/myproject/utils.py (imported in 5 files)
- [ ] config.py → src/myproject/config.py (imported in 2 files)
... (9 more files)

## Step 3: Configuration Files
- [ ] Create pyproject.toml (if missing)
- [ ] Create src/myproject/__init__.py
- [ ] Update .gitignore

## Step 4: Verify
- [ ] Run: `brownfield structure --verify`
- [ ] All checks pass: structure, build, imports

## Alternative: Shell Script Only
```bash
# WARNING: This only moves files, does NOT update imports!
bash .specify/memory/structure-moves.sh
# You MUST fix imports manually afterwards
```
```

**Verify Mode (Exit Code 0 - All Checks Pass)**:
```
✅ Verifying project structure...

Checking directory structure...
  ✓ src/myproject/ exists
  ✓ tests/ exists
  ✓ docs/ exists
  ✓ No source files in root directory
  ✓ Configuration files present

Checking build integrity...
  ✓ Running build verification...
  ✓ All modules compile successfully
  ✓ No syntax errors

Checking import integrity...
  ✓ All imports resolve correctly
  ✓ No circular dependencies detected
  ✓ No missing module references

═══════════════════════════════════════════════════════════════
✅ STRUCTURE VERIFICATION PASSED ✅
═══════════════════════════════════════════════════════════════

Project structure now follows Python PEP 518 conventions!

Structure compliance: ✓ PASS
Build verification: ✓ PASS
Import integrity: ✓ PASS

State updated to Phase: TESTING

Next steps:
  Run: brownfield testing
```

**Verify Mode (Exit Code 1 - Failures)**:
```
❌ Verifying project structure...

Checking directory structure...
  ❌ Source files still in root: main.py, utils.py
  ⚠️  Expected location: src/myproject/

Checking build integrity...
  ❌ Build failed: ImportError: No module named 'config'
  💡 Suggestion: Imports may not have been updated correctly

Checking import integrity...
  ❌ Found 3 broken imports:
     - main.py:5: from utils import helper (should be: from myproject.utils import helper)
     - test_main.py:2: import config (should be: from myproject import config)
     - app.py:10: from config import settings

═══════════════════════════════════════════════════════════════
❌ STRUCTURE VERIFICATION FAILED ❌
═══════════════════════════════════════════════════════════════

Issues found:
  ❌ 2 source files not moved
  ❌ Build verification failed
  ❌ 3 broken import statements

Recommended actions:
  1. Complete file moves using IDE refactoring
  2. Use IDE's "Move Module" to update imports automatically
  3. Fix broken imports listed above
  4. Re-run: brownfield structure --verify
```

**Files Created (Plan Mode)**:
- `.specify/memory/structure-plan.md` (detailed refactoring guide)
- `.specify/memory/structure-moves.sh` (shell script for file moves only)

**Files Created (Verify Mode)**:
- `.specify/memory/structure-verification-report.md` (detailed check results)
- `.specify/memory/brownfield-state.json` updated (if verification passes)

**Error Cases**:

| Exit Code | Scenario | Output |
|-----------|----------|--------|
| 1 | Assessment not run | `Error: Assessment required. Run 'brownfield assess' first.` |
| 1 | Verification failed | (See verify mode failure output above) |
| 2 | Cannot write plan | `Error: Cannot write to .specify/memory/. Check permissions.` |

**Preconditions**:
- `brownfield assess` completed
- For verify mode: Manual refactoring should be attempted

**Postconditions (Plan Mode)**:
- Refactoring plan and shell script generated
- User has clear instructions for IDE refactoring

**Postconditions (Verify Mode - Success)**:
- Structure compliance verified
- Build passes with no errors
- Import integrity confirmed
- State updated to `current_phase: "testing"`

---

### `brownfield testing`

**Purpose**: Add test framework, generate initial tests, and achieve 60% coverage on core modules.

**Usage**:
```bash
brownfield testing [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--coverage-target FLOAT` | Float | 0.6 | Target coverage (0.0-1.0) |
| `--core-modules PATH...` | Multiple | Auto-detect | Specify core business logic modules |
| `--skip-framework-install` | Flag | False | Skip test framework installation (assume already installed) |
| `--test-type TYPE` | Choice | contract | Test type to generate (contract, smoke, integration) |

**Inputs**:
- Structure phase complete
- Test framework may or may not be installed

**Outputs**:

**Success (Exit Code 0)**:
```
🧪 Bootstrapping test infrastructure...

Phase 1: Test Framework Setup
  ✓ Detected testing needs: pytest, pytest-cov, pytest-mock
  ✓ Added dependencies to pyproject.toml
  ✓ Created tests/ directory structure
  ✓ Generated tests/conftest.py with fixtures
  ✓ Committed: xyz789a [brownfield] testing: Add pytest framework

Phase 2: Core Module Identification
  Detected core business logic modules:
    • src/myproject/api.py (347 LOC)
    • src/myproject/processor.py (892 LOC)
    • src/myproject/validator.py (234 LOC)

  Is this correct? [Y/n]: y

Phase 3: Test Generation
  [1/3] Generating contract tests for api.py...
    ✓ Created tests/contract/test_api.py (12 tests)
    ✓ Committed: abc123b [brownfield] testing: Add contract tests for API

  [2/3] Generating contract tests for processor.py...
    ✓ Created tests/contract/test_processor.py (8 tests)
    ✓ Committed: def456c [brownfield] testing: Add contract tests for processor

  [3/3] Generating smoke tests...
    ✓ Created tests/test_smoke.py (5 tests)
    ✓ Committed: ghi789d [brownfield] testing: Add smoke tests

Phase 4: Coverage Verification
  Running tests...
  ✓ 25 tests passed, 0 failed

  Coverage Report:
  Module                        Coverage
  ─────────────────────────────────────
  src/myproject/api.py          72%  ✓
  src/myproject/processor.py    65%  ✓
  src/myproject/validator.py    58%  ⚠️
  ─────────────────────────────────────
  Overall Core Coverage:        65%  ✓

  Target: 60% ✓ ACHIEVED

Testing infrastructure complete!
  ✓ Test framework installed
  ✓ 25 tests generated
  ✓ 65% coverage achieved (target: 60%)
  🔀 4 git commits created

Next steps:
  Run: brownfield quality
```

**Files Created**:
- `tests/` directory structure
- `tests/conftest.py` (pytest fixtures)
- `tests/contract/test_*.py` (contract tests for public APIs)
- `tests/test_smoke.py` (basic smoke tests)
- `pytest.ini` or `pyproject.toml` (pytest configuration)
- `.coveragerc` (coverage configuration)

**Error Cases**:

| Exit Code | Scenario | Output |
|-----------|----------|--------|
| 1 | Structure phase incomplete | `Error: Structure phase required. Run 'brownfield structure' first.` |
| 2 | Test framework install failed | `Error: Failed to install pytest. Install manually and use --skip-framework-install.` |
| 3 | Coverage target not met | `Warning: Only achieved 45% coverage (target: 60%). Manual test writing needed.` (non-fatal) |
| 4 | No core modules identified | `Error: Could not identify core business logic. Use --core-modules to specify.` |

**Preconditions**:
- `brownfield structure` completed
- Python/npm/cargo available

**Postconditions**:
- Test framework installed and configured
- At least 60% coverage on core modules
- All generated tests pass
- State updated to `current_phase: "quality"`

---

### `brownfield quality`

**Purpose**: Install linters, formatters, complexity analysis, and pre-commit hooks.

**Usage**:
```bash
brownfield quality [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--skip-linter` | Flag | False | Skip linter installation |
| `--skip-formatter` | Flag | False | Skip formatter installation |
| `--skip-hooks` | Flag | False | Skip pre-commit hook installation |
| `--complexity-threshold INT` | Integer | 10 | Maximum cyclomatic complexity |
| `--fix-auto` | Flag | False | Automatically fix linting/formatting issues |

**Inputs**:
- Testing phase complete
- Git repository with commits

**Outputs**:

**Success (Exit Code 0)**:
```
⚙️  Installing quality gates...

Phase 1: Linter Setup
  ✓ Added pylint to dev dependencies
  ✓ Created .pylintrc with project-specific rules
  ✓ Running initial lint check...
    ⚠️  Found 23 linting issues

  Fix automatically? [y/N]: y
  ✓ Fixed 18 issues (5 require manual review)
  ✓ Committed: abc123e [brownfield] quality: Add pylint configuration

Phase 2: Formatter Setup
  ✓ Added black to dev dependencies
  ✓ Created pyproject.toml formatting config
  ✓ Running formatter...
    ✓ Formatted 12 files
  ✓ Committed: def456f [brownfield] quality: Apply black formatting

Phase 3: Complexity Analysis
  Running lizard complexity check...

  Functions exceeding complexity threshold (10):
    • process_data() in processor.py: CCN=15
    • validate_input() in validator.py: CCN=12
    • parse_config() in config.py: CCN=11

  These functions need refactoring or justification.
  Document justification? [y/N]: y

  ✓ Created complexity-justification.md
  ✓ Committed: ghi789g [brownfield] quality: Document complexity exceptions

Phase 4: Security Scanning
  Running bandit security scanner...
  ✓ No new vulnerabilities introduced
  ⚠️  2 existing critical vulnerabilities from assessment:
      - CVE-2023-1234: flask<2.3.0 (Update available)
      - CVE-2023-5678: requests<2.28.0 (Update available)

  Apply security updates? [Y/n]: y
  ✓ Updated vulnerable dependencies
  ✓ Re-ran tests: all passing
  ✓ Committed: jkl012h [brownfield] quality: Fix security vulnerabilities

Phase 5: Pre-commit Hooks
  ✓ Installed pre-commit framework
  ✓ Created .pre-commit-config.yaml
  ✓ Installed git hooks
  ✓ Tested hooks: all passing
  ✓ Committed: mno345i [brownfield] quality: Add pre-commit hooks

Quality gates installed!
  ✓ Linter: pylint (18 issues auto-fixed, 5 require manual review)
  ✓ Formatter: black (12 files formatted)
  ✓ Complexity: 3 exceptions documented
  ✓ Security: 2 vulnerabilities fixed
  ✓ Pre-commit hooks: active
  🔀 5 git commits created

Next steps:
  Review manual issues in brownfield-decisions.md
  Run: brownfield validate
```

**Files Created**:
- `.pylintrc` / `.eslintrc.json` (linter config)
- `pyproject.toml` / `.prettierrc` (formatter config)
- `.pre-commit-config.yaml` (pre-commit hooks)
- `complexity-justification.md` (documented exceptions)

**Error Cases**:

| Exit Code | Scenario | Output |
|-----------|----------|--------|
| 1 | Testing phase incomplete | `Error: Testing phase required. Run 'brownfield testing' first.` |
| 2 | Pre-commit install failed | `Error: Failed to install pre-commit. Install manually: pip install pre-commit` |
| 3 | Security fixes break tests | `Error: Security updates caused test failures. Manual resolution needed.` |

**Preconditions**:
- `brownfield testing` completed
- Git repository with commits

**Postconditions**:
- Linters and formatters configured
- Pre-commit hooks installed and active
- Complexity documented or reduced
- Critical security vulnerabilities fixed
- State updated to `current_phase: "validation"`

---

### `brownfield validate`

**Purpose**: Check all 7 readiness gates to determine graduation eligibility.

**Usage**:
```bash
brownfield validate [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--gate NAME` | String | All | Validate specific gate only |
| `--fail-fast` | Flag | False | Stop on first gate failure |
| `--report PATH` | Path | stdout | Output path for validation report |

**Inputs**:
- Quality phase complete
- All previous phases successful

**Outputs**:

**Success (Exit Code 0)**:
```
✅ Validating readiness gates...

Gate 1: Test Coverage
  Threshold: ≥60%
  Current: 65%
  Status: ✅ PASS

Gate 2: Cyclomatic Complexity
  Threshold: <10 (or documented)
  Current: Max 15 (3 exceptions documented)
  Status: ✅ PASS

Gate 3: Directory Structure
  Threshold: Follows ecosystem conventions
  Current: Python PEP 518 structure
  Status: ✅ PASS

Gate 4: Build Status
  Threshold: Clean build (<10 warnings)
  Current: 0 errors, 2 warnings
  Status: ✅ PASS

Gate 5: API Documentation
  Threshold: ≥80% of public APIs documented
  Current: 92%
  Status: ✅ PASS

Gate 6: Security
  Threshold: 0 critical vulnerabilities
  Current: 0 critical, 3 medium
  Status: ✅ PASS

Gate 7: Git Hygiene
  Threshold: No secrets, no large binaries
  Current: Clean
  Status: ✅ PASS

═══════════════════════════════════════
Result: ALL GATES PASSED ✅
═══════════════════════════════════════

Metrics Improvement Summary:
  Test Coverage:    0% → 65% (+65pp)
  Avg Complexity:   15.2 → 8.4 (-6.8)
  Critical Vulns:   2 → 0 (-2)
  Build Status:     Unknown → Passing

Your project is ready for graduation! 🎓

Next steps:
  Run: brownfield graduate
```

**Failure Example (Exit Code 1)**:
```
❌ Validating readiness gates...

Gate 1: Test Coverage
  Threshold: ≥60%
  Current: 48%
  Status: ❌ FAIL
  Remediation: Run 'brownfield testing' to generate more tests

Gate 2: Cyclomatic Complexity
  Threshold: <10 (or documented)
  Current: Max 15 (undocumented)
  Status: ❌ FAIL
  Remediation: Document exceptions in complexity-justification.md

... (remaining gates)

═══════════════════════════════════════
Result: 2 GATES FAILED ❌
═══════════════════════════════════════

Recommended actions:
  1. Return to testing phase: brownfield testing
  2. Document complexity exceptions
  3. Re-run validation: brownfield validate

Cannot graduate until all gates pass.
```

**Error Cases**:

| Exit Code | Scenario | Output |
|-----------|----------|--------|
| 1 | One or more gates failed | (See failure example above) |
| 2 | Quality phase incomplete | `Error: Quality phase required. Run 'brownfield quality' first.` |
| 3 | Gate verification command failed | `Error: Could not run 'pytest --cov'. Ensure test framework installed.` |

**Preconditions**:
- `brownfield quality` completed

**Postconditions**:
- Validation results stored in state
- If passed: State updated to allow graduation
- If failed: Recommendations provided for remediation

---

### `brownfield graduate`

**Purpose**: Generate Speckit constitution, archive brownfield artifacts, create graduation report.

**Usage**:
```bash
brownfield graduate [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--force` | Flag | False | Graduate even if validation incomplete (not recommended) |
| `--archive-path PATH` | Path | `.specify/memory/brownfield-archive/` | Custom archive location |

**Inputs**:
- All 7 readiness gates passed
- Validation complete

**Outputs**:

**Success (Exit Code 0)**:
```
🎓 Graduating project to Speckit...

Phase 1: Validation Check
  ✓ All 7 readiness gates passed
  ✓ Metrics improvement verified

Phase 2: Speckit Constitution Generation
  Analyzing project architecture...
  ✓ Detected: Flask web application
  ✓ Tech stack: Python 3.9, pytest, SQLAlchemy

  Generated constitution principles:
    • TESTING_FIRST: All features require tests before implementation
    • API_CONTRACTS: REST APIs must have OpenAPI specs
    • DATABASE_MIGRATIONS: Schema changes via Alembic migrations
    • SECURITY_REVIEW: Authentication/authorization changes require review

  ✓ Created .specify/memory/constitution.md
  ✓ Committed: abc123j [brownfield] graduation: Add Speckit constitution

Phase 3: Template Generation
  ✓ Created .specify/templates/spec-template.md
  ✓ Created .specify/templates/plan-template.md
  ✓ Created .specify/templates/tasks-template.md
  ✓ Committed: def456k [brownfield] graduation: Add Speckit templates

Phase 4: Artifact Archival
  Archiving brownfield artifacts...
  ✓ Moved assessment-report.md → brownfield-archive/
  ✓ Moved brownfield-decisions.md → brownfield-archive/
  ✓ Moved brownfield-checkpoint.json → brownfield-archive/
  ✓ Updated brownfield-state.json (graduated: true)

Phase 5: Graduation Report
  ✓ Generated brownfield-graduation-report.md

  Report highlights:
    • Baseline coverage: 0% → 65%
    • Complexity reduced: 15.2 → 8.4
    • Security issues fixed: 2 critical
    • Structural changes: 47 commits
    • Time invested: 2h 15m

═══════════════════════════════════════
🎉 GRADUATION COMPLETE! 🎉
═══════════════════════════════════════

Your project is now Speckit-ready!

Generated artifacts:
  📜 Constitution: .specify/memory/constitution.md
  📋 Templates: .specify/templates/
  📊 Graduation Report: brownfield-graduation-report.md
  📦 Archived: .specify/memory/brownfield-archive/

Next steps:
  1. Review constitution: cat .specify/memory/constitution.md
  2. Start spec-driven development: /speckit.specify "your feature"
  3. Share graduation report with team

Thank you for using BrownKit! 🚀
```

**Files Created**:
- `.specify/memory/constitution.md` (Speckit constitution)
- `.specify/templates/` (spec/plan/tasks templates)
- `brownfield-graduation-report.md` (graduation summary)

**Files Archived**:
- `.specify/memory/brownfield-archive/assessment-report.md`
- `.specify/memory/brownfield-archive/brownfield-decisions.md`
- `.specify/memory/brownfield-archive/brownfield-checkpoint.json`

**Error Cases**:

| Exit Code | Scenario | Output |
|-----------|----------|--------|
| 1 | Validation incomplete | `Error: Validation required. Run 'brownfield validate' first.` |
| 2 | Gates not passing | `Error: Cannot graduate with failed gates. Fix issues and re-validate.` |
| 3 | File permissions | `Error: Cannot write to .specify/. Check permissions.` |

**Preconditions**:
- `brownfield validate` passed all gates

**Postconditions**:
- Speckit constitution generated
- Templates configured for project
- Brownfield artifacts archived
- Graduation report available
- State updated to `graduated: true`

---

### `brownfield resume`

**Purpose**: Resume interrupted phase from last checkpoint.

**Usage**:
```bash
brownfield resume [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--restart` | Flag | False | Restart phase from beginning (ignore checkpoint) |

**Inputs**:
- Checkpoint file exists (`.specify/memory/brownfield-checkpoint.json`)
- Interruption detected

**Outputs**:

**Success (Exit Code 0)**:
```
🔄 Resuming interrupted phase...

Detected interrupted phase: Structure
Started: 2025-10-12 14:30:00
Last checkpoint: 2025-10-12 14:45:00
Progress: 8/12 tasks completed (66.7%)

Completed tasks:
  ✓ create_src_dir
  ✓ move_main_py
  ✓ move_utils_py
  ... (5 more)

Pending tasks:
  ⏳ update_imports_config
  ⏳ create_pyproject_toml
  ⏳ create_tests_directory
  ⏳ verify_build

Resume from checkpoint? [Y/n]: y

Resuming...

[9/12] Updating imports in config.py...
  ✓ Imports updated
  ✓ Build verified
  ✓ Committed: xyz789l [brownfield] structure: Update imports in config.py

... (continuing)
```

**No Checkpoint (Exit Code 0)**:
```
ℹ️  No interrupted phase detected.

Current state:
  Phase: Quality
  Last activity: 2025-10-12 15:30:00
  Status: In progress

No action needed. Continue with current phase.
```

**Error Cases**:

| Exit Code | Scenario | Output |
|-----------|----------|--------|
| 1 | Corrupted checkpoint | `Error: Checkpoint file corrupted. Use --restart to begin phase again.` |
| 2 | User declined resume | `Cancelled by user. Use --restart to begin phase again.` (Exit 0, not error) |

---

### `brownfield status`

**Purpose**: Show current workflow state, progress, and metrics.

**Usage**:
```bash
brownfield status [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--json` | Flag | False | Output as JSON for scripting |
| `--verbose` | Flag | False | Show detailed metrics and history |

**Outputs**:

**Success (Exit Code 0)**:
```
📊 BrownKit Status

Project: /home/user/my-project
Current Phase: Testing
Status: In Progress

Progress:
  ✅ Assessment      (2025-10-12 14:00)
  ✅ Structure       (2025-10-12 15:00)
  ⏳ Testing         (started 2025-10-12 15:30)
  ⬜ Quality
  ⬜ Validation
  ⬜ Graduation

Current Metrics:
  Test Coverage:     45% (target: 60%)
  Avg Complexity:    10.2 (target: <10)
  Critical Vulns:    1 (target: 0)

Baseline Metrics:
  Test Coverage:     0%
  Avg Complexity:    15.2
  Critical Vulns:    2

Improvement:
  Test Coverage:     +45pp
  Avg Complexity:    -5.0
  Critical Vulns:    -1

Next steps:
  Continue testing phase: brownfield testing
  Or check detailed report: cat .specify/memory/brownfield-state.json
```

**JSON Output (`--json`)**:
```json
{
  "project_root": "/home/user/my-project",
  "current_phase": "testing",
  "status": "in_progress",
  "phases_complete": ["assessment", "structure"],
  "current_metrics": {
    "test_coverage": 0.45,
    "complexity_avg": 10.2,
    "critical_vulnerabilities": 1
  },
  "baseline_metrics": {
    "test_coverage": 0.0,
    "complexity_avg": 15.2,
    "critical_vulnerabilities": 2
  },
  "timestamps": {
    "assessment": "2025-10-12T14:00:00Z",
    "structure_complete": "2025-10-12T15:00:00Z",
    "testing_start": "2025-10-12T15:30:00Z"
  }
}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error (missing precondition, validation failure) |
| 2 | Configuration error (bad options, invalid state) |
| 3 | Tool error (missing dependencies, external command failed) |
| 4 | User cancellation (explicit cancellation via prompt) |
| 130 | Interrupted (Ctrl+C) - checkpoint saved |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BROWNFIELD_PROJECT_ROOT` | Override project root | Current directory |
| `BROWNFIELD_VERBOSE` | Enable verbose logging | False |
| `BROWNFIELD_AUTO_APPROVE` | Auto-approve all prompts (CI mode) | False |
| `BROWNFIELD_CHECKPOINT_INTERVAL` | Seconds between checkpoints | 60 |

## Shell Completion

Install shell completion for better UX:

```bash
# Bash
brownfield --install-completion bash

# Zsh
brownfield --install-completion zsh

# Fish
brownfield --install-completion fish
```
