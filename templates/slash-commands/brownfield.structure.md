# Brownfield Structure

Generate refactoring plan for directory structure reorganization, then verify after manual refactoring.

## Generate Plan (Default)

```bash
brownfield structure
```

Generates:
- `structure-plan.md` - Step-by-step reorganization checklist with IDE instructions
- `structure-moves.sh` - Bash script for file moves only (no import updates)

Then manually refactor using IDE tools (PyCharm "Move Module", VSCode drag-and-drop).

## Verify After Refactoring

```bash
brownfield structure --verify
```

Validates:
- Directory structure follows ecosystem conventions
- Build passes cleanly
- All imports resolve correctly
- No stray source files in root

If verification passes, state advances to TESTING phase.

Options:
- `--output PATH` - Custom plan location
- `--format [markdown|json]` - Output format
