---
status: active
created: 2025-10-20
updated: 2025-10-20
type: guide
lifecycle: persistent
---

# Brownfield Kit Quickstart Guide

Get started with Brownfield Kit to transform legacy codebases into well-structured, tested, and maintainable projects.

## Prerequisites

### Required Tools

- **bash** 4.0+ (check: `bash --version`)
- **git** 2.0+ (check: `git --version`)
- **jq** 1.6+ (check: `jq --version`)

### Language-Specific Tools

Depending on your project's language, install the appropriate quality tools:

**Python**:
```bash
pip install lizard pytest pytest-cov bandit
```

**JavaScript/TypeScript**:
```bash
npm install -g jest eslint @typescript-eslint/parser lizard
```

**Rust**:
```bash
# Tools included with rustup
rustup component add clippy rustfmt
cargo install cargo-audit
```

**Go**:
```bash
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
go install github.com/securego/gosec/v2/cmd/gosec@latest
```

### System Requirements

- **Disk Space**: 100MB for Brownfield Kit + space for project backups
- **Memory**: 512MB minimum (2GB recommended for large projects)
- **Operating System**: Linux, macOS, WSL2

## Installation

### Method 1: Direct Download (Recommended)

```bash
# Download latest release
curl -L https://github.com/brownfield-kit/brownfield/releases/latest/download/brownfield -o brownfield

# Make executable
chmod +x brownfield

# Move to PATH
sudo mv brownfield /usr/local/bin/

# Verify installation
brownfield --version
```

### Method 2: From Source

```bash
# Clone repository
git clone https://github.com/brownfield-kit/brownfield.git
cd brownfield

# Run installation script
./install.sh

# Verify installation
brownfield --version
```

### Method 3: NixOS

```nix
# Add to configuration.nix or home.nix
environment.systemPackages = with pkgs; [
  brownfield
];
```

## Quick Start

### Step 1: Initialize Project

Navigate to your legacy project and initialize Brownfield Kit:

```bash
cd /path/to/your/project

# Initialize brownfield
brownfield init

# This creates:
# .brownfield/
# ├── config.json          (default configuration)
# └── README.md            (documentation)
```

### Step 2: Run Assessment

Analyze your codebase to establish baseline metrics:

```bash
# Quick assessment (10-15 minutes for most projects)
brownfield assess --quick

# Full assessment (more detailed, takes longer)
brownfield assess --full

# Output: .brownfield/metrics/baseline.json
#         .brownfield/reports/assessment-report.md
```

**Review the assessment report**:
```bash
bat .brownfield/reports/assessment-report.md
# or
cat .brownfield/reports/assessment-report.md
```

### Step 3: Configure Quality Gates

Edit quality thresholds to match your team's standards:

```bash
# Edit configuration
$EDITOR .brownfield/config.json

# Key settings:
# - quality_gates.test_coverage_min: 60.0
# - quality_gates.complexity_max: 10.0
# - quality_gates.allow_high_vulnerabilities: false
```

### Step 4: Run Transformation Phases

Execute phases sequentially or run the full workflow:

```bash
# Option A: Run all phases automatically
brownfield graduate

# Option B: Run phases individually
brownfield structure    # Reorganize directory structure
brownfield testing      # Add test framework and generate tests
brownfield quality      # Install linters and pre-commit hooks
brownfield validate     # Check all quality gates
```

### Step 5: Review Results

After transformation, review the graduation report:

```bash
bat .brownfield/reports/graduation-report.md

# Check final metrics
jq . .brownfield/metrics/current.json

# View git history
git log --oneline --grep="brownfield"
```

## Common Workflows

### Workflow 1: Quick Assessment Only

Just want to understand your codebase without making changes?

```bash
brownfield init
brownfield assess --quick
bat .brownfield/reports/assessment-report.md
```

### Workflow 2: Structure Remediation Only

Only fix directory structure without adding tests:

```bash
brownfield init
brownfield assess --quick
brownfield structure --auto-approve
```

### Workflow 3: Add Tests to Existing Structure

Project already well-organized but needs tests?

```bash
brownfield init

# Disable structure phase
jq '.phases.structure.enabled = false' .brownfield/config.json > tmp.json
mv tmp.json .brownfield/config.json

brownfield assess --quick
brownfield testing --coverage-target=70
```

### Workflow 4: Resume Interrupted Workflow

Brownfield Kit automatically creates checkpoints. If interrupted:

```bash
# Check if checkpoint exists
if [ -f .brownfield/checkpoint.json ]; then
  echo "Checkpoint detected"
  jq '.progress' .brownfield/checkpoint.json
fi

# Resume from checkpoint
brownfield resume

# Or restart from beginning
brownfield graduate --restart
```

## Configuration Reference

### Basic Configuration

```json
{
  "schema_version": "1.0",
  "quality_gates": {
    "test_coverage_min": 60.0,
    "complexity_max": 10.0,
    "allow_high_vulnerabilities": false
  },
  "phases": {
    "structure": {
      "enabled": true,
      "auto_approve": false,
      "backup_before": true
    },
    "testing": {
      "enabled": true,
      "framework": "auto",
      "coverage_target": 60.0,
      "generate_tests": true
    },
    "quality": {
      "enabled": true,
      "install_precommit": true,
      "linters": ["ruff", "pylint"],
      "formatters": ["black"]
    }
  },
  "git": {
    "auto_commit": true,
    "commit_prefix": "[brownfield]",
    "verify_build_before_commit": true,
    "auto_revert_on_failure": true
  }
}
```

