# Structure Refactoring Plan

**Generated**: 2025-10-12 19:54:54 UTC
**Language**: python
**Project**: brownkit

## Overview

Moving 0 files to standard python structure.

⚠️  **IMPORTANT**: Use your IDE's refactoring tools to ensure imports are updated correctly!

## Step 1: Create Directories

- [ ] Create `docs/`

```bash
# Create all directories at once:
mkdir -p docs
```

## Step 2: Move Files (Use IDE Refactoring!)

### ⚠️ CRITICAL: Use IDE Refactoring for Correct Import Updates

BrownKit does NOT move files automatically to avoid breaking your code with
naive import updates. Your IDE has proper AST parsing and will update imports correctly.

**PyCharm Users:**
1. Right-click file → **Refactor** → **Move File**
2. Select destination directory (e.g., `src/{project}`)
3. ✅ Enable "**Search for references**" (updates imports automatically)
4. Review changes in diff view
5. Click "Refactor" to apply

**VSCode Users:**
1. Install "**Python Refactor**" extension (if not installed)
2. Drag file to destination in Explorer pane
3. When prompted, click "**Update imports**"
4. Review changes
5. Save all modified files

**Vim/Emacs/Other:**
- Use LSP refactoring commands if available
- OR use shell script below + manual import fixes

### Files to Move:


## Step 3: Configuration Files

No configuration files need to be created.

## Step 4: Verify Structure

After completing the manual refactoring:

```bash
brownfield structure --verify
```

This will check:
- ✓ Directory structure compliance
- ✓ Build integrity (no syntax errors)
- ✓ Import integrity (all imports resolve)
- ✓ No stray files in root

## Alternative: Shell Script (Advanced)

⚠️  **WARNING**: This script only moves files. It does NOT update imports!

You will need to manually fix all import statements after running this.

See: `.specify/memory/structure-moves.sh`

Only use this if you're comfortable manually updating imports or using find-replace.

## Need Help?

- **Import errors after moving?** Use IDE's "Optimize Imports" or "Fix All" features
- **Build failures?** Check that all import paths match new file locations
- **Circular dependencies?** Review import structure and refactor if needed

## Next Steps

1. ✅ Complete file moves using IDE refactoring
2. ✅ Verify all imports work: `brownfield structure --verify`
3. ✅ Commit changes: `git add . && git commit -m "refactor: reorganize project structure"`
4. ✅ Continue to testing phase: `brownfield testing`
