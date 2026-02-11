# BrownKit: Migrate

**Migrate BrownKit v1.0 state to v2.0 format with Spec-Kit compatibility.**

This command handles migration from BrownKit v1.0 to v2.0, including state file renaming, schema updates, and checkpoint directory relocation. It ensures backward compatibility while enabling new workflow enforcement and Spec-Kit integration features.

## What This Command Does

1. **State File Migration**: Renames `brownfield-state.json` → `state.json`
2. **Schema Upgrade**: Converts v1.0 state to v2.0 with workflow tracking
3. **Checkpoint Relocation**: Moves `.brownfield/checkpoints/` → `.specify/brownfield/`
4. **Backup Creation**: Creates timestamped backups before migration
5. **Validation**: Verifies migrated state loads correctly

## When to Use

Run migration:
- **Upgrading from v1.0**: After installing BrownKit v2.0
- **State file confusion**: If you have both old and new state files
- **Checkpoint issues**: If checkpoints are in old location
- **Manual trigger**: Use `--force` to re-migrate after manual edits

## What Gets Migrated

### 1. State File Path
- **From**: `.specify/memory/brownfield-state.json`
- **To**: `.specify/memory/state.json`
- **Reason**: Spec-Kit compatibility (unified state naming)

### 2. State Schema (v1.0 → v2.0)
**Added fields**:
- `workflow_state`: Sequential phase tracking
- `speckit`: Spec-Kit integration metadata
- `migrated_from_version`: Migration tracking

**Preserved fields**:
- `project_root`
- `current_phase`
- `baseline_metrics`
- `current_metrics`
- All existing data

### 3. Checkpoint Directory
- **From**: `.brownfield/checkpoints/`
- **To**: `.specify/brownfield/checkpoints/`
- **Reason**: Consolidate all BrownKit state under `.specify/`

### 4. Workflow State Initialization
For v1.0 states, workflow state is initialized based on `current_phase`:
- `Phase.ASSESSMENT` → `WorkflowPhase.ASSESSMENT` (completed)
- `Phase.PLANNING` → `WorkflowPhase.PLANNING` (completed)
- `Phase.REMEDIATION` → `WorkflowPhase.REMEDIATION` (in_progress)
- `Phase.VALIDATION` → `WorkflowPhase.VALIDATION` (completed)
- `Phase.GRADUATED` → `WorkflowPhase.SPEC_KIT_READY` (completed)

## Expected Output

### Successful Migration

```
🔄 BrownKit Migration (v1.0 → v2.0)
===================================

Checking for migration needs...
  ✅ Found v1.0 state: .specify/memory/brownfield-state.json
  ℹ️  Target location: .specify/memory/state.json

Backup Creation:
  ✅ Created backup: .specify/memory/state.backup_20251026_143022.json

State Migration:
  ✅ Schema upgraded: v1.0 → v2.0
  ✅ Workflow state initialized
  ✅ Spec-Kit integration added
  ✅ State file renamed

Checkpoint Migration:
  ✅ Found checkpoints: .brownfield/checkpoints/ (3 files)
  ✅ Moved to: .specify/brownfield/checkpoints/
  ✅ Cleaned up old directory

Validation:
  ✅ Migrated state loads correctly
  ✅ All metrics preserved
  ✅ Workflow phase: REMEDIATION (in_progress)

Migration Complete!
  Old state: Backed up to state.backup_20251026_143022.json
  New state: .specify/memory/state.json
  Checkpoints: .specify/brownfield/checkpoints/

Next steps:
  - Run 'brownfield status' to verify migration
  - Continue your workflow from where you left off
  - Old state files can be deleted after verification
```

### Already Migrated

```
🔄 BrownKit Migration Check
===========================

Status: ✅ Already migrated to v2.0

Current state:
  Schema version: 2.0
  State file: .specify/memory/state.json
  Migrated from: 1.0 (on 2025-10-15)

No migration needed.
```

### Nothing to Migrate

```
🔄 BrownKit Migration Check
===========================

Status: ℹ️  No v1.0 state found

Current state:
  Schema version: 2.0 (native v2.0)
  State file: .specify/memory/state.json

No migration needed.
```

## Migration Safety

### Backups Created
Before migration:
- **State backup**: `.specify/memory/state.backup_YYYYMMDD_HHMMSS.json`
- **Checkpoint backup**: `.specify/brownfield/checkpoints.backup_YYYYMMDD_HHMMSS/`

### Atomic Operations
Migration uses atomic file operations:
1. Create new state file
2. Verify it loads correctly
3. Rename old state to backup
4. Only then delete old files

### Rollback
If migration fails or you want to rollback:

```bash
# Restore from backup
cd .specify/memory
mv state.json state.json.migrated
mv state.backup_YYYYMMDD_HHMMSS.json brownfield-state.json

# Restore checkpoints
mv .specify/brownfield/checkpoints.backup_YYYYMMDD_HHMMSS .brownfield/checkpoints
```

## Migration Modes

### Automatic (Default)
Migration runs automatically on first v2.0 command if v1.0 state detected.

### Manual (Explicit)
```bash
brownfield migrate
```

### Force Re-migration
```bash
brownfield migrate --force
```
Re-runs migration even if already migrated (uses backup if available).

## Technical Details

- **Command**: `brownfield migrate` (CLI) or orchestrator
- **Input**: v1.0 state at `.specify/memory/brownfield-state.json`
- **Output**: v2.0 state at `.specify/memory/state.json`
- **Prerequisites**: None (can run anytime)
- **Duration**: < 1 second

## Error Handling

### Migration Fails

**State file locked**:
- Ensure no other BrownKit process is running
- Check file permissions
- Try again after closing other editors

**Invalid v1.0 state**:
- Review state file for corruption
- Restore from older backup if needed
- Contact support if data is critical

**Checkpoint migration fails**:
- Manual checkpoint copy may be needed
- Old checkpoints remain in `.brownfield/` until successful
- Use `--skip-checkpoints` flag to migrate state only

### Verification Fails

If migrated state doesn't load:
- Check backup file integrity
- Review migration error messages
- Rollback to v1.0 state
- Report issue with error log

## Post-Migration

After successful migration:

1. **Verify**: Run `brownfield status` to check workflow state
2. **Test**: Execute next workflow phase to ensure functionality
3. **Clean up**: Delete backup files after confirming everything works
4. **Continue**: Resume workflow from where you left off

## Checkpoint Compatibility

v2.0 checkpoints are compatible with v1.0 format:
- Existing checkpoint data is preserved
- New checkpoints include workflow metadata
- Can resume from v1.0 checkpoints after migration

---

**Note**: Migration is idempotent and safe. It can be run multiple times without data loss. Backups are always created before modifications.