### Advanced Options

**Skip Prerequisites Check** (development only):
```bash
SKIP_CHECKS=true brownfield assess
```

**Custom Metrics Thresholds**:
```bash
# Via config file
jq '.quality_gates.complexity_max = 15' .brownfield/config.json > tmp.json
mv tmp.json .brownfield/config.json

# Via command-line flag
brownfield validate --complexity-max=15 --coverage-min=50
```

**Exclude Directories**:
```json
{
  "exclude_patterns": [
    "*.pyc",
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "vendor",
    "target",
    "dist",
    "build"
  ]
}
```

## Troubleshooting

### Issue: "Command not found: brownfield"

**Solution**: Ensure `/usr/local/bin` is in your PATH:
```bash
echo $PATH
# If missing, add to ~/.bashrc or ~/.zshrc:
export PATH="/usr/local/bin:$PATH"
```

### Issue: "jq: command not found"

**Solution**: Install jq:
```bash
# Debian/Ubuntu
sudo apt-get install jq

# macOS
brew install jq

# NixOS (add to configuration.nix)
environment.systemPackages = [ pkgs.jq ];
```

### Issue: "No quality tools detected"

**Solution**: Install language-specific tools (see Prerequisites section)

### Issue: "Build verification failed after commit"

Brownfield Kit automatically reverts failed commits. Check the decision log:
```bash
bat .specify/memory/brownfield-decisions.md
```

To disable auto-revert (not recommended):
```json
{
  "git": {
    "auto_revert_on_failure": false
  }
}
```

### Issue: "Quality gates not passing"

**Solution**: Lower thresholds temporarily or fix issues:
```bash
# Check which gates are failing
jq '.gates[] | select(.passed == false)' .brownfield/quality-gates.json

# Adjust thresholds
$EDITOR .brownfield/config.json

# Or fix the underlying issues
brownfield testing --coverage-target=60
```

### Issue: "Checkpoint recovery fails"

**Solution**: Start fresh or manually resume:
```bash
# Option 1: Delete checkpoint and restart
rm .brownfield/checkpoint.json
brownfield graduate

# Option 2: Inspect checkpoint
jq . .brownfield/checkpoint.json

# Option 3: Resume specific phase
brownfield testing --resume
```

## Command Reference

### Core Commands

```bash
brownfield init                    # Initialize project
brownfield assess [--quick|--full] # Run assessment
brownfield structure               # Fix directory structure
brownfield testing                 # Add tests and coverage
brownfield quality                 # Install quality tools
brownfield validate                # Check quality gates
brownfield graduate                # Run full workflow
brownfield resume                  # Resume from checkpoint
```

### Utility Commands

```bash
brownfield status                  # Show current phase and metrics
brownfield metrics                 # Display metrics comparison
brownfield gates                   # Show quality gate status
brownfield clean                   # Remove .brownfield/ directory
brownfield version                 # Show version information
```

### Flags

```bash
--quick                   # Fast assessment (sampling)
--full                    # Comprehensive assessment
--auto-approve            # Skip confirmation prompts
--coverage-target=N       # Set coverage target (0-100)
--complexity-max=N        # Set max complexity threshold
--skip-phase=PHASE        # Skip specific phase
--resume                  # Resume from checkpoint
--restart                 # Ignore checkpoint, start fresh
```

## Environment Variables

```bash
SKIP_CHECKS=true          # Skip prerequisite validation
BROWNFIELD_CONFIG=path    # Custom config file location
BROWNFIELD_VERBOSE=1      # Enable verbose logging
BROWNFIELD_DRY_RUN=1      # Show what would be done (no changes)
```

## Integration with Specify

Brownfield Kit integrates with GitHub's Specify (Spec-Kit) workflow:

```bash
# After graduation, create constitution
brownfield graduate

# Constitution created at:
# .specify/memory/constitution.md

# Use with future spec-driven development
/speckit.specify "Add user authentication feature"
```

## Next Steps

After completing the quickstart:

1. **Review Documentation**:
   - `docs/data-model.md` - Understand data structures
   - `docs/research.md` - Learn about implementation patterns
   - `docs/architecture.md` - System design details

2. **Customize Workflow**:
   - Adjust quality gates to your team's standards
   - Configure language-specific tool preferences
   - Set up pre-commit hooks

3. **Integrate with CI/CD**:
   - Add brownfield validation to CI pipeline
   - Enforce quality gates on pull requests
   - Track metrics over time

4. **Share with Team**:
   - Document your brownfield configuration
   - Create team-specific presets
   - Establish transition guidelines

## Support

- **Documentation**: https://brownfield-kit.dev/docs
- **GitHub Issues**: https://github.com/brownfield-kit/brownfield/issues
- **Discussions**: https://github.com/brownfield-kit/brownfield/discussions
- **Examples**: https://github.com/brownfield-kit/examples

## License

Brownfield Kit is open source software licensed under MIT.
