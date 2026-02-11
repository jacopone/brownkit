---
status: active
created: 2025-10-20
updated: 2025-10-20
type: architecture
lifecycle: persistent
---

# Data Model: Brownfield Kit

This document defines the core data entities and their relationships for the bash-based Brownfield Kit implementation.

## Overview

The Brownfield Kit uses JSON files for state persistence and data exchange between bash scripts. All entities are designed to be serializable to JSON and human-readable.

## Core Entities

### BrownfieldProject

Represents a project undergoing brownfield transformation.

```bash
# File: .brownfield/project.json
{
  "schema_version": "1.0",
  "project_name": "legacy-api",
  "project_root": "/home/user/projects/legacy-api",
  "detected_language": "python",
  "detected_framework": "flask",
  "created_at": "2025-10-20T14:00:00Z",
  "updated_at": "2025-10-20T15:30:00Z",
  "current_phase": "testing",
  "git_info": {
    "is_repo": true,
    "current_branch": "brownfield-transition",
    "has_uncommitted": false,
    "remote_url": "https://github.com/org/legacy-api"
  }
}
```

**Fields**:
- `schema_version` (string): Data model version for migration support
- `project_name` (string): Project directory name
- `project_root` (string): Absolute path to project
- `detected_language` (string): Primary language (python, javascript, rust, go)
- `detected_framework` (string|null): Framework if detected (flask, express, actix, gin)
- `created_at` (ISO 8601): When assessment started
- `updated_at` (ISO 8601): Last modification timestamp
- `current_phase` (string): Current workflow phase (assessment, structure, testing, quality, validation, graduated)
- `git_info` (object): Git repository metadata

### Metrics

Captures quantitative measurements of code quality.

```bash
# File: .brownfield/metrics/baseline.json
# File: .brownfield/metrics/current.json
{
  "schema_version": "1.0",
  "timestamp": "2025-10-20T14:00:00Z",
  "phase": "baseline",
  "confidence": "high",
  "codebase": {
    "total_files": 156,
    "total_lines": 12450,
    "source_lines": 9823,
    "comment_lines": 1205,
    "blank_lines": 1422,
    "languages": {
      "python": 9823,
      "javascript": 0,
      "rust": 0
    }
  },
  "complexity": {
    "avg_cyclomatic": 8.5,
    "max_cyclomatic": 45,
    "functions_over_threshold": 12,
    "threshold": 10,
    "files_analyzed": 156
  },
  "testing": {
    "has_test_framework": false,
    "test_files": 0,
    "total_tests": 0,
    "coverage_percent": 0.0,
    "coverage_available": false
  },
  "security": {
    "vulnerabilities": {
      "high": 3,
      "medium": 8,
      "low": 15
    },
    "total_issues": 26,
    "tool": "bandit",
    "scan_completed": true
  },
  "structure": {
    "has_src_dir": false,
    "has_tests_dir": false,
    "has_docs_dir": false,
    "files_in_root": 12,
    "max_depth": 4,
    "follows_conventions": false
  }
}
```

**Sections**:
- `codebase`: Lines of code and file counts
- `complexity`: Cyclomatic complexity metrics
- `testing`: Test coverage and framework detection
- `security`: Vulnerability scan results
- `structure`: Directory organization metrics

**Files**:
- `baseline.json`: Initial assessment metrics (never modified)
- `current.json`: Latest metrics (updated after each phase)

### QualityGate

Defines pass/fail criteria for graduation.

```bash
# File: .brownfield/quality-gates.json
{
  "schema_version": "1.0",
  "gates": [
    {
      "id": "test_coverage",
      "name": "Test Coverage",
      "description": "Minimum test coverage percentage",
      "metric_path": "testing.coverage_percent",
      "operator": ">=",
      "threshold": 60.0,
      "severity": "required",
      "passed": false,
      "current_value": 45.0,
      "message": "Coverage is 45%, need 60%"
    },
    {
      "id": "complexity_avg",
      "name": "Average Complexity",
      "description": "Average cyclomatic complexity",
      "metric_path": "complexity.avg_cyclomatic",
      "operator": "<=",
      "threshold": 10.0,
      "severity": "required",
      "passed": true,
      "current_value": 8.5,
      "message": "Complexity within limits"
    },
    {
      "id": "high_vulnerabilities",
      "name": "High Severity Vulnerabilities",
      "description": "No high severity security issues",
      "metric_path": "security.vulnerabilities.high",
      "operator": "==",
      "threshold": 0,
      "severity": "required",
      "passed": false,
      "current_value": 3,
      "message": "3 high severity vulnerabilities remain"
    },
    {
      "id": "has_test_framework",
      "name": "Test Framework",
      "description": "Test framework installed and configured",
      "metric_path": "testing.has_test_framework",
      "operator": "==",
      "threshold": true,
      "severity": "required",
      "passed": false,
      "current_value": false,
      "message": "No test framework detected"
    },
    {
      "id": "structure_conventions",
      "name": "Directory Structure",
      "description": "Follows language conventions",
      "metric_path": "structure.follows_conventions",
      "operator": "==",
      "threshold": true,
      "severity": "required",
      "passed": false,
      "current_value": false,
      "message": "Structure does not follow conventions"
    }
  ],
  "summary": {
    "total_gates": 5,
    "passed": 1,
    "failed": 4,
    "all_passed": false,
    "required_passed": false
  }
}
```

