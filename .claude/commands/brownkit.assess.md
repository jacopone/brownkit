# BrownKit: Assess

**Execute comprehensive brownfield project assessment.**

This command initiates the BrownKit workflow by analyzing the current project's structure, test coverage, code quality, and technical debt. This is the **entry point** for the brownfield-to-Spec-Kit transformation workflow.

## What This Command Does

1. **Enforces Workflow**: Validates this is the correct phase to execute
2. **Project Analysis**: Scans codebase for structure, tests, and quality metrics
3. **Baseline Metrics**: Establishes baseline for future regression detection
4. **Planning Foundation**: Generates data needed for remediation planning
5. **State Initialization**: Creates `.specify/memory/state.json` with results

## Workflow Position

```
[YOU ARE HERE] → PLANNING → REMEDIATION → VALIDATION → GRADUATION → SPEC-KIT READY
  ASSESSMENT
```

This phase can always be executed, even if state doesn't exist (it initializes the workflow).

## Assessment Dimensions

### 1. Structure Analysis
- File organization and directory structure
- Module dependencies and coupling
- Dead code detection
- Duplicate code identification

### 2. Testing Analysis
- Test coverage percentage
- Test types present (unit, integration, e2e)
- Test quality and assertions
- Missing test areas

### 3. Quality Analysis
- Cyclomatic complexity (functions, classes, modules)
- Code smells and anti-patterns
- Linting violations
- Security vulnerabilities

### 4. Build & CI Analysis
- Build system configuration
- CI/CD pipeline status
- Deployment readiness
- Documentation quality

## Expected Output

After completion, you'll see:
- **Assessment summary** with key metrics
- **Baseline metrics** recorded in state
- **Recommended next steps** for planning
- **State file** created at `.specify/memory/state.json`

## Next Steps

After assessment completes successfully:
1. Review the assessment report
2. Run `/brownkit.plan` to create remediation plan
3. The workflow enforcer will guide you through remaining phases

## Technical Details

- **Command**: `brownfield assess` (CLI) or orchestrator
- **Output**: `.specify/memory/state.json`
- **Prerequisites**: None (entry point)
- **Duration**: 2-5 minutes depending on codebase size

## Error Handling

If this command fails:
- Check that you're in a project root directory
- Ensure basic language tools are available (pytest, jest, cargo, go, etc.)
- Review error output for specific issues
- Re-run after addressing issues

---

**Note**: This command can be re-run multiple times. Each run updates the state with latest metrics, allowing you to track improvement over time.
