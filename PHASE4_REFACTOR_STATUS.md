# Phase 4 Human-in-the-Loop Refactoring Status

**Date**: 2025-10-12
**Reason**: Avoid risks of automated import updates with naive string replacement

## ✅ Completed

### 1. Updated Specification Documents
- ✅ **spec.md** - Updated User Story 2 to reflect human-in-the-loop workflow
- ✅ **spec.md** - Updated FR-006, FR-006a, FR-007 to require plan generation + verification
- ✅ **spec.md** - Updated SC-003 success criteria for plan quality metrics
- ✅ **contracts/cli-commands.md** - Completely rewrote `brownfield structure` command contract

### 2. New Command Design
**Default Mode**: Generate refactoring plan
```bash
brownfield structure
# Generates: structure-plan.md + structure-moves.sh
# User manually refactors with IDE tools
```

**Verify Mode**: Validate after manual refactoring
```bash
brownfield structure --verify
# Checks: directory structure, build, imports
# Updates state to Phase.TESTING if passes
```

## ⏳ Remaining Tasks

### 3. Implementation Changes Needed

#### A. Refactor `structure.py` (Remediation Logic)
**Current**: Auto-executes file moves + naive import updates
**New**: Plan generation only

**Changes**:
- Remove `execute_plan()` method
- Remove `_update_imports_for_move()` (dangerous string replacement)
- Add `generate_plan()` → creates markdown checklist
- Add `generate_shell_script()` → bash script for file moves only
- Keep `analyze_structure()` for identifying issues

#### B. Add `structure_verifier.py` (New Module)
**Location**: `src/brownfield/remediation/structure_verifier.py`

**Features**:
- `verify_directory_structure()` - checks standard dirs exist
- `verify_build_integrity()` - runs language-specific build
- `verify_import_integrity()` - attempts to import all modules
- `check_stray_files()` - finds source files in root
- `generate_verification_report()` - markdown report with failures

#### C. Update `structure.py` CLI Command
**Current**: Executes automated remediation
**New**: Two modes - plan generation (default) + verification (--verify flag)

**Options to Change**:
- Remove: `--auto-approve`, `--skip-imports`, `--max-files`, `--dry-run`
- Add: `--verify` (flag), `--output` (path), `--format` (markdown/json)

**New Flow**:
```python
if verify_mode:
    verifier = StructureVerifier(project_root, lang_detection)
    result = verifier.verify()
    if result.passed:
        state.advance_phase(Phase.TESTING)
else:
    # Default: generate plan
    remediator = StructureRemediator(project_root, lang_detection)
    plan = remediator.analyze_structure()
    markdown_plan = remediator.generate_plan(plan)
    shell_script = remediator.generate_shell_script(plan)
    # Write files, show instructions
```

### 4. Update Other Documentation

#### D. Update `plan.md`
**Section to Update**: "Structure Remediation"
- Remove references to automated import updates
- Add plan generation architecture
- Add verification component design
- Update user interaction flow

#### E. Update `tasks.md`
**Current Tasks (T043-T047)** already completed but need description updates:
- T043: ~~"move files to standard dirs, update imports"~~ → "generate refactoring plan with IDE instructions"
- T044: ~~"integrate safe commit and auto-revert"~~ → "N/A - removed automated execution"  
- T045: "implement structure command with --verify mode"
- T046: "add CLI command imports" - no change
- T047: ~~"approval handler for destructive operations"~~ → "N/A - no automated destructive ops"

**New Task Needed**:
- T043a: Create structure verification module (structure_verifier.py)

## 📝 Generated Plan Template Example

```markdown
# Structure Refactoring Plan

## Overview
12 Python files need reorganization to PEP 518 structure

## Step 1: Create Directories
- [ ] mkdir -p src/myproject
- [ ] mkdir -p tests
- [ ] mkdir -p docs

## Step 2: Move Files (Use IDE!)

### PyCharm Instructions:
Right-click file → Refactor → Move Module → Select src/myproject/

### VSCode Instructions:
Drag file in explorer → Confirm import updates

### Files to Move:
- [ ] main.py → src/myproject/main.py (3 import references)
- [ ] utils.py → src/myproject/utils.py (5 import references)
...

## Step 3: Verify
```bash
brownfield structure --verify
```
```

## 🎯 Benefits of This Approach

1. **No Code Corruption**: IDE AST parsing > naive string replacement
2. **User Trust**: Advisory tool, not scary automated changes  
3. **Learn Codebase**: Manual process helps understand structure
4. **Constitution Aligned**: Transparent reasoning, reversibility, human approval
5. **IDE Features**: Leverage refactoring tools developers already trust

## ⚠️ Breaking Changes

**For Users**:
- `brownfield structure` no longer executes automatically
- Must manually refactor using IDE tools
- Must run `brownfield structure --verify` after refactoring

**Migration Path**:
- Old behavior available via shell script if needed
- Clear error messages guide users to new workflow
- Documentation emphasizes IDE refactoring benefits

## 📊 Test Plan

1. **Plan Generation**: Verify markdown + shell script generated correctly
2. **Verification - Pass**: Manual refactoring completed correctly
3. **Verification - Fail**: Detects stray files, broken imports, build failures
4. **Multi-Language**: Test with Python, JavaScript, Rust, Go projects

## Next Steps

Would you like me to:
1. **Continue refactoring** - Implement structure.py changes + verifier
2. **Update tasks.md** - Revise task descriptions to match new design
3. **Update plan.md** - Document architecture changes
4. **All of the above** - Complete the refactoring