**Gate Fields**:
- `id` (string): Unique gate identifier
- `name` (string): Human-readable name
- `description` (string): What the gate validates
- `metric_path` (string): JSON path to metric (e.g., "testing.coverage_percent")
- `operator` (string): Comparison operator (>=, <=, ==, !=, >, <)
- `threshold` (number|boolean): Required value
- `severity` (string): "required" or "recommended"
- `passed` (boolean): Gate status
- `current_value` (any): Current metric value
- `message` (string): Status explanation

### PhaseResult

Records the outcome of a workflow phase.

```bash
# File: .brownfield/phases/structure.json
{
  "schema_version": "1.0",
  "phase": "structure",
  "status": "completed",
  "started_at": "2025-10-20T14:30:00Z",
  "completed_at": "2025-10-20T14:45:00Z",
  "duration_seconds": 900,
  "operations": [
    {
      "operation": "create_directory",
      "target": "src/",
      "status": "success",
      "commit": "a1b2c3d"
    },
    {
      "operation": "move_files",
      "source": "*.py (root)",
      "target": "src/",
      "files_moved": 12,
      "status": "success",
      "commit": "e4f5g6h"
    },
    {
      "operation": "update_imports",
      "files_modified": 12,
      "status": "success",
      "commit": "i7j8k9l"
    },
    {
      "operation": "verify_build",
      "command": "python -m py_compile src/*.py",
      "exit_code": 0,
      "status": "success"
    }
  ],
  "metrics_before": {
    "structure.has_src_dir": false,
    "structure.files_in_root": 12
  },
  "metrics_after": {
    "structure.has_src_dir": true,
    "structure.files_in_root": 0
  },
  "git_commits": [
    {
      "sha": "a1b2c3d",
      "message": "[brownfield] structure: Create src/ directory",
      "timestamp": "2025-10-20T14:35:00Z"
    },
    {
      "sha": "e4f5g6h",
      "message": "[brownfield] structure: Move source files to src/",
      "timestamp": "2025-10-20T14:40:00Z"
    },
    {
      "sha": "i7j8k9l",
      "message": "[brownfield] structure: Update import statements",
      "timestamp": "2025-10-20T14:45:00Z"
    }
  ],
  "errors": [],
  "warnings": [
    {
      "message": "Found potential circular import in module.py",
      "severity": "warning"
    }
  ]
}
```

**Fields**:
- `phase` (string): Phase name (assessment, structure, testing, quality, validation)
- `status` (string): completed, failed, in_progress, interrupted
- `started_at` (ISO 8601): Phase start time
- `completed_at` (ISO 8601|null): Phase completion time
- `duration_seconds` (number): Elapsed time
- `operations` (array): List of operations performed
- `metrics_before` (object): Metrics snapshot before phase
- `metrics_after` (object): Metrics snapshot after phase
- `git_commits` (array): Commits created during phase
- `errors` (array): Critical errors
- `warnings` (array): Non-critical issues

### Checkpoint

Enables interruption recovery for long-running phases.

```bash
# File: .brownfield/checkpoint.json
{
  "schema_version": "1.0",
  "phase": "testing",
  "status": "interrupted",
  "started_at": "2025-10-20T15:00:00Z",
  "last_checkpoint": "2025-10-20T15:15:00Z",
  "tasks": [
    {
      "id": "install_pytest",
      "description": "Install pytest framework",
      "status": "completed",
      "completed_at": "2025-10-20T15:05:00Z"
    },
    {
      "id": "generate_test_module_a",
      "description": "Generate tests for module_a.py",
      "status": "completed",
      "completed_at": "2025-10-20T15:10:00Z"
    },
    {
      "id": "generate_test_module_b",
      "description": "Generate tests for module_b.py",
      "status": "in_progress",
      "started_at": "2025-10-20T15:12:00Z"
    },
    {
      "id": "generate_test_module_c",
      "description": "Generate tests for module_c.py",
      "status": "pending"
    },
    {
      "id": "run_tests",
      "description": "Run test suite",
      "status": "pending"
    }
  ],
  "progress": {
    "completed": 2,
    "in_progress": 1,
    "pending": 2,
    "total": 5,
    "percent": 40
  },
  "recovery_data": {
    "current_file": "module_b.py",
    "files_processed": ["module_a.py"],
    "files_remaining": ["module_c.py", "module_d.py"]
  }
}
```

**Fields**:
- `phase` (string): Current phase
- `status` (string): interrupted, completed, failed
- `tasks` (array): Task list with status
- `progress` (object): Completion statistics
- `recovery_data` (object): Phase-specific recovery information

