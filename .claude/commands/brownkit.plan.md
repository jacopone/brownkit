# BrownKit: Plan

**Generate comprehensive remediation plan based on assessment results.**

This command creates a detailed, actionable plan for transforming your brownfield project into a Spec-Kit-ready codebase. It combines structure analysis, test coverage gaps, and quality issues into a prioritized task list.

## What This Command Does

1. **Enforces Workflow**: Validates assessment is complete before planning
2. **Gap Analysis**: Identifies missing tests, structure issues, quality problems
3. **Task Generation**: Creates prioritized remediation tasks with time estimates
4. **Dependency Mapping**: Orders tasks to minimize rework and maximize impact
5. **State Update**: Saves plan to `.specify/memory/state.json`

## Workflow Position

```
ASSESSMENT → [YOU ARE HERE] → REMEDIATION → VALIDATION → GRADUATION → SPEC-KIT READY
              PLANNING
```

**Prerequisites**: Assessment must be completed successfully.

## Plan Components

### 1. Structure Remediation
- File reorganization tasks
- Module separation and decoupling
- Dead code removal
- Duplicate code consolidation

### 2. Testing Plan
- Missing test identification by module
- Test type prioritization (unit → integration → e2e)
- Coverage target setting per module
- Test infrastructure setup if needed

### 3. Quality Improvements
- Complexity reduction tasks (functions with CCN > 10)
- Linting violation fixes by severity
- Security vulnerability remediation
- Code smell elimination

### 4. Build & CI Setup
- Build system configuration
- CI pipeline creation or improvement
- Pre-commit hook setup
- Documentation updates

## Expected Output

After completion, you'll see:
- **Task count** by category and priority
- **Estimated effort** in hours/days
- **Dependency graph** showing execution order
- **Recommended next steps** for remediation

## Next Steps

After planning completes successfully:
1. Review the generated plan and time estimates
2. Run `/brownkit.remediate` to execute the plan
3. The workflow enforcer ensures you complete planning before remediation

## Technical Details

- **Command**: `brownfield plan` (CLI) or orchestrator
- **Input**: Assessment results from state
- **Output**: Updated `.specify/memory/state.json` with tasks
- **Prerequisites**: Completed assessment phase
- **Duration**: 1-2 minutes

## Error Handling

If this command fails:
- Ensure assessment completed successfully (`/brownkit.assess`)
- Check that state file exists at `.specify/memory/state.json`
- Review assessment metrics for completeness
- Re-run assessment if metrics are missing

## Plan Structure

The generated plan includes:
- **High Priority**: Critical issues blocking Spec-Kit readiness
- **Medium Priority**: Important improvements for code quality
- **Low Priority**: Nice-to-have enhancements
- **Time Estimates**: Per-task effort estimates
- **Dependencies**: Task ordering for efficient execution

---

**Note**: The plan can be regenerated if assessment metrics change. Re-running assessment and planning will update task priorities based on current state.
