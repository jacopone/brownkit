# /brownfield.remediate - Execute Remediation with Checkpoints

**Purpose**: Execute remediation tasks incrementally with checkpoint validation after each task to prevent breaking the codebase.

## Workflow

1. **Verify prerequisites**:
   - Remediation plan exists
   - Git working tree is clean (or user acknowledges uncommitted changes)
   - Tests are executable

2. **Run remediation script**:
   ```bash
   .specify/scripts/bash/brownfield-remediate.sh --json [--auto-commit]
   ```

3. **Execute tasks sequentially**:
   - Load task list from plan.md
   - For each task:
     - Present task to Claude for implementation
     - Wait for completion
     - Run checkpoint validation (pytest)
     - If `--auto-commit`: Create git commit
     - Log result to execution-log.md

4. **Checkpoint validation**:
   - Run full test suite
   - Check for regressions
   - Verify build succeeds
   - If failed: Stop execution, log error

5. **Present progress** to user:
   - Tasks completed / total
   - Current phase
   - Any checkpoint failures
   - Next task or completion status

## Example Output

```
=== Remediation Execution ===

Project: 001-legacy-api-cleanup
Mode: Interactive (no auto-commit)

✓ Git working tree clean
✓ Test suite executable

Progress: Task 3 of 28

Phase 1 - Critical Security Fixes:
  ✓ Task 1: Fix SQL injection in queries.py [PASS]
  ✓ Task 2: Remove hardcoded API key [PASS]
  ⚙ Task 3: Update vulnerable dependency (in progress)

Checkpoint Status:
  - All tests passing (142 passed, 0 failed)
  - No regressions detected
  - Build successful

Next: Task 4 - Fix deserialization vulnerability

Execution log: .specify/brownfield/001-project/execution-log.md
```

## Checkpoint Failure Handling

If checkpoint fails:
```
✗ Checkpoint Failed - Task 5

Error: 3 tests failed after refactoring user_service.py
  - test_process_user_valid_input FAILED
  - test_process_user_invalid_input FAILED
  - test_user_service_integration FAILED

Execution stopped. Review failures in execution-log.md

Options:
  1. Fix the issue manually
  2. Re-run tests to verify fix
  3. Resume with /brownfield.remediate --resume
```

## Flags

- `--auto-commit`: Create git commit after each successful checkpoint (default: false)
- `--resume`: Resume from last checkpoint after fixing failures
- `--dry-run`: Show what would be executed without making changes

## Error Handling

- If no plan exists: Error with instructions to run `/brownfield.plan`
- If git dirty and no `--force`: Warn and ask user to commit/stash
- If tests not executable: Error with instructions to fix test setup
- If checkpoint fails: Stop execution, log error, provide recovery options

## Script Interface

**Input**: None (uses active brownfield project)
**Output**: JSON with structure:
```json
{
  "COMPLETED_TASKS": 12,
  "FAILED_TASKS": 0,
  "STATUS": "success",
  "EXECUTION_LOG": "/abs/path/to/001-project/execution-log.md"
}
```

**Note**: This is a Post-MVP feature (Priority P1). For MVP, users execute tasks manually from plan.md.