### Configuration

User-defined settings for brownfield workflow.

```bash
# File: .brownfield/config.json
{
  "schema_version": "1.0",
  "quality_gates": {
    "test_coverage_min": 60.0,
    "complexity_max": 10.0,
    "allow_high_vulnerabilities": false
  },
  "phases": {
    "structure": {
      "enabled": true,
      "auto_approve": false,
      "backup_before": true
    },
    "testing": {
      "enabled": true,
      "framework": "auto",
      "coverage_target": 60.0,
      "generate_tests": true
    },
    "quality": {
      "enabled": true,
      "install_precommit": true,
      "linters": ["ruff", "pylint"],
      "formatters": ["black"]
    }
  },
  "git": {
    "auto_commit": true,
    "commit_prefix": "[brownfield]",
    "verify_build_before_commit": true,
    "auto_revert_on_failure": true
  },
  "tools": {
    "python": {
      "complexity": "lizard",
      "security": "bandit",
      "test_runner": "pytest"
    }
  },
  "exclude_patterns": [
    "*.pyc",
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules"
  ]
}
```

**Sections**:
- `quality_gates`: Graduation thresholds
- `phases`: Per-phase configuration
- `git`: Git integration settings
- `tools`: Tool preferences per language
- `exclude_patterns`: Files/directories to ignore

## Directory Structure

```
.brownfield/
├── config.json              # User configuration
├── project.json             # Project metadata
├── quality-gates.json       # Gate definitions and status
├── checkpoint.json          # Recovery checkpoint (if interrupted)
├── metrics/
│   ├── baseline.json        # Initial metrics (immutable)
│   └── current.json         # Latest metrics
├── phases/
│   ├── assessment.json      # Assessment phase results
│   ├── structure.json       # Structure phase results
│   ├── testing.json         # Testing phase results
│   ├── quality.json         # Quality phase results
│   └── validation.json      # Validation phase results
└── reports/
    ├── assessment-report.md # Human-readable assessment
    └── graduation-report.md # Final graduation report
```

## Data Flow

### Phase 0: Assessment
```
Input: Project directory
  ↓
Detect language/framework
  ↓
Collect baseline metrics → baseline.json
  ↓
Initialize quality gates → quality-gates.json
  ↓
Create project.json
  ↓
Generate assessment-report.md
```

### Phases 1-4: Transformation
```
Load project.json + current.json + quality-gates.json
  ↓
Execute phase operations
  ↓
Create git commits (with auto-revert on failure)
  ↓
Update current.json with new metrics
  ↓
Evaluate quality gates
  ↓
Save phase results → phases/{phase}.json
  ↓
Update checkpoint.json (for recovery)
```

### Phase 5: Graduation
```
Load all metrics and phase results
  ↓
Validate all quality gates passed
  ↓
Generate graduation-report.md
  ↓
Create constitution.md (if using Specify)
  ↓
Mark project.json as "graduated"
```

## JSON Schema References

All entities have corresponding JSON schemas in `contracts/` directory:
- `contracts/project.schema.json`
- `contracts/metrics.schema.json`
- `contracts/quality-gate.schema.json`
- `contracts/phase-result.schema.json`
- `contracts/checkpoint.schema.json`
- `contracts/config.schema.json`

These schemas enable validation using `jq` or external validators.

## Metric Path Notation

Quality gates reference metrics using dot notation:

```bash
# Examples
"testing.coverage_percent"           → 45.0
"complexity.avg_cyclomatic"          → 8.5
"security.vulnerabilities.high"      → 3
"structure.follows_conventions"      → false
"codebase.total_lines"               → 12450
```

Bash implementation:
```bash
# Extract metric value using jq
get_metric() {
  local metrics_file="$1"
  local path="$2"

  jq -r ".${path}" "$metrics_file"
}

# Usage
coverage=$(get_metric ".brownfield/metrics/current.json" "testing.coverage_percent")
```

## State Transitions

### Project Status States
```
uninitialized → assessing → assessed → transforming → graduated
                    ↓
                  failed
```

### Phase Status States
```
pending → in_progress → completed
              ↓
          interrupted → resumed → completed
              ↓
            failed
```

## Versioning and Migration

### Schema Version Format
`"schema_version": "MAJOR.MINOR"`

**MAJOR**: Incompatible changes requiring migration
**MINOR**: Backward-compatible additions

### Migration Strategy
```bash
migrate_data() {
  local file="$1"
  local current_version=$(jq -r '.schema_version' "$file")

  case "$current_version" in
    "0.0"|"0.9")
      # Migrate to 1.0
      jq '.schema_version = "1.0" | .phase_timestamps = .timestamps | del(.timestamps)' "$file"
      ;;
    "1.0")
      # Already current
      cat "$file"
      ;;
  esac
}
```

## References

- JSON Schema: https://json-schema.org/
- jq Manual: https://stedolan.github.io/jq/manual/
- ISO 8601 Timestamps: https://en.wikipedia.org/wiki/ISO_8601
