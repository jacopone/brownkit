# /brownfield.plan - Generate Remediation Plan

**Purpose**: Convert assessment metrics into actionable remediation plan with specific tasks mapped 1:1 to assessment issues and quality gate checklist.

## Workflow

1. **Run plan generation script**:
   ```bash
   .specify/scripts/bash/brownfield-plan.sh --json
   ```

2. **Parse JSON output** to get:
   - `PLAN_FILE`: Path to plan.md
   - `TASK_COUNT`: Number of remediation tasks
   - `CHECKLIST_FILE`: Path to quality-gates.md

3. **Present plan summary** to user:
   - Total tasks generated
   - Phases (Security → Complexity → Testing → Validation)
   - Estimated effort and timeline
   - Quality gate targets
   - Path to detailed plan

4. **Suggest next steps**:
   - Review plan.md
   - Execute manually or run `/brownfield.remediate` for automation

## Example Output

```
=== Remediation Plan Generated ===

Project: 001-legacy-api-cleanup
Total Tasks: 28

Plan Breakdown:
  Phase 1 - Critical Security: 11 tasks (~8 hours)
    - Fix 3 SQL injection vulnerabilities
    - Remove 2 hardcoded credentials
    - Update 6 unsafe dependencies

  Phase 2 - Complexity Reduction: 12 tasks (~12 hours)
    - Refactor 12 functions with CCN > 10
    - Extract service layer from controllers
    - Simplify validation logic

  Phase 3 - Test Coverage: 4 tasks (~6 hours)
    - Add unit tests for user_service.py
    - Add integration tests for API endpoints
    - Add tests for validators module

  Phase 4 - Validation: 1 task (~1 hour)
    - Run /brownfield.validate to verify quality gates

Quality Gate Targets:
  ✓ CCN < 10 (currently 12.5)
  ✓ Coverage > 80% (currently 15%)
  ✓ Zero critical vulnerabilities (currently 3)

Estimated Total Effort: 27 hours (~4 weeks)

Files Created:
  - Plan: .specify/brownfield/001-project/plan.md
  - Checklist: .specify/brownfield/001-project/checklists/quality-gates.md

Next steps:
  1. Review plan.md for task details
  2. Execute manually OR run /brownfield.remediate for automated execution
```

## Error Handling

- If no assessment exists: Error with instructions to run `/brownfield.assess` first
- If assessment is incomplete: Warn about missing metrics and proceed with available data
- If plan generation fails: Display error and suggest manual planning

## Script Interface

**Input**: None (uses active brownfield project from brownfield-state.json)
**Output**: JSON with structure:
```json
{
  "PLAN_FILE": "/abs/path/to/001-project/plan.md",
  "TASK_COUNT": 28,
  "CHECKLIST_FILE": "/abs/path/to/001-project/checklists/quality-gates.md",
  "estimated_hours": 27,
  "timeline_weeks": 4
}
```
