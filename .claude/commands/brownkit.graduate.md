# BrownKit: Graduate

**Graduate to Spec-Kit readiness by generating project constitution.**

This command marks the successful completion of the BrownKit workflow by generating a project constitution that encodes all quality standards, testing requirements, and architectural constraints. The constitution becomes the foundation for Spec-Kit's specification-driven development.

## What This Command Does

1. **Enforces Workflow**: Validates all readiness gates passed before graduation
2. **Constitution Generation**: Creates `constitution.md` from graduation metrics
3. **Spec-Kit Integration**: Verifies Spec-Kit compatibility and initializes integration
4. **Workflow Completion**: Marks project as SPEC_KIT_READY
5. **Monitoring Setup**: Establishes baseline for post-graduation regression detection

## Workflow Position

```
ASSESSMENT → PLANNING → REMEDIATION → VALIDATION → [YOU ARE HERE] → SPEC-KIT READY
                                                     GRADUATION
```

**Prerequisites**: All 7 readiness gates must pass validation.

## Graduation Process

### 1. Pre-Graduation Checks
- ✅ All 7 readiness gates passed
- ✅ Validation completed without regressions
- ✅ Build and CI passing
- ✅ No critical security issues

### 2. Constitution Generation
The constitution encodes your project's quality standards:

**Structure Standards**:
- Directory organization rules
- Module coupling constraints
- Dead code tolerance (0%)

**Testing Requirements**:
- Minimum coverage percentage (from achieved metrics)
- Required test types (unit, integration, e2e)
- Test quality standards (assertions per test)

**Quality Gates**:
- Maximum cyclomatic complexity (CCN threshold)
- Linting rules and violation tolerance
- Code smell detection rules

**Security Standards**:
- Vulnerability tolerance by severity
- Secrets detection requirements
- Dependency update policy

**Build & CI Requirements**:
- Build success criteria
- CI pipeline requirements
- Pre-commit hook configuration

### 3. Spec-Kit Compatibility Check
Verifies:
- ✅ `.claude/commands/speckit.specify.md` exists (Spec-Kit installed)
- ✅ `.specify/memory/` directory writable
- ✅ Slash commands available
- ⚠️ Warns if constitution already exists (offers backup)

### 4. Constitution File Creation
Generated file: `.specify/memory/constitution.md`

**Content includes**:
```markdown
# Project Constitution

Generated: YYYY-MM-DD
Language: Python/JavaScript/Rust/Go
Baseline: [graduation metrics]

## Quality Standards
[Encoded from validation metrics]

## Testing Requirements
[Coverage targets, test types, quality gates]

## Security Requirements
[Vulnerability thresholds, secrets policy]

## Build & CI Requirements
[Build configuration, pipeline requirements]

## Regression Thresholds
[Post-graduation monitoring thresholds]
```

## Expected Output

After graduation, you'll see:
- **✅ Graduation successful** message
- **Constitution path**: `.specify/memory/constitution.md`
- **Spec-Kit status**: Integration details
- **Next steps**: Using Spec-Kit for new features
- **Monitoring setup**: Regression detection active

## Graduation Report

```
🎓 Graduation Report
====================

Phase: SPEC_KIT_READY
Date: 2025-10-26

Readiness Gates: 7/7 passed (100%)
  ✅ Structure Gate
  ✅ Testing Gate
  ✅ Quality Gate
  ✅ Security Gate
  ✅ Build Gate
  ✅ CI Gate
  ✅ Documentation Gate

Constitution: .specify/memory/constitution.md
Spec-Kit: Installed (v1.2.3)

Improvements Achieved:
  Test Coverage: 45% → 85% (+40%)
  Complexity Avg: 18.3 → 8.2 (-55%)
  Critical Vulns: 3 → 0 (-100%)
  Build Status: failing → passing

Your project is now Spec-Kit ready!
```

## Next Steps

After graduation:
1. Review the generated constitution
2. Use `/speckit.specify` to create feature specifications
3. Monitor for regressions with `/brownkit.monitor`
4. All new features follow Spec-Kit workflow

## Spec-Kit Workflow

With graduation complete, use Spec-Kit for new development:

```
/speckit.specify → /speckit.clarify → /speckit.plan → /speckit.implement
```

The constitution ensures all new code maintains quality standards.

## Technical Details

- **Command**: `brownfield graduate` (CLI) or orchestrator
- **Input**: Validation results + graduation metrics
- **Output**: `.specify/memory/constitution.md`
- **Prerequisites**: All 7 readiness gates passed
- **Duration**: 1-2 minutes

## Error Handling

If graduation fails:

### Not All Gates Passed:
- Review which gates failed
- Return to `/brownkit.validate` to see detailed report
- Address remaining issues via remediation
- Validate again before graduating

### Spec-Kit Not Installed:
- Install Spec-Kit following documentation
- Ensure `.claude/commands/speckit.specify.md` exists
- Re-run graduation

### Constitution Already Exists:
- BrownKit will offer to backup existing constitution
- Confirm overwrite or cancel
- Review backup before proceeding

## Post-Graduation Monitoring

After graduation, BrownKit enters monitoring mode:
- **Regression detection**: Tracks metrics against baseline
- **Alert thresholds**: Warns when metrics degrade
- **Re-entry triggers**: Critical regressions trigger workflow re-entry
- **Use `/brownkit.monitor`** to check post-graduation health

---

**Note**: Graduation is the final step of BrownKit workflow. Once graduated, the project uses Spec-Kit for all new features while BrownKit monitors for quality regressions.
