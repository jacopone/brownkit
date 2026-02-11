# /brownfield.graduate - Graduate to Spec-Kit Feature Development

**Purpose**: Certify codebase as AI-ready, update constitution with validated patterns, and enable transition from brownfield remediation to greenfield feature development with Spec-Kit.

## Workflow

1. **Verify prerequisites**:
   - All quality gates passed (from `/brownfield.validate`)
   - Quality gates checklist 100% complete
   - Remediation plan fully executed

2. **Run graduation script**:
   ```bash
   .specify/scripts/bash/brownfield-graduate.sh --json
   ```

3. **Verify checklist completion**:
   - Load `checklists/quality-gates.md`
   - Check all items marked `[X]`
   - If incomplete: Block graduation and show missing items

4. **Create graduation artifacts**:
   - Generate graduation snapshot in `.specify/memory/brownfield-graduation.md`
   - Include final metrics, improvements, and certification
   - Update constitution with graduation timestamp
   - Mark project as "graduated" in brownfield-state.json

5. **Present graduation summary** to user:
   - Graduation status
   - Final quality metrics
   - Improvements achieved
   - Next step guidance for Spec-Kit

## Example Output - Successful Graduation

```
=== Brownfield Graduation ===

Project: 001-legacy-api-cleanup
Graduation Date: 2025-10-20

✓ GRADUATION SUCCESSFUL - Codebase Certified AI-Ready!

Quality Gates: 3 / 3 PASSED ✓
Checklist: 100% Complete ✓

Final Metrics:
  Complexity: Avg CCN 8.2 (target < 10) ✓
  Coverage: 82% (target > 80%) ✓
  Security: 0 critical, 0 high vulnerabilities ✓

Improvements Achieved:
  - Complexity reduced 34% (12.5 → 8.2)
  - Coverage increased 67 points (15% → 82%)
  - All 3 critical vulnerabilities resolved
  - All 8 high-severity issues fixed

Remediation Stats:
  - Total Tasks: 28
  - Duration: 4 weeks
  - Commits: 28 (one per task)

Graduation Documents:
  - Certificate: .specify/memory/brownfield-graduation.md
  - Constitution: Updated with validated patterns

🎓 Codebase is now ready for AI-driven feature development!

Next step: Run /speckit.specify to begin feature planning with Spec-Kit

Example:
  /speckit.specify "Add user authentication with JWT tokens"
```

## Example Output - Graduation Blocked

```
=== Brownfield Graduation ===

Project: 001-legacy-api-cleanup

✗ GRADUATION BLOCKED

Reasons:
  ✗ Quality gates not passing (2 / 3 failed)
      - Test coverage: 68% (need 80%+)
      - Complexity: Avg CCN 11.2 (need < 10)

  ✗ Checklist incomplete (85% complete)
      Missing items:
        - [ ] All high-complexity functions refactored
        - [ ] Integration tests added for API endpoints
        - [ ] Pre-commit hooks configured

Required Actions:
  1. Run /brownfield.validate to see detailed gate failures
  2. Address remaining test coverage gaps
  3. Complete checklist items in quality-gates.md
  4. Re-run /brownfield.graduate when ready

Current status saved. Progress not lost.
```

## Graduation Requirements

Must have ALL of:
- ✓ `/brownfield.validate` shows all gates PASSED
- ✓ `checklists/quality-gates.md` is 100% complete (all items checked)
- ✓ Remediation plan executed (or all manual changes made)

## Post-Graduation

After successful graduation:
- Brownfield project marked "graduated" in state
- Constitution contains validated architectural patterns
- Codebase ready for `/speckit.specify` commands
- Quality gates enforced going forward

## Error Handling

- If validation not run: Error with instructions to run `/brownfield.validate`
- If gates failing: Block graduation, show detailed failures
- If checklist incomplete: Block graduation, show missing items
- If graduation fails: Preserve state, allow retry after fixing issues

## Script Interface

**Input**: None (uses active brownfield project)
**Output**: JSON with structure:
```json
{
  "GRADUATED": true,
  "NEXT_STEP": "/speckit.specify",
  "GRADUATION_FILE": "/abs/path/to/brownfield-graduation.md",
  "final_metrics": {
    "avg_ccn": 8.2,
    "coverage": 82.0,
    "critical_vulns": 0
  }
}
```

**Note**: This is a Post-MVP feature (Priority P1). For MVP, users can manually verify graduation criteria.
