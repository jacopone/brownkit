# Brownfield Graduate

Generate Speckit constitution, archive brownfield artifacts, create graduation report.

```bash
brownfield graduate
```

This command performs the final transition from brownfield to spec-driven development:

**Phase 1: Validation Check**
- Verifies all 7 readiness gates passed
- Ensures metrics improvement verified

**Phase 2: Speckit Constitution Generation**
- Analyzes project architecture and tech stack
- Generates `.specify/constitution.md` with:
  - Core development principles
  - Language-specific conventions
  - Testing standards
  - Quality gate requirements
  - Architecture patterns
  - Spec-driven workflow guidelines

**Phase 3: Speckit Templates Creation**
- `.specify/templates/spec-template.md` - Feature specification template
- `.specify/templates/plan-template.md` - Implementation plan template
- `.specify/templates/tasks-template.md` - Task breakdown template

**Phase 4: Artifact Archival**
- Archives brownfield state, reports, and working files
- Default location: `.specify/memory/brownfield-archive/YYYYMMDD-HHMMSS/`
- Cleans up temporary working files
- Preserves active configs (complexity-justification.md, .pre-commit-config.yaml)

**Phase 5: Graduation Report**
- `brownfield-graduation-report.md` - Complete transition summary
- Baseline vs final metrics comparison
- All 7 gates validation status
- Structural changes made
- Quality improvements installed
- Next steps for spec-driven development

Options:
- `--force` - Force graduation even if validation incomplete
- `--archive-path PATH` - Custom archive location

After graduation, use Speckit slash commands:
```bash
/speckit.specify  # Create feature specification
/speckit.plan     # Design implementation approach
/speckit.tasks    # Generate task breakdown
```

For ongoing quality monitoring:
```bash
brownfield validate  # Re-check readiness periodically
```

If quality regresses after graduation:
```bash
brownfield assess   # Detects regression and re-enters appropriate phase
```
