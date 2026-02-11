# BrownKit: Remediate

**Execute the remediation plan to transform your brownfield codebase.**

This command guides you through executing the prioritized remediation tasks generated during planning. It tracks progress, handles failures gracefully, and allows resumption from checkpoints.

## What This Command Does

1. **Enforces Workflow**: Validates planning is complete before remediation
2. **Task Execution**: Processes tasks in dependency order
3. **Progress Tracking**: Creates checkpoints after each completed task
4. **Failure Handling**: Allows retry and resume on failures
5. **State Updates**: Continuously saves progress to state

## Workflow Position

```
ASSESSMENT → PLANNING → [YOU ARE HERE] → VALIDATION → GRADUATION → SPEC-KIT READY
                         REMEDIATION
```

**Prerequisites**: Planning must be completed successfully.

## Remediation Categories

### 1. Structure Tasks
- Reorganize files into proper directory structure
- Split large modules into smaller, focused ones
- Remove dead code and unused imports
- Consolidate duplicate code

### 2. Testing Tasks
- Add missing unit tests for uncovered modules
- Create integration tests for critical paths
- Set up test infrastructure (fixtures, mocks)
- Achieve target coverage percentage

### 3. Quality Tasks
- Refactor complex functions (CCN > 10)
- Fix linting violations (critical → high → medium)
- Remediate security vulnerabilities
- Address code smells and anti-patterns

### 4. Build & CI Tasks
- Configure build system
- Set up CI/CD pipeline
- Add pre-commit hooks
- Update documentation

## Expected Output

During remediation, you'll see:
- **Current task** being executed
- **Progress percentage** (completed/total tasks)
- **Checkpoint saves** after each task
- **Failure notifications** with suggested fixes
- **Resume instructions** if interrupted

## Task Execution Flow

```
For each task in priority order:
  1. Check prerequisites met
  2. Execute task (manual or automated)
  3. Verify completion criteria
  4. Save checkpoint
  5. Update metrics
  6. Continue to next task
```

## Checkpoints & Resume

If remediation is interrupted:
- Progress is saved at `.specify/brownfield/checkpoints/`
- Run `/brownkit.remediate` again to resume
- Use `brownfield resume` CLI command
- Completed tasks are skipped automatically

## Next Steps

After remediation completes successfully:
1. Review the remediation summary
2. Run `/brownkit.validate` to verify improvements
3. The workflow enforcer ensures validation before graduation

## Technical Details

- **Command**: `brownfield remediate` (CLI) or orchestrator
- **Input**: Remediation plan from state
- **Output**: Updated codebase + checkpoints
- **Prerequisites**: Completed planning phase
- **Duration**: Hours to days (depends on plan size)

## Interactive vs Automated

- **Automated tasks**: Linting fixes, formatting, simple refactoring
- **Interactive tasks**: Complex refactoring, test writing, architecture changes
- **Manual review**: High-impact changes require confirmation

## Error Handling

If remediation fails:
- Review the error message and task description
- Fix the issue manually if needed
- Use `brownfield resume` to continue from checkpoint
- Skip failing tasks if necessary (marks as failed, continues)
- Re-run planning if requirements changed

## Metrics Tracking

Throughout remediation, BrownKit tracks:
- Test coverage changes
- Complexity reduction
- Vulnerability fixes
- Build status improvements

These metrics are used in validation phase to verify improvements.

---

**Note**: Remediation can be paused and resumed at any time. All progress is checkpointed, so interruptions don't lose work.
